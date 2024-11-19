import json
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest
from pydantic import BaseModel
from tenacity import RetryError

from fmp_data.base import BaseClient, EndpointGroup
from fmp_data.config import ClientConfig
from fmp_data.exceptions import (
    AuthenticationError,
    FMPError,
    RateLimitError,
    ValidationError,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)


class SampleResponse(BaseModel):
    test: str


@pytest.fixture
def mock_response():
    def _create_response(status_code=200, json_data=None):
        mock = Mock()
        mock.status_code = status_code
        mock.json.return_value = json_data or {}
        mock.raise_for_status = Mock()
        if status_code >= 400:
            mock.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=Mock(), response=mock
            )
        return mock

    return _create_response


@pytest.fixture
def mock_endpoint():
    """Create mock endpoint with proper response model"""
    endpoint = Mock()
    endpoint.name = "test_endpoint"
    endpoint.version = APIVersion.V3
    endpoint.path = "test/path"
    endpoint.validate_params.return_value = {}
    endpoint.build_url.return_value = "https://test.com/api/v3/test"
    endpoint.get_query_params = Mock(
        return_value={}
    )  # Return empty dict instead of Mock
    endpoint.response_model = Mock()
    endpoint.response_model.model_validate = Mock(return_value={"test": "data"})
    return endpoint


@pytest.fixture
def test_endpoint():
    return Endpoint(
        name="test",
        path="test/{symbol}",
        version=APIVersion.V3,
        description="Test endpoint",
        mandatory_params=[
            EndpointParam(
                name="symbol",
                location=ParamLocation.PATH,
                param_type=ParamType.STRING,
                required=True,
                description="Stock symbol (ticker)",
            ),
        ],
        optional_params=[
            EndpointParam(
                name="limit",
                location=ParamLocation.QUERY,
                param_type=ParamType.STRING,
                required=True,
                description="Result limit",
            )
        ],
        response_model=SampleResponse,
    )


@pytest.fixture
def client_config():
    return ClientConfig(api_key="test_key", base_url="https://api.test.com")


@pytest.fixture
def base_client(client_config):
    return BaseClient(client_config)


@patch("httpx.Client.request")
def test_base_client_request(mock_request, mock_endpoint, client_config, mock_response):
    """Test base client request method"""
    mock_data = {"test": "data"}
    mock_request.return_value = mock_response(status_code=200, json_data=mock_data)

    # Configure mock endpoint
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.path = "test/path"
    mock_endpoint.validate_params.return_value = {}
    mock_endpoint.build_url.return_value = "https://test.url"
    mock_endpoint.get_query_params.return_value = {}
    mock_endpoint.response_model = SampleResponse

    client = BaseClient(client_config)
    result = client.request(mock_endpoint)

    # Verify response processing
    assert isinstance(result, SampleResponse)
    assert result.test == "data"

    # Verify the request was made with correct parameters
    mock_request.assert_called_once()
    mock_endpoint.validate_params.assert_called_once()
    mock_endpoint.build_url.assert_called_once()


@patch("httpx.Client")
def test_base_client_initialization(mock_client_class, client_config):
    """Test base client initialization"""
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    client = BaseClient(client_config)
    assert client.config == client_config
    assert client.logger is not None
    mock_client_class.assert_called_once()


def test_base_client_query_params(client_config):
    """Test query parameter handling"""
    client = BaseClient(client_config)
    test_params = {"param1": "value1"}
    endpoint = Mock()
    endpoint.get_query_params.return_value = test_params

    # Mock the request to avoid actual HTTP call
    with patch.object(client.client, "request") as mock_request:
        mock_request.return_value.json.return_value = {}
        client.request(endpoint)

        # Verify API key was added to params
        called_params = mock_request.call_args[1]["params"]
        assert called_params["apikey"] == client_config.api_key
        assert called_params["param1"] == "value1"


def test_handle_response_errors(base_client, mock_response):
    """Test response error handling"""
    # Test rate limit error
    response = mock_response(
        status_code=429, json_data={"message": "Rate limit exceeded"}
    )
    with pytest.raises(RateLimitError):
        base_client.handle_response(response)

    # Test authentication error
    response = mock_response(status_code=401, json_data={"message": "Invalid API key"})
    with pytest.raises(AuthenticationError):
        base_client.handle_response(response)

    # Test validation error
    response = mock_response(
        status_code=400, json_data={"message": "Invalid parameters"}
    )
    with pytest.raises(ValidationError):
        base_client.handle_response(response)

    # Test general API error
    response = mock_response(status_code=500, json_data={"message": "Server error"})
    with pytest.raises(FMPError):
        base_client.handle_response(response)


def test_endpoint_group():
    """Test endpoint group functionality"""
    client = Mock()
    group = EndpointGroup(client)
    assert group.client == client


def test_request_with_retry(base_client, mock_endpoint, mock_response):
    """Test request retry functionality"""
    # Create a mock that fails twice then succeeds
    mock_request = Mock()
    mock_request.side_effect = [
        httpx.TimeoutException("Timeout"),  # First attempt fails
        httpx.NetworkError("Network Error"),  # Second attempt fails
        mock_response(status_code=200, json_data={"test": "data"}),  # Third succeeds
    ]

    # Configure mock_endpoint's response model
    mock_endpoint.response_model = SampleResponse
    mock_endpoint.method.value = "GET"

    with patch.object(base_client.client, "request", mock_request):
        result = base_client.request(mock_endpoint)

        # Verify result
        assert isinstance(result, SampleResponse)
        assert result.test == "data"


def test_client_cleanup(base_client):
    """Test client cleanup"""
    # Store reference to client
    client = base_client.client

    # Close the client
    base_client.close()

    # Verify the client was closed
    assert client.is_closed

    # Test double cleanup doesn't raise
    base_client.close()


def test_request_rate_limit(base_client, test_endpoint):
    """Test rate limiting in requests"""
    # Simulate rate limit exceeded
    base_client._rate_limiter._daily_requests = (
        base_client._rate_limiter.quota_config.daily_limit + 1
    )

    with pytest.raises(RateLimitError):
        base_client.request(test_endpoint, symbol="AAPL")


@pytest.mark.asyncio
async def test_request_async(base_client, mock_endpoint):
    """Test async request handling"""
    # Configure mock endpoint properly
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.validate_params.return_value = {}
    mock_endpoint.build_url.return_value = "https://test.url"
    mock_endpoint.get_query_params.return_value = {}
    mock_endpoint.response_model = SampleResponse
    mock_endpoint.response_model.model_validate = Mock(
        return_value=SampleResponse(test="data")
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}

    with patch("httpx.AsyncClient.request", return_value=mock_response):
        result = await base_client.request_async(mock_endpoint)
        assert isinstance(result, SampleResponse)
        assert result.test == "data"


def test_process_response(mock_endpoint):
    """Test response processing"""
    # Create mock endpoint with proper response model
    mock_endpoint.response_model = SampleResponse

    # Test successful response
    data = {"test": "data"}
    result = BaseClient._process_response(mock_endpoint, data)
    assert isinstance(result, SampleResponse)
    assert result.test == "data"

    # Test error response
    with pytest.raises(FMPError):
        BaseClient._process_response(mock_endpoint, {"message": "Error"})


def test_invalid_json_response(base_client, mock_response):
    """Test handling of invalid JSON responses"""
    response = mock_response(status_code=200)
    response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

    with pytest.raises(FMPError) as exc_info:
        base_client.handle_response(response)
    assert "Invalid JSON response" in str(exc_info.value)


@patch("httpx.Client.request")
def test_request_max_retries_exceeded(mock_request, mock_endpoint, base_client):
    """Test that requests stop after max retries"""
    # Make the request always fail with a timeout
    mock_request.side_effect = httpx.TimeoutException("Timeout")

    # Attempt request and verify it fails with RetryError
    with pytest.raises(RetryError):
        base_client.request(mock_endpoint)

    # Verify the number of retry attempts
    assert mock_request.call_count > 1  # Should have multiple attempts


@patch("httpx.Client.request")
def test_request_with_retry_success(mock_request, mock_endpoint, base_client):
    """Test successful retry after failures"""
    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {"test": "data"}

    # Configure mock endpoint
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    mock_endpoint.validate_params.return_value = {}
    mock_endpoint.build_url.return_value = "https://test.url"
    mock_endpoint.get_query_params.return_value = {}

    # Set up retry sequence
    mock_request.side_effect = [
        httpx.TimeoutException("Timeout"),  # First attempt fails
        success_response,  # Second attempt succeeds
    ]

    result = base_client.request(mock_endpoint)

    # Verify result and retry behavior
    assert isinstance(result, SampleResponse)
    assert result.test == "data"
    assert mock_request.call_count == 2


@patch("httpx.Client.request")
def test_request_non_retryable_error(mock_request, mock_endpoint, base_client):
    """Test that non-retryable errors aren't retried"""
    mock_request.side_effect = ValueError("Non-retryable error")

    with pytest.raises(ValueError):
        base_client.request(mock_endpoint)

    assert mock_request.call_count == 1  # Should not retry
