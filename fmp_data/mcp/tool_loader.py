# fmp_data/mcp/tool_loader.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import importlib
import inspect
import os
from typing import Any
import warnings

from fmp_data.client import FMPDataClient
from fmp_data.logger import FMPLogger
from fmp_data.mcp._compat import MCPServerType
from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS, WITHDRAWN_TOOLS

ERR = RuntimeError  # shorten

logger = FMPLogger().get_logger(__name__)


def _resolve_attr(obj: object, dotted: str) -> Callable:
    for part in dotted.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            raise ERR(f"Attribute chain '{dotted}' failed at '{part}'")
    if not callable(obj):
        raise ERR(f"'{dotted}' is not callable")
    return obj


def _load_semantics(client_slug: str, key: str) -> Any:
    mod_path = f"fmp_data.{client_slug}.mapping"
    try:
        mapping_mod = importlib.import_module(mod_path)
    except ModuleNotFoundError as e:
        raise ERR(f"No mapping module '{mod_path}'") from e

    table_name = f"{client_slug.upper()}_ENDPOINTS_SEMANTICS"
    table = getattr(mapping_mod, table_name, None)
    if table is None:
        raise ERR(f"'{mod_path}' lacks {table_name}")

    if key not in table:
        raise ERR(f"Endpoint semantics '{key}' not found in {table_name}")
    return table[key]  # EndpointSemantics instance


def _get_tool_name_style() -> str:
    style = os.getenv("FMP_MCP_TOOL_NAME_STYLE", "key").strip().lower()
    if style not in {"key", "spec"}:
        return "key"
    return style


def build_key_to_spec(all_tools: list[dict[str, str]]) -> dict[str, list[str]]:
    key_to_spec: dict[str, list[str]] = {}
    for tool in all_tools:
        key = tool["key"]
        spec = tool["spec"]
        if key not in key_to_spec:
            key_to_spec[key] = []
        key_to_spec[key].append(spec)
    return key_to_spec


def _warn_if_deprecated(full_spec: str) -> None:
    """Announce a tool key that is scheduled for removal in 3.0.

    Emitted once per resolution, i.e. once per manifest entry naming the key.
    Deduplication is delegated to Python's default warning filter, which shows
    a given (message, category, module, lineno) once per process — so each
    distinct deprecated key surfaces once, at the caller's own location.

    The announcement goes out over **two** channels, because neither one
    reaches every consumer on its own:

    * ``warnings.warn`` with ``stacklevel=4`` walks out of the library to the
      caller: ``_warn_if_deprecated`` (1) -> ``_resolve_tool_spec`` (2) ->
      ``register_from_manifest`` (3) -> caller (4). Attributing the warning to
      the user's module is what lets their own ``filterwarnings`` rules match.
    * ``logger.warning`` covers the path that actually dominates in practice.
      When the caller is :func:`fmp_data.mcp.server.create_app` — which is what
      ``python -m fmp_data.mcp``, ``fmp-mcp serve`` and Claude Desktop all
      funnel through — frame 4 *is* ``create_app``, so the warning is
      attributed to ``fmp_data.mcp.server``. Python's default filter chain is
      ``default::DeprecationWarning:__main__`` followed by
      ``ignore::DeprecationWarning``, so a warning attributed to any module
      other than ``__main__`` is discarded before it is ever printed. Without
      the log line, the single most common way to run this server announces
      nothing at all before 3.0 removes the key.

    No stacklevel can point at the real culprit anyway: the offending key
    usually lives in a manifest *data* file, not in a stack frame.
    """
    replacement = DEPRECATED_TOOLS.get(full_spec)
    if replacement is not None:
        message = (
            f"MCP tool key '{full_spec}' is deprecated and will be removed in "
            f"3.0; use '{replacement}' instead. Both names call the same "
            f"client method, so the replacement is a drop-in."
        )
    elif full_spec in WITHDRAWN_TOOLS:
        # A different failure from the alias case above, and it needs a
        # different sentence: the endpoint is gone, so the tool answers with
        # nothing at all, and any successor is a migration rather than a
        # rename. Saying "drop-in" here would be untrue.
        successor = WITHDRAWN_TOOLS[full_spec]
        remedy = (
            f"the closest live tool is '{successor}', but its payload differs "
            f"-- check the fields you rely on"
            if successor
            else "FMP publishes no replacement"
        )
        message = (
            f"MCP tool key '{full_spec}' names an endpoint FMP no longer "
            f"serves; it returns no data and will be removed in 3.0. {remedy}."
        )
    else:
        return
    warnings.warn(message, DeprecationWarning, stacklevel=4)
    logger.warning(message)


class ResolutionStatus(Enum):
    """What :func:`resolve_tool_spec` made of a single manifest entry."""

    #: Resolves to exactly one catalog spec, which is not deprecated.
    RESOLVED = "resolved"
    #: Resolves, but to a spec removed in 3.0. ``replacement`` names the
    #: canonical spec. Still registrable today, hence a resolved status.
    DEPRECATED = "deprecated"
    #: Resolves, but to an endpoint FMP no longer serves: the tool registers
    #: and answers with nothing. Distinct from :attr:`DEPRECATED`, which is a
    #: rename whose replacement is a drop-in -- here ``successor`` is a
    #: migration and may not exist at all. Still registrable today, so an
    #: explicit manifest keeps working until 3.0.
    WITHDRAWN = "withdrawn"
    #: A bare key claimed by more than one client. ``candidates`` lists them.
    AMBIGUOUS = "ambiguous"
    #: Neither a known spec nor a known key.
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Resolution:
    """The outcome of resolving one manifest entry, as data.

    Deliberately not a tuple: callers ask different questions of it. The
    registration path wants the ``(spec, client, key)`` triple and whether to
    announce a deprecation; ``fmp-mcp validate`` wants the failure kind and
    the material to explain it with (every candidate of an ambiguous key, the
    replacement for a deprecated spec). Both read the same fields off the same
    object, so neither can drift from the rule (#149).

    Attributes
    ----------
    entry
        The manifest entry as written, bare key or fully qualified spec.
    status
        See :class:`ResolutionStatus`.
    spec, client, key
        The resolved ``"<client>.<key>"`` spec split into its parts, or
        ``None`` when :attr:`is_resolved` is false.
    replacement
        The canonical spec superseding a deprecated one; ``None`` otherwise.
        Deliberately not set for a withdrawn spec: a withdrawal has no
        drop-in, and callers bucket on it.
    successor
        The nearest live spec for a withdrawn one, or ``None`` when FMP
        publishes no replacement at all. Kept apart from ``replacement``
        because the two carry different promises.
    candidates
        Every spec claiming an ambiguous bare key, sorted; empty otherwise.
    message
        Why an unresolved entry failed, phrased for a user; ``None`` when
        resolved. This is the text the registration path raises.
    """

    entry: str
    status: ResolutionStatus
    spec: str | None = None
    client: str | None = None
    key: str | None = None
    replacement: str | None = None
    successor: str | None = None
    candidates: tuple[str, ...] = ()
    message: str | None = None

    @property
    def is_resolved(self) -> bool:
        """True when the entry names exactly one registrable tool.

        A withdrawn spec still registers -- it answers empty rather than
        failing -- so an explicit manifest naming one keeps working until 3.0.
        """
        return self.status in (
            ResolutionStatus.RESOLVED,
            ResolutionStatus.DEPRECATED,
            ResolutionStatus.WITHDRAWN,
        )

    @property
    def is_deprecated(self) -> bool:
        """True when the entry resolves to a spec removed in 3.0."""
        return self.status is ResolutionStatus.DEPRECATED

    @property
    def is_withdrawn(self) -> bool:
        """True when the entry resolves to an endpoint FMP no longer serves."""
        return self.status is ResolutionStatus.WITHDRAWN

    @property
    def is_retired(self) -> bool:
        """True when resolving this entry must announce something.

        The gate the registration path warns behind. Both retirement kinds
        have to pass it; gating on :attr:`is_deprecated` alone is what made
        the withdrawal branch of ``_warn_if_deprecated`` unreachable.
        """
        return self.is_deprecated or self.is_withdrawn

    def require(self) -> tuple[str, str, str]:
        """Return ``(spec, client, key)`` or raise the failure message."""
        if not self.is_resolved or self.spec is None:
            raise ERR(self.message or f"Tool key '{self.entry}' cannot be resolved")
        client_slug, sem_key = self.spec.split(".", 1)
        return self.spec, client_slug, sem_key


def _resolved(entry: str, full_spec: str) -> Resolution:
    client_slug, sem_key = full_spec.split(".", 1)
    replacement = DEPRECATED_TOOLS.get(full_spec)
    if replacement is not None:
        status = ResolutionStatus.DEPRECATED
    elif full_spec in WITHDRAWN_TOOLS:
        status = ResolutionStatus.WITHDRAWN
    else:
        status = ResolutionStatus.RESOLVED
    return Resolution(
        entry=entry,
        status=status,
        spec=full_spec,
        client=client_slug,
        key=sem_key,
        replacement=replacement,
        successor=(
            WITHDRAWN_TOOLS.get(full_spec)
            if status is ResolutionStatus.WITHDRAWN
            else None
        ),
    )


def resolve_tool_spec(spec: str, key_to_spec: dict[str, list[str]]) -> Resolution:
    """Resolve one manifest entry against the tool catalog. Pure.

    The single implementation of "a bare tool key resolves only when exactly
    one client claims it" (#126). It emits no warning, writes no log line and
    raises nothing, so a validator can classify a whole manifest without
    announcing deprecations for keys the user is merely *checking*. The
    registration path pairs it with :func:`_warn_if_deprecated`; nobody else
    does (#149).

    Parameters
    ----------
    spec
        A bare key (``"profile"``) or a full spec (``"company.profile"``).
    key_to_spec
        Key to claiming specs, from :func:`build_key_to_spec`. Its values are
        also the catalog, so a full spec absent from them is UNKNOWN rather
        than trusted -- a typo must not survive to a confusing import error.

    Returns
    -------
    Resolution
        Never ``None``; failures are a status, not an exception.
    """
    if "." in spec:
        catalog = {claimed for specs in key_to_spec.values() for claimed in specs}
        if spec not in catalog:
            return Resolution(
                entry=spec,
                status=ResolutionStatus.UNKNOWN,
                message=f"Tool key '{spec}' not found in available tools",
            )
        return _resolved(spec, spec)

    # Two clients can legitimately expose distinct tools under the same key
    # (see issue #126), and there is no defensible way to pick one.
    specs_for_key = sorted(key_to_spec.get(spec, []))
    if not specs_for_key:
        return Resolution(
            entry=spec,
            status=ResolutionStatus.UNKNOWN,
            message=f"Tool key '{spec}' not found in available tools",
        )
    if len(specs_for_key) > 1:
        candidates = ", ".join(specs_for_key)
        return Resolution(
            entry=spec,
            status=ResolutionStatus.AMBIGUOUS,
            candidates=tuple(specs_for_key),
            message=(
                f"Tool key '{spec}' is claimed by {len(specs_for_key)} clients "
                f"({candidates}), so the bare key cannot be resolved. Bare tool "
                f"keys work only when exactly one client claims them; name the "
                f"client explicitly using the full '<client>.<key>' form, e.g. "
                f"'{specs_for_key[0]}'."
            ),
        )

    return _resolved(spec, specs_for_key[0])


def _resolve_tool_spec(
    spec: str, key_to_spec: dict[str, list[str]]
) -> tuple[str, str, str]:
    """Registration-path resolution: the pure rule plus the announcement.

    Raises
    ------
    RuntimeError
        If the entry is unknown or ambiguous.
    """
    resolution = resolve_tool_spec(spec, key_to_spec)
    full_spec, client_slug, sem_key = resolution.require()
    if resolution.is_retired:
        _warn_if_deprecated(full_spec)
    return full_spec, client_slug, sem_key


def _validate_tool_names(
    resolved_specs: list[tuple[str, str, str]], name_style: str
) -> None:
    if name_style != "key":
        return
    name_counts: dict[str, int] = {}
    for _, _, sem_key in resolved_specs:
        name_counts[sem_key] = name_counts.get(sem_key, 0) + 1
    duplicates = [name for name, count in name_counts.items() if count > 1]
    if duplicates:
        dup_list = ", ".join(sorted(duplicates))
        raise ERR(
            "Duplicate tool keys detected for MCP tool names: "
            f"{dup_list}. Set FMP_MCP_TOOL_NAME_STYLE=spec or remove duplicates."
        ) from None


def register_from_manifest(
    mcp: MCPServerType,
    fmp_client: FMPDataClient,
    tool_specs: list[str],
) -> None:
    """
    Register tools declared in a list of tool specifications.

    Tool specs can be in two formats:
    1. Full format: "<client>.<semantics_key>" (e.g., "company.profile")
    2. Key-only format: "<semantics_key>" (e.g., "profile")

    For key-only format, the function will auto-discover the correct client.

    Raises:
        RuntimeError: on any lookup / validation failure.
    """
    # Import discovery utilities
    from fmp_data.mcp.discovery import discover_all_tools

    # Build a map from keys to full specs for auto-discovery
    all_tools = discover_all_tools()
    key_to_spec = build_key_to_spec(all_tools)

    resolved_specs: list[tuple[str, str, str]] = []
    for spec in tool_specs:
        resolved_specs.append(_resolve_tool_spec(spec, key_to_spec))

    name_style = _get_tool_name_style()
    _validate_tool_names(resolved_specs, name_style)

    for full_spec, client_slug, sem_key in resolved_specs:
        sem = _load_semantics(client_slug, sem_key)

        # dotted path to real method on the live client object
        dotted_method = f"{client_slug}.{sem.method_name}"
        func = _resolve_attr(fmp_client, dotted_method)

        # Build description - fall back to callable docstring if required
        description = sem.natural_description or inspect.getdoc(func) or ""

        # Attach as MCP tool
        tool_name = sem_key if name_style == "key" else full_spec
        mcp.add_tool(func, name=tool_name, description=description)
