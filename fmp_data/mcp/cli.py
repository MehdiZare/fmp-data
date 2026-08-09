"""
MCP CLI Commands

This module provides command-line utilities for managing MCP tools and configurations.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def list_available_tools() -> list[dict[str, Any]]:
    """
    Discover and list all available MCP tools from endpoint semantics.

    Each tool carries a ``deprecated`` key: the spec that replaces it, or
    ``None``. Deprecated specs still resolve but are removed in 3.0, so every
    output format can flag them without re-deriving the policy.

    Returns
    -------
    list[dict[str, Any]]
        List of tool definitions with metadata
    """
    from fmp_data.mcp.discovery import discover_all_tools
    from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

    return [
        {**tool, "deprecated": DEPRECATED_TOOLS.get(tool["spec"])}
        for tool in discover_all_tools()
    ]


def _deprecation_note(tool: dict[str, Any]) -> str:
    """``" [DEPRECATED -> <replacement>]"`` for a deprecated tool, else ``""``."""
    replacement = tool.get("deprecated")
    return f" [DEPRECATED -> {replacement}]" if replacement else ""


def print_tools_table(tools: list[dict[str, Any]], format: str = "table") -> None:
    """Print tools in specified format."""
    if format == "json":
        print(json.dumps(tools, indent=2))
    elif format == "list":
        _print_tools_list(tools)
    elif format == "tree":
        _print_tools_tree(tools)
    else:
        _print_tools_table_format(tools)


def _print_tools_list(tools: list[dict[str, Any]]) -> None:
    """Print tools as a simple list."""
    for tool in tools:
        print(f"{tool['spec']}{_deprecation_note(tool)}: {tool['description']}")


def _print_tools_tree(tools: list[dict[str, Any]]) -> None:
    """Print tools in tree format."""
    if not HAS_RICH:
        print("Tree format requires 'rich' package. Using list format instead.")
        _print_tools_list(tools)
        return

    console = Console()
    tree = Tree("FMP MCP Tools")

    # Group by client
    clients: dict[str, list[dict[str, Any]]] = {}
    for tool in tools:
        client = tool["client"]
        if client not in clients:
            clients[client] = []
        clients[client].append(tool)

    for client, client_tools in sorted(clients.items()):
        branch = tree.add(f"[bold cyan]{client}[/bold cyan]")
        for tool in client_tools:
            # The full spec, not the method name (#163). Leaves used to be
            # labelled `tool["method"]`, so the entry a user has to write into
            # a manifest never appeared anywhere in this format -- and because
            # a deprecated key shares its replacement's method, the deprecated
            # row was labelled with the *replacement's* name and read as
            # self-referential. The method is kept as trailing detail.
            desc = tool["description"][:40]
            branch.add(
                f"[green]{tool['spec']}[/green]{_deprecation_note(tool)} "
                f"[dim]({tool['method']})[/dim]: {desc}..."
            )

    console.print(tree)


def _print_tools_table_format(tools: list[dict[str, Any]]) -> None:
    """Print tools in table format."""
    if HAS_RICH:
        _print_rich_table(tools)
    else:
        _print_simple_table(tools)


def _print_rich_table(tools: list[dict[str, Any]]) -> None:
    """Print tools using rich table.

    The spec column never truncates (#163). It is the primary key of this
    output -- the string a user copies into a manifest -- and rich's default
    ellipsis overflow rendered ``company.historical_price`` and
    ``company.historical_prices`` as the same ``company.historica…``, flattening
    precisely the pair a reader most needs to tell apart. ``overflow="fold"``
    wraps instead, so a narrow terminal costs a line rather than the answer.

    The deprecation marker moves to its own column for the same reason: as a
    suffix on the spec cell it was inside the truncated region, so the one
    piece of text explaining the duplicate row was the first thing cut.
    """
    console = Console()
    table = Table(title="Available FMP MCP Tools")
    table.add_column("Tool Spec", style="cyan", overflow="fold", no_wrap=False)
    table.add_column("Client", style="green")
    table.add_column("Method", style="yellow")
    table.add_column("Deprecated", style="magenta", overflow="fold", no_wrap=False)
    table.add_column("Description", style="white")

    for tool in tools:
        replacement = tool.get("deprecated")
        table.add_row(
            tool["spec"],
            tool["client"],
            tool["method"],
            f"-> {replacement}" if replacement else "",
            (
                tool["description"][:50] + "..."
                if len(tool["description"]) > 50
                else tool["description"]
            ),
        )

    console.print(table)


def _print_simple_table(tools: list[dict[str, Any]]) -> None:
    """Print tools using simple table format.

    Columns are padded, never truncated: an over-long spec pushes the row wide
    rather than losing characters, for the same reason as :func:`_print_rich_table`.
    """
    print("\nAvailable FMP MCP Tools")
    print("-" * 100)
    print(f"{'Tool Spec':<45} {'Client':<12} {'Method':<25} {'Deprecated':<30}")
    print("-" * 100)
    for tool in tools:
        replacement = tool.get("deprecated")
        note = f"-> {replacement}" if replacement else ""
        print(
            f"{tool['spec']:<45} {tool['client']:<12} {tool['method']:<25} {note:<30}"
        )


def _pluralise(count: int, noun: str) -> str:
    """``"1 tool"`` / ``"2 tools"``. Fixes the "1 tools" in validate's verdict."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _tool_name(spec: str) -> str:
    """The name a spec is advertised under in the default ``key`` style."""
    return spec.split(".", 1)[1]


def _name_collisions(specs: list[str]) -> dict[str, list[str]]:
    """Advertised name to the specs claiming it, for names claimed twice.

    Delegates the grouping to :func:`fmp_data.mcp.tool_loader.advertised_names`
    so ``generate``'s idea of "these two share a name" is the loader's, not a
    parallel one. Fixed to ``key`` style because that is what a generated
    manifest must start under by default; the ``spec`` style escape hatch is
    what the header then points at.
    """
    from fmp_data.mcp import tool_loader

    resolved = [(spec, spec.split(".", 1)[0], _tool_name(spec)) for spec in specs]
    _, collisions = tool_loader.split_name_clashes(
        tool_loader.advertised_names(resolved, "key")
    )
    return collisions


def _preferred_spec(candidates: list[str]) -> str:
    """Which side of a collision a generated manifest keeps.

    The spec the default server already serves, so ``generate`` agrees with
    ``DEFAULT_TOOLS`` rather than inventing a second opinion; sorted order
    otherwise, so the choice is deterministic and reproducible.
    """
    from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

    defaults = set(DEFAULT_TOOLS)
    for spec in candidates:
        if spec in defaults:
            return spec
    return candidates[0]


def _manifest_header(
    deprecated: list[str],
    excluded: list[str],
    collisions: dict[str, list[str]],
    withdrawn: list[str] | None = None,
) -> str:
    """The generated file's docstring, explaining anything non-obvious.

    The three kinds of drop are listed separately because the reason and the
    remedy differ: a withdrawn spec has no working endpoint behind it at all,
    a deprecated spec has a live replacement in this same manifest, and a
    collision loser is a distinct working tool you can serve by changing the
    name style. Collapsing them would tell a reader to "use the replacement"
    for something that has none.
    """
    withdrawn = withdrawn or []
    lines = [
        '"""',
        "Custom MCP Tools Manifest",
        "",
        "Generated by fmp-data MCP CLI",
    ]

    if withdrawn:
        lines += [
            "",
            "Omitted because FMP no longer serves the endpoint: the path returns",
            "404 for every request, so the tool can only ever answer empty. Where",
            "a live tool covers similar ground it is named, but the payload",
            "differs -- these are migrations, not renames:",
            "",
        ]
        lines += [f"  - {note}" for note in withdrawn]

    if deprecated:
        lines += [
            "",
            "Omitted because they are deprecated: each warns on every server",
            "start and is removed in 3.0. The replacement named beside each one",
            "is already included below, so no capability is lost:",
            "",
        ]
        lines += [f"  - {note}" for note in deprecated]

    if excluded:
        lines += [
            "",
            "Excluded so this manifest starts a server as-is. Under the default",
            "FMP_MCP_TOOL_NAME_STYLE=key the advertised tool name is the bare key,",
            "so two clients claiming one key cannot both be registered:",
            "",
        ]
        lines += [f"  - {note}" for note in excluded]
        lines += [
            "",
            "Set FMP_MCP_TOOL_NAME_STYLE=spec (names become '<client>.<key>') and add",
            "them back to serve both sides.",
        ]

    if collisions:
        lines += [
            "",
            "WARNING: these tool names are claimed by two selected specs and will",
            "fail at registration under the default FMP_MCP_TOOL_NAME_STYLE=key:",
            "",
        ]
        lines += [
            f"  - {name}: {', '.join(claims)}"
            for name, claims in sorted(collisions.items())
        ]
        lines += [
            "",
            "Set FMP_MCP_TOOL_NAME_STYLE=spec, or drop one side of each pair.",
        ]

    lines += ['"""', ""]
    return "\n".join(lines)


def _startable_catalog(
    available_specs: set[str],
    excluded: list[str],
    deprecated: list[str],
    withdrawn: list[str],
) -> list[str]:
    """The whole catalog minus what would stop it starting a *useful* server.

    Three reasons to drop a spec, kept apart because the remedy differs:

    * **withdrawn** -- the FMP endpoint 404s, so the tool can only ever answer
      empty. Dropped *before* the collision pass, because a dead spec must
      never beat a live one. It did: ``alternative.crypto_quotes`` and
      ``batch.crypto_quotes`` both claim the bare key ``crypto_quotes``, and
      ``_preferred_spec`` keeps whichever side is in ``DEFAULT_TOOLS``. Once
      the dead side was removed from ``DEFAULT_TOOLS`` the tie-break fell
      through to sorted order, which puts ``alternative`` first -- so a
      generated manifest advertised the endpoint that 404s and excluded the
      one that works.
    * **deprecated** -- an alias that still works, removed in 3.0.
    * **collision loser** -- both sides work, but one bare key cannot name two.

    Every removal appends a note to its own list and the header prints all
    three, so nothing disappears silently.
    """
    from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS, WITHDRAWN_TOOLS

    gone = sorted(set(WITHDRAWN_TOOLS) & available_specs)
    dropped = sorted(set(DEPRECATED_TOOLS) & available_specs)
    selected = sorted(available_specs - set(DEPRECATED_TOOLS) - set(WITHDRAWN_TOOLS))
    for name, candidates in sorted(_name_collisions(selected).items()):
        kept = _preferred_spec(candidates)
        for spec in candidates:
            if spec == kept:
                continue
            selected.remove(spec)
            excluded.append(f"{spec} (kept {kept}, both advertised as '{name}')")

    # Written after the collision pass, so "included below" is checked against
    # the list that actually ships rather than asserted.
    survivors = set(selected)
    for spec in dropped:
        replacement = DEPRECATED_TOOLS[spec]
        where = "included below" if replacement in survivors else "not in this manifest"
        deprecated.append(f"{spec} (deprecated; use {replacement}, {where})")
    for spec in gone:
        successor = WITHDRAWN_TOOLS[spec]
        if successor is None:
            remedy = "FMP publishes no replacement"
        else:
            where = (
                "included below" if successor in survivors else "not in this manifest"
            )
            remedy = f"nearest live tool is {successor}, {where}"
        withdrawn.append(f"{spec} ({remedy})")
    return selected


def _validated_specs(tools: list[str]) -> list[str]:
    """An explicit selection, resolved and minus entries naming nothing.

    Entries are judged by :func:`fmp_data.mcp.tool_loader.resolve_tool_spec`,
    the same pure rule the loader and ``validate`` use, so ``generate`` is the
    fourth *consumer* of that rule rather than a fourth implementation of it
    (#160). Before that it did its own membership test against fully qualified
    specs only, so ``--tools profile`` -- a form the loader resolves and
    ``validate`` blesses -- was reported "unknown" and silently dropped.

    What is written out is always the **resolved** ``<client>.<key>`` spec,
    never the bare key as typed: the qualified form is unambiguous under either
    name style, so a manifest generated from bare keys keeps working if a
    second client later claims one of them.

    Deprecated and withdrawn specs are kept -- an explicit ask is honoured --
    but reported, so the one path that can still put a retired key in a
    manifest says so just as the default path does. Both kinds are reported,
    and separately: the default path drops withdrawn specs entirely, so this
    is the only way one reaches a generated manifest, and it would otherwise
    be the one place a dead tool is written with nothing said about it.
    """
    from fmp_data.mcp import tool_loader

    key_to_spec = tool_loader.build_key_to_spec(list_available_tools())

    selected: list[str] = []
    for tool in tools:
        resolution = tool_loader.resolve_tool_spec(tool, key_to_spec)
        if resolution.status is tool_loader.ResolutionStatus.UNKNOWN:
            print(
                f"Warning: Unknown tool '{tool}', skipping. "
                "Run `fmp-mcp list` to see available tools.",
                file=sys.stderr,
            )
            continue
        if resolution.status is tool_loader.ResolutionStatus.AMBIGUOUS:
            # Reported as an ambiguity rather than as "unknown": the key is
            # perfectly good, it just needs a client. Saying "unknown" sent
            # users looking for a typo that was not there.
            print(
                f"Warning: bare key '{tool}' is claimed by "
                f"{len(resolution.candidates)} clients "
                f"({', '.join(resolution.candidates)}), so it cannot be "
                f"resolved; skipping. Name the client explicitly, e.g. "
                f"'{resolution.candidates[0]}'.",
                file=sys.stderr,
            )
            continue
        if resolution.is_deprecated:
            print(
                f"Warning: '{tool}' is deprecated and is removed in 3.0; "
                f"including it as asked. Use {resolution.replacement} instead.",
                file=sys.stderr,
            )
        elif resolution.is_withdrawn:
            successor = resolution.successor
            remedy = (
                f"The nearest live tool is {successor}, but its payload differs."
                if successor
                else "FMP publishes no replacement."
            )
            print(
                f"Warning: '{tool}' names an endpoint FMP no longer serves, so "
                f"it answers with no data; including it as asked. {remedy}",
                file=sys.stderr,
            )
        if resolution.spec is None:  # unreachable: is_resolved implies a spec
            continue
        # Two entries can name one tool -- `profile` and `company.profile` --
        # and writing both would produce a manifest the loader refuses (#162).
        # A repeated ask is one ask, so it is collapsed rather than reported.
        if resolution.spec not in selected:
            selected.append(resolution.spec)
    return selected


def _add_defaults(
    selected: list[str], available_specs: set[str], excluded: list[str]
) -> None:
    """Append ``DEFAULT_TOOLS`` in place, yielding on any name already claimed.

    A default must not break a manifest by colliding with a spec the caller
    explicitly asked for, so it is skipped and noted rather than added.

    Retired specs -- deprecated or withdrawn -- are skipped here too. Neither
    set intersects ``DEFAULT_TOOLS`` today, so this is dead defence -- but it
    runs *after* ``_startable_catalog`` has stripped both, and without it a
    future retired entry in ``DEFAULT_TOOLS`` would be silently reinstated
    into a manifest the same release just cleaned. The withdrawn half matters
    more than the deprecated one: a deprecated default still answers, while a
    withdrawn default would advertise a tool that can only return nothing.
    """
    from fmp_data.mcp.tools_manifest import (
        DEFAULT_TOOLS,
        DEPRECATED_TOOLS,
        WITHDRAWN_TOOLS,
    )

    claimed = {_tool_name(spec): spec for spec in selected}
    for tool in DEFAULT_TOOLS:
        if tool in selected or tool not in available_specs:
            continue
        if tool in DEPRECATED_TOOLS or tool in WITHDRAWN_TOOLS:
            continue
        name = _tool_name(tool)
        owner = claimed.get(name)
        if owner is not None:
            excluded.append(
                f"{tool} (default; kept {owner}, both advertised as '{name}')"
            )
            continue
        selected.append(tool)
        claimed[name] = tool


def _warn_collisions(collisions: dict[str, list[str]]) -> None:
    """Report a collision an explicit selection asked for; do not resolve it."""
    pairs = "; ".join(
        f"{name}: {', '.join(claims)}" for name, claims in sorted(collisions.items())
    )
    print(
        "Warning: selected tools collide on advertised names and will fail "
        f"to register under FMP_MCP_TOOL_NAME_STYLE=key: {pairs}. Set "
        "FMP_MCP_TOOL_NAME_STYLE=spec or drop one side.",
        file=sys.stderr,
    )


def generate_manifest(
    output_path: str | Path,
    tools: list[str] | None = None,
    include_defaults: bool = True,
) -> None:
    """
    Generate a custom manifest file with selected tools.

    With no ``tools`` filter the whole catalog is written *minus* what would
    make the file unusable (#148): specs whose FMP endpoint has been withdrawn
    and answers 404, deprecated specs, which are removed in 3.0 and warn on
    every server start, and one side of each tool-name collision, since
    ``alternative.crypto_quotes`` and ``batch.crypto_quotes`` both want to be
    advertised as ``crypto_quotes`` under the default name style and
    registration refuses the pair. Every exclusion is named in the file header
    and on stdout, under whichever of the three reasons applies -- a withdrawal
    beside the nearest live tool if there is one, a deprecation beside the
    replacement that ships in its place, a collision loser beside the
    ``FMP_MCP_TOOL_NAME_STYLE=spec`` setting that lets both sides coexist --
    so nothing is dropped silently.

    An explicit ``tools`` list is the caller's own selection and is never
    thinned: a collision inside it is reported on stderr and in the header
    instead.

    Parameters
    ----------
    output_path
        Path to save the manifest file
    tools
        List of tool specs to include (if None, includes the whole catalog)
    include_defaults
        Whether to include default tools
    """
    output_path = Path(output_path)

    # Get available tools
    available_tools = list_available_tools()
    available_specs = {tool["spec"] for tool in available_tools}

    excluded: list[str] = []
    deprecated: list[str] = []
    withdrawn: list[str] = []

    # Build tool list
    if tools is None:
        selected_tools = _startable_catalog(
            available_specs, excluded, deprecated, withdrawn
        )
    else:
        selected_tools = _validated_specs(tools)

    if include_defaults:
        _add_defaults(selected_tools, available_specs, excluded)

    # Anything left can only come from an explicitly requested pair.
    collisions = _name_collisions(selected_tools)
    if collisions:
        _warn_collisions(collisions)

    # Generate manifest content
    manifest_content = (
        _manifest_header(deprecated, excluded, collisions, withdrawn) + "\nTOOLS = [\n"
    )
    for tool in sorted(selected_tools):
        manifest_content += f'    "{tool}",\n'

    manifest_content += "]\n"

    # Save manifest
    output_path.write_text(manifest_content)
    print(f"Manifest saved to: {output_path}")
    print(f"Total tools: {len(selected_tools)}")
    _report_exclusions(withdrawn, deprecated, excluded)


def _report_exclusions(
    withdrawn: list[str],
    deprecated: list[str],
    excluded: list[str],
) -> None:
    """Print each exclusion category to stdout, with its reason.

    Extracted from :func:`generate_manifest` to keep it under the complexity
    limit; three near-identical blocks are also easier to keep in step here
    than inline.
    """
    for label, notes in (
        ("Omitted as withdrawn by FMP", withdrawn),
        ("Omitted as deprecated", deprecated),
        ("Excluded to keep the manifest startable", excluded),
    ):
        if not notes:
            continue
        print(f"{label}: {len(notes)}")
        for note in notes:
            print(f"  {note}")


def _classify_manifest_entries(
    entries: list[str],
) -> tuple[list[str], list[str], list[tuple[str, str]], list[tuple[str, str | None]]]:
    """Sort manifest entries into unknown, ambiguous, deprecated and withdrawn.

    An entry may be a bare key (``profile``) or a fully qualified spec
    (``company.profile``). Both forms are judged by
    :func:`fmp_data.mcp.tool_loader.resolve_tool_spec` -- the same pure
    function the loader resolves with -- so validation cannot bless a manifest
    that registration then refuses (#149). Resolution is pure, so looping over
    a manifest here announces nothing; only the registration path warns.

    Withdrawn is reported apart from deprecated, and bucketed on ``status``
    rather than on ``replacement is not None``: a withdrawal deliberately
    carries no ``replacement``, so the old truthiness test filed all 19 of
    them as healthy and ``validate`` blessed a manifest full of tools that can
    only answer empty.

    Returns
    -------
    tuple[list[str], list[str], list[tuple[str, str]], list[tuple[str, str | None]]]
        ``(unknown, ambiguous, deprecated, withdrawn)`` where ``ambiguous``
        entries are preformatted with their candidates, ``deprecated`` pairs
        the entry as written with the spec that replaces it, and ``withdrawn``
        pairs it with the nearest live spec or ``None`` when FMP publishes no
        replacement.
    """
    from fmp_data.mcp import tool_loader

    key_to_spec = tool_loader.build_key_to_spec(list_available_tools())

    unknown: list[str] = []
    ambiguous: list[str] = []
    deprecated: list[tuple[str, str]] = []
    withdrawn: list[tuple[str, str | None]] = []

    for entry in entries:
        resolution = tool_loader.resolve_tool_spec(entry, key_to_spec)
        if resolution.status is tool_loader.ResolutionStatus.UNKNOWN:
            unknown.append(entry)
        elif resolution.status is tool_loader.ResolutionStatus.AMBIGUOUS:
            candidates = ", ".join(resolution.candidates)
            ambiguous.append(f"{entry} (use one of: {candidates})")
        elif resolution.is_withdrawn:
            withdrawn.append((entry, resolution.successor))
        elif resolution.replacement is not None:
            deprecated.append((entry, resolution.replacement))

    return unknown, ambiguous, deprecated, withdrawn


def _manifest_name_clashes(
    entries: list[str],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Entries that would advertise one tool name twice, split by cause.

    A clash is a property of the manifest as a whole, so it cannot fall out
    of the per-entry classification above -- which is why ``validate`` was
    blind to it while ``generate`` was not. Entries are resolved first
    because a bare key and its qualified spec are the same tool:
    ``["profile", "company.profile"]`` fails at registration, and comparing
    the strings as written would miss it.

    Names are computed under the **effective** ``FMP_MCP_TOOL_NAME_STYLE``,
    not the default. Under ``spec`` the advertised name is the whole spec, so
    the two ``crypto_quotes`` tools no longer clash -- warning about them
    there would tell a user to set the variable they have already set.

    Returns
    -------
    tuple[dict[str, list[str]], dict[str, list[str]]]
        ``(duplicates, collisions)``, each advertised name to the entries as
        the user wrote them. The two need different advice: a duplicate is
        one tool listed twice, which no name style separates, while a
        collision is two genuinely different tools that ``spec`` style can
        serve at once.
    """
    from fmp_data.mcp import tool_loader

    key_to_spec = tool_loader.build_key_to_spec(list_available_tools())
    name_style = tool_loader._get_tool_name_style()

    resolved: list[tuple[str, str, str]] = []
    entries_by_spec: dict[str, list[str]] = {}
    for entry in entries:
        resolution = tool_loader.resolve_tool_spec(entry, key_to_spec)
        if resolution.spec is None or resolution.key is None:
            continue  # unknown or ambiguous; already reported as such
        resolved.append((resolution.spec, resolution.client or "", resolution.key))
        entries_by_spec.setdefault(resolution.spec, []).append(entry)

    # Grouping and the duplicate/collision split are the loader's, not a
    # parallel implementation: `_validate_tool_names` raises off exactly these
    # two dicts, so validate cannot report a clash the loader tolerates or
    # miss one it refuses (#162).
    by_name = tool_loader.advertised_names(resolved, name_style)
    dup_specs, coll_specs = tool_loader.split_name_clashes(by_name)

    def _as_written(specs: list[str]) -> list[str]:
        """Name each clashing spec by the entry the user actually typed.

        ``dict.fromkeys`` because a duplicate arrives as one spec repeated;
        the entries that produced it are already all in ``entries_by_spec``.
        """
        written: list[str] = []
        for spec in dict.fromkeys(specs):
            written.extend(entries_by_spec.get(spec, [spec]))
        return written

    duplicates = {name: _as_written(specs) for name, specs in dup_specs.items()}
    collisions = {name: _as_written(specs) for name, specs in coll_specs.items()}
    return duplicates, collisions


def _report_manifest_findings(
    unknown: list[str],
    ambiguous: list[str],
    deprecated: list[tuple[str, str]],
    withdrawn: list[tuple[str, str | None]] | None = None,
    duplicates: dict[str, list[str]] | None = None,
    collisions: dict[str, list[str]] | None = None,
) -> None:
    """Print what validation found.

    Reporting only. Which findings are fatal is
    :func:`validate_manifest`'s call, and it is made in exactly one place so
    the verdict cannot disagree with the text printed above it (#161).
    """
    if unknown:
        print(
            f"Warning: Unknown tools found: {', '.join(unknown)}. "
            "Run `fmp-mcp list` to see available tools.",
            file=sys.stderr,
        )

    if ambiguous:
        print(
            "Warning: bare keys claimed by more than one client, which fail to "
            f"resolve at registration: {'; '.join(ambiguous)}",
            file=sys.stderr,
        )

    # Registration refuses this under *every* name style since #162: one spec
    # listed twice is one spec listed twice however names are derived. The
    # advice deliberately does not mention FMP_MCP_TOOL_NAME_STYLE, which
    # cannot help and is useless to someone already on `spec`.
    for name, claims in sorted((duplicates or {}).items()):
        print(
            f"Warning: '{name}' is listed more than once ({', '.join(claims)}) "
            "-- these are the same tool. No tool-name style separates them; "
            "drop all but one.",
            file=sys.stderr,
        )

    for name, claims in sorted((collisions or {}).items()):
        print(
            f"Warning: '{name}' is claimed by two different tools "
            f"({', '.join(claims)}), which fails to register under the "
            "default FMP_MCP_TOOL_NAME_STYLE=key. Set "
            "FMP_MCP_TOOL_NAME_STYLE=spec to serve both, or drop one side.",
            file=sys.stderr,
        )

    # Deprecated is still valid -- it resolves today -- so this reports rather
    # than fails. It is the answer to "is my manifest future-proof?", which is
    # what someone running `validate` is asking.
    if deprecated:
        print(f"Deprecated tools found ({len(deprecated)}), removed in 3.0:")
        for entry, replacement in deprecated:
            print(f"  {entry} -> use {replacement}")

    # Reported apart from deprecated because the remedy differs: a deprecated
    # key is a rename and its replacement is a drop-in, while these name an
    # endpoint FMP stopped serving, so the tool registers and answers nothing.
    # Four of them have no successor at all, and saying "use X" would be a lie.
    if withdrawn:
        print(
            f"Withdrawn tools found ({len(withdrawn)}): FMP no longer serves "
            "these endpoints, so they answer with no data. Removed in 3.0:"
        )
        for entry, successor in withdrawn:
            remedy = (
                f"nearest live tool is {successor}, payload differs"
                if successor
                else "FMP publishes no replacement"
            )
            print(f"  {entry} -> {remedy}")


def validate_manifest(manifest_path: str | Path) -> bool:
    """
    Validate a manifest file for correctness.

    Parameters
    ----------
    manifest_path
        Path to the manifest file

    Returns
    -------
    bool
        True if valid, False otherwise
    """
    import importlib.util

    manifest_path = Path(manifest_path).expanduser().resolve()

    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return False

    # Try to import the manifest
    spec = importlib.util.spec_from_file_location("test_manifest", manifest_path)
    if spec is None or spec.loader is None:
        print(f"Error: Cannot import manifest: {manifest_path}", file=sys.stderr)
        return False

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading manifest: {e}", file=sys.stderr)
        return False

    tools = getattr(module, "TOOLS", None)
    if tools is None:
        print("Error: Manifest does not define TOOLS variable", file=sys.stderr)
        return False
    if not isinstance(tools, list):
        print("Error: TOOLS must be a list", file=sys.stderr)
        return False

    for tool in tools:
        if not isinstance(tool, str):
            print(f"Error: Tool spec must be string, got {type(tool)}", file=sys.stderr)
            return False

    unknown, ambiguous, deprecated, withdrawn = _classify_manifest_entries(tools)
    duplicates, collisions = _manifest_name_clashes(tools)
    _report_manifest_findings(
        unknown, ambiguous, deprecated, withdrawn, duplicates, collisions
    )

    # Exactly the four conditions under which `register_from_manifest` raises,
    # and nothing else (#161). Reporting a fatal finding and then printing
    # "Manifest is valid" with exit 0 turned a startup error into a trusted
    # green check -- the precise failure mode a validator exists to prevent.
    #
    # Deprecated and withdrawn stay reports: both resolve and register today,
    # so "is my manifest future-proof?" is a question you can ask without
    # failing your build.
    fatal = bool(unknown or ambiguous or duplicates or collisions)
    if fatal:
        print(
            f"Manifest is invalid: {_pluralise(len(tools), 'tool')} listed, but "
            "the findings above stop the server starting.",
            file=sys.stderr,
        )
        return False

    print(f"Manifest is valid with {_pluralise(len(tools), 'tool')}")
    return True


def serve_with_manifest(manifest_path: str | Path | None = None) -> None:
    """
    Start the MCP server with a specific manifest.

    Parameters
    ----------
    manifest_path
        Path to manifest file, or None for defaults
    """
    if not os.getenv("FMP_API_KEY"):
        print(
            "Error: FMP_API_KEY environment variable is required.\n"
            "Set it with: export FMP_API_KEY=your_api_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    from fmp_data.mcp.server import create_app

    if manifest_path:
        manifest_path = Path(manifest_path).expanduser().resolve()
        if not manifest_path.exists():
            print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
            sys.exit(1)

        print(f"Loading tools from: {manifest_path}")
        app = create_app(tools=str(manifest_path))
    else:
        print("Using default MCP tools configuration")
        app = create_app()

    print("Starting FMP Data MCP Server...")
    app.run()


# CLI command implementations
def setup_command(args: argparse.Namespace) -> int:
    """Run the setup wizard."""
    from fmp_data.mcp.setup import run_setup

    return run_setup(quiet=getattr(args, "quiet", False))


def status_command(args: argparse.Namespace) -> int:
    """Check MCP server status."""
    from fmp_data.mcp.utils import (
        check_claude_desktop_installed,
        get_api_key_from_env,
        get_claude_config_path,
        load_claude_config,
        test_mcp_server,
    )

    print("🔍 MCP Server Status")
    print("=" * 40)

    # Check Claude Desktop
    if check_claude_desktop_installed():
        print("✅ Claude Desktop is installed")
        config_path = get_claude_config_path()
        print(f"   Config path: {config_path}")

        # Check configuration
        config = load_claude_config()
        if "mcpServers" in config and "fmp-data" in config["mcpServers"]:
            print("✅ FMP Data server is configured")
            server_config = config["mcpServers"]["fmp-data"]
            print(f"   Python: {server_config.get('command', 'Not set')}")

            # Test server
            api_key = (
                server_config.get("env", {}).get("FMP_API_KEY")
                or get_api_key_from_env()
            )
            if api_key:
                print("🧪 Testing server connection...")
                success, message = test_mcp_server(api_key)
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
            else:
                print("⚠️  No API key configured")
        else:
            print("❌ FMP Data server not configured")
            print("   Run 'fmp-mcp setup' to configure")
    else:
        print("❌ Claude Desktop not detected")
        print("   Install from: https://claude.ai/download")

    return 0


def test_command(args: argparse.Namespace) -> int:
    """Test MCP server."""
    from fmp_data.mcp.utils import get_api_key_from_env, test_mcp_server

    print("🧪 Testing MCP Server")
    print("=" * 40)

    # Get API key
    api_key = get_api_key_from_env()
    if not api_key:
        print("❌ FMP_API_KEY not set in environment")
        print("   Set with: export FMP_API_KEY=your_key_here")
        return 1

    # Test server
    success, message = test_mcp_server(api_key)
    if success:
        print(f"✅ {message}")

        # Try to get tool count
        try:
            from fmp_data.mcp.server import create_app

            app = create_app()
            tool_manager = getattr(app, "_tool_manager", None)
            tool_count = len(tool_manager._tools) if tool_manager else 0
            print(f"✅ {tool_count} tools registered")
        except Exception as e:
            print(f"⚠️  Could not count tools: {e}")

        return 0
    else:
        print(f"❌ {message}")
        return 1


# CLI entry points for potential future integration with click/argparse
def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="fmp-mcp",
        description=(
            "FMP Data MCP Server CLI - Manage MCP server for Claude Desktop integration"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command (NEW)
    setup_parser = subparsers.add_parser(
        "setup", help="Setup MCP server for Claude Desktop (interactive wizard)"
    )
    setup_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Run in quiet mode with minimal output",
    )

    # Status command (NEW)
    subparsers.add_parser("status", help="Check MCP server configuration status")

    # Test command (NEW)
    subparsers.add_parser("test", help="Test MCP server connection")

    # List tools command
    list_parser = subparsers.add_parser("list", help="List available MCP tools")
    list_parser.add_argument(
        "--format",
        choices=["table", "json", "list", "tree"],
        default="table",
        help="Output format",
    )
    list_parser.add_argument(
        "--client",
        help="Filter tools by client module (e.g., company, market, technical)",
    )

    # Generate manifest command
    gen_parser = subparsers.add_parser("generate", help="Generate manifest file")
    gen_parser.add_argument("output", help="Output file path")
    gen_parser.add_argument("--tools", nargs="+", help="Specific tools to include")
    gen_parser.add_argument(
        "--no-defaults", action="store_true", help="Exclude default tools"
    )

    # Validate manifest command
    val_parser = subparsers.add_parser("validate", help="Validate manifest file")
    val_parser.add_argument("manifest", help="Manifest file path")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--manifest", help="Custom manifest file path")

    args = parser.parse_args()

    # Handle new commands
    if args.command == "setup":
        sys.exit(setup_command(args))

    elif args.command == "status":
        sys.exit(status_command(args))

    elif args.command == "test":
        sys.exit(test_command(args))

    elif args.command == "list":
        tools = list_available_tools()

        # Apply client filter if specified
        client_filter = getattr(args, "client", None)
        if client_filter:
            tools = [t for t in tools if t["client"] == client_filter]
            if not tools:
                print(f"No tools found for client: {client_filter}")
                sys.exit(1)

        print_tools_table(tools, args.format)

    elif args.command == "generate":
        generate_manifest(args.output, args.tools, not args.no_defaults)

    elif args.command == "validate":
        valid = validate_manifest(args.manifest)
        sys.exit(0 if valid else 1)

    elif args.command == "serve":
        serve_with_manifest(args.manifest)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
