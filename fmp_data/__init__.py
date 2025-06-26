# fmp_data/__init__.py
import warnings
from typing import TYPE_CHECKING, Any

# Core imports - always available
from fmp_data.client import FMPDataClient
from fmp_data.config import (
    ClientConfig,
    LoggingConfig,
    LogHandlerConfig,
    RateLimitConfig,
)
from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)

# Import the availability check function without triggering LangChain imports
from fmp_data.lc.utils import is_langchain_available
from fmp_data.logger import FMPLogger

# Only import LangChain types for type checking
if TYPE_CHECKING:
    from fmp_data.lc.models import EndpointSemantics, SemanticCategory
    from fmp_data.lc.vector_store import EndpointVectorStore

# Initialize the logger when the library is imported
logger = FMPLogger()

# Core exports - always available
__all__ = [
    "FMPDataClient",
    "ClientConfig",
    "LoggingConfig",
    "LogHandlerConfig",
    "RateLimitConfig",
    "FMPError",
    "FMPLogger",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "ConfigError",
    "logger",
    "is_langchain_available",
]

# Conditionally add LangChain exports
if is_langchain_available():
    __all__.extend(
        [
            "EndpointVectorStore",
            "EndpointSemantics",
            "SemanticCategory",
            "create_vector_store",
        ]
    )


def __getattr__(name: str) -> Any:
    """
    Lazy import LangChain components when accessed.

    This allows the package to work without LangChain dependencies,
    but provides helpful error messages when LangChain features are accessed
    without the required dependencies.
    """
    # LangChain-related attributes
    langchain_attrs = {
        "EndpointVectorStore",
        "EndpointSemantics",
        "SemanticCategory",
        "create_vector_store",
    }

    if name in langchain_attrs:
        if not is_langchain_available():
            raise ImportError(
                f"'{name}' requires LangChain dependencies. "
                "Install with: pip install 'fmp-data[langchain]'"
            )

        try:
            # Import from the lc module which handles its own lazy loading
            if name == "create_vector_store":
                from fmp_data.lc import create_vector_store

                return create_vector_store
            elif name == "EndpointVectorStore":
                from fmp_data.lc.vector_store import EndpointVectorStore

                return EndpointVectorStore
            elif name == "EndpointSemantics":
                from fmp_data.lc.models import EndpointSemantics

                return EndpointSemantics
            elif name == "SemanticCategory":
                from fmp_data.lc.models import SemanticCategory

                return SemanticCategory

        except ImportError as e:
            warnings.warn(
                f"Failed to import {name}: {e}. "
                "Ensure all LangChain dependencies are installed with: "
                "pip install 'fmp-data[langchain]'",
                ImportWarning,
                stacklevel=2,
            )
            raise ImportError(
                f"'{name}' not available. Install LangChain dependencies: "
                "pip install 'fmp-data[langchain]'"
            ) from e

    # If we get here, the attribute doesn't exist
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__version__ = "0.3.1"
