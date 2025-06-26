# tests/conftest.py
"""
Root conftest.py combining existing fixtures with dependency management.

This file handles:
- All existing test fixtures (preserved)
- Detection of available optional dependencies
- Automatic test skipping based on markers and dependencies
- Safe imports that don't fail when dependencies are missing
"""
import importlib.util
import json
import os
import warnings
from unittest.mock import Mock, create_autospec

import httpx
import pytest

# Safe imports for core functionality - these should always work
try:
    from fmp_data import FMPDataClient
    from fmp_data.config import ClientConfig, LoggingConfig, RateLimitConfig
    from fmp_data.models import APIVersion, Endpoint
except ImportError as e:
    pytest.skip(f"Core fmp_data modules not available: {e}", allow_module_level=True)


# ============================================================================
# DEPENDENCY DETECTION (New)
# ============================================================================


def _is_package_available(package_name: str) -> bool:
    """Check if a package is available for import."""
    return importlib.util.find_spec(package_name) is not None


# Check available dependencies at import time
LANGCHAIN_AVAILABLE = _is_package_available("langchain")
OPENAI_AVAILABLE = _is_package_available("openai")
FAISS_AVAILABLE = _is_package_available("faiss")


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with dependency information."""
    # Add dependency info to config
    config._langchain_available = LANGCHAIN_AVAILABLE  # type: ignore
    config._openai_available = OPENAI_AVAILABLE  # type: ignore
    config._fmp_api_key = os.getenv("FMP_TEST_API_KEY")  # type: ignore
    config._openai_api_key = os.getenv("OPENAI_API_KEY")  # type: ignore

    # Print dependency status
    if config.option.verbose >= 1:
        print("\n🔍 Dependency Check:")
        print(f"   LangChain: {'✅' if LANGCHAIN_AVAILABLE else '❌'}")
        print(f"   OpenAI: {'✅' if OPENAI_AVAILABLE else '❌'}")
        print(f"   FAISS: {'✅' if FAISS_AVAILABLE else '❌'}")
        print(f"   FMP API Key: {'✅' if config._fmp_api_key else '❌'}")  # type: ignore
        print(f"   OpenAI API Key: {'✅' if config._openai_api_key else '❌'}")  # type: ignore


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to skip tests based on available dependencies."""

    for item in items:
        # Auto-mark tests based on location
        if "/unit/" in str(item.fspath) and "/lc/" not in str(item.fspath):
            item.add_marker(pytest.mark.core)
            item.add_marker(pytest.mark.unit)
        elif "/lc/" in str(item.fspath):
            item.add_marker(pytest.mark.langchain)
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Skip LangChain tests if LangChain not available
        if item.get_closest_marker("langchain") and not LANGCHAIN_AVAILABLE:
            item.add_marker(
                pytest.mark.skip(
                    reason="LangChain dependencies not installed. "
                    "Install with: pip install 'fmp-data[langchain]'"
                )
            )

        # Skip integration tests if no API key
        if item.get_closest_marker("integration") and not config._fmp_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="FMP_TEST_API_KEY not set"))

        # Skip tests requiring API keys
        if item.get_closest_marker("requires_api_key") and not config._fmp_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="FMP_TEST_API_KEY not set"))

        if item.get_closest_marker("requires_openai_key") and not config._openai_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="OPENAI_API_KEY not set"))


def pytest_ignore_collect(collection_path: str, config: pytest.Config) -> bool | None:
    """Skip collecting certain test files based on dependencies."""
    path_str = str(collection_path)

    # Skip LangChain test files if LangChain not available
    if "/lc/" in path_str or "langchain" in path_str.lower():
        if not LANGCHAIN_AVAILABLE:
            return True

    return None


@pytest.fixture(autouse=True)
def suppress_dependency_warnings() -> None:
    """Automatically suppress dependency-related warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ImportWarning)
        warnings.filterwarnings("ignore", message=".*langchain.*")
        warnings.filterwarnings("ignore", message=".*faiss.*")
        warnings.filterwarnings("ignore", message=".*openai.*")
        yield


# ============================================================================
# DEPENDENCY STATUS FIXTURES (New)
# ============================================================================


@pytest.fixture(scope="session")
def langchain_available() -> bool:
    """Fixture indicating if LangChain is available."""
    return LANGCHAIN_AVAILABLE


@pytest.fixture(scope="session")
def openai_available() -> bool:
    """Fixture indicating if OpenAI is available."""
    return OPENAI_AVAILABLE


@pytest.fixture(scope="session")
def has_fmp_api_key() -> bool:
    """Fixture indicating if FMP API key is available."""
    return bool(os.getenv("FMP_TEST_API_KEY"))


@pytest.fixture(scope="session")
def has_openai_api_key() -> bool:
    """Fixture indicating if OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY"))


# ============================================================================
# EXISTING FIXTURES (Preserved)
# ============================================================================


@pytest.fixture
def client_config():
    """Create a test client configuration"""
    return ClientConfig(
        api_key="test_api_key",
        timeout=5,
        max_retries=1,
        max_rate_limit_retries=5,
        base_url="https://test.financialmodelingprep.com/api",
        logging=LoggingConfig(
            level="ERROR",
            handlers={
                "console": {
                    "class_name": "StreamHandler",
                    "level": "ERROR",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }
            },
        ),
        rate_limit=RateLimitConfig(
            daily_limit=1000, requests_per_second=10, requests_per_minute=300
        ),
    )


@pytest.fixture
def fmp_client(client_config):
    """Create a test FMP client"""
    client = FMPDataClient(config=client_config)
    yield client
    client.close()


@pytest.fixture
def mock_company_profile():
    """Complete mock company profile data"""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "beta": 1.2,
        "volAvg": 82034567,
        "mktCap": 2500000000000,
        "lastDiv": 0.88,
        "range": "120.5-155.75",
        "changes": 2.35,
        "companyName": "Apple Inc.",
        "currency": "USD",
        "cik": "0000320193",
        "isin": "US0378331005",
        "cusip": "037833100",
        "exchange": "NASDAQ",
        "exchangeShortName": "NASDAQ",
        "industry": "Consumer Electronics",
        "website": "https://www.apple.com",
        "description": "Apple Inc. designs, manufactures, and markets smartphones...",
        "ceo": "Tim Cook",
        "sector": "Technology",
        "country": "US",
        "fullTimeEmployees": "147000",
        "phone": "14089961010",
        "address": "One Apple Park Way",
        "city": "Cupertino",
        "state": "CA",
        "zip": "95014",
        "dcfDiff": 1.5,
        "dcf": 155.75,
        "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
        "ipoDate": "1980-12-12",
        "defaultImage": False,
        "isEtf": False,
        "isActivelyTrading": True,
        "isAdr": False,
        "isFund": False,
    }


@pytest.fixture
def mock_api_response():
    """Mock validated API response with proper attributes"""
    mock_resp = Mock()
    mock_resp.text = ""
    mock_resp.status_code = 200
    mock_resp.json.return_value = {}
    return mock_resp


@pytest.fixture
def mock_company_executive():
    """Mock company executive data"""
    return {
        "title": "Chief Executive Officer",
        "name": "Tim Cook",
        "pay": 3000000,
        "currencyPay": "USD",
        "gender": "M",
        "yearBorn": 1960,
        "titleSince": "2011-08-24",
    }


@pytest.fixture
def mock_search_result():
    """Mock company search result"""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "currency": "USD",
        "stockExchange": "NASDAQ",
        "exchangeShortName": "NASDAQ",
    }


@pytest.fixture
def mock_endpoint():
    """Create a mock endpoint with proper response model"""
    endpoint = create_autospec(Endpoint)
    endpoint.name = "test_endpoint"
    endpoint.version = APIVersion.V3
    endpoint.path = "test/path"
    endpoint.validate_params.return_value = {}
    endpoint.build_url.return_value = "https://test.url"
    endpoint.response_model = Mock()
    endpoint.response_model.model_validate = Mock(return_value={"test": "data"})
    return endpoint


@pytest.fixture
def mock_company_response():
    """Mock company profile response"""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "beta": 1.2,
        "volAvg": 82034567,
        "mktCap": 2500000000000,
        "lastDiv": 0.88,
        "range": "120.5-155.75",
        "changes": 2.35,
        "companyName": "Apple Inc.",
        "currency": "USD",
        "cik": "0000320193",
        "isin": "US0378331005",
        "cusip": "037833100",
        "exchange": "NASDAQ",
        "exchangeShortName": "NASDAQ",
        "industry": "Consumer Electronics",
        "website": "https://www.apple.com",
        "description": "Apple Inc. designs, manufactures, and markets smartphones...",
        "ceo": "Tim Cook",
        "sector": "Technology",
        "country": "US",
        "fullTimeEmployees": "147000",
        "phone": "14089961010",
        "address": "One Apple Park Way",
        "city": "Cupertino",
        "state": "CA",
        "zip": "95014",
        "dcfDiff": 1.5,
        "dcf": 155.75,
        "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
        "ipoDate": "1980-12-12",
        "defaultImage": False,
        "isEtf": False,
        "isActivelyTrading": True,
        "isAdr": False,
        "isFund": False,
    }


@pytest.fixture
def mock_error_response():
    """Mock error response"""

    def _create_error(message="Error occurred", code=500):
        return {"message": message, "code": str(code)}

    return _create_error


@pytest.fixture
def mock_response():
    """Create a mock HTTP response"""

    def _create_response(status_code=200, json_data=None, raise_error=False):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = json.dumps(json_data) if json_data else ""

        if raise_error:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=Mock(), response=response
            )
        else:
            response.raise_for_status.return_value = None

        return response

    return _create_response
