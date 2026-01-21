# fmp-data LLM Guide

Use this file as a quick reference for generating correct usage examples for the
`fmp-data` Python package.

## What this package is
`fmp-data` is a typed Python client for the Financial Modeling Prep (FMP) API.
It supports synchronous and async usage, rate limiting, retries, and optional
LangChain and MCP integrations.

## Setup
- Install: `pip install fmp-data` (or `uv pip install fmp-data`)
- Set API key: `export FMP_API_KEY=...`
- Optional env vars: `FMP_TIMEOUT`, `FMP_MAX_RETRIES`, `FMP_BASE_URL`
- Rate limits: `FMP_DAILY_LIMIT`, `FMP_REQUESTS_PER_SECOND`,
  `FMP_REQUESTS_PER_MINUTE`

## Quickstart (sync)
```python
from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    quote = client.company.get_quote("AAPL")
    profile = client.company.get_profile("AAPL")
    prices = client.company.get_historical_prices(
        symbol="AAPL", from_date="2024-01-01", to_date="2024-03-01"
    )
    gainers = client.market.get_gainers()
    ratios = client.fundamental.get_financial_ratios("AAPL")
    print(quote.price, profile.company_name)
```

## Quickstart (async)
```python
import asyncio
from fmp_data import AsyncFMPDataClient

async def main():
    async with AsyncFMPDataClient.from_env() as client:
        quote = await client.company.get_quote("AAPL")
        rsi = await client.technical.get_rsi("AAPL", period_length=14)
        return quote, rsi

asyncio.run(main())
```

## Client surface
Access API groups via the main client:
- `client.company`
- `client.market`
- `client.fundamental`
- `client.technical`
- `client.intelligence`
- `client.institutional`
- `client.investment`
- `client.alternative`
- `client.economics`
- `client.batch`
- `client.transcripts`
- `client.sec`
- `client.index`

Async equivalents exist on `AsyncFMPDataClient` with the same method names.

## Responses and data handling
Endpoints return Pydantic models (or lists of models). Use attributes directly
or call `model_dump()` / `model_dump_json()` for raw data.

## Errors to handle
- `ConfigError` for missing or invalid config (e.g., no API key)
- `AuthenticationError` for invalid credentials
- `RateLimitError` for rate limiting
- `ValidationError` for input validation issues
- `FMPError` for API-related failures

## Optional integrations
- LangChain extras: `pip install "fmp-data[langchain]"`
  - Vector store helper: `from fmp_data import create_vector_store`
  - 2.0.0+: `EndpointVectorStore.load(..., allow_dangerous_deserialization=True)` is
    required for cached stores and should only be used with trusted cache sources.
- MCP server extras: `pip install "fmp-data[mcp]"`
  - CLI: `fmp-mcp setup` or `fmp-mcp`
  - Server API: `from fmp_data.mcp.server import create_app`

## Pointers
- Examples: `examples/`
- MCP docs: `docs/mcp/claude_desktop.md`
- Package entrypoints: `fmp_data/__init__.py`
