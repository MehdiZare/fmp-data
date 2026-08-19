import json
import logging
import traceback
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
from pydantic import BaseModel, ConfigDict
import pytest

from fmp_data.base import (
    AsyncEndpointGroup,
    BaseClient,
    EndpointGroup,
    _origin,
    _reject_cross_origin_redirect,
    _sanitize_error_details,
    _sanitize_error_value,
)
from fmp_data.config import ClientConfig
from fmp_data.exceptions import (
    AuthenticationError,
    FMPError,
    FMPNetworkError,
    FMPTimeoutError,
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
        # Real responses carry bytes here; see the note in tests/unit/conftest.py.
        mock.content = mock.text.encode()
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
                description="Stock symbol (ticker)",
            ),
        ],
        optional_params=[
            EndpointParam(
                name="limit",
                location=ParamLocation.QUERY,
                param_type=ParamType.STRING,
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

        # Verify API key was added to params.
        # Assert the literal value, not `== client_config.api_key`: with
        # SecretStr fields that comparison passes vacuously the moment both
        # sides are masked, so it would go green on a client sending
        # `apikey=**********`. httpx accepts a SecretStr and stringifies it,
        # so that failure is silent (#252).
        called_params = mock_request.call_args[1]["params"]
        assert called_params["apikey"] == client_config.api_key.get_secret_value()
        assert isinstance(called_params["apikey"], str)
        assert set(called_params["apikey"]) != {"*"}
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


def test_get_error_details_redacts_api_keys():
    """Error details should not preserve reflected API keys."""
    fake_key_value = "SECRET_FMP_KEY"
    response = Mock()
    response.json.return_value = {
        "url": f"https://example.test/path?apikey={fake_key_value}&symbol=AAPL",
        "encoded": f"apikey%3D{fake_key_value}%26symbol%3DAAPL",
        "apikey": fake_key_value,
        "nested": [{"message": f'apikey="{fake_key_value}"'}],
    }

    details = BaseClient._get_error_details(response)

    rendered = repr(details)
    assert fake_key_value not in rendered
    assert "[REDACTED]" in rendered


def test_get_error_details_redacts_api_keys_in_raw_content():
    """Non-JSON error bodies should still redact reflected API keys."""
    fake_key_value = "SECRET_FMP_KEY"
    response = Mock()
    response.json.side_effect = json.JSONDecodeError("bad", "doc", 0)
    response.content = (
        f"Error at https://api.example/path?apikey={fake_key_value}".encode()
    )

    details = BaseClient._get_error_details(response)

    assert isinstance(details, dict)
    assert fake_key_value not in repr(details)
    assert details["raw_content"].count("[REDACTED]") >= 1


def test_get_error_details_redacts_api_keys_in_scalar_json():
    """Scalar JSON error bodies should redact embedded API keys."""
    fake_key_value = "SECRET_FMP_KEY"
    response = Mock()
    response.json.return_value = f"apikey={fake_key_value}"

    details = BaseClient._get_error_details(response)

    assert isinstance(details, dict)
    assert fake_key_value not in repr(details)
    assert "[REDACTED]" in details["raw_content"]


def _handle_body(client_config, status, content):
    """Drive the real ``handle_response`` and return the raised FMPError."""
    client = BaseClient(client_config)
    response = httpx.Response(
        status, request=httpx.Request("GET", "https://example.com"), content=content
    )
    with pytest.raises(FMPError) as excinfo:
        client.handle_response(response)
    return excinfo.value


def test_handle_response_redacts_key_in_non_json_success_body(client_config):
    """A 2xx with a non-JSON body must redact like every other error path.

    The ``JSONDecodeError`` branch built ``FMPError.response`` from the raw
    bytes with no redaction, while the 5xx sibling ran them through
    ``_redact_api_keys``. Every existing test drove the *helper*, never this
    branch -- which is how the asymmetry survived (#252 FMP-SEC-005).

    Reachable in normal operation: WAF and CDN block pages echo the full
    request URL, and ours carries ``apikey=``.
    """
    fake_key_value = "SECRET_FMP_KEY"
    body = f"<html>blocked for apikey={fake_key_value}</html>".encode()

    error = _handle_body(client_config, 200, body)

    rendered = repr(error.response)
    assert fake_key_value not in rendered
    assert "[REDACTED]" in rendered


def test_handle_response_redacts_scalar_json_body(client_config):
    """A bare JSON *string* body is how proxies return short error text."""
    fake_key_value = "SECRET_FMP_KEY"
    body = json.dumps(f"denied for apikey={fake_key_value}").encode()

    error = _handle_body(client_config, 200, body)

    rendered = repr(error.response)
    assert fake_key_value not in rendered
    assert "[REDACTED]" in rendered


def test_handle_response_non_json_redaction_matches_the_error_path(client_config):
    """Pin the parity, not just the fix.

    The defect was that two branches handling the same bytes disagreed.
    Asserting only "200 redacts" would still pass if the paths drifted apart
    again in the other direction.
    """
    fake_key_value = "SECRET_FMP_KEY"
    body = f"<html>blocked for apikey={fake_key_value}</html>".encode()

    assert (
        _handle_body(client_config, 200, body).response
        == _handle_body(client_config, 500, body).response
    )


def test_handle_response_non_utf8_body_does_not_mask_the_json_error(client_config):
    """A non-UTF-8 body must not raise *while handling* the JSON failure.

    Bare ``.decode()`` raises ``UnicodeDecodeError`` from inside the
    ``except json.JSONDecodeError`` block, replacing the real error with a
    decoding one. ``errors="replace"`` matches ``_get_error_details``.
    """
    fake_key_value = "SECRET_FMP_KEY"
    body = b"\xff\xfe blocked for apikey=" + fake_key_value.encode()

    error = _handle_body(client_config, 200, body)

    assert "Invalid JSON response" in str(error)
    assert fake_key_value not in repr(error.response)


def test_handle_response_does_not_blank_32_char_request_ids(client_config):
    """Wizard key-shaped heuristics must not run on HTTP error bodies (#316)."""
    token = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"  # noqa: S105  # pragma: allowlist secret
    body = f"<html>request-id={token} denied</html>".encode()

    error = _handle_body(client_config, 500, body)

    assert token in repr(error.response)


def test_handle_response_redacts_fmp_api_key_assignment(client_config):
    """``FMP_API_KEY=`` on an error body must redact; request ids stay (#330)."""
    planted = "PLANTED_error_body_fmp_key"
    request_id = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"
    body = f"<html>denied FMP_API_KEY={planted} request-id={request_id}</html>".encode()
    error = _handle_body(client_config, 500, body)
    rendered = repr(error.response)
    assert planted not in rendered
    assert "[REDACTED]" in rendered
    assert request_id in rendered


def test_get_error_details_handles_non_utf8_body():
    """Non-UTF-8 error bodies should not raise while extracting details."""
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(401, request=request, content=b"\xff\xfe binary body")

    details = BaseClient._get_error_details(response)

    assert isinstance(details, dict)
    assert "raw_content" in details
    assert isinstance(details["raw_content"], str)


def test_sanitize_error_details_top_level_string_and_list():
    """Sanitize helpers should handle top-level string and list payloads."""
    fake_key_value = "SECRET_FMP_KEY"
    redacted_str = _sanitize_error_details(f"apikey={fake_key_value}")
    assert fake_key_value not in redacted_str
    assert "[REDACTED]" in redacted_str

    redacted_list = _sanitize_error_details(
        [f"apikey={fake_key_value}", {"count": 1, "api-key": fake_key_value}]
    )
    assert isinstance(redacted_list, list)
    assert fake_key_value not in repr(redacted_list)
    assert redacted_list[1]["count"] == 1
    assert redacted_list[1]["api-key"] == "[REDACTED]"


def test_sanitize_error_value_preserves_non_string_scalars():
    """Non-string scalar values should pass through sanitization unchanged."""
    assert _sanitize_error_value(42) == 42
    assert _sanitize_error_value(None) is None
    assert _sanitize_error_value(True) is True
    assert _sanitize_error_value(3.14) == 3.14

    nested = _sanitize_error_details(
        {"code": 401, "ok": False, "retries": None, "items": [1, True, None]}
    )
    assert nested == {
        "code": 401,
        "ok": False,
        "retries": None,
        "items": [1, True, None],
    }


def test_safe_error_details_fallback_when_extraction_raises():
    """Unreadable bodies should fall back without propagating extraction errors."""
    response = Mock()
    with patch.object(
        BaseClient, "_get_error_details", side_effect=RuntimeError("boom")
    ):
        details = BaseClient._safe_error_details(response)

    assert details == {"raw_content": "[unreadable error body]"}


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


def test_handle_http_status_error_allow_empty_on_404(base_client, mock_endpoint):
    """Endpoints with allow_empty_on_404 should return [] on 404."""
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(404, request=request, json={"message": "missing"})
    error = httpx.HTTPStatusError("Not found", request=request, response=response)
    mock_endpoint.allow_empty_on_404 = True
    mock_endpoint.name = "sample-endpoint"

    result = base_client._handle_http_status_error(mock_endpoint, error)

    assert result == []


def test_handle_http_status_error_404_non_empty_raises(base_client):
    """404 with a non-empty payload should raise a typed FMP error."""
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(404, request=request, json={"message": "missing"})
    error = httpx.HTTPStatusError("Not found", request=request, response=response)

    with pytest.raises(FMPError) as exc_info:
        base_client._handle_http_status_error(error)

    assert exc_info.value.status_code == 404
    assert exc_info.value.__cause__ is None


def test_handle_http_status_error_requires_error_argument(base_client):
    """Missing error argument should raise TypeError."""
    with pytest.raises(TypeError, match="missing required error argument"):
        base_client._handle_http_status_error(None)


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


def test_rate_limit_handler_receives_redacted_response_body(base_client):
    """429 handling should not pass raw API keys into the rate limiter."""
    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        429,
        request=request,
        headers={"Retry-After": "5"},
        text=f"Rate limited for https://api.example/?apikey={fake_key_value}",
    )
    error = httpx.HTTPStatusError(
        "Too many requests", request=request, response=response
    )

    with (
        patch.object(base_client._rate_limiter, "handle_response") as handle_response,
        patch.object(base_client._rate_limiter, "get_retry_after", return_value=5.0),
        pytest.raises(RateLimitError),
    ):
        base_client._handle_http_status_error(error)

    handle_response.assert_called_once()
    body = handle_response.call_args.args[1]
    assert fake_key_value not in body
    assert "[REDACTED]" in body


def test_handle_response_error_traceback_suppresses_httpx_request_url(base_client):
    """HTTP error handling should not chain tracebacks that expose API keys."""
    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/profile?apikey={fake_key_value}&symbol=AAPL",
    )
    response = httpx.Response(
        401,
        request=request,
        json={"message": "Invalid API key"},
    )

    with pytest.raises(AuthenticationError) as exc_info:
        base_client.handle_response(response)

    exc = exc_info.value
    rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    assert fake_key_value not in rendered
    assert "HTTPStatusError" not in rendered
    assert fake_key_value not in repr(exc.response)


def test_bytes_response_http_error_uses_typed_fmp_exception(base_client, mock_endpoint):
    """Binary endpoints map httpx status errors to FMP exceptions without chaining."""
    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/download?apikey={fake_key_value}",
    )
    response = httpx.Response(
        401,
        request=request,
        json={"message": "Invalid API key"},
    )
    mock_endpoint.method.value = "GET"
    mock_endpoint.build_url.return_value = (
        "https://financialmodelingprep.com/stable/download"
    )
    mock_endpoint.response_model = bytes

    with (
        patch.object(base_client.client, "request", return_value=response),
        pytest.raises(AuthenticationError) as exc_info,
    ):
        base_client._execute_request(mock_endpoint)

    exc = exc_info.value
    rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    assert fake_key_value not in rendered
    assert "HTTPStatusError" not in rendered
    assert fake_key_value not in repr(exc.response)


def test_bytes_response_non_utf8_error_body_uses_typed_fmp_exception(
    base_client, mock_endpoint
):
    """Binary non-UTF-8 error bodies still raise typed FMP exceptions safely."""
    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/download?apikey={fake_key_value}",
    )
    response = httpx.Response(
        401,
        request=request,
        content=b"\xff\xfe binary error body",
    )
    mock_endpoint.method.value = "GET"
    mock_endpoint.build_url.return_value = (
        "https://financialmodelingprep.com/stable/download"
    )
    mock_endpoint.response_model = bytes

    with (
        patch.object(base_client.client, "request", return_value=response),
        pytest.raises(AuthenticationError) as exc_info,
    ):
        base_client._execute_request(mock_endpoint)

    exc = exc_info.value
    rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    assert fake_key_value not in rendered
    assert "HTTPStatusError" not in rendered
    assert fake_key_value not in repr(exc.response)


@pytest.mark.asyncio
async def test_async_bytes_response_http_error_uses_typed_fmp_exception(
    base_client, mock_endpoint
):
    """Async binary endpoints map status errors without chaining httpx."""
    from unittest.mock import AsyncMock

    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/download?apikey={fake_key_value}",
    )
    response = httpx.Response(
        401,
        request=request,
        json={"message": "Invalid API key"},
    )
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.validate_params.return_value = {}
    mock_endpoint.build_url.return_value = (
        "https://financialmodelingprep.com/stable/download"
    )
    mock_endpoint.get_query_params.return_value = {}
    mock_endpoint.response_model = bytes

    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(return_value=response)

    with (
        patch.object(
            base_client, "_setup_async_client", return_value=mock_async_client
        ),
        pytest.raises(AuthenticationError) as exc_info,
    ):
        await base_client._execute_request_async(mock_endpoint)

    exc = exc_info.value
    rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    assert fake_key_value not in rendered
    assert "HTTPStatusError" not in rendered
    assert fake_key_value not in repr(exc.response)


@pytest.mark.parametrize(
    ("status_code", "expected_exception"),
    [
        (400, ValidationError),
        (500, FMPError),
    ],
)
def test_handle_http_status_error_redacts_key_in_exception_message(
    base_client: BaseClient,
    status_code: int,
    expected_exception: type[FMPError],
) -> None:
    """400/500 messages embed error details and must redact reflected keys."""
    fake_key_value = "SECRET_FMP_KEY"
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        status_code,
        request=request,
        json={
            "message": f"Failed for https://api.example/?apikey={fake_key_value}",
            "apikey": fake_key_value,
        },
    )

    with pytest.raises(expected_exception) as exc_info:
        base_client.handle_response(response)

    exc = exc_info.value
    assert fake_key_value not in str(exc)
    assert fake_key_value not in repr(exc.response)
    assert "[REDACTED]" in str(exc)


@pytest.mark.parametrize(
    ("status_code", "expected_exception"),
    [
        (429, RateLimitError),
        (401, AuthenticationError),
        (400, ValidationError),
        (500, FMPError),
    ],
)
def test_handle_http_status_error_redacts_chained_apikey_traceback(
    base_client: BaseClient,
    status_code: int,
    expected_exception: type[FMPError],
) -> None:
    """Test HTTP error tracebacks do not expose the API key query parameter."""
    marker = "TRACEBACK_REDACTION_SENTINEL"
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey={marker}",
    )
    response = httpx.Response(
        status_code,
        request=request,
        json={"message": "Rate limit exceeded"},
    )

    try:
        base_client.handle_response(response)
    except FMPError as exc:
        assert isinstance(exc, expected_exception)
        formatted_traceback = traceback.format_exc()
        assert "apikey=" not in formatted_traceback
        assert marker not in formatted_traceback
        assert "apikey=" not in str(exc)
        assert marker not in str(exc)
        assert exc.__cause__ is None
        assert exc.__suppress_context__ is True
    else:
        pytest.fail(f"Expected {expected_exception.__name__}")


def test_is_retryable_error_includes_mapped_5xx_fmp_errors():
    """Mapped FMP 5xx errors from status conversion should still be retried."""
    assert BaseClient._is_retryable_error(FMPError("server", status_code=500)) is True
    assert BaseClient._is_retryable_error(FMPError("server", status_code=503)) is True
    assert (
        BaseClient._is_retryable_error(AuthenticationError("auth", status_code=401))
        is False
    )
    assert BaseClient._is_retryable_error(FMPError("client", status_code=400)) is False
    assert BaseClient._is_retryable_error(FMPError("no status")) is False
    assert BaseClient._is_retryable_error(RateLimitError("limited", retry_after=1.0))
    request = httpx.Request("GET", "https://example.com")
    response_5xx = httpx.Response(503, request=request)
    response_4xx = httpx.Response(404, request=request)
    assert BaseClient._is_retryable_error(
        httpx.HTTPStatusError("server", request=request, response=response_5xx)
    )
    assert not BaseClient._is_retryable_error(
        httpx.HTTPStatusError("not found", request=request, response=response_4xx)
    )
    assert not BaseClient._is_retryable_error(ValueError("other"))
    assert BaseClient._is_retryable_error(FMPTimeoutError("Request timed out"))
    assert BaseClient._is_retryable_error(FMPNetworkError("Network error"))
    assert BaseClient._is_retryable_error(FMPNetworkError("Protocol error"))
    assert not BaseClient._is_retryable_error(
        FMPNetworkError("Transport error", retryable=False)
    )
    assert BaseClient._is_retryable_error(
        httpx.ProtocolError("protocol", request=request)
    )
    assert BaseClient._is_retryable_error(httpx.ProxyError("proxy", request=request))
    assert not BaseClient._is_retryable_error(
        httpx.TooManyRedirects("redirects", request=request)
    )
    assert not BaseClient._is_retryable_error(
        httpx.UnsupportedProtocol("scheme", request=request)
    )
    assert not BaseClient._is_retryable_error(
        httpx.DecodingError("decode", request=request)
    )


_LEAK_SECRET = "SECRET_FMP_KEY_123"  # noqa: S105  # pragma: allowlist secret


def _httpx_error_with_key(
    exc_cls: type[httpx.RequestError], secret: str
) -> httpx.RequestError:
    """Transport error whose request URL carries a live-looking apikey."""
    request = httpx.Request(
        "GET",
        f"https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey={secret}",
    )
    return exc_cls(f"failed for url '{request.url}'", request=request)


def _assert_secret_stays_off_exception(exc: BaseException, secret: str) -> None:
    rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    assert secret not in str(exc)
    assert secret not in repr(exc)
    assert secret not in repr(exc.__cause__)
    assert secret not in rendered
    for name in (
        "httpx.TimeoutException",
        "httpx.ConnectError",
        "httpx.NetworkError",
        "httpx.ProtocolError",
        "httpx.ProxyError",
        "httpx.DecodingError",
        "httpx.TooManyRedirects",
        "httpx.UnsupportedProtocol",
    ):
        assert name not in rendered, name


@patch("httpx.Client.request")
def test_timeout_does_not_leak_apikey_via_cause_or_logs(
    mock_request, mock_endpoint, client_config
) -> None:
    """#350: timeout mapping must not chain httpx or log the request URL."""
    mock_request.side_effect = _httpx_error_with_key(
        httpx.TimeoutException, _LEAK_SECRET
    )
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    try:
        with (
            patch.object(client.logger, "error") as mock_error,
            patch("tenacity.nap.sleep", return_value=None),
            pytest.raises(FMPTimeoutError) as exc_info,
        ):
            client.request(mock_endpoint)
    finally:
        client.close()

    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


@patch("httpx.Client.request")
def test_network_error_does_not_leak_apikey_via_cause_or_logs(
    mock_request, mock_endpoint, client_config
) -> None:
    """#350: connect/network mapping must not chain httpx or log the request URL."""
    mock_request.side_effect = _httpx_error_with_key(httpx.ConnectError, _LEAK_SECRET)
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    try:
        with (
            patch.object(client.logger, "error") as mock_error,
            patch("tenacity.nap.sleep", return_value=None),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            client.request(mock_endpoint)
    finally:
        client.close()

    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


@pytest.mark.asyncio
async def test_async_timeout_does_not_leak_apikey_via_cause_or_logs(
    mock_endpoint, client_config
) -> None:
    """#350 async twin of the timeout pin."""
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(
        side_effect=_httpx_error_with_key(httpx.TimeoutException, _LEAK_SECRET)
    )
    try:
        with (
            patch.object(client, "_setup_async_client", return_value=mock_async_client),
            patch.object(client.logger, "error") as mock_error,
            patch("asyncio.sleep", new_callable=AsyncMock),
            pytest.raises(FMPTimeoutError) as exc_info,
        ):
            await client.request_async(mock_endpoint)
    finally:
        await client.aclose()
        client.close()

    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


@pytest.mark.asyncio
async def test_async_network_error_does_not_leak_apikey_via_cause_or_logs(
    mock_endpoint, client_config
) -> None:
    """#350 async twin of the network pin."""
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(
        side_effect=_httpx_error_with_key(httpx.ConnectError, _LEAK_SECRET)
    )
    try:
        with (
            patch.object(client, "_setup_async_client", return_value=mock_async_client),
            patch.object(client.logger, "error") as mock_error,
            patch("asyncio.sleep", new_callable=AsyncMock),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            await client.request_async(mock_endpoint)
    finally:
        await client.aclose()
        client.close()

    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


_LEFTOVER_REQUEST_CASES = (
    (httpx.ProtocolError, "Protocol error", True),
    (httpx.ProxyError, "Proxy error", True),
    (httpx.TooManyRedirects, "Transport error", False),
    (httpx.UnsupportedProtocol, "Transport error", False),
    (httpx.DecodingError, "Transport error", False),
)


@pytest.mark.parametrize(("exc_cls", "message", "retryable"), _LEFTOVER_REQUEST_CASES)
@patch("httpx.Client.request")
def test_leftover_request_error_does_not_leak_apikey_via_cause_or_logs(
    mock_request,
    mock_endpoint,
    client_config,
    exc_cls: type[httpx.RequestError],
    message: str,
    retryable: bool,
) -> None:
    """#354: leftover RequestError subclasses must not chain httpx or log the URL."""
    mock_request.side_effect = _httpx_error_with_key(exc_cls, _LEAK_SECRET)
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    try:
        with (
            patch.object(client.logger, "error") as mock_error,
            patch("tenacity.nap.sleep", return_value=None),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            client.request(mock_endpoint)
    finally:
        client.close()

    assert exc_info.value.message == message
    assert exc_info.value.retryable is retryable
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


@pytest.mark.parametrize(("exc_cls", "message", "retryable"), _LEFTOVER_REQUEST_CASES)
@pytest.mark.asyncio
async def test_async_leftover_request_error_does_not_leak_apikey_via_cause_or_logs(
    mock_endpoint,
    client_config,
    exc_cls: type[httpx.RequestError],
    message: str,
    retryable: bool,
) -> None:
    """#354 async twin of the leftover RequestError pin."""
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=1,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(
        side_effect=_httpx_error_with_key(exc_cls, _LEAK_SECRET)
    )
    try:
        with (
            patch.object(client, "_setup_async_client", return_value=mock_async_client),
            patch.object(client.logger, "error") as mock_error,
            patch("asyncio.sleep", new_callable=AsyncMock),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            await client.request_async(mock_endpoint)
    finally:
        await client.aclose()
        client.close()

    assert exc_info.value.message == message
    assert exc_info.value.retryable is retryable
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)
    mock_error.assert_called()
    for call in mock_error.call_args_list:
        assert _LEAK_SECRET not in str(call)
        assert call.kwargs.get("exc_info") is not True


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


@pytest.mark.parametrize(
    "payload",
    [
        {"Error Message": "Invalid API KEY"},
        {"Error Message": ("Invalid API KEY. Feel free to create a Free API Key...")},
        {"message": "Invalid API KEY"},
        {"error": "invalid api key"},
    ],
)
def test_check_error_response_invalid_api_key_is_authentication_error(
    payload: dict,
) -> None:
    """2xx invalid-key bodies must raise AuthenticationError (#340)."""
    with pytest.raises(AuthenticationError) as exc_info:
        BaseClient._check_error_response(payload)
    assert exc_info.value.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {"Error Message": "Legacy endpoint retired"},
        {"message": "Legacy endpoint retired"},
        {"error": "Legacy endpoint retired"},
    ],
)
def test_check_error_response_unrelated_2xx_body_stays_fmp_error(
    payload: dict,
) -> None:
    """Do not type every 2xx error body as auth failure (#340)."""
    with pytest.raises(FMPError) as exc_info:
        BaseClient._check_error_response(payload)
    assert type(exc_info.value) is FMPError
    assert exc_info.value.status_code is None


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
    result: SingleField = BaseClient._validate_single_item(endpoint, 7)
    assert isinstance(result, SingleField)
    assert result.value == 7


def test_process_response_raises_on_error_message():
    """Test process_response raises on error payloads."""
    endpoint = Mock()
    endpoint.response_model = dict

    with pytest.raises(FMPError):
        BaseClient._process_response(endpoint, {"message": "boom"})


def _list_quote_endpoint() -> Mock:
    class QuoteRow(BaseModel):
        model_config = ConfigDict(extra="allow")
        symbol: str | None = None

    endpoint = Mock()
    endpoint.name = "quote"
    endpoint.response_model = QuoteRow
    return endpoint


@pytest.mark.parametrize("key", ["Error Message", "message", "error"])
def test_process_response_singleton_invalid_api_key_list_is_auth_error(
    key: str,
) -> None:
    """A one-row list error body must type as AuthenticationError (#342)."""
    with pytest.raises(AuthenticationError) as exc_info:
        BaseClient._process_response(
            _list_quote_endpoint(),
            [{key: "Invalid API KEY"}],
        )
    assert exc_info.value.status_code == 200


def test_process_response_singleton_unrelated_error_list_is_not_auth() -> None:
    """Legacy 2xx list bodies stay a non-auth failure (#342)."""
    with pytest.raises(FMPError) as exc_info:
        BaseClient._process_response(
            _list_quote_endpoint(),
            [{"Error Message": "Legacy endpoint retired"}],
        )
    assert type(exc_info.value) is FMPError


def test_process_response_normal_quote_list_is_unchanged() -> None:
    result: object = BaseClient._process_response(
        _list_quote_endpoint(),
        [{"symbol": "AAPL", "price": 1.0}],
    )
    assert isinstance(result, list)
    assert result[0].symbol == "AAPL"


@pytest.mark.parametrize("key", ["Error Message", "message", "error"])
def test_process_response_singleton_error_plus_data_keys_is_auth_error(
    key: str,
) -> None:
    """Decorator keys plus the invalid-key copy type as auth (#344)."""
    with pytest.raises(AuthenticationError) as exc_info:
        BaseClient._process_response(
            _list_quote_endpoint(),
            [{key: "Invalid API KEY", "symbol": "AAPL"}],
        )
    assert exc_info.value.status_code == 200


def test_process_response_singleton_unrelated_decorator_keys_stay_a_row() -> None:
    """Mixed-key rows that are not the junk-key copy stay data (#344)."""
    result: object = BaseClient._process_response(
        _list_quote_endpoint(),
        [{"Error Message": "Legacy endpoint retired", "symbol": "AAPL"}],
    )
    assert isinstance(result, list)
    assert result[0].symbol == "AAPL"


@pytest.mark.parametrize(
    "payload",
    [
        {"Error Message": {"message": "Invalid API KEY"}},
        {"message": {"Error Message": "Invalid API KEY"}},
        {"error": {"error": "invalid api key"}},
        [{"Error Message": {"message": "Invalid API KEY"}}],
    ],
)
def test_nested_invalid_api_key_value_is_authentication_error(
    payload: object,
) -> None:
    """Nested error values unwrap instead of becoming a repr (#344)."""
    with pytest.raises(AuthenticationError) as exc_info:
        BaseClient._process_response(_list_quote_endpoint(), payload)
    assert exc_info.value.status_code == 200


def test_nested_junk_error_value_stays_fmp_error() -> None:
    """Do not map an unrecognized nested body to None or to auth (#344)."""
    with pytest.raises(FMPError) as exc_info:
        BaseClient._check_error_response({"Error Message": {"foo": 1}})
    assert type(exc_info.value) is FMPError
    assert exc_info.value.status_code is None


def test_process_response_singleton_invalid_api_key_scalar_is_auth_error() -> None:
    """A one-element string list must not become the first model field (#344)."""
    with pytest.raises(AuthenticationError) as exc_info:
        BaseClient._process_response(
            _list_quote_endpoint(),
            ["Invalid API KEY"],
        )
    assert exc_info.value.status_code == 200


def test_process_response_singleton_plain_scalar_keeps_first_field_fallback() -> None:
    """Only the invalid-key scalar is typed; other strings stay data."""
    result: object = BaseClient._process_response(
        _list_quote_endpoint(),
        ["AAPL"],
    )
    assert isinstance(result, list)
    assert result[0].symbol == "AAPL"


def test_process_response_does_not_walk_a_multi_row_list_for_errors() -> None:
    """Do not inspect every row of a multi-row list (#342)."""
    result: object = BaseClient._process_response(
        _list_quote_endpoint(),
        [
            {"Error Message": "Invalid API KEY"},
            {"symbol": "AAPL"},
        ],
    )
    assert isinstance(result, list)
    assert len(result) == 2


def test_process_response_does_not_inspect_a_trailing_error_row() -> None:
    """A last-row-only walker would still raise; only len == 1 is typed."""
    result: object = BaseClient._process_response(
        _list_quote_endpoint(),
        [
            {"symbol": "AAPL"},
            {"Error Message": "Invalid API KEY"},
        ],
    )
    assert isinstance(result, list)
    assert result[0].symbol == "AAPL"


def test_process_response_strict_mode_rejects_unknown_fields() -> None:
    """Strict mode should reject unknown fields on extra-allow models."""

    class ExtraAllowModel(BaseModel):
        model_config = ConfigDict(extra="allow")
        value: int

    endpoint = Mock()
    endpoint.name = "extra_allow_endpoint"
    endpoint.response_model = ExtraAllowModel

    with pytest.raises(ValidationError, match="Unexpected fields in response"):
        BaseClient._process_response(
            endpoint, {"value": 1, "unexpected": 2}, validation_mode="strict"
        )


def test_process_response_warn_mode_logs_unknown_fields(caplog) -> None:
    """Warn mode should log unknown fields on extra-allow models."""

    class ExtraAllowModel(BaseModel):
        model_config = ConfigDict(extra="allow")
        value: int

    endpoint = Mock()
    endpoint.name = "warn_extra_endpoint"
    endpoint.response_model = ExtraAllowModel

    with caplog.at_level(logging.WARNING, logger="fmp_data.base"):
        result: ExtraAllowModel | list[ExtraAllowModel] = BaseClient._process_response(
            endpoint, {"value": 1, "unexpected": 2}, validation_mode="warn"
        )

    assert isinstance(result, ExtraAllowModel)
    assert result.value == 1
    extras = [record for record in caplog.records if record.name == "fmp_data.base"]
    assert extras


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
        pytest.raises(FMPTimeoutError),
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


@patch("httpx.Client.request")
def test_protocol_error_is_retried(mock_request, mock_endpoint, base_client) -> None:
    """#354: ProtocolError stays retryable after mapping."""
    mock_request.side_effect = _httpx_error_with_key(httpx.ProtocolError, _LEAK_SECRET)
    with (
        patch("tenacity.nap.sleep", return_value=None),
        pytest.raises(FMPNetworkError) as exc_info,
    ):
        base_client.request(mock_endpoint)
    assert exc_info.value.retryable is True
    assert mock_request.call_count == base_client.config.max_retries
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)


@patch("httpx.Client.request")
def test_too_many_redirects_is_not_retried(
    mock_request, mock_endpoint, base_client
) -> None:
    """#354: leftover RequestErrors such as TooManyRedirects are not retried."""
    mock_request.side_effect = _httpx_error_with_key(
        httpx.TooManyRedirects, _LEAK_SECRET
    )
    with pytest.raises(FMPNetworkError) as exc_info:
        base_client.request(mock_endpoint)
    assert exc_info.value.retryable is False
    assert mock_request.call_count == 1
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)


@pytest.mark.asyncio
async def test_async_protocol_error_is_retried(mock_endpoint, client_config) -> None:
    """#354: ProtocolError uses the configured attempt count on the async path."""
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=3,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(
        side_effect=_httpx_error_with_key(httpx.ProtocolError, _LEAK_SECRET)
    )
    try:
        with (
            patch.object(client, "_setup_async_client", return_value=mock_async_client),
            patch("asyncio.sleep", new_callable=AsyncMock),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            await client.request_async(mock_endpoint)
    finally:
        await client.aclose()
        client.close()
    assert exc_info.value.retryable is True
    assert mock_async_client.request.call_count == config.max_retries
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)


@pytest.mark.asyncio
async def test_async_too_many_redirects_is_not_retried(
    mock_endpoint, client_config
) -> None:
    """#354: TooManyRedirects is a single attempt on the async path."""
    mock_endpoint.method = MagicMock()
    mock_endpoint.method.value = "GET"
    mock_endpoint.response_model = SampleResponse
    config = ClientConfig(
        api_key=_LEAK_SECRET,
        base_url=client_config.base_url,
        max_retries=3,
        max_rate_limit_retries=0,
    )
    client = BaseClient(config)
    mock_async_client = AsyncMock()
    mock_async_client.request = AsyncMock(
        side_effect=_httpx_error_with_key(httpx.TooManyRedirects, _LEAK_SECRET)
    )
    try:
        with (
            patch.object(client, "_setup_async_client", return_value=mock_async_client),
            pytest.raises(FMPNetworkError) as exc_info,
        ):
            await client.request_async(mock_endpoint)
    finally:
        await client.aclose()
        client.close()
    assert exc_info.value.retryable is False
    assert mock_async_client.request.call_count == 1
    _assert_secret_stays_off_exception(exc_info.value, _LEAK_SECRET)


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
                with pytest.raises(FMPTimeoutError):
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


class TestUnwrapList:
    """List counterpart of _unwrap_single (#235)."""

    def test_unwrap_list_passes_through_list(self):
        items = [SampleResponse(test="first"), SampleResponse(test="second")]
        assert EndpointGroup._unwrap_list(items, SampleResponse) is items

    def test_unwrap_list_wraps_single_item(self):
        item = SampleResponse(test="data")
        result = EndpointGroup._unwrap_list(item, SampleResponse)
        assert result == [item]

    def test_unwrap_list_recognizes_row_type_before_list(self):
        """A lone row is wrapped even though the fallback is list-shaped."""
        item = SampleResponse(test="data")
        assert EndpointGroup._unwrap_list(item, SampleResponse) == [item]
        items = [item]
        assert EndpointGroup._unwrap_list(items, SampleResponse) is items

    def test_unwrap_list_empty_list_stays_empty(self):
        assert EndpointGroup._unwrap_list([], SampleResponse) == []

    def test_async_group_matches_sync(self):
        item = SampleResponse(test="data")
        assert AsyncEndpointGroup._unwrap_list(item, SampleResponse) == [item]


class TestRequestList:
    """BaseClient.request_list is Endpoint[T] -> list[T] (#235)."""

    def test_request_list_wraps_single_object(self, base_client, test_endpoint):
        item = SampleResponse(test="data")
        with patch.object(base_client, "request", return_value=item) as request:
            result = base_client.request_list(test_endpoint, symbol="AAPL")

        assert result == [item]
        request.assert_called_once_with(test_endpoint, symbol="AAPL")

    def test_request_list_keeps_list(self, base_client, test_endpoint):
        items = [SampleResponse(test="a"), SampleResponse(test="b")]
        with patch.object(base_client, "request", return_value=items):
            assert base_client.request_list(test_endpoint, symbol="AAPL") is items

    @pytest.mark.asyncio
    async def test_request_async_list_wraps_single_object(
        self, base_client, test_endpoint
    ):
        item = SampleResponse(test="data")
        with patch.object(
            base_client, "request_async", return_value=item
        ) as request_async:
            result = await base_client.request_async_list(test_endpoint, symbol="AAPL")

        assert result == [item]
        request_async.assert_called_once_with(test_endpoint, symbol="AAPL")

    @pytest.mark.asyncio
    async def test_request_async_list_keeps_list(self, base_client, test_endpoint):
        items = [SampleResponse(test="a"), SampleResponse(test="b")]
        with patch.object(base_client, "request_async", return_value=items):
            assert (
                await base_client.request_async_list(test_endpoint, symbol="AAPL")
                is items
            )


def test_http_client_does_not_put_apikey_in_default_headers(client_config):
    """Query param is the only key channel (#252 FMP-SEC-004)."""
    from fmp_data.base import BaseClient

    client = BaseClient(client_config)
    try:
        assert "apikey" not in {k.lower() for k in client.client.headers}
    finally:
        client.close()


def _redirect_response(src_url: str, location: str) -> httpx.Response:
    """A 302 as ``follow_redirects=True`` presents it: Location set, no next_request."""
    src = httpx.Request("GET", src_url)
    return httpx.Response(302, headers={"location": location}, request=src)


def test_reject_cross_origin_redirect_reads_location_when_next_request_unset():
    """httpx sets next_request only when follow_redirects is False (#252)."""
    response = _redirect_response(
        "https://trusted.test/path?apikey=SECRET",
        "https://attacker.test/steal",
    )
    assert response.next_request is None
    with pytest.raises(FMPError, match="cross-origin"):
        _reject_cross_origin_redirect(response)


def test_same_origin_location_redirect_is_allowed():
    response = _redirect_response(
        "https://trusted.test/old", "https://trusted.test/new"
    )
    assert response.next_request is None
    _reject_cross_origin_redirect(response)


def test_scheme_relative_cross_origin_location_is_refused():
    response = _redirect_response(
        "https://trusted.test/path?apikey=SECRET",
        "//attacker.test/steal",
    )
    with pytest.raises(FMPError, match="cross-origin"):
        _reject_cross_origin_redirect(response)


def test_https_to_http_same_host_is_refused():
    response = _redirect_response(
        "https://trusted.test/path",
        "http://trusted.test/path",
    )
    with pytest.raises(FMPError, match="cross-origin"):
        _reject_cross_origin_redirect(response)


def test_origin_defaults_http_ports_and_leaves_other_schemes():
    https = httpx.URL("https://trusted.test/path")
    http = httpx.URL("http://127.0.0.1/path")
    ftp = httpx.URL("ftp://files.test/x")
    custom = httpx.URL("https://trusted.test:8443/path")
    assert _origin(https) == ("https", "trusted.test", 443)
    assert _origin(http) == ("http", "127.0.0.1", 80)
    assert _origin(ftp) == ("ftp", "files.test", None)
    assert _origin(custom) == ("https", "trusted.test", 8443)


def test_https_default_port_is_same_origin():
    response = _redirect_response(
        "https://trusted.test/old",
        "https://trusted.test:443/new",
    )
    _reject_cross_origin_redirect(response)


def test_http_default_port_is_same_origin():
    response = _redirect_response(
        "http://127.0.0.1/old",
        "http://127.0.0.1:80/new",
    )
    _reject_cross_origin_redirect(response)


def test_explicit_non_default_port_is_different_origin():
    response = _redirect_response(
        "https://trusted.test/old",
        "https://trusted.test:8443/new",
    )
    with pytest.raises(FMPError, match="cross-origin"):
        _reject_cross_origin_redirect(response)


def test_explicit_same_non_default_port_is_allowed():
    response = _redirect_response(
        "http://127.0.0.1:8080/old",
        "http://127.0.0.1:8080/new",
    )
    _reject_cross_origin_redirect(response)


def test_relative_location_is_same_origin():
    response = _redirect_response("https://trusted.test/old", "/new")
    _reject_cross_origin_redirect(response)


def test_scheme_relative_same_host_is_allowed():
    response = _redirect_response(
        "https://trusted.test/old",
        "//trusted.test/new",
    )
    _reject_cross_origin_redirect(response)


def test_malformed_absolute_location_keeps_source_host():
    """``https:/new`` is scheme+path with no host; httpx copies the source host."""
    response = _redirect_response("https://trusted.test/old", "https:/new")
    _reject_cross_origin_redirect(response)


def test_non_redirect_response_is_ignored():
    src = httpx.Request("GET", "https://trusted.test/path")
    _reject_cross_origin_redirect(httpx.Response(200, request=src))


def test_next_request_fallback_is_honored_when_set():
    src = httpx.Request("GET", "https://trusted.test/path")
    dst = httpx.Request("GET", "https://attacker.test/steal")
    response = httpx.Response(
        302,
        headers={"location": "https://trusted.test/new"},
        request=src,
    )
    object.__setattr__(response, "next_request", dst)
    with pytest.raises(FMPError, match="cross-origin"):
        _reject_cross_origin_redirect(response)


def test_invalid_location_is_refused(monkeypatch):
    response = _redirect_response("https://trusted.test/path", "https://ok.test/x")

    def _boom(_value: str) -> httpx.URL:
        raise httpx.InvalidURL("bad")

    monkeypatch.setattr("fmp_data.base.httpx.URL", _boom)
    with pytest.raises(FMPError, match="invalid Location"):
        _reject_cross_origin_redirect(response)


def test_http_client_does_not_follow_cross_origin_302():
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(f"{request.url.scheme}://{request.url.host}{request.url.path}")
        if request.url.host == "trusted.test":
            return httpx.Response(
                302,
                headers={"location": "https://attacker.test/steal"},
                request=request,
            )
        return httpx.Response(200, content=b"leaked", request=request)

    with httpx.Client(
        follow_redirects=True,
        event_hooks={"response": [_reject_cross_origin_redirect]},
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(FMPError, match="cross-origin"):
            client.get("https://trusted.test/path?apikey=SECRET")

    assert seen == ["https://trusted.test/path"]


def test_http_client_follows_same_origin_302():
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        if request.url.path == "/old":
            return httpx.Response(
                302,
                headers={"location": "https://trusted.test/new"},
                request=request,
            )
        return httpx.Response(200, json={"ok": True}, request=request)

    with httpx.Client(
        follow_redirects=True,
        event_hooks={"response": [_reject_cross_origin_redirect]},
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.get("https://trusted.test/old")

    assert response.status_code == 200
    assert seen == ["/old", "/new"]


def test_base_client_installs_hook_that_refuses_cross_origin_302(client_config):
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.host)
        if request.url.host == "api.test.com":
            return httpx.Response(
                302,
                headers={"location": "https://attacker.test/steal"},
                request=request,
            )
        return httpx.Response(200, content=b"leaked", request=request)

    client = BaseClient(client_config)
    try:
        hooks = client.client.event_hooks
        wrapped = httpx.Client(
            timeout=client.config.timeout,
            follow_redirects=True,
            headers=dict(client.client.headers),
            event_hooks=hooks,
            transport=httpx.MockTransport(handler),
        )
        client.client.close()
        client.client = wrapped
        with pytest.raises(FMPError, match="cross-origin"):
            client.client.get("https://api.test.com/stable/profile?apikey=SECRET")
        assert seen == ["api.test.com"]
    finally:
        client.close()
