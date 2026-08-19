# FMP Data

A robust Python client for Financial Modeling Prep API with comprehensive features including rate limiting, retry strategies, async support, and full type safety.
Now with 100% coverage of the FMP stable endpoint catalog.

## Features

✨ **Core Features**
- Rate limiting with automatic backoff
- Retry strategies for failed requests
- Comprehensive error handling
- Async/await support
- Opt-in response caching with memory, file, and Redis backends
- Full type hints with Pydantic validation

🏢 **API Coverage**
- Full coverage of FMP stable endpoints
- Company profiles and financial data
- Market data and quotes
- Fundamental analysis (financial statements, ratios, metrics)
- Technical analysis indicators
- Market intelligence and research
- Institutional holdings and insider trading
- Investment funds data
- Alternative markets data
- Economic indicators
- Batch market data
- Earnings call transcripts
- SEC filings and company profiles
- Index constituents and historical changes

🔧 **Developer Experience**
- Intuitive client interface with property-based access
- Structured logging with configurable handlers
- Environment-based configuration
- LangChain integration for AI applications
- Python 3.10-3.14 support

## Quick Start

### Launch Notes

- Price-history volume fields now normalize to `float` for a single stable return type when FMP mixes whole-number and fractional payloads.
- This affects `alternative.HistoricalPrice.volume`, `alternative.HistoricalPrice.unadjusted_volume`, and `company.IntradayPrice.volume`.
- If your code previously type-checked these values as integers, expect whole-number payloads to deserialize as values like `123.0`.

### Installation

```bash
pip install fmp-data
```

For Redis-backed caching:

```bash
pip install "fmp-data[cache-redis]"
```

For LangChain integration:
```bash
pip install "fmp-data[langchain]"
```

LangChain integration requires LangChain v1 (`langchain-core`, `langchain-openai`) and LangGraph v1.

### Basic Usage

```python
from fmp_data import FMPDataClient, Period

# Initialize from environment variables
with FMPDataClient.from_env() as client:
    # Get company profile
    profile = client.company.get_profile("AAPL")
    print(f"Company: {profile.company_name}")

    # Get financial statements
    period: Period = "annual"
    income = client.fundamental.get_income_statement("AAPL", period=period)
    print(f"Revenue: ${income[0].revenue:,.0f}")

    # Get market data
    quote = client.company.get_quote("AAPL")
    print(f"Current Price: ${quote.price}")
```

### Async Usage

For async applications, use `AsyncFMPDataClient`:

```python
import asyncio
from fmp_data import AsyncFMPDataClient


async def main():
    async with AsyncFMPDataClient.from_env() as client:
        # All methods are async - same names as sync client
        profile = await client.company.get_profile("AAPL")
        print(f"Company: {profile.company_name}")

        # Fetch multiple items concurrently
        quote, income = await asyncio.gather(
            client.company.get_quote("AAPL"),
            client.fundamental.get_income_statement("AAPL", period="annual"),
        )
        print(f"Price: ${quote.price}, Revenue: ${income[0].revenue:,.0f}")


asyncio.run(main())
```

Period, interval, and timeframe are closed `Literal` aliases. Import them
from the package root when you want to annotate against the live client
contracts:

```python
from fmp_data import (
    Interval,
    Period,
    PeriodAnnualQuarter,
    PeriodFiscal,
    Structure,
    TechnicalInterval,
    Timeframe,
)
```

There are three period types on purpose: most statement endpoints take
`Period` (`annual` / `quarter` / `FY` / `Q1`–`Q4`). Financial reports and
batch bulk take only `PeriodFiscal`. Some company series take only
`PeriodAnnualQuarter`. `Timeframe` is `Interval` plus `"1day"`.
`TechnicalClient.interval=` takes `TechnicalInterval` (`Interval` plus
`"daily"` / `"hourly"`), not `Timeframe`. Revenue segmentation
`structure=` takes `Structure` (`flat` / `nested`); live `/stable`
returns the same list-of-objects for both.

### Response Caching

```python
from fmp_data import CacheConfig, ClientConfig, FMPDataClient

config = ClientConfig(
    api_key="YOUR_FMP_API_KEY",  # pragma: allowlist secret
    cache=CacheConfig(
        backend="file",
        default_ttl=300,
        cache_dir=".cache/fmp-data",
        ttl_overrides={"quote": 30},
    ),
)

with FMPDataClient(config=config) as client:
    quote = client.company.get_quote("AAPL")
    fresh_quote = client.company.get_quote("AAPL", force_refresh=True)
```

### Environment Configuration

Create a `.env` file in your project root:

```bash
FMP_API_KEY=your_api_key_here
FMP_TIMEOUT=30
FMP_MAX_RETRIES=3
# Note: Do NOT include /api in the base URL - it's added automatically
FMP_BASE_URL=https://financialmodelingprep.com
FMP_CACHE_ENABLED=true
FMP_CACHE_BACKEND=memory
FMP_CACHE_TTL=300
```

Use `FMP_CACHE_DIR` for the file backend and `FMP_CACHE_REDIS_URL` for the Redis backend.

### Error Handling

```python
from fmp_data import FMPDataClient
from fmp_data.exceptions import RateLimitError, AuthenticationError

try:
    with FMPDataClient.from_env() as client:
        profile = client.company.get_profile("AAPL")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after}s")
except AuthenticationError:
    print("Invalid API key")
```

## API Client Structure

Both `FMPDataClient` (sync) and `AsyncFMPDataClient` (async) provide organized access to different data categories through the same interface:

```python
# Sync client
client = FMPDataClient.from_env()

# Async client (same structure, async methods)
async_client = AsyncFMPDataClient.from_env()

# Both clients provide access to these endpoint groups:
client.company.*        # Company data, quotes, and historical prices
client.market.*         # Market movers, hours, and listings/search
client.fundamental.*    # Fundamental analysis
client.technical.*      # Technical analysis
client.intelligence.*   # Market intelligence
client.institutional.*  # Institutional data
client.investment.*     # Investment funds
client.alternative.*    # Alternative markets
client.economics.*      # Economic data
client.batch.*          # Batch data operations
client.transcripts.*    # Earnings call transcripts
client.sec.*            # SEC filings
client.index.*          # Index constituents
```

## Documentation

- **[API Reference](api/reference.md)**: Complete API documentation
- **[Endpoints List](api/endpoints.md)**: Stable endpoint catalog
- **[MCP Integration](mcp/index.md)**: Claude Desktop setup, manifests, and tools
- **[Development Guide](contributing/development.md)**: Set up development environment
- **[Testing Guide](contributing/testing.md)**: Running and writing tests

## Examples

### Financial Analysis

```python
with FMPDataClient.from_env() as client:
    # Get comprehensive financial data
    symbol = "AAPL"

    # Company overview
    profile = client.company.get_profile(symbol)

    # Financial statements (last 5 years)
    income_statements = client.fundamental.get_income_statement(symbol, limit=5)
    balance_sheets = client.fundamental.get_balance_sheet(symbol, limit=5)
    cash_flows = client.fundamental.get_cash_flow(symbol, limit=5)

    # Key metrics and ratios
    metrics = client.fundamental.get_key_metrics(symbol, limit=5)
    ratios = client.fundamental.get_financial_ratios(symbol, limit=5)

    # Valuation
    dcf = client.fundamental.get_discounted_cash_flow(symbol)
```

### Market Monitoring

```python
with FMPDataClient.from_env() as client:
    # Market overview
    market_hours = client.market.get_market_hours()
    sector_performance = client.market.get_sector_performance()

    # Top movers
    gainers = client.market.get_gainers()
    losers = client.market.get_losers()
    active = client.market.get_most_active()

    # Company search
    results = client.market.search_company("technology")
```

### Async Concurrent Requests

```python
import asyncio
from fmp_data import AsyncFMPDataClient


async def analyze_portfolio(symbols: list[str]):
    async with AsyncFMPDataClient.from_env() as client:
        # Fetch all profiles concurrently
        profiles = await asyncio.gather(
            *[client.company.get_profile(symbol) for symbol in symbols]
        )

        # Fetch all quotes concurrently
        quotes = await asyncio.gather(
            *[client.company.get_quote(symbol) for symbol in symbols]
        )

        for profile, quote in zip(profiles, quotes):
            print(f"{profile.symbol}: ${quote.price:,.2f} ({profile.sector})")


asyncio.run(analyze_portfolio(["AAPL", "MSFT", "GOOGL", "AMZN"]))
```

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/MehdiZare/fmp-data/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/MehdiZare/fmp-data/discussions)
- **Examples**: Check the `examples/` directory for more code samples

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/MehdiZare/fmp-data/blob/main/LICENSE) file for details.
