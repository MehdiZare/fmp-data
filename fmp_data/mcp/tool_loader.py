# fmp_data/mcp/tool_loader.py
from __future__ import annotations

from collections.abc import Callable
import importlib
import inspect
from typing import Any

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
    if not hasattr(mapping_mod, table_name):
        raise ERR(f"'{mod_path}' lacks {table_name}")
    table = getattr(mapping_mod, table_name)

    if key not in table:
        raise ERR(f"Endpoint semantics '{key}' not found in {table_name}")
    return table[key]  # EndpointSemantics instance


def register_from_manifest(
    mcp: FastMCP,
    fmp_client: FMPDataClient,
    tool_specs: list[str],
) -> None:
    """
    Register tools declared in a list of "<client>.<semantics_key>" strings.

    Raises:
        RuntimeError: on any lookup / validation failure.
    """
    for spec in tool_specs:
        try:
            client_slug, sem_key = spec.split(".", 1)
        except ValueError:
            raise ERR(f"'{spec}' is not in '<client>.<endpoint>' format") from None

        sem = _load_semantics(client_slug, sem_key)

        # dotted path to real method on the live client object
        dotted_method = f"{client_slug}.{sem.method_name}"
        func = _resolve_attr(fmp_client, dotted_method)

        # Build description - fall back to callable docstring if required
        description = sem.natural_description or inspect.getdoc(func) or ""

        # Attach as MCP tool
        mcp.add_tool(
            func,
            name=sem_key,  # tool name shown to LLM
            description=description,
        )
