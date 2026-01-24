"""
MCP Server Example - Custom tool selection.

IMPORTANT: This example requires MCP dependencies to be installed:
    pip install fmp-data[mcp]
    # or with uv:
    uv pip install fmp-data[mcp]

For detailed setup instructions, see: examples/mcp/setup_guide.md
"""

import os

from fmp_data.mcp.server import create_app
from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

os.environ["FMP_API_KEY"] = "your_api_key"  # pragma: allowlist secret

TOOLS = [
    *DEFAULT_TOOLS,
    "company.employee_count",  # shows workforce history
    "alternative.commodities_quotes",  # live commodity prices
]

app = create_app(TOOLS)

if __name__ == "__main__":
    app.run()

# run it with this
# FMP_API_KEY=my_api_key mcp dev examples/mcp_server.py
