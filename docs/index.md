# FMP Data

A robust Python client for Financial Modeling Prep API with comprehensive features including rate limiting, caching, retry strategies, and full type safety.

## Features

✨ **Core Features**
- Rate limiting with automatic backoff
- Response caching with configurable TTL
- Retry strategies for failed requests
- Comprehensive error handling
- Async/await support
- Full type hints with Pydantic validation

🏢 **API Coverage**
- Company profiles and financial data
- Market data and quotes
- Fundamental analysis (financial statements, ratios, metrics)
- Technical analysis indicators
- Market intelligence and research
- Institutional holdings and insider trading
- Investment funds data
- Alternative markets data
- Economic indicators

🔧 **Developer Experience**
- Intuitive client interface with property-based access
- Structured logging with configurable handlers
- Environment-based configuration
- LangChain integration for AI applications
- Modern Python 3.10+ syntax support

## Quick Start

### Installation

```bash
pip install fmp-data
```

For LangChain integration:
```bash
pip install "fmp-data[langchain]"
```

### Basic Usage

```python
from fmp_data import FMPDataClient

# Initialize from environment variables
with FMPDataClient.from_env() as client:
    # Get company profile
    profile = client.company.get_profile("AAPL")
    print(f"Company: {profile.company_name}")

    # Get financial statements
    income = client.fundamental.get_income_statement("AAPL", period="annual")
    print(f"Revenue: ${income[0].revenue:,.0f}")

    # Get market data
    quote = client.market.get_quote("AAPL")
    print(f"Current Price: ${quote.price}")
```

### Environment Configuration

Create a `.env` file in your project root:

```bash
FMP_API_KEY=your_api_key_here
FMP_TIMEOUT=30
FMP_MAX_RETRIES=3
FMP_BASE_URL=https://financialmodelingprep.com/api
```

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

The `FMPDataClient` provides organized access to different data categories:

```python
client = FMPDataClient.from_env()

# Company data and profiles
client.company.*

# Market data and quotes
client.market.*

# Fundamental analysis
client.fundamental.*

# Technical analysis
client.technical.*

# Market intelligence
client.intelligence.*

# Institutional data
client.institutional.*

# Investment funds
client.investment.*

# Alternative markets
client.alternative.*

# Economic data
client.economics.*
```

## Documentation

- **[API Reference](api/reference.md)**: Complete API documentation
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
    cash_flows = client.fundamental.get_cash_flow_statement(symbol, limit=5)

    # Key metrics and ratios
    metrics = client.fundamental.get_key_metrics(symbol, limit=5)
    ratios = client.fundamental.get_financial_ratios(symbol, limit=5)

    # Valuation
    dcf = client.fundamental.get_dcf(symbol)
```

### Market Monitoring

```python
with FMPDataClient.from_env() as client:
    # Market overview
    market_hours = client.market.get_market_hours()
    sector_performance = client.market.get_sector_performance()

    # Top movers
    gainers = client.market.get_market_gainers()
    losers = client.market.get_market_losers()
    active = client.market.get_most_active()

    # Company search
    results = client.market.search_companies("technology")
```

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/MehdiZare/fmp-data/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/MehdiZare/fmp-data/discussions)
- **Examples**: Check the `examples/` directory for more code samples

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/MehdiZare/fmp-data/blob/main/LICENSE) file for details.
