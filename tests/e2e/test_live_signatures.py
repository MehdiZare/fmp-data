"""Every endpoint declaration must match what the live API actually does.

Opt-in: skipped unless ``FMP_TEST_API_KEY`` (or ``FMP_API_KEY``) is set, so the
default CI matrix -- which installs no extras and has no key -- is unaffected.
Run it before a release, or on a schedule:

    FMP_TEST_API_KEY=... pytest tests/e2e/ -v

Why this exists: a one-off probe of all 275 declarations found 28 paths that
return 404 for every request, a parameter declared under the wrong name, three
endpoints whose ``from``/``to`` are mandatory despite being declared optional,
and two whose ``symbol`` was modelled as a path segment when the API wants a
query parameter. None of that was visible to the unit suite, which never calls
the API, and VCR cassettes are gitignored so a clean checkout cannot replay
them either. The only way to catch this class is to ask the API.

Each test reports every mismatch it finds rather than stopping at the first, so
one run gives the whole picture.
"""

from __future__ import annotations

import importlib
import json
import os
import pkgutil
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

import pytest

import fmp_data
from fmp_data.models import Endpoint, ParamLocation

API_KEY = os.getenv("FMP_TEST_API_KEY") or os.getenv("FMP_API_KEY")

pytestmark = pytest.mark.skipif(
    not API_KEY,
    reason="live API test: set FMP_TEST_API_KEY to run",
)

BASE = "https://financialmodelingprep.com"

#: Seconds between calls. The suite makes a few hundred requests; this keeps it
#: well inside a normal plan's rate limit without making the run painful.
THROTTLE = 0.12

#: Representative values per parameter name, chosen to be live and liquid so an
#: empty response means the declaration is wrong rather than the sample.
SAMPLES: dict[str, str] = {
    "symbol": "AAPL",
    "symbols": "AAPL,MSFT",
    "cik": "0001067983",
    "exchange": "NASDAQ",
    "sector": "Technology",
    "industry": "Software",
    "query": "Apple",
    "name": "Apple",
    "company": "Apple",
    "date": "2024-09-30",
    "from": "2024-01-01",
    "to": "2024-06-30",
    "year": "2024",
    "quarter": "3",
    "period": "annual",
    "limit": "5",
    "page": "0",
    "interval": "5min",
    "timeframe": "5min",
    "periodLength": "10",
    "formType": "10-K",
    "sicCode": "3571",
}

#: Endpoints whose emptiness depends on the entity, not the declaration --
#: e.g. an ETF-holdings call with a non-ETF symbol legitimately returns [].
#: These are exempt from the "answers with data" assertion but NOT from the
#: 404 assertion, which is the one that catches a dead path.
ENTITY_SENSITIVE = {
    "ETF_HOLDINGS",
    "ETF_INFO",
    "ETF_SECTOR_WEIGHTINGS",
    "ETF_COUNTRY_WEIGHTINGS",
    "MUTUAL_FUND_DATES",
    "FUNDS_DISCLOSURE",
    "FUNDS_DISCLOSURE_HOLDERS_SEARCH",
    "FORM_13F",
    "FORM_13F_DATES",
    "INSTITUTIONAL_OWNERSHIP_EXTRACT",
    "INSTITUTIONAL_OWNERSHIP_DATES",
    "HOLDER_PERFORMANCE_SUMMARY",
    "HOLDER_INDUSTRY_BREAKDOWN",
    "SENATE_TRADES_BY_NAME",
    "HOUSE_TRADES_BY_NAME",
    "CROWDFUNDING_SEARCH",
    "CROWDFUNDING_BY_CIK",
    "EQUITY_OFFERING_BY_CIK",
    "COMMITMENT_OF_TRADERS_REPORT",
    "COMMITMENT_OF_TRADERS_ANALYSIS",
    "HISTORICAL_INDUSTRY_PERFORMANCE",
    "HISTORICAL_INDUSTRY_PE",
    "SEARCH_SYMBOL",
}

#: Clients whose endpoints answer with CSV rather than JSON. Their bodies are
#: not parsed; only the HTTP status is asserted.
CSV_CLIENTS = {"batch"}

#: Endpoints requiring *at least one of* several individually-optional params.
#:
#: ``mandatory_params``/``optional_params`` cannot express "one of these
#: three", so every param is correctly declared optional and a request with
#: none of them correctly 400s. That is the API's contract, not a declaration
#: bug, so ``test_optional_params_are_really_optional`` skips them. The
#: constraint is enforced in the client method instead -- see
#: ``SECClient.search_industry_classification``.
ONE_OF_ENDPOINTS = {"INDUSTRY_CLASSIFICATION_SEARCH"}


def _sample(param: Any) -> str:
    """A live value for ``param`` that ``validate_params`` will accept.

    ``valid_values`` wins over :data:`SAMPLES` because it is a hard
    constraint: ``period`` is sampled as ``"annual"``, but the endpoints that
    restrict it accept only ``Q1..Q4``/``FY``, and validation rejects the
    sample before any request is made.

    The lookup is by *wire* name -- ``param.alias or param.name`` -- because
    that is the key the API sees. ``CIK_SEARCH`` declares ``query`` with
    ``alias="cik"``; sampled by declared name it gets ``"Apple"`` and the API
    answers 400, which looks like a declaration bug but is a sampling bug.
    """
    valid = getattr(param, "valid_values", None)
    if valid:
        first = next(iter(valid))
        return str(getattr(first, "value", first))
    wire_name = getattr(param, "alias", None) or param.name
    if wire_name in SAMPLES:
        return SAMPLES[wire_name]
    if param.name in SAMPLES:
        return SAMPLES[param.name]
    return {
        "integer": "1",
        "float": "1",
        "boolean": "false",
        "date": "2024-06-30",
        "datetime": "2024-06-30",
    }.get(param.param_type.value, "AAPL")


def _fetch(url: str, parse: bool = True) -> tuple[Any, Any]:
    """Return (status, row_count_or_detail). Never raises for HTTP errors."""
    time.sleep(THROTTLE)
    try:
        # S310: the scheme is not attacker-controlled -- every URL is built
        # from BASE, a literal https:// constant, plus a declaration from this
        # repo. There is no user input in the path.
        with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
            raw = resp.read()
            if not parse:
                return resp.status, len(raw)
            body = json.loads(raw)
            return resp.status, len(body) if isinstance(body, list) else 1
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")[:120]
    except Exception as exc:
        return type(exc).__name__, str(exc)[:100]


def _call(endpoint: Endpoint, params: dict[str, str], parse: bool = True) -> Any:
    """Probe ``endpoint`` through the library's own request-building code.

    Building the URL by hand here would test a reimplementation rather than
    the library, and would mis-report three ways the declaration can differ
    from the naive form:

    * ``build_url`` substitutes ``{placeholder}``s, so a hand-built URL keeps
      a literal ``{interval}`` and 404s on every templated endpoint;
    * ``get_query_params`` sends ``param.alias or param.name``, so an aliased
      param -- ``CIK_SEARCH``'s ``query``, which goes out as ``cik`` -- is
      probed under the wrong key and 400s;
    * ``validate_params`` applies the ``ParamType`` conversion, so a CIK is
      zero-padded exactly as a real call would pad it.

    Using the real path means a failure here is a real failure for callers.
    """
    validated = endpoint.validate_params(dict(params))
    url = endpoint.build_url(BASE, validated)
    query = endpoint.get_query_params(validated)
    query["apikey"] = API_KEY or ""
    return _fetch(f"{url}?{urllib.parse.urlencode(query)}", parse=parse)


def _all_endpoints() -> list[tuple[str, str, Endpoint]]:
    found: list[tuple[str, str, Endpoint]] = []
    for info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not info.name.endswith(".endpoints"):
            continue
        try:
            module = importlib.import_module(info.name)
        except BaseException:  # noqa: S112
            # SystemExit from fmp_data/mcp/__main__.py without its extra.
            continue
        client = info.name.split(".")[1]
        for attr, value in vars(module).items():
            if isinstance(value, Endpoint):
                found.append((client, attr, value))
    return found


ENDPOINTS = _all_endpoints() if API_KEY else []


def _endpoint_map(mapping_module: Any) -> dict[str, Endpoint]:
    """Merge every ``*_ENDPOINT_MAP`` in a mapping module: method -> endpoint."""
    merged: dict[str, Endpoint] = {}
    for attr, value in vars(mapping_module).items():
        if attr.endswith("_ENDPOINT_MAP") and isinstance(value, dict):
            merged.update(value)
    return merged


def _deprecated_method_names(client_module: Any) -> set[str]:
    """Method names on a client module's classes carrying the deprecation mark."""
    marked: set[str] = set()
    for cls in vars(client_module).values():
        if not isinstance(cls, type):
            continue
        for method_name, method in vars(cls).items():
            if getattr(method, "__fmp_deprecated__", False):
                marked.add(method_name)
    return marked


def _deprecated_endpoints() -> set[str]:
    """Endpoint attribute names whose client method is deprecated or removed.

    A path FMP has withdrawn still 404s after we deprecate it -- deprecating
    is the acknowledgement that it is dead, not a repair. Probing it would
    make this suite fail forever for endpoints that are already handled, so
    the 404 assertion skips them.

    The set is derived, not hand-written: ``@deprecated`` and ``@removed``
    stamp ``__fmp_deprecated__`` on the wrapper, and each module's
    ``*_ENDPOINT_MAP`` maps a method name to its endpoint. A method that
    stops being deprecated therefore rejoins the assertion automatically,
    and a list here cannot silently rot.
    """
    # Orphans: an endpoint reachable from no client method has no decorator to
    # carry the marker, so its description is the only place the deprecation
    # can live. COMPANY_OUTLOOK is declared but wired to nothing.
    deprecated = {
        attr
        for _client, attr, endpoint in ENDPOINTS
        if (endpoint.description or "").lstrip().upper().startswith("DEPRECATED")
    }
    name_by_endpoint = {id(endpoint): attr for _c, attr, endpoint in ENDPOINTS}

    for info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not info.name.endswith(".mapping"):
            continue
        group = info.name.split(".")[1]
        try:
            endpoint_map = _endpoint_map(importlib.import_module(info.name))
            marked = set()
            for client_mod in ("client", "async_client"):
                marked |= _deprecated_method_names(
                    importlib.import_module(f"fmp_data.{group}.{client_mod}")
                )
        except BaseException:  # noqa: S112
            # SystemExit/ImportError from a module whose extra is absent, as
            # in _all_endpoints above. A group we cannot import contributes
            # nothing rather than aborting the sweep.
            continue

        for method_name in marked:
            endpoint = endpoint_map.get(method_name)
            attr_name = name_by_endpoint.get(id(endpoint)) if endpoint else None
            if attr_name:
                deprecated.add(attr_name)

    return deprecated


DEPRECATED_ENDPOINTS = _deprecated_endpoints() if API_KEY else set()


def test_no_endpoint_path_returns_404() -> None:
    """A declared path that 404s is broken for every caller of that method.

    This is the assertion that would have caught all 28 dead paths, and the
    two whose ``symbol`` was modelled as a path segment.
    """
    dead: list[str] = []
    for client, name, endpoint in ENDPOINTS:
        if name in DEPRECATED_ENDPOINTS:
            continue
        version = getattr(endpoint.version, "value", "stable")
        params = {p.name: _sample(p) for p in endpoint.mandatory_params}
        status, _detail = _call(endpoint, params, parse=client not in CSV_CLIENTS)
        if status == 404:
            dead.append(f"{client}.{name}  {version}/{endpoint.path}")

    assert not dead, (
        f"{len(dead)} endpoint path(s) return 404 -- these are broken for "
        "every caller, sync, async, LangChain and MCP alike:\n  " + "\n  ".join(dead)
    )


def test_deprecated_endpoints_are_really_dead() -> None:
    """The exemption above must stay earned, in both directions.

    Skipping deprecated endpoints in the 404 sweep is only honest while they
    really are dead. Without this, the exemption becomes a place for a mistake
    to hide: deprecate something prematurely, or have FMP quietly revive a
    path, and the suite goes quiet either way.

    So the three states are asserted separately. Dead-and-deprecated passes
    here. Dead-and-not-deprecated fails the test above. Alive-and-deprecated
    fails *this* one -- and that is worth knowing, because it means the
    library is telling users to migrate off an endpoint that still works.
    """
    alive: list[str] = []
    for client, name, endpoint in ENDPOINTS:
        if name not in DEPRECATED_ENDPOINTS:
            continue
        version = getattr(endpoint.version, "value", "stable")
        params = {p.name: _sample(p) for p in endpoint.mandatory_params}
        status, detail = _call(endpoint, params, parse=client not in CSV_CLIENTS)
        if status == 200 and isinstance(detail, int) and detail > 0:
            alive.append(f"{client}.{name}  {version}/{endpoint.path} -> {detail} rows")

    assert not alive, (
        "endpoints marked deprecated that the API still answers with data. "
        "Either FMP revived the path and the deprecation should be lifted, or "
        "it was deprecated on bad evidence -- either way the docstring is "
        "telling users to migrate away from something that works:\n  "
        + "\n  ".join(alive)
    )


def test_mandatory_params_are_really_mandatory() -> None:
    """Omitting a declared-mandatory param must not silently succeed.

    A param we force callers to supply, which the API does not need, is a
    declaration that over-constrains the client for no reason.
    """
    not_required: list[str] = []
    for client, name, endpoint in ENDPOINTS:
        if name in DEPRECATED_ENDPOINTS:
            continue
        if len(endpoint.mandatory_params) != 1:
            # With several mandatory params, omitting one leaves the request
            # ambiguous; single-param endpoints give a clean signal.
            continue
        if endpoint.mandatory_params[0].location is ParamLocation.PATH:
            # The param IS the URL. Omitting it does not make a weaker
            # request, it makes a different one, so the answer says nothing
            # about whether the API requires it.
            continue
        # Deliberately incomplete, so validate_params would refuse to build
        # it -- the point of this probe is to send what the library never
        # would. Only a query-param endpoint reaches here, so the path is
        # already literal and needs no substitution.
        version = getattr(endpoint.version, "value", "stable")
        status, detail = _fetch(
            f"{BASE}/{version}/{endpoint.path}?"
            + urllib.parse.urlencode({"apikey": API_KEY or ""}),
            parse=client not in CSV_CLIENTS,
        )
        if status == 200 and isinstance(detail, int) and detail > 0:
            param = endpoint.mandatory_params[0].name
            not_required.append(
                f"{client}.{name}: omitting mandatory '{param}' still "
                f"returned {detail} rows"
            )

    assert not not_required, (
        "parameters declared mandatory that the API does not require:\n  "
        + "\n  ".join(not_required)
    )


def test_optional_params_are_really_optional() -> None:
    """Omitting every declared-optional param must still work.

    This is the assertion that catches the inverse of the above: the three SEC
    search endpoints whose ``from``/``to`` are declared optional but which the
    API rejects with 400 when they are absent.
    """
    wrongly_optional: list[str] = []
    for client, name, endpoint in ENDPOINTS:
        if name in DEPRECATED_ENDPOINTS or name in ONE_OF_ENDPOINTS:
            continue
        if not endpoint.optional_params:
            continue
        params = {p.name: _sample(p) for p in endpoint.mandatory_params}
        status, detail = _call(endpoint, params, parse=client not in CSV_CLIENTS)
        if status == 400:
            wrongly_optional.append(
                f"{client}.{name}: 400 with only mandatory params -- {str(detail)[:90]}"
            )

    assert not wrongly_optional, (
        "endpoints rejecting a request that supplies every mandatory param, "
        "so something declared optional is actually required:\n  "
        + "\n  ".join(wrongly_optional)
    )


def test_declared_path_templates_are_substitutable() -> None:
    """A ``{placeholder}`` in a path must correspond to a declared param.

    ``historical-chart/{interval}/{symbol}`` modelled ``symbol`` as a path
    segment when the API wants it as a query parameter, so the request 404'd
    for every caller.
    """
    import re

    unsatisfiable: list[str] = []
    for client, name, endpoint in ENDPOINTS:
        placeholders = set(re.findall(r"\{(\w+)\}", endpoint.path))
        if not placeholders:
            continue
        declared = {p.name for p in endpoint.mandatory_params} | {
            p.name for p in (endpoint.optional_params or [])
        }
        missing = placeholders - declared
        if missing:
            unsatisfiable.append(
                f"{client}.{name}: path {endpoint.path} needs "
                f"{sorted(missing)}, which no parameter supplies"
            )

    assert not unsatisfiable, (
        "path templates that cannot be filled from declared params:\n  "
        + "\n  ".join(unsatisfiable)
    )


def test_the_probe_actually_ran() -> None:
    """Floor: an empty endpoint list would make every test above vacuous."""
    assert len(ENDPOINTS) > 200, (
        f"only {len(ENDPOINTS)} endpoints discovered; the walk is not finding "
        "the package and the assertions above would pass having tested nothing"
    )
