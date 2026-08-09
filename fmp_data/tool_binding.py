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
from dataclasses import dataclass
from enum import Enum
import inspect
from typing import Any, cast

__all__ = [
    "ENDPOINT_TO_METHOD_ALIASES",
    "DispatchStatus",
    "MethodBinding",
    "bind_client_method",
    "bindable_params",
    "camel_to_snake",
    "keyword_unfillable_required_params",
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

#: Parameter names that name the receiver rather than an argument. A *bound*
#: method hides them already, which is the only case at runtime; the filter is
#: for the unbound functions the catalogue guard and the unit tests pass in.
#: A plain function with a parameter genuinely called ``self`` or ``cls`` would
#: be misread here, and that is an accepted trade for not treating a
#: classmethod's receiver as a required, unfillable argument (#195).
_RECEIVER_NAMES = frozenset({"self", "cls"})


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
    """Parameters of *method* that a caller can fill **by name**.

    Everything here dispatches with ``method(**mapped)``, so "by name" is the
    only thing that counts. Excluded:

    * ``self`` / ``cls`` -- the receiver. Bound methods hide it, which is the
      only case at runtime, but the catalogue guard and the unit tests pass
      plain functions. ``cls`` was missed before #195.
    * ``*args`` / ``**kwargs`` -- not names a caller can target. Treating
      ``**kwargs`` as a real parameter made a method look like it accepted
      anything and, because a ``VAR_KEYWORD`` parameter has no default, like
      it *required* a parameter literally called ``kwargs``.
    * ``POSITIONAL_ONLY`` -- reachable only positionally, so a keyword call
      can never fill it. Excluding it from *this* map is right; the trap is
      concluding it therefore does not matter, which is why
      :func:`keyword_unfillable_required_params` exists.

    A method with ``**kwargs`` does **not** get unmapped wire fields passed
    through: they reach no named parameter, so they are dropped. No catalog
    method relies on passthrough today; a future one would need an explicit
    opt-in rather than silently inheriting this behaviour (#195).

    This is the definition every other function here shares. It existed in
    four hand-written copies before #188 and they were not identical; that is
    the bug class this module exists to remove.
    """
    return {
        name: param
        for name, param in inspect.signature(method).parameters.items()
        if name not in _RECEIVER_NAMES
        and param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }


def keyword_unfillable_required_params(
    method: Callable[..., Any],
) -> frozenset[str]:
    """Required ``POSITIONAL_ONLY`` parameters -- unfillable by any keyword call.

    Dispatch is ``method(**mapped)``. A positional-only parameter without a
    default can never be satisfied that way, no matter how well the wire names
    line up, so a method that has one must not be dispatched through.

    Before #195 these were merely *absent* from :func:`bindable_params`, which
    read as "nothing required is missing" -- the gate reported compatible and
    the call then raised ``TypeError: missing 1 required positional
    argument``, which is exactly the failure the gate exists to prevent::

        def f(cik, /, year=2020): ...
        method_dispatch_compatible(f, ["cik", "year"])  # was True, now False
    """
    return frozenset(
        name
        for name, param in inspect.signature(method).parameters.items()
        if name not in _RECEIVER_NAMES
        and param.kind is inspect.Parameter.POSITIONAL_ONLY
        and param.default is inspect.Parameter.empty
    )


def uncovered_required_params(
    method: Callable[..., Any],
    endpoint_param_names: Sequence[str],
) -> frozenset[str]:
    """Required parameters of *method* that no endpoint field can fill.

    Empty means method dispatch is safe: every parameter without a default has
    a wire source, so the call cannot ``TypeError`` on a missing argument.
    Non-empty names the debt, which is what the catalogue guard reports and
    allowlists (see ``tests/unit/lc/test_endpoint_method_coverage.py``).

    Two ways a required parameter goes uncovered:

    * no endpoint field maps onto it (the ``report_date`` case #188 fixed), or
    * it is positional-only, so a keyword call cannot reach it at all --
      see :func:`keyword_unfillable_required_params` (#195).
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
    ) | keyword_unfillable_required_params(method)


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

    Keys that reach no parameter are dropped, including when the method takes
    ``**kwargs`` -- see :func:`bindable_params`.

    Raises
    ------
    ValueError
        If two different keys both resolve to one method parameter (e.g.
        ``from`` and ``from_date`` against a method taking ``from_date``).
        Silently keeping whichever came last would pick one of two
        *conflicting* values -- for a date window, quietly answering about the
        wrong period. No endpoint declares an aliased pair today, and the tool
        args model is ``extra="forbid"``, so this is unreachable from a
        well-formed schema; a direct caller who hits it gets told which two
        keys collided instead of a plausible wrong answer (#195).
    """
    method_params = set(bindable_params(method))
    mapped: dict[str, Any] = {}
    source: dict[str, str] = {}
    for endpoint_name, value in kwargs.items():
        if value is None:
            continue
        method_name = resolve_method_param_name(endpoint_name, method_params)
        if method_name is None:
            continue
        claimed_by = source.get(method_name)
        if claimed_by is not None and mapped[method_name] != value:
            raise ValueError(
                f"'{claimed_by}' and '{endpoint_name}' both map to method "
                f"parameter '{method_name}' with different values "
                f"({mapped[method_name]!r} and {value!r}); pass only one."
            )
        mapped[method_name] = value
        source[method_name] = claimed_by or endpoint_name
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


class DispatchStatus(Enum):
    """Why :func:`bind_client_method` did or did not produce a method."""

    #: Bound. Dispatch through the method.
    METHOD = "method"
    #: The client has no such sub-client. Expected and unremarkable for a
    #: bare ``BaseClient`` or a test double -- not a misconfiguration.
    NO_SUBCLIENT = "no_subclient"
    #: The sub-client exists but has no callable of that name. The semantics
    #: name a method that is not there: almost always a typo or a rename.
    NO_METHOD = "no_method"
    #: The method exists but a required parameter has no wire source, so
    #: calling it would ``TypeError``. See :attr:`MethodBinding.uncovered`.
    SHAPE_MISMATCH = "shape_mismatch"


@dataclass(frozen=True)
class MethodBinding:
    """The outcome of binding one endpoint to a client method, as data.

    A bare ``Callable | None`` could not answer *why* there was no method, so
    the LangChain layer fell back to ``client.request`` in silence and a
    genuinely misconfigured store looked exactly like a bare client (#194).
    Modelled on :class:`fmp_data.mcp.tool_loader.Resolution`, for the same
    reason: callers ask different questions of the same outcome.
    """

    method: Callable[..., Any] | None
    status: DispatchStatus
    #: Required method params with no wire source; only for SHAPE_MISMATCH.
    uncovered: frozenset[str] = frozenset()

    @property
    def is_dispatchable(self) -> bool:
        """True when the caller should dispatch through :attr:`method`."""
        return self.method is not None

    @property
    def is_expected_miss(self) -> bool:
        """True when falling back is normal rather than a misconfiguration.

        Only :attr:`DispatchStatus.NO_SUBCLIENT` qualifies: a store built on a
        bare client legitimately has no sub-clients, and warning once per
        endpoint would bury the two statuses that *are* worth reading.
        """
        return self.status is DispatchStatus.NO_SUBCLIENT

    def describe(self, client_name: str, method_name: str) -> str:
        """One line explaining the outcome, for a log record."""
        target = f"{client_name}.{method_name}"
        match self.status:
            case DispatchStatus.METHOD:
                return f"dispatching through {target}"
            case DispatchStatus.NO_SUBCLIENT:
                return (
                    f"client has no '{client_name}' sub-client; falling back "
                    f"to client.request"
                )
            case DispatchStatus.NO_METHOD:
                return (
                    f"'{client_name}' sub-client has no callable "
                    f"'{method_name}'; falling back to client.request"
                )
            case _:
                return (
                    f"{target} cannot be filled from the endpoint's fields "
                    f"(required method params without a wire source: "
                    f"{sorted(self.uncovered)}); falling back to "
                    f"client.request"
                )


def bind_client_method(
    client: Any,
    client_name: str,
    method_name: str,
    endpoint_param_names: Sequence[str],
) -> MethodBinding:
    """Bind an endpoint to its client method, reporting why when it cannot.

    The full form of :func:`resolve_dispatch_method`. Prefer this when the
    caller can act on the reason -- which, since #194, the LangChain tool
    factory does: it logs a misconfiguration and stays quiet about a bare
    client.
    """
    subclient = getattr(client, client_name, None)
    if subclient is None:
        return MethodBinding(None, DispatchStatus.NO_SUBCLIENT)

    method = getattr(subclient, method_name, None)
    if method is None or not callable(method):
        return MethodBinding(None, DispatchStatus.NO_METHOD)

    uncovered = uncovered_required_params(method, endpoint_param_names)
    if uncovered:
        return MethodBinding(None, DispatchStatus.SHAPE_MISMATCH, uncovered)

    return MethodBinding(cast(Callable[..., Any], method), DispatchStatus.METHOD)


def resolve_dispatch_method(
    client: Any,
    client_name: str,
    method_name: str,
    endpoint_param_names: Sequence[str],
) -> Callable[..., Any] | None:
    """Resolve a client method only when every required param can be mapped.

    ``None`` for any reason -- no sub-client, no such method, or a shape the
    wire fields cannot fill -- and the caller should fall back to
    ``client.request`` with the endpoint's own schema. Use
    :func:`bind_client_method` when the reason matters.
    """
    return bind_client_method(
        client, client_name, method_name, endpoint_param_names
    ).method
