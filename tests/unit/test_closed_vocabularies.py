"""Closed request vocabularies: period, interval, timeframe.

These must stay three *different* period types. One union enum is how
``annual`` leaked onto financial-reports (FY/Qn only).
"""

from __future__ import annotations

import importlib
import inspect
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

import pytest

from fmp_data.async_client import AsyncFMPDataClient
from fmp_data.client import FMPDataClient
from fmp_data.company.schema import IntradayTimeInterval
from fmp_data.exceptions import ValidationError
from fmp_data.models import Endpoint
from fmp_data.schema import (
    INTERVAL_VALUES,
    PERIOD_ANNUAL_QUARTER_VALUES,
    PERIOD_FISCAL_VALUES,
    PERIOD_VALUES,
    TECHNICAL_INTERVAL_VALUES,
    TIMEFRAME_VALUES,
    Interval,
    IntervalAlias,
    IntervalEnum,
    Period,
    PeriodAnnualQuarter,
    PeriodFiscal,
    ReportingPeriodEnum,
    TechnicalInterval,
    Timeframe,
    literal_values,
)
from fmp_data.tool_binding import bindable_params
from tests.e2e.harness import (
    CLIENT_GROUPS,
    build_kwargs,
    discover_cases,
    first_closed_sample,
)

FISCAL_METHODS = frozenset(
    {
        ("company", "get_financial_reports_json"),
        ("company", "get_financial_reports_xlsx"),
        ("batch", "get_income_statement_bulk"),
        ("batch", "get_income_statement_growth_bulk"),
        ("batch", "get_balance_sheet_bulk"),
        ("batch", "get_balance_sheet_growth_bulk"),
        ("batch", "get_cash_flow_bulk"),
        ("batch", "get_cash_flow_growth_bulk"),
    }
)


def test_period_aliases_are_distinct_contracts() -> None:
    assert literal_values(PeriodAnnualQuarter) == ("annual", "quarter")
    assert literal_values(PeriodFiscal) == ("FY", "Q1", "Q2", "Q3", "Q4")
    assert literal_values(Period) == (
        "annual",
        "quarter",
        "FY",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
    )
    # The wide alias is the union of the two contracts, not a third list.
    assert literal_values(Period) == PERIOD_ANNUAL_QUARTER_VALUES + PERIOD_FISCAL_VALUES
    period_runtime: Any = Period
    assert get_origin(period_runtime) in {Union, UnionType}
    assert get_args(period_runtime) == (PeriodAnnualQuarter, PeriodFiscal)


def test_literal_values_flattens_unions_and_rejects_non_literals() -> None:
    assert literal_values(TechnicalInterval) == (
        *INTERVAL_VALUES,
        *literal_values(IntervalAlias),
    )
    assert literal_values(TechnicalInterval) == TECHNICAL_INTERVAL_VALUES
    with pytest.raises(TypeError, match=r"not a typing\.Literal alias"):
        literal_values(str)


def test_legacy_enums_match_the_literal_sets() -> None:
    """Keep leftover enums from drifting off the Literals."""
    assert tuple(member.value for member in ReportingPeriodEnum) == PERIOD_VALUES
    assert tuple(member.value for member in IntervalEnum) == INTERVAL_VALUES
    assert tuple(member.value for member in IntradayTimeInterval) == INTERVAL_VALUES


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
    timeframe_runtime: Any = Timeframe
    assert get_origin(timeframe_runtime) in {Union, UnionType}
    assert "1day" in literal_values(Timeframe)


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


def _endpoint_closed_params() -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    for endpoint in _all_endpoints():
        params = list(endpoint.mandatory_params) + list(endpoint.optional_params or [])
        for param in params:
            if param.name in {"period", "interval", "timeframe"}:
                found.append((f"{endpoint.name}.{param.name}", param))
    return found


def test_endpoint_closed_valid_values_come_from_the_typed_sets() -> None:
    allowed = _closed_sets()
    unknown: list[str] = []
    missing: list[str] = []
    for label, param in _endpoint_closed_params():
        if not param.valid_values:
            missing.append(label)
            continue
        values = frozenset(str(v) for v in param.valid_values)
        if values not in allowed:
            unknown.append(f"{label}={sorted(values)}")
    assert not missing, "closed param missing valid_values:\n  " + "\n  ".join(missing)
    assert not unknown, (
        "endpoint valid_values drifted from typed sets:\n  " + "\n  ".join(unknown)
    )


def test_fiscal_valid_values_reject_annual() -> None:
    fiscal = [
        (label, param)
        for label, param in _endpoint_closed_params()
        if param.name == "period"
        and frozenset(str(v) for v in (param.valid_values or []))
        == frozenset(PERIOD_FISCAL_VALUES)
    ]
    assert fiscal, "expected at least one fiscal period endpoint"
    for label, param in fiscal:
        with pytest.raises(ValidationError, match="Must be one of"):
            param.validate_value("annual")
        assert param.validate_value("FY") == "FY", label


def test_annual_quarter_valid_values_reject_fy() -> None:
    narrow = [
        (label, param)
        for label, param in _endpoint_closed_params()
        if param.name == "period"
        and frozenset(str(v) for v in (param.valid_values or []))
        == frozenset(PERIOD_ANNUAL_QUARTER_VALUES)
    ]
    assert narrow, "expected at least one annual/quarter period endpoint"
    for label, param in narrow:
        with pytest.raises(ValidationError, match="Must be one of"):
            param.validate_value("FY")
        assert param.validate_value("annual") == "annual", label


def _annotation_members(annotation: Any) -> tuple[Any, ...] | None:
    if annotation is inspect.Parameter.empty:
        return None
    try:
        return literal_values(annotation)
    except TypeError:
        origin = get_origin(annotation)
        if origin is None:
            return None
        collected: list[Any] = []
        for arg in get_args(annotation):
            if arg is type(None):
                continue
            members = _annotation_members(arg)
            if members:
                collected.extend(members)
        return tuple(collected) if collected else None


def _iter_group_methods(root_cls: type) -> list[tuple[str, str, Any]]:
    found: list[tuple[str, str, Any]] = []
    for group in CLIENT_GROUPS:
        prop = getattr(root_cls, group, None)
        if prop is None:
            continue
        getter = getattr(prop, "fget", None)
        if getter is None:
            continue
        annotation = inspect.signature(getter).return_annotation
        if isinstance(annotation, str):
            annotation = inspect.get_annotations(getter, eval_str=True).get(
                "return", annotation
            )
        if not isinstance(annotation, type):
            continue
        for name, func in inspect.getmembers(annotation, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            found.append((group, name, func))
    return found


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
    for root_cls in (FMPDataClient, AsyncFMPDataClient):
        for group, method, func in _iter_group_methods(root_cls):
            hints = get_type_hints(func)
            for name in ("period", "interval", "timeframe"):
                if name not in bindable_params(func):
                    continue
                members = _annotation_members(hints.get(name, inspect.Parameter.empty))
                if members is None or frozenset(str(m) for m in members) not in allowed:
                    untyped.append(
                        f"{root_cls.__name__}.{group}.{method}.{name}={members!r}"
                    )
    assert not untyped, "client methods still take a naked str:\n  " + "\n  ".join(
        untyped
    )


def test_fiscal_client_methods_stay_period_fiscal() -> None:
    """The contract the e2e sweep tripped over, on every fiscal method."""
    seen: set[tuple[str, str]] = set()
    wrong: list[str] = []
    for root_cls in (FMPDataClient, AsyncFMPDataClient):
        for group, method, func in _iter_group_methods(root_cls):
            key = (group, method)
            if key not in FISCAL_METHODS:
                continue
            seen.add(key)
            hints = get_type_hints(func)
            members = _annotation_members(hints.get("period", inspect.Parameter.empty))
            default = inspect.signature(func).parameters["period"].default
            if members != PERIOD_FISCAL_VALUES:
                wrong.append(
                    f"{root_cls.__name__}.{group}.{method} members={members!r}"
                )
            if default not in {"FY", inspect.Parameter.empty}:
                wrong.append(
                    f"{root_cls.__name__}.{group}.{method} default={default!r}"
                )
    missing = sorted(FISCAL_METHODS - seen)
    assert not missing, f"fiscal methods not found: {missing}"
    assert not wrong, "fiscal methods drifted off PeriodFiscal:\n  " + "\n  ".join(
        wrong
    )


def test_harness_samples_required_period_from_the_annotation() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "batch" and case.method == "get_income_statement_bulk"
    )
    kwargs = build_kwargs(case)
    assert kwargs["period"] == first_closed_sample(PeriodFiscal)
    assert first_closed_sample(PeriodFiscal) != first_closed_sample(PeriodAnnualQuarter)
    assert first_closed_sample(PeriodAnnualQuarter) == "annual"
    assert first_closed_sample(Period) == "annual"
    # Required fiscal sampling must not depend on the name-based fallback.
    assert first_closed_sample(PeriodFiscal) == "FY"


def test_income_statement_accepts_both_period_contracts() -> None:
    from fmp_data.fundamental.endpoints import INCOME_STATEMENT

    period = next(
        param
        for param in (INCOME_STATEMENT.optional_params or [])
        if param.name == "period"
    )
    assert period.validate_value("annual") == "annual"
    assert period.validate_value("FY") == "FY"
    with pytest.raises(ValidationError, match="Must be one of"):
        period.validate_value("invalid")
