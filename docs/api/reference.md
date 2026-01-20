# API Reference

## Main Clients

### Sync Client

::: fmp_data.client.FMPDataClient
handler: python
options:
show_root_heading: true
show_source: false
members_order: source
docstring_section_style: spacy

### Async Client

::: fmp_data.async_client.AsyncFMPDataClient
handler: python
options:
show_root_heading: true
show_source: false
members_order: source
docstring_section_style: spacy

## Configuration

::: fmp_data.config.ClientConfig
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.config.LoggingConfig
handler: python
options:
show_root_heading: true
show_source: false

## Endpoint Group Clients

The library provides both sync and async versions of each endpoint group client.
All async clients have the same methods as their sync counterparts, but return awaitables.

### Company Client

::: fmp_data.company.CompanyClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.company.AsyncCompanyClient
handler: python
options:
show_root_heading: true
show_source: false

### Market Client

::: fmp_data.market.MarketClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.market.AsyncMarketClient
handler: python
options:
show_root_heading: true
show_source: false

### Fundamental Client

::: fmp_data.fundamental.FundamentalClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.fundamental.AsyncFundamentalClient
handler: python
options:
show_root_heading: true
show_source: false

### Technical Client

::: fmp_data.technical.TechnicalClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.technical.AsyncTechnicalClient
handler: python
options:
show_root_heading: true
show_source: false

### Market Intelligence Client

::: fmp_data.intelligence.MarketIntelligenceClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.intelligence.AsyncMarketIntelligenceClient
handler: python
options:
show_root_heading: true
show_source: false

### Institutional Client

::: fmp_data.institutional.InstitutionalClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.institutional.AsyncInstitutionalClient
handler: python
options:
show_root_heading: true
show_source: false

### Investment Client

::: fmp_data.investment.InvestmentClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.investment.AsyncInvestmentClient
handler: python
options:
show_root_heading: true
show_source: false

### Alternative Markets Client

::: fmp_data.alternative.AlternativeMarketsClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.alternative.AsyncAlternativeMarketsClient
handler: python
options:
show_root_heading: true
show_source: false

### Economics Client

::: fmp_data.economics.EconomicsClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.economics.AsyncEconomicsClient
handler: python
options:
show_root_heading: true
show_source: false

### Batch Client

::: fmp_data.batch.BatchClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.batch.AsyncBatchClient
handler: python
options:
show_root_heading: true
show_source: false

### Transcripts Client

::: fmp_data.transcripts.TranscriptsClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.transcripts.AsyncTranscriptsClient
handler: python
options:
show_root_heading: true
show_source: false

### SEC Client

::: fmp_data.sec.SECClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.sec.AsyncSECClient
handler: python
options:
show_root_heading: true
show_source: false

### Index Client

::: fmp_data.index.IndexClient
handler: python
options:
show_root_heading: true
show_source: false

::: fmp_data.index.AsyncIndexClient
handler: python
options:
show_root_heading: true
show_source: false

## Exceptions

::: fmp_data.exceptions
handler: python
options:
show_root_heading: true
show_source: false

## Data Models

### Company Models

::: fmp_data.company.models
handler: python
options:
show_root_heading: true
show_source: false
filters:
- "!^_"

### Market Models

::: fmp_data.market.models
handler: python
options:
show_root_heading: true
show_source: false
filters:
- "!^_"

### Fundamental Models

::: fmp_data.fundamental.models
handler: python
options:
show_root_heading: true
show_source: false
filters:
- "!^_"

## Usage Examples

### Sync Client Usage

```python
from fmp_data import FMPDataClient

# Initialize from environment
with FMPDataClient.from_env() as client:
    profile = client.company.get_profile("AAPL")
    print(f"Company: {profile.company_name}")

# Manual initialization
client = FMPDataClient(
    api_key="your_api_key", # pragma: allowlist secret
    timeout=30,
    max_retries=3,
    debug=True
)
```

### Async Client Usage

```python
import asyncio
from fmp_data import AsyncFMPDataClient

async def main():
    # Initialize from environment
    async with AsyncFMPDataClient.from_env() as client:
        profile = await client.company.get_profile("AAPL")
        print(f"Company: {profile.company_name}")

    # Manual initialization
    client = AsyncFMPDataClient(
        api_key="your_api_key", # pragma: allowlist secret
        timeout=30,
        max_retries=3,
        debug=True
    )
    try:
        quote = await client.company.get_quote("AAPL")
        print(f"Price: ${quote.price}")
    finally:
        await client.aclose()

asyncio.run(main())
```

### Concurrent Async Requests

```python
import asyncio
from fmp_data import AsyncFMPDataClient

async def fetch_multiple_profiles(symbols: list[str]):
    async with AsyncFMPDataClient.from_env() as client:
        # Fetch all profiles concurrently
        tasks = [client.company.get_profile(symbol) for symbol in symbols]
        profiles = await asyncio.gather(*tasks)

        for profile in profiles:
            print(f"{profile.symbol}: {profile.company_name}")

asyncio.run(fetch_multiple_profiles(["AAPL", "MSFT", "GOOGL"]))
```

### Configuration Examples

```python
from fmp_data import FMPDataClient, ClientConfig, LoggingConfig, LogHandlerConfig

# Custom configuration
config = ClientConfig(
    api_key="your_api_key", # pragma: allowlist secret
    base_url="https://financialmodelingprep.com/api",
    timeout=60,
    max_retries=5,
    logging=LoggingConfig(
        level="INFO",
        handlers={
            "console": LogHandlerConfig(
                class_name="StreamHandler",
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        }
    )
)

client = FMPDataClient(config=config)
```

### Error Handling

```python
from fmp_data import FMPDataClient
from fmp_data.exceptions import (
    FMPError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)

try:
    with FMPDataClient.from_env() as client:
        data = client.company.get_profile("INVALID")
except AuthenticationError:
    print("Check your API key")
except RateLimitError as e:
    print(f"Rate limited. Wait {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except FMPError as e:
    print(f"API error: {e.message}")
```

### Custom Logging

```python
from fmp_data import FMPDataClient, LoggingConfig, LogHandlerConfig, ClientConfig

# Custom logging configuration
logging_config = LoggingConfig(
    level="DEBUG",
    handlers={
        "file": LogHandlerConfig(
            class_name="FileHandler",
            level="DEBUG",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        ),
        "console": LogHandlerConfig(
            class_name="StreamHandler",
            level="INFO",
            format="%(levelname)s - %(message)s"
        )
    }
)

client = FMPDataClient(
    config=ClientConfig(
        api_key="your_api_key",  # pragma: allowlist secret
        logging=logging_config
    )
)
```
