# docs/api/reference.md
# API Reference

## Client

::: fmp_data.client.FMPClient
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

## Models

::: fmp_data.models
    handler: python
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Usage

```python
from fmp_data import FMPClient

# Initialize client
client = FMPClient(api_key="your_api_key")

# Get company profile
profile = client.get_company_profile("AAPL")
print(profile.company_name)
```

### With Error Handling

```python
from fmp_data import FMPClient
from fmp_data.exceptions import RateLimitExceeded

client = FMPClient(api_key="your_api_key") # pragma: allowlist secret

try:
    profile = client.get_company_profile("AAPL")
except RateLimitExceeded:
    print("Rate limit reached, waiting...")
```

### With Custom Configuration

```python
from fmp_data import FMPClient

client = FMPClient(
    api_key="your_api_key", # pragma: allowlist secret
    rate_limit=100,  # requests per minute
    cache_ttl=300,   # cache for 5 minutes
    retries=3        # retry failed requests
)
```
