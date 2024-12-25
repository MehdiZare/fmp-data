# fmp_data/lc/vector_store.py
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import faiss
from langchain.embeddings.base import Embeddings
from langchain.tools import StructuredTool
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from pydantic import BaseModel, ConfigDict, Field, create_model

from fmp_data.base import BaseClient
from fmp_data.exceptions import ConfigError
from fmp_data.lc.registry import EndpointInfo, EndpointRegistry
from fmp_data.logger import FMPLogger
from fmp_data.models import ParamType

logger = FMPLogger().get_logger(__name__)


class ToolFactory:
    """Helper class to modularize create_tool behavior"""

    PARAM_TYPE_MAPPING = {
        ParamType.STRING: str,
        ParamType.INTEGER: int,
        ParamType.FLOAT: float,
        ParamType.BOOLEAN: bool,
        ParamType.DATE: date,
        ParamType.DATETIME: datetime,
    }

    @staticmethod
    def get_field_type(param_type: ParamType, optional: bool) -> Any:
        """Map ParamType to Python type, including optional wrapper."""
        base_type = ToolFactory.PARAM_TYPE_MAPPING.get(param_type, str)
        return base_type | None if optional else base_type

    @staticmethod
    def generate_description(param: Any, hint: Any | None) -> str:
        """Generate the description string for a parameter."""
        if hint:
            return (
                f"{param.description}\n"
                f"Examples: {', '.join(hint.examples)}\n"
                f"Context clues: {', '.join(hint.context_clues)}"
            )
        return param.description

    @staticmethod
    def create_parameter_fields(
        params: list, parameter_hints: dict
    ) -> dict[str, tuple]:
        """Construct field definitions for parameters (mandatory or optional)."""
        param_fields = {}
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
    """Vector store for semantic endpoint search using
    LangChain's FAISS implementation"""

    def __init__(
        self,
        client: BaseClient,
        registry: EndpointRegistry,
        embeddings: Embeddings,
        cache_dir: str | None = None,
        store_name: str = "default",
    ):
        """Initialize vector store"""
        self.client = client
        self.registry = registry
        self.embeddings = embeddings

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
        if self._store_exists():
            self._load_store()
        else:
            index = faiss.IndexFlatL2(self._get_embedding_dimension())

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
                dimension=self._get_embedding_dimension(),
            )

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
            raise ConfigError(f"Failed to load vector store: {str(e)}") from e

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
                logger.warning("Vector store has no vectors")
                return False

            # Check if we have metadata that matches our registry
            stored_endpoints = set(self.vector_store.index_to_docstore_id.values())
            registry_endpoints = set(self.registry.list_endpoints().keys())

            if stored_endpoints != registry_endpoints:
                missing = registry_endpoints - stored_endpoints
                extra = stored_endpoints - registry_endpoints
                if missing:
                    logger.warning(f"Missing endpoints in store: {missing}")
                if extra:
                    logger.warning(f"Extra endpoints in store: {extra}")
                return False

            # Basic embedding check
            try:
                # Try a simple embedding operation
                self.embeddings.embed_query("test")
            except Exception as e:
                logger.warning(f"Embedding check failed: {str(e)}")
                return False

            return True

        except Exception as e:
            logger.warning(f"Store validation failed: {str(e)}")
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

            logger.info(f"Saved vector store with {self.metadata.num_vectors} vectors")
        except Exception as e:
            raise ConfigError(f"Failed to save vector store: {str(e)}") from e

    def add_endpoint(self, name: str) -> None:
        """Add endpoint to vector store"""
        info = self.registry.get_endpoint(name)
        if not info:
            logger.warning(f"Endpoint not found in registry: {name}")
            return

        text = self.registry.get_embedding_text(name)
        if not text:
            logger.warning(f"No embedding text for endpoint: {name}")
            return

        metadata = {"endpoint": name}
        document = Document(page_content=text, metadata=metadata)
        self.vector_store.add_documents([document])
        logger.debug(f"Added endpoint to vector store: {name}")

    # In EndpointVectorStore class

    def add_endpoints(self, names: list[str]) -> None:
        """Add multiple endpoints to vector store"""
        documents = []
        skipped_endpoints = set()

        for name in names:
            info = self.registry.get_endpoint(name)
            text = self.registry.get_embedding_text(name)
            if info and text:
                doc = Document(page_content=text, metadata={"endpoint": name})
                documents.append(doc)
            else:
                skipped_endpoints.add(name)
                if not info:
                    logger.warning(f"Skipping endpoint {name}: missing endpoint info")
                if not text:
                    logger.warning(f"Skipping endpoint {name}: missing embedding text")

        if documents:
            self.vector_store.add_documents(documents)
            logger.debug(
                f"Added {len(documents)} endpoints to vector store "
                f"(skipped {len(skipped_endpoints)})"
            )
            if skipped_endpoints:
                logger.debug(f"Skipped endpoints: {skipped_endpoints}")
        else:
            logger.warning("No valid endpoints to add to vector store")

    def search(
        self, query: str, k: int = 3, threshold: float = 0.3
    ) -> list[SearchResult]:
        """Search for relevant endpoints"""
        results = []
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)

        for doc, score in docs_and_scores:
            # Convert distance to similarity score (FAISS returns L2 distance)
            similarity = 1 / (1 + score)
            if similarity < threshold:
                continue

            name = doc.metadata.get("endpoint")
            info = self.registry.get_endpoint(name)
            if info:
                results.append(SearchResult(score=similarity, name=name, info=info))

        return sorted(results, key=lambda x: x.score, reverse=True)

    # pylint: disable=C901
    def create_tool(self, info: EndpointInfo) -> StructuredTool:
        """Create a LangChain tool from endpoint info"""
        semantics = info.semantics
        endpoint = info.endpoint

        # Create function to handle endpoint call
        def endpoint_func(**kwargs: Any) -> Any:
            return self.client.request(endpoint, **kwargs)

        # Collect parameter fields
        param_fields = {}

        # Add mandatory parameters
        param_fields.update(
            ToolFactory.create_parameter_fields(
                endpoint.mandatory_params, semantics.parameter_hints
            )
        )

        # Add optional parameters
        if endpoint.optional_params:
            param_fields.update(
                ToolFactory.create_parameter_fields(
                    endpoint.optional_params, semantics.parameter_hints
                )
            )

        # Create tool parameters model
        tool_args_model = create_model(f"{semantics.method_name}Args", **param_fields)

        # Create tool description
        tool_description = (
            f"{semantics.natural_description}\n\n"
            f"Examples:\n"
            f"{chr(10).join(f'- {q}' for q in semantics.example_queries)}\n\n"
            f"Use cases:\n"
            f"{chr(10).join(f'- {u}' for u in semantics.use_cases)}"
        )

        return StructuredTool.from_function(
            func=endpoint_func,
            name=semantics.method_name,
            description=tool_description,
            args_schema=tool_args_model,
            return_direct=True,
        )

    def get_tools(
        self, query: str | None = None, k: int = 3, threshold: float = 0.3
    ) -> list[StructuredTool]:
        """Get LangChain tools for relevant endpoints"""
        if query:
            results = self.search(query, k=k, threshold=threshold)
            return [self.create_tool(r.info) for r in results]
        else:
            # Get all stored endpoints
            stored_docs = self.vector_store.similarity_search("", k=10000)
            tools = []
            for doc in stored_docs:
                name = doc.metadata.get("endpoint")
                info = self.registry.get_endpoint(name)
                if info:
                    tools.append(self.create_tool(info))
            return tools
