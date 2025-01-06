# fmp_data/__init__.py
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
    "FMPLogger",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "ConfigError",
    "logger",
    "is_langchain_available",
]

# Import vector store components if LangChain is available
if is_langchain_available():
    try:
        from fmp_data.lc import (
            EndpointSemantics,
            EndpointVectorStore,
            SemanticCategory,
            create_vector_store,
        )

        __all__.extend(
            [
                "EndpointVectorStore",
                "EndpointSemantics",
                "SemanticCategory",
                "create_vector_store",
            ]
        )
    except ImportError:
        warnings.warn(
            "LangChain vector store components not available. "
            "Install with: pip install 'fmp-data[langchain]'",
            ImportWarning,
            stacklevel=2,
        )

__version__ = "0.3.0"
