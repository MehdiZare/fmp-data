# fmp_data/__init__.py
import importlib.util
import warnings

from fmp_data.client import FMPDataClient
from fmp_data.config import ClientConfig, LoggingConfig, RateLimitConfig
from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)
from fmp_data.lc.utils import is_langchain_available
from fmp_data.logger import FMPLogger

# Initialize the logger when the library is imported
logger = FMPLogger()

__all__ = [
    "FMPDataClient",
    "ClientConfig",
    "LoggingConfig",
    "RateLimitConfig",
    "FMPError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "ConfigError",
    "logger",
    "is_langchain_available",
]

# Only expose langchain components if dependencies are available
if is_langchain_available:
    try:
        from fmp_data.lc import FMPLangChainClient, FMPLangChainLoader, FMPLangChainTool

        __all__.extend(["FMPLangChainClient", "FMPLangChainLoader", "FMPLangChainTool"])
    except ImportError:
        warnings.warn(
            "LangChain dependencies are not fully installed. "
            "To use LangChain features, install the package with: "
            "pip install 'fmp-data[langchain]'",
            ImportWarning,
            stacklevel=2,
        )

__version__ = "0.3.0"
