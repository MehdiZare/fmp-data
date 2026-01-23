# src/helpers.py
from collections.abc import Callable
import functools
from typing import Any, TypeVar
import warnings

from fmp_data.exceptions import FMPError

F = TypeVar("F", bound=Callable[..., Any])


def deprecated(reason: str = "") -> Callable[[F], F]:
    """
    Decorator to mark functions as deprecated.

    Args:
        reason (str): Optional reason for deprecation.

    Returns:
        A decorator that emits a DeprecationWarning when the function is called.

    Example:
        >>> @deprecated("Use `new_method` instead.")
        ... def old_method():
        ...     pass
    """

    def decorator(func: F) -> F:
        msg = f"{func.__name__} is deprecated."
        if reason:
            msg += f" {reason}"

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator


class RemovedEndpointError(FMPError):
    """Raised when a removed API endpoint is called."""

    def __init__(self, method_name: str, reason: str = "") -> None:
        msg = f"'{method_name}' has been removed from the FMP API."
        if reason:
            msg += f" {reason}"
        super().__init__(msg)
        self.method_name = method_name


def removed(reason: str = "") -> Callable[[F], F]:
    """
    Decorator to mark functions as removed from the API.

    Unlike @deprecated which warns, this raises RemovedEndpointError
    when the method is called.

    Args:
        reason (str): Optional explanation or alternative to use.

    Returns:
        A decorator that raises RemovedEndpointError when the function is called.

    Example:
        >>> @removed("This endpoint was discontinued by FMP in 2024.")
        ... def old_method():
        ...     pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapped(*_args: Any, **_kwargs: Any) -> Any:
            raise RemovedEndpointError(func.__name__, reason)

        return wrapped  # type: ignore[return-value]

    return decorator
