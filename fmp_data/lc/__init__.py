# fmp_data/lc/__init__.py
"""
LangChain integration for FMP Data API.
Relative path: fmp_data/lc/__init__.py

This module provides LangChain integration features including:
- Semantic search for API endpoints
- LangChain tool creation
- Vector store management
- Natural language endpoint discovery
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from langchain.embeddings.base import Embeddings

from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.embedding import EmbeddingProvider
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.utils import is_langchain_available
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger
from fmp_data.models import Endpoint

# Only import for type checking, not at runtime
if TYPE_CHECKING:
    from fmp_data.client import FMPDataClient

logger = FMPLogger().get_logger(__name__)


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
    """
    Initialize and populate endpoint registry.

    Args:
        client: The FMP Data client instance

    Returns:
        Configured endpoint registry
    """
    registry = EndpointRegistry()

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
            # Look for semantics - try exact match first, then without 'get_' prefix
            semantics = semantics_map.get(endpoint_name)
            if semantics is None and endpoint_name.startswith("get_"):
                # Try without the 'get_' prefix
                base_name = endpoint_name[4:]
                semantics = semantics_map.get(base_name)

            if semantics is not None:
                endpoints_for_batch[endpoint_name] = (endpoint, semantics)
            else:
                logger.warning(f"No semantics found for endpoint: {endpoint_name}")

        # Register the batch for this group
        if endpoints_for_batch:
            try:
                registry.register_batch(endpoints_for_batch)
                logger.debug(
                    f"Registered {len(endpoints_for_batch)} endpoints from {group_name}"
                )
            except Exception as e:
                logger.error(f"Failed to register {group_name} endpoints: {e}")

    return registry


def create_vector_store(
    fmp_api_key: str | None = None,
    openai_api_key: str | None = None,
    cache_dir: str | None = None,
    store_name: str = "fmp_endpoints",
    force_create: bool = False,
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI,
    embedding_model: str | None = None,
) -> EndpointVectorStore | None:
    """
    Create a vector store for endpoint semantic search.

    Args:
        fmp_api_key: FMP API key (or from env)
        openai_api_key: OpenAI API key (or from env)
        cache_dir: Directory to store vector index
        store_name: Name for the vector store
        force_create: Whether to recreate existing store
        embedding_provider: Provider for embeddings
        embedding_model: Specific model name

    Returns:
        Configured vector store or None if setup fails
    """
    # Late import to avoid circular dependency
    from fmp_data.client import FMPDataClient

    try:
        # Validate API keys
        fmp_key, openai_key = validate_api_keys(fmp_api_key, openai_api_key)

        # Create client
        client = FMPDataClient(api_key=fmp_key)

        # Setup registry
        registry = setup_registry(client)

        # Configure embeddings
        from fmp_data.lc.embedding import EmbeddingConfig

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
        return None


def try_load_existing_store(
    client: FMPDataClient,
    registry: EndpointRegistry,
    embeddings: Embeddings,
    cache_dir: str | None,
    store_name: str,
) -> EndpointVectorStore | None:
    """Attempt to load existing vector store (using existing pattern)."""
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
    "SemanticCategory",
    "create_new_store",
    "create_vector_store",
    "init_langchain",
    "setup_registry",
    "try_load_existing_store",
    "validate_api_keys",
]
