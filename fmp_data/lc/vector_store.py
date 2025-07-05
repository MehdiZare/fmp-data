from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
import json
from logging import Logger
from pathlib import Path
from typing import Any, ClassVar, cast

from langchain.embeddings.base import Embeddings
from langchain.tools import StructuredTool
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_core.utils.function_calling import convert_to_openai_function
from pydantic import BaseModel, ConfigDict, Field, create_model

try:
    import faiss
    from langchain_community.vectorstores import FAISS
except ModuleNotFoundError:  # pragma: no cover
    raise ImportError(
        "FAISS is required for vector-store support. "
        "Install with:  pip install 'fmp-data[langchain]'"
    ) from None

from fmp_data.base import BaseClient
from fmp_data.exceptions import ConfigError
from fmp_data.lc.registry import EndpointInfo, EndpointRegistry
from fmp_data.logger import FMPLogger
from fmp_data.models import ParamType


class ToolFactory:
    """Helper class to modularize create_tool behavior"""

    PARAM_TYPE_MAPPING: ClassVar[dict[ParamType, type]] = {
        ParamType.STRING: str,
        ParamType.INTEGER: int,
        ParamType.FLOAT: float,
        ParamType.BOOLEAN: bool,
        ParamType.DATE: date,
        ParamType.DATETIME: datetime,
    }

    @staticmethod
    def get_field_type(param_type: ParamType, optional: bool) -> Any:
        """
        Map ParamType to Python type, including optional wrapper.

        Args:
            param_type: The parameter type from the ParamType enum
            optional: Whether the parameter is optional

        Returns:
            The corresponding Python type
        """

        base_type = ToolFactory.PARAM_TYPE_MAPPING.get(param_type, str)
        return base_type | None if optional else base_type

    @staticmethod
    def generate_description(param: Any, hint: Any | None) -> str:
        """Generate the description string for a parameter."""
        if hint:
            return (
                f"{param.description!s}\n"
                f"Examples: {', '.join(str(ex) for ex in hint.examples)}\n"
                f"Context clues: {', '.join(str(c) for c in hint.context_clues)}"
            )
        return str(param.description)

    @staticmethod
    def create_parameter_fields(
        params: list, parameter_hints: dict[str, Any]
    ) -> dict[str, Any]:
        """Construct field definitions for parameters (mandatory or optional)."""
        param_fields: dict[str, Any] = {}
        for param in params:
            hint = parameter_hints.get(param.name)
            description = ToolFactory.generate_description(param, hint)
            field_type = ToolFactory.get_field_type(
                param.param_type, optional=(param.default is not None)
            )
            param_fields[param.name] = (field_type, Field(description=description))

        return param_fields


class VectorStoreMetadata(BaseModel):
    """Metadata for the vector store"""

    version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    embedding_provider: str = Field(description="Embedding provider name")
    embedding_model: str = Field(description="Embedding model name")
    dimension: int = Field(gt=0, description="Embedding dimension")
    num_vectors: int = Field(default=0, ge=0, description="Number of vectors stored")

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class SearchResult(BaseModel):
    """Search result with similarity score"""

    score: float = Field(description="Similarity score")
    name: str = Field(description="Endpoint name")
    info: EndpointInfo = Field(description="Endpoint information")


class EndpointVectorStore:
    """
    Vector store for semantic endpoint search using FAISS.

    Provides semantic search and LangChain tool creation for FMP API endpoints.

    Args:
        client: FMP API client instance
        registry: Endpoint registry instance
        embeddings: LangChain embeddings instance
        cache_dir: Directory for storing vector store cache
        store_name: Name for this vector store instance

    Examples:
        store = EndpointVectorStore(client, registry, embeddings)
        results = store.search("Find company financials")
        tools = store.get_tools("Get historical prices")
    """

    def __init__(
        self,
        client: BaseClient,
        registry: EndpointRegistry,
        embeddings: Embeddings,
        cache_dir: str | None = None,
        store_name: str = "default",
        logger: Logger | None = None,
    ):
        """Initialize vector store"""
        self.client = client
        self.registry = registry
        self.embeddings = embeddings
        self.logger = logger or FMPLogger().get_logger(__name__)

        # Setup storage paths
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".fmp_cache"
        self.store_dir = self.cache_dir / "vector_stores" / store_name
        self.store_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.store_dir / "faiss_store"
        self.metadata_path = self.store_dir / "metadata.json"

        # Initialize store
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize or load vector store"""
        try:
            if self._store_exists():
                self._load_store()
            else:
                # Get proper dimension from embeddings
                dimension = len(self.embeddings.embed_query("test"))
                index = faiss.IndexFlatL2(dimension)

                self.vector_store = FAISS(
                    embedding_function=self.embeddings,
                    index=index,
                    docstore=InMemoryDocstore(),
                    index_to_docstore_id={},
                )

                # Initialize metadata
                self.metadata = VectorStoreMetadata(
                    embedding_provider=self.embeddings.__class__.__name__,
                    embedding_model=getattr(self.embeddings, "model_name", "default"),
                    dimension=dimension,
                )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector store: {e!s}") from e

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension by testing with a sample text"""
        sample_embedding = self.embeddings.embed_query("test")
        return len(sample_embedding)

    def _store_exists(self) -> bool:
        """Check if store exists on disk"""
        return self.index_path.exists() and self.metadata_path.exists()

    def _load_store(self) -> None:
        """Load stored vectors and metadata"""
        try:
            # Load metadata
            with self.metadata_path.open("r") as f:
                metadata_dict = json.load(f)
            self.metadata = VectorStoreMetadata.model_validate(metadata_dict)

            # Load vector store
            self.vector_store = FAISS.load_local(
                str(self.index_path),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            raise ConfigError(f"Failed to load vector store: {e!s}") from e

    from typing import Any

    from pydantic import BaseModel

    @staticmethod
    def _format_tool_for_provider(
        tool: StructuredTool,
        provider: str = "openai",
    ) -> dict[str, Any] | StructuredTool:
        """
        Convert a LangChain ``StructuredTool`` into the JSON/function spec required
        by a specific provider.

        Args:
            tool:      The LangChain tool to transform.
            provider:  Target provider (“openai”, “anthropic”, …).

        Returns
        -------
        dict | StructuredTool
            * OpenAI → OpenAI-function spec (dict).
            * Anthropic → Claude JSON-tool spec (dict).
            * default → original ``StructuredTool`` unchanged.
        """
        match provider.lower():
            case "openai":
                return convert_to_openai_function(tool)

            case "anthropic":
                if isinstance(tool.args_schema, type) and issubclass(
                    tool.args_schema, BaseModel
                ):
                    model_schema: dict[str, Any] = tool.args_schema.model_json_schema()
                else:
                    # just assign, no new annotation
                    model_schema = tool.args_schema or {}

                return {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": model_schema,
                }

            case _:
                return tool

    def validate(self) -> bool:
        """
        Validate the vector store is usable with current configuration

        Returns:
            bool: True if store is valid, False otherwise
        """
        try:
            # Check if the store has vectors
            if (
                not hasattr(self.vector_store, "index_to_docstore_id")
                or not self.vector_store.index_to_docstore_id
            ):
                self.logger.warning("Vector store has no vectors")
                return False

            # Check if we have metadata that matches our registry
            stored_endpoints = set(self.vector_store.index_to_docstore_id.values())
            registry_endpoints = set(self.registry.list_endpoints().keys())

            if stored_endpoints != registry_endpoints:
                missing = registry_endpoints - stored_endpoints
                extra = stored_endpoints - registry_endpoints
                if missing:
                    self.logger.warning(f"Missing endpoints in store: {missing}")
                if extra:
                    self.logger.warning(f"Extra endpoints in store: {extra}")
                return False

            # Basic embedding check
            try:
                # Try a simple embedding operation
                self.embeddings.embed_query("test")
            except Exception as e:
                self.logger.warning(f"Embedding check failed: {e!s}")
                return False

            return True

        except Exception as e:
            self.logger.warning(f"Store validation failed: {e!s}")
            return False

    def save(self) -> None:
        """Save vector store to disk"""
        try:
            # Update and save metadata
            self.metadata.updated_at = datetime.now()
            self.metadata.num_vectors = len(self.vector_store.index_to_docstore_id)

            with self.metadata_path.open("w") as f:
                json.dump(self.metadata.model_dump(), f, default=str)

            # Save vector store
            self.vector_store.save_local(str(self.index_path))

            self.logger.info(
                f"Saved vector store with {self.metadata.num_vectors} vectors"
            )
        except Exception as e:
            raise ConfigError(f"Failed to save vector store: {e!s}") from e

    def add_endpoint(self, name: str) -> None:
        """Add endpoint to vector store"""
        info = self.registry.get_endpoint(name)
        if not info:
            self.logger.warning(f"Endpoint not found in registry: {name}")
            return

        text = self.registry.get_embedding_text(name)
        if not text:
            self.logger.warning(f"No embedding text for endpoint: {name}")
            return

        metadata = {"endpoint": name}
        document = Document(page_content=text, metadata=metadata)
        self.vector_store.add_documents([document])
        self.logger.debug(f"Added endpoint to vector store: {name}")

    def add_endpoints(self, names: list[str]) -> None:
        """Add multiple endpoints to vector store"""
        if not names:
            raise ValueError("No endpoint names provided")

        documents = []
        skipped_endpoints = set()
        invalid_endpoints = set()

        for name in names:
            try:
                info = self.registry.get_endpoint(name)
                if not info:
                    invalid_endpoints.add(name)
                    continue

                text = self.registry.get_embedding_text(name)
                if not text:
                    self.logger.warning(f"No embedding text for endpoint: {name}")
                    skipped_endpoints.add(name)
                    continue

                doc = Document(page_content=text, metadata={"endpoint": name})
                documents.append(doc)
            except Exception as e:
                self.logger.error(f"Error processing endpoint {name}: {e!s}")
                skipped_endpoints.add(name)

        if invalid_endpoints:
            self.logger.error(f"Invalid endpoints: {sorted(invalid_endpoints)}")

        if skipped_endpoints:
            self.logger.warning(f"Skipped endpoints: {sorted(skipped_endpoints)}")

        if not documents:
            raise RuntimeError("No valid endpoints to add to vector store")

        try:
            self.vector_store.add_documents(documents)
            self.logger.info(
                f"Added {len(documents)} endpoints to vector store "
                f"(skipped {len(skipped_endpoints)})"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to vector store: {e!s}") from e

    def search(
        self, query: str, k: int = 3, threshold: float = 0.3
    ) -> list[SearchResult]:
        """
        Search for relevant endpoints using semantic similarity.

        Args:
            query: Natural language query
            k: Maximum number of results to return
            threshold: Minimum similarity score threshold (0-1)

        Returns:
            List of SearchResult objects containing matches

        Raises:
            ValueError: If invalid k or threshold values
        """
        if k < 1:
            raise ValueError("k must be >= 1")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")

        try:
            results = []
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)

            for doc, score in docs_and_scores:
                similarity = 1 / (1 + score)
                if similarity < threshold:
                    continue

                endpoint_name = cast(str, doc.metadata.get("endpoint"))
                info = self.registry.get_endpoint(endpoint_name)
                if info:
                    results.append(
                        SearchResult(score=similarity, name=endpoint_name, info=info)
                    )

            return sorted(results, key=lambda x: x.score, reverse=True)
        except Exception as e:
            self.logger.error(f"Search failed: {e!s}")
            raise

    def create_tool(self, info: EndpointInfo) -> StructuredTool:
        """Create a LangChain tool from endpoint info."""
        if not info:
            raise ValueError("EndpointInfo cannot be None")
        if not info.endpoint or not info.semantics:
            raise ValueError("Incomplete endpoint information provided")

        try:
            semantics = info.semantics
            endpoint = info.endpoint

            def endpoint_func(**kwargs: Any) -> Any:
                try:
                    result = self.client.request(endpoint, **kwargs)

                    # Handle successful response
                    if isinstance(result, list):
                        return {
                            "status": "success",
                            "data": [
                                (
                                    item.model_dump(mode="json")
                                    if hasattr(item, "model_dump")
                                    else item
                                )
                                for item in result
                            ],
                        }
                    elif hasattr(result, "model_dump"):
                        return {
                            "status": "success",
                            "data": result.model_dump(mode="json"),
                        }
                    return {"status": "success", "data": result}

                except Exception as e:
                    # Handle different types of errors
                    error_message = str(e)
                    error_type = type(e).__name__

                    if "ValidationError" in error_type:
                        # Parse validation error for better feedback
                        error_details = str(e).split("\n")
                        field_errors = [
                            line.strip() for line in error_details if "  " in line
                        ]

                        return {
                            "status": "error",
                            "error_type": "validation_error",
                            "message": "Invalid input parameters or response format",
                            "details": {
                                "validation_errors": field_errors,
                                "original_error": error_message,
                            },
                            "suggestions": [
                                "Check if all required parameters are provided",
                                "Verify parameter types match the expected format",
                                "Ensure date formats are YYYY-MM-DD",
                                "Make sure numeric values are properly formatted",
                            ],
                        }

                    elif "RateLimitError" in error_type:
                        return {
                            "status": "error",
                            "error_type": "rate_limit",
                            "message": "Rate limit exceeded",
                            "details": {"retry_after": getattr(e, "retry_after", None)},
                            "suggestions": [
                                "Wait before making another request",
                                "Consider reducing request frequency",
                            ],
                        }

                    else:
                        return {
                            "status": "error",
                            "error_type": "unexpected_error",
                            "message": f"An unexpected error occurred: {error_message}",
                            "details": {"error_class": error_type},
                            "suggestions": [
                                "Check your input parameters",
                                "Verify the API endpoint is available",
                                "Try again later if the issue persists",
                            ],
                        }

            # Create tool parameters model with fixed create_model call
            tool_args_model = create_model(
                f"{semantics.method_name}Args",
                **ToolFactory.create_parameter_fields(
                    endpoint.mandatory_params + (endpoint.optional_params or []),
                    semantics.parameter_hints,
                ),
                __config__=ConfigDict(
                    extra="forbid",
                    arbitrary_types_allowed=True,
                ),
            )

            # Update description to include error handling information
            full_description = (
                f"{semantics.natural_description}\n\n"
                f"Note: This tool returns a structured response "
                f"with 'status' and 'data'/'error' fields. "
                f"Check 'status' field to handle success/error cases appropriately."
            )

            return StructuredTool.from_function(
                func=endpoint_func,
                name=semantics.method_name,
                description=full_description,
                args_schema=tool_args_model,
                return_direct=True,
                infer_schema=False,
            )

        except Exception as e:
            self.logger.error(f"Failed to create tool: {e!s}", exc_info=True)
            raise RuntimeError(f"Tool creation failed: {e!s}") from e

    def get_tools(
        self,
        query: str | None = None,
        k: int = 3,
        threshold: float = 0.3,
        provider: str | None = None,
    ) -> Sequence[StructuredTool | dict[str, Any]]:
        """
        Get LangChain tools for relevant endpoints.

        Args:
            query: Natural language query (None returns all tools)
            k: Maximum number of tools to return
            threshold: Minimum similarity score threshold (0-1)
            provider: Model provider to format tools for ('openai', 'anthropic', etc)
                     If None, returns unformatted StructuredTool objects

        Returns:
            List of tools (formatted or unformatted based on provider)
        """
        try:
            tools: list[StructuredTool] = []
            if query:
                results = self.search(query, k=k, threshold=threshold)
                tools = [self.create_tool(r.info) for r in results]
            else:
                stored_docs = self.vector_store.similarity_search("", k=10000)
                for doc in stored_docs:
                    endpoint_name = cast(str, doc.metadata.get("endpoint"))
                    info = self.registry.get_endpoint(endpoint_name)
                    if info:
                        tools.append(self.create_tool(info))

            if provider:
                return [
                    self._format_tool_for_provider(tool, provider) for tool in tools
                ]
            return tools

        except Exception as e:
            self.logger.error(f"Failed to get tools: {e!s}")
            raise
