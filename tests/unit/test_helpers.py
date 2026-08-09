# tests/unit/test_helpers.py
"""Tests for the deprecated decorator in fmp_data/helpers.py"""

import asyncio
from collections.abc import AsyncIterator
import inspect
from pathlib import Path
import sys
from types import FrameType
import warnings

import pytest

from fmp_data.helpers import RemovedEndpointError, deprecated, removed

_THIS_FILE = Path(__file__).resolve()


def _here() -> int:
    """The line number of the statement that called this function."""
    frame: FrameType | None = sys._getframe(1)
    assert frame is not None
    return frame.f_lineno


class TestDeprecatedDecorator:
    """Tests for the @deprecated decorator"""

    def test_deprecated_without_reason(self):
        """Test deprecated decorator without a reason"""

        @deprecated()
        def old_function():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function is deprecated." in str(w[0].message)

    def test_deprecated_with_reason(self):
        """Test deprecated decorator with a reason"""

        @deprecated("Use new_function instead.")
        def old_function():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function is deprecated." in str(w[0].message)
            assert "Use new_function instead." in str(w[0].message)

    def test_deprecated_preserves_function_name(self):
        """Test that deprecated decorator preserves function metadata"""

        @deprecated("Reason")
        def documented_function():
            """This is a docstring."""
            pass

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring."

    def test_deprecated_with_arguments(self):
        """Test deprecated decorator with function arguments"""

        @deprecated("Old API")
        def add_numbers(a: int, b: int) -> int:
            return a + b

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = add_numbers(2, 3)

            assert result == 5
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_deprecated_with_kwargs(self):
        """Test deprecated decorator with keyword arguments"""

        @deprecated()
        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = greet("World", greeting="Hi")

            assert result == "Hi, World!"
            assert len(w) == 1

    def test_deprecated_multiple_calls(self):
        """Test that warning is raised on each call"""

        @deprecated("Old function")
        def old_func():
            return True

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            old_func()
            old_func()

            assert len(w) == 3
            for warning in w:
                assert issubclass(warning.category, DeprecationWarning)

    def test_deprecated_on_method(self):
        """Test deprecated decorator on class method"""

        class MyClass:
            @deprecated("Use new_method instead")
            def old_method(self):
                return "old result"

        obj = MyClass()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = obj.old_method()

            assert result == "old result"
            assert len(w) == 1
            assert "old_method is deprecated." in str(w[0].message)

    def test_deprecated_async_preserves_coroutine(self):
        """Async wrappers stay coroutine functions and still warn on await."""

        @deprecated("Use new_async instead.")
        async def old_async() -> str:
            return "result"

        assert inspect.iscoroutinefunction(old_async)

        async def _run() -> str:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = await old_async()
                assert result == "result"
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "old_async is deprecated." in str(w[0].message)
                assert "Use new_async instead." in str(w[0].message)
            return result

        assert asyncio.run(_run()) == "result"


class TestRemovedDecorator:
    """Tests for the @removed decorator."""

    def test_removed_raises_without_reason(self):
        @removed()
        def old_endpoint():
            return "unreachable"

        with pytest.raises(RemovedEndpointError) as exc_info:
            old_endpoint()
        assert "old_endpoint" in str(exc_info.value)
        assert "has been removed from the FMP API" in str(exc_info.value)

    def test_removed_raises_with_reason(self):
        @removed("Discontinued by FMP in 2024.")
        def old_endpoint():
            return "unreachable"

        with pytest.raises(RemovedEndpointError) as exc_info:
            old_endpoint()
        assert "Discontinued by FMP in 2024." in str(exc_info.value)

    def test_removed_preserves_function_name(self):
        @removed("Reason")
        def documented_endpoint():
            """This is a docstring."""

        assert documented_endpoint.__name__ == "documented_endpoint"
        assert documented_endpoint.__doc__ == "This is a docstring."

    def test_removed_on_method_never_reaches_the_body(self):
        class MyClass:
            @removed("Use new_method instead")
            def old_method(self):
                raise AssertionError("body must not run")  # pragma: no cover

        with pytest.raises(RemovedEndpointError):
            MyClass().old_method()

    def test_removed_async_preserves_coroutine_and_raises_on_await(self):
        """Async wrappers stay coroutine functions and raise on await (#170).

        Before #170, ``removed()`` always returned a plain ``def`` wrapper, so
        calling it raised immediately -- before an ``await`` ever happened.
        """

        @removed("Discontinued.")
        async def old_async() -> str:
            return "unreachable"  # pragma: no cover

        assert inspect.iscoroutinefunction(old_async)

        # The call itself must not raise -- only awaiting the coroutine may.
        coro = old_async()
        assert inspect.isawaitable(coro)

        async def _run() -> None:
            with pytest.raises(RemovedEndpointError):
                await coro

        asyncio.run(_run())


def test_deprecated_and_removed_preserve_coroutine_ness() -> None:
    """Neither decorator may change whether the wrapped function is a
    coroutine function (#170).

    ``removed()`` used to always return a plain ``def`` wrapper regardless of
    what it decorated, unlike its sibling ``deprecated()``. Parameterised over
    both decorators and both sync/async inputs so a future decorator added to
    this module -- or a regression in either existing one -- is caught here
    rather than only incidentally, by whichever client-method sweep happens
    to exercise it.
    """

    def sync_fn(value: int) -> int:
        return value

    async def async_fn(value: int) -> int:
        return value

    checked = 0
    for factory_name, factory in (("deprecated", deprecated), ("removed", removed)):
        for fn, expected_async in ((sync_fn, False), (async_fn, True)):
            wrapped = factory("reason")(fn)
            actual_async = inspect.iscoroutinefunction(wrapped)
            assert actual_async is expected_async, (
                f"@{factory_name} on "
                f"{'an async' if expected_async else 'a sync'} function "
                f"produced iscoroutinefunction={actual_async}"
            )
            checked += 1

    # Floor: guards against the parametrization silently shrinking (e.g. one
    # of the two branches above being dropped) and the guard passing vacuously.
    assert checked == 4, f"only {checked}/4 decorator x sync/async pairs checked"


class TestDeprecationIsBlamedOnTheCaller:
    """#177: the warning must name the user's call site, not the event loop.

    A ``DeprecationWarning`` exists to point at the line that has to change.
    The async wrapper called ``warnings.warn(..., stacklevel=2)`` from inside
    the coroutine body, and a coroutine body does not run in its caller's
    stack -- it runs wherever the loop resumed it -- so ``stacklevel=2``
    resolved to ``asyncio/events.py``. Measured before the fix::

        sync path:  DeprecationWarning at test_helpers.py
        async path: DeprecationWarning at .../asyncio/events.py

    Every test here asserts the recorded ``filename`` *is this file*, and
    that the recorded ``lineno`` falls in the window around the call.
    Asserting merely that a warning fired is what let the bug survive: the
    pre-existing async tests all passed throughout.
    """

    @staticmethod
    def _assert_blamed_here(
        record: warnings.WarningMessage, start: int, end: int
    ) -> None:
        assert Path(record.filename).resolve() == _THIS_FILE, (
            f"warning blamed on {record.filename}:{record.lineno}, "
            f"expected {_THIS_FILE}"
        )
        assert start < record.lineno < end, (
            f"warning blamed on line {record.lineno}, expected between "
            f"{start} and {end}"
        )
        assert record.filename.endswith("test_helpers.py")

    def test_sync_call_is_blamed_on_the_caller(self) -> None:
        """The path that was already correct -- pinned so it stays that way."""

        @deprecated("Use new_sync instead.")
        def old_sync() -> str:
            return "sync"

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            start = _here()
            old_sync()
            end = _here()

        assert len(caught) == 1
        self._assert_blamed_here(caught[0], start, end)

    def test_async_call_driven_by_asyncio_run_is_blamed_on_the_caller(self) -> None:
        """The exact shape reported in #177.

        ``asyncio.run(old_async())`` makes the deprecated coroutine the task
        coroutine itself, so *no* user frame sits below the wrapper. Before
        the fix this reported ``asyncio/events.py``; the only user frame left
        on the stack is the ``asyncio.run`` call, and that is the answer.
        """

        @deprecated("Use new_async instead.")
        async def old_async() -> str:
            return "async"

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            start = _here()
            assert asyncio.run(old_async()) == "async"
            end = _here()

        assert len(caught) == 1
        self._assert_blamed_here(caught[0], start, end)

    def test_awaited_async_call_is_blamed_on_the_awaiting_line(self) -> None:
        """The common shape: ``await client.old_method()`` in user code."""

        @deprecated("Use new_async instead.")
        async def old_async() -> str:
            return "async"

        holder: dict[str, int] = {}

        async def caller() -> str:
            holder["start"] = _here()
            result = await old_async()
            holder["end"] = _here()
            return result

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert asyncio.run(caller()) == "async"

        assert len(caught) == 1
        self._assert_blamed_here(caught[0], holder["start"], holder["end"])

    def test_gathered_async_call_is_blamed_on_a_frame_in_this_file(self) -> None:
        """``asyncio.gather`` suspends the frame that built the call.

        Its line is therefore unrecoverable, but the frame still driving the
        loop is the user's, so the warning stays inside their code instead of
        landing in ``asyncio``.
        """

        @deprecated("Use new_async instead.")
        async def old_async() -> str:
            return "async"

        async def sibling() -> str:
            await asyncio.sleep(0)
            return "ok"

        async def run() -> list[str]:
            return list(await asyncio.gather(old_async(), sibling()))

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            start = _here()
            assert asyncio.run(run()) == ["async", "ok"]
            end = _here()

        assert len(caught) == 1
        self._assert_blamed_here(caught[0], start, end)

    def test_the_warning_carries_the_callers_module_for_filterwarnings(self) -> None:
        """``filterwarnings(module=...)`` keyed on the caller must match.

        The second half of #177: a warning attributed to ``asyncio`` cannot be
        silenced -- or escalated -- by a rule naming the user's own module.
        ``module`` is matched by ``re.compile(...).match`` against the
        *filename*, so the caller's file is what has to be there.
        """

        @deprecated("Use new_async instead.")
        async def old_async() -> str:
            return "async"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            warnings.filterwarnings(
                "error",
                category=DeprecationWarning,
                module=r".*test_helpers",
            )
            with pytest.raises(DeprecationWarning):
                asyncio.run(old_async())


class TestAsyncGeneratorsGetAnAsyncGeneratorWrapper:
    """#177, related half: ``async def ... yield`` took the sync branch.

    ``inspect.iscoroutinefunction`` is False for an async generator function,
    so both decorators fell through to the plain ``def`` wrapper. That makes
    ``inspect.isasyncgenfunction(wrapped)`` False and moves the warning (or
    the raise) to generator *creation* rather than iteration -- the same
    defect #170 fixed for coroutines. There are no async generators in
    ``fmp_data`` today, so these define their own.
    """

    def test_deprecated_preserves_async_generator_ness(self) -> None:
        @deprecated("Use new_stream instead.")
        async def old_stream() -> AsyncIterator[int]:
            yield 1
            yield 2

        assert inspect.isasyncgenfunction(old_stream)

        async def consume() -> list[int]:
            return [item async for item in old_stream()]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert asyncio.run(consume()) == [1, 2]

        assert len(caught) == 1
        assert "old_stream is deprecated." in str(caught[0].message)
        assert Path(caught[0].filename).resolve() == _THIS_FILE

    def test_deprecated_async_generator_stays_silent_until_iterated(self) -> None:
        """Creating the generator object is not using the endpoint."""

        @deprecated("Use new_stream instead.")
        async def old_stream() -> AsyncIterator[int]:
            yield 1

        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            generator = old_stream()

        async def drain() -> None:
            with pytest.warns(DeprecationWarning):
                async for _ in generator:
                    pass

        asyncio.run(drain())

    def test_removed_async_generator_raises_on_iteration_not_creation(self) -> None:
        """Mirrors #170: raising early kills siblings in the same ``gather``."""

        @removed("Discontinued.")
        async def old_stream() -> AsyncIterator[int]:
            raise AssertionError("body must not run")  # pragma: no cover
            # Unreachable, and required: the ``yield`` is what makes this an
            # async *generator* function rather than a coroutine function.
            yield 1  # type: ignore[unreachable]  # pragma: no cover

        assert inspect.isasyncgenfunction(old_stream)

        generator = old_stream()  # must not raise

        async def drain() -> None:
            with pytest.raises(RemovedEndpointError):
                async for _ in generator:
                    pass  # pragma: no cover

        asyncio.run(drain())


def test_removed_async_lets_sibling_coroutines_start_in_asyncio_gather() -> None:
    """A removed async method must fail like every other async method: while
    it is awaited, not while ``asyncio.gather``'s argument list is still
    being built (#170).

    Before #170, calling a ``@removed`` async method raised synchronously --
    during expression evaluation, before ``asyncio.gather`` was even invoked
    -- so a sibling coroutine passed alongside it in the same ``gather()``
    call never started.
    """

    @removed("Discontinued.")
    async def removed_endpoint() -> None:
        raise AssertionError("body must not run")  # pragma: no cover

    started = {"sibling": False}

    async def sibling() -> str:
        started["sibling"] = True
        await asyncio.sleep(0)
        return "ok"

    async def run() -> None:
        with pytest.raises(RemovedEndpointError):
            await asyncio.gather(removed_endpoint(), sibling())

    asyncio.run(run())
    assert started["sibling"], (
        "sibling coroutine never started -- removed_endpoint() must have "
        "raised while gather's argument list was still being built"
    )
