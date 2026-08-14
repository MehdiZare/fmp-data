"""Unit tests for the local VCR-backed client-method e2e harness."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fmp_data.exceptions import FMPError
from tests.e2e.harness import (
    NO_HTTP_METHODS,
    build_kwargs,
    classify_result,
    discover_cases,
    format_report,
    redact_text,
    select_cases,
    write_report,
)


def test_discover_cases_includes_public_client_methods() -> None:
    cases = discover_cases()
    keys = {(case.group, case.method) for case in cases}

    assert ("company", "get_profile") in keys
    assert ("market", "get_gainers") in keys
    assert ("batch", "get_quotes") in keys
    assert ("alternative", "get_crypto_quote") in keys
    assert len(cases) > 200


def test_discover_cases_skips_private_helpers() -> None:
    cases = discover_cases()
    names = {case.method for case in cases}
    assert not any(name.startswith("_") for name in names)


def test_discover_cases_marks_deprecated_methods() -> None:
    cases = discover_cases()
    deprecated = {(case.group, case.method) for case in cases if case.deprecated}
    assert ("company", "get_core_information") in deprecated


def test_kwargs_for_get_profile_use_aapl() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "company" and case.method == "get_profile"
    )
    assert build_kwargs(case) == {"symbol": "AAPL"}


def test_kwargs_for_crypto_quote_use_btcusd() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "alternative" and case.method == "get_crypto_quote"
    )
    assert build_kwargs(case)["symbol"] == "BTCUSD"


def test_kwargs_for_etf_holdings_use_spy() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "investment" and case.method == "get_etf_holdings"
    )
    kwargs = build_kwargs(case)
    assert kwargs["symbol"] == "SPY"


def test_kwargs_for_search_by_cik_use_a_cik() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "market" and case.method == "search_by_cik"
    )
    assert build_kwargs(case)["query"] == "0000320193"


def test_kwargs_for_search_by_cusip_use_a_cusip() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "market" and case.method == "search_by_cusip"
    )
    assert build_kwargs(case)["query"] == "037833100"


def test_kwargs_for_insider_trading_by_name_fill_reporting_name() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "institutional"
        and case.method == "get_insider_trading_by_name"
    )
    assert build_kwargs(case)["reporting_name"] == "Cook"


def test_kwargs_for_industry_classification_supply_a_one_of_param() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "sec" and case.method == "search_industry_classification"
    )
    kwargs = build_kwargs(case)
    assert kwargs.get("symbol") == "AAPL"
    case = next(
        case
        for case in discover_cases()
        if case.group == "batch" and case.method == "get_quotes"
    )
    assert build_kwargs(case)["symbols"] == ["AAPL", "MSFT"]


def test_kwargs_do_not_override_method_period_default() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "company" and case.method == "get_financial_reports_json"
    )
    kwargs = build_kwargs(case)
    assert "period" not in kwargs
    assert kwargs["year"] == 2024


def test_kwargs_pin_intraday_interval_for_vcr_paths() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "company" and case.method == "get_intraday_prices"
    )
    assert build_kwargs(case)["interval"] == "5min"


def test_logo_url_is_local_and_needs_no_cassette() -> None:
    assert ("company", "get_company_logo_url") in NO_HTTP_METHODS


def test_kwargs_fill_optional_dates_with_anchored_values() -> None:
    case = next(
        case
        for case in discover_cases()
        if case.group == "sec" and case.method == "search_by_symbol"
    )
    kwargs = build_kwargs(case)
    assert kwargs["from_date"] == date(2024, 1, 1)
    assert kwargs["to_date"] == date(2024, 1, 31)


def test_select_cases_filters_by_group_and_method() -> None:
    cases = discover_cases()
    selected = select_cases(cases, group="transcripts", method="get_transcript")
    assert len(selected) == 1
    assert selected[0].group == "transcripts"
    assert selected[0].method == "get_transcript"


def test_select_cases_can_drop_bulk() -> None:
    cases = discover_cases()
    selected = select_cases(cases, skip_bulk=True)
    assert all(not case.bulk for case in selected)
    assert any(case.bulk for case in cases)


def test_classify_non_empty_list_is_ok() -> None:
    result = classify_result([object()], allow_empty=False)
    assert result == "ok"


def test_classify_empty_list_is_empty() -> None:
    result = classify_result([], allow_empty=False)
    assert result == "empty"


def test_classify_empty_list_is_ok_when_allowed() -> None:
    result = classify_result([], allow_empty=True)
    assert result == "ok"


def test_classify_exception_is_error() -> None:
    result = classify_result(FMPError("nope"), allow_empty=False)
    assert result == "error"


def test_format_report_counts_statuses() -> None:
    text = format_report(
        [
            {"group": "company", "method": "get_profile", "status": "ok"},
            {"group": "company", "method": "get_peers", "status": "empty"},
            {"group": "market", "method": "get_gainers", "status": "error"},
        ]
    )
    assert "ok=1" in text
    assert "empty=1" in text
    assert "error=1" in text
    assert "company.get_peers" in text


def test_write_report_round_trips_json(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    rows = [{"group": "company", "method": "get_profile", "status": "ok"}]
    write_report(path, rows)
    assert path.is_file()
    assert "get_profile" in path.read_text(encoding="utf-8")


def test_redact_text_masks_apikey_query_values() -> None:
    raw = (
        "No match for the request "
        "(<Request (GET) https://example.test/x?apikey=SUPERSECRETKEY123>)"
    )
    assert "SUPERSECRETKEY123" not in redact_text(raw)
    assert "apikey=DUMMY_API_KEY" in redact_text(raw)  # pragma: allowlist secret


def test_unknown_group_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown group"):
        select_cases(discover_cases(), group="not-a-group")
