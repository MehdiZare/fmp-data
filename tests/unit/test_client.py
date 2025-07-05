# tests/test_client.py
from unittest.mock import Mock, patch

import httpx
import pytest

from fmp_data.client import ClientConfig, FMPDataClient
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


def test_all_client_properties_lazy_loading(fmp_client):
    """Test that all client properties lazy load correctly"""
    # Test all major client properties exist and work
    properties = [
        'company', 'market', 'fundamental', 'technical',
        'intelligence', 'institutional', 'investment',
        'alternative', 'economics'
    ]

    for prop_name in properties:
        client_instance = getattr(fmp_client, prop_name)
        assert client_instance is not None
        # Second access should return same instance
        assert getattr(fmp_client, prop_name) is client_instance


def test_client_properties_when_not_initialized():
    """Test property access when client not properly initialized"""
    client = FMPDataClient(api_key="test_key")
    client._initialized = False

    with pytest.raises(RuntimeError, match="Client not properly initialized"):
        _ = client.company


def test_from_env_debug_creates_client():
    """Test from_env class method with debug mode"""
    with patch.dict("os.environ", {"FMP_API_KEY": "env_test_key"}):
        client = FMPDataClient.from_env(debug=True)
        assert client.config.api_key == "env_test_key"
        client.close()


def test_client_api_key_validation():
    """Test API key validation"""
    # Empty string API key should fail
    with pytest.raises(ConfigError):
        FMPDataClient(api_key="")

    # None API key should fail
    with pytest.raises(ConfigError):
        FMPDataClient(api_key=None)


def test_debug_vs_production_logging():
    """Test logging configuration for debug vs production"""
    # Debug mode
    client1 = FMPDataClient(api_key="test_key", debug=True)
    assert client1._initialized
    client1.close()

    # Production mode
    client2 = FMPDataClient(api_key="test_key", debug=False)
    assert client2._initialized
    client2.close()


def test_client_cleanup_missing_attributes(client_config):
    """Test client cleanup with missing attributes"""
    client = FMPDataClient(config=client_config)

    # Test cleanup with missing httpx client - should not raise
    if hasattr(client, "client"):
        delattr(client, "client")
    client.close()


def test_context_manager_cleanup_on_exception():
    """Test context manager cleanup on exceptions"""
    with patch("fmp_data.client.FMPDataClient.close") as mock_close:
        try:
            with FMPDataClient(api_key="test_key") as _:
                raise ValueError("Test exception")
        except ValueError:
            pass

        mock_close.assert_called_once()


def test_property_access_creates_clients(fmp_client):
    """Test that property access creates expected client instances"""
    # Initially should be None
    assert fmp_client._company is None
    assert fmp_client._market is None

    # Access creates instance
    company = fmp_client.company
    assert fmp_client._company is company
    assert company is not None

    market = fmp_client.market
    assert fmp_client._market is market
    assert market is not None


def test_logger_property_accessible(fmp_client):
    """Test that logger property is accessible"""
    logger = fmp_client.logger
    assert logger is not None
    assert hasattr(logger, 'debug')
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')


def test_client_config_vs_params():
    """Test initialization with config vs individual parameters"""
    # Test with individual parameters
    client1 = FMPDataClient(api_key="test_key", timeout=30, max_retries=3)
    assert client1._initialized
    assert client1.config.api_key == "test_key"
    assert client1.config.timeout == 30
    client1.close()

    # Test with config object
    config = ClientConfig(api_key="test_key2", timeout=60, max_retries=5)
    client2 = FMPDataClient(config=config)
    assert client2._initialized
    assert client2.config.api_key == "test_key2"
    assert client2.config.timeout == 60
    client2.close()


def test_all_property_types_return_correct_instances(fmp_client):
    """Test all properties return instances of expected types"""
    property_checks = [
        ('company', 'CompanyClient'),
        ('market', 'MarketClient'),
        ('fundamental', 'FundamentalClient'),
        ('technical', 'TechnicalClient'),
        ('intelligence', 'MarketIntelligenceClient'),
        ('institutional', 'InstitutionalClient'),
        ('investment', 'InvestmentClient'),
        ('alternative', 'AlternativeMarketsClient'),
        ('economics', 'EconomicsClient')
    ]

    for prop_name, expected_class in property_checks:
        client_instance = getattr(fmp_client, prop_name)
        assert client_instance is not None
        assert expected_class in str(type(client_instance))


def test_client_has_base_functionality(fmp_client):
    """Test that client has expected base functionality"""
    # Should inherit from BaseClient
    assert hasattr(fmp_client, 'config')
    assert hasattr(fmp_client, 'client')  # httpx client
    assert fmp_client.config.api_key == "test_api_key"


def test_client_initialization_attributes(client_config):
    """Test client initialization creates expected attributes"""
    client = FMPDataClient(config=client_config)

    # Check core attributes exist
    assert hasattr(client, '_initialized')
    assert hasattr(client, '_logger')
    assert hasattr(client, '_company')
    assert hasattr(client, '_market')

    # Verify initialization state
    assert client._initialized is True
    assert client._logger is not None
    assert client._company is None  # Lazy loaded
    assert client._market is None  # Lazy loaded

    client.close()


def test_multiple_property_access_same_instance(fmp_client):
    """Test multiple property accesses return same instance"""
    # Test caching behavior
    company1 = fmp_client.company
    company2 = fmp_client.company
    assert company1 is company2

    market1 = fmp_client.market
    market2 = fmp_client.market
    assert market1 is market2


def test_context_manager_functionality():
    """Test context manager basic functionality"""
    with FMPDataClient(api_key="test_key") as client:
        assert client._initialized
        assert client.config.api_key == "test_key"
        # Should not be closed while in context
        assert hasattr(client, 'client')


def test_client_string_operations(fmp_client):
    """Test client string operations don't raise exceptions"""
    # These operations should not crash
    str_repr = str(fmp_client)
    assert str_repr is not None

    repr_result = repr(fmp_client)
    assert repr_result is not None


def test_config_with_missing_api_key():
    """Test config object with missing API key"""
    config = Mock()
    config.api_key = ""

    with pytest.raises(ConfigError):
        FMPDataClient(config=config)
