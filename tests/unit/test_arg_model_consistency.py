"""Every ``Args`` model must agree with the endpoint it describes.

#141's second concern: 31 arg-model classes have no consumer in the package,
so anything that rots in them rots silently. ``test_imports.py`` catches a
module that will not import; nothing caught a model whose *parameters* had
drifted from the endpoint's. That is the live gap, and it is not confined to
the three domains #141 names -- ``Endpoint.arg_model`` is read by nothing
anywhere, so all nine ``schema.py`` modules are equally unchecked.

#143 is one instance of the drift this catches: ``ETFHoldingsArgs.date`` was
required while ``ETF_HOLDINGS`` declares the parameter optional, so a caller
who satisfied the endpoint contract was rejected by the tool schema before a
request was ever built.

Three rules, in decreasing strictness:

1. **A model may not be stricter than its endpoint.** A field required where
   the endpoint's param is optional removes a capability the endpoint has.
   No baseline -- this is #143's defect and must stay at zero.
2. **A model must be able to satisfy its endpoint.** A field optional where
   the endpoint's param is mandatory is fine *only* when some default exists,
   on either side, so a value still reaches the wire. No baseline.
3. **Every field must name a real parameter.** Violations are frozen in
   ``_KNOWN_PARAM_DRIFT`` below: each is pre-existing rot that predates this
   guard and needs its own fix, so the set may not grow -- and may not go
   stale either, since a fixed entry must be deleted from it.

Pairing a model to an endpoint uses only declarations already in the repo:
``Endpoint.arg_model`` where it is set, plus ``_EXPLICIT_PAIRS`` for the three
domains that set it nowhere. Models with no single unambiguous endpoint (a
``fund_type`` selector spanning two endpoints, an abstract base, a model for
an endpoint that was deleted) are skipped and counted rather than guessed at.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from pydantic import BaseModel

import fmp_data
from fmp_data.models import Endpoint

# Hand-verified pairings for investment / institutional / intelligence, which
# declare `arg_model` on no endpoint at all. Each was checked against the
# endpoint's actual parameter list; anything ambiguous is deliberately absent
# and lands in the skipped count instead.
_EXPLICIT_PAIRS: dict[str, list[tuple[str, str]]] = {
    "investment": [
        ("ETFHoldingsArgs", "ETF_HOLDINGS"),
        ("ETFInfoArgs", "ETF_INFO"),
        ("MutualFundHoldingsArgs", "MUTUAL_FUND_HOLDINGS"),
        ("MutualFundSearchArgs", "MUTUAL_FUND_BY_NAME"),
    ],
    "institutional": [
        ("Form13FArgs", "FORM_13F"),
        ("Form13FDatesArgs", "FORM_13F_DATES"),
        ("AssetAllocationArgs", "ASSET_ALLOCATION"),
        ("InstitutionalHoldingsArgs", "INSTITUTIONAL_HOLDINGS"),
        ("InsiderTradesArgs", "INSIDER_TRADES"),
        ("InsiderRosterArgs", "INSIDER_ROSTER"),
        ("InsiderStatisticsArgs", "INSIDER_STATISTICS"),
        ("CIKMapperArgs", "CIK_MAPPER"),
        ("BeneficialOwnershipArgs", "BENEFICIAL_OWNERSHIP"),
        ("FailToDeliverArgs", "FAIL_TO_DELIVER"),
    ],
    # intelligence maps nothing on purpose. Its six models are either generic
    # shapes reused across many endpoints (CalendarArgs, NewsArgs suit a dozen
    # calendars and news feeds each) or name endpoints that live in another
    # domain entirely (AnalystEstimatesArgs, UpgradeDowngradeArgs belong to
    # `company`). Picking one would be inventing a mapping, not reading one.
    "intelligence": [],
}

# Model fields that name no parameter on their endpoint. Every entry is
# pre-existing drift, found when this guard was written -- none is introduced
# by it. The set is frozen: it may not grow, and an entry that gets fixed must
# be deleted from it, so it cannot quietly go stale.
_KNOWN_PARAM_DRIFT: dict[tuple[str, str], str] = {
    # `SEARCH_COMPANY` declares query/limit/exchange and no pagination at all.
    ("SearchArgs", "page"): "search-name takes no page parameter",
    # The technical endpoints declare from/to/periodLength/timeframe. The model
    # uses different names with no alias bridging them, so `periodLength` and
    # `timeframe` -- both *mandatory* -- have nothing to fill them, and the
    # model's own period/interval would never reach the wire. Applies to all 9
    # indicator endpoints sharing this model.
    ("TechnicalIndicatorArgs", "start_date"): "endpoint param is `from`",
    ("TechnicalIndicatorArgs", "end_date"): "endpoint param is `to`",
    ("TechnicalIndicatorArgs", "period"): "endpoint param is `periodLength`",
    ("TechnicalIndicatorArgs", "interval"): "endpoint param is `timeframe`",
    # FORM_13F takes cik/year/quarter; the model offers a single filing_date,
    # so it can express neither the year nor the quarter the endpoint requires.
    ("Form13FArgs", "filing_date"): "endpoint takes year+quarter, not a date",
    # ASSET_ALLOCATION's parameter is plain `date`.
    ("AssetAllocationArgs", "filing_date"): "endpoint param is `date`",
    # INSTITUTIONAL_HOLDINGS takes symbol/year/quarter; this flag matches none
    # of them and the model cannot supply the mandatory year or quarter.
    ("InstitutionalHoldingsArgs", "include_current_quarter"): "no such param",
    # FAIL_TO_DELIVER paginates with `page` only.
    ("FailToDeliverArgs", "limit"): "fail_to_deliver takes no limit",
}

# Models with no single unambiguous endpoint, skipped rather than guessed at.
# Reporting the count is the point: it may not grow, but enumerating 56 names
# would be noise. Most are in the *wired* domains -- a model that simply is
# not attached to anything (QuoteArgs, ProfileArgs), an abstract base
# (BaseListArgs), or a model for an endpoint that has since been deleted
# (CIKMapperByNameArgs, whose endpoint went in #130).
_MAX_UNMAPPED = 56

# 81 (endpoint, model) pairs today, covering 52 distinct models and 148
# fields. Floors stop the whole scan passing vacuously if the walk stops
# yielding.
_MIN_MODELS = 45
_MIN_FIELDS = 130


def _walk(suffix: str) -> list[tuple[str, object]]:
    """Import every ``fmp_data.*.<suffix>`` module that imports cleanly.

    ``BaseException``, not ``Exception``: ``fmp_data/mcp/__main__.py`` raises
    ``SystemExit`` without its extra, which is not an ``Exception`` and would
    otherwise take the whole scan down in CI, where no extras are installed.
    """
    modules: list[tuple[str, object]] = []
    for info in pkgutil.walk_packages(
        fmp_data.__path__, prefix="fmp_data.", onerror=lambda _name: None
    ):
        if not info.name.endswith(f".{suffix}"):
            continue
        try:
            modules.append((info.name, importlib.import_module(info.name)))
        except BaseException:  # noqa: S112 - see docstring
            # Nothing to log: a module absent because its extra is not
            # installed is the documented behaviour, and test_imports.py is
            # the guard that distinguishes that from a genuine break.
            continue
    return modules


def _declared_pairs() -> list[tuple[str, Endpoint, type[BaseModel]]]:
    """(label, endpoint, model) for every endpoint declaring an ``arg_model``."""
    pairs: list[tuple[str, Endpoint, type[BaseModel]]] = []
    for module_name, module in _walk("endpoints"):
        for attr, obj in vars(module).items():
            if isinstance(obj, Endpoint) and obj.arg_model is not None:
                pairs.append((f"{module_name}.{attr}", obj, obj.arg_model))
    return pairs


def _explicit_pairs() -> list[tuple[str, Endpoint, type[BaseModel]]]:
    """(label, endpoint, model) for the hand-verified unwired-domain pairs."""
    pairs: list[tuple[str, Endpoint, type[BaseModel]]] = []
    for domain, entries in _EXPLICIT_PAIRS.items():
        schema = importlib.import_module(f"fmp_data.{domain}.schema")
        endpoints = importlib.import_module(f"fmp_data.{domain}.endpoints")
        for model_name, endpoint_name in entries:
            endpoint = getattr(endpoints, endpoint_name)
            model = getattr(schema, model_name)
            pairs.append((f"{domain}.{endpoint_name}", endpoint, model))
    return pairs


def _all_arg_models() -> dict[str, str]:
    """Every ``*Args`` model defined in a ``schema.py``, mapped to its module."""
    found: dict[str, str] = {}
    for module_name, module in _walk("schema"):
        for attr, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj.__module__ == module_name
                and attr.endswith("Args")
            ):
                found[attr] = module_name
    return found


def _endpoint_default(endpoint: Endpoint, names: set[str]) -> object:
    """The endpoint-side default for the mandatory param matching ``names``."""
    for param in endpoint.mandatory_params:
        if param.name in names:
            return param.default
    return None


def test_arg_models_agree_with_their_endpoints() -> None:
    """Parameter names and required-ness must match the endpoint."""
    too_strict: list[str] = []
    cannot_satisfy: list[str] = []
    unknown: list[str] = []
    seen_drift: set[tuple[str, str]] = set()
    models_checked: set[str] = set()
    fields_checked = 0

    for label, endpoint, model in _declared_pairs() + _explicit_pairs():
        mandatory = {param.name for param in endpoint.mandatory_params}
        optional = {param.name for param in endpoint.optional_params or []}
        models_checked.add(model.__name__)

        for name, field in model.model_fields.items():
            fields_checked += 1
            names = {name, field.alias or name}
            key = (model.__name__, name)

            if not (names & mandatory or names & optional):
                if key in _KNOWN_PARAM_DRIFT:
                    seen_drift.add(key)
                else:
                    unknown.append(
                        f"{label}: {model.__name__}.{name} names no parameter "
                        f"of `{endpoint.name}`"
                    )
            elif names & optional and field.is_required():
                too_strict.append(
                    f"{label}: {model.__name__}.{name} is required but "
                    f"`{endpoint.name}` declares it optional"
                )
            elif names & mandatory and not field.is_required():
                # Optional in the model is fine as long as *some* default
                # fills the mandatory param -- the request still goes out
                # complete. Only a hole on both sides is a defect.
                if _endpoint_default(endpoint, names) is None and field.default is None:
                    cannot_satisfy.append(
                        f"{label}: {model.__name__}.{name} is optional with no "
                        f"default but `{endpoint.name}` requires it"
                    )

    # Rule 1 -- #143's defect. Never baselined.
    assert not too_strict, (
        "arg models stricter than their endpoints:\n  " + "\n  ".join(too_strict)
    )
    # Rule 2 -- a model that cannot produce a complete request.
    assert not cannot_satisfy, (
        "arg models that cannot satisfy their endpoints:\n  "
        + "\n  ".join(cannot_satisfy)
    )
    # Rule 3 -- new drift only; the frozen set is allowed through above.
    assert not unknown, (
        "arg-model fields naming no endpoint parameter:\n  "
        + "\n  ".join(unknown)
        + "\n\nFix the model, or -- if this is pre-existing rot being "
        "catalogued rather than introduced -- add it to _KNOWN_PARAM_DRIFT "
        "with the reason."
    )
    # ...and the frozen set may not go stale.
    stale = set(_KNOWN_PARAM_DRIFT) - seen_drift
    assert not stale, (
        f"_KNOWN_PARAM_DRIFT entries no longer drifting: {sorted(stale)}. "
        "They were fixed -- delete them so the baseline keeps shrinking."
    )

    assert len(models_checked) >= _MIN_MODELS, (
        f"only checked {len(models_checked)} arg models, expected "
        f">= {_MIN_MODELS} -- did the endpoint walk stop yielding?"
    )
    assert fields_checked >= _MIN_FIELDS, (
        f"only checked {fields_checked} fields, expected >= {_MIN_FIELDS}"
    )


def test_unmapped_arg_models_do_not_grow() -> None:
    """Models with no endpoint are skipped, but the skipped set may not grow.

    Skipping is honest -- inventing a mapping would be worse -- but an
    unbounded skip list would let a new orphan model hide in it forever.
    """
    mapped = {model.__name__ for _, _, model in _declared_pairs() + _explicit_pairs()}
    unmapped = sorted(name for name in _all_arg_models() if name not in mapped)

    assert len(unmapped) <= _MAX_UNMAPPED, (
        f"{len(unmapped)} arg models have no endpoint, up from "
        f"{_MAX_UNMAPPED}. New orphans:\n  " + "\n  ".join(unmapped) + "\n"
        "Pair the model with its endpoint, or raise _MAX_UNMAPPED with a "
        "reason if it genuinely describes no single endpoint."
    )
    # A floor too: if the schema walk breaks, `unmapped` empties and the
    # ceiling above passes for the wrong reason.
    assert len(_all_arg_models()) >= 100, "arg-model discovery found almost nothing"


def test_etf_holdings_date_is_optional_on_both_sides() -> None:
    """#143: ``date`` is optional for ETF holdings, and the model agrees.

    Probed against the live API on 2026-08-08: ``etf/holdings?symbol=SPY``
    returns 505 rows with *and* without ``date``, so the endpoint's optional
    declaration is correct and the arg model was the side that was wrong.
    """
    from fmp_data.investment.endpoints import ETF_HOLDINGS
    from fmp_data.investment.schema import ETFHoldingsArgs

    optional = {param.name for param in ETF_HOLDINGS.optional_params or []}
    assert "date" in optional
    assert not ETFHoldingsArgs.model_fields["date"].is_required()
    assert ETFHoldingsArgs(symbol="SPY").date is None


def test_mutual_fund_holdings_date_stays_required() -> None:
    """``MUTUAL_FUND_HOLDINGS`` declares ``date`` mandatory; the model agrees.

    Whether that declaration is *true* is unknowable while the path 404s for
    every request (probed 2026-08-08) -- that question is #152. This pins only
    the internal agreement between the two declarations, so a future fix to
    one is not silently made without the other.
    """
    from fmp_data.investment.endpoints import MUTUAL_FUND_HOLDINGS
    from fmp_data.investment.schema import MutualFundHoldingsArgs

    mandatory = {param.name for param in MUTUAL_FUND_HOLDINGS.mandatory_params}
    assert "date" in mandatory
    assert MutualFundHoldingsArgs.model_fields["date"].is_required()
