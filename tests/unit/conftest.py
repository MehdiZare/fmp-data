# tests/conftest.py
import json
from unittest.mock import Mock, create_autospec

import httpx
import pytest

from fmp_data import FMPDataClient
from fmp_data.config import ClientConfig, LoggingConfig, RateLimitConfig
from fmp_data.models import APIVersion, Endpoint


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
    endpoint.version = APIVersion.STABLE
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
        payload = {} if json_data is None else json_data
        response.json.return_value = payload
        response.text = json.dumps(payload) if payload is not None else ""

        if raise_error:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=Mock(), response=response
            )
        else:
            response.raise_for_status.return_value = None

        return response

    return _create_response
