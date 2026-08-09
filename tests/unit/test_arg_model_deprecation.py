"""The hand-written argument-model layer is deprecated in 2.7, gone in 3.0.

#153: ``Endpoint.arg_model`` was declared once, assigned ~68 times across six
domains, and read by nothing. LangChain argument schemas are built
*dynamically* in ``fmp_data/lc/vector_store.py`` from each endpoint's
``mandatory_params``/``optional_params`` plus its ``parameter_hints`` -- that
is the only path a tool schema has ever taken. So the 106 ``*Args`` models in
the nine ``schema.py`` modules never reached a tool, whether or not their
endpoint assigned ``arg_model``.

#167 is what that bought: the models drifted freely because nothing could
observe them. ``TechnicalIndicatorArgs``, shared by all nine indicator
endpoints, has *zero* parameter-name overlap with its endpoint, and two of the
endpoint's mandatory parameters have nothing in the model that could fill
them. Five more models carry the same class of defect.

What this file guards, until 3.0 removes the layer outright:

1. The inert wiring is gone -- no endpoint in the package sets ``arg_model``.
2. The field survives for external callers, but saying so warns.
3. Every ``*Args`` model still imports, and using one warns.
4. The two endpoint-side facts pinned by #143/#152, kept from the deleted
   ``test_arg_model_consistency.py`` because they are about the *endpoint*
   declarations and outlive the models.
5. A breadcrumb so 3.0 cannot ship with the cycle still open.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
import pkgutil
import re
from typing import Any
import warnings

from pydantic import BaseModel
import pytest

import fmp_data
from fmp_data.models import Endpoint
from fmp_data.schema import DeprecatedArgModel

# 106 ``*Args`` models across the nine ``schema.py`` modules today. A floor,
# not an equality: the point is that the walk cannot stop yielding and let
# these assertions pass over an empty set.
_MIN_ARG_MODELS = 100

# 275 endpoints today across the ``endpoints.py`` modules. Same reason.
_MIN_ENDPOINTS = 250


def _walk(suffix: str) -> list[tuple[str, Any]]:
    """Import every ``fmp_data.*.<suffix>`` module that imports cleanly.

    ``BaseException``, not ``Exception``: ``fmp_data/mcp/__main__.py`` raises
    ``SystemExit`` without its extra, which is not an ``Exception`` and would
    otherwise take the whole scan down in CI, where no extras are installed.
    """
    modules: list[tuple[str, Any]] = []
    for info in pkgutil.walk_packages(
        fmp_data.__path__, prefix="fmp_data.", onerror=lambda _name: None
    ):
        if not info.name.endswith(f".{suffix}"):
            continue
        try:
            modules.append((info.name, importlib.import_module(info.name)))
        except BaseException:  # noqa: S112 - see docstring
            # A module absent because its extra is not installed is documented
            # behaviour; test_imports.py distinguishes that from a real break.
            continue
    return modules


def _arg_models() -> dict[str, type[BaseModel]]:
    """Every ``*Args`` model defined in a ``schema.py``, by qualified name."""
    found: dict[str, type[BaseModel]] = {}
    for module_name, module in _walk("schema"):
        for attr, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj.__module__ == module_name
                and attr.endswith("Args")
            ):
                found[f"{module_name}.{attr}"] = obj
    return found


def test_no_endpoint_declares_an_arg_model() -> None:
    """The inert wiring is gone from every domain (#153).

    Assigning it read as a contract -- ``arg_model=ETFHoldingsArgs`` looks
    like the model validates that endpoint's arguments. It never did.
    """
    wired: list[str] = []
    endpoints_seen = 0

    for module_name, module in _walk("endpoints"):
        for attr, obj in vars(module).items():
            if not isinstance(obj, Endpoint):
                continue
            endpoints_seen += 1
            if obj.arg_model is not None:
                wired.append(f"{module_name}.{attr} -> {obj.arg_model.__name__}")

    assert not wired, (
        "endpoints still declaring the dead arg_model wiring:\n  "
        + "\n  ".join(wired)
        + "\n\nNothing reads it. Delete the assignment."
    )
    assert endpoints_seen >= _MIN_ENDPOINTS, (
        f"only walked {endpoints_seen} endpoints, expected "
        f">= {_MIN_ENDPOINTS} -- did the endpoint walk stop yielding?"
    )


def test_setting_arg_model_warns() -> None:
    """The field stays for external callers, but using it says so."""
    from fmp_data.models import APIVersion, CompanySymbol

    with pytest.warns(DeprecationWarning) as record:
        Endpoint(
            name="probe",
            path="probe",
            version=APIVersion.STABLE,
            description="probe",
            mandatory_params=[],
            optional_params=None,
            response_model=CompanySymbol,
            arg_model=DeprecatedArgModel,
        )

    message = str(record[0].message)
    assert "arg_model" in message
    assert "3.0" in message


def test_omitting_arg_model_does_not_warn() -> None:
    """The default path -- and an explicit ``None`` -- stay silent."""
    from fmp_data.models import APIVersion, CompanySymbol

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        for extra in ({}, {"arg_model": None}):
            Endpoint(
                name="probe",
                path="probe",
                version=APIVersion.STABLE,
                description="probe",
                mandatory_params=[],
                optional_params=None,
                response_model=CompanySymbol,
                **extra,
            )


def test_every_arg_model_is_marked_deprecated() -> None:
    """All 106 models route through ``DeprecatedArgModel``.

    Importing one is still silent -- a bare import is not use -- so the
    deprecation has to attach to the class, not to the module.
    """
    models = _arg_models()
    unmarked = sorted(
        name
        for name, model in models.items()
        if not issubclass(model, DeprecatedArgModel)
    )

    assert not unmarked, "arg models outside the deprecation cycle:\n  " + "\n  ".join(
        unmarked
    )
    assert len(models) >= _MIN_ARG_MODELS, (
        f"only found {len(models)} arg models, expected >= {_MIN_ARG_MODELS} "
        "-- did the schema walk stop yielding?"
    )


@pytest.mark.parametrize(
    ("module", "name", "kwargs"),
    [
        ("fmp_data.technical.schema", "TechnicalIndicatorArgs", {"symbol": "AAPL"}),
        ("fmp_data.market.schema", "QuoteArgs", {"symbol": "AAPL"}),
        ("fmp_data.alternative.schema", "CryptoListArgs", {}),
        ("fmp_data.company.schema", "CoreInformationArgs", {"symbol": "AAPL"}),
    ],
)
def test_using_an_arg_model_warns(
    module: str, name: str, kwargs: dict[str, Any]
) -> None:
    """One per distinct base, including the four roots outside ``BaseArgModel``."""
    model = getattr(importlib.import_module(module), name)

    with pytest.warns(DeprecationWarning) as record:
        model(**kwargs)

    message = str(record[0].message)
    assert name in message
    assert "3.0" in message


def test_arg_models_still_import() -> None:
    """Deprecated, not gone: 2.7 must not break a downstream import."""
    from fmp_data.institutional.schema import Form13FArgs  # noqa: F401
    from fmp_data.intelligence.schema import NewsArgs  # noqa: F401
    from fmp_data.investment.schema import ETFHoldingsArgs  # noqa: F401
    from fmp_data.models import BaseSymbolArg  # noqa: F401
    from fmp_data.schema import BaseArgModel  # noqa: F401
    from fmp_data.technical.schema import TechnicalIndicatorArgs  # noqa: F401


def test_etf_holdings_date_is_optional_on_the_endpoint() -> None:
    """#143, endpoint side -- kept from ``test_arg_model_consistency.py``.

    Probed against the live API on 2026-08-08: ``etf/holdings?symbol=SPY``
    returns 505 rows with *and* without ``date``, so the endpoint's optional
    declaration is the correct one. This half survives the arg models.
    """
    from fmp_data.investment.endpoints import ETF_HOLDINGS
    from fmp_data.investment.schema import ETFHoldingsArgs

    optional = {param.name for param in ETF_HOLDINGS.optional_params or []}
    assert "date" in optional
    assert not ETFHoldingsArgs.model_fields["date"].is_required()


def test_mutual_fund_holdings_date_stays_required() -> None:
    """``MUTUAL_FUND_HOLDINGS`` declares ``date`` mandatory (#152).

    Whether that declaration is *true* is unknowable while the path 404s for
    every request (probed 2026-08-08). This pins only the declaration, so a
    future fix does not move it by accident.
    """
    from fmp_data.investment.endpoints import MUTUAL_FUND_HOLDINGS

    mandatory = {param.name for param in MUTUAL_FUND_HOLDINGS.mandatory_params}
    assert "date" in mandatory


def test_three_zero_must_not_ship_with_the_cycle_open() -> None:
    """Breadcrumb: 3.0 removes the layer, and this is what trips.

    ``fmp_data.__version__`` is hatch-vcs derived and resolves to the
    ``"0.0.0"`` fallback whenever the suite imports the source tree rather
    than a built wheel -- which is what happens in this repo -- so it is
    checked only when it carries a real value. The CHANGELOG is the signal
    that actually moves in-tree: cutting 3.0 adds a released ``## [3.x.y]``
    heading, and that is what trips this test.

    On failure: delete ``Endpoint.arg_model`` and its ``_warn_deprecated_arg_model``
    validator, ``fmp_data.models.BaseSymbolArg``, the nine ``fmp_data/*/schema.py``
    modules apart from the enums still imported at runtime
    (``EconomicIndicatorType``, ``IntradayTimeInterval``), the arg-model half of
    ``fmp_data/schema.py`` including ``DeprecatedArgModel``, and this file.
    """
    from fmp_data import __version__

    reminder = (
        "3.0: drop Endpoint.arg_model, DeprecatedArgModel, BaseSymbolArg and "
        "the nine schema.py arg-model modules (keep the runtime enums)"
    )

    if __version__ != "0.0.0":
        assert int(__version__.split(".")[0]) < 3, reminder

    changelog = (Path(__file__).resolve().parents[2] / "CHANGELOG.md").read_text()
    released_majors = {
        int(match) for match in re.findall(r"^## \[(\d+)\.", changelog, re.M)
    }

    assert not any(major >= 3 for major in released_majors), reminder
