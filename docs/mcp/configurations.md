# MCP Configuration Examples

Example MCP (Model Context Protocol) manifests live in `examples/mcp_configurations/`.
Use them to scope which tools are exposed to Claude or other MCP clients. If you
installed from PyPI, copy the manifests from the repo or create your own.

## Quick Setup

For guided setup, run:
```bash
pip install "fmp-data[mcp]"
fmp-mcp setup
```

See [Claude Desktop Setup](claude_desktop.md) for full setup instructions.

## Available Configurations

### Default (no manifest)
Uses the full tool set. Do not set `FMP_MCP_MANIFEST`.

### `minimal_manifest.py`
The smallest useful configuration with just essential tools:
- Company profiles and quotes
- Basic market data
- Cryptocurrency support

**Use case:** Testing, development, or lightweight deployments

### `trading_manifest.py`
Optimized for active trading and technical analysis:
- Real-time quotes and market movers
- Technical indicators (SMA, RSI, MACD, etc.)
- Pre/post market data
- Price targets and news

**Use case:** Day trading, swing trading, technical analysis

### `research_manifest.py`
Comprehensive tools for fundamental analysis:
- Complete financial statements
- Key metrics and ratios
- Analyst recommendations
- Institutional holdings
- Economic indicators

**Use case:** Investment research, due diligence, long-term investing

### `crypto_manifest.py`
Specialized for cryptocurrency markets:
- Crypto quotes and historical data
- Intraday crypto prices
- Crypto news
- Technical indicators for crypto

**Use case:** Cryptocurrency trading and analysis

## Usage

### Quick Setup with CLI (Recommended)
```bash
# Setup wizard for Claude Desktop
fmp-mcp setup

# Check server status
fmp-mcp status

# Test server connection
fmp-mcp test

# List available tools
fmp-mcp list

# List tools for specific client
fmp-mcp list --client market
```

### Manual Configuration

#### Using with Python module execution
```bash
export FMP_API_KEY=your_api_key_here  # pragma: allowlist secret
export FMP_MCP_MANIFEST=examples/mcp_configurations/trading_manifest.py
python -m fmp_data.mcp
```

#### Using with MCP CLI
```bash
FMP_API_KEY=your_api_key mcp dev python -c "
from fmp_data.mcp.server import create_app
app = create_app("examples/mcp_configurations/research_manifest.py")
app.run()
"
```

#### Using in your own code
```python
from fmp_data.mcp.server import create_app

# Load a specific configuration
app = create_app(tools="examples/mcp_configurations/minimal_manifest.py")
app.run()
```

## Creating Custom Configurations

You can create your own manifest by:

1. **Manual creation** - Copy one of these examples and modify:
```python
# my_custom_manifest.py
TOOLS = [
    "company.profile",
    "market.quote",
    # Add your desired tools here
]
```

2. **Using the CLI tool** - Generate a manifest with specific tools:
```bash
# Generate manifest with specific tools
fmp-mcp generate my_manifest.py --tools company.profile market.quote

# Generate manifest without default tools
fmp-mcp generate my_manifest.py --no-defaults --tools market.quote market.movers
```

3. **Discovering available tools** - List all available tools:
```bash
# List all tools in table format
fmp-mcp list

# List as tree structure
fmp-mcp list --format tree

# Filter by client module
fmp-mcp list --client technical

# Export as JSON
fmp-mcp list --format json > tools.json
```

## Validation

Validate your manifest file before using:
```bash
fmp-mcp validate my_manifest.py
```

## Tips

- Start with `minimal_manifest.py` and add tools as needed
- Group related tools together with comments
- Test your configuration with a simple query before deployment
- Consider API rate limits when selecting tools
- Use `research_manifest.py` for comprehensive analysis
- Use `trading_manifest.py` for real-time market monitoring
