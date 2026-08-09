"""Every retired client method must announce itself and answer without a call.

The decorators are only useful if they fire. Nothing exercised these method
bodies -- they wrap endpoints FMP no longer serves, so no test called them --
so the warning text, the replacement it names, and the empty return were all
unverified. A decorator applied to the wrong method would have looked
identical to a working one.

Two decorators, two different contracts, and they must not be confused:

* ``@deprecated`` emits a ``DeprecationWarning`` and still calls through, so
  existing callers keep working.
* ``@removed`` raises ``RemovedEndpointError`` instead. Three intelligence
  social-sentiment methods use it.

Both stamp ``__fmp_deprecated__``, so a test that only looked for a warning
would report the ``@removed`` three as broken. They are not -- raising is
their contract. This asserts each against its own.

**Arguments are supplied, and that is the whole point.** Calling
``method()`` bare fires the decorator and then dies on the missing argument
*before the body runs*, so the warning assertion passes while the body stays
uncovered -- which is the opposite of what this file is for. Each method is
called with a value per required parameter, so the body executes and the two
things that actually matter can be asserted: it returns empty, and it does
**not** reach the client. "Returns empty without issuing the request" is the
contract these deprecations promise; the network call is the part that would
cost a caller a rate-limit slot to earn a 404.

Sync and async are both swept, because the decorators wrap a coroutine
differently and only the sync path was incidentally exercised elsewhere.
"""

from __future__ import annotations

from datetime import date
import importlib
import inspect
import pkgutil
from typing import Any
import warnings

import pytest

import fmp_data
from fmp_data.helpers import RemovedEndpointError

#: Modules the walk could not import, kept so a failure can name them.
SKIPPED_MODULES: dict[str, str] = {}


class _StubClient:
    """Stands in for ``BaseClient`` and records any call that reaches it.

    A deprecated method must not issue a request at all, so this exists to be
    *not* called. It returns ``[]`` rather than raising so that a method which
    does call through still completes and is reported as a failed assertion
    rather than as an incidental exception.
    """

    def __init__(self) -> None:
        self.calls: list[str] = []

    def request(self, *args: Any, **_kwargs: Any) -> list[Any]:
        self.calls.append(getattr(args[0], "name", "?") if args else "?")
        return []

    async def request_async(self, *args: Any, **_kwargs: Any) -> list[Any]:
        self.calls.append(getattr(args[0], "name", "?") if args else "?")
        return []


def _warned(caught: list[warnings.WarningMessage]) -> bool:
    return any(issubclass(w.category, DeprecationWarning) for w in caught)


def _argument_for(parameter: inspect.Parameter) -> Any:
    """A value the method will accept, chosen from its annotation and name.

    Only needs to get past the signature: every body under test returns a
    constant without looking at what it was handed.
    """
    annotation = str(parameter.annotation)
    if "date" in annotation.lower() or "date" in parameter.name.lower():
        return date(2024, 1, 1)
    if "int" in annotation and "str" not in annotation:
        return 1
    return "AAPL"


def _call_args(method: Any) -> dict[str, Any]:
    """One value per parameter the method requires; defaults are left alone."""
    signature = inspect.signature(method)
    return {
        name: _argument_for(parameter)
        for name, parameter in signature.parameters.items()
        if name != "self"
        and parameter.default is inspect.Parameter.empty
        and parameter.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    }


def _deprecated_methods() -> list[tuple[str, type, str]]:
    """Every ``@deprecated`` or ``@removed`` method on every client class."""
    found: list[tuple[str, type, str]] = []
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        name = module_info.name
        if not (name.endswith(".client") or name.endswith(".async_client")):
            continue
        try:
            module = importlib.import_module(name)
        except BaseException as exc:
            # SystemExit from fmp_data/mcp/__main__.py without its extra.
            SKIPPED_MODULES[name] = f"{type(exc).__name__}: {exc}"
            continue
        for class_name, cls in vars(module).items():
            if not (isinstance(cls, type) and class_name.endswith("Client")):
                continue
            if cls.__module__ != name:
                continue  # imported, not defined here
            for attr in dir(cls):
                method = getattr(cls, attr, None)
                if getattr(method, "__fmp_deprecated__", False):
                    found.append((name, cls, attr))
    return found


DEPRECATED = _deprecated_methods()


def test_the_walk_found_the_deprecated_methods() -> None:
    """Floor: an empty list would make the sweeps below vacuous."""
    assert len(DEPRECATED) > 50, (
        f"only {len(DEPRECATED)} deprecated methods found; the walk is not "
        f"reaching the client modules. Skipped: {SKIPPED_MODULES}"
    )


def test_every_deprecated_method_warns_and_never_calls_the_api() -> None:
    """Warn (or raise), return empty, and leave the client untouched."""
    silent: list[str] = []
    called_api: list[str] = []
    call_errors: list[str] = []
    returned: list[str] = []
    checked = 0

    for module_name, cls, attr in DEPRECATED:
        method = getattr(cls, attr)
        if inspect.iscoroutinefunction(inspect.unwrap(method)):
            continue  # covered by the async test below

        instance: Any = object.__new__(cls)
        stub = _StubClient()
        # ``client`` is a read-only property over ``_client``.
        instance._client = stub

        checked += 1
        where = f"{module_name}.{cls.__name__}.{attr}"
        raised_removed = False
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                result = getattr(instance, attr)(**_call_args(method))
                if result not in ([], None):
                    returned.append(f"{where}: returned {result!r}")
            except RemovedEndpointError:
                raised_removed = True
            except Exception as exc:
                # Asserted below rather than swallowed. A method that cannot
                # even be called is a broken declaration, not a pass.
                call_errors.append(f"{where}: {type(exc).__name__}: {exc}")

        if not (raised_removed or _warned(caught)):
            silent.append(where)
        if stub.calls:
            called_api.append(f"{where}: requested {stub.calls}")

    assert not silent, (
        "retired methods that neither warned nor raised RemovedEndpointError "
        "when called:\n  " + "\n  ".join(silent)
    )
    assert not call_errors, (
        "retired methods that raised something unexpected. The body should "
        "return a constant, so this means the declaration or the call is "
        "wrong:\n  " + "\n  ".join(call_errors)
    )
    assert not called_api, (
        "retired methods that issued a request. The endpoint 404s, so this "
        "spends a rate-limit slot to earn nothing:\n  " + "\n  ".join(called_api)
    )
    assert not returned, (
        "retired methods returning something other than empty:\n  "
        + "\n  ".join(returned)
    )
    assert checked > 25, f"only {checked} sync methods exercised; is the sweep working?"


@pytest.mark.asyncio
async def test_every_deprecated_async_method_warns_and_never_calls_the_api() -> None:
    """Same guarantee for the async clients.

    ``@deprecated`` wraps a coroutine differently from a plain function, so a
    decorator that works on one can silently no-op on the other.
    """
    silent: list[str] = []
    called_api: list[str] = []
    call_errors: list[str] = []
    returned: list[str] = []
    checked = 0

    for module_name, cls, attr in DEPRECATED:
        method = getattr(cls, attr)
        if not inspect.iscoroutinefunction(inspect.unwrap(method)):
            continue

        instance: Any = object.__new__(cls)
        stub = _StubClient()
        instance._client = stub

        checked += 1
        where = f"{module_name}.{cls.__name__}.{attr}"
        raised_removed = False
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                result = await getattr(instance, attr)(**_call_args(method))
                # Asserted on both halves. The async wrapper is a separate
                # code path from the sync one, so it is precisely where the
                # two contracts could diverge unnoticed.
                if result not in ([], None):
                    returned.append(f"{where}: returned {result!r}")
            except RemovedEndpointError:
                raised_removed = True
            except Exception as exc:
                call_errors.append(f"{where}: {type(exc).__name__}: {exc}")

        if not (raised_removed or _warned(caught)):
            silent.append(where)
        if stub.calls:
            called_api.append(f"{where}: requested {stub.calls}")

    assert not silent, (
        "retired async methods that neither warned nor raised "
        "RemovedEndpointError when called:\n  " + "\n  ".join(silent)
    )
    assert not call_errors, (
        "retired async methods that raised something unexpected:\n  "
        + "\n  ".join(call_errors)
    )
    assert not called_api, (
        "retired async methods that issued a request:\n  " + "\n  ".join(called_api)
    )
    assert not returned, (
        "retired async methods returning something other than empty:\n  "
        + "\n  ".join(returned)
    )
    assert checked > 25, (
        f"only {checked} async methods exercised; is the sweep working?"
    )
