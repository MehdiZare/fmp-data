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
from typing import Any, TypedDict, cast

from langchain_core.embeddings import Embeddings

from fmp_data import FMPDataClient
from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.embedding import EmbeddingProvider
from fmp_data.lc.mapping import ENDPOINT_GROUPS
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.utils import is_langchain_available
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

from .models import Endpoint

logger = FMPLogger().get_logger(__name__)


class GroupConfig(TypedDict):
    """Configuration for an endpoint group"""

    endpoint_map: dict[str, Endpoint[Any]]  # Maps endpoint names to Endpoint objects
    semantics_map: dict[
        str, EndpointSemantics
    ]  # Maps endpoint names to their semantics
    display_name: str  # Display name for the group


# Define more specific types for ENDPOINT_GROUPS
EndpointMap = dict[str, Endpoint[Any]]
SemanticsMap = dict[str, EndpointSemantics]
EndpointGroups = dict[str, GroupConfig]


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


def setup_registry(client: FMPDataClient) -> EndpointRegistry:
    """Initialize and populate endpoint registry."""
    registry = EndpointRegistry()

    # Cast ENDPOINT_GROUPS to the correct type
    endpoint_groups = cast(dict[str, GroupConfig], ENDPOINT_GROUPS)

    for _, group_config in endpoint_groups.items():
        endpoints_dict = {}
        for name, endpoint in group_config["endpoint_map"].items():
            semantic_name = name[4:] if name.startswith("get_") else name
            if semantic_name in group_config["semantics_map"]:
                endpoints_dict[name] = (
                    endpoint,
                    group_config["semantics_map"][semantic_name],
                )

        if endpoints_dict:
            registry.register_batch(endpoints_dict)

    return registry


def try_load_existing_store(
    client: FMPDataClient,
    registry: EndpointRegistry,
    embeddings: Embeddings,
    cache_dir: str | None,
    store_name: str,
) -> EndpointVectorStore | None:
    """Attempt to load existing vector store."""
    try:
        vector_store = EndpointVectorStore(
            client=client,
            registry=registry,
            embeddings=embeddings,
            cache_dir=cache_dir,
            store_name=store_name,
        )

        if vector_store.validate():
            logger.info("Successfully loaded existing vector store")
            return vector_store

        logger.warning("Existing vector store validation failed")
        return None

    except Exception as e:
        logger.warning(f"Failed to load vector store: {str(e)}")
        return None


def create_new_store(
    client: FMPDataClient,
    registry: EndpointRegistry,
    embeddings: Embeddings,
    cache_dir: str | None,
    store_name: str,
) -> EndpointVectorStore:
    """Create and initialize new vector store."""
    vector_store = EndpointVectorStore(
        client=client,
        registry=registry,
        embeddings=embeddings,
        cache_dir=cache_dir,
        store_name=store_name,
    )

    endpoint_names = list(registry.list_endpoints().keys())
    vector_store.add_endpoints(endpoint_names)
    vector_store.save()

    logger.info(f"Created new vector store with {len(endpoint_names)} endpoints")
    return vector_store


def create_vector_store(
    fmp_api_key: str | None = None,
    openai_api_key: str | None = None,
    store_name: str = "fmp_endpoints",
    cache_dir: str | None = None,
    force_create: bool = False,
) -> EndpointVectorStore | None:
    """
    Create or load a vector store for FMP API endpoint search.

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


__all__ = [
    "EndpointVectorStore",
    "EndpointSemantics",
    "SemanticCategory",
    "is_langchain_available",
    "LangChainConfig",
    "create_vector_store",
]
