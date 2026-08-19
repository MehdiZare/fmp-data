"""LangChain tools dispatch through client methods, not bare endpoints (#172).

Client methods carry behaviour the endpoint declaration cannot express —
default date windows, one-of constraints, post-processing. Tools used to call
``client.request(endpoint, **kwargs)`` and skip all of it. These tests pin the
method path and the wire-name → method-name mapping it depends on.
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

from langchain_core.embeddings import Embeddings

from fmp_data.base import BaseClient
from fmp_data.company.endpoints import (
    EMPLOYEE_COUNT,
    PRODUCT_REVENUE_SEGMENTATION,
)
from fmp_data.institutional.endpoints import FORM_13F
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.vector_store import (
    EndpointVectorStore,
    map_tool_kwargs_to_method,
    method_dispatch_compatible,
    method_param_aliases,
    partition_params_for_method,
    resolve_client_method,
    resolve_method_param_name,
)
from fmp_data.sec.endpoints import (
    INDUSTRY_CLASSIFICATION_SEARCH,
    SEC_FILINGS_SEARCH_SYMBOL,
)
from fmp_data.sec.mapping import SEC_ENDPOINTS_SEMANTICS


class _StubEmbeddings(Embeddings):
    def embed_query(self, text: str) -> list[float]:
        return [0.1] * 8

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 8 for _ in texts]


def _store_with(
    client: Any, registry: EndpointRegistry, tmp_path: Any
) -> EndpointVectorStore:
    return EndpointVectorStore(
        client=client,
        registry=registry,
        embeddings=_StubEmbeddings(),
        cache_dir=str(tmp_path),
        store_name="method-dispatch",
    )


def _sec_registry(*semantics_keys: str) -> EndpointRegistry:
    """Build a registry from SEC semantics table keys (not method names)."""
    from fmp_data.sec.mapping import SEC_ENDPOINT_MAP

    registry = EndpointRegistry()
    endpoints = {}
    for key in semantics_keys:
        sem = SEC_ENDPOINTS_SEMANTICS[key]
        endpoints[sem.method_name] = (SEC_ENDPOINT_MAP[sem.method_name], sem)
    failures = registry.register_batch(endpoints)
    assert failures == {}, failures
    return registry


def _institutional_registry(*semantics_keys: str) -> EndpointRegistry:
    """Build a registry from institutional semantics table keys."""
    from fmp_data.institutional.mapping import (
        INSTITUTIONAL_ENDPOINT_MAP,
        INSTITUTIONAL_ENDPOINTS_SEMANTICS,
    )

    registry = EndpointRegistry()
    endpoints = {}
    for key in semantics_keys:
        sem = INSTITUTIONAL_ENDPOINTS_SEMANTICS[key]
        endpoints[sem.method_name] = (INSTITUTIONAL_ENDPOINT_MAP[sem.method_name], sem)
    failures = registry.register_batch(endpoints)
    assert failures == {}, failures
    return registry


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_method_param_aliases_cover_wire_renames() -> None:
    assert "from_date" in method_param_aliases("from")
    assert "start_date" in method_param_aliases("from")
    assert "period_length" in method_param_aliases("periodLength")
    assert "sic_code" in method_param_aliases("sicCode")
    assert "indicator_name" in method_param_aliases("name")


def test_date_aliases_include_trade_date() -> None:
    assert "trade_date" in method_param_aliases("date")
    assert resolve_method_param_name("date", {"trade_date", "symbol"}) == "trade_date"


def test_method_dispatch_compatible_rejects_uncovered_required() -> None:
    def get_form_13f(cik: str | int, report_date: date) -> list[Any]:
        return []

    assert not method_dispatch_compatible(get_form_13f, ["cik", "year", "quarter"])
    assert method_dispatch_compatible(get_form_13f, ["cik", "report_date"])


def test_resolve_method_param_name_prefers_exact_then_alias() -> None:
    assert resolve_method_param_name("symbol", {"symbol", "from_date"}) == "symbol"
    assert resolve_method_param_name("from", {"symbol", "from_date"}) == "from_date"
    assert resolve_method_param_name("from", {"symbol", "start_date"}) == "start_date"
    assert (
        resolve_method_param_name("periodLength", {"period_length"}) == "period_length"
    )
    assert resolve_method_param_name("limit", {"symbol"}) is None


def test_map_tool_kwargs_drops_none_so_method_defaults_apply() -> None:
    def search_by_symbol(
        symbol: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Any]:
        return []

    mapped = map_tool_kwargs_to_method(
        search_by_symbol,
        {"symbol": "AAPL", "from": None, "to": None, "page": 1},
    )
    assert mapped == {"symbol": "AAPL", "page": 1}
    assert "from_date" not in mapped
    assert "to_date" not in mapped


def test_map_tool_kwargs_renames_wire_fields() -> None:
    def search_by_form_type(
        form_type: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Any]:
        return []

    mapped = map_tool_kwargs_to_method(
        search_by_form_type,
        {
            "formType": "10-K",
            "from": "2024-01-01",
            "to": "2024-12-31",
            "page": 0,
            "limit": 50,
        },
    )
    assert mapped == {
        "form_type": "10-K",
        "from_date": "2024-01-01",
        "to_date": "2024-12-31",
        "page": 0,
        "limit": 50,
    }


def test_partition_promotes_method_defaults_to_optional() -> None:
    """Endpoint-mandatory from/to become optional when the method defaults them."""

    def search_by_symbol(
        symbol: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Any]:
        return []

    mandatory, optional = partition_params_for_method(
        SEC_FILINGS_SEARCH_SYMBOL.mandatory_params,
        SEC_FILINGS_SEARCH_SYMBOL.optional_params or [],
        search_by_symbol,
    )
    mand_names = {p.name for p in mandatory}
    opt_names = {p.name for p in optional}
    assert mand_names == {"symbol"}
    assert "from" in opt_names
    assert "to" in opt_names
    assert "page" in opt_names
    assert "limit" in opt_names


def test_partition_without_method_keeps_endpoint_lists() -> None:
    mandatory, optional = partition_params_for_method(
        SEC_FILINGS_SEARCH_SYMBOL.mandatory_params,
        SEC_FILINGS_SEARCH_SYMBOL.optional_params or [],
        None,
    )
    assert [p.name for p in mandatory] == [
        p.name for p in SEC_FILINGS_SEARCH_SYMBOL.mandatory_params
    ]
    assert [p.name for p in optional] == [
        p.name for p in (SEC_FILINGS_SEARCH_SYMBOL.optional_params or [])
    ]


def test_resolve_client_method_walks_subclient() -> None:
    method = Mock(name="search_by_symbol")
    client = SimpleNamespace(sec=SimpleNamespace(search_by_symbol=method))
    assert resolve_client_method(client, "sec", "search_by_symbol") is method
    assert resolve_client_method(client, "sec", "missing") is None
    assert resolve_client_method(SimpleNamespace(), "sec", "search_by_symbol") is None


# ---------------------------------------------------------------------------
# create_tool integration
# ---------------------------------------------------------------------------


def test_tool_invokes_client_method_not_request(tmp_path: Any) -> None:
    """The motivating #172 path: SEC search with only a symbol hits the method."""
    calls: list[dict[str, Any]] = []

    def search_by_symbol(
        symbol: str,
        page: int = 0,
        limit: int = 100,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Any]:
        calls.append(
            {
                "symbol": symbol,
                "page": page,
                "limit": limit,
                "from_date": from_date,
                "to_date": to_date,
            }
        )
        return []

    request = Mock(side_effect=AssertionError("must not call client.request"))
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=request,
            sec=SimpleNamespace(search_by_symbol=search_by_symbol),
        ),
    )
    registry = _sec_registry("filings_search_symbol")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("search_by_symbol")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    # from/to are method-defaulted → optional in the schema
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == {"symbol"}

    result = tool.invoke({"symbol": "AAPL"})
    assert result["status"] == "success"
    assert len(calls) == 1
    assert calls[0]["symbol"] == "AAPL"
    # Method defaults applied (not forced None from omitted wire params)
    assert calls[0]["from_date"] is None  # method default before its own fill
    assert calls[0]["to_date"] is None
    assert calls[0]["page"] == 0
    assert calls[0]["limit"] == 100
    request.assert_not_called()


def test_tool_falls_back_to_request_without_subclient(tmp_path: Any) -> None:
    """Bare BaseClient / test doubles without sub-clients keep working."""
    request = Mock(return_value=[{"symbol": "AAPL"}])
    client = cast(BaseClient, SimpleNamespace(request=request))
    registry = _sec_registry("filings_search_symbol")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("search_by_symbol")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    # No method → endpoint mandatory set unchanged
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == {"symbol", "from", "to"}

    result = tool.invoke({"symbol": "AAPL", "from": "2024-01-01", "to": "2024-01-31"})
    assert result["status"] == "success"
    request.assert_called_once()
    assert request.call_args.args[0] is SEC_FILINGS_SEARCH_SYMBOL


def test_industry_classification_one_of_constraint_surfaces(tmp_path: Any) -> None:
    """Method-level one-of enforcement becomes a structured validation error."""

    def search_industry_classification(
        symbol: str | None = None,
        cik: str | int | None = None,
        sic_code: str | None = None,
    ) -> list[Any]:
        if not symbol and not cik and not sic_code:
            raise ValueError("Provide at least one of symbol, cik, or sic_code")
        return []

    client = cast(
        BaseClient,
        SimpleNamespace(
            request=Mock(side_effect=AssertionError("must not call request")),
            sec=SimpleNamespace(
                search_industry_classification=search_industry_classification
            ),
        ),
    )
    registry = _sec_registry("industry_classification_search")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("search_industry_classification")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    # All three are optional on the method → none required on the schema
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == set()

    empty = tool.invoke({})
    assert empty["status"] == "error"
    assert empty["error_type"] == "validation_error"
    assert "at least one" in empty["details"]["original_error"].lower()

    ok = tool.invoke({"symbol": "AAPL"})
    assert ok["status"] == "success"


def test_partition_industry_classification_all_optional() -> None:
    def search_industry_classification(
        symbol: str | None = None,
        cik: str | int | None = None,
        sic_code: str | None = None,
    ) -> list[Any]:
        return []

    mandatory, optional = partition_params_for_method(
        INDUSTRY_CLASSIFICATION_SEARCH.mandatory_params,
        INDUSTRY_CLASSIFICATION_SEARCH.optional_params or [],
        search_industry_classification,
    )
    assert mandatory == []
    assert {p.name for p in optional} == {"symbol", "cik", "sicCode"}


def test_partition_omits_unmapped_when_method_active() -> None:
    """Unmapped endpoint params (e.g. employee-count limit) are dropped.

    Revenue ``structure`` is advertised once the method accepts it.
    """

    def get_product_revenue_segmentation(
        symbol: str, period: str = "annual", structure: str = "flat"
    ) -> list[Any]:
        return []

    def get_employee_count(symbol: str) -> list[Any]:
        return []

    rev_mandatory, rev_optional = partition_params_for_method(
        PRODUCT_REVENUE_SEGMENTATION.mandatory_params,
        PRODUCT_REVENUE_SEGMENTATION.optional_params or [],
        get_product_revenue_segmentation,
    )
    assert {p.name for p in rev_mandatory} == {"symbol"}
    assert {p.name for p in rev_optional} == {"period", "structure"}

    emp_mandatory, emp_optional = partition_params_for_method(
        EMPLOYEE_COUNT.mandatory_params,
        EMPLOYEE_COUNT.optional_params or [],
        get_employee_count,
    )
    assert {p.name for p in emp_mandatory} == {"symbol"}
    assert emp_optional == []
    assert "limit" not in {p.name for p in emp_mandatory + emp_optional}

    # Without a method, lists stay as declared (structure and limit optional).
    bare_mand, bare_opt = partition_params_for_method(
        PRODUCT_REVENUE_SEGMENTATION.mandatory_params,
        PRODUCT_REVENUE_SEGMENTATION.optional_params or [],
        None,
    )
    assert "structure" not in {p.name for p in bare_mand}
    assert "structure" in {p.name for p in bare_opt}
    bare_emp_mand, bare_emp_opt = partition_params_for_method(
        EMPLOYEE_COUNT.mandatory_params,
        EMPLOYEE_COUNT.optional_params or [],
        None,
    )
    assert "limit" in {p.name for p in bare_emp_opt}
    assert bare_emp_mand  # symbol still present


def test_form_13f_dispatches_through_wire_shaped_method(tmp_path: Any) -> None:
    """FORM_13F now reaches a method whose signature matches the wire (#188).

    ``form_13f`` semantics used to name ``get_form_13f(cik, report_date)``,
    which no alias could fill from wire ``year``/``quarter``, so the tool fell
    back to ``client.request``. It now names ``get_form_13f_by_quarter``,
    which takes the wire triple as-is. The tool schema is unchanged — that is
    the point: the same arguments now go through the client method, so its
    error handling and post-processing apply.
    """
    calls: list[dict[str, Any]] = []

    def get_form_13f_by_quarter(cik: str | int, year: int, quarter: int) -> list[Any]:
        calls.append({"cik": cik, "year": year, "quarter": quarter})
        return []

    request = Mock(side_effect=AssertionError("must not fall back to request"))
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=request,
            institutional=SimpleNamespace(
                get_form_13f_by_quarter=get_form_13f_by_quarter
            ),
        ),
    )
    registry = _institutional_registry("form_13f")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("get_form_13f_by_quarter")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == {"cik", "year", "quarter"}

    result = tool.invoke({"cik": "0001067983", "year": 2023, "quarter": 3})
    assert result["status"] == "success"
    request.assert_not_called()
    assert calls == [{"cik": "0001067983", "year": 2023, "quarter": 3}]


def test_institutional_holdings_dispatches_through_wire_shaped_method(
    tmp_path: Any,
) -> None:
    """INSTITUTIONAL_HOLDINGS reaches the matching wire-shaped method (#188).

    Same story as ``form_13f``: semantics used to name a date-shaped method
    that wire ``year``/``quarter`` could not fill. It now names
    ``get_institutional_holdings_by_quarter`` so the tool dispatches through
    the client method with an unchanged argument schema.
    """
    calls: list[dict[str, Any]] = []

    def get_institutional_holdings_by_quarter(
        symbol: str, year: int, quarter: int
    ) -> list[Any]:
        calls.append({"symbol": symbol, "year": year, "quarter": quarter})
        return []

    request = Mock(side_effect=AssertionError("must not fall back to request"))
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=request,
            institutional=SimpleNamespace(
                get_institutional_holdings_by_quarter=get_institutional_holdings_by_quarter
            ),
        ),
    )
    registry = _institutional_registry("institutional_holdings")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("get_institutional_holdings_by_quarter")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == {"symbol", "year", "quarter"}

    result = tool.invoke({"symbol": "AAPL", "year": 2023, "quarter": 3})
    assert result["status"] == "success"
    request.assert_not_called()
    assert calls == [{"symbol": "AAPL", "year": 2023, "quarter": 3}]


def test_unmappable_method_shape_still_falls_back_to_request(tmp_path: Any) -> None:
    """The request-fallback path stays live even with an empty allowlist.

    Nothing in the catalogue needs it since #188
    (``tests/unit/lc/test_endpoint_method_coverage.py`` asserts the allowlist
    is empty), so without a synthetic case the fallback branch of
    ``create_tool`` would go untested and could rot before the next shape
    mismatch lands. Here the client's method keeps the old
    ``report_date``-shaped signature, which wire ``year``/``quarter`` cannot
    fill.
    """

    def get_form_13f_by_quarter(cik: str | int, report_date: date) -> list[Any]:
        raise AssertionError("must not call method with unmappable shape")

    request = Mock(return_value=[])
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=request,
            institutional=SimpleNamespace(
                get_form_13f_by_quarter=get_form_13f_by_quarter
            ),
        ),
    )
    registry = _institutional_registry("form_13f")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("get_form_13f_by_quarter")
    assert info is not None

    tool = cast(Any, store.create_tool(info))
    # Fallback keeps the pre-#172 wire schema (cik/year/quarter).
    required = {
        name
        for name, field in tool.args_schema.model_fields.items()
        if field.is_required()
    }
    assert required == {"cik", "year", "quarter"}

    result = tool.invoke({"cik": "0001067983", "year": 2023, "quarter": 3})
    assert result["status"] == "success"
    request.assert_called_once()
    assert request.call_args.args[0] is FORM_13F
    assert request.call_args.kwargs == {
        "cik": "0001067983",
        "year": 2023,
        "quarter": 3,
    }


# ---------------------------------------------------------------------------
# Fallback is announced, not silent (#194)
# ---------------------------------------------------------------------------


def _fallback_store(client: Any, tmp_path: Any) -> tuple[Any, Any]:
    """A store over *client* for the form_13f endpoint, with a mock logger."""
    registry = _institutional_registry("form_13f")
    store = _store_with(client, registry, tmp_path)
    store.logger = Mock()
    info = registry.get_endpoint("get_form_13f_by_quarter")
    assert info is not None
    return store, info


def test_bare_client_fallback_is_debug_not_warning(tmp_path: Any) -> None:
    """A store on a bare client has no sub-clients by design.

    Warning here would emit one line per endpoint in the catalogue and bury
    the two statuses that do mean something is wrong.
    """
    client = cast(BaseClient, SimpleNamespace(request=Mock(return_value=[])))
    store, info = _fallback_store(client, tmp_path)

    store.create_tool(info)

    store.logger.warning.assert_not_called()
    store.logger.debug.assert_called_once()
    # %-style formatting: template plus args; join them for the assertion.
    args = store.logger.debug.call_args[0]
    combined = " ".join(str(a) for a in args)
    assert "no" in combined and "institutional" in combined and "sub-client" in combined


def test_unmappable_method_shape_fallback_warns_once(tmp_path: Any) -> None:
    """Sub-client present, shape incompatible → one WARNING naming the gap (#194)."""

    def get_form_13f_by_quarter(cik: str, report_date: date) -> list[Any]:
        raise AssertionError("must not be called")  # pragma: no cover

    client = cast(
        BaseClient,
        SimpleNamespace(
            request=Mock(return_value=[]),
            institutional=SimpleNamespace(
                get_form_13f_by_quarter=get_form_13f_by_quarter
            ),
        ),
    )
    store, info = _fallback_store(client, tmp_path)

    store.create_tool(info)

    store.logger.warning.assert_called_once()
    args = store.logger.warning.call_args[0]
    combined = " ".join(str(a) for a in args)
    assert "report_date" in combined
    store.logger.debug.assert_not_called()


def test_missing_method_fallback_warns(tmp_path: Any) -> None:
    """A sub-client that lacks the named method is a real misconfiguration."""
    client = cast(
        BaseClient,
        SimpleNamespace(request=Mock(return_value=[]), institutional=SimpleNamespace()),
    )
    store, info = _fallback_store(client, tmp_path)

    store.create_tool(info)

    store.logger.warning.assert_called_once()
    args = store.logger.warning.call_args[0]
    combined = " ".join(str(a) for a in args)
    assert "get_form_13f_by_quarter" in combined
    assert "no callable" in combined


def test_successful_dispatch_logs_no_fallback(tmp_path: Any) -> None:
    """No warning, no debug line when the method binds — silence means fine."""

    def get_form_13f_by_quarter(cik: str, year: int, quarter: int) -> list[Any]:
        return []

    client = cast(
        BaseClient,
        SimpleNamespace(
            request=Mock(side_effect=AssertionError("must not fall back")),
            institutional=SimpleNamespace(
                get_form_13f_by_quarter=get_form_13f_by_quarter
            ),
        ),
    )
    store, info = _fallback_store(client, tmp_path)

    store.create_tool(info)

    store.logger.warning.assert_not_called()
    store.logger.debug.assert_not_called()


def test_tool_error_envelope_redacts_reflected_api_keys(tmp_path: Any) -> None:
    """The envelope is the tool's return value, so it reaches the model (#252).

    `str()` of an `httpx.HTTPStatusError` stringifies the request URL, which
    for this client always carries `apikey=`. That dict goes into the agent
    scratchpad, the chat history and any tracing backend -- `base.py` suppresses
    this exact leak on its own paths, but nothing under `lc/` was redacting.
    """
    planted = "PLANTEDCREDENTIALVALUE"
    boom = RuntimeError(
        f"Server error '500' for url "
        f"'https://financialmodelingprep.com/stable/profile?apikey={planted}'"
    )
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=Mock(side_effect=boom),
            sec=SimpleNamespace(
                search_industry_classification=Mock(side_effect=boom),
            ),
        ),
    )
    registry = _sec_registry("industry_classification_search")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("search_industry_classification")
    assert info is not None

    result = cast(Any, store.create_tool(info)).invoke({"symbol": "AAPL"})

    assert result["status"] == "error"
    rendered = repr(result)
    assert planted not in rendered, f"tool envelope leaked the key: {rendered}"
    assert "[REDACTED]" in rendered


def test_validation_error_envelope_redacts_reflected_api_keys(tmp_path: Any) -> None:
    """Field-error lines must use the redacted message, not raw ``str(e)``."""
    planted = "PLANTEDCREDENTIALVALUE"
    boom = ValueError(
        "  extra  url "
        f"'https://financialmodelingprep.com/stable/profile?apikey={planted}'"
    )
    client = cast(
        BaseClient,
        SimpleNamespace(
            request=Mock(side_effect=boom),
            sec=SimpleNamespace(
                search_industry_classification=Mock(side_effect=boom),
            ),
        ),
    )
    registry = _sec_registry("industry_classification_search")
    store = _store_with(client, registry, tmp_path)
    info = registry.get_endpoint("search_industry_classification")
    assert info is not None

    result = cast(Any, store.create_tool(info)).invoke({"symbol": "AAPL"})

    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"
    rendered = repr(result)
    assert planted not in rendered, f"validation envelope leaked the key: {rendered}"
    assert planted not in "".join(result["details"]["validation_errors"])
    assert "[REDACTED]" in rendered
