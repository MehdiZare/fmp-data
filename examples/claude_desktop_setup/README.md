# FMP Data MCP Server for Claude Desktop

This guide will help you connect the FMP Data MCP server to Claude Desktop app, giving Claude access to real-time financial market data.

## Prerequisites

Before starting, you'll need:
1. **Claude Desktop App** - [Download here](https://claude.ai/download)
2. **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
3. **FMP API Key** - [Get a free key here](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi)

## Step 1: Install FMP Data Package

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
pip install "fmp-data[mcp]"
```

## Step 2: Set Up Your FMP API Key

### On Mac/Linux:
```bash
export FMP_API_KEY="your_api_key_here"  # pragma: allowlist secret
```

### On Windows:
```cmd
set FMP_API_KEY=your_api_key_here  # pragma: allowlist secret
```

Replace `your_api_key_here` with your actual FMP API key.

## Step 3: Configure Claude Desktop

Claude Desktop looks for MCP server configurations in a specific location:

### Mac Configuration
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows Configuration
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux Configuration
Location: `~/.config/Claude/claude_desktop_config.json`

Create or edit this file with the following content:

```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret
      }
    }
  }
}
```

**Important**: Replace `your_api_key_here` with your actual FMP API key.

## Step 4: Verify Installation

1. Restart Claude Desktop app (quit completely and reopen)
2. Start a new conversation
3. Ask Claude: "Can you check the current price of Apple stock (AAPL)?"

If everything is set up correctly, Claude will use the FMP MCP server to fetch real-time data.

## Available Commands

Once connected, you can ask Claude questions like:

### Company Information
- "What's the current price of Tesla stock?"
- "Show me Apple's company profile"
- "What's Microsoft's market cap?"
- "Who are the executives at Amazon?"

### Market Data
- "What are today's top gainers in the stock market?"
- "Show me the most active stocks today"
- "What's the performance of different sectors?"

### Financial Statements
- "Show me Apple's latest income statement"
- "What's Tesla's cash flow situation?"
- "Display Microsoft's balance sheet"

### Technical Analysis
- "Calculate the 20-day SMA for AAPL"
- "What's the RSI for Tesla?"
- "Show me the MACD for SPY"

### Alternative Markets
- "What's the current Bitcoin price?"
- "Show me the EUR/USD exchange rate"
- "What's the price of gold?"

### Market Intelligence
- "What's the latest news about Tesla?"
- "Show me upcoming earnings dates"
- "What are analysts saying about Apple?"

## Custom Configuration (Optional)

If you want to customize which tools are available, you can use a custom manifest:

1. Create a file called `my_tools.py`:

```python
# my_tools.py
TOOLS = [
    # Essential tools
    "company.profile",
    "company.quote",
    "market.quote",

    # Add more tools as needed
    "fundamental.income_statement",
    "intelligence.stock_news",
    "alternative.crypto_quote",
]
```

2. Update your Claude Desktop config to use the custom manifest:

```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret,
        "FMP_MCP_MANIFEST": "/path/to/my_tools.py"
      }
    }
  }
}
```

## Troubleshooting

### Claude doesn't respond with financial data
1. **Check API Key**: Ensure your FMP API key is valid and correctly set
2. **Restart Claude**: Completely quit and restart Claude Desktop
3. **Check Python**: Ensure Python is installed and accessible from terminal
4. **Verify Installation**: Run `pip show fmp-data` to confirm installation

### "MCP server not found" error
1. Ensure the config file is in the correct location
2. Check that the JSON format is valid (no missing commas or quotes)
3. Make sure Python path is correct (use `which python` or `where python`)

### Rate limit errors
- Free FMP accounts have limited API calls
- Consider upgrading your FMP plan for more requests
- Space out your queries to avoid hitting limits

### Testing the server independently
You can test if the MCP server works before connecting to Claude:

```bash
# Set your API key
export FMP_API_KEY="your_api_key_here"  # pragma: allowlist secret

# Test the server
python -m fmp_data.mcp
```

If you see "Starting FMP Data MCP Server..." without errors, the server is working correctly.

## Advanced Usage

### Using Different Tool Sets

We provide pre-configured tool sets for different use cases:

#### For Trading and Technical Analysis:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret,
        "FMP_MCP_MANIFEST": "examples/mcp_configurations/trading_manifest.py"
      }
    }
  }
}
```

#### For Investment Research:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret,
        "FMP_MCP_MANIFEST": "examples/mcp_configurations/research_manifest.py"
      }
    }
  }
}
```

#### For Cryptocurrency:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_api_key_here"  # pragma: allowlist secret,
        "FMP_MCP_MANIFEST": "examples/mcp_configurations/crypto_manifest.py"
      }
    }
  }
}
```

## Security Notes

- **Never share your API key** publicly or commit it to version control
- Your API key is stored locally in the Claude Desktop config
- The connection between Claude and the MCP server is local to your machine
- No data is sent to external servers except API calls to FMP

## Getting Help

- **FMP Data Issues**: [GitHub Issues](https://github.com/MehdiZare/fmp-data/issues)
- **API Documentation**: [FMP API Docs](https://site.financialmodelingprep.com/developer/docs)
- **Claude Desktop Help**: [Claude Support](https://support.anthropic.com)

## Example Conversations

Here are some example conversations you can have with Claude once connected:

### Investment Analysis
```
You: "I'm interested in investing in tech stocks. Can you analyze Apple, Microsoft, and Google for me?"
Claude: [Will fetch current prices, key metrics, and provide analysis]
```

### Market Overview
```
You: "What's happening in the market today? Show me gainers, losers, and sector performance."
Claude: [Will fetch and display market movers and sector data]
```

### Financial Research
```
You: "Compare the financial health of Tesla and Ford using their latest financial statements."
Claude: [Will fetch and analyze income statements, balance sheets, and key ratios]
```

## Next Steps

1. Explore more [FMP API endpoints](https://site.financialmodelingprep.com/developer/docs)
2. Customize your tool manifest for specific use cases
3. Learn about [rate limiting and API tiers](https://site.financialmodelingprep.com/pricing-plans)
4. Join the [FMP Data community](https://github.com/MehdiZare/fmp-data/discussions)

---

**Note**: This integration requires an active internet connection for real-time data fetching. API rate limits apply based on your FMP subscription tier.
