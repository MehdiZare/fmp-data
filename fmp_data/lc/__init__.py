# fmp_data/lc/__init__.py
"""
LangChain integration for FMP Data API.
Relative path: fmp_data/lc/__init__.py

This module provides LangChain integration features including:
- Semantic search for API endpoints
- LangChain tool creation
- Vector store management
- Natural language endpoint discovery

Heavy LangChain imports are deferred so domain mapping modules can import
``fmp_data.lc.models`` (and MCP discovery can load semantics) without the
``langchain`` extra installed.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, NamedTuple

from fmp_data.exceptions import VectorStoreCreationError
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.registry import EndpointRegistry, resolve_semantics_for_endpoint
from fmp_data.lc.utils import is_langchain_available
from fmp_data.logger import FMPLogger

# Only import for type checking, not at runtime
if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

    from fmp_data.client import FMPDataClient
    from fmp_data.lc.config import LangChainConfig
    from fmp_data.lc.embedding import EmbeddingProvider
    from fmp_data.lc.vector_store import EndpointVectorStore
    from fmp_data.models import Endpoint

logger = FMPLogger().get_logger(__name__)


def __getattr__(name: str) -> Any:
    """Lazy-export symbols that require the optional langchain extra."""
    if name == "EmbeddingProvider":
        from fmp_data.lc.embedding import EmbeddingProvider

        return EmbeddingProvider
    if name == "EndpointVectorStore":
        from fmp_data.lc.vector_store import EndpointVectorStore

        return EndpointVectorStore
    if name == "LangChainConfig":
        from fmp_data.lc.config import LangChainConfig

        return LangChainConfig
    # Not in ``__all__``, but importable from this module before the lazy-import
    # rework -- keep them reachable so ``from fmp_data.lc import Endpoint`` and
    # ``from fmp_data.lc import Embeddings`` do not start raising AttributeError.
    if name == "Endpoint":
        from fmp_data.models import Endpoint

        return Endpoint
    if name == "Embeddings":
        from langchain_core.embeddings import Embeddings

        return Embeddings
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Include lazily-exported names so REPL/IDE completion still finds them."""
    return sorted({*globals(), *__all__, "Endpoint", "Embeddings"})


def init_langchain() -> bool:
    """
    Initialize LangChain integration if dependencies are available.

    Returns:
        bool: True if initialization successful, False otherwise
    """
    if not is_langchain_available():
        logger.warning(
            "LangChain dependencies not available. "
            "Install with: pip install 'fmp-data[langchain]'"
        )
        return False
    return True


def validate_api_keys(
    fmp_api_key: str | None = None, openai_api_key: str | None = None
) -> tuple[str, str]:
    """Validate and retrieve API keys from args or environment."""
    fmp_key = fmp_api_key or os.getenv("FMP_API_KEY")
    if not fmp_key:
        raise ValueError(
            "FMP API key required. Provide as argument "
            "or set FMP_API_KEY environment variable"
        )

    openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError(
            "OpenAI API key required for embeddings. "
            "Provide as argument or set OPENAI_API_KEY environment variable"
        )

    return fmp_key, openai_key


class RegistrySetup(NamedTuple):
    """What :func:`setup_registry` built, and what did not make it in.

    ``register_batch`` returns a per-endpoint failure dict; ``setup_registry``
    used to inspect it, log a summary and drop it, so the only way to learn
    which endpoints were skipped was to parse logs (#133's closing note). It is
    now returned alongside the registry.

    A ``NamedTuple`` so ``registry, failures = setup_registry(client)`` reads
    naturally and ``result.failures`` stays self-describing.
    """

    registry: EndpointRegistry
    failures: dict[str, str]


def setup_registry(client: FMPDataClient) -> RegistrySetup:
    """
    Initialize and populate endpoint registry.

    Args:
        client: The FMP Data client instance

    Returns:
        The configured registry, plus a mapping of endpoint name to the
        validation error that kept it out. Empty when everything registered.

    Note:
        **Breaking in 2.6** -- this used to return a bare ``EndpointRegistry``.
        Change ``registry = setup_registry(client)`` to
        ``registry, failures = setup_registry(client)`` (or use
        ``.registry``).
    """
    from fmp_data.models import Endpoint

    endpoint_registry = EndpointRegistry()
    all_failures: dict[str, str] = {}

    # Get endpoint groups with lazy loading to avoid circular imports
    from fmp_data.lc.registry import get_endpoint_groups

    endpoint_groups = get_endpoint_groups()

    # Register endpoints from all client modules using the actual interface
    for group_name, group_config in endpoint_groups.items():
        endpoint_map = group_config["endpoint_map"]
        semantics_map = group_config["semantics_map"]

        # Transform to the format expected by register_batch:
        # dict[str, tuple[Endpoint, EndpointSemantics]]
        endpoints_for_batch: dict[str, tuple[Endpoint[Any], EndpointSemantics]] = {}

        for endpoint_name, endpoint in endpoint_map.items():
            semantics = resolve_semantics_for_endpoint(endpoint_name, semantics_map)

            if semantics is not None:
                endpoints_for_batch[endpoint_name] = (endpoint, semantics)
            else:
                logger.warning(f"No semantics found for endpoint: {endpoint_name}")

        # Register the batch for this group. Invalid endpoints are skipped
        # individually so drift in one endpoint cannot drop the whole group.
        if endpoints_for_batch:
            failures = endpoint_registry.register_batch(endpoints_for_batch)
            registered = len(endpoints_for_batch) - len(failures)
            logger.debug(
                f"Registered {registered}/{len(endpoints_for_batch)} "
                f"endpoints from {group_name}"
            )
            if failures:
                all_failures.update(failures)
                logger.warning(
                    f"Skipped {len(failures)} invalid {group_name} endpoints: "
                    f"{', '.join(sorted(failures))}"
                )

    return RegistrySetup(registry=endpoint_registry, failures=all_failures)


def create_vector_store(
    fmp_api_key: str | None = None,
    openai_api_key: str | None = None,
    cache_dir: str | None = None,
    store_name: str = "fmp_endpoints",
    force_create: bool = False,
    embedding_provider: EmbeddingProvider | None = None,
    embedding_model: str | None = None,
) -> EndpointVectorStore:
    """
    Create a vector store for endpoint semantic search.

    Args:
        fmp_api_key: FMP API key (or from env)
        openai_api_key: OpenAI API key (or from env)
        cache_dir: Directory to store vector index
        store_name: Name for the vector store
        force_create: Whether to recreate existing store
        embedding_provider: Provider for embeddings (default: OpenAI)
        embedding_model: Specific model name

    Returns:
        Configured vector store.

    Raises:
        VectorStoreCreationError: if the store cannot be built. Carries the
            underlying exception as ``cause`` and any endpoints skipped during
            registration as ``failures``.

    Note:
        **Breaking in 2.6** -- this used to return ``None`` on any failure.
        Replace ``store = create_vector_store(...); if store is None: ...``
        with a ``try``/``except VectorStoreCreationError`` block. ``None`` was
        reachable from exactly one place, the blanket handler below, so it
        never distinguished one failure from another; it also swallowed the
        errors #121/#127 made ``setup_registry`` propagate.
    """
    # Late import to avoid circular dependency and optional langchain deps
    from fmp_data.client import FMPDataClient
    from fmp_data.lc.embedding import EmbeddingConfig
    from fmp_data.lc.embedding import EmbeddingProvider as EP

    if embedding_provider is None:
        embedding_provider = EP.OPENAI

    # Bound outside the try so a failure *after* registration can still report
    # which endpoints were skipped on the way here.
    failures: dict[str, str] = {}

    try:
        # Validate API keys
        fmp_key, openai_key = validate_api_keys(fmp_api_key, openai_api_key)

        # Create client
        client = FMPDataClient(api_key=fmp_key)

        # Setup registry
        registry, failures = setup_registry(client)

        embedding_config = EmbeddingConfig(
            provider=embedding_provider, model_name=embedding_model, api_key=openai_key
        )
        embeddings = embedding_config.get_embeddings()

        # Use existing helper functions from your codebase
        if not force_create:
            # Try loading existing store first
            existing_store = try_load_existing_store(
                client, registry, embeddings, cache_dir, store_name
            )
            if existing_store:
                logger.info("Successfully loaded existing vector store")
                return existing_store

        # Create new store using your existing pattern
        logger.info("Creating new vector store...")
        return create_new_store(client, registry, embeddings, cache_dir, store_name)

    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise VectorStoreCreationError(
            f"Failed to create vector store: {e}", cause=e, failures=failures
        ) from e


def try_load_existing_store(
    client: FMPDataClient,
    registry: EndpointRegistry,
    embeddings: Embeddings,
    cache_dir: str | None,
    store_name: str,
) -> EndpointVectorStore | None:
    """Attempt to load existing vector store (using existing pattern)."""
    from fmp_data.lc.vector_store import EndpointVectorStore

    try:
        vector_store = EndpointVectorStore(
            client=client,
            registry=registry,
            embeddings=embeddings,
            cache_dir=cache_dir,
            store_name=store_name,
        )

        # Use the validate method that exists in your codebase
        if vector_store.validate():
            logger.info("Successfully loaded existing vector store")
            return vector_store

        logger.warning("Existing vector store validation failed")
        return None

    except Exception as e:
        logger.warning(f"Failed to load vector store: {e!s}")
        return None


def create_new_store(
    client: FMPDataClient,
    registry: EndpointRegistry,
    embeddings: Embeddings,
    cache_dir: str | None,
    store_name: str,
) -> EndpointVectorStore:
    """Create and populate new vector store (using existing pattern)."""
    from fmp_data.lc.vector_store import EndpointVectorStore

    vector_store = EndpointVectorStore(
        client=client,
        registry=registry,
        embeddings=embeddings,
        cache_dir=cache_dir,
        store_name=store_name,
    )

    # Get all endpoints from registry and populate store
    endpoint_names = list(registry.list_endpoints().keys())
    vector_store.add_endpoints(endpoint_names)  # Use the actual method
    vector_store.save()  # Use the actual method

    logger.info(f"Created new vector store with {len(endpoint_names)} endpoints")
    return vector_store


# Export main functions - including the existing helper functions
__all__ = [
    "EmbeddingProvider",
    "EndpointSemantics",
    "EndpointVectorStore",
    "LangChainConfig",
    "RegistrySetup",
    "SemanticCategory",
    "VectorStoreCreationError",
    "create_new_store",
    "create_vector_store",
    "init_langchain",
    "resolve_semantics_for_endpoint",
    "setup_registry",
    "try_load_existing_store",
    "validate_api_keys",
]
