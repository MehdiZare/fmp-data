"""
MCP Server Module Execution

This module allows running the MCP server directly using:
    python -m fmp_data.mcp

Environment Variables:
    FMP_API_KEY: Required FMP API key for accessing financial data
    FMP_MCP_MANIFEST: Optional path to custom manifest file with tool definitions
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

try:
    import mcp.server.fastmcp  # noqa: F401
except ImportError:
    print(
        "Error: MCP dependencies not installed.\n"
        "Please install with: uv pip install 'fmp-data[mcp]'",
        file=sys.stderr,
    )
    sys.exit(1)

from fmp_data.mcp.server import create_app


def main() -> None:
    """Run the MCP server with configured tools."""
    # Check for API key
    if not os.getenv("FMP_API_KEY"):
        print(
            "Error: FMP_API_KEY environment variable is required.\n"
            "Set it with: export FMP_API_KEY=your_api_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check for custom manifest
    manifest_path_str = os.getenv("FMP_MCP_MANIFEST")
    if manifest_path_str:
        manifest_path = Path(manifest_path_str).expanduser().resolve()
        if not manifest_path.exists():
            print(
                f"Error: Manifest file not found: {manifest_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Loading tools from: {manifest_path}")
        app = create_app(tools=str(manifest_path))
    else:
        print("Using default MCP tools configuration")
        app = create_app()

    print("Starting FMP Data MCP Server...")

    # Run the server
    app.run()


if __name__ == "__main__":
    main()
