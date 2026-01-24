# tests/unit/test_exceptions.py
"""Tests for custom exception classes in fmp_data/exceptions.py"""

import pytest

from fmp_data.exceptions import (
    AuthenticationError,
    ConfigError,
    DependencyError,
    FMPError,
    FMPNotFound,
    InvalidResponseTypeError,
    InvalidSymbolError,
    RateLimitError,
    ValidationError,
)


class TestFMPError:
    """Tests for the base FMPError exception"""

    def test_basic_fmp_error(self):
        """Test FMPError with just a message"""
        error = FMPError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response is None

    def test_fmp_error_with_status_code(self):
        """Test FMPError with status code"""
        error = FMPError("Server error", status_code=500)
        assert error.message == "Server error"
        assert error.status_code == 500
        assert error.response is None

    def test_fmp_error_with_response(self):
        """Test FMPError with response dict"""
        response_data = {"error": "details", "code": "ERR001"}
        error = FMPError("API error", status_code=400, response=response_data)
        assert error.message == "API error"
        assert error.status_code == 400
        assert error.response == response_data

    def test_fmp_error_is_exception(self):
        """Test that FMPError can be raised and caught"""
        with pytest.raises(FMPError) as exc_info:
            raise FMPError("Test error")
        assert str(exc_info.value) == "Test error"


class TestRateLimitError:
    """Tests for RateLimitError exception"""

    def test_rate_limit_error_basic(self):
        """Test RateLimitError with basic parameters"""
        error = RateLimitError("Rate limit exceeded")
        assert error.message == "Rate limit exceeded"
        assert error.retry_after is None
        assert str(error) == "Rate limit exceeded"

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after"""
        error = RateLimitError(
            "Rate limit exceeded",
            status_code=429,
            retry_after=30.5,
        )
        assert error.status_code == 429
        assert error.retry_after == 30.5
        assert "(retry after 30.5 seconds)" in str(error)

    def test_rate_limit_error_str_formatting(self):
        """Test RateLimitError string formatting"""
        error = RateLimitError(
            "Too many requests",
            status_code=429,
            response={"message": "slow down"},
            retry_after=60.0,
        )
        error_str = str(error)
        assert "Too many requests" in error_str
        assert "(retry after 60.0 seconds)" in error_str

    def test_rate_limit_error_inheritance(self):
        """Test that RateLimitError inherits from FMPError"""
        error = RateLimitError("Rate limit")
        assert isinstance(error, FMPError)
        assert isinstance(error, Exception)

    def test_rate_limit_error_can_be_caught_as_fmp_error(self):
        """Test catching RateLimitError as FMPError"""
        with pytest.raises(FMPError):
            raise RateLimitError("Rate limit", retry_after=10)


class TestAuthenticationError:
    """Tests for AuthenticationError exception"""

    def test_authentication_error_basic(self):
        """Test AuthenticationError with basic parameters"""
        error = AuthenticationError("Invalid API key")
        assert error.message == "Invalid API key"
        assert str(error) == "Invalid API key"

    def test_authentication_error_with_status_code(self):
        """Test AuthenticationError with 401 status code"""
        error = AuthenticationError(
            "Authentication failed",
            status_code=401,
            response={"error": "invalid_token"},
        )
        assert error.status_code == 401
        assert error.response == {"error": "invalid_token"}

    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError inherits from FMPError"""
        error = AuthenticationError("Auth error")
        assert isinstance(error, FMPError)
        assert isinstance(error, Exception)


class TestValidationError:
    """Tests for ValidationError exception"""

    def test_validation_error_basic(self):
        """Test ValidationError with basic parameters"""
        error = ValidationError("Invalid parameter")
        assert error.message == "Invalid parameter"

    def test_validation_error_with_details(self):
        """Test ValidationError with response details"""
        error = ValidationError(
            "Invalid request",
            status_code=400,
            response={"field": "symbol", "error": "required"},
        )
        assert error.status_code == 400
        assert error.response["field"] == "symbol"

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from FMPError"""
        error = ValidationError("Validation failed")
        assert isinstance(error, FMPError)


class TestConfigError:
    """Tests for ConfigError exception"""

    def test_config_error_basic(self):
        """Test ConfigError with basic message"""
        error = ConfigError("Configuration missing")
        assert error.message == "Configuration missing"
        assert str(error) == "Configuration missing"

    def test_config_error_without_status_code(self):
        """Test ConfigError typically doesn't have HTTP status code"""
        error = ConfigError("API key not set")
        assert error.status_code is None
        assert error.response is None

    def test_config_error_inheritance(self):
        """Test that ConfigError inherits from FMPError"""
        error = ConfigError("Config error")
        assert isinstance(error, FMPError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Tests for the exception hierarchy"""

    def test_all_exceptions_are_fmp_errors(self):
        """Test all custom exceptions inherit from FMPError"""
        exceptions = [
            RateLimitError("msg"),
            AuthenticationError("msg"),
            ValidationError("msg"),
            ConfigError("msg"),
        ]
        for exc in exceptions:
            assert isinstance(exc, FMPError)

    def test_exception_types_are_distinct(self):
        """Test that different exception types can be caught separately"""
        # Ensure each type can be uniquely caught
        with pytest.raises(RateLimitError):
            raise RateLimitError("rate limit")

        with pytest.raises(AuthenticationError):
            raise AuthenticationError("auth")

        with pytest.raises(ValidationError):
            raise ValidationError("validation")

        with pytest.raises(ConfigError):
            raise ConfigError("config")

    def test_catching_specific_vs_base(self):
        """Test catching specific exception vs base FMPError"""

        def raise_rate_limit():
            raise RateLimitError("Too fast", retry_after=5)

        # Can catch as RateLimitError
        try:
            raise_rate_limit()
        except RateLimitError as e:
            assert e.retry_after == 5

        # Can also catch as FMPError
        try:
            raise_rate_limit()
        except FMPError as e:
            assert "Too fast" in str(e)


class TestInvalidSymbolError:
    """Tests for InvalidSymbolError"""

    def test_inherits_from_validation_error(self):
        assert issubclass(InvalidSymbolError, ValidationError)
        assert issubclass(InvalidSymbolError, FMPError)

    def test_default_message(self):
        error = InvalidSymbolError()
        assert "Symbol is required" in str(error)

    def test_custom_message(self):
        error = InvalidSymbolError("Custom symbol error")
        assert "Custom symbol error" == str(error)


class TestInvalidResponseTypeError:
    """Tests for InvalidResponseTypeError"""

    def test_inherits_from_fmp_error(self):
        assert issubclass(InvalidResponseTypeError, FMPError)

    def test_error_message_with_types(self):
        error = InvalidResponseTypeError(
            endpoint_name="test_endpoint", expected_type="dict", actual_type="list"
        )
        assert "test_endpoint" in str(error)
        assert "expected dict" in str(error)
        assert "got list" in str(error)

    def test_error_message_without_actual_type(self):
        error = InvalidResponseTypeError(
            endpoint_name="test_endpoint", expected_type="dict"
        )
        assert "test_endpoint" in str(error)
        assert "expected dict" in str(error)


class TestDependencyError:
    """Tests for DependencyError"""

    def test_inherits_from_config_error(self):
        assert issubclass(DependencyError, ConfigError)
        assert issubclass(DependencyError, FMPError)

    def test_error_message_format(self):
        error = DependencyError(
            feature="MCP server", install_command="pip install fmp-data[mcp]"
        )
        assert "MCP server" in str(error)
        assert "pip install fmp-data[mcp]" in str(error)

    def test_attributes(self):
        error = DependencyError(
            feature="Test feature", install_command="pip install test"
        )
        assert error.feature == "Test feature"
        assert error.install_command == "pip install test"


class TestFMPNotFound:
    """Tests for FMPNotFound"""

    def test_inherits_from_fmp_error(self):
        assert issubclass(FMPNotFound, FMPError)

    def test_error_message_with_symbol(self):
        error = FMPNotFound(symbol="AAPL")
        assert "Symbol AAPL not found" == str(error)

    def test_can_be_caught_as_fmp_error(self):
        with pytest.raises(FMPError):
            raise FMPNotFound("TEST")
