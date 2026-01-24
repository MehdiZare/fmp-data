# fmp_data/mcp/tool_loader.py
from __future__ import annotations

from collections.abc import Callable
import importlib
import inspect
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

from fmp_data.client import FMPDataClient

ERR = RuntimeError  # shorten


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


def _build_key_to_spec(all_tools: list[dict[str, str]]) -> dict[str, list[str]]:
    key_to_spec: dict[str, list[str]] = {}
    for tool in all_tools:
        key = tool["key"]
        spec = tool["spec"]
        if key not in key_to_spec:
            key_to_spec[key] = []
        key_to_spec[key].append(spec)
    return key_to_spec


def _resolve_tool_spec(
    spec: str, key_to_spec: dict[str, list[str]]
) -> tuple[str, str, str]:
    if "." in spec:
        # Full format: "<client>.<semantics_key>"
        try:
            client_slug, sem_key = spec.split(".", 1)
        except ValueError:
            raise ERR(f"'{spec}' is not in '<client>.<endpoint>' format") from None
        return spec, client_slug, sem_key

    if spec not in key_to_spec:
        raise ERR(f"Tool key '{spec}' not found in available tools") from None

    specs_for_key = key_to_spec[spec]
    if len(specs_for_key) > 1:
        specs_list = ", ".join(sorted(specs_for_key))
        raise ERR(
            f"Tool key '{spec}' is ambiguous; matches multiple tools: {specs_list}"
        ) from None

    full_spec = specs_for_key[0]
    client_slug, sem_key = full_spec.split(".", 1)
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
    mcp: FastMCP,
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
    key_to_spec = _build_key_to_spec(all_tools)

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
