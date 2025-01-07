# FMP Data Client

[![Test](https://github.com/MehdiZare/fmp-data/actions/workflows/test.yml/badge.svg)](https://github.com/MehdiZare/fmp-data/actions/workflows/test.yml)
[![CI/CD Pipeline](https://github.com/MehdiZare/fmp-data/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MehdiZare/fmp-data/actions/workflows/ci-cd.yml)[![codecov](https://codecov.io/gh/MehdiZare/fmp-data/branch/main/graph/badge.svg)](https://codecov.io/gh/MehdiZare/fmp-data)
[![Python](https://img.shields.io/pypi/pyversions/fmp-data.svg)](https://pypi.org/project/fmp-data/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for the Financial Modeling Prep (FMP) API with comprehensive logging, rate limiting, and error handling.

## Features

- 🚀 Simple and intuitive interface
- 🔒 Built-in rate limiting
- 📝 Comprehensive logging
- ⚡ Async support
- 🏷️ Type hints and validation with Pydantic
- 🔄 Automatic retries with exponential backoff
- 🎯 100% test coverage (excluding predefined endpoints)
- 🛡️ Secure API key handling
- 📊 Support for all major FMP endpoints
- 🔍 Detailed error messages
- 🚦 Configurable retry strategies
- 🤖 **NEW: Langchain Integration**

## Getting an API Key

To use this library, you'll need an API key from Financial Modeling Prep (FMP). You can:
- Get a [free API key from FMP](https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi)
- All paid plans come with a 10% discount.

## Installation

```bash
# Using pip
pip install fmp-data

# Using poetry
poetry add fmp-data

# For Langchain integration
pip install fmp-data[langchain]
# or
poetry add fmp-data --extras langchain
```

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

### Alternative Setup: Using Configuration

```python
from fmp_data import FMPDataClient, ClientConfig
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

# Create vector store using the client
vector_store = client.create_vector_store()

# Search for relevant endpoints
results = vector_store.search("show me Tesla's financial metrics")
for result in results:
    print(f"Found endpoint: {result.name}")
    print(f"Relevance score: {result.score:.2f}")
```
### Interactive Example
Try out the LangChain integration in our interactive Colab notebook:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](link-to-your-colab-notebook)

This notebook demonstrates how to:
- Build an intelligent financial agent using fmp-data and LangChain
- Access real-time market data through natural language queries
- Use semantic search to select relevant financial tools
- Create multi-turn conversations about financial data
-
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
- 🔍 Semantic search across all FMP endpoints
- 🤖 Auto-conversion to LangChain tools
- 📊 Query endpoints using natural language
- 🎯 Relevance scoring for search results
- 🔄 Automatic caching of embeddings
- 💾 Persistent vector store for faster lookups

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
    base_url="https://financialmodelingprep.com/api",
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
        results = client.company.search("Tesla", limit=5)
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

## Key Components

### 1. Company Information
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get company profile
    profile = client.company.get_profile("AAPL")

    # Get company executives
    executives = client.company.get_executives("AAPL")

    # Search companies
    results = client.company.search("Tesla", limit=5)

    # Get employee count history
    employees = client.company.get_employee_count("AAPL")
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
    cash_flow = client.fundamental.get_cash_flow_statement("AAPL")
```

### 3. Market Data
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    # Get real-time quote
    quote = client.market.get_quote("TSLA")

    # Get historical prices
    history = client.market.get_historical_price(
        "TSLA",
        from_date="2023-01-01",
        to_date="2023-12-31"
    )
```

### 4. Async Support
```python
import asyncio
from fmp_data import FMPDataClient

async def get_multiple_profiles(symbols):
    async with FMPDataClient.from_env() as client:
        tasks = [client.company.get_profile_async(symbol)
                for symbol in symbols]
        return await asyncio.gather(*tasks)

# Run async function
symbols = ["AAPL", "MSFT", "GOOGL"]
profiles = asyncio.run(get_multiple_profiles(symbols))
```

## Configuration

### Environment Variables
```bash
# Required
FMP_API_KEY=your_api_key_here

# Optional
FMP_BASE_URL=https://financialmodelingprep.com/api
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
```

### Custom Configuration
```python
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig, RateLimitConfig, LogHandlerConfig

config = ClientConfig(
    api_key="your_api_key_here",  # pragma: allowlist secret
    timeout=30,
    max_retries=3,
    base_url="https://financialmodelingprep.com/api",
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

```python
from fmp_data import FMPDataClient
from fmp_data.exceptions import (
    FMPError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    ConfigError
)
try:
    with FMPDataClient.from_env() as client:
        profile = client.company.get_profile("INVALID")

except RateLimitError as e:
    print(f"Rate limit exceeded. Wait {e.retry_after} seconds")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")

except AuthenticationError as e:
    print("Invalid API key or authentication failed")
    print(f"Status code: {e.status_code}")

except ValidationError as e:
    print(f"Invalid parameters: {e.message}")

except ConfigError as e:
    print(f"Configuration error: {e.message}")

except FMPError as e:
    print(f"General API error: {e.message}")
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

## Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=fmp_data

# Run specific test file
poetry run pytest tests/test_client.py

# Run integration tests (requires API key)
FMP_TEST_API_KEY=your_test_api_key poetry run pytest tests/integration/
```

View the latest test coverage report [here](https://codecov.io/gh/MehdiZare/fmp-data).

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `poetry run pytest`
5. Create a pull request

Please ensure:
- Tests pass
- Code is formatted with black
- Type hints are included
- Documentation is updated
- Commit messages follow conventional commits

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- Financial Modeling Prep for providing the API
- Contributors to the project
- Open source packages used in this project

## Support

- GitHub Issues: [Create an issue](https://github.com/MehdiZare/fmp-data/issues)
- Documentation: [Read the docs](./docs)

## Examples

### Interactive Notebooks
- [Financial Agent Tutorial](https://colab.research.google.com/drive/1cSyLX-j9XhyrXyVJ2HwMZJvPy1Lf2CuA?usp=sharing): Build an intelligent financial agent with LangChain integration
- [Basic Usage Examples](./examples): Simple code examples demonstrating key features

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

See [CHANGELOG.md](./CHANGELOG.md) for a list of changes in each release.