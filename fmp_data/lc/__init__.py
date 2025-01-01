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
from typing import Optional

from fmp_data import FMPLogger
from fmp_data.lc.manager import FMPToolManager
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.utils import is_langchain_available
from fmp_data.lc.vector_store import EndpointVectorStore

logger = FMPLogger().get_logger(__name__)

__all__ = [
    "FMPToolManager",
    "EndpointVectorStore",
    "EndpointSemantics",
    "SemanticCategory",
    "create_tool_manager",
    "is_langchain_available",
]


def create_tool_manager(
    api_key: str | None = None,
    store_name: str = "fmp_endpoints",
    auto_initialize: bool = True,
) -> FMPToolManager | None:
    """
    Create a configured FMP Tool Manager for LangChain integration.

    Args:
        api_key: FMP API key (defaults to FMP_API_KEY environment variable)
        store_name: Name for the vector store
        auto_initialize: Whether to initialize endpoints and store on creation

    Returns:
        Configured FMPToolManager instance or None if dependencies aren't available

    Examples:
        # Create with default settings
        manager = create_tool_manager()

        # Create with explicit API key
        manager = create_tool_manager(api_key="your-api-key")

        # Create without auto-initialization
        manager = create_tool_manager(auto_initialize=False)
    """
    if not is_langchain_available():
        logger.warning(
            "LangChain dependencies not available. "
            "Install with: pip install 'fmp-data[langchain]'"
        )
        return None

    try:
        # Check for API key
        api_key = api_key or os.getenv("FMP_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Provide as argument or set FMP_API_KEY "
                "environment variable"
            )

        # Check for OpenAI API key (required for embeddings)
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key required for embeddings. "
                "Set OPENAI_API_KEY environment variable"
            )

        # Create and return manager
        return FMPToolManager(
            store_name=store_name,
            auto_initialize=auto_initialize,
        )

    except Exception as e:
        logger.error(f"Failed to create tool manager: {str(e)}")
        return None


# Optional: Auto-initialize if configured
if (
    os.getenv("FMP_AUTO_INIT_VECTOR_STORE", "false").lower() == "true"
    and is_langchain_available()
):
    try:
        logger.info("Auto-initializing FMP Tool Manager")
        create_tool_manager()
    except Exception as e:
        logger.warning(f"Auto-initialization failed: {str(e)}")
