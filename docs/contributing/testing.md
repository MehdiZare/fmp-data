# docs/contributing/testing.md
# Testing Guide

## Running Tests

1. Run all tests:
```bash
uv run pytest
```

2. Run with coverage:
```bash
uv run pytest --cov=fmp_data
```

3. Run specific test file:
```bash
uv run pytest tests/unit/test_client.py
```

4. Run integration tests with VCR replay (default, fast):
```bash
FMP_VCR_RECORD=none uv run pytest tests/integration/
```

5. Record or refresh VCR cassettes (live API, slower):
```bash
FMP_TEST_API_KEY=your_test_api_key FMP_VCR_RECORD=new_episodes uv run pytest tests/integration/  # pragma: allowlist secret
```

6. Record only the tests you're touching:
```bash
FMP_TEST_API_KEY=your_test_api_key FMP_VCR_RECORD=new_episodes uv run pytest tests/integration/test_sec.py  # pragma: allowlist secret
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
└── integration/         # Integration tests
```

## Writing Tests

1. **Fixtures**: Add shared fixtures to `conftest.py`:
```python
import pytest

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def client(api_key):
    from fmp_data import FMPDataClient
    return FMPDataClient(api_key=api_key)
```

2. **Test Files**: Create test files with descriptive names:
```python
from unittest.mock import Mock

from fmp_data.company.models import CompanyProfile

def test_get_company_profile(client):
    """Test retrieving company profile."""
    client.company.client.request = Mock(
        return_value=[CompanyProfile(symbol="AAPL")]
    )
    profile = client.company.get_profile("AAPL")
    assert profile.symbol == "AAPL"
```

## Mocking HTTP Requests

Mock the client's internal request method in unit tests to avoid real HTTP calls:

```python
from unittest.mock import Mock

from fmp_data.company.models import CompanyProfile

def test_api_call(client):
    # Mock API response at the client request layer
    client.company.client.request = Mock(
        return_value=[CompanyProfile(symbol="AAPL")]
    )

    # Make request through business logic
    result = client.company.get_profile("AAPL")

    # Verify result
    assert result.symbol == "AAPL"
```

## Test Coverage

We maintain high test coverage:

- Minimum coverage: 80%
- Coverage report: `uv run pytest --cov=fmp_data --cov-report=html`
- View report: `open htmlcov/index.html`

## Continuous Integration

Tests run automatically on:
- Every pull request
- Push to main branch
- Release creation
Coverage is collected in a dedicated CI job separate from the test matrix.

## Best Practices

1. **Test Organization**:
   - One test file per module
   - Descriptive test names
   - Group related tests in classes

2. **Test Data**:
   - Use fixtures for shared data
   - Mock external API calls
   - Use realistic test data

3. **Assertions**:
   - Be specific in assertions
   - Test edge cases
   - Handle exceptions properly
