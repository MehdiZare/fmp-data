# FMP Data Client

[![Test](https://github.com/MehdiZare/fmp-data/actions/workflows/test.yml/badge.svg)](https://github.com/MehdiZare/fmp-data/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/MehdiZare/fmp-data/branch/main/graph/badge.svg)](https://codecov.io/gh/MehdiZare/fmp-data)
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

## Installation

```bash
# Using pip
pip install fmp-data

# Using poetry
poetry add fmp-data
```

## Quick Start

```python
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig
from fmp_data.exceptions import FMPError, RateLimitError, AuthenticationError

# Method 1: Initialize with direct API key
client = FMPDataClient(api_key="your_api_key_here")  # pragma: allowlist secret

# Method 2: Initialize from environment variable (FMP_API_KEY)
client = FMPDataClient.from_env()

# Method 3: Initialize with custom configuration
config = ClientConfig(
    api_key="your_api_key_here",  # pragma: allowlist secret
    timeout=30,
    max_retries=3,
    base_url="https://financialmodelingprep.com/api",
    logging=LoggingConfig(level="INFO")
)
client = FMPDataClient(config=config)

# Using with context manager (recommended)
with FMPDataClient(api_key="your_api_key_here") as client:  # pragma: allowlist secret
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
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig, RateLimitConfig

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
            "console": {
                "class_name": "StreamHandler",
                "level": "INFO"
            },
            "file": {
                "class_name": "RotatingFileHandler",
                "level": "DEBUG",
                "filename": "fmp.log",
                "maxBytes": 10485760,
                "backupCount": 5
            }
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

## Releasing New Versions

To release a new version, follow these steps:

1. Ensure all changes are committed and pushed to the `main` branch
2. Update the CHANGELOG.md with the new version changes
3. Create and push a new version tag:

```bash
# For a new release (e.g., v0.1.2)
git tag -a v0.1.2 -m "Release version 0.1.2"
git push origin v0.1.2
```

The CI/CD pipeline will automatically:

Run all tests across Python versions 3.10-3.13
Run style, type and security checks
Publish the package to TestPyPI
Publish the package to PyPI (for non-alpha/beta tags)
Create a GitHub release

Notes:

Version tags must start with 'v' (e.g., v0.1.2)
Alpha/beta versions (e.g., v0.1.2-beta) will only be published to TestPyPI
The package uses poetry-dynamic-versioning to manage versions based on git tags

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- Financial Modeling Prep for providing the API
- Contributors to the project
- Open source packages used in this project

## Support

- GitHub Issues: [Create an issue](https://github.com/MehdiZare/fmp-data/issues)
- Documentation: [Read the docs](./docs)
- Examples: [View examples](./examples)

## Release Notes

See [CHANGELOG.md](./CHANGELOG.md) for a list of changes in each release.