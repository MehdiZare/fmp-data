"""Local VCR-backed sweep of every public sync client method.

This is a maintainer tool, not a default test. Discovery walks
``FMPDataClient`` group properties; each public method is one case.
See ``docs/superpowers/specs/2026-08-14-e2e-client-sweep-design.md``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
import importlib
import inspect
import json
import os
from pathlib import Path
import re
import time
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

from fmp_data.client import FMPDataClient
from fmp_data.exceptions import RateLimitError
from fmp_data.tool_binding import bindable_params

CLIENT_GROUPS: tuple[str, ...] = (
    "alternative",
    "batch",
    "company",
    "economics",
    "fundamental",
    "index",
    "institutional",
    "intelligence",
    "investment",
    "market",
    "sec",
    "technical",
    "transcripts",
)

ANCHORED_FROM = date(2024, 1, 1)
ANCHORED_TO = date(2024, 1, 31)
ANCHORED_AS_OF = date(2024, 9, 30)

# Methods whose emptiness is about the entity, not a broken declaration.
ALLOW_EMPTY: frozenset[tuple[str, str]] = frozenset(
    {
        ("investment", "get_etf_holdings"),
        ("investment", "get_etf_info"),
        ("investment", "get_etf_sector_weightings"),
        ("investment", "get_etf_country_weightings"),
        ("investment", "get_mutual_fund_dates"),
        ("investment", "get_fund_disclosure"),
        ("investment", "search_fund_disclosure_holders"),
        ("institutional", "get_form_13f"),
        ("institutional", "get_form_13f_dates"),
        ("institutional", "get_institutional_ownership_extract"),
        ("institutional", "get_institutional_ownership_dates"),
        ("institutional", "get_holder_performance_summary"),
        ("institutional", "get_holder_industry_breakdown"),
        ("intelligence", "get_senate_trades_by_name"),
        ("intelligence", "get_house_trades_by_name"),
        ("intelligence", "get_senate_trades_by_id"),
        ("intelligence", "get_house_trades_by_id"),
        ("intelligence", "search_crowdfunding"),
        ("intelligence", "get_crowdfunding_by_cik"),
        ("intelligence", "search_equity_offering"),
        ("intelligence", "get_equity_offering_by_cik"),
        ("economics", "get_commitment_of_traders_report"),
        ("economics", "get_commitment_of_traders_analysis"),
        ("market", "get_historical_industry_performance"),
        ("market", "get_historical_industry_pe"),
        ("market", "search_symbol"),
        ("institutional", "search_cik_by_name"),
    }
)

CASSETTE_ROOT = Path(__file__).resolve().parent / "vcr_cassettes"
REPORT_PATH = Path(__file__).resolve().parent / "reports" / "last-report.json"


@dataclass(frozen=True)
class SweepCase:
    group: str
    method: str
    func: Callable[..., Any]
    deprecated: bool
    bulk: bool
    endpoint_path: str | None = None


@dataclass
class CaseRow:
    group: str
    method: str
    status: str
    detail: str = ""
    path: str | None = None
    elapsed_ms: float = 0.0
    kwargs: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "group": self.group,
            "method": self.method,
            "status": self.status,
            "detail": self.detail,
            "path": self.path,
            "elapsed_ms": self.elapsed_ms,
            "kwargs": _jsonable(self.kwargs),
        }


def _jsonable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _client_class(group: str) -> type:
    prop = getattr(FMPDataClient, group)
    getter = prop.fget
    if getter is None:  # pragma: no cover - properties always have fget
        raise TypeError(f"{group} is not a client property")
    annotation = inspect.signature(getter).return_annotation
    if annotation is inspect.Signature.empty:
        raise TypeError(f"{group} property has no return annotation")
    if isinstance(annotation, str):
        hints = inspect.get_annotations(getter, eval_str=True)
        annotation = hints.get("return", annotation)
    if not isinstance(annotation, type):
        raise TypeError(f"{group} return annotation is not a class: {annotation!r}")
    return annotation


def _endpoint_path(group: str, method: str) -> str | None:
    try:
        module = importlib.import_module(f"fmp_data.{group}.mapping")
    except ImportError:
        return None
    for attr, value in vars(module).items():
        if attr.endswith("_ENDPOINT_MAP") and isinstance(value, dict):
            endpoint = value.get(method)
            if endpoint is not None:
                version = getattr(getattr(endpoint, "version", None), "value", None)
                path = getattr(endpoint, "path", None)
                if path:
                    return f"{version}/{path}" if version else str(path)
    return None


def discover_cases() -> list[SweepCase]:
    """Every public sync method on every ``FMPDataClient`` group."""
    cases: list[SweepCase] = []
    for group in CLIENT_GROUPS:
        client_cls = _client_class(group)
        for name, func in inspect.getmembers(client_cls, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            cases.append(
                SweepCase(
                    group=group,
                    method=name,
                    func=func,
                    deprecated=bool(getattr(func, "__fmp_deprecated__", False)),
                    bulk=name.endswith("_bulk"),
                    endpoint_path=_endpoint_path(group, name),
                )
            )
    cases.sort(key=lambda case: (case.group, case.method))
    return cases


def select_cases(
    cases: Sequence[SweepCase],
    *,
    group: str | None = None,
    method: str | None = None,
    skip_bulk: bool = False,
) -> list[SweepCase]:
    if group is not None and group not in CLIENT_GROUPS:
        raise ValueError(f"unknown group: {group}")
    selected = list(cases)
    if group is not None:
        selected = [case for case in selected if case.group == group]
    if method is not None:
        selected = [case for case in selected if case.method == method]
    if skip_bulk:
        selected = [case for case in selected if not case.bulk]
    return selected


def _inferred_symbol(group: str, method: str) -> str:
    name = method.lower()
    if "etf" in name:
        return "SPY"
    if "mutual_fund" in name or "fund_disclosure" in name:
        return "VTSAX"
    if "crypto" in name:
        return "BTCUSD"
    if "forex" in name:
        return "EURUSD"
    if "commodity" in name or "commodities" in name:
        return "GCUSD"
    if group == "alternative":
        return "BTCUSD"
    return "AAPL"


def _inferred_name(method: str) -> str:
    name = method.lower()
    if "senate" in name or "house" in name:
        return "Nancy Pelosi"
    if "mutual_fund" in name:
        return "Vanguard"
    return "Apple"


def _inferred_query(method: str) -> str:
    name = method.lower()
    if "cusip" in name:
        return "037833100"
    if "isin" in name:
        return "US0378331005"
    if "cik" in name:
        return "0000320193"
    return "Apple"


# Methods whose contract is "at least one of these optionals".
_ONE_OF_DEFAULTS: dict[tuple[str, str], dict[str, Any]] = {
    ("sec", "search_industry_classification"): {"symbol": "AAPL"},
}


_FIXED_SAMPLES: dict[str, Any] = {
    "symbols": ["AAPL", "MSFT"],
    "cik": "0001067983",
    "from_date": ANCHORED_FROM,
    "start_date": ANCHORED_FROM,
    "to_date": ANCHORED_TO,
    "end_date": ANCHORED_TO,
    "date": ANCHORED_AS_OF,
    "holdings_date": ANCHORED_AS_OF,
    "report_date": ANCHORED_AS_OF,
    "target_date": ANCHORED_AS_OF,
    "trade_date": ANCHORED_AS_OF,
    "indicator_name": "GDP",
    "company": "Apple",
    "reporting_name": "Cook",
    "form_type": "10-K",
    "exchange": "NASDAQ",
    "year": 2024,
    "quarter": 3,
    "period": "FY",
    "period_length": 10,
    "timeframe": "1day",
    "interval": "5min",
    "limit": 5,
    "page": 0,
    "sector": "Technology",
    "industry": "Software",
    "sic_code": "3571",
    "sicCode": "3571",
    "part": 0,
    "part_number": 0,
    "senate_id": "P000197",
}


def first_closed_sample(annotation: Any) -> Any | None:
    """First member of a ``Literal`` or ``Enum`` annotation, if any."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return None
    origin = get_origin(annotation)
    if origin is Literal:
        args = get_args(annotation)
        return args[0] if args else None
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return next(iter(annotation)).value
    if origin in {Union, UnionType}:
        for arg in get_args(annotation):
            if arg is type(None) or arg is str:
                continue
            value = first_closed_sample(arg)
            if value is not None:
                return value
    return None


def sample_for(
    param_name: str,
    group: str,
    method: str,
    annotation: Any = None,
) -> Any | None:
    """A representative value for ``param_name``, or ``None`` if unknown."""
    closed = first_closed_sample(annotation)
    if closed is not None:
        return closed
    if param_name == "symbol":
        return _inferred_symbol(group, method)
    if param_name == "name":
        return _inferred_name(method)
    if param_name == "query":
        return _inferred_query(method)
    return _FIXED_SAMPLES.get(param_name)


# Optional params we still fill: dates (VCR stability) and limit (smaller bodies).
_ALWAYS_FILL = frozenset(
    {
        "from_date",
        "to_date",
        "start_date",
        "end_date",
        "date",
        "holdings_date",
        "report_date",
        "target_date",
        "trade_date",
        "limit",
    }
)

# Pin path/query values that already exist in recorded cassettes. Do not
# put ``interval`` in ``_ALWAYS_FILL``: technical methods treat it as an
# override of ``timeframe`` and would stop matching their 1day cassettes.
_METHOD_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {
    ("company", "get_intraday_prices"): {"interval": "5min"},
    ("intelligence", "get_senate_trades_by_id"): {"senate_id": "W000802"},
}

# Public methods that never perform HTTP. Calling them under VCR in replay
# mode fails with "missing cassette".
NO_HTTP_METHODS: frozenset[tuple[str, str]] = frozenset(
    {
        ("company", "get_company_logo_url"),
    }
)


def build_kwargs(case: SweepCase) -> dict[str, Any]:
    """Keyword arguments for ``case``.

    Required parameters are always filled. Optional date parameters are
    filled with anchored values so VCR query strings stay stable. Other
    optional parameters keep the method default -- overriding ``period``
    with a global sample is how we used to send ``annual`` to endpoints
    that only accept ``FY``.
    """
    try:
        hints = get_type_hints(case.func)
    except Exception:
        hints = {}
    kwargs: dict[str, Any] = {}
    for name, param in bindable_params(case.func).items():
        required = param.default is inspect.Parameter.empty
        if not required and name not in _ALWAYS_FILL:
            continue
        value = sample_for(
            name, case.group, case.method, hints.get(name, param.annotation)
        )
        if value is not None:
            kwargs[name] = value
    kwargs.update(_ONE_OF_DEFAULTS.get((case.group, case.method), {}))
    kwargs.update(_METHOD_OVERRIDES.get((case.group, case.method), {}))
    return kwargs


def missing_required(case: SweepCase, kwargs: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for name, param in bindable_params(case.func).items():
        if param.default is inspect.Parameter.empty and name not in kwargs:
            missing.append(name)
    return missing


def _payload_size(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, tuple, set, bytes, str)):
        return len(value)
    historical = getattr(value, "historical", None)
    if isinstance(historical, list):
        return len(historical)
    return 1


def redact_text(text: str) -> str:
    """Strip live API keys from exception text before it hits a report."""
    scrubbed = text
    for key in (
        os.getenv("FMP_TEST_API_KEY", "").strip(),
        os.getenv("FMP_API_KEY", "").strip(),
    ):
        if key:
            scrubbed = scrubbed.replace(
                key, "DUMMY_API_KEY"
            )  # pragma: allowlist secret
    return re.sub(
        r"(?i)(apikey=)([^&\s\"']+)",
        r"\1DUMMY_API_KEY",  # pragma: allowlist secret
        scrubbed,
    )


def classify_result(value: Any, *, allow_empty: bool) -> str:
    if isinstance(value, BaseException):
        return "error"
    if _payload_size(value) == 0:
        return "ok" if allow_empty else "empty"
    return "ok"


def format_report(rows: Sequence[dict[str, Any]]) -> str:
    counts = Counter(str(row.get("status", "unknown")) for row in rows)
    header = (
        f"ok={counts.get('ok', 0)} empty={counts.get('empty', 0)} "
        f"error={counts.get('error', 0)} skip={counts.get('skip', 0)} "
        f"total={len(rows)}"
    )
    lines = [header]
    for row in rows:
        status = str(row.get("status", "unknown"))
        if status == "ok":
            continue
        group = row.get("group", "?")
        method = row.get("method", "?")
        detail = row.get("detail") or ""
        suffix = f"  {detail}" if detail else ""
        lines.append(f"{group}.{method}  {status}{suffix}")
    return "\n".join(lines)


def write_report(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"count": len(rows), "rows": list(rows)}
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def cassette_relpath(case: SweepCase) -> str:
    return f"{case.group}/{case.method}.yaml"


def _make_vcr(record_mode: str) -> Any:
    import vcr

    from tests.integration.conftest import (
        SafeFilesystemPersister,
        drop_unauthorized_response,
        scrub_api_key,
        scrub_response_secrets,
    )

    CASSETTE_ROOT.mkdir(parents=True, exist_ok=True)
    config = vcr.VCR(
        serializer="yaml",
        cassette_library_dir=str(CASSETTE_ROOT),
        record_mode=record_mode,
        match_on=["method", "host", "path", "query"],
        filter_headers=["authorization", "x-api-key", "apikey"],
        before_record_request=scrub_api_key,
        before_record_response=scrub_response_secrets,
        decode_compressed_response=True,
        filter_query_parameters=["apikey"],
        path_transformer=lambda path: str(CASSETTE_ROOT / path),
    )
    config.register_persister(SafeFilesystemPersister)
    config.before_playback_response = drop_unauthorized_response
    return config


def _call_with_retries(
    func: Callable[..., Any], kwargs: dict[str, Any], *, attempts: int = 5
) -> Any:
    wait = 1.0
    for attempt in range(attempts):
        try:
            return func(**kwargs)
        except RateLimitError as exc:
            if attempt == attempts - 1:
                raise
            delay = wait
            if exc.retry_after:
                delay = max(delay, float(exc.retry_after))
            time.sleep(delay)
            wait = min(wait * 2, 32.0)
    raise RuntimeError("unreachable")  # pragma: no cover


def run_cases(
    cases: Iterable[SweepCase],
    *,
    client: FMPDataClient,
    record_mode: str,
    throttle: float = 0.2,
) -> list[CaseRow]:
    """Execute ``cases`` under VCR. ``record_mode='none'`` never hits the API."""
    vcr_instance = _make_vcr(record_mode)
    rows: list[CaseRow] = []
    for case in cases:
        kwargs = build_kwargs(case)
        missing = missing_required(case, kwargs)
        if case.deprecated:
            rows.append(
                CaseRow(
                    group=case.group,
                    method=case.method,
                    status="skip",
                    detail="deprecated",
                    path=case.endpoint_path,
                    kwargs=kwargs,
                )
            )
            continue
        if missing:
            rows.append(
                CaseRow(
                    group=case.group,
                    method=case.method,
                    status="error",
                    detail=f"no sample for required params: {', '.join(missing)}",
                    path=case.endpoint_path,
                    kwargs=kwargs,
                )
            )
            continue

        cassette = cassette_relpath(case)
        method = getattr(getattr(client, case.group), case.method)
        local = (case.group, case.method) in NO_HTTP_METHODS
        if (
            not local
            and record_mode == "none"
            and not (CASSETTE_ROOT / cassette).is_file()
        ):
            rows.append(
                CaseRow(
                    group=case.group,
                    method=case.method,
                    status="error",
                    detail=f"missing cassette {cassette}",
                    path=case.endpoint_path,
                    kwargs=kwargs,
                )
            )
            continue

        started = time.perf_counter()
        try:
            if local:
                value = method(**kwargs)
            else:
                with vcr_instance.use_cassette(cassette):
                    value = _call_with_retries(method, kwargs)
        except Exception as exc:
            value = exc
        elapsed_ms = (time.perf_counter() - started) * 1000
        allow_empty = (case.group, case.method) in ALLOW_EMPTY
        status = classify_result(value, allow_empty=allow_empty)
        detail = ""
        if isinstance(value, BaseException):
            detail = redact_text(f"{type(value).__name__}: {value}")
        elif status == "empty":
            detail = "empty payload"
        else:
            detail = f"n={_payload_size(value)}"
        rows.append(
            CaseRow(
                group=case.group,
                method=case.method,
                status=status,
                detail=detail,
                path=case.endpoint_path,
                elapsed_ms=round(elapsed_ms, 1),
                kwargs=kwargs,
            )
        )
        if record_mode != "none":
            time.sleep(throttle)
    return rows
