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


def test_legacy_enums_are_unpacked_from_the_literal_tuples() -> None:
    """#307: member values come from the Literal tuples, names stay put."""
    import fmp_data.company.schema as company_schema
    import fmp_data.schema as schema

    source = inspect.getsource(schema.ReportingPeriodEnum)
    assert "PERIOD_ANNUAL_QUARTER_VALUES" in source
    assert "PERIOD_FISCAL_VALUES" in source
    assert "INTERVAL_VALUES" in inspect.getsource(schema.IntervalEnum)
    assert "INTERVAL_VALUES" in inspect.getsource(company_schema.IntradayTimeInterval)
    assert ReportingPeriodEnum.ANNUAL.value == "annual"
    assert ReportingPeriodEnum.QUARTER.value == "quarter"
    assert ReportingPeriodEnum.FY.value == "FY"
    assert ReportingPeriodEnum.Q1.value == "Q1"
    assert ReportingPeriodEnum.Q2.value == "Q2"
    assert ReportingPeriodEnum.Q3.value == "Q3"
    assert ReportingPeriodEnum.Q4.value == "Q4"
    assert IntervalEnum.MIN_1.value == "1min"
    assert IntervalEnum.MIN_5.value == "5min"
    assert IntervalEnum.MIN_15.value == "15min"
    assert IntervalEnum.MIN_30.value == "30min"
    assert IntervalEnum.HOUR_1.value == "1hour"
    assert IntervalEnum.HOUR_4.value == "4hour"
    assert IntradayTimeInterval.ONE_MINUTE.value == "1min"
    assert IntradayTimeInterval.FIVE_MINUTES.value == "5min"
    assert IntradayTimeInterval.FIFTEEN_MINUTES.value == "15min"
    assert IntradayTimeInterval.THIRTY_MINUTES.value == "30min"
    assert IntradayTimeInterval.ONE_HOUR.value == "1hour"
    assert IntradayTimeInterval.FOUR_HOURS.value == "4hour"


def test_readme_sma_example_does_not_stack_interval_on_timeframe() -> None:
    """interval overrides timeframe; examples must show one or the other."""
    from pathlib import Path
    import re

    text = (Path(__file__).resolve().parents[2] / "README.md").read_text(
        encoding="utf-8"
    )
    fence = re.compile(r"```(?:python)?\n(.*?)```", re.S)
    stacked = [
        i
        for i, block in enumerate(fence.findall(text))
        if "get_sma" in block
        and (
            re.search(r"get_sma\([^)]*timeframe\s*=[^)]*interval\s*=", block, re.S)
            or re.search(r"get_sma\([^)]*interval\s*=[^)]*timeframe\s*=", block, re.S)
        )
    ]
    assert not stacked, (
        "get_sma examples must not pass both timeframe and interval; "
        "interval overrides timeframe:\n  README.md fence(s) "
        + ", ".join(map(str, stacked))
    )


def test_getting_started_income_statement_examples_use_period() -> None:
    """#308: get_income_statement takes Period, not PeriodAnnualQuarter."""
    from pathlib import Path
    import re

    root = Path(__file__).resolve().parents[2]
    fence = re.compile(r"```(?:python)?\n(.*?)```", re.S)
    offenders: list[str] = []
    for rel in ("README.md", "docs/index.md"):
        text = (root / rel).read_text(encoding="utf-8")
        for block in fence.findall(text):
            if "get_income_statement" in block and "PeriodAnnualQuarter" in block:
                offenders.append(rel)
    assert not offenders, (
        "get_income_statement takes Period; do not annotate "
        "PeriodAnnualQuarter in these examples:\n  " + "\n  ".join(offenders)
    )


def test_closed_vocabularies_are_public_exports() -> None:
    """#308 / #311: callers annotate against the live contracts from fmp_data."""
    import fmp_data

    assert fmp_data.Period is Period
    assert fmp_data.PeriodFiscal is PeriodFiscal
    assert fmp_data.PeriodAnnualQuarter is PeriodAnnualQuarter
    assert fmp_data.Interval is Interval
    assert fmp_data.Timeframe is Timeframe
    assert fmp_data.TechnicalInterval is TechnicalInterval
    for name in (
        "Period",
        "PeriodFiscal",
        "PeriodAnnualQuarter",
        "Interval",
        "TechnicalInterval",
        "Timeframe",
    ):
        assert name in fmp_data.__all__, name
    assert "1day" not in literal_values(fmp_data.TechnicalInterval)
    assert "daily" in literal_values(fmp_data.TechnicalInterval)
    assert "hourly" in literal_values(fmp_data.TechnicalInterval)


def test_deprecated_time_interval_tracks_technical_interval() -> None:
    """#309: leftover TimeInterval follows the live TechnicalInterval alias."""
    import warnings

    from pydantic import ValidationError as PydanticValidationError

    from fmp_data.technical.schema import TechnicalIndicatorArgs, TimeInterval

    assert literal_values(TimeInterval) == literal_values(TechnicalInterval)
    assert "daily" in literal_values(TimeInterval)
    assert "hourly" in literal_values(TimeInterval)
    assert "1day" not in literal_values(TimeInterval)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        TechnicalIndicatorArgs(symbol="AAPL", interval="daily")
        TechnicalIndicatorArgs(symbol="AAPL", interval="hourly")
        with pytest.raises(PydanticValidationError):
            TechnicalIndicatorArgs(symbol="AAPL", interval="1day")


def test_deprecated_intraday_args_do_not_hardcode_interval_values() -> None:
    """#309: BaseIntradayArgs must not keep a second interval list."""
    import warnings

    from pydantic import ValidationError as PydanticValidationError

    from fmp_data.alternative.schema import BaseIntradayArgs, CryptoIntradayArgs

    source = inspect.getsource(BaseIntradayArgs)
    assert "1min" not in source
    assert "4hour" not in source
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        CryptoIntradayArgs(symbol="BTCUSD", interval="5min")
        with pytest.raises(PydanticValidationError):
            CryptoIntradayArgs(symbol="BTCUSD", interval="1day")


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
