"""Binding endpoint declarations to live client methods (#188).

Both optional integrations answer the same question -- *given an endpoint and
the semantics naming its client method, how do I call that method?* -- and
both used to answer it themselves:

* ``fmp_data.mcp.tool_loader`` resolved ``client.<module>.<method>`` and handed
  the callable to the MCP framework, which advertises its Python signature.
* ``fmp_data.lc.vector_store`` resolved the same callable, then mapped
  wire/endpoint parameter names onto it at invoke time (#172), gated on whether
  every required method parameter could be filled (#186).

Keeping the two apart is what #188 calls drift risk, and it was already real:
the "which parameters of this method can receive a value" filter was written
out four separate times -- three in ``vector_store`` and once more in the
catalogue guard -- and one of the four quietly disagreed with the others (it
did not exclude ``*args``/``**kwargs``). This module is the single
implementation. Both integrations import from here; neither reimplements.

It deliberately lives in the core package rather than under ``lc/`` or
``mcp/``: it depends on nothing but :mod:`inspect`, and a shared layer that
could only be imported with an optional extra installed would not be shared.

Two resolution styles, one rule
-------------------------------
:func:`resolve_attr` raises and :func:`resolve_client_method` returns ``None``.
That is not an oversight -- the callers want different things from a missing
method. MCP is registering a tool at startup and a ghost ``method_name`` must
be a loud failure, not a tool that 500s on first use. LangChain builds tools
against whatever client the store was handed, including a bare
:class:`~fmp_data.base.BaseClient` with no sub-clients, and falls back to
``client.request``. Both walk the same chain to the same callable.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import inspect
from typing import Any, cast

__all__ = [
    "ENDPOINT_TO_METHOD_ALIASES",
    "bindable_params",
    "camel_to_snake",
    "map_tool_kwargs_to_method",
    "method_dispatch_compatible",
    "method_param_aliases",
    "partition_params_for_method",
    "resolve_attr",
    "resolve_client_method",
    "resolve_dispatch_method",
    "resolve_method_param_name",
    "uncovered_required_params",
]


def camel_to_snake(name: str) -> str:
    """Convert ``periodLength`` / ``sicCode`` to ``period_length`` / ``sic_code``."""
    parts: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index:
            parts.append("_")
            parts.append(char.lower())
        else:
            parts.append(char.lower() if char.isupper() else char)
    return "".join(parts)


#: Endpoint-param name -> ordered method-param candidates.
#:
#: Client methods are the call surface both integrations use
#: (``fmp_client.<client>.<method>``). Their parameter names are ordinary
#: Python (``from_date``, ``sic_code``, ``period_length``), while endpoint
#: declarations keep the wire names (``from``, ``sicCode``, ``periodLength``).
#: LangChain tools mirror the wire names; #172 maps them so tools can dispatch
#: through the method without renaming every schema field.
#:
#: Order matters: the first candidate present in the method's signature wins,
#: so an exact match always beats an alias.
ENDPOINT_TO_METHOD_ALIASES: Mapping[str, tuple[str, ...]] = {
    "from": ("from", "from_date", "start_date"),
    "to": ("to", "to_date", "end_date"),
    "start_date": ("start_date", "from_date"),
    "end_date": ("end_date", "to_date"),
    # economics.get_economic_indicators renames the wire ``name`` param.
    "name": ("name", "indicator_name", "query"),
    # Several clients take a single report/as-of day under a different name.
    "date": (
        "date",
        "report_date",
        "holdings_date",
        "target_date",
        "trade_date",
    ),
    # sec.search_company_by_name: endpoint ``company``, method ``name``.
    "company": ("company", "name"),
}


def method_param_aliases(endpoint_param: str) -> tuple[str, ...]:
    """Ordered method-parameter names that may correspond to *endpoint_param*."""
    aliases = list(ENDPOINT_TO_METHOD_ALIASES.get(endpoint_param, (endpoint_param,)))
    snake = camel_to_snake(endpoint_param)
    if snake not in aliases:
        aliases.append(snake)
    return tuple(aliases)


def resolve_method_param_name(
    endpoint_param: str, method_params: set[str]
) -> str | None:
    """Pick the method parameter that should receive *endpoint_param*'s value."""
    for candidate in method_param_aliases(endpoint_param):
        if candidate in method_params:
            return candidate
    return None


def bindable_params(method: Callable[..., Any]) -> dict[str, inspect.Parameter]:
    """Parameters of *method* that a caller can fill by name.

    ``self`` is excluded (bound methods hide it anyway, but the catalogue guard
    and the synthetic tests pass plain functions), and so are ``*args`` /
    ``**kwargs``: they are not names a caller can target, and treating
    ``**kwargs`` as a real parameter made a method look like it accepted
    anything -- and, because a ``VAR_KEYWORD`` parameter has no default, like
    it *required* a parameter literally named ``kwargs``.

    This is the definition every other function here shares. It existed in
    four hand-written copies before #188 and they were not identical; that is
    the bug class this module exists to remove.
    """
    return {
        name: param
        for name, param in inspect.signature(method).parameters.items()
        if name != "self"
        and param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }


def uncovered_required_params(
    method: Callable[..., Any],
    endpoint_param_names: Sequence[str],
) -> frozenset[str]:
    """Required parameters of *method* that no endpoint field can fill.

    Empty means method dispatch is safe: every parameter without a default has
    a wire source, so the call cannot ``TypeError`` on a missing argument.
    Non-empty names the debt, which is what the catalogue guard reports and
    allowlists (see ``tests/unit/lc/test_endpoint_method_coverage.py``).
    """
    method_params = bindable_params(method)
    names = set(method_params)
    covered = {
        resolved
        for ep_name in endpoint_param_names
        if (resolved := resolve_method_param_name(ep_name, names)) is not None
    }
    return frozenset(
        name
        for name, param in method_params.items()
        if param.default is inspect.Parameter.empty and name not in covered
    )


def method_dispatch_compatible(
    method: Callable[..., Any],
    endpoint_param_names: Sequence[str],
) -> bool:
    """True if every required method param can be filled from endpoint params.

    A shape mismatch that no alias can bridge means the tool must keep
    ``client.request`` dispatch rather than risk a ``TypeError`` at invoke.
    """
    return not uncovered_required_params(method, endpoint_param_names)


def map_tool_kwargs_to_method(
    method: Callable[..., Any], kwargs: Mapping[str, Any]
) -> dict[str, Any]:
    """Translate tool kwargs (endpoint/wire names) onto *method*'s signature.

    ``None`` values are dropped so a method default can apply — that is the
    half of #172 that makes an LLM-omitted ``from``/``to`` still work on SEC
    search methods, which default the window to the last 30 days.
    """
    method_params = set(bindable_params(method))
    mapped: dict[str, Any] = {}
    for endpoint_name, value in kwargs.items():
        if value is None:
            continue
        method_name = resolve_method_param_name(endpoint_name, method_params)
        if method_name is not None:
            mapped[method_name] = value
    return mapped


def partition_params_for_method(
    mandatory_params: Sequence[Any],
    optional_params: Sequence[Any],
    method: Callable[..., Any] | None,
) -> tuple[list[Any], list[Any]]:
    """Reclassify endpoint params by the client method's defaults (#172).

    When *method* is available, an endpoint-mandatory parameter whose mapped
    method parameter has a default becomes optional in the tool schema — the
    method will fill it. Endpoint params that do not resolve to any method
    parameter are omitted entirely: method dispatch drops unmapped kwargs at
    invoke time, so advertising them as required would force LLMs to supply
    values that never reach the API (e.g. revenue ``structure``, employee
    ``limit``). Without a resolvable method the endpoint lists are returned
    unchanged (the pre-#172 behaviour).

    Takes and returns ``EndpointParam``-shaped objects, but only reads
    ``.name``, so this module stays free of a model import.
    """
    if method is None:
        return list(mandatory_params), list(optional_params)

    method_params = bindable_params(method)
    method_names = set(method_params)

    new_mandatory: list[Any] = []
    new_optional: list[Any] = []

    def place(param: Any) -> None:
        method_name = resolve_method_param_name(param.name, method_names)
        if method_name is None:
            # Cannot reach the method; omit from the tool schema.
            return
        method_param = method_params[method_name]
        if method_param.default is inspect.Parameter.empty:
            new_mandatory.append(param)
        else:
            new_optional.append(param)

    for param in mandatory_params:
        place(param)
    for param in optional_params:
        place(param)
    return new_mandatory, new_optional


def resolve_attr(obj: object, dotted: str) -> Callable[..., Any]:
    """Walk a dotted attribute chain to a callable, or raise.

    The strict half of the pair. MCP registers tools at startup from a
    manifest, so a ``method_name`` naming nothing must fail there and then --
    a tool that resolves to ``None`` and explodes on first invoke is strictly
    worse than a server that refuses to start.

    Raises
    ------
    RuntimeError
        If any link in the chain is missing, or the endpoint of it is not
        callable.
    """
    for part in dotted.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            raise RuntimeError(f"Attribute chain '{dotted}' failed at '{part}'")
    if not callable(obj):
        raise RuntimeError(f"'{dotted}' is not callable")
    return cast(Callable[..., Any], obj)


def resolve_client_method(
    client: Any, client_name: str, method_name: str
) -> Callable[..., Any] | None:
    """Resolve ``client.<client_name>.<method_name>``, or ``None`` if missing.

    The lenient half of the pair — same walk as :func:`resolve_attr`, but
    returns ``None`` rather than raising so tool creation still works when the
    store holds a bare :class:`~fmp_data.base.BaseClient` (or a test double)
    that has no sub-clients. Dispatch then falls back to ``client.request``.
    """
    try:
        return resolve_attr(client, f"{client_name}.{method_name}")
    except RuntimeError:
        return None


def resolve_dispatch_method(
    client: Any,
    client_name: str,
    method_name: str,
    endpoint_param_names: Sequence[str],
) -> Callable[..., Any] | None:
    """Resolve a client method only when every required param can be mapped.

    ``None`` for either reason -- no such method, or a shape the wire fields
    cannot fill -- and the caller should fall back to ``client.request`` with
    the endpoint's own schema.
    """
    method = resolve_client_method(client, client_name, method_name)
    if method is None:
        return None
    if not method_dispatch_compatible(method, endpoint_param_names):
        return None
    return method
