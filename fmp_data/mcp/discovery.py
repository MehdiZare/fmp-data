"""
MCP Tool Discovery Utilities

This module provides functionality to discover and enumerate all available
MCP tools from the endpoint semantics defined across all client modules.
"""

from __future__ import annotations

from functools import lru_cache
import importlib
from pathlib import Path
import pkgutil
from typing import Any


@lru_cache(maxsize=1)
def _get_client_modules() -> list[str]:
    """
    Discover client modules that expose MCP semantics mappings.

    Returns
    -------
    list[str]
        Sorted list of client module names.
    """
    import fmp_data

    package_path = Path(fmp_data.__file__).resolve().parent
    modules: list[str] = []

    for module_info in pkgutil.iter_modules([str(package_path)]):
        if not module_info.ispkg:
            continue
        name = module_info.name
        if name in {"lc", "mcp"}:
            continue
        if not (package_path / name / "mapping.py").exists():
            continue
        modules.append(name)

    return sorted(modules)


def discover_client_tools(client_name: str) -> list[dict[str, Any]]:
    """
    Discover all available tools for a specific client module.

    Parameters
    ----------
    client_name
        Name of the client module (e.g., "company", "market")

    Returns
    -------
    list[dict[str, Any]]
        List of tool definitions with metadata
    """
    tools: list[dict[str, Any]] = []

    try:
        # Import the mapping module for this client
        mapping_module = importlib.import_module(f"fmp_data.{client_name}.mapping")

        # Get the semantics table
        semantics_table_name = f"{client_name.upper()}_ENDPOINTS_SEMANTICS"

        semantics_table = getattr(mapping_module, semantics_table_name, None)
        if semantics_table is None:
            return tools

    except (ImportError, AttributeError):
        # Module doesn't exist or doesn't have semantics
        return tools

    # Process each item in the semantics table
    for key, semantics in semantics_table.items():
        try:
            tool_spec = f"{client_name}.{key}"

            # Extract description safely
            description = getattr(semantics, "natural_description", None)
            if not description:
                description = getattr(semantics, "description", "")

            # Extract method name safely
            method_name = getattr(semantics, "method_name", "<unknown>")

            tools.append(
                {
                    "spec": tool_spec,
                    "client": client_name,
                    "method": method_name,
                    "key": key,
                    "description": description,
                    "example_queries": getattr(semantics, "example_queries", []),
                    "related_terms": getattr(semantics, "related_terms", []),
                }
            )

        except AttributeError:
            # Skip malformed semantics entries
            continue

    return tools


def discover_all_tools() -> list[dict[str, Any]]:
    """
    Discover all available MCP tools across all client modules.

    Returns
    -------
    list[dict[str, Any]]
        Complete list of all available tool definitions
    """
    all_tools = []

    for client_name in _get_client_modules():
        client_tools = discover_client_tools(client_name)
        all_tools.extend(client_tools)

    # Sort by spec for consistent ordering
    all_tools.sort(key=lambda x: x["spec"])

    return all_tools


def get_tool_by_spec(spec: str) -> dict[str, Any] | None:
    """
    Get detailed information about a specific tool.

    Parameters
    ----------
    spec
        Tool specification in format "client.method"

    Returns
    -------
    dict[str, Any] | None
        Tool definition or None if not found
    """
    try:
        client_name, _ = spec.split(".", 1)
    except ValueError:
        return None

    if client_name not in _get_client_modules():
        return None

    tools = discover_client_tools(client_name)

    for tool in tools:
        if tool["spec"] == spec:
            return tool

    return None


def get_tools_by_client(client_name: str) -> list[dict[str, Any]]:
    """
    Get all tools for a specific client.

    Parameters
    ----------
    client_name
        Name of the client module

    Returns
    -------
    list[dict[str, Any]]
        List of tools for the specified client
    """
    if client_name not in _get_client_modules():
        return []

    return discover_client_tools(client_name)


def search_tools(query: str) -> list[dict[str, Any]]:
    """
    Search for tools matching a query string.

    Parameters
    ----------
    query
        Search query (case-insensitive)

    Returns
    -------
    list[dict[str, Any]]
        List of matching tools
    """
    query_lower = query.lower()
    all_tools = discover_all_tools()
    matching_tools = []

    for tool in all_tools:
        # Check if query matches in various fields
        if (
            query_lower in tool["spec"].lower()
            or query_lower in tool["description"].lower()
            or any(query_lower in q.lower() for q in tool.get("example_queries", []))
            or any(query_lower in t.lower() for t in tool.get("related_terms", []))
        ):
            matching_tools.append(tool)

    return matching_tools


def get_recommended_tools() -> list[str]:
    """
    Get a list of recommended/commonly-used tool specs.

    Returns
    -------
    list[str]
        List of recommended tool specifications
    """
    # These are the most commonly used endpoints
    recommended = [
        # Company data
        "company.profile",
        "company.market_cap",
        "company.quote",
        "company.historical_price",
        # Market data
        "market.gainers",
        "market.losers",
        "market.most_active",
        "market.sector_performance",
        "market.search",
        # Fundamental data
        "fundamental.income_statement",
        "fundamental.balance_sheet",
        "fundamental.cash_flow",
        "fundamental.key_metrics",
        # Alternative data
        "alternative.crypto_quote",
        "alternative.forex_quote",
        "alternative.commodities_quotes",
        # Intelligence
        "intelligence.stock_news",
        "intelligence.earnings_calendar",
        # Technical indicators
        "technical.sma",
        "technical.rsi",
        "technical.ema",
        # Economics
        "economics.treasury_rates",
        "economics.economic_calendar",
    ]

    # Filter to only include tools that actually exist
    all_tools = discover_all_tools()
    available_specs = {tool["spec"] for tool in all_tools}

    return [spec for spec in recommended if spec in available_specs]


def group_tools_by_category() -> dict[str, list[dict[str, Any]]]:
    """
    Group all tools by their client category.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        Dictionary mapping client names to their tools
    """
    all_tools = discover_all_tools()
    grouped: dict[str, list[dict[str, Any]]] = {}

    for tool in all_tools:
        client = tool["client"]
        if client not in grouped:
            grouped[client] = []
        grouped[client].append(tool)

    return grouped


def export_tools_json() -> str:
    """
    Export all tools as a JSON string.

    Returns
    -------
    str
        JSON representation of all tools
    """
    import json

    all_tools = discover_all_tools()
    return json.dumps(all_tools, indent=2)


def export_tools_yaml() -> str:
    """
    Export all tools as a YAML string.

    Returns
    -------
    str
        YAML representation of all tools
    """
    try:
        import yaml

        all_tools = discover_all_tools()
        result = yaml.dump(all_tools, default_flow_style=False)
        return result if isinstance(result, str) else str(result)
    except ImportError:
        return "# YAML export requires PyYAML: uv pip install pyyaml\n"
