# tests/unit/test_client.py
import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
from pydantic import ValidationError as PydanticValidationError
from pydantic_core import InitErrorDetails
import pytest

from fmp_data.client import FMPDataClient
from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    FMPError,
    RateLimitError,
    ValidationError,
)


class TestFMPDataClientInitialization:
    """Test client initialization scenarios"""

    def test_client_initialization_with_config(self, client_config):
        """Test client initialization with config object"""
        client = FMPDataClient(config=client_config)
        assert client.config.api_key == "test_api_key"
        assert client.config.base_url == "https://test.financialmodelingprep.com/api"
        assert client._initialized is True
        client.close()

    def test_client_initialization_with_individual_params(self):
        """Test client initialization with individual parameters"""
        client = FMPDataClient(
            api_key="test_key",
            timeout=60,
            max_retries=5,
            base_url="https://custom.api.com",
            debug=True,
        )
        assert client.config.api_key == "test_key"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
        assert client.config.base_url == "https://custom.api.com"
        assert client._initialized is True
        client.close()

    def test_client_initialization_debug_mode(self):
        """Test client initialization with debug mode enabled"""
        client = FMPDataClient(api_key="test_key", debug=True)
        assert client.config.logging.level == "DEBUG"
        assert client.config.logging.handlers["console"].level == "DEBUG"
        client.close()

    def test_client_initialization_production_mode(self):
        """Test client initialization with debug mode disabled"""
        client = FMPDataClient(api_key="test_key", debug=False)
        assert client.config.logging.level == "INFO"
        assert client.config.logging.handlers["console"].level == "INFO"
        client.close()

    def test_client_initialization_missing_api_key_error(self):
        """Test client initialization fails without API key"""
        with pytest.raises(ConfigError, match="Invalid client configuration"):
            FMPDataClient(api_key=None)

    def test_client_initialization_empty_api_key_error(self):
        """Test client initialization fails with empty API key"""
        with pytest.raises(ConfigError, match="Invalid client configuration"):
            FMPDataClient(api_key="")

    def test_client_initialization_config_without_api_key(self):
        """Test client initialization fails with config missing API key"""
        config = Mock()
        config.api_key = ""
        with pytest.raises(ConfigError):
            FMPDataClient(config=config)

    @patch("fmp_data.client.ClientConfig")
    def test_client_initialization_pydantic_validation_error(self, mock_config):
        """Test client initialization handles pydantic validation errors"""
        errors: list[InitErrorDetails] = [
            InitErrorDetails(type="missing", loc=("api_key",), input=None)
        ]
        mock_config.side_effect = PydanticValidationError.from_exception_data(
            "Invalid config",
            errors,
        )

        with pytest.raises(ConfigError, match="Invalid client configuration"):
            FMPDataClient(api_key="test_key")

    @patch("fmp_data.client.FMPLogger")
    def test_client_initialization_logger_error_handling(self, mock_logger):
        """Test client initialization handles logger errors gracefully"""
        mock_logger.side_effect = Exception("Logger error")

        with pytest.raises(Exception):  # noqa: B017
            FMPDataClient(api_key="test_key")

    def test_client_initialization_sets_all_attributes(self):
        """Test client initialization sets all expected attributes"""
        client = FMPDataClient(api_key="test_key")

        # Check initial state - accessing attributes verifies they exist
        assert client._initialized is True
        assert client._logger is not None
        assert client._company is None  # Lazy loaded
        assert client._market is None  # Lazy loaded
        assert client._batch is None  # Lazy loaded
        assert client._transcripts is None  # Lazy loaded
        assert client._sec is None  # Lazy loaded
        assert client._index is None  # Lazy loaded

        client.close()


class TestFMPDataClientFromEnv:
    """Test client creation from environment variables"""

    @patch.dict(os.environ, {"FMP_API_KEY": "env_test_key"})
    def test_from_env_basic(self):
        """Test basic from_env functionality"""
        client = FMPDataClient.from_env()
        assert client.config.api_key == "env_test_key"
        assert client._initialized is True
        client.close()

    @patch.dict(os.environ, {"FMP_API_KEY": "env_test_key"})
    def test_from_env_with_debug(self):
        """Test from_env with debug mode"""
        client = FMPDataClient.from_env(debug=True)
        assert client.config.api_key == "env_test_key"
        assert client.config.logging.level == "DEBUG"
        assert client.config.logging.handlers["console"].level == "DEBUG"
        client.close()

    @patch.dict(os.environ, {"FMP_API_KEY": "env_test_key"})
    def test_from_env_debug_false(self):
        """Test from_env with debug explicitly False"""
        client = FMPDataClient.from_env(debug=False)
        assert client.config.api_key == "env_test_key"
        # Should use default config logging levels
        client.close()

    @patch("fmp_data.config.ClientConfig.from_env")
    def test_from_env_with_custom_config(self, mock_from_env):
        """Test from_env modifies logging config correctly"""
        mock_config = Mock()
        mock_config.api_key = "test_key"

        # Create proper logging config mock
        mock_logging = Mock()
        mock_logging.level = "INFO"
        mock_logging.log_path = None  # Set to None instead of Mock

        # Create proper handlers mock with real string values
        mock_console_handler = Mock()
        mock_console_handler.level = "INFO"
        mock_console_handler.class_name = "StreamHandler"  # Real string, not Mock
        mock_console_handler.format = (
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        mock_console_handler.handler_kwargs = {}
        mock_logging.handlers = {"console": mock_console_handler}

        mock_config.logging = mock_logging
        mock_from_env.return_value = mock_config

        client = FMPDataClient.from_env(debug=True)

        # Verify debug mode was applied
        assert mock_config.logging.level == "DEBUG"
        assert mock_config.logging.handlers["console"].level == "DEBUG"
        client.close()


class TestFMPDataClientContextManager:
    """Test client as context manager"""

    def test_context_manager_basic_usage(self):
        """Test basic context manager functionality"""
        with FMPDataClient(api_key="test_key") as client:
            assert client.config.api_key == "test_key"
            assert client._initialized is True
            assert client.client is not None
            assert not client.client.is_closed

    def test_context_manager_returns_self(self):
        """Test context manager __enter__ returns self"""
        client = FMPDataClient(api_key="test_key")
        result = client.__enter__()
        assert result is client
        client.close()

    def test_context_manager_cleanup_on_exit(self):
        """Test context manager properly cleans up on exit"""
        httpx_client = None

        with FMPDataClient(api_key="test_key") as c:
            httpx_client = c.client
            assert not httpx_client.is_closed

        # After exiting context, client should be closed
        assert httpx_client.is_closed

    def test_context_manager_cleanup_on_exception(self):
        """Test context manager cleanup occurs even when exception is raised"""
        httpx_client = None

        try:
            with FMPDataClient(api_key="test_key") as c:
                httpx_client = c.client
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Even with exception, client should be closed
        assert httpx_client.is_closed

    def test_context_manager_not_initialized_error(self):
        """Test context manager when client not properly initialized"""
        client = FMPDataClient(api_key="test_key")
        client._initialized = False

        with pytest.raises(RuntimeError, match="Client not properly initialized"):
            client.__enter__()

        # Cleanup
        client._initialized = True
        client.close()

    @pytest.mark.asyncio
    async def test_async_context_manager_usage(self):
        """Test async context manager on sync client."""
        client = FMPDataClient(api_key="test_key")

        async with client as async_client:
            assert async_client is client
            assert not client.client.is_closed

        assert client.client.is_closed

    @pytest.mark.asyncio
    async def test_async_context_manager_not_initialized_error(self):
        """Test async context manager when client not properly initialized."""
        client = FMPDataClient(api_key="test_key")
        client._initialized = False

        with pytest.raises(RuntimeError, match="Client not properly initialized"):
            await client.__aenter__()

        client._initialized = True
        client.close()


class TestFMPDataClientProperties:
    """Test client property accessors"""

    @pytest.fixture
    def client(self):
        """Create a client for testing properties"""
        client = FMPDataClient(api_key="test_key")
        yield client
        client.close()

    def test_company_property(self, client):
        """Test company property lazy loading"""
        # Initially None
        assert client._company is None

        # Access creates instance
        company = client.company
        assert company is not None
        assert client._company is company

        # Second access returns same instance
        company2 = client.company
        assert company2 is company

    def test_market_property(self, client):
        """Test market property lazy loading"""
        assert client._market is None

        market = client.market
        assert market is not None
        assert client._market is market

        market2 = client.market
        assert market2 is market

    def test_fundamental_property(self, client):
        """Test fundamental property lazy loading"""
        assert client._fundamental is None

        fundamental = client.fundamental
        assert fundamental is not None
        assert client._fundamental is fundamental

    def test_technical_property(self, client):
        """Test technical property lazy loading"""
        assert client._technical is None

        technical = client.technical
        assert technical is not None
        assert client._technical is technical

    def test_intelligence_property(self, client):
        """Test intelligence property lazy loading"""
        assert client._intelligence is None

        intelligence = client.intelligence
        assert intelligence is not None
        assert client._intelligence is intelligence

    def test_institutional_property(self, client):
        """Test institutional property lazy loading"""
        assert client._institutional is None

        institutional = client.institutional
        assert institutional is not None
        assert client._institutional is institutional

    def test_investment_property(self, client):
        """Test investment property lazy loading"""
        assert client._investment is None

        investment = client.investment
        assert investment is not None
        assert client._investment is investment

    def test_alternative_property(self, client):
        """Test alternative property lazy loading"""
        assert client._alternative is None

        alternative = client.alternative
        assert alternative is not None
        assert client._alternative is alternative

    def test_economics_property(self, client):
        """Test economics property lazy loading"""
        assert client._economics is None

        economics = client.economics
        assert economics is not None
        assert client._economics is economics

    def test_batch_property(self, client):
        """Test batch property lazy loading"""
        assert client._batch is None

        batch = client.batch
        assert batch is not None
        assert client._batch is batch

    def test_transcripts_property(self, client):
        """Test transcripts property lazy loading"""
        assert client._transcripts is None

        transcripts = client.transcripts
        assert transcripts is not None
        assert client._transcripts is transcripts

    def test_sec_property(self, client):
        """Test sec property lazy loading"""
        assert client._sec is None

        sec = client.sec
        assert sec is not None
        assert client._sec is sec

    def test_index_property(self, client):
        """Test index property lazy loading"""
        assert client._index is None

        index = client.index
        assert index is not None
        assert client._index is index

    def test_all_properties_when_not_initialized(self):
        """Test all properties raise error when client not initialized"""
        client = FMPDataClient(api_key="test_key")
        client._initialized = False

        properties = [
            "company",
            "market",
            "fundamental",
            "technical",
            "intelligence",
            "institutional",
            "investment",
            "alternative",
            "economics",
            "batch",
            "transcripts",
            "sec",
            "index",
        ]

        for prop_name in properties:
            with pytest.raises(RuntimeError, match="Client not properly initialized"):
                getattr(client, prop_name)

        # Cleanup
        client._initialized = True
        client.close()

    @patch("fmp_data.client.CompanyClient")
    def test_property_with_debug_logging(self, mock_company_client, client):
        """Test property access logs debug message when logger available"""
        with patch.object(client, "logger") as mock_logger:
            mock_logger.debug = Mock()

            # Access property
            _ = client.company

            # Verify debug was called
            mock_logger.debug.assert_called_once_with("Initializing company client")


class TestFMPDataClientLogger:
    """Test client logger functionality"""

    def test_logger_property_returns_logger(self):
        """Test logger property returns valid logger"""
        client = FMPDataClient(api_key="test_key")
        logger = client.logger

        assert logger is not None
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.error)

        client.close()

    @patch("fmp_data.client.FMPLogger")
    def test_logger_property_creates_new_when_missing(self, mock_fmp_logger):
        """Test logger property creates new logger when missing"""
        mock_logger_instance = Mock()
        mock_fmp_logger_obj = Mock()
        mock_fmp_logger_obj.get_logger.return_value = mock_logger_instance
        mock_fmp_logger.return_value = mock_fmp_logger_obj

        client = FMPDataClient(api_key="test_key")

        # Remove logger
        client._logger = None

        # Access should create new logger
        logger = client.logger

        assert logger is mock_logger_instance
        mock_fmp_logger_obj.get_logger.assert_called_with(client.__class__.__module__)

        client.close()

    def test_logger_property_returns_existing_logger(self):
        """Test logger property returns existing logger when available"""
        client = FMPDataClient(api_key="test_key")
        original_logger = client._logger

        # Access logger property
        logger = client.logger

        # Should return same instance
        assert logger is original_logger

        client.close()


class TestFMPDataClientCleanup:
    """Test client cleanup and resource management"""

    def test_close_method_basic(self):
        """Test basic close functionality"""
        client = FMPDataClient(api_key="test_key")
        httpx_client = client.client

        # Verify client is open
        assert not httpx_client.is_closed

        # Close and verify
        client.close()
        assert httpx_client.is_closed

    def test_close_method_missing_client_attribute(self):
        """Test close method when client attribute is missing"""
        client = FMPDataClient(api_key="test_key")

        # Remove client attribute
        delattr(client, "client")

        # Should not raise exception
        client.close()

    def test_close_method_none_client(self):
        """Test close method when client is None"""
        client = FMPDataClient(api_key="test_key")
        client.client = None

        # Should not raise exception
        client.close()

    def test_close_method_already_closed_client(self):
        """Test close method on already closed client"""
        client = FMPDataClient(api_key="test_key")

        # Close once
        client.close()

        # Close again - should not raise
        client.close()

    def test_close_method_client_close_exception(self):
        """Test close method handles client.close() exceptions"""
        client = FMPDataClient(api_key="test_key")

        # Mock client.close to raise exception
        client.client.close = Mock(side_effect=Exception("Close error"))

        # Should handle exception gracefully
        client.close()

    def test_multiple_close_calls(self):
        """Test multiple calls to close method"""
        client = FMPDataClient(api_key="test_key")

        # Multiple closes should not raise
        client.close()
        client.close()
        client.close()

    def test_cleanup_when_not_fully_initialized(self):
        """Test cleanup when client not fully initialized"""
        client = FMPDataClient(api_key="test_key")
        client._initialized = False

        # Should not raise any exceptions
        client.close()

    @pytest.mark.asyncio
    async def test_aclose_closes_async_client(self):
        """Test aclose handles async clients and sync cleanup."""
        client = FMPDataClient(api_key="test_key")
        async_client = AsyncMock()
        async_client.is_closed = False
        client._async_client = async_client
        client.client = Mock()
        logger_mock = Mock()
        client._logger = logger_mock

        await client.aclose()

        async_client.aclose.assert_awaited_once()
        client.client.close.assert_called_once()
        logger_mock.info.assert_called_once_with("FMP Data client closed")

    @pytest.mark.asyncio
    async def test_async_exit_logs_error(self):
        """Test async exit logs errors."""
        client = FMPDataClient(api_key="test_key")
        client.client = Mock()
        logger_mock = Mock()
        client._logger = logger_mock
        client.aclose = AsyncMock()

        await client.__aexit__(ValueError, ValueError("boom"), None)

        logger_mock.error.assert_called_once()


class TestFMPDataClientEdgeCases:
    """Test edge cases and error scenarios"""

    def test_client_string_representation(self):
        """Test client string operations don't crash"""
        client = FMPDataClient(api_key="test_key")

        # These should not raise exceptions
        str_result = str(client)
        repr_result = repr(client)

        assert str_result is not None
        assert repr_result is not None

        client.close()

    def test_client_attributes_exist(self):
        """Test all expected attributes exist after initialization"""
        client = FMPDataClient(api_key="test_key")

        required_attrs = [
            "_initialized",
            "_logger",
            "_company",
            "_market",
            "_fundamental",
            "_technical",
            "_intelligence",
            "_institutional",
            "_investment",
            "_alternative",
            "_economics",
        ]

        # Verify attributes exist by accessing them
        for attr in required_attrs:
            assert getattr(client, attr, "MISSING") != "MISSING"

        client.close()

    def test_client_inheritance_from_base_client(self):
        """Test client properly inherits from BaseClient"""
        client = FMPDataClient(api_key="test_key")

        # Should inherit BaseClient functionality
        assert client.config is not None
        assert client.client is not None  # httpx client
        assert callable(client.close)

        client.close()

    def test_client_with_different_base_urls(self):
        """Test client with various base URL configurations"""
        test_urls = [
            "https://financialmodelingprep.com/api",
            "https://custom.api.com/v1",
            "http://localhost:8000",
        ]

        for url in test_urls:
            client = FMPDataClient(api_key="test_key", base_url=url)
            assert client.config.base_url == url
            client.close()

    def test_client_with_different_timeouts(self):
        """Test client with various timeout configurations"""
        timeouts = [10, 30, 60, 120]

        for timeout in timeouts:
            client = FMPDataClient(api_key="test_key", timeout=timeout)
            assert client.config.timeout == timeout
            client.close()

    def test_client_with_different_retry_counts(self):
        """Test client with various retry configurations"""
        retry_counts = [1, 3, 5, 10]

        for retries in retry_counts:
            client = FMPDataClient(api_key="test_key", max_retries=retries)
            assert client.config.max_retries == retries
            client.close()


# Integration tests with actual HTTP calls (existing tests from original file)
@patch("httpx.Client.request")
def test_get_profile_success(
    mock_request, fmp_client, mock_response, mock_company_profile
):
    """Test successful company profile retrieval"""
    mock_request.return_value = mock_response(
        status_code=200,
        json_data=[mock_company_profile],
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
    client = FMPDataClient(
        config=fmp_client.config.model_copy(update={"max_retries": 2})
    )
    mock_request.side_effect = [
        httpx.TimeoutException("Connection timeout"),
        mock_response(status_code=200, json_data=[mock_company_profile]),
    ]

    with patch("tenacity.nap.sleep", return_value=None):
        result = client.company.get_profile("AAPL")
    assert result.symbol == "AAPL"
    assert mock_request.call_count == 2
    client.close()


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
