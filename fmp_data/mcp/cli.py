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
            desc = tool["description"][:60]
            branch.add(
                f"[green]{tool['method']}[/green]{_deprecation_note(tool)}: {desc}..."
            )

    console.print(tree)


def _print_tools_table_format(tools: list[dict[str, Any]]) -> None:
    """Print tools in table format."""
    if HAS_RICH:
        _print_rich_table(tools)
    else:
        _print_simple_table(tools)


def _print_rich_table(tools: list[dict[str, Any]]) -> None:
    """Print tools using rich table."""
    console = Console()
    table = Table(title="Available FMP MCP Tools")
    table.add_column("Tool Spec", style="cyan")
    table.add_column("Client", style="green")
    table.add_column("Method", style="yellow")
    table.add_column("Description", style="white")

    for tool in tools:
        table.add_row(
            tool["spec"] + _deprecation_note(tool),
            tool["client"],
            tool["method"],
            (
                tool["description"][:50] + "..."
                if len(tool["description"]) > 50
                else tool["description"]
            ),
        )

    console.print(table)


def _print_simple_table(tools: list[dict[str, Any]]) -> None:
    """Print tools using simple table format."""
    print("\nAvailable FMP MCP Tools")
    print("-" * 80)
    print(f"{'Tool Spec':<30} {'Client':<12} {'Method':<25}")
    print("-" * 80)
    for tool in tools:
        spec = tool["spec"] + _deprecation_note(tool)
        print(f"{spec:<30} {tool['client']:<12} {tool['method']:<25}")


def generate_manifest(
    output_path: str | Path,
    tools: list[str] | None = None,
    include_defaults: bool = True,
) -> None:
    """
    Generate a custom manifest file with selected tools.

    Parameters
    ----------
    output_path
        Path to save the manifest file
    tools
        List of tool specs to include (if None, includes all)
    include_defaults
        Whether to include default tools
    """
    output_path = Path(output_path)

    # Get available tools
    available_tools = list_available_tools()
    available_specs = {tool["spec"] for tool in available_tools}

    # Build tool list
    if tools is None:
        # Include all available tools
        selected_tools = list(available_specs)
    else:
        # Validate provided tools
        selected_tools = []
        for tool in tools:
            if tool not in available_specs:
                print(f"Warning: Unknown tool '{tool}', skipping", file=sys.stderr)
            else:
                selected_tools.append(tool)

    if include_defaults:
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        # Add defaults if not already present
        for tool in DEFAULT_TOOLS:
            if tool not in selected_tools and tool in available_specs:
                selected_tools.append(tool)

    # Generate manifest content
    manifest_content = '''"""
Custom MCP Tools Manifest

Generated by fmp-data MCP CLI
"""

TOOLS = [
'''
    for tool in sorted(selected_tools):
        manifest_content += f'    "{tool}",\n'

    manifest_content += "]"

    # Save manifest
    output_path.write_text(manifest_content)
    print(f"Manifest saved to: {output_path}")
    print(f"Total tools: {len(selected_tools)}")


def _classify_manifest_entries(
    entries: list[str],
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Sort manifest entries into unknown, ambiguous and deprecated.

    An entry may be a bare key (``profile``) or a fully qualified spec
    (``company.profile``), so each one is resolved the same way the loader
    resolves it before being judged.

    Returns
    -------
    tuple[list[str], list[str], list[tuple[str, str]]]
        ``(unknown, ambiguous, deprecated)`` where ``ambiguous`` entries are
        preformatted with their candidates and ``deprecated`` pairs the entry
        as written with the spec that replaces it.
    """
    available_tools = list_available_tools()
    available_specs = {tool["spec"] for tool in available_tools}
    replacement_by_spec = {tool["spec"]: tool["deprecated"] for tool in available_tools}
    specs_by_key: dict[str, list[str]] = {}
    for tool in available_tools:
        specs_by_key.setdefault(tool["key"], []).append(tool["spec"])

    unknown: list[str] = []
    ambiguous: list[str] = []
    deprecated: list[tuple[str, str]] = []

    for entry in entries:
        if entry in available_specs:
            resolved = entry
        else:
            candidates = sorted(specs_by_key.get(entry, []))
            if not candidates:
                unknown.append(entry)
                continue
            if len(candidates) > 1:
                ambiguous.append(f"{entry} (use one of: {', '.join(candidates)})")
                continue
            resolved = candidates[0]

        replacement = replacement_by_spec.get(resolved)
        if replacement:
            deprecated.append((entry, replacement))

    return unknown, ambiguous, deprecated


def _report_manifest_findings(
    unknown: list[str],
    ambiguous: list[str],
    deprecated: list[tuple[str, str]],
) -> None:
    """Print what validation found. None of it is fatal on its own."""
    if unknown:
        print(f"Warning: Unknown tools found: {', '.join(unknown)}", file=sys.stderr)

    if ambiguous:
        print(
            "Warning: bare keys claimed by more than one client, which fail to "
            f"resolve at registration: {'; '.join(ambiguous)}",
            file=sys.stderr,
        )

    # Deprecated is still valid -- it resolves today -- so this reports rather
    # than fails. It is the answer to "is my manifest future-proof?", which is
    # what someone running `validate` is asking.
    if deprecated:
        print(f"Deprecated tools found ({len(deprecated)}), removed in 3.0:")
        for entry, replacement in deprecated:
            print(f"  {entry} -> use {replacement}")


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

    _report_manifest_findings(*_classify_manifest_entries(tools))

    print(f"Manifest is valid with {len(tools)} tools")
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
