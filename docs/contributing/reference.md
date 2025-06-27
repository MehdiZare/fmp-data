# docs/api/reference.md
# API Reference

## Client

::: fmp_data.client.FMPDataClient
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
from fmp_data import FMPDataClient

# Initialize client
client = FMPDataClient(api_key="your_api_key")

# Get company profile
profile = client.company.get_profile("AAPL")
print(profile.company_name)
```

### With Error Handling

```python
from fmp_data import FMPClient
from fmp_data.exceptions import RateLimitError

client = FMPClient(api_key="your_api_key") # pragma: allowlist secret

try:
    profile = client.get_company_profile("AAPL")
except RateLimitError:
    print("Rate limit reached, waiting...")
```

### With Custom Configuration

```python
from fmp_data import FMPDataClient

client = FMPDataClient(
    api_key="your_api_key", # pragma: allowlist secret
)
```
