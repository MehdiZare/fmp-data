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

from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.manager import FMPToolManager
from fmp_data.lc.models import EndpointSemantics, SemanticCategory
from fmp_data.lc.utils import is_langchain_available
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

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


def create_tool_manager(
    fmp_api_key: str | None = None,
    openai_api_key: str | None = None,
    store_name: str = "fmp_endpoints",
    auto_initialize: bool = True,
) -> FMPToolManager | None:
    """
    Create a configured FMP Tool Manager for LangChain integration.

    Args:
        fmp_api_key: FMP API key (defaults to FMP_API_KEY environment variable)
        openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
        store_name: Name for the vector store
        auto_initialize: Whether to initialize endpoints and store on creation

    Returns:
        Configured FMPToolManager instance or None if dependencies aren't available

    Examples:
        # Create with default settings (using environment variables)
        manager = create_tool_manager()

        # Create with explicit API keys
        manager = create_tool_manager(
            fmp_api_key="your-fmp-key", #pragma: allowlist secret
            openai_api_key="your-openai-key" #pragma: allowlist secret
        )

        # Create without auto-initialization
        manager = create_tool_manager(auto_initialize=False)

    Raises:
        ValueError: If either API key is not provided or not found in environment
    """
    if not is_langchain_available():
        logger.warning(
            "LangChain dependencies not available. "
            "Install with: pip install 'fmp-data[langchain]'"
        )
        return None

    try:
        # Check for FMP API key
        fmp_api_key = fmp_api_key or os.getenv("FMP_API_KEY")
        if not fmp_api_key:
            raise ValueError(
                "FMP API key required. Provide as argument or set FMP_API_KEY "
                "environment variable"
            )

        # Check for OpenAI API key
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key required for embeddings. Provide as argument or "
                "set OPENAI_API_KEY environment variable"
            )

        # Create and return manager with both API keys
        return FMPToolManager(
            fmp_api_key=fmp_api_key,
            openai_api_key=openai_api_key,
            store_name=store_name,
            auto_initialize=auto_initialize,
        )

    except Exception as e:
        logger.error(f"Failed to create tool manager: {str(e)}")
        return None


__all__ = [
    "EndpointVectorStore",
    "EndpointSemantics",
    "SemanticCategory",
    "is_langchain_available",
    "LangChainConfig",
    "create_tool_manager",
]
