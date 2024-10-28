# docs/index.md
# FMP Data

A robust Python client for Financial Modeling Prep API with rate limiting, caching, and retry capabilities.

## Installation

```bash
pip install fmp-data
```

Or with Poetry:
```bash
poetry add fmp-data
```

## Quick Start

```python
from fmp_data import FMPClient

# Initialize client
client = FMPClient(api_key="your_api_key")

# Get company profile
profile = client.get_company_profile("AAPL")

# Get financial statements
income_statement = client.get_income_statement("AAPL")
```

## Features

- Rate limiting with automatic backoff
- Response caching
- Retry strategies for failed requests
- Type hints and data validation using Pydantic
- Comprehensive error handling
- Async support

## Documentation

- [Development Setup](contributing/development.md): How to set up your development environment
- [API Reference](api/reference.md): Detailed API documentation
- [Contributing Guide](contributing/development.md): How to contribute to the project
