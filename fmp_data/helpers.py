# src/helpers.py
from collections.abc import Callable
import functools
from typing import Any, TypeVar
import warnings

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
