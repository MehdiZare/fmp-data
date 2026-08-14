"""Closed request vocabularies: period, interval, timeframe.

These must stay three *different* period types. One union enum is how
``annual`` leaked onto financial-reports (FY/Qn only).
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Literal, get_args, get_origin, get_type_hints

from fmp_data.models import Endpoint
from fmp_data.schema import (
    INTERVAL_VALUES,
    PERIOD_ANNUAL_QUARTER_VALUES,
    PERIOD_FISCAL_VALUES,
    PERIOD_VALUES,
    TECHNICAL_INTERVAL_VALUES,
    TIMEFRAME_VALUES,
    Interval,
    Period,
    PeriodAnnualQuarter,
    PeriodFiscal,
    Timeframe,
    literal_values,
)
from fmp_data.tool_binding import bindable_params
from tests.e2e.harness import build_kwargs, discover_cases


def test_period_aliases_are_distinct_contracts() -> None:
    assert literal_values(PeriodAnnualQuarter) == ("annual", "quarter")
    assert literal_values(PeriodFiscal) == ("FY", "Q1", "Q2", "Q3", "Q4")
    assert set(literal_values(Period)) == {
        "annual",
        "quarter",
        "FY",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
    }
    # The wide alias is a union of the two contracts, not a third set.
    assert set(literal_values(Period)) == set(PERIOD_ANNUAL_QUARTER_VALUES) | set(
        PERIOD_FISCAL_VALUES
    )


def test_interval_is_a_strict_subset_of_timeframe() -> None:
    assert literal_values(Interval) == (
        "1min",
        "5min",
        "15min",
        "30min",
        "1hour",
        "4hour",
    )
    assert literal_values(Timeframe) == (
        "1min",
        "5min",
        "15min",
        "30min",
        "1hour",
        "4hour",
        "1day",
    )
    assert set(INTERVAL_VALUES) < set(TIMEFRAME_VALUES)


def _closed_sets() -> tuple[frozenset[str], ...]:
    return (
        frozenset(PERIOD_ANNUAL_QUARTER_VALUES),
        frozenset(PERIOD_FISCAL_VALUES),
        frozenset(PERIOD_VALUES),
        frozenset(INTERVAL_VALUES),
        frozenset(TIMEFRAME_VALUES),
    )


def _all_endpoints() -> list[Endpoint[Any]]:
    found: list[Endpoint[Any]] = []
    import pkgutil

    import fmp_data

    for info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not info.name.endswith(".endpoints"):
            continue
        module = importlib.import_module(info.name)
        for value in vars(module).values():
            if isinstance(value, Endpoint):
                found.append(value)
    return found


def test_endpoint_closed_valid_values_come_from_the_typed_sets() -> None:
    allowed = _closed_sets()
    unknown: list[str] = []
    for endpoint in _all_endpoints():
        params = list(endpoint.mandatory_params) + list(endpoint.optional_params or [])
        for param in params:
            if param.name not in {"period", "interval", "timeframe"}:
                continue
            if not param.valid_values:
                continue
            values = frozenset(str(v) for v in param.valid_values)
            if values not in allowed:
                unknown.append(f"{endpoint.name}.{param.name}={sorted(values)}")
    assert not unknown, (
        "endpoint valid_values drifted from typed sets:\n  " + "\n  ".join(unknown)
    )


def _literal_members(annotation: Any) -> tuple[Any, ...] | None:
    if annotation is inspect.Parameter.empty:
        return None
    origin = get_origin(annotation)
    if origin is Literal:
        return get_args(annotation)
    if origin is None:
        return None
    collected: list[Any] = []
    for arg in get_args(annotation):
        if arg is type(None):
            continue
        members = _literal_members(arg)
        if members:
            collected.extend(members)
    return tuple(collected) if collected else None


def test_client_period_interval_annotations_are_the_typed_literals() -> None:
    """Every public period/interval/timeframe param is one of the Literals."""
    allowed = {
        frozenset(PERIOD_ANNUAL_QUARTER_VALUES),
        frozenset(PERIOD_FISCAL_VALUES),
        frozenset(PERIOD_VALUES),
        frozenset(INTERVAL_VALUES),
        frozenset(TIMEFRAME_VALUES),
        frozenset(TECHNICAL_INTERVAL_VALUES),
    }
    untyped: list[str] = []
    for case in discover_cases():
        try:
            hints = get_type_hints(case.func)
        except Exception:
            hints = {}
        for name in ("period", "interval", "timeframe"):
            if name not in bindable_params(case.func):
                continue
            members = _literal_members(hints.get(name, inspect.Parameter.empty))
            if members is None or frozenset(str(m) for m in members) not in allowed:
                untyped.append(f"{case.group}.{case.method}.{name}={members!r}")
    assert not untyped, "client methods still take a naked str:\n  " + "\n  ".join(
        untyped
    )


def test_financial_reports_are_fiscal_not_annual() -> None:
    """The contract the e2e sweep tripped over."""
    case = next(
        case
        for case in discover_cases()
        if case.group == "company" and case.method == "get_financial_reports_json"
    )
    hints = get_type_hints(case.func)
    assert _literal_members(hints["period"]) == PERIOD_FISCAL_VALUES


def test_harness_samples_required_period_from_the_annotation() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "batch" and case.method == "get_income_statement_bulk"
    )
    assert build_kwargs(case)["period"] == "FY"
