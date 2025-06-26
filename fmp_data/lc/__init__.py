# fmp_data/lc/__init__.py
"""
LangChain integration for FMP Data API.

This module provides LangChain integration features including:
- Semantic search for API endpoints
- LangChain tool creation
- Vector store management
- Natural language endpoint discovery
"""
import os
from typing import TYPE_CHECKING, Any, TypedDict

# Only import types for type checking, not at runtime
if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

    from fmp_data import FMPDataClient
    from fmp_data.lc.models import Endpoint, EndpointSemantics, SemanticCategory
    from fmp_data.lc.vector_store import EndpointVectorStore

from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.utils import is_langchain_available
from fmp_data.logger import FMPLogger

logger = FMPLogger().get_logger(__name__)


class GroupConfig(TypedDict):
    """Configuration for an endpoint group"""

    endpoint_map: dict[str, Any]  # Maps endpoint names to Endpoint objects
    semantics_map: dict[str, Any]  # Maps endpoint names to their semantics
    display_name: str  # Display name for the group


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


def setup_registry(client: "FMPDataClient") -> Any:  # EndpointRegistry
    """Initialize and populate endpoint registry."""
    if not is_langchain_available():
        raise ImportError(
            "LangChain dependencies required. Install with: pip install 'fmp-data[langchain]'"
        )

    from fmp_data.lc.mapping import ENDPOINT_GROUPS
    from fmp_data.lc.registry import EndpointRegistry

    registry = EndpointRegistry(client)

    # Populate registry with endpoints
    for group_name, group_config in ENDPOINT_GROUPS.items():
        for endpoint_name, endpoint in group_config["endpoint_map"].items():
            registry.register_endpoint(
                endpoint_name,
                endpoint,
                group_config["semantics_map"].get(endpoint_name),
            )

    return registry


def try_load_existing_store(
    client: "FMPDataClient",
    registry: Any,  # EndpointRegistry
    embeddings: "Embeddings",
    cache_dir: str,
    store_name: str,
) -> Any | None:  # EndpointVectorStore | None
    """Try to load existing vector store from cache."""
    if not is_langchain_available():
        return None

    from fmp_data.lc.vector_store import EndpointVectorStore

    cache_path = os.path.join(cache_dir, store_name)
    if os.path.exists(cache_path):
        try:
            logger.info(f"Loading existing vector store from {cache_path}")
            return EndpointVectorStore.load(cache_path, client, registry, embeddings)
        except Exception as e:
            logger.warning(f"Failed to load existing store: {e}. Creating new one.")

    return None


def create_new_store(
    client: "FMPDataClient",
    registry: Any,  # EndpointRegistry
    embeddings: "Embeddings",
    cache_dir: str,
    store_name: str,
) -> Any:  # EndpointVectorStore
    """Create a new vector store."""
    if not is_langchain_available():
        raise ImportError(
            "LangChain dependencies required. Install with: pip install 'fmp-data[langchain]'"
        )

    from fmp_data.lc.vector_store import EndpointVectorStore

    logger.info("Creating new vector store...")
    store = EndpointVectorStore(client, registry, embeddings)

    # Save the store if cache directory is provided
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, store_name)
        store.save(cache_path)
        logger.info(f"Vector store saved to {cache_path}")

    return store


def create_vector_store(
    fmp_api_key: str | None = None,
    openai_api_key: str | None = None,
    store_name: str = "fmp_endpoints",
    cache_dir: str | None = None,
    force_create: bool = False,
) -> Any | None:  # EndpointVectorStore | None
    """
    Create a vector store for FMP API endpoints with semantic search capabilities.

    Args:
        fmp_api_key: FMP API key (defaults to FMP_API_KEY environment variable)
        openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
        store_name: Name for the vector store
        cache_dir: Directory for storing vector store cache (defaults to ~/.fmp_cache)
        force_create: Whether to force creation of new store even if cache exists

    Returns:
        Configured EndpointVectorStore instance or None if setup fails
    """
    if not is_langchain_available():
        logger.warning(
            "LangChain dependencies not available. "
            "Install with: pip install 'fmp-data[langchain]'"
        )
        return None

    try:
        # Import required modules only when needed
        from fmp_data import FMPDataClient
        from fmp_data.lc.config import LangChainConfig
        from fmp_data.lc.embedding import EmbeddingProvider

        # Set default cache directory
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.fmp_cache")

        # Validate API keys
        fmp_key, openai_key = validate_api_keys(fmp_api_key, openai_api_key)

        # Create config and initialize components
        config = LangChainConfig(
            api_key=fmp_key,
            embedding_provider=EmbeddingProvider.OPENAI,
            embedding_api_key=openai_key,
        )

        client = FMPDataClient(config=config)
        registry = setup_registry(client)

        # Handle potential None case for embedding_config
        if config.embedding_config is None:
            raise ValueError("Embedding configuration is required")

        embeddings = config.embedding_config.get_embeddings()

        # Try loading existing store if not forcing creation
        if not force_create:
            existing_store = try_load_existing_store(
                client, registry, embeddings, cache_dir, store_name
            )
            if existing_store:
                return existing_store

        # Create new store
        return create_new_store(client, registry, embeddings, cache_dir, store_name)

    except Exception as e:
        logger.error(f"Failed to create vector store: {str(e)}")
        return None


# Lazy imports for exports - only available when LangChain is installed
def __getattr__(name: str) -> Any:
    """Lazy import attributes when accessed."""
    if not is_langchain_available():
        raise ImportError(
            f"'{name}' requires LangChain dependencies. "
            "Install with: pip install 'fmp-data[langchain]'"
        )

    if name == "EndpointVectorStore":
        from fmp_data.lc.vector_store import EndpointVectorStore

        return EndpointVectorStore
    elif name == "EndpointSemantics":
        from fmp_data.lc.models import EndpointSemantics

        return EndpointSemantics
    elif name == "SemanticCategory":
        from fmp_data.lc.models import SemanticCategory

        return SemanticCategory
    elif name == "LangChainConfig":
        from fmp_data.lc.config import LangChainConfig

        return LangChainConfig
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "EndpointVectorStore",
    "EndpointSemantics",
    "SemanticCategory",
    "is_langchain_available",
    "LangChainConfig",
    "create_vector_store",
]
