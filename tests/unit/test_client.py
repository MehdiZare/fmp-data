# tests/test_client.py
from unittest.mock import Mock, patch

import httpx
import pytest

from fmp_data.client import FMPDataClient
from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)


def test_client_initialization(client_config):
    """Test client initialization with config"""
    client = FMPDataClient(config=client_config)
    assert client.config.api_key == "test_api_key"
    assert client.config.base_url == "https://test.financialmodelingprep.com/api"


def test_client_from_env():
    """Test client initialization from environment variables"""
    with patch.dict("os.environ", {"FMP_API_KEY": "env_test_key"}):
        client = FMPDataClient.from_env()
        assert client.config.api_key == "env_test_key"


@patch("httpx.Client.request")
def test_get_profile_success(
    mock_request, fmp_client, mock_response, mock_company_profile
):
    """Test successful company profile retrieval"""
    mock_request.return_value = mock_response(
        status_code=200,
        json_data=[mock_company_profile],  # API returns list with single item
    )

    profile = fmp_client.company.get_profile("AAPL")
    assert profile.symbol == "AAPL"
    assert profile.company_name == "Apple Inc."
    mock_request.assert_called_once()


@patch("httpx.Client.request")
def test_retry_on_timeout(
    mock_request, fmp_client, mock_response, mock_company_profile
):
    """Test retry behavior on timeout"""
    # First call raises timeout, second succeeds
    mock_request.side_effect = [
        httpx.TimeoutException("Connection timeout"),
        mock_response(status_code=200, json_data=[mock_company_profile]),
    ]

    result = fmp_client.company.get_profile("AAPL")
    assert result.symbol == "AAPL"
    assert mock_request.call_count == 2


@patch("httpx.Client.request")
def test_rate_limit_quota_tracking(
    mock_request, fmp_client, mock_response, mock_company_profile
):
    """Test rate limit quota tracking"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_company_profile]
    )

    # Make multiple requests
    for _ in range(5):
        result = fmp_client.company.get_profile("AAPL")
        assert result.symbol == "AAPL"

    assert mock_request.call_count == 5


@patch("httpx.Client.request")
def test_validation_error(mock_request, fmp_client, mock_response, mock_error_response):
    """Test validation error handling"""
    error = mock_error_response("Invalid parameters", 400)
    mock_resp = mock_response(
        status_code=400,
        json_data=error,
        raise_error=httpx.HTTPStatusError(
            "400 error", request=Mock(), response=mock_response(400, error)
        ),
    )
    mock_request.return_value = mock_resp

    with pytest.raises(ValidationError):
        fmp_client.company.get_profile("")


@patch("httpx.Client.request")
def test_unexpected_error(mock_request, fmp_client, mock_response, mock_error_response):
    """Test unexpected server error"""
    error = mock_error_response("Internal server error", 500)
    mock_resp = mock_response(
        status_code=500,
        json_data=error,
        raise_error=httpx.HTTPStatusError(
            "500 error", request=Mock(), response=mock_response(500, error)
        ),
    )
    mock_request.return_value = mock_resp

    with pytest.raises(FMPError):
        fmp_client.company.get_profile("AAPL")


@patch("httpx.Client.request")
def test_rate_limit_handling(
    mock_request, fmp_client, mock_response, mock_error_response
):
    """Test rate limit handling"""
    error = mock_error_response("Rate limit exceeded", 429)
    mock_resp = mock_response(
        status_code=429,
        json_data=error,
        raise_error=httpx.HTTPStatusError(
            "429 error", request=Mock(), response=mock_response(429, error)
        ),
    )
    mock_request.return_value = mock_resp

    with pytest.raises(RateLimitError):
        fmp_client.company.get_profile("AAPL")


@patch("httpx.Client.request")
def test_authentication_error(
    mock_request, fmp_client, mock_response, mock_error_response
):
    """Test authentication error handling"""
    error = mock_error_response("Invalid API key", 401)
    mock_resp = mock_response(
        status_code=401,
        json_data=error,
        raise_error=httpx.HTTPStatusError(
            "401 error", request=Mock(), response=mock_response(401, error)
        ),
    )
    mock_request.return_value = mock_resp

    with pytest.raises(AuthenticationError):
        fmp_client.company.get_profile("AAPL")


def test_context_manager():
    """Test client as context manager"""
    with FMPDataClient(api_key="test_key") as client:
        assert client.config.api_key == "test_key"
        assert hasattr(client, "client")
        assert not client.client.is_closed


def test_client_close(client_config):
    """Test client cleanup"""
    client = FMPDataClient(config=client_config)
    assert client._initialized
    client.close()
    assert hasattr(client, "logger")


def test_client_without_api_key():
    """Test client initialization without API key"""
    with pytest.raises(ConfigError) as exc_info:
        FMPDataClient(api_key=None)
    assert "Invalid client configuration" in str(exc_info.value)


def test_client_cleanup(client_config):
    """Test client cleanup even when not fully initialized"""
    client = FMPDataClient(config=client_config)
    client._initialized = False  # Simulate failed initialization
    client.close()  # Should not raise any exceptions


@pytest.mark.parametrize("attribute", ["client", "logger", "_logger"])
def test_client_robust_cleanup(client_config, attribute):
    """Test client cleanup with missing attributes"""
    client = FMPDataClient(config=client_config)
    if hasattr(client, attribute):
        delattr(client, attribute)
    client.close()  # Should not raise any exceptions


def test_logger_property():
    """Test logger property creates logger if missing"""
    with patch("fmp_data.client.FMPLogger") as mock_logger:
        client = FMPDataClient(api_key="test_key")
        delattr(client, "_logger")  # Remove logger
        logger = client.logger  # Should create new logger
        assert logger is not None
        mock_logger().get_logger.assert_called_once_with(client.__class__.__module__)
