"""
fmp-data top-level package
~~~~~~~~~~~~~~~~~~~~~~~~~~

Core usage:

    import fmp_data as fmp
    client = fmp.FMPDataClient(...)

Optional LangChain / FAISS helpers are exposed lazily and raise
ImportError with guidance if the extra is not installed.
"""

from __future__ import annotations

import importlib
import importlib.util as _importlib_util
import types as _types
from typing import Any

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

# Version handling - let poetry-dynamic-versioning handle this
try:
    from fmp_data._version import __version__
except ImportError:
    # Fallback for development/local builds where _version.py might not exist
    __version__ = "0.0.0"

# --------------------------------------------------------------------------- #
#  Public re-exports guaranteed to work without optional dependencies
# --------------------------------------------------------------------------- #
__all__ = [
    "AuthenticationError",
    "ClientConfig",
    "ConfigError",
    "FMPDataClient",
    "FMPError",
    "FMPLogger",
    "LogHandlerConfig",
    "LoggingConfig",
    "RateLimitConfig",
    "RateLimitError",
    "ValidationError",
    "__version__",
    "is_langchain_available",
    "logger",
]

logger = FMPLogger()


# --------------------------------------------------------------------------- #
#  Helper: detect whether LangChain core stack is available
# --------------------------------------------------------------------------- #
def is_langchain_available() -> bool:
    """
    Return ``True`` if the optional *langchain* extra is installed.

    We check for ``langchain_core`` because it is imported by every
    sub-module that fmp-data's LC helpers rely on.
    """
    return _importlib_util.find_spec("langchain_core") is not None


# --------------------------------------------------------------------------- #
#  Lazy import machinery for optional vector-store helpers
# --------------------------------------------------------------------------- #
def _lazy_import_vector_store() -> _types.ModuleType:
    """
    Import fmp_data.lc only when a LC-specific symbol is first accessed.
    Raises ImportError with installation hint if LangChain (or FAISS) is missing.
    """
    if not is_langchain_available():
        raise ImportError(
            "Optional LangChain features are not installed. "
            "Run:  pip install 'fmp-data[langchain]'"
        ) from None

    # Import inside the function to keep top-level import cheap.
    _lc = importlib.import_module("fmp_data.lc")

    # Check FAISS at runtime to give a clearer error than module not found.
    if _importlib_util.find_spec("faiss") is None:
        raise ImportError(
            "FAISS is required for vector-store helpers. "
            "Run:  pip install 'fmp-data[langchain]'"
        ) from None

    return _lc


def _lazy_import_langchain() -> _types.ModuleType:
    """
    Import fmp_data.langchain only when accessed.
    Raises ImportError with installation hint if LangChain is missing.
    """
    if not is_langchain_available():
        raise ImportError(
            "Optional LangChain features are not installed. "
            "Run:  pip install 'fmp-data[langchain]'"
        ) from None

    try:
        _langchain = importlib.import_module("fmp_data.langchain")
        return _langchain
    except ImportError as e:
        raise ImportError(
            "LangChain integration module could not be imported. "
            "Run:  pip install 'fmp-data[langchain]'"
        ) from e


def _lazy_import_mcp() -> _types.ModuleType:
    """
    Import fmp_data.mcp only when accessed.
    Raises ImportError with installation hint if MCP is missing.
    """
    try:
        _mcp = importlib.import_module("fmp_data.mcp")
        return _mcp
    except ImportError as e:
        raise ImportError(
            "MCP integration module could not be imported. "
            "Run:  pip install 'fmp-data[mcp-server]'"
        ) from e


# Map attribute names to callables that will supply them on demand.
_LAZY_IMPORTS = {
    "lc": _lazy_import_vector_store,
    "langchain": _lazy_import_langchain,
    "mcp": _lazy_import_mcp,
    "create_vector_store": lambda: _lazy_import_vector_store().create_vector_store,
    "FMPVectorStore": lambda: _lazy_import_vector_store().FMPVectorStore,
}


def __getattr__(name: str) -> Any:
    """
    Lazy import handler for optional dependencies.

    This allows importing optional modules only when they're actually used.
    """
    if name in _LAZY_IMPORTS:
        return _LAZY_IMPORTS[name]()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
