# fmp_data/__init__.py
from fmp_data.client import FMPDataClient
from fmp_data.config import ClientConfig, LoggingConfig, RateLimitConfig
from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)
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
]

__version__ = "0.1.0"
