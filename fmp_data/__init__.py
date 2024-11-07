# fmp_data/__init__.py
from .client import FMPDataClient
from .config import ClientConfig, LoggingConfig
from .exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)
from .logger import FMPLogger

# Initialize the logger when the library is imported
logger = FMPLogger()

__all__ = [
    "FMPDataClient",
    "ClientConfig",
    "LoggingConfig",
    "FMPError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "ConfigError",
]
