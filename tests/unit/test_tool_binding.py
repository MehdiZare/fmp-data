"""The shared endpoint -> client-method binding layer (#188).

``fmp_data.tool_binding`` is what MCP and LangChain both bind through. These
tests pin the parts that used to be duplicated between them, plus the two
properties the split into a core module exists to guarantee:

* it imports with **no optional extra installed** — a shared layer reachable
  only with ``[langchain]`` would not be shared;
* the strict (:func:`resolve_attr`) and lenient (:func:`resolve_client_method`)
  resolvers reach the *same* callable, and differ only in how they report a
  miss.

Deliberately placed in ``tests/unit/`` rather than ``tests/unit/lc/``: the
module under test has no LangChain dependency, and the ``lc`` package refuses
to import without the extra, so a test living there would be skipped in
exactly the environment this module is supposed to work in.
"""

from __future__ import annotations

import ast
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from fmp_data.tool_binding import (
    bindable_params,
    camel_to_snake,
    map_tool_kwargs_to_method,
    method_dispatch_compatible,
    method_param_aliases,
    partition_params_for_method,
    resolve_attr,
    resolve_client_method,
    resolve_dispatch_method,
    resolve_method_param_name,
    uncovered_required_params,
)


class _Param:
    """Stand-in for ``EndpointParam``; the binding layer only reads ``.name``."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"_Param({self.name!r})"


def _names(params: list[Any]) -> set[str]:
    return {p.name for p in params}


# ---------------------------------------------------------------------------
# Name mapping
# ---------------------------------------------------------------------------


def test_camel_to_snake_handles_wire_names() -> None:
    assert camel_to_snake("periodLength") == "period_length"
    assert camel_to_snake("sicCode") == "sic_code"
    assert camel_to_snake("symbol") == "symbol"
    # A leading capital must not produce a leading underscore.
    assert camel_to_snake("Symbol") == "symbol"


def test_aliases_prefer_exact_match_over_rename() -> None:
    assert resolve_method_param_name("from", {"from", "from_date"}) == "from"
    assert resolve_method_param_name("from", {"from_date"}) == "from_date"
    assert resolve_method_param_name("from", {"start_date"}) == "start_date"
    assert resolve_method_param_name("limit", {"symbol"}) is None


def test_camel_case_fallback_is_always_available() -> None:
    """An unlisted wire name still reaches its snake_case method param."""
    assert "period_length" in method_param_aliases("periodLength")
    assert resolve_method_param_name("sicCode", {"sic_code"}) == "sic_code"


# ---------------------------------------------------------------------------
# bindable_params: the definition that used to exist in four copies
# ---------------------------------------------------------------------------


def test_bindable_params_excludes_self_and_varargs() -> None:
    def method(  # pragma: no cover - signature only
        self: Any, symbol: str, *args: Any, limit: int = 10, **kwargs: Any
    ) -> None: ...

    assert set(bindable_params(method)) == {"symbol", "limit"}


def test_var_keyword_does_not_make_a_method_look_required() -> None:
    """``**kwargs`` has no default; counting it would invent a required param.

    This is the disagreement between the pre-#188 copies:
    ``partition_params_for_method`` filtered only on the name ``self`` while
    the dispatch gate also filtered on parameter *kind*, so the two could
    classify the same method differently.
    """

    def method(symbol: str, **kwargs: Any) -> None: ...  # pragma: no cover

    assert uncovered_required_params(method, ["symbol"]) == frozenset()
    assert method_dispatch_compatible(method, ["symbol"])

    mandatory, optional = partition_params_for_method(
        [_Param("symbol")], [_Param("kwargs")], method
    )
    assert _names(mandatory) == {"symbol"}
    # ``kwargs`` is not a fillable parameter, so it is dropped, not advertised.
    assert _names(optional) == set()


# ---------------------------------------------------------------------------
# Dispatch gate
# ---------------------------------------------------------------------------


def test_uncovered_required_params_names_the_gap() -> None:
    def method(cik: str, report_date: str) -> None: ...  # pragma: no cover

    assert uncovered_required_params(method, ["cik", "year", "quarter"]) == frozenset(
        {"report_date"}
    )
    assert not method_dispatch_compatible(method, ["cik", "year", "quarter"])


def test_defaulted_params_are_never_uncovered() -> None:
    def method(symbol: str, from_date: str | None = None) -> None:  # pragma: no cover
        ...

    assert uncovered_required_params(method, ["symbol"]) == frozenset()
    assert method_dispatch_compatible(method, ["symbol"])


def test_compatible_is_exactly_the_absence_of_uncovered_params() -> None:
    """The two must not be able to disagree — one is defined by the other."""

    def method(a: str, b: str, c: str = "") -> None: ...  # pragma: no cover

    for wire in ([], ["a"], ["b"], ["a", "b"], ["a", "b", "c"]):
        assert method_dispatch_compatible(method, wire) == (
            not uncovered_required_params(method, wire)
        )


# ---------------------------------------------------------------------------
# Invoke-time mapping
# ---------------------------------------------------------------------------


def test_map_tool_kwargs_renames_and_drops() -> None:
    def method(  # pragma: no cover - signature only
        symbol: str, from_date: str | None = None, to_date: str | None = None
    ) -> None: ...

    mapped = map_tool_kwargs_to_method(
        method,
        {"symbol": "AAPL", "from": "2024-01-01", "to": None, "bogus": "x"},
    )
    # ``to`` is dropped so the method default applies; ``bogus`` reaches no
    # parameter and would be a TypeError if passed through.
    assert mapped == {"symbol": "AAPL", "from_date": "2024-01-01"}


def test_partition_without_a_method_is_the_identity() -> None:
    mandatory = [_Param("symbol")]
    optional = [_Param("limit")]
    got_mand, got_opt = partition_params_for_method(mandatory, optional, None)
    assert got_mand == mandatory
    assert got_opt == optional


def test_partition_demotes_params_the_method_defaults() -> None:
    def method(symbol: str, period: str = "annual") -> None: ...  # pragma: no cover

    mandatory, optional = partition_params_for_method(
        [_Param("symbol"), _Param("period"), _Param("structure")], [], method
    )
    assert _names(mandatory) == {"symbol"}
    assert _names(optional) == {"period"}
    # ``structure`` maps to nothing on the method, so advertising it would ask
    # an LLM for a value that never reaches the API.


# ---------------------------------------------------------------------------
# The two resolvers
# ---------------------------------------------------------------------------


def _client_double() -> Any:
    def profile(symbol: str) -> str:  # pragma: no cover - identity only
        return symbol

    return SimpleNamespace(company=SimpleNamespace(get_profile=profile, data=42))


def test_both_resolvers_reach_the_same_callable() -> None:
    client = _client_double()
    assert resolve_client_method(client, "company", "get_profile") is resolve_attr(
        client, "company.get_profile"
    )


def test_strict_resolver_raises_on_a_missing_link() -> None:
    client = _client_double()
    with pytest.raises(RuntimeError, match=r"Attribute chain .* failed at 'nope'"):
        resolve_attr(client, "company.nope")
    with pytest.raises(RuntimeError, match=r"failed at 'ghost'"):
        resolve_attr(client, "ghost.get_profile")


def test_strict_resolver_rejects_a_non_callable() -> None:
    with pytest.raises(RuntimeError, match=r"is not callable"):
        resolve_attr(_client_double(), "company.data")


def test_lenient_resolver_returns_none_for_the_same_misses() -> None:
    client = _client_double()
    assert resolve_client_method(client, "company", "nope") is None
    assert resolve_client_method(client, "ghost", "get_profile") is None
    assert resolve_client_method(client, "company", "data") is None


def test_dispatch_resolver_refuses_an_unfillable_shape() -> None:
    def get_form_13f(cik: str, report_date: str) -> None: ...  # pragma: no cover

    client = SimpleNamespace(institutional=SimpleNamespace(get_form_13f=get_form_13f))
    assert (
        resolve_dispatch_method(
            client, "institutional", "get_form_13f", ["cik", "year", "quarter"]
        )
        is None
    )
    assert (
        resolve_dispatch_method(
            client, "institutional", "get_form_13f", ["cik", "report_date"]
        )
        is get_form_13f
    )


def test_binding_layer_imports_without_optional_extras() -> None:
    """No langchain, no mcp — only the standard library.

    ``fmp_data.lc`` raises at import without its extra and ``fmp_data.mcp``
    calls ``sys.exit(1)``, so a binding layer importing either would be
    unusable in the environment CI actually installs.
    """
    module = inspect.getmodule(bindable_params)
    assert module is not None
    assert module.__name__ == "fmp_data.tool_binding"

    # Read the imports rather than grepping the text: the module's own
    # docstring names both integrations, and a guard that cannot tell prose
    # from an import statement fails on correct code.
    imported: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(module))):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    forbidden = {"fmp_data.lc", "fmp_data.mcp", "langchain", "langchain_core", "faiss"}
    offenders = sorted(
        name
        for name in imported
        for bad in forbidden
        if name == bad or name.startswith(f"{bad}.")
    )
    assert not offenders, (
        f"the shared binding layer must not import optional-extra modules: {offenders}"
    )
