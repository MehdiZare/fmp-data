# docs/contributing/testing.md
# Testing Guide

## Running Tests

1. Run all tests:
```bash
poetry run pytest
```

2. Run with coverage:
```bash
poetry run pytest --cov=fmp_data
```

3. Run specific test file:
```bash
poetry run pytest tests/test_client.py
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_client.py       # API client tests
└── test_exceptions.py   # Exception handling tests
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
def test_get_company_profile(client):
    """Test retrieving company profile."""
    profile = client.get_company_profile("AAPL")
    assert profile.symbol == "AAPL"
```

## Mocking HTTP Requests

We use `responses` to mock HTTP requests:

```python
import responses

@responses.activate
def test_api_call(client):
    # Mock API response
    responses.add(
        responses.GET,
        "https://financialmodelingprep.com/api/v3/profile/AAPL",
        json=[{"symbol": "AAPL"}],
        status=200,
    )

    # Make request
    result = client.get_company_profile("AAPL")

    # Verify result
    assert result.symbol == "AAPL"
```

## Test Coverage

We maintain high test coverage:

- Minimum coverage: 80%
- Coverage report: `poetry run pytest --cov=fmp_data --cov-report=html`
- View report: `open htmlcov/index.html`

## Continuous Integration

Tests run automatically on:
- Every pull request
- Push to main branch
- Release creation

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
