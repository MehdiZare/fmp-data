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
import subprocess
import sys
from typing import Any
import warnings

from pydantic import BaseModel
import pytest

import fmp_data
from fmp_data.models import Endpoint
from fmp_data.schema import DeprecatedArgModel

# 116 argument models across the ``schema.py`` modules today: 106 ``*Args``
# plus 10 singular ``*Arg``. A floor, not an equality: the point is that the
# walk cannot stop yielding and let these assertions pass over an empty set.
_MIN_ARG_MODELS = 110

# 275 endpoints today across the ``endpoints.py`` modules. Same reason.
_MIN_ENDPOINTS = 250


def _walk(suffix: str) -> list[tuple[str, Any]]:
    """Import every ``fmp_data.*.<suffix>`` module that imports cleanly.

    ``BaseException``, not ``Exception``: a module whose extra is missing can
    fail on import with something outside the ``Exception`` hierarchy -- a
    bare ``SystemExit`` from a module-level guard is the usual shape -- which
    would otherwise take the whole scan down in CI, where no extras are
    installed. No module reached by this walk does that today (the filter
    only imports names ending ``.schema``/``.endpoints``, and
    ``walk_packages`` imports packages, whose ``__init__`` files are empty
    here), so this is a guard against a future one, not a live workaround.
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
    """Every ``*Arg``/``*Args`` model defined in a ``schema.py``, by name.

    Both suffixes, not just the plural: ``BaseSearchArg`` and
    ``BaseExchangeArg`` are public and deprecated but have no in-tree
    subclass, so a plural-only filter misses them entirely and a revert of
    either would leave this file green. The other singular roots are only
    covered transitively, through whichever ``*Args`` subclass they happen
    to have -- which is coverage by accident, not by design.
    """
    found: dict[str, type[BaseModel]] = {}
    for module_name, module in _walk("schema"):
        for attr, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj.__module__ == module_name
                and attr.endswith(("Arg", "Args"))
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


def test_every_arg_model_documents_the_deprecation() -> None:
    """Every model *says* it is deprecated, not just behaves so (#178).

    The runtime ``DeprecationWarning`` only reaches someone who runs the code.
    ``help(ETFHoldingsArgs)``, an IDE tooltip and the rendered docs all read
    ``__doc__``, and docstrings are not inherited for documentation purposes,
    so inheriting ``DeprecatedArgModel`` told a *reader* nothing -- and a
    reader is the one who can still avoid the migration.

    Companion to ``test_every_arg_model_is_marked_deprecated``: that one pins
    the behaviour, this one pins the documentation.
    """
    models = _arg_models()
    undocumented = sorted(
        name
        for name, model in models.items()
        if ".. deprecated:: 2.7" not in (model.__doc__ or "")
    )

    assert not undocumented, (
        "arg models whose docstring does not mention the deprecation:\n  "
        + "\n  ".join(undocumented)
    )
    assert len(models) >= _MIN_ARG_MODELS, (
        f"only found {len(models)} arg models, expected >= {_MIN_ARG_MODELS} "
        "-- did the schema walk stop yielding?"
    )


def test_the_injected_note_keeps_the_models_own_docstring() -> None:
    """The marker is appended, never substituted.

    An ``__init_subclass__`` that overwrote ``__doc__`` would trade one
    documentation gap for a worse one: the reader would learn the class is
    deprecated and lose what it was for.
    """
    from fmp_data.investment.schema import ETFHoldingsArgs

    doc = ETFHoldingsArgs.__doc__ or ""
    assert "ETF holdings" in doc, "the model's own summary was replaced"
    assert doc.index("ETF holdings") < doc.index(".. deprecated:: 2.7")
    assert "\n\n.. deprecated:: 2.7" in doc, "the directive must be its own block"
    assert "3.0" in doc


def test_a_root_that_documents_itself_is_left_alone() -> None:
    """The eight roots wrote their own marker; do not double it up."""
    from fmp_data.schema import BaseArgModel

    doc = BaseArgModel.__doc__ or ""
    assert doc.count(".. deprecated:: 2.7") == 1


def test_a_subclass_without_a_docstring_still_gets_one() -> None:
    """``__doc__ = None`` has nothing to append to, so a summary is invented."""

    class _UndocumentedArgs(DeprecatedArgModel):
        pass

    doc = _UndocumentedArgs.__doc__ or ""
    assert "_UndocumentedArgs" in doc
    assert ".. deprecated:: 2.7" in doc


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
    """A spot-check across distinct bases, one per inheritance shape.

    Not exhaustive over the roots: there are seven outside ``BaseArgModel``
    (``BaseListArgs``, ``BaseQuoteArgs``, ``BaseSearchArg``,
    ``BaseExchangeArg``, ``QuoteArgs``, ``MarketCapArgs``, ``BaseSymbolArg``)
    and these four cases cover three of them plus ``BaseArgModel`` itself.
    Exhaustiveness is ``test_every_arg_model_is_marked_deprecated``'s job --
    it walks all 116; this one pins that the warning actually fires on real
    construction with real kwargs.
    """
    model = getattr(importlib.import_module(module), name)

    with pytest.warns(DeprecationWarning) as record:
        model(**kwargs)

    message = str(record[0].message)
    assert name in message
    assert "3.0" in message


def test_generating_a_json_schema_warns() -> None:
    """Schema generation is a use, and it never validates anything.

    An "argument model" an external caller kept is most naturally handed to a
    tool/function-schema generator, which calls ``model_json_schema()`` and
    goes nowhere near ``model_validate``. Warning only from the validator
    would let exactly that caller reach 3.0 having never been told.
    """
    from fmp_data.technical.schema import TechnicalIndicatorArgs

    with pytest.warns(DeprecationWarning) as record:
        schema = TechnicalIndicatorArgs.model_json_schema()

    assert "TechnicalIndicatorArgs" in str(record[0].message)
    # The warning must not cost the caller the schema they asked for.
    assert schema["properties"], "model_json_schema returned an empty schema"


def test_importing_an_arg_model_stays_silent() -> None:
    """An import is not a use, and JSON-schema generation is lazy.

    Pins the other half of the contract above: ``__get_pydantic_json_schema__``
    must not fire at class-creation time. If pydantic ever started building
    JSON schemas eagerly, every ``import fmp_data`` would start warning and
    the deprecation would become noise users filter out wholesale.
    """
    code = (
        "import warnings\n"
        "warnings.simplefilter('error', DeprecationWarning)\n"
        "import fmp_data.technical.schema\n"
        "import fmp_data.market.schema\n"
        "import fmp_data.models\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, (
        "importing a schema module raised a DeprecationWarning:\n" + result.stderr
    )


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
