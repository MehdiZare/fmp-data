# tests/unit/test_helpers.py
"""Tests for the deprecated decorator in fmp_data/helpers.py"""

import asyncio
import inspect
import warnings

import pytest

from fmp_data.helpers import RemovedEndpointError, deprecated, removed


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
