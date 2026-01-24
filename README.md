# FMP Data Client

[![Test-Matrix](https://github.com/MehdiZare/fmp-data/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MehdiZare/fmp-data/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/fmp-data.svg)](https://pypi.org/project/fmp-data/)
[![Python](https://img.shields.io/pypi/pyversions/fmp-data.svg)](https://pypi.org/project/fmp-data/)
[![codecov](https://codecov.io/gh/MehdiZare/fmp-data/branch/main/graph/badge.svg)](https://codecov.io/gh/MehdiZare/fmp-data)
[![UV](https://img.shields.io/badge/uv-Package%20Manager-blue)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for the Financial Modeling Prep (FMP) API with comprehensive logging, rate limiting, and error handling. Built with UV for fast, reliable dependency management and modern Python development practices.

For AI/LLM integration guidance, see the [LLM Guide](https://github.com/MehdiZare/fmp-data/blob/main/LLM.md).

## Why UV?

This project uses UV as the primary package management tool for several key benefits:
- **Lightning-fast performance** - 10-100x faster than pip and pip-tools
- **Deterministic builds** with lock files ensuring reproducible environments
- **Drop-in pip replacement** with familiar commands and workflows
- **Virtual environment management** that's transparent and reliable
- **Built in Rust** for maximum performance and reliability
- **Dependency resolution** that prevents conflicts before they happen

## Features

- Simple and intuitive interface
- Built-in rate limiting
- Comprehensive logging
- Async support
- Type hints and validation with Pydantic
- Automatic retries with exponential backoff
- 85%+ test coverage with comprehensive test suite
- Secure API key handling
- 100% coverage of FMP stable endpoints
- Detailed error messages
- Configurable retry strategies
- **Langchain Integration**
- **MCP Server Support**

## Getting an API Key

To use this library, you'll need an API key from Financial Modeling Prep (FMP). You can:
- Get a [free API key from FMP](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi)
- All paid plans come with a 10% discount.

## Installation

### Using UV (Recommended)

```bash
# Basic installation
uv pip install fmp-data

# With Langchain integration
uv pip install "fmp-data[langchain]"

# With MCP server support
uv pip install "fmp-data[mcp]"

# With both integrations
uv pip install "fmp-data[langchain,mcp]"
```

LangChain integration requires LangChain v1 (`langchain-core`, `langchain-openai`) and LangGraph v1.

### Using pip

```bash
# Basic installation
pip install fmp-data

# With extras
pip install fmp-data[langchain]
pip install fmp-data[mcp]
pip install fmp-data[langchain,mcp]
```

## MCP Server (Claude Desktop Integration)

Model Context Protocol (MCP) server provides financial data access through a standardized protocol, enabling Claude Desktop to query FMP data seamlessly.

### Quick Setup for Claude Desktop

```bash
# Install with MCP support
pip install fmp-data[mcp]

# Run interactive setup wizard
fmp-mcp setup
```

The setup wizard will automatically configure Claude Desktop with FMP Data tools. After setup, restart Claude Desktop and try asking: "What's the current price of AAPL?"

### Manual Configuration

```bash
# Set your API key
export FMP_API_KEY=your_api_key_here

# Run the MCP server
fmp-mcp
```

For detailed setup instructions, see [docs/mcp/claude_desktop.md](https://github.com/MehdiZare/fmp-data/blob/main/docs/mcp/claude_desktop.md).

### Available Commands

```bash
fmp-mcp setup    # Interactive setup wizard
fmp-mcp status   # Check server status
fmp-mcp test     # Test connection
fmp-mcp list     # List available tools
```

### Configuration Profiles

Choose from pre-configured tool sets. See [docs/mcp/configurations.md](https://github.com/MehdiZare/fmp-data/blob/main/docs/mcp/configurations.md).
Full tool list: [docs/mcp/tools.md](https://github.com/MehdiZare/fmp-data/blob/main/docs/mcp/tools.md).

### Custom Configuration

```bash
# Environment variables
export FMP_API_KEY=your_api_key_here
export FMP_MCP_MANIFEST=/path/to/custom/manifest.py

# Custom manifest example (manifest.py)
TOOLS = [
    "company.profile",
    "market.search",
    "company.quote",
    "fundamental.income_statement",
    "fundamental.balance_sheet"
]
```

### Integration with AI Assistants

The MCP server exposes FMP endpoints as tools that can be used by MCP-compatible AI assistants:

```python
from fmp_data.mcp.server import create_app

# Create MCP server with default tools
app = create_app()

# Create with custom tools
app = create_app(tools=["company.profile", "company.quote"])

# Create with manifest file
app = create_app(tools="/path/to/manifest.py")
```

### Available Tools

The MCP server exposes tools for endpoints that have MCP tool semantics.
For the full MCP catalog, run `fmp-mcp list` or see [docs/mcp/tools.md](https://github.com/MehdiZare/fmp-data/blob/main/docs/mcp/tools.md).
- `company.profile` - Get company profiles
- `market.search` - Search companies
- `company.quote` - Get real-time quotes
- `fundamental.income_statement` - Financial statements
- `technical.rsi` - Technical analysis
- And many more...

## Langchain Integration

### Prerequisites
- FMP API Key (`FMP_API_KEY`) - [Get one here](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi)
- OpenAI API Key (`OPENAI_API_KEY`) - Required for embeddings

### Quick Start with Vector Store

```python
from fmp_data import create_vector_store

# Initialize the vector store
vector_store = create_vector_store(
    fmp_api_key="YOUR_FMP_API_KEY",       # pragma: allowlist secret
    openai_api_key="YOUR_OPENAI_API_KEY"  # pragma: allowlist secret
)

# Example queries
queries = [
    "what is the price of Apple stock?",
    "what was the revenue of Tesla last year?",
    "what's new in the market?"
]

# Search for relevant endpoints and tools
for query in queries:
    print(f"\nQuery: {query}")

    # Get tools formatted for OpenAI
    tools = vector_store.get_tools(query, provider="openai")

    print("\nMatching Tools:")
    for tool in tools:
        print(f"Name: {tool.get('name')}")
        print(f"Description: {tool.get('description')}")
        print("Parameters:", tool.get('parameters'))
        print()

    # You can also search endpoints directly
    results = vector_store.search(query)
    print("\nRelevant Endpoints:")
    for result in results:
        print(f"Endpoint: {result.name}")
        print(f"Score: {result.score:.2f}")
        print()
```

Note (2.0.0+): Loading cached vector stores now requires instantiating
`EndpointVectorStore(client, registry, embeddings, allow_dangerous_deserialization=True)`.
The `allow_dangerous_deserialization` boolean is passed at construction so cached
stores load automatically if present and the flag is enabled; use only with
trusted cache sources.

### Alternative Setup: Using Configuration

```python
from fmp_data import FMPDataClient, ClientConfig, create_vector_store
from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.embedding import EmbeddingProvider

# Configure with LangChain support
config = LangChainConfig(
    api_key="YOUR_FMP_API_KEY",           # pragma: allowlist secret
    embedding_provider=EmbeddingProvider.OPENAI,
    embedding_api_key="YOUR_OPENAI_API_KEY", # pragma: allowlist secret
    embedding_model="text-embedding-3-small"
)

# Create client with LangChain config
client = FMPDataClient(config=config)

# Create vector store using the config
vector_store = create_vector_store(
    fmp_api_key=config.api_key,  # pragma: allowlist secret
    openai_api_key=config.embedding_api_key,  # pragma: allowlist secret
    cache_dir=config.vector_store_path,
    embedding_provider=config.embedding_provider,
    embedding_model=config.embedding_model,
)

# Search for relevant endpoints
results = vector_store.search("show me Tesla's financial metrics")
for result in results:
    print(f"Found endpoint: {result.name}")
    print(f"Relevance score: {result.score:.2f}")
```

### Environment Variables
You can also configure the integration using environment variables:
```bash
# Required
export FMP_API_KEY=your_fmp_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here

# Optional
export FMP_EMBEDDING_PROVIDER=openai
export FMP_EMBEDDING_MODEL=text-embedding-3-small
```

### Features
- Semantic search across the full FMP endpoint catalog
- Auto-conversion to LangChain tools
- Query endpoints using natural language
- Relevance scoring for search results
- Automatic caching of embeddings
- Persistent vector store for faster lookups

## Quick Start

```python
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig
from fmp_data.exceptions import FMPError, RateLimitError, AuthenticationError

# Method 1: Initialize with direct API key
client = FMPDataClient(api_key="your_api_key_here") # pragma: allowlist secret

# Method 2: Initialize from environment variable (FMP_API_KEY)
client = FMPDataClient.from_env()

# Method 3: Initialize with custom configuration
config = ClientConfig(
    api_key="your_api_key_here", #pragma: allowlist secret
    timeout=30,
    max_retries=3,
    base_url="https://financialmodelingprep.com",
    logging=LoggingConfig(level="INFO")
)
client = FMPDataClient(config=config)

# Using with context manager (recommended)
with FMPDataClient(api_key="your_api_key_here") as client: # pragma: allowlist secret
    try:
        # Get company profile
        profile = client.company.get_profile("AAPL")
        print(f"Company: {profile.company_name}")
        print(f"Industry: {profile.industry}")
        print(f"Market Cap: ${profile.mkt_cap:,.2f}")

        # Search companies
        results = client.market.search_company("Tesla", limit=5)
        for company in results:
            print(f"{company.symbol}: {company.name}")

    except RateLimitError as e:
        print(f"Rate limit exceeded. Wait {e.retry_after} seconds")
    except AuthenticationError:
        print("Invalid API key")
    except FMPError as e:
        print(f"API error: {e}")

# Client is automatically closed after the with block
```

## Available Client Modules

The FMP Data Client provides access to all FMP API endpoints (100% stable coverage)
through specialized client modules:

- **company**: Company profiles, quotes, historical prices, executives, peers
- **market**: Market movers, sector performance, market hours, listings/search
- **fundamental**: Financial statements (income, balance sheet, cash flow)
- **technical**: Technical indicators (SMA, EMA, RSI, MACD, etc.)
- **intelligence**: Market news, press releases, analyst ratings
- **institutional**: Institutional holdings, insider trading
- **investment**: ETF and mutual fund data
- **alternative**: Crypto, forex, and commodity data
- **economics**: Economic indicators and calendar data
- **batch**: Batch quotes for multiple symbols or entire asset classes
- **transcripts**: Earnings call transcripts
- **sec**: SEC filings, company profiles, and SIC codes
- **index**: Market index constituents (S&P 500, NASDAQ, Dow Jones)

Full endpoint catalog: [docs/api/endpoints.md](https://github.com/MehdiZare/fmp-data/blob/main/docs/api/endpoints.md)

## Key Components

### 1. Company Information
```python
from datetime import date

from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get company profile
    profile = client.company.get_profile("AAPL")

    # Get company executives
    executives = client.company.get_executives("AAPL")

    # Search companies (market lookup)
    results = client.market.search_company("apple", limit=5)

    # Get employee count history
    employees = client.company.get_employee_count("AAPL")

    # Get company peers
    peers = client.company.get_company_peers("AAPL")
```

### 2. Financial Statements
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get income statements
    income_stmt = client.fundamental.get_income_statement(
        "AAPL",
        period="quarter",  # or "annual"
        limit=4
    )

    # Get balance sheets
    balance_sheet = client.fundamental.get_balance_sheet(
        "AAPL",
        period="annual"
    )

    # Get cash flow statements
    cash_flow = client.fundamental.get_cash_flow("AAPL")
```

### 3. Market Data
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get real-time quote
    quote = client.company.get_quote("TSLA")

    # Get historical prices
    history = client.company.get_historical_prices(
        symbol="TSLA",
        from_date=date(2023, 1, 1),
        to_date=date(2023, 12, 31)
    )

    # Get intraday prices
    intraday = client.company.get_intraday_prices(
        "TSLA",
        interval="5min"
    )
```

### 4. Technical Indicators
```python
from fmp_data import FMPDataClient
from datetime import date

with FMPDataClient.from_env() as client:
    # Simple Moving Average
    sma = client.technical.get_sma(
        "AAPL",
        period_length=20,
        timeframe="1day"
    )

    # RSI (Relative Strength Index)
    rsi = client.technical.get_rsi(
        "AAPL",
        period_length=14,
        timeframe="1day"
    )

    # MACD
    macd = client.technical.get_macd(
        "AAPL",
        fast_period=12,
        slow_period=26,
        signal_period=9
    )
```

### 5. Alternative Data
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Crypto quotes
    btc = client.alternative.get_crypto_quote("BTCUSD")

    # Forex quotes
    eurusd = client.alternative.get_forex_quote("EURUSD")

    # Commodity quotes
    gold = client.alternative.get_commodity_quote("GCUSD")
```

### 6. Institutional and Intelligence Data
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Institutional holdings
    holders = client.institutional.get_institutional_holders("AAPL")

    # Insider trading
    insider = client.institutional.get_insider_trading("AAPL")

    # Market news
    news = client.intelligence.get_stock_news("TSLA", limit=10)

    # Analyst grades
    grades = client.intelligence.get_grades("AAPL")
```

### 7. Batch Data
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get quotes for multiple symbols at once
    quotes = client.batch.get_quotes(["AAPL", "MSFT", "GOOGL"])

    # Get all ETF quotes
    etf_quotes = client.batch.get_etf_quotes()

    # Get all crypto quotes
    crypto_quotes = client.batch.get_crypto_quotes()

    # Get market caps for multiple symbols
    market_caps = client.batch.get_market_caps(["AAPL", "MSFT"])
```

### 8. Earnings Transcripts
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get latest earnings call transcripts
    latest = client.transcripts.get_latest(limit=10)

    # Get transcript for specific company and quarter
    transcript = client.transcripts.get_transcript("AAPL", year=2024, quarter=4)

    # Get available transcript dates
    dates = client.transcripts.get_available_dates("AAPL")
```

### 9. SEC Filings
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get latest 8-K filings
    filings_8k = client.sec.get_latest_8k(limit=10)

    # Search filings by symbol
    filings = client.sec.search_by_symbol("AAPL")

    # Get SEC company profile (may return None if not found)
    profile = client.sec.get_profile("AAPL")

    # Get SIC codes
    sic_codes = client.sec.get_sic_codes()
```

### 10. Market Index Constituents
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get S&P 500 constituents
    sp500 = client.index.get_sp500_constituents()

    # Get NASDAQ constituents
    nasdaq = client.index.get_nasdaq_constituents()

    # Get Dow Jones constituents
    dowjones = client.index.get_dowjones_constituents()

    # Get historical changes
    changes = client.index.get_historical_sp500()
```

### 11. Async Support
Async support is available via `AsyncFMPDataClient` and the async endpoint
clients (e.g., `AsyncCompanyClient`, `AsyncMarketClient`, and more). For a full
walkthrough, see the async usage guide in `docs/index.md#async-usage` and the
API reference in `docs/api/reference.md#async-client-usage`.

```python
from fmp_data import AsyncFMPDataClient
import asyncio

async def main():
    async with AsyncFMPDataClient.from_env() as client:
        # All endpoint methods are async
        profile = await client.company.get_profile("AAPL")
        print(f"Company: {profile.company_name}")

        # Concurrent requests
        profiles = await asyncio.gather(
            client.company.get_profile("AAPL"),
            client.company.get_profile("MSFT"),
            client.company.get_profile("GOOGL"),
        )
        for p in profiles:
            print(f"{p.symbol}: {p.company_name}")

asyncio.run(main())
```

## Configuration

### Environment Variables
```bash
# Required
FMP_API_KEY=your_api_key_here

# Optional
FMP_BASE_URL=https://financialmodelingprep.com
FMP_TIMEOUT=30
FMP_MAX_RETRIES=3

# Rate Limiting
FMP_DAILY_LIMIT=250
FMP_REQUESTS_PER_SECOND=10
FMP_REQUESTS_PER_MINUTE=300

# Logging
FMP_LOG_LEVEL=INFO
FMP_LOG_PATH=/path/to/logs
FMP_LOG_MAX_BYTES=10485760
FMP_LOG_BACKUP_COUNT=5

# MCP Server
FMP_MCP_MANIFEST=/path/to/custom/manifest.py
```

### Custom Configuration
```python
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig, RateLimitConfig, LogHandlerConfig

config = ClientConfig(
    api_key="your_api_key_here",  # pragma: allowlist secret
    timeout=30,
    max_retries=3,
    base_url="https://financialmodelingprep.com",
    rate_limit=RateLimitConfig(
        daily_limit=250,
        requests_per_second=10,
        requests_per_minute=300
    ),
    logging=LoggingConfig(
        level="DEBUG",
        handlers={
            "console": LogHandlerConfig(
                class_name="StreamHandler",
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            "file": LogHandlerConfig(
                class_name="RotatingFileHandler",
                level="DEBUG",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handler_kwargs={
                    "filename": "fmp.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            )
        }
    )
)

client = FMPDataClient(config=config)
```

## Error Handling

The library provides a comprehensive exception hierarchy for robust error handling:

```python
from fmp_data import FMPDataClient
from fmp_data.exceptions import (
    FMPError,              # Base exception for all FMP errors
    RateLimitError,        # API rate limit exceeded
    AuthenticationError,   # Invalid or missing API key
    ValidationError,       # Invalid request parameters
    ConfigError,           # Configuration errors
    InvalidSymbolError,    # Missing or blank required symbol
    InvalidResponseTypeError,  # Unexpected API response type
    DependencyError,       # Missing optional dependency
    FMPNotFound,          # Symbol or resource not found
)

try:
    with FMPDataClient.from_env() as client:
        profile = client.company.get_profile("AAPL")

except RateLimitError as e:
    print(f"Rate limit exceeded. Wait {e.retry_after} seconds")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")

except AuthenticationError as e:
    print("Invalid API key or authentication failed")
    print(f"Status code: {e.status_code}")

except InvalidSymbolError as e:
    print(f"Symbol error: {e.message}")

except ValidationError as e:
    print(f"Invalid parameters: {e.message}")

except DependencyError as e:
    print(f"Missing dependency: {e.feature}")
    print(f"Install with: {e.install_command}")

except FMPNotFound as e:
    print(f"Not found: {e.message}")

except InvalidResponseTypeError as e:
    print(f"Unexpected response type: {e.message}")

except ConfigError as e:
    print(f"Configuration error: {e.message}")

except FMPError as e:
    print(f"General API error: {e.message}")
```

## Development Setup

### Prerequisites
- Python 3.10-3.14
- UV (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. Install dependencies with UV:
```bash
# Create virtual environment and install all dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode with all extras
uv pip install -e ".[langchain,mcp]" --all-extras

# Install development dependencies
uv pip install --group dev -e .
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

5. Set up environment variables:
```bash
# Create .env file
echo "FMP_API_KEY=your_api_key_here" > .env
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests with coverage
pytest --cov=fmp_data

# Run tests with coverage report
pytest --cov=fmp_data --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py

# Run tests with verbose output
pytest -v

# Run integration tests (requires API key)
FMP_TEST_API_KEY=your_test_api_key pytest tests/integration/

# Using make commands (if available)
make test        # Run unit tests
make test-cov    # Run tests with coverage
make test-all    # Run all tests for all Python versions
```

### Development Commands

```bash
# Format code with ruff
ruff format fmp_data tests

# Lint with ruff
ruff check fmp_data tests --fix

# Type checking with mypy
mypy fmp_data

# Run all quality checks
pre-commit run --all-files

# Using make commands (recommended)
make fix         # Auto-fix all issues
make lint        # Run linting
make typecheck   # Run type checking
make check       # Run all checks
make test        # Run tests
make test-cov    # Run tests with coverage report
make ci          # Run full CI checks locally
```

### Building and Publishing

```bash
# Build the package
uv build

# Or using Python build
python -m build

# Check package before publishing
twine check dist/*

# Publish to PyPI (maintainers only)
twine upload dist/*

# Using make commands
make build       # Build package
make build-check # Build and verify
```

### UV Configuration

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install/upgrade packages
uv pip install --upgrade package-name

# Sync dependencies from pyproject.toml
uv pip sync pyproject.toml

# Export requirements.txt (if needed)
uv pip freeze > requirements.txt

# Compile requirements (fast dependency resolution)
uv pip compile pyproject.toml -o requirements.txt
```

View the latest test coverage report [here](https://codecov.io/gh/MehdiZare/fmp-data).

## Contributing

We welcome contributions! Please follow these steps:

### Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/fmp-data.git
cd fmp-data
```

3. Set up development environment:
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies with UV
uv pip install -e ".[langchain,mcp]" --all-extras

# Install pre-commit hooks
pre-commit install
```

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure quality:
```bash
# Format code
ruff format fmp_data tests

# Fix linting issues
ruff check fmp_data tests --fix

# Run type checking
mypy fmp_data

# Run tests
pytest --cov=fmp_data

# Or use make commands
make fix    # Fix all auto-fixable issues
make check  # Run all checks
```

3. Commit your changes:
```bash
git add .
git commit -m "feat: add your feature description"
```

4. Push and create a pull request

### Requirements

Please ensure your contributions meet these requirements:
- Tests pass: `pytest` or `make test`
- Code is formatted: `ruff format` or `make fix`
- Code passes linting: `ruff check` or `make lint`
- Type hints are included for all functions
- Documentation is updated for new features
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- Test coverage remains above 80%

### Running Quality Checks

```bash
# Run all quality checks at once
pre-commit run --all-files

# Or use make commands (recommended)
make check      # Run all checks
make fix        # Fix all auto-fixable issues
make test       # Run tests
make test-cov   # Run tests with coverage

# Or run individual checks
ruff check fmp_data tests
ruff format --check fmp_data tests
mypy fmp_data
pytest --cov=fmp_data
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/MehdiZare/fmp-data/blob/main/LICENSE) file for details.

## Acknowledgments

- Financial Modeling Prep for providing the API
- Contributors to the project
- Open source packages used in this project

## Support

- GitHub Issues: [Create an issue](https://github.com/MehdiZare/fmp-data/issues)
- Documentation: [Read the docs](https://github.com/MehdiZare/fmp-data/tree/main/docs)
- Connect with the author: [LinkedIn](https://www.linkedin.com/in/mehdizare/)

## Examples

### Interactive Notebooks
- [Financial Agent Tutorial](https://colab.research.google.com/drive/1cSyLX-j9XhyrXyVJ2HwMZJvPy1Lf2CuA?usp=sharing): Build an intelligent financial agent with LangChain integration
- [Basic Usage Examples](https://github.com/MehdiZare/fmp-data/tree/main/examples): Simple code examples demonstrating key features

### Code Examples

```python
# Basic usage example
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get company profile
    profile = client.company.get_profile("AAPL")
    print(f"Company: {profile.company_name}")
```

## Release Notes

See [CHANGELOG.md](https://github.com/MehdiZare/fmp-data/blob/main/CHANGELOG.md) for a list of changes in each release.
