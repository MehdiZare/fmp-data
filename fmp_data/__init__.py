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

import importlib.util as _importlib_util
import types as _types
import warnings as _warnings
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

__version__ = "0.0.0"

# --------------------------------------------------------------------------- #
#  Public re-exports guaranteed to work without optional dependencies
# --------------------------------------------------------------------------- #
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

logger = FMPLogger()


# --------------------------------------------------------------------------- #
#  Helper: detect whether LangChain core stack is available
# --------------------------------------------------------------------------- #
def is_langchain_available() -> bool:
    """
    Return ``True`` if the optional *langchain* extra is installed.

    We check for ``langchain_core`` because it is imported by every
    sub-module that fmp-data’s LC helpers rely on.
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
    from fmp_data import lc as _lc  # noqa: WPS433 (allow internal import)

    # Check FAISS at runtime to give a clearer error than module not found.
    if _importlib_util.find_spec("faiss") is None:
        raise ImportError(
            "FAISS is required for vector-store helpers. "
            "Run:  pip install 'fmp-data[langchain]'"
        ) from None

    return _lc


# Map attribute names to callables that will supply them on demand.
# Keys must match what you later append to __all__.
_lazy_attrs = {
    "EndpointVectorStore": lambda: _lazy_import_vector_store().EndpointVectorStore,
    "EndpointSemantics": lambda: _lazy_import_vector_store().EndpointSemantics,
    "SemanticCategory": lambda: _lazy_import_vector_store().SemanticCategory,
    "create_vector_store": lambda: _lazy_import_vector_store().create_vector_store,
}

# extend __all__ so IDEs still see the names when LC is installed
__all__.extend(_lazy_attrs.keys())


def __getattr__(name: str) -> Any:  # pragma: no cover
    """
    PEP 562 hook: resolve optional symbols at first access.

    If *name* is one of the LC helpers, call the associated factory,
    cache the result in the module dict, and return it.
    """
    if name in _lazy_attrs:
        value = _lazy_attrs[name]()
        globals()[name] = value  # cache so subsequent access is fast
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# --------------------------------------------------------------------------- #
#  Warn immediately if user tried to import LC helpers without extras
# --------------------------------------------------------------------------- #
if not is_langchain_available():
    _warnings.filterwarnings("once", category=ImportWarning)
    _warnings.warn(
        "LangChain extras not installed; vector-store helpers will be unavailable "
        "until you run:  pip install 'fmp-data[langchain]'",
        ImportWarning,
        stacklevel=2,
    )
