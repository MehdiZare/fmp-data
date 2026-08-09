"""Guard tests: generated LangChain tool schemas must mirror endpoint arity.

``ToolFactory`` turns an endpoint's parameters into a pydantic model that the
LLM fills in. If an optional endpoint parameter lands in that model without a
default, pydantic marks it required and the LLM has to invent a value for
something the endpoint never wanted (#128).
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, create_model
import pytest

from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import get_endpoint_groups
from fmp_data.lc.vector_store import ToolFactory
from fmp_data.models import Endpoint

# Below the current catalog size but far above zero: a refactor that empties
# the iteration (renamed group dict, broken semantics resolution) must fail
# here rather than pass vacuously.
MINIMUM_ENDPOINTS_CHECKED = 150

# Below the observed count (29, at time of writing) but far above zero, so a
# refactor that stops iterating params-with-valid_values fails loudly instead
# of this guard passing vacuously (#156).
MIN_CONSTRAINED_PARAMS_CHECKED = 20


def _args_model(
    endpoint: Endpoint[Any], semantics: EndpointSemantics
) -> type[BaseModel]:
    """Build the args model exactly the way ``create_tool`` does."""
    return create_model(
        f"{semantics.method_name}Args",
        **ToolFactory.create_parameter_fields(
            endpoint.mandatory_params,
            endpoint.optional_params or [],
            semantics.parameter_hints,
        ),
        __config__=ConfigDict(extra="forbid", arbitrary_types_allowed=True),
    )


def _catalog() -> list[tuple[str, Endpoint[Any], EndpointSemantics]]:
    """Every (name, endpoint, semantics) triple ``setup_registry`` would enroll."""
    from fmp_data.lc import resolve_semantics_for_endpoint

    triples: list[tuple[str, Endpoint[Any], EndpointSemantics]] = []
    for group, config in get_endpoint_groups().items():
        semantics_map = config["semantics_map"]
        for name, endpoint in config["endpoint_map"].items():
            semantics = resolve_semantics_for_endpoint(name, semantics_map)
            if semantics is not None:
                triples.append((f"{group}.{name}", endpoint, semantics))
    return triples


def test_tool_schema_requires_exactly_the_mandatory_params() -> None:
    """A tool's required arguments must be the endpoint's mandatory params.

    Not ``param.required`` and not "has no default": 13 endpoints declare a
    ``default`` on a mandatory param and 13 more carry ``required=True`` on a
    param that sits in ``optional_params``. Membership of ``mandatory_params``
    is the only self-consistent answer, so it is the one the schema follows.
    """
    drift: dict[str, str] = {}
    checked = 0

    for label, endpoint, semantics in _catalog():
        checked += 1
        model = _args_model(endpoint, semantics)
        required = {
            name for name, field in model.model_fields.items() if field.is_required()
        }
        expected = {param.name for param in endpoint.mandatory_params}
        if required != expected:
            drift[label] = (
                f"over-required={sorted(required - expected)} "
                f"under-required={sorted(expected - required)}"
            )

    assert drift == {}, f"Tool schemas disagree with endpoint arity: {drift}"
    assert checked >= MINIMUM_ENDPOINTS_CHECKED, (
        f"Only {checked} endpoints checked; expected at least "
        f"{MINIMUM_ENDPOINTS_CHECKED}. The catalog iteration is broken."
    )


def test_optional_params_default_to_their_declared_value() -> None:
    """An optional param with a ``default`` must keep it in the tool schema.

    ``Endpoint.validate_params`` marks a param as seen before it skips a
    ``None`` value, so an explicitly-passed ``None`` suppresses the default it
    would otherwise apply. Defaulting the schema field to ``None`` instead of
    ``param.default`` would therefore silently drop the default off the wire.
    """
    mismatches: dict[str, str] = {}
    checked = 0

    for label, endpoint, semantics in _catalog():
        model = _args_model(endpoint, semantics)
        for param in endpoint.optional_params or []:
            field = model.model_fields[param.name]
            checked += 1
            if field.default != param.default:
                mismatches[f"{label}.{param.name}"] = (
                    f"schema default {field.default!r} != endpoint default "
                    f"{param.default!r}"
                )

    assert mismatches == {}, f"Optional param defaults drifted: {mismatches}"
    assert checked > 0, "No optional params were checked"


def test_optional_params_accept_omission() -> None:
    """The canonical #128 repro: an all-optional-but-one endpoint stays callable."""
    from fmp_data.market.endpoints import HISTORICAL_SECTOR_PE
    from fmp_data.market.mapping import MARKET_ENDPOINTS_SEMANTICS

    semantics = MARKET_ENDPOINTS_SEMANTICS["historical_sector_pe"]
    model = _args_model(HISTORICAL_SECTOR_PE, semantics)

    required = {
        name for name, field in model.model_fields.items() if field.is_required()
    }
    assert required == {"sector"}

    instance = model(sector="Technology")
    assert instance.model_dump()["sector"] == "Technology"


def test_mandatory_params_are_still_enforced() -> None:
    """Relaxing optional params must not make mandatory ones optional."""
    from fmp_data.company.endpoints import PROFILE
    from fmp_data.company.mapping import COMPANY_ENDPOINTS_SEMANTICS

    semantics = COMPANY_ENDPOINTS_SEMANTICS["profile"]
    model = _args_model(PROFILE, semantics)

    with pytest.raises(ValueError):
        model()


def test_omitted_optional_reaches_the_endpoint_with_its_declared_default() -> None:
    """An omitted optional must still arrive at the client carrying its default.

    This pins a *third-party* contract, which is why it drives a real
    ``StructuredTool`` rather than inspecting ``model_fields``. Giving optional
    params ``default=param.default`` only helps if langchain then forwards
    those fields: ``BaseTool._parse_input`` currently includes fields holding
    explicit defaults, but langchain has historically used the narrower
    ``if k in tool_input`` filter, and ``langchain-core`` is pinned ``>=1.4.9``
    with no upper bound.

    If that behaviour reverts, 64 optional params across the catalog silently
    stop sending their declared defaults -- ``period=annual`` and ``limit=40``
    would fall off the wire on every LLM call that omitted them -- while every
    schema-shape assertion in this file still passes. So assert on the kwargs
    the wrapped function actually receives.
    """
    from langchain_core.tools import StructuredTool

    from fmp_data.fundamental.endpoints import INCOME_STATEMENT
    from fmp_data.fundamental.mapping import FUNDAMENTAL_ENDPOINTS_SEMANTICS

    semantics = FUNDAMENTAL_ENDPOINTS_SEMANTICS["income_statement"]
    assert [p.name for p in INCOME_STATEMENT.mandatory_params] == ["symbol"]
    declared = {p.name: p.default for p in INCOME_STATEMENT.optional_params or []}
    assert declared == {"period": "annual", "limit": 40}, (
        f"fixture drifted -- INCOME_STATEMENT optional defaults are now {declared}"
    )

    received: dict[str, Any] = {}

    def endpoint_func(**kwargs: Any) -> str:
        received.update(kwargs)
        return "ok"

    tool = StructuredTool.from_function(
        func=endpoint_func,
        name=semantics.method_name,
        description=semantics.natural_description,
        args_schema=_args_model(INCOME_STATEMENT, semantics),
        return_direct=True,
        infer_schema=False,
    )

    # The LLM supplies only the mandatory param, as it is now entitled to.
    assert tool.invoke({"symbol": "AAPL"}) == "ok"

    assert received == {"symbol": "AAPL", "period": "annual", "limit": 40}, (
        "langchain dropped fields holding explicit defaults, so optional "
        f"endpoint defaults no longer reach the client. Received: {received}"
    )

    # ...and the endpoint agrees those kwargs are valid, closing the round trip.
    assert INCOME_STATEMENT.validate_params(received)["period"] == "annual"


def test_constrained_params_advertise_only_valid_values() -> None:
    """A schema's advertised examples must never fall outside ``valid_values``.

    #156: ``ToolFactory.create_parameter_fields`` used to advertise a
    parameter's hand-written ``ParameterHint.examples`` regardless of what the
    endpoint actually accepts (``EndpointParam.valid_values``, enforced by
    ``EndpointParam.validate_value``), so the two could disagree and the LLM
    would be handed a value the client rejects. Examples are now derived from
    ``valid_values`` whenever the endpoint declares it, which makes this
    assertion true by construction -- the guard exists so a future hand-written
    override cannot make it false again.
    """
    offenders: dict[str, str] = {}
    constrained_checked = 0

    for label, endpoint, semantics in _catalog():
        model = _args_model(endpoint, semantics)
        params = list(endpoint.mandatory_params) + list(endpoint.optional_params or [])
        for param in params:
            valid_values = getattr(param, "valid_values", None)
            if not valid_values:
                continue
            constrained_checked += 1
            allowed = {
                str(value.value) if isinstance(value, Enum) else str(value)
                for value in valid_values
            }
            field = model.model_fields[param.name]
            schema_examples = field.examples or []
            rejected = [
                example for example in schema_examples if str(example) not in allowed
            ]
            if rejected:
                offenders[f"{label}.{param.name}"] = (
                    f"schema advertises {rejected}, outside valid_values "
                    f"{sorted(allowed)}"
                )

    assert constrained_checked >= MIN_CONSTRAINED_PARAMS_CHECKED, (
        f"only {constrained_checked} constrained params were checked; the "
        "scan is not covering the catalog and this guard would pass vacuously"
    )
    assert offenders == {}, (
        "these generated tool schemas advertise examples the endpoint "
        f"rejects: {offenders}"
    )


def test_examples_and_field_type_prefer_valid_values_over_a_drifted_hint() -> None:
    """Direct unit check: ``valid_values`` wins even when a hint disagrees.

    The catalog-wide guard above is data-dependent -- it can only fail if some
    real hint has actually drifted from its parameter's ``valid_values``, and
    at time of writing none has (that is the point of #156: examples are now
    derived, not hand-written). So it cannot, by itself, prove a future
    regression that reverts ``ToolFactory`` to prefer ``hint.examples`` would
    be caught. This test manufactures the disagreement and drives it through
    ``create_parameter_fields`` -- the production path that builds tool schemas
    -- so a regression in the wiring (not only the helpers) fails the suite.
    """
    from fmp_data.lc.models import ParameterHint
    from fmp_data.models import EndpointParam, ParamLocation, ParamType

    param = EndpointParam(
        name="period",
        location=ParamLocation.QUERY,
        param_type=ParamType.STRING,
        required=True,
        description="Reporting period",
        valid_values=["annual", "quarter"],
    )
    drifted_hint = ParameterHint(
        natural_names=["period"],
        extraction_patterns=[],
        examples=["annual", "quarter", "biweekly"],  # "biweekly" is not valid
        context_clues=[],
    )

    # Focused helper assertions: still useful for pinpointing which step drifted.
    examples = ToolFactory.get_examples_for_param(param, drifted_hint)
    assert examples == ["annual", "quarter"], (
        f"examples must come from valid_values, not the drifted hint: {examples}"
    )

    # Critical path: the same assembly ``create_tool`` / ``_args_model`` use.
    model = create_model(
        "DriftProbe",
        **ToolFactory.create_parameter_fields([param], [], {"period": drifted_hint}),
        __config__=ConfigDict(extra="forbid", arbitrary_types_allowed=True),
    )
    field = model.model_fields["period"]
    assert field.examples == ["annual", "quarter"], (
        f"schema examples must come from valid_values, not the drifted hint: "
        f"{field.examples}"
    )
    assert "biweekly" not in (field.description or ""), (
        "derived description must not re-advertise the drifted hint example"
    )
    with pytest.raises(ValidationError):
        model(period="biweekly")
    model(period="annual")  # does not raise
