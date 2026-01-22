# FMP Data MCP Server for Claude Desktop

Connect the FMP Data MCP server to Claude Desktop to enable real-time financial data queries.

## Prerequisites

- Claude Desktop App: https://claude.ai/download
- Python 3.10-3.14: https://www.python.org/downloads/
- FMP API key: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi

## Quick Setup (Recommended)

```bash
pip install "fmp-data[mcp]"
fmp-mcp setup
```

The setup wizard:
- Checks prerequisites
- Configures your FMP API key
- Lets you pick a configuration profile
- Updates your Claude Desktop config
- Tests the MCP server connection

Restart Claude Desktop after setup.

## Manual Setup

### Step 1: Install
```bash
pip install "fmp-data[mcp]"
```

### Step 2: Set your API key

Mac/Linux:
```bash
export FMP_API_KEY="your_api_key_here"  # pragma: allowlist secret
```

Windows:
```cmd
set FMP_API_KEY=your_api_key_here  # pragma: allowlist secret
```

### Step 3: Configure Claude Desktop

Config location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Create or update the file:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  // pragma: allowlist secret
      }
    }
  }
}
```

If you need a specific Python path, run `which python` (macOS/Linux) or
`where python` (Windows) and use that in `command`.

### Step 4: Verify
1. Restart Claude Desktop (quit completely and reopen).
2. Start a new conversation.
3. Ask: "What's the current price of AAPL?"

## CLI Commands

```bash
fmp-mcp setup
fmp-mcp status
fmp-mcp test
fmp-mcp list
fmp-mcp list --client market
fmp-mcp generate custom.py --tools company.profile company.quote
fmp-mcp validate custom.py
fmp-mcp serve --manifest custom.py
```

## Example Prompts

- "Show me Apple's company profile"
- "What's the current price of Tesla stock?"
- "Show me today's top gainers"
- "Calculate the RSI for MSFT"
- "What's the current Bitcoin price?"

## Custom Tool Manifests

To use a predefined or custom tool set, set `FMP_MCP_MANIFEST`:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here",  // pragma: allowlist secret
        "FMP_MCP_MANIFEST": "examples/mcp_configurations/trading_manifest.py"
      }
    }
  }
}
```

Use an absolute path for `FMP_MCP_MANIFEST` in the Claude Desktop config.

See [Configuration Profiles](configurations.md) for profiles and custom manifests.

## Troubleshooting

See [Troubleshooting](troubleshooting.md).

## Next Steps

- Configuration profiles: [Configuration Profiles](configurations.md)
- Tools reference: [Tools Reference](tools.md)
