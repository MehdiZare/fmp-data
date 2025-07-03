"""
FMP Data Client
==============

A Python client for the Financial Modeling Prep (FMP) API with comprehensive
logging, rate limiting, and error handling.

File: fmp_data/__init__.py
"""

from __future__ import annotations

import os

# Main API exports
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
from fmp_data.logger import FMPLogger

# Convenience logger instance
logger = FMPLogger()


# Version handling - compatible with both Poetry and uv approaches
def _get_version() -> str:
    """Get package version from multiple possible sources."""
    # Try Poetry dynamic versioning first (if available)
    try:
        # This gets populated by poetry-dynamic-versioning
        from fmp_data._version import __version__

        return __version__
    except ImportError:
        # Continue to next method
        pass

    # Try setuptools-scm generated version (for uv builds)
    try:
        from fmp_data._version import version

        return version
    except ImportError:
        # Continue to next method
        pass

    # Try importlib.metadata (standard approach)
    try:
        from importlib.metadata import version

        return version("fmp-data")
    except ImportError:
        # Continue to next method
        pass

    # Try pkg_resources (older approach)
    try:
        import pkg_resources

        return pkg_resources.get_distribution("fmp-data").version
    except Exception:  # noqa: S110
        # All version detection methods failed
        return "unknown"

    # Development fallback (should not reach here)
    return "unknown"


__version__ = _get_version()

# Optional imports with graceful degradation
_HAS_LANGCHAIN = False
_HAS_MCP = False

try:
    from fmp_data.langchain import FMPDataLoader

    _HAS_LANGCHAIN = True
except ImportError:
    # LangChain integration not available
    FMPDataLoader = None  # type: ignore

try:
    from fmp_data.mcp import FMPMCPServer

    _HAS_MCP = True
except ImportError:
    # MCP integration not available
    FMPMCPServer = None  # type: ignore

__all__ = [
    "__version__",
    "FMPClient",
    "FMPError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ConfigError",
]

# Conditionally add optional exports
if _HAS_LANGCHAIN:
    __all__.append("FMPDataLoader")

if _HAS_MCP:
    __all__.append("FMPMCPServer")

# Package metadata
__author__ = "Mehdi Zare"
__email__ = "mehdizare@users.noreply.github.com"
__license__ = "MIT"
__description__ = "Python client for the Financial Modeling Prep API"


# Compatibility flags for runtime detection
def _detect_build_tool() -> str:
    """Detect which build tool was used."""
    # Check if we're in a uv environment
    if os.getenv("VIRTUAL_ENV") and "uv" in os.getenv("VIRTUAL_ENV", ""):
        return "uv"
    # Check if we're in a Poetry environment
    elif os.getenv("POETRY_ACTIVE"):
        return "poetry"
    else:
        return "unknown"


__build_tool__ = _detect_build_tool()
