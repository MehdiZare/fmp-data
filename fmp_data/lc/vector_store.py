from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from enum import Enum
import inspect
import json
from logging import Logger
from pathlib import Path
from typing import Any, ClassVar, Literal, Protocol, cast

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.tools import StructuredTool
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
        # A CIK is presented to the LLM as a string; ParamType.CIK zero-pads
        # it on the way out. Mapping it to int would strip the leading zeros
        # the API matches on.
        ParamType.CIK: str,
    }

    @staticmethod
    def get_field_type(
        param_type: ParamType,
        optional: bool,
        valid_values: list[Any] | None = None,
    ) -> Any:
        """
        Map ParamType to Python type, including optional wrapper.

        Args:
            param_type: The parameter type from the ParamType enum
            optional: Whether the parameter is optional
            valid_values: The endpoint's declared allowed values, if any.
                When present, the field is narrowed to a ``Literal`` of those
                values (#156) instead of the bare ``param_type`` mapping, so
                the constraint the client enforces
                (``EndpointParam.validate_value``) reaches the LLM through
                the schema rather than being discovered on a rejected call.

        Returns:
            The corresponding Python type
        """
        if valid_values:
            # Values arrive already unwrapped: EndpointParam.__post_init__
            # replaces Enum members with their wire value. The isinstance
            # branch mirrors EndpointRegistry._get_type_pattern's defensive
            # handling for callers that bypass the dataclass.
            literal_values = tuple(
                value.value if isinstance(value, Enum) else value
                for value in valid_values
            )
            base_type: Any = Literal[literal_values]
        else:
            base_type = ToolFactory.PARAM_TYPE_MAPPING.get(param_type, str)
        return base_type | None if optional else base_type

    @staticmethod
    def get_examples_for_param(param: Any, hint: Any | None) -> list[str]:
        """Derive the examples to advertise for a parameter.

        ``valid_values`` is the client-enforced constraint
        (``EndpointParam.validate_value``); a hint's hand-written ``examples``
        can drift from it -- which is exactly the defect #156 fixes. When the
        endpoint declares ``valid_values``, they are the sole source of
        advertised schema examples, so the schema-examples guard in
        ``tests/unit/lc/test_tool_schema.py`` is true by construction on this
        parameter. ``test_hint_examples_are_within_valid_values`` (#150) is a
        separate pipeline: it still checks the hand-written hint content used
        by embedding text. Falls back to the hint's examples only when the
        endpoint places no constraint on the value.
        """
        valid_values = getattr(param, "valid_values", None)
        if valid_values:
            return [
                str(value.value) if isinstance(value, Enum) else str(value)
                for value in valid_values
            ]
        if hint:
            return [str(ex) for ex in hint.examples]
        return []

    @staticmethod
    def generate_description(
        param: Any, hint: Any | None, examples: Sequence[str] = ()
    ) -> str:
        """Generate the description string for a parameter."""
        lines = [str(param.description)]
        if examples:
            lines.append(f"Examples: {', '.join(examples)}")
        if hint:
            clues = ", ".join(str(c) for c in hint.context_clues)
            lines.append(f"Context clues: {clues}")
        return "\n".join(lines)

    @staticmethod
    def create_parameter_fields(
        mandatory_params: Sequence[Any],
        optional_params: Sequence[Any],
        parameter_hints: dict[str, Any],
    ) -> dict[str, Any]:
        """Construct field definitions for an endpoint's parameters.

        Mandatory-ness is taken from which list a parameter arrives in, never
        inferred from the parameter itself. ``EndpointParam.required`` and
        ``EndpointParam.default`` both disagreed with list membership across
        the catalog: 14 params sat in ``optional_params`` with
        ``required=True``, and 13 more sit in ``mandatory_params`` carrying a
        ``default`` -- so either one would silently mis-shape a schema.
        ``Endpoint`` itself resolves the same question by list membership in
        ``validate_params``.

        The ``required`` half is settled as of #165: the flag is no longer
        stored at all, and ``EndpointParam.required`` is now a read-only
        property that ``Endpoint`` derives from these very lists. Reading it
        here would be correct today but circular -- it would route the answer
        through the parameter to get back the list it came from -- so the list
        stays the direct source. The ``default`` half is still live, and
        reading *that* would still be wrong.

        Optional parameters get a pydantic default so ``is_required()`` is
        false and the LLM may omit them. That default is ``param.default``
        rather than ``None`` whenever the endpoint declares one:
        ``validate_params`` marks a param seen before it skips a ``None``
        value, so passing ``None`` explicitly suppresses the default it would
        otherwise have applied on the way out.

        That last step depends on langchain forwarding fields that hold
        explicit defaults -- see ``BaseTool._parse_input``, which has in the
        past used the narrower ``if k in tool_input`` filter, and note that
        ``langchain-core`` is pinned ``>=1.4.9`` with no upper bound. If it
        ever stops forwarding them, declared defaults silently stop reaching
        the API. ``test_omitted_optional_reaches_the_endpoint_with_its_
        declared_default`` drives a real ``StructuredTool`` to pin it.
        """
        param_fields: dict[str, Any] = {}

        for param in mandatory_params:
            hint = parameter_hints.get(param.name)
            examples = ToolFactory.get_examples_for_param(param, hint)
            description = ToolFactory.generate_description(param, hint, examples)
            field_type = ToolFactory.get_field_type(
                param.param_type, optional=False, valid_values=param.valid_values
            )
            field_kwargs: dict[str, Any] = {"description": description}
            if examples:
                field_kwargs["examples"] = examples
            param_fields[param.name] = (field_type, Field(**field_kwargs))

        for param in optional_params:
            hint = parameter_hints.get(param.name)
            examples = ToolFactory.get_examples_for_param(param, hint)
            description = ToolFactory.generate_description(param, hint, examples)
            field_type = ToolFactory.get_field_type(
                param.param_type, optional=True, valid_values=param.valid_values
            )
            field_kwargs = {"default": param.default, "description": description}
            if examples:
                field_kwargs["examples"] = examples
            param_fields[param.name] = (field_type, Field(**field_kwargs))

        return param_fields


def _camel_to_snake(name: str) -> str:
    """Convert ``periodLength`` / ``sicCode`` to ``period_length`` / ``sic_code``."""
    parts: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index:
            parts.append("_")
            parts.append(char.lower())
        else:
            parts.append(char.lower() if char.isupper() else char)
    return "".join(parts)


#: Endpoint-param name -> ordered method-param candidates.
#:
#: Client methods are the call surface MCP already uses
#: (``fmp_client.<client>.<method>``). Their parameter names are ordinary
#: Python (``from_date``, ``sic_code``, ``period_length``), while endpoint
#: declarations keep the wire names (``from``, ``sicCode``, ``periodLength``).
#: LangChain tools historically mirrored the wire names; #172 maps them so
#: tools can dispatch through the method without renaming every schema field.
_ENDPOINT_TO_METHOD_ALIASES: Mapping[str, tuple[str, ...]] = {
    "from": ("from", "from_date", "start_date"),
    "to": ("to", "to_date", "end_date"),
    "start_date": ("start_date", "from_date"),
    "end_date": ("end_date", "to_date"),
    # economics.get_economic_indicators renames the wire ``name`` param.
    "name": ("name", "indicator_name", "query"),
    # Several clients take a single report/as-of day under a different name.
    "date": ("date", "report_date", "holdings_date", "target_date"),
    # sec.search_company_by_name: endpoint ``company``, method ``name``.
    "company": ("company", "name"),
}


def method_param_aliases(endpoint_param: str) -> tuple[str, ...]:
    """Ordered method-parameter names that may correspond to *endpoint_param*."""
    aliases = list(_ENDPOINT_TO_METHOD_ALIASES.get(endpoint_param, (endpoint_param,)))
    snake = _camel_to_snake(endpoint_param)
    if snake not in aliases:
        aliases.append(snake)
    return tuple(aliases)


def resolve_method_param_name(
    endpoint_param: str, method_params: set[str]
) -> str | None:
    """Pick the method parameter that should receive *endpoint_param*'s value."""
    for candidate in method_param_aliases(endpoint_param):
        if candidate in method_params:
            return candidate
    return None


def resolve_client_method(
    client: Any, client_name: str, method_name: str
) -> Callable[..., Any] | None:
    """Resolve ``client.<client_name>.<method_name>``, or ``None`` if missing.

    Returns ``None`` rather than raising so tool creation still works when the
    store holds a bare :class:`~fmp_data.base.BaseClient` (or a test double)
    that has no sub-clients. Dispatch then falls back to ``client.request``.
    """
    subclient = getattr(client, client_name, None)
    if subclient is None:
        return None
    method = getattr(subclient, method_name, None)
    if method is None or not callable(method):
        return None
    return cast(Callable[..., Any], method)


def map_tool_kwargs_to_method(
    method: Callable[..., Any], kwargs: Mapping[str, Any]
) -> dict[str, Any]:
    """Translate tool kwargs (endpoint/wire names) onto *method*'s signature.

    ``None`` values are dropped so a method default can apply — that is the
    half of #172 that makes an LLM-omitted ``from``/``to`` still work on SEC
    search methods, which default the window to the last 30 days.
    """
    signature = inspect.signature(method)
    method_params = {
        name
        for name, param in signature.parameters.items()
        if name != "self"
        and param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    mapped: dict[str, Any] = {}
    for endpoint_name, value in kwargs.items():
        if value is None:
            continue
        method_name = resolve_method_param_name(endpoint_name, method_params)
        if method_name is not None:
            mapped[method_name] = value
    return mapped


def partition_params_for_method(
    mandatory_params: Sequence[Any],
    optional_params: Sequence[Any],
    method: Callable[..., Any] | None,
) -> tuple[list[Any], list[Any]]:
    """Reclassify endpoint params by the client method's defaults (#172).

    When *method* is available, an endpoint-mandatory parameter whose mapped
    method parameter has a default becomes optional in the tool schema — the
    method will fill it. Without a resolvable method the endpoint lists are
    returned unchanged (the pre-#172 behaviour).
    """
    if method is None:
        return list(mandatory_params), list(optional_params)

    signature = inspect.signature(method)
    method_params = {
        name: param for name, param in signature.parameters.items() if name != "self"
    }
    method_names = set(method_params)

    new_mandatory: list[Any] = []
    new_optional: list[Any] = list(optional_params)
    for param in mandatory_params:
        method_name = resolve_method_param_name(param.name, method_names)
        if method_name is None:
            # Method does not accept this wire param; keep it mandatory so the
            # schema does not silently drop a required API field for tools that
            # still fall back to ``client.request``.
            new_mandatory.append(param)
            continue
        method_param = method_params[method_name]
        if method_param.default is inspect.Parameter.empty:
            new_mandatory.append(param)
        else:
            new_optional.append(param)
    return new_mandatory, new_optional


class ToolLike(Protocol):
    """Minimal protocol for tool objects returned by this module."""

    name: str
    description: str
    args_schema: Any


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
        allow_dangerous_deserialization: bool = False,
    ):
        """Initialize vector store

        Args:
            client: FMP API client instance
            registry: Endpoint registry instance
            embeddings: LangChain embeddings instance
            cache_dir: Directory for storing vector store cache
            store_name: Name for this vector store instance
            logger: Optional logger instance
            allow_dangerous_deserialization: If True, allows loading pickled data from
                the cached FAISS index. Only enable this if you trust the source of
                the cache files. Defaults to False for security.
        """
        self.client = client
        self.registry = registry
        self.embeddings = embeddings
        self.logger = logger or FMPLogger().get_logger(__name__)
        self._allow_dangerous_deserialization = allow_dangerous_deserialization

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

                try:
                    from langchain_community.docstore.in_memory import InMemoryDocstore
                except ModuleNotFoundError as exc:  # pragma: no cover
                    raise ImportError(
                        "LangChain dependencies not available. "
                        "Install with: pip install 'fmp-data[langchain]'"
                    ) from exc

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
            if isinstance(e, ConfigError):
                raise
            raise RuntimeError(f"Failed to initialize vector store: {e!s}") from e

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension by testing with a sample text"""
        sample_embedding = self.embeddings.embed_query("test")
        return len(sample_embedding)

    def _store_exists(self) -> bool:
        """Check if store exists on disk"""
        return self.index_path.exists() and self.metadata_path.exists()

    def _load_store(self) -> None:
        """Load stored vectors and metadata

        Raises:
            ConfigError: If loading fails or if dangerous deserialization is not allowed
        """
        if not self._allow_dangerous_deserialization:
            raise ConfigError(
                "Cannot load cached vector store: "
                "allow_dangerous_deserialization=False. "
                "Loading a cached FAISS index involves deserializing pickled "
                "data which can execute arbitrary code. Only enable this if "
                "you trust the cache source. "
                "Set allow_dangerous_deserialization=True to load cached stores."
            )

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
        except ConfigError:
            raise
        except json.JSONDecodeError as e:
            raise ConfigError(f"Failed to parse vector store metadata: {e!s}") from e
        except OSError as e:
            raise ConfigError(f"Failed to read vector store files: {e!s}") from e
        except Exception as e:
            raise ConfigError(f"Failed to load vector store: {e!s}") from e

    @staticmethod
    def _format_tool_for_provider(
        tool: ToolLike,
        provider: str = "openai",
    ) -> dict[str, Any] | ToolLike:
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
                try:
                    from langchain_core.utils.function_calling import (
                        convert_to_openai_function,
                    )
                except ModuleNotFoundError as exc:  # pragma: no cover
                    raise ImportError(
                        "LangChain dependencies not available. "
                        "Install with: pip install 'fmp-data[langchain]'"
                    ) from exc
                if not isinstance(tool, StructuredTool):
                    raise TypeError("OpenAI tool conversion requires StructuredTool")
                result = convert_to_openai_function(tool)
                if not isinstance(result, dict):
                    raise TypeError("OpenAI tool conversion returned non-dict")
                return result

            case "anthropic":
                model_schema: dict[str, Any]
                if isinstance(tool.args_schema, type) and issubclass(
                    tool.args_schema, BaseModel
                ):
                    model_schema = tool.args_schema.model_json_schema()
                else:
                    raw_schema = tool.args_schema or {}
                    if not isinstance(raw_schema, dict):
                        raise TypeError("Tool args schema must be a dict")
                    model_schema = raw_schema

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
            index_to_docstore_id = getattr(
                self.vector_store, "index_to_docstore_id", None
            )
            if not index_to_docstore_id:
                self.logger.warning("Vector store has no vectors")
                return False

            # Check if we have metadata that matches our registry
            stored_endpoints = set(index_to_docstore_id.values())
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
        """Save vector store to disk

        Raises:
            ConfigError: If saving fails due to IO or serialization errors
        """
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
        except OSError as e:
            raise ConfigError(f"Failed to write vector store files: {e!s}") from e
        except (TypeError, ValueError) as e:
            raise ConfigError(f"Failed to serialize vector store data: {e!s}") from e
        except Exception as e:
            raise ConfigError(f"Failed to save vector store: {e!s}") from e

    @staticmethod
    def _is_deprecated(info: EndpointInfo) -> bool:
        """Whether an endpoint no longer returns data (#137).

        Deprecated endpoints stay in the semantics tables -- their MCP tool
        keys must keep resolving for explicit manifests, and the catalog count
        must not move -- but they are kept out of this store entirely, because
        an LLM that selects one gets an empty *success* it cannot tell apart
        from "no data matched your query".

        Distinct from ``fmp_data.mcp.tools_manifest.DEPRECATED_TOOLS``, which
        maps duplicate tool *names* onto the canonical name of a method that
        still works. See ``EndpointSemantics.deprecated``; do not merge them.

        Typed ``EndpointInfo`` (#159) rather than ``Any`` with a
        ``getattr(..., default=False)`` fallback: that combination made a
        renamed or dropped ``deprecated`` field fail silently into "nothing is
        deprecated" instead of a mypy error or an ``AttributeError``. Reading
        the field directly means a rename is caught at type-check time.
        """
        return info.semantics.deprecated

    def add_endpoint(self, name: str) -> None:
        """Add endpoint to vector store.

        Deprecated endpoints are skipped -- see :meth:`_is_deprecated`.
        """
        info = self.registry.get_endpoint(name)
        if not info:
            self.logger.warning(f"Endpoint not found in registry: {name}")
            return

        if self._is_deprecated(info):
            self.logger.debug(f"Skipping deprecated endpoint: {name}")
            return

        text = self.registry.get_embedding_text(name)
        if not text:
            self.logger.warning(f"No embedding text for endpoint: {name}")
            return

        metadata = {"endpoint": name}
        document = Document(page_content=text, metadata=metadata)
        self.vector_store.add_documents([document])
        self.logger.debug(f"Added endpoint to vector store: {name}")

    def _classify_endpoint(self, name: str) -> tuple[str, Document | None]:
        """Sort one endpoint into ``ok`` / ``invalid`` / ``deprecated`` / ``skip``.

        Split out of :meth:`add_endpoints` purely to keep that method under the
        complexity limit; it holds no state of its own.
        """
        try:
            info = self.registry.get_endpoint(name)
            if not info:
                return "invalid", None

            if self._is_deprecated(info):
                return "deprecated", None

            text = self.registry.get_embedding_text(name)
            if not text:
                self.logger.warning(f"No embedding text for endpoint: {name}")
                return "skip", None

            return "ok", Document(page_content=text, metadata={"endpoint": name})
        except Exception as e:
            self.logger.error(f"Error processing endpoint {name}: {e!s}")
            return "skip", None

    def add_endpoints(self, names: list[str]) -> int:
        """Add multiple endpoints to vector store.

        Deprecated endpoints are skipped -- see :meth:`_is_deprecated`. They are
        counted separately from ``skipped_endpoints`` because being deprecated
        is a deliberate exclusion, not a defect worth a warning.

        Returns:
            How many endpoints were actually indexed. Callers offering the whole
            catalog get back fewer than they passed, so reporting the input
            length would overstate the store's contents.
        """
        if not names:
            raise ValueError("No endpoint names provided")

        documents: list[Document] = []
        buckets: dict[str, set[str]] = {
            "invalid": set(),
            "deprecated": set(),
            "skip": set(),
        }

        for name in names:
            outcome, document = self._classify_endpoint(name)
            if document is not None:
                documents.append(document)
            else:
                buckets[outcome].add(name)

        invalid_endpoints = buckets["invalid"]
        skipped_endpoints = buckets["skip"]
        deprecated_endpoints = buckets["deprecated"]

        if invalid_endpoints:
            self.logger.error(f"Invalid endpoints: {sorted(invalid_endpoints)}")

        if skipped_endpoints:
            self.logger.warning(f"Skipped endpoints: {sorted(skipped_endpoints)}")

        if deprecated_endpoints:
            self.logger.info(
                f"Excluded {len(deprecated_endpoints)} deprecated endpoints: "
                f"{sorted(deprecated_endpoints)}"
            )

        if not documents:
            raise RuntimeError("No valid endpoints to add to vector store")

        try:
            self.vector_store.add_documents(documents)
            self.logger.info(
                f"Added {len(documents)} endpoints to vector store "
                f"(skipped {len(skipped_endpoints)}, "
                f"deprecated {len(deprecated_endpoints)})"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to vector store: {e!s}") from e

        return len(documents)

    #: How many widening fetches :meth:`search` may make. A store persisted by
    #: an earlier release still carries deprecated endpoints in its backing
    #: index; they are filtered out here, but a plain top-k fetch lets each one
    #: consume a slot, so ``search(query, k=3)`` would quietly return two live
    #: endpoints -- under-recall in exactly the stale-index case this filtering
    #: exists for. Each round doubles the window, and the loop stops as soon as
    #: k results are live, nothing was displaced, or the index is exhausted.
    _SEARCH_FETCH_ROUNDS = 3

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
            List of SearchResult objects containing matches. Never more than
            ``k``; deprecated entries in a stale index do not reduce the count
            below ``k`` while live matches remain.

        Raises:
            ValueError: If invalid k or threshold values
        """
        if k < 1:
            raise ValueError("k must be >= 1")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")

        try:
            fetch_k = k
            results: list[SearchResult] = []
            for _ in range(self._SEARCH_FETCH_ROUNDS):
                docs_and_scores = self.vector_store.similarity_search_with_score(
                    query, k=fetch_k
                )
                results, displaced = self._collect_live_results(
                    docs_and_scores, threshold
                )
                index_exhausted = len(docs_and_scores) < fetch_k
                if len(results) >= k or not displaced or index_exhausted:
                    break
                fetch_k *= 2

            results.sort(key=lambda x: x.score, reverse=True)
            return results[:k]
        except Exception as e:
            self.logger.error(f"Search failed: {e!s}")
            raise

    def _collect_live_results(
        self, docs_and_scores: Sequence[tuple[Any, float]], threshold: float
    ) -> tuple[list[SearchResult], int]:
        """Turn raw hits into results, dropping deprecated and unknown entries.

        Returns the results plus how many hits were *displaced* -- dropped for
        a reason a wider fetch can compensate for. Hits below ``threshold`` are
        not counted: those are a genuine relevance cut, and re-fetching would
        only surface less relevant matches.
        """
        results: list[SearchResult] = []
        displaced = 0
        for doc, score in docs_and_scores:
            similarity = 1 / (1 + score)
            if similarity < threshold:
                continue

            endpoint_name = doc.metadata.get("endpoint")
            if not isinstance(endpoint_name, str):
                displaced += 1
                continue
            info = self.registry.get_endpoint(endpoint_name)
            if info is None or self._is_deprecated(info):
                displaced += 1
                continue
            results.append(
                SearchResult(score=similarity, name=endpoint_name, info=info)
            )
        return results, displaced

    def _serialize_result(self, result: Any) -> dict[str, Any]:
        """Serialize result, converting Pydantic models to JSON."""
        if isinstance(result, list):
            data = []
            for item in result:
                dump = getattr(item, "model_dump", None)
                data.append(dump(mode="json") if callable(dump) else item)
            return {"status": "success", "data": data}
        # Single result
        model_dump = getattr(result, "model_dump", None)
        if callable(model_dump):
            return {"status": "success", "data": model_dump(mode="json")}
        return {"status": "success", "data": result}

    def create_tool(self, info: EndpointInfo) -> ToolLike:
        """Create a LangChain tool from endpoint info.

        Dispatch goes through the client method named by
        ``EndpointSemantics.method_name`` (the same path MCP uses) so
        method-level defaults and constraints apply. See #172. When the store
        holds a client without that sub-client (tests, bare ``BaseClient``),
        dispatch falls back to ``client.request(endpoint, ...)``.
        """
        if not info:
            raise ValueError("EndpointInfo cannot be None")
        if not info.endpoint or not info.semantics:
            raise ValueError("Incomplete endpoint information provided")

        try:
            semantics = info.semantics
            endpoint = info.endpoint
            method = resolve_client_method(
                self.client, semantics.client_name, semantics.method_name
            )
            mandatory_params, optional_params = partition_params_for_method(
                endpoint.mandatory_params,
                endpoint.optional_params or [],
                method,
            )

            def endpoint_func(**kwargs: Any) -> Any:
                try:
                    if method is not None:
                        result = method(**map_tool_kwargs_to_method(method, kwargs))
                    else:
                        result = self.client.request(endpoint, **kwargs)
                    return self._serialize_result(result)

                except Exception as e:
                    # Handle different types of errors
                    error_message = str(e)
                    error_type = type(e).__name__

                    # ValueError covers method-level constraints the endpoint
                    # cannot express (e.g. SEC search_industry_classification
                    # requiring at least one of symbol/cik/sic_code).
                    if "ValidationError" in error_type or error_type == "ValueError":
                        # Parse validation error for better feedback
                        error_details = str(e).split("\n")
                        field_errors = [
                            line.strip() for line in error_details if "  " in line
                        ]
                        if not field_errors:
                            field_errors = [error_message]

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
                    mandatory_params,
                    optional_params,
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

            tool: StructuredTool = StructuredTool.from_function(
                func=endpoint_func,
                name=semantics.method_name,
                description=full_description,
                args_schema=tool_args_model,
                return_direct=True,
                infer_schema=False,
            )
            return cast(ToolLike, tool)

        except Exception as e:
            self.logger.error(f"Failed to create tool: {e!s}", exc_info=True)
            raise RuntimeError(f"Tool creation failed: {e!s}") from e

    def get_tools(
        self,
        query: str | None = None,
        k: int = 3,
        threshold: float = 0.3,
        provider: str | None = None,
    ) -> Sequence[ToolLike | dict[str, Any]]:
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

        Note:
            Deprecated endpoints are excluded here as well as at index time
            (:meth:`_is_deprecated`). Filtering only on the way in would leave a
            store persisted by an earlier release still serving them, which is
            exactly the state #137 describes.
        """
        try:
            tools: list[ToolLike] = []
            if query:
                results = self.search(query, k=k, threshold=threshold)
                tools = [self.create_tool(r.info) for r in results]
            else:
                stored_docs = self.vector_store.similarity_search("", k=10000)
                for doc in stored_docs:
                    endpoint_name = doc.metadata.get("endpoint")
                    if not isinstance(endpoint_name, str):
                        continue
                    info = self.registry.get_endpoint(endpoint_name)
                    if info and not self._is_deprecated(info):
                        tools.append(self.create_tool(info))

            if provider:
                return [
                    self._format_tool_for_provider(tool, provider) for tool in tools
                ]
            return tools

        except Exception as e:
            self.logger.error(f"Failed to get tools: {e!s}")
            raise
