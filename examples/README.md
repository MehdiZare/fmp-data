# FMP Data Examples

This directory contains comprehensive examples demonstrating how to use the FMP Data library for various financial data tasks.

## Directory Structure

```text
examples/
├── basic/                    # Basic operations
│   ├── company_info.py      # Company profiles, executives, peers
│   ├── historical_prices.py # Historical price data and analysis
│   └── market.py            # Real-time quotes and market data
│
├── fundamental_analysis/     # Financial statement analysis
│   └── financial_statements.py  # Income statements, balance sheets, cash flow
│
├── technical_analysis/       # Technical indicators
│   └── indicators.py        # RSI, MACD, SMA, EMA
│
├── batch_operations/         # Bulk data retrieval (v2.0+)
│   └── multi_symbol_quotes.py   # Multi-symbol quotes, ETF quotes, market caps
│
├── transcripts/              # Earnings call transcripts (v2.0+)
│   └── earnings_calls.py    # Fetch and analyze earnings transcripts
│
├── sec_filings/              # SEC filings access (v2.0+)
│   └── filings_search.py    # Search 8-K, 10-K, 10-Q filings
│
├── index_tracking/           # Market index constituents (v2.0+)
│   └── index_constituents.py    # S&P 500, NASDAQ, Dow Jones tracking
│
├── workflows/                # Real-world workflows
│   └── portfolio_analysis.py    # Complete portfolio analysis workflow
│
└── mcp/                      # MCP server integration
    ├── setup_guide.md       # MCP setup guide
    ├── server.py            # MCP server example
    ├── configurations/      # Pre-configured tool sets
    └── claude_desktop/      # Claude Desktop integration
```

## Getting Started

### Prerequisites

1. Install fmp-data:
```bash
pip install fmp-data
```

2. Set your API key:
```bash
export FMP_API_KEY=your_api_key_here
```

Get your API key from [Financial Modeling Prep](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi)

### Running Examples

All examples use the context manager pattern for automatic resource cleanup:

```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Your code here
    profile = client.company.get_profile("AAPL")
# Client automatically closed
```

To run an example:
```bash
python examples/basic/company_info.py
```

## Example Categories

### Basic Operations

Start here if you're new to the library:

- **company_info.py**: Get company profiles, executives, peers, and employee data
- **historical_prices.py**: Fetch historical prices, earnings, and technical indicators
- **market.py**: Real-time quotes, market movers, sector performance

```bash
python examples/basic/company_info.py
```

### Fundamental Analysis

Financial statement analysis:

- **financial_statements.py**: Income statements, balance sheets, cash flow analysis

```bash
python examples/fundamental_analysis/financial_statements.py
```

### Technical Analysis

Technical indicators and chart patterns:

- **indicators.py**: RSI, MACD, SMA, EMA calculations

```bash
python examples/technical_analysis/indicators.py
```

### Batch Operations (v2.0+)

Efficient multi-symbol data retrieval:

- **multi_symbol_quotes.py**: Batch quotes for portfolios, ETF universe, market caps

```bash
python examples/batch_operations/multi_symbol_quotes.py
```

### Earnings Transcripts (v2.0+)

Access to earnings call transcripts:

- **earnings_calls.py**: Fetch and analyze earnings call transcripts

```bash
python examples/transcripts/earnings_calls.py
```

### SEC Filings (v2.0+)

SEC filing search and analysis:

- **filings_search.py**: Search and retrieve 8-K, 10-K, 10-Q filings

```bash
python examples/sec_filings/filings_search.py
```

### Index Tracking (v2.0+)

Track major market index constituents:

- **index_constituents.py**: S&P 500, NASDAQ, Dow Jones constituents and changes

```bash
python examples/index_tracking/index_constituents.py
```

### Workflows

Real-world use case demonstrations:

- **portfolio_analysis.py**: Complete portfolio analysis with quotes, profiles, and technical indicators

```bash
python examples/workflows/portfolio_analysis.py
```

### MCP Server Integration

Model Context Protocol (MCP) integration for Claude Desktop:

- **setup_guide.md**: Step-by-step MCP setup instructions
- **server.py**: MCP server implementation
- **configurations/**: Pre-configured tool manifests (minimal, research, trading, crypto)
- **claude_desktop/**: Claude Desktop setup scripts and troubleshooting

See [mcp/setup_guide.md](mcp/setup_guide.md) for detailed MCP setup instructions.

## Common Patterns

### Using Context Managers (Recommended)

```python
with FMPDataClient.from_env() as client:
    profile = client.company.get_profile("AAPL")
# Client automatically closed
```

### Error Handling

```python
from fmp_data import FMPDataClient
from fmp_data.exceptions import FMPError, RateLimitError

with FMPDataClient.from_env() as client:
    try:
        profile = client.company.get_profile("AAPL")
    except RateLimitError as e:
        print(f"Rate limit hit. Retry after {e.retry_after}s")
    except FMPError as e:
        print(f"API error: {e}")
```

### Batch Processing

```python
# Efficient: Single API call for multiple symbols
quotes = client.batch.get_quotes(["AAPL", "MSFT", "GOOGL"])

# Less efficient: Multiple API calls
for symbol in ["AAPL", "MSFT", "GOOGL"]:
    quote = client.company.get_quote(symbol)
```

## What's New in v2.0

Version 2.0 introduces several new data domains:

- **Batch Operations**: Multi-symbol quotes, bulk financials, exchange-wide data
- **Transcripts**: Earnings call transcript access and search
- **SEC Filings**: Comprehensive SEC filing search (8-K, 10-K, 10-Q, etc.)
- **Index Tracking**: S&P 500, NASDAQ, Dow Jones constituent tracking

See the respective folders for examples of these new features.

## Need Help?

- **Documentation**: See [docs/](../docs/) for full API documentation
- **Issues**: [GitHub Issues](https://github.com/MehdiZare/fmp-data/issues)
- **Author**: [LinkedIn](https://www.linkedin.com/in/mehdizare/)

## Contributing

Have a useful example to share? We welcome contributions!

1. Fork the repository
2. Add your example following the existing structure
3. Update this README
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
