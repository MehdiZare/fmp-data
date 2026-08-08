"""Arg models may not be stricter than the endpoint they describe.

#143: ``ETF_HOLDINGS`` declares ``date`` optional while ``ETFHoldingsArgs``
declared it required. A caller who satisfies the endpoint contract is then
rejected by the tool schema before the request is ever built -- the arg model
silently removes a capability the endpoint has.

Only that direction is a defect. The reverse -- an arg-model field that is
optional where the endpoint param is mandatory -- cannot under-supply the
request: a pydantic field is optional exactly when it has a default, so the
model always yields a value (``LatestFinancialStatementsArgs.page`` defaults to
``0`` against a mandatory ``page``, and that is fine).

The scan is keyed on ``Endpoint.arg_model``, so any endpoint that gains one
later is covered automatically. ``fmp_data.investment.schema`` is checked
explicitly as well, because nothing attaches those models to their endpoints
yet (#141) and #143's fix lives in exactly that module.
"""

from __future__ import annotations

import importlib
import pkgutil

from pydantic import BaseModel
import pytest

import fmp_data
from fmp_data.investment.endpoints import ETF_HOLDINGS, MUTUAL_FUND_HOLDINGS
from fmp_data.investment.schema import ETFHoldingsArgs, MutualFundHoldingsArgs
from fmp_data.models import Endpoint

# 125 (endpoint, field) pairs carry an arg model today. A floor stops the walk
# silently finding nothing and reporting success.
_MIN_FIELDS = 100


def _endpoints_with_arg_models() -> list[tuple[str, Endpoint]]:
    """Every ``Endpoint`` in the package that declares an ``arg_model``."""
    found: list[tuple[str, Endpoint]] = []
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".endpoints"):
            continue
        module = importlib.import_module(module_info.name)
        for attr_name, obj in vars(module).items():
            if isinstance(obj, Endpoint) and obj.arg_model is not None:
                found.append((f"{module_info.name}.{attr_name}", obj))
    return found


def _over_strict_fields(endpoint: Endpoint, arg_model: type[BaseModel]) -> list[str]:
    """Arg-model fields required where the endpoint's param is optional."""
    optional = {param.name for param in endpoint.optional_params or []}
    return [
        f"{arg_model.__name__}.{name}"
        for name, field in arg_model.model_fields.items()
        if name in optional and field.is_required()
    ]


def test_arg_models_are_not_stricter_than_their_endpoints() -> None:
    """No arg model may require a parameter its endpoint declares optional."""
    offenders: list[str] = []
    fields_checked = 0

    for label, endpoint in _endpoints_with_arg_models():
        arg_model = endpoint.arg_model
        assert arg_model is not None  # narrowed by _endpoints_with_arg_models
        fields_checked += len(arg_model.model_fields)
        offenders += [
            f"{label}: {field} is required but the endpoint declares it optional"
            for field in _over_strict_fields(endpoint, arg_model)
        ]

    assert not offenders, "arg models stricter than their endpoints:\n  " + "\n  ".join(
        offenders
    )
    assert fields_checked >= _MIN_FIELDS, (
        f"only checked {fields_checked} arg-model fields, expected "
        f">= {_MIN_FIELDS} -- did endpoints stop carrying arg models?"
    )


@pytest.mark.parametrize(
    ("endpoint", "arg_model"),
    [
        pytest.param(ETF_HOLDINGS, ETFHoldingsArgs, id="etf_holdings"),
        pytest.param(
            MUTUAL_FUND_HOLDINGS, MutualFundHoldingsArgs, id="mutual_fund_holdings"
        ),
    ],
)
def test_holdings_arg_models_match_their_endpoints(
    endpoint: Endpoint, arg_model: type[BaseModel]
) -> None:
    """#143's pair, checked directly -- they are not wired via ``arg_model``."""
    assert not _over_strict_fields(endpoint, arg_model)


def test_etf_holdings_date_is_optional_on_both_sides() -> None:
    """``date`` is optional for ETF holdings, and the arg model agrees.

    Probed against the live API on 2026-08-08: ``etf/holdings?symbol=SPY``
    returns 505 rows with *and* without ``date``, so the endpoint's optional
    declaration is correct and the arg model was the side that was wrong.
    """
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
    mandatory = {param.name for param in MUTUAL_FUND_HOLDINGS.mandatory_params}
    assert "date" in mandatory
    assert MutualFundHoldingsArgs.model_fields["date"].is_required()
