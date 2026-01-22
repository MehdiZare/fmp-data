import json
from unittest.mock import MagicMock, Mock, patch

import httpx
from pydantic import BaseModel
import pytest

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
        payload = json_data or {}
        mock.json.return_value = payload
        mock.text = json.dumps(payload)
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
    endpoint.version = APIVersion.STABLE
    endpoint.path = "test/path"
    endpoint.validate_params.return_value = {}
    endpoint.build_url.return_value = "https://test.com/stable/test"
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
        version=APIVersion.STABLE,
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
    endpoint.response_model = dict

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

    with (
        patch.object(base_client.client, "request", mock_request),
        patch("tenacity.nap.sleep", return_value=None),
    ):
        result = base_client.request(mock_endpoint)

        # Verify result
        assert isinstance(result, SampleResponse)
        assert result.test == "data"


def test_parse_json_response_invalid_type():
    """Test parsing raises for unexpected JSON types."""
    response = Mock()
    response.json.return_value = "oops"

    with pytest.raises(FMPError, match="Unexpected response type"):
        BaseClient._parse_json_response(response)


def test_get_error_details_json_decode_error():
    """Test error details fallback when JSON decode fails."""
    response = Mock()
    response.json.side_effect = json.JSONDecodeError("bad", "doc", 0)
    response.content = b"not json"

    details = BaseClient._get_error_details(response)

    assert details == {"raw_content": "not json"}


def test_handle_http_status_error_404_empty_payloads(base_client):
    """Test 404 errors return empty payloads without raising."""
    request = httpx.Request("GET", "https://example.com")
    list_response = httpx.Response(404, json=[])
    list_error = httpx.HTTPStatusError(
        "Not found", request=request, response=list_response
    )
    assert base_client._handle_http_status_error(list_error) == []

    dict_response = httpx.Response(404, json={})
    dict_error = httpx.HTTPStatusError(
        "Not found", request=request, response=dict_response
    )
    assert base_client._handle_http_status_error(dict_error) == {}


def test_handle_http_status_error_uses_retry_after_header(base_client):
    """Test 429 handling uses Retry-After header when present."""
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        429,
        request=request,
        headers={"Retry-After": "12"},
        json={"message": "Rate limit exceeded"},
    )
    error = httpx.HTTPStatusError(
        "Too many requests", request=request, response=response
    )

    with pytest.raises(RateLimitError) as exc_info:
        base_client._handle_http_status_error(error)

    assert exc_info.value.retry_after == 12.0


@pytest.mark.parametrize(
    "payload",
    [
        {"Error Message": "boom"},
        {"message": "boom"},
        {"error": "boom"},
    ],
)
def test_check_error_response_raises(payload):
    """Test error payloads raise FMPError."""
    with pytest.raises(FMPError):
        BaseClient._check_error_response(payload)


def test_validate_single_item_primitives_and_model():
    """Test validation handles primitive and model responses."""

    class SingleField(BaseModel):
        value: int

    endpoint = Mock()
    endpoint.response_model = int
    assert BaseClient._validate_single_item(endpoint, "5") == 5

    endpoint.response_model = dict
    assert BaseClient._validate_single_item(endpoint, {"key": "value"}) == {
        "key": "value"
    }

    endpoint.response_model = SingleField
    result = BaseClient._validate_single_item(endpoint, 7)
    assert isinstance(result, SingleField)
    assert result.value == 7


def test_process_response_raises_on_error_message():
    """Test process_response raises on error payloads."""
    endpoint = Mock()
    endpoint.response_model = dict

    with pytest.raises(FMPError):
        BaseClient._process_response(endpoint, {"message": "boom"})


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
    with (
        patch.object(
            base_client._rate_limiter, "should_allow_request", return_value=False
        ),
        patch.object(base_client._rate_limiter, "get_wait_time", return_value=0.0),
        patch.object(
            base_client, "_handle_rate_limit", side_effect=RateLimitError("rl")
        ),
    ):
        with pytest.raises(RateLimitError):
            base_client._execute_request(test_endpoint, symbol="AAPL")


@pytest.mark.asyncio
async def test_request_async(base_client, mock_endpoint):
    """Test async request handling"""
    from unittest.mock import AsyncMock

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
    mock_response.aclose = AsyncMock()

    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(return_value=mock_response)

    with patch.object(
        base_client, "_setup_async_client", return_value=mock_async_client
    ):
        result = await base_client.request_async(mock_endpoint)
        assert isinstance(result, SampleResponse)
        assert result.test == "data"

    await base_client.aclose()


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

    # Attempt request and verify it fails with the underlying error (reraise=True)
    with (
        patch("tenacity.nap.sleep", return_value=None),
        pytest.raises(httpx.TimeoutException),
    ):
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

    with patch("tenacity.nap.sleep", return_value=None):
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


def test_request_retries_on_http_5xx(base_client):
    """Test that 5xx HTTPStatusError is retried"""
    response = Mock()
    response.status_code = 500
    http_error = httpx.HTTPStatusError(
        "Server error", request=Mock(), response=response
    )

    with (
        patch.object(
            base_client, "_execute_request", side_effect=[http_error, "ok"]
        ) as mock_execute,
        patch("tenacity.nap.sleep", return_value=None),
    ):
        result = base_client.request(Mock())

    assert result == "ok"
    assert mock_execute.call_count == 2


def test_request_does_not_retry_on_http_4xx(base_client):
    """Test that 4xx HTTPStatusError is not retried"""
    response = Mock()
    response.status_code = 404
    http_error = httpx.HTTPStatusError("Not found", request=Mock(), response=response)

    with patch.object(
        base_client, "_execute_request", side_effect=http_error
    ) as mock_execute:
        with pytest.raises(httpx.HTTPStatusError):
            base_client.request(Mock())

    assert mock_execute.call_count == 1


class TestRequestLatencyLogging:
    """Tests for request latency logging."""

    @patch("httpx.Client.request")
    def test_request_logs_latency(self, mock_request, mock_endpoint, client_config):
        """Test that request logs latency metrics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response

        # Configure mock endpoint
        mock_endpoint.method = MagicMock()
        mock_endpoint.method.value = "GET"
        mock_endpoint.response_model = SampleResponse

        client = BaseClient(client_config)

        with patch.object(client.logger, "debug") as mock_debug:
            client.request(mock_endpoint)

            # Should have logged latency
            debug_calls = [str(call) for call in mock_debug.call_args_list]
            latency_logged = any("latency_ms" in call for call in debug_calls)
            assert latency_logged


class TestMetricsCallback:
    """Tests for the metrics callback functionality."""

    def test_metrics_callback_called_on_success(self, mock_endpoint):
        """Test that metrics callback is called on successful request."""
        callback_calls = []

        def metrics_callback(**kwargs):
            callback_calls.append(kwargs)

        config = ClientConfig(
            api_key="test_key",
            base_url="https://api.test.com",
            metrics_callback=metrics_callback,
        )
        client = BaseClient(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}

        # Configure mock endpoint
        mock_endpoint.method = MagicMock()
        mock_endpoint.method.value = "GET"
        mock_endpoint.response_model = SampleResponse

        with patch.object(client.client, "request", return_value=mock_response):
            client.request(mock_endpoint)

        # Verify callback was called
        assert len(callback_calls) == 1
        call = callback_calls[0]
        assert "endpoint_name" in call
        assert "latency_ms" in call
        assert "success" in call
        assert call["success"] is True
        assert call["status_code"] == 200

    def test_metrics_callback_called_on_failure(self, mock_endpoint):
        """Test that metrics callback is called even on request failure."""
        callback_calls = []

        def metrics_callback(**kwargs):
            callback_calls.append(kwargs)

        config = ClientConfig(
            api_key="test_key",
            base_url="https://api.test.com",
            metrics_callback=metrics_callback,
        )
        client = BaseClient(config)

        # Configure mock endpoint
        mock_endpoint.method = MagicMock()
        mock_endpoint.method.value = "GET"
        mock_endpoint.response_model = SampleResponse

        # Make the request fail
        with patch.object(
            client.client, "request", side_effect=httpx.TimeoutException("Timeout")
        ):
            with patch("tenacity.nap.sleep", return_value=None):
                with pytest.raises(httpx.TimeoutException):
                    client.request(mock_endpoint)

        # Callback should have been called for each attempt
        assert len(callback_calls) >= 1
        # At least the last call should have success=False
        last_call = callback_calls[-1]
        assert last_call["success"] is False

    def test_metrics_callback_exception_doesnt_break_request(self, mock_endpoint):
        """Test that a failing metrics callback doesn't break the request."""

        def failing_callback(**_kwargs):
            raise RuntimeError

        config = ClientConfig(
            api_key="test_key",
            base_url="https://api.test.com",
            metrics_callback=failing_callback,
        )
        client = BaseClient(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}

        # Configure mock endpoint
        mock_endpoint.method = MagicMock()
        mock_endpoint.method.value = "GET"
        mock_endpoint.response_model = SampleResponse

        with patch.object(client.client, "request", return_value=mock_response):
            # Request should still succeed even if callback fails
            result = client.request(mock_endpoint)
            assert isinstance(result, SampleResponse)
            assert result.test == "data"

    def test_no_metrics_callback_by_default(self, base_client):
        """Test that metrics callback is None by default."""
        assert base_client.config.metrics_callback is None


class TestUnwrapSingle:
    """Tests for the _unwrap_single helper method."""

    def test_unwrap_single_from_list(self):
        """Test unwrapping a single item from a list."""
        result = EndpointGroup._unwrap_single(
            [SampleResponse(test="data")], SampleResponse
        )
        assert isinstance(result, SampleResponse)
        assert result.test == "data"

    def test_unwrap_single_not_list(self):
        """Test unwrapping when result is already a single item."""
        item = SampleResponse(test="data")
        result = EndpointGroup._unwrap_single(item, SampleResponse)
        assert result is item
        assert result.test == "data"

    def test_unwrap_single_empty_list_allow_none(self):
        """Test unwrapping empty list with allow_none=True returns None."""
        result = EndpointGroup._unwrap_single([], SampleResponse, allow_none=True)
        assert result is None

    def test_unwrap_single_empty_list_raises(self):
        """Test unwrapping empty list with allow_none=False raises ValueError."""
        with pytest.raises(ValueError, match="Expected at least one SampleResponse"):
            EndpointGroup._unwrap_single([], SampleResponse, allow_none=False)

    def test_unwrap_single_multiple_items_returns_first(self):
        """Test unwrapping list with multiple items returns the first."""
        items = [SampleResponse(test="first"), SampleResponse(test="second")]
        result = EndpointGroup._unwrap_single(items, SampleResponse)
        assert isinstance(result, SampleResponse)
        assert result.test == "first"
