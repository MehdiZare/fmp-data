# FMP Data MCP Server Setup Guide

This guide will walk you through setting up the FMP Data MCP server for use with Claude Desktop application.

## Prerequisites

- Python 3.10 or higher
- Claude Desktop application installed
- FMP API key (get a free one at [Financial Modeling Prep](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi))

## Quick Setup (Recommended)

The easiest way to set up the MCP server is using our interactive setup wizard:

```bash
# Install the package with MCP support
pip install fmp-data[mcp]

# Run the setup wizard
fmp-mcp setup
```

The setup wizard will:
1. ✅ Check all prerequisites
2. 🔑 Configure your FMP API key
3. ⚙️ Let you choose a configuration profile
4. 🐍 Find the correct Python executable
5. 📝 Update Claude Desktop configuration
6. 🧪 Test the server connection

After setup, restart Claude Desktop and you're ready to go!

## Manual Setup

If you prefer to configure manually:

### Step 1: Install the Package

```bash
pip install fmp-data[mcp]
```

### Step 2: Set Your API Key

```bash
export FMP_API_KEY=your_api_key_here  # pragma: allowlist secret
```

### Step 3: Find Claude Configuration File

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 4: Add MCP Server Configuration

Edit the configuration file and add:

```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "/path/to/python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret
      }
    }
  }
}
```

Replace `/path/to/python` with your Python executable path (use `which python` or `where python` to find it).

### Step 5: Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

## Configuration Profiles

FMP Data comes with several pre-configured profiles:

| Profile | Tools | Use Case |
|---------|-------|----------|
| **Default** | 130 tools | Complete toolkit for all use cases |
| **Minimal** | 8 tools | Essential tools for basic queries |
| **Trading** | 25 tools | Real-time quotes, technical indicators |
| **Research** | 38 tools | Financial statements, fundamental analysis |
| **Crypto** | 14 tools | Cryptocurrency focused tools |

To use a specific profile during manual setup, set the `FMP_MCP_MANIFEST` environment variable.

**Note:** Replace `your_api_key_here` with your actual FMP API key.

```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "/path/to/python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here",
        "FMP_MCP_MANIFEST": "/path/to/fmp-data/examples/mcp_configurations/trading_manifest.py"
      }
    }
  }
}
```

## CLI Commands

Once installed, you can use the `fmp-mcp` command:

```bash
# Run setup wizard
fmp-mcp setup

# Check server status
fmp-mcp status

# Test server connection
fmp-mcp test

# List available tools
fmp-mcp list

# List tools in tree format
fmp-mcp list --format tree

# Filter tools by client
fmp-mcp list --client market

# Generate custom manifest
fmp-mcp generate custom.py --tools company.profile market.quote

# Validate a manifest
fmp-mcp validate custom.py

# Start server with custom manifest
fmp-mcp serve --manifest custom.py
```

## Testing Your Setup

After configuration, test in Claude Desktop:

1. Start a new conversation
2. Ask: "What's the current price of AAPL?"
3. Claude should use the FMP Data tools to fetch real-time data

### Example Queries to Try

- **Market Data**: "Show me today's top gainers"
- **Company Info**: "Get Tesla's company profile"
- **Financials**: "Show me Apple's latest income statement"
- **Technical**: "What's the RSI for Microsoft?"
- **Crypto**: "Get Bitcoin's current price"
- **News**: "Show me recent news for NVDA"

## Troubleshooting

### Server Not Showing in Claude

1. Check configuration file syntax (valid JSON)
2. Verify Python path is correct
3. Ensure Claude Desktop was fully restarted
4. Run `fmp-mcp status` to check configuration

### API Key Issues

1. Verify your API key is valid: `fmp-mcp test`
2. Check environment variable: `echo $FMP_API_KEY`
3. Ensure API key is in the config file

### Python Import Errors

1. Ensure MCP dependencies are installed: `pip install fmp-data[mcp]`
2. Use the full path to Python in your virtual environment
3. Test with: `python -m fmp_data.mcp` in terminal

### Tools Not Working

1. Check which tools are available: `fmp-mcp list`
2. Verify your configuration profile has the needed tools
3. Check API tier limitations for certain endpoints

## Advanced Usage

### Creating Custom Tool Sets

Create your own manifest file:

```python
# my_tools.py
TOOLS = [
    "company.profile",
    "company.quote",
    "market.movers",
    "technical.rsi",
    # Add more tools as needed
]
```

Then use it:

```bash
fmp-mcp serve --manifest my_tools.py
```

### Programmatic Usage

Use the MCP server in your own Python code:

```python
from fmp_data.mcp.server import create_app

# Create server with default tools
app = create_app()

# Or with custom manifest
app = create_app(tools="path/to/manifest.py")

# Run the server
app.run()
```

## Support

- **Documentation**: [GitHub Repository](https://github.com/MehdiZare/fmp-data)
- **Issues**: [GitHub Issues](https://github.com/MehdiZare/fmp-data/issues)
- **API Documentation**: [FMP API Docs](https://site.financialmodelingprep.com/developer/docs)

## Security Notes

- Never commit your API key to version control
- Use environment variables for sensitive data
- The API key is only accessible to the MCP server process
- Consider using read-only API keys for additional security

## Rate Limits

Be aware of FMP API rate limits based on your plan:
- Free: 250 requests/day
- Basic: Higher limits
- Professional: Even higher limits
- Enterprise: Custom limits

The MCP server includes rate limiting to help stay within your tier's limits.
