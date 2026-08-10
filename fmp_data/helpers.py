# src/helpers.py
from collections.abc import AsyncIterator, Callable
import functools
import inspect
import sys
from types import FrameType
from typing import Any, TypeVar
import warnings

from fmp_data.exceptions import FMPError

F = TypeVar("F", bound=Callable[..., Any])


# Event-loop packages that resume coroutines and must not be blamed for a
# DeprecationWarning raised inside one. ``asyncio`` is CPython's; ``uvloop``
# is the drop-in used under uvicorn/FastAPI. Matched as ``name`` or ``name.*``.
_INTERNAL_LOOP_MODULES: tuple[str, ...] = ("asyncio", "uvloop")


def _is_internal_frame_module(module: str) -> bool:
    """True for this helpers module and known event-loop packages."""
    if module == __name__:
        return True
    for name in _INTERNAL_LOOP_MODULES:
        if module == name or module.startswith(f"{name}."):
            return True
    return False


def _first_caller_frame() -> FrameType | None:
    """The nearest frame outside this module and outside event-loop packages.

    ``stacklevel`` counts *frames*, and there is no fixed number of them
    between a warning raised inside a coroutine body and the code that asked
    for the call (#177). A coroutine body does not run in its caller's stack:
    it runs wherever the event loop resumed it, so ``stacklevel=2`` resolves
    to ``asyncio/events.py`` or ``asyncio/tasks.py`` rather than to user code.
    Walking outward until the frame stops belonging to this module or to a
    known loop package (``asyncio``, ``uvloop``) lands on the right frame for
    every shape:

    * ``await client.old()`` inside a user coroutine -- the awaiting frame is
      directly below the wrapper, and is the answer.
    * ``asyncio.run(client.old())`` -- the wrapper is the task coroutine, so
      the only user frame left is the one that called ``asyncio.run``; the
      walk skips the four ``asyncio`` frames between them and finds it.
    * ``asyncio.gather(client.old(), ...)`` -- same, via whichever user frame
      is still driving the loop.
    * A uvloop-driven server (uvicorn/FastAPI) -- same walk, skipping
      ``uvloop`` / ``uvloop.*`` frames instead of (or as well as) ``asyncio``.

    Frames are matched on their module ``__name__`` rather than on filenames:
    ``asyncio``'s C accelerator (``_asyncio.Task.__step``) contributes no
    Python frame at all, and comparing ``co_filename`` against ``__file__``
    is fragile under zipimport and namespace packages.

    Returns
    -------
    FrameType | None
        The caller's frame, or ``None`` if the stack is entirely internal.
    """
    frame: FrameType | None = sys._getframe(1)
    while frame is not None:
        module = frame.f_globals.get("__name__", "")
        if not _is_internal_frame_module(module):
            return frame
        frame = frame.f_back
    return None


def _warn_at_caller(message: str) -> None:
    """Emit ``message`` as a ``DeprecationWarning`` blamed on the caller.

    ``warnings.warn_explicit`` takes the location as data instead of counting
    frames, which is what makes the async path reportable at all. The module
    name is passed too, so a user's ``filterwarnings(..., module=...)`` rule
    keyed on their own package matches -- under the old ``stacklevel=2`` the
    warning claimed to come from ``asyncio``, so no such rule ever fired.

    The caller's ``__warningregistry__`` is threaded through for the same
    reason ``warnings.warn`` threads it: without it the ``"default"`` action
    cannot dedup per location and a deprecated call in a loop warns on every
    iteration.
    """
    frame = _first_caller_frame()
    if frame is None:  # pragma: no cover - the stack is never fully internal
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)
        return

    warnings.warn_explicit(
        message,
        DeprecationWarning,
        frame.f_code.co_filename,
        frame.f_lineno,
        module=frame.f_globals.get("__name__"),
        registry=frame.f_globals.setdefault("__warningregistry__", {}),
    )


def deprecated(reason: str = "") -> Callable[[F], F]:
    """
    Decorator to mark functions as deprecated.

    Args:
        reason (str): Optional reason for deprecation.

    Returns:
        A decorator that emits a DeprecationWarning when the function is called.
        Coroutine functions are wrapped with an async wrapper and async
        generator functions with an async generator wrapper, so
        ``inspect.iscoroutinefunction`` / ``inspect.isasyncgenfunction``
        remain True. The warning is attributed to the caller's file and
        module rather than to whichever frame resumed the coroutine (#177).

    Example:
        >>> @deprecated("Use `new_method` instead.")
        ... def old_method():
        ...     pass
    """

    def decorator(func: F) -> F:
        msg = f"{func.__name__} is deprecated."
        if reason:
            msg += f" {reason}"

        if inspect.isasyncgenfunction(func):

            @functools.wraps(func)
            async def asyncgen_wrapped(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
                _warn_at_caller(msg)
                async for item in func(*args, **kwargs):
                    yield item

            asyncgen_wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
            return asyncgen_wrapped  # type: ignore[return-value]

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
                _warn_at_caller(msg)
                return await func(*args, **kwargs)

            async_wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
            return async_wrapped  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            _warn_at_caller(msg)
            return func(*args, **kwargs)

        wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
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
        Coroutine functions are wrapped with an async wrapper so
        ``inspect.iscoroutinefunction`` remains True, mirroring ``deprecated()``
        (#170): a sync wrapper around an ``async def`` raises while its caller's
        argument list is still being built (e.g. inside ``asyncio.gather(...)``),
        not while it is awaited, which stops sibling coroutines passed alongside
        it from ever starting. Async generator functions get the same treatment
        for the same reason (#177): they must raise on iteration, not while the
        generator object is being created.

    Example:
        >>> @removed("This endpoint was discontinued by FMP in 2024.")
        ... def old_method():
        ...     pass
    """

    def decorator(func: F) -> F:
        if inspect.isasyncgenfunction(func):

            @functools.wraps(func)
            async def asyncgen_wrapped(
                *_args: Any, **_kwargs: Any
            ) -> AsyncIterator[Any]:
                raise RemovedEndpointError(func.__name__, reason)
                # Unreachable, and deliberately so: the ``yield`` is what makes
                # this an async *generator* function, which is what keeps
                # ``inspect.isasyncgenfunction`` true for the wrapper.
                yield  # type: ignore[unreachable]

            asyncgen_wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
            return asyncgen_wrapped  # type: ignore[return-value]

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapped(*_args: Any, **_kwargs: Any) -> Any:
                raise RemovedEndpointError(func.__name__, reason)

            async_wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
            return async_wrapped  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapped(*_args: Any, **_kwargs: Any) -> Any:
            raise RemovedEndpointError(func.__name__, reason)

        wrapped.__fmp_deprecated__ = True  # type: ignore[attr-defined]
        return wrapped  # type: ignore[return-value]

    return decorator
