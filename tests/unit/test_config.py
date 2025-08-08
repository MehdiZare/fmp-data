# tests/unit/test_config.py
from contextlib import contextmanager
import os
from pathlib import Path

from pydantic import ValidationError
import pytest

from fmp_data.config import (
    ClientConfig,
    LoggingConfig,
    LogHandlerConfig,
    RateLimitConfig,
)
from fmp_data.exceptions import ConfigError


@contextmanager
def temp_environ():
    """Context manager to temporarily modify environment variables."""
    old_environ = dict(os.environ)
    try:
        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


class TestLogHandlerConfig:
    """Test LogHandlerConfig functionality"""

    def test_basic_initialization(self):
        """Test basic log handler configuration"""
        config = LogHandlerConfig(
            class_name="StreamHandler", level="INFO", format="%(message)s"
        )
        assert config.class_name == "StreamHandler"
        assert config.level == "INFO"
        assert config.format == "%(message)s"
        assert config.handler_kwargs == {}

    def test_with_kwargs(self):
        """Test log handler with additional kwargs"""
        kwargs = {"filename": "test.log", "maxBytes": 1024}
        config = LogHandlerConfig(
            class_name="RotatingFileHandler", level="DEBUG", handler_kwargs=kwargs
        )
        assert config.handler_kwargs == kwargs
        assert config.handler_kwargs["filename"] == "test.log"
        assert config.handler_kwargs["maxBytes"] == 1024

    def test_level_validation_valid_levels(self):
        """Test valid logging levels are accepted"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            config = LogHandlerConfig(class_name="StreamHandler", level=level)
            assert config.level == level

    def test_level_validation_case_insensitive(self):
        """Test level validation handles case conversion"""
        config = LogHandlerConfig(class_name="StreamHandler", level="debug")
        assert config.level == "DEBUG"

        config = LogHandlerConfig(class_name="StreamHandler", level="info")
        assert config.level == "INFO"

    def test_level_validation_invalid_level(self):
        """Test invalid logging level raises error"""
        with pytest.raises(ValidationError, match="Invalid log level"):
            LogHandlerConfig(class_name="StreamHandler", level="INVALID")

    def test_default_values(self):
        """Test default values are set correctly"""
        config = LogHandlerConfig(class_name="StreamHandler")
        assert config.level == "INFO"
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert config.handler_kwargs == {}

    def test_empty_class_name_validation(self):
        """Test empty class name validation"""
        with pytest.raises(ValidationError):
            LogHandlerConfig(class_name="")

        with pytest.raises(ValidationError):
            LogHandlerConfig(class_name="   ")  # whitespace only


class TestRateLimitConfig:
    """Test RateLimitConfig functionality"""

    def test_default_values(self):
        """Test default rate limit configuration"""
        config = RateLimitConfig()
        assert config.daily_limit == 250
        assert config.requests_per_second == 5
        assert config.requests_per_minute == 300

    def test_custom_values(self):
        """Test custom rate limit configuration"""
        config = RateLimitConfig(
            daily_limit=1000, requests_per_second=10, requests_per_minute=600
        )
        assert config.daily_limit == 1000
        assert config.requests_per_second == 10
        assert config.requests_per_minute == 600

    def test_from_env_with_values(self):
        """Test creating rate limit config from environment variables"""
        with temp_environ() as env:
            env.update(
                {
                    "FMP_DAILY_LIMIT": "1500",
                    "FMP_REQUESTS_PER_SECOND": "8",
                    "FMP_REQUESTS_PER_MINUTE": "480",
                }
            )

            config = RateLimitConfig.from_env()
            assert config.daily_limit == 1500
            assert config.requests_per_second == 8
            assert config.requests_per_minute == 480

    def test_from_env_with_defaults(self):
        """Test rate limit config from env with missing variables uses defaults"""
        with temp_environ() as env:
            # Clear any existing rate limit env vars
            for key in [
                "FMP_DAILY_LIMIT",
                "FMP_REQUESTS_PER_SECOND",
                "FMP_REQUESTS_PER_MINUTE",
            ]:
                env.pop(key, None)

            config = RateLimitConfig.from_env()
            assert config.daily_limit == 250
            assert config.requests_per_second == 5
            assert config.requests_per_minute == 300

    def test_from_env_partial_override(self):
        """Test rate limit config with only some env vars set"""
        with temp_environ() as env:
            env.update({"FMP_DAILY_LIMIT": "2000"})
            # Don't set other variables
            env.pop("FMP_REQUESTS_PER_SECOND", None)
            env.pop("FMP_REQUESTS_PER_MINUTE", None)

            config = RateLimitConfig.from_env()
            assert config.daily_limit == 2000
            assert config.requests_per_second == 5  # Default
            assert config.requests_per_minute == 300  # Default

    def test_from_env_invalid_values(self):
        """Test rate limit config handles invalid env values"""
        with temp_environ() as env:
            env.update({"FMP_DAILY_LIMIT": "invalid"})

            # Should fall back to default when int() conversion fails
            config = RateLimitConfig.from_env()
            assert config.daily_limit == 250  # Default value

    def test_validation_positive_values(self):
        """Test rate limit config validates positive values"""
        with pytest.raises(ValidationError):
            RateLimitConfig(daily_limit=-1)

        with pytest.raises(ValidationError):
            RateLimitConfig(requests_per_second=0)

        with pytest.raises(ValidationError):
            RateLimitConfig(requests_per_minute=-5)


class TestLoggingConfig:
    """Test LoggingConfig functionality"""

    def test_default_configuration(self):
        """Test default logging configuration"""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert "console" in config.handlers
        assert config.handlers["console"].class_name == "StreamHandler"
        assert config.log_path is None

    def test_custom_configuration(self, tmp_path):
        """Verify custom log handlers and path

        Args:
            tmp_path (Path): pytest fixture - unique tmp dir per test run
        """
        # Arrange
        log_dir = tmp_path / "logs"  # /tmp/pytest-of-.../logs
        custom_handlers = {
            "file": LogHandlerConfig(
                class_name="FileHandler",
                level="DEBUG",
                handler_kwargs={"filename": "test.log"},
            )
        }

        # Act
        config = LoggingConfig(
            level="DEBUG",
            handlers=custom_handlers,
            log_path=log_dir,
        )

        # Assert
        assert config.level == "DEBUG"
        assert config.handlers == custom_handlers
        assert config.log_path == log_dir

    def test_from_env_console_only(self):
        """Test logging config from env with console handler only"""
        with temp_environ() as env:
            env.update(
                {
                    "FMP_LOG_LEVEL": "DEBUG",
                    "FMP_LOG_CONSOLE": "true",
                    "FMP_LOG_CONSOLE_LEVEL": "WARNING",
                }
            )
            env.pop("FMP_LOG_PATH", None)  # No file logging

            config = LoggingConfig.from_env()
            assert config.level == "DEBUG"
            assert "console" in config.handlers
            assert config.handlers["console"].level == "WARNING"
            assert config.log_path is None
            assert "file" not in config.handlers
            assert "json" not in config.handlers

    def test_from_env_console_disabled(self):
        """Test logging config from env with console disabled"""
        with temp_environ() as env:
            env.update({"FMP_LOG_CONSOLE": "false", "FMP_LOG_LEVEL": "INFO"})
            env.pop("FMP_LOG_PATH", None)

            config = LoggingConfig.from_env()
            assert config.level == "INFO"
            assert "console" not in config.handlers

    def test_from_env_with_file_path(self, tmp_path):
        """Test logging config from env with file logging"""
        log_path = tmp_path / "logs"

        with temp_environ() as env:
            env.update(
                {
                    "FMP_LOG_LEVEL": "INFO",
                    "FMP_LOG_PATH": str(log_path),
                    "FMP_LOG_FILE_LEVEL": "DEBUG",
                    "FMP_LOG_MAX_BYTES": "2048",
                    "FMP_LOG_BACKUP_COUNT": "3",
                }
            )

            config = LoggingConfig.from_env()
            assert config.log_path == log_path
            assert "file" in config.handlers

            file_handler = config.handlers["file"]
            assert file_handler.class_name == "RotatingFileHandler"
            assert file_handler.level == "DEBUG"
            assert file_handler.handler_kwargs["maxBytes"] == 2048
            assert file_handler.handler_kwargs["backupCount"] == 3
            assert str(log_path / "fmp.log") in file_handler.handler_kwargs["filename"]

    def test_from_env_with_json_logging(self, tmp_path):
        """Test logging config from env with JSON logging enabled"""
        log_path = tmp_path / "logs"

        with temp_environ() as env:
            env.update(
                {
                    "FMP_LOG_PATH": str(log_path),
                    "FMP_LOG_JSON": "true",
                    "FMP_LOG_JSON_LEVEL": "ERROR",
                }
            )

            config = LoggingConfig.from_env()
            assert "json" in config.handlers

            json_handler = config.handlers["json"]
            assert json_handler.class_name == "JsonRotatingFileHandler"
            assert json_handler.level == "ERROR"
            assert str(log_path / "fmp.json") in json_handler.handler_kwargs["filename"]

    def test_from_env_json_disabled(self, tmp_path):
        """Test JSON logging disabled by default"""
        log_path = tmp_path / "logs"

        with temp_environ() as env:
            env.update({"FMP_LOG_PATH": str(log_path), "FMP_LOG_JSON": "false"})

            config = LoggingConfig.from_env()
            assert "json" not in config.handlers

    def test_from_env_default_values(self):
        """Test logging config from env uses defaults when vars missing"""
        with temp_environ() as env:
            # Clear all logging-related env vars
            for key in list(env.keys()):
                if key.startswith("FMP_LOG"):
                    env.pop(key)

            config = LoggingConfig.from_env()
            assert config.level == "INFO"
            assert "console" in config.handlers
            assert config.handlers["console"].level == "INFO"

    def test_model_post_init(self):
        """Test model post-initialization hook"""
        # This tests the model_post_init method is called
        config = LoggingConfig()
        # Should not raise any exceptions during initialization
        assert config.level == "INFO"

    def test_level_validation(self):
        """Test logging level validation in config"""
        valid_config = LoggingConfig(level="DEBUG")
        assert valid_config.level == "DEBUG"

        # Invalid level should be caught by LogHandlerConfig validation
        # but LoggingConfig itself doesn't validate the main level
        config = LoggingConfig(level="INVALID")
        assert config.level == "INVALID"  # No validation on main level


class TestClientConfig:
    """Test ClientConfig functionality"""

    def test_basic_initialization(self):
        """Test basic client configuration"""
        config = ClientConfig(
            api_key="test_key", base_url="https://api.test.com", timeout=60
        )
        assert config.api_key == "test_key"
        assert config.base_url == "https://api.test.com"
        assert config.timeout == 60

    def test_default_values(self):
        """Test default configuration values"""
        config = ClientConfig(api_key="test_key")
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.base_url == "https://financialmodelingprep.com"
        assert isinstance(config.rate_limit, RateLimitConfig)
        assert isinstance(config.logging, LoggingConfig)

    def test_custom_sub_configs(self):
        """Test custom rate limit and logging configurations"""
        rate_limit = RateLimitConfig(daily_limit=1000)
        logging_config = LoggingConfig(level="DEBUG")

        config = ClientConfig(
            api_key="test_key", rate_limit=rate_limit, logging=logging_config
        )

        assert config.rate_limit is rate_limit
        assert config.logging is logging_config
        assert config.rate_limit.daily_limit == 1000
        assert config.logging.level == "DEBUG"

    def test_url_validation_valid_urls(self):
        """Test URL validation with valid URLs"""
        valid_urls = [
            "https://api.test.com",
            "http://localhost:8000",
            "https://financialmodelingprep.com/stable",
            "https://sub.domain.com/path",
        ]

        for url in valid_urls:
            config = ClientConfig(api_key="test_key", base_url=url)
            assert config.base_url == url

    def test_url_validation_invalid_urls(self):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "not_a_url",
            "ftp://invalid.scheme.com",
            "https://",
            "",
            "just_text",
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError):
                ClientConfig(api_key="test_key", base_url=url)

    def test_api_key_validation(self):
        """Test API key validation"""
        # Valid API key
        config = ClientConfig(api_key="valid_key")
        assert config.api_key == "valid_key"

        # Empty API key should fail
        with pytest.raises(ValidationError):
            ClientConfig(api_key="")

        # Whitespace-only API key should fail
        with pytest.raises(ValidationError):
            ClientConfig(api_key="   ")

    def test_timeout_validation(self):
        """Test timeout validation"""
        # Valid timeouts
        valid_timeouts = [1, 30, 60, 120, 300]
        for timeout in valid_timeouts:
            config = ClientConfig(api_key="test_key", timeout=timeout)
            assert config.timeout == timeout

        # Invalid timeouts
        with pytest.raises(ValidationError):
            ClientConfig(api_key="test_key", timeout=0)

        with pytest.raises(ValidationError):
            ClientConfig(api_key="test_key", timeout=-1)

    def test_max_retries_validation(self):
        """Test max retries validation"""
        # Valid retry counts
        valid_retries = [0, 1, 3, 5, 10]
        for retries in valid_retries:
            config = ClientConfig(api_key="test_key", max_retries=retries)
            assert config.max_retries == retries

        # Invalid retry counts
        with pytest.raises(ValidationError):
            ClientConfig(api_key="test_key", max_retries=-1)

    def test_from_env_complete(self, tmp_path):
        """Test creating client config from environment with all variables"""
        log_path = tmp_path / "logs"

        with temp_environ() as env:
            env.update(
                {
                    "FMP_API_KEY": "env_test_key",
                    "FMP_BASE_URL": "https://env.api.com",
                    "FMP_TIMEOUT": "45",
                    "FMP_MAX_RETRIES": "4",
                    "FMP_DAILY_LIMIT": "500",
                    "FMP_REQUESTS_PER_SECOND": "3",
                    "FMP_LOG_LEVEL": "WARNING",
                    "FMP_LOG_PATH": str(log_path),
                }
            )

            config = ClientConfig.from_env()
            assert config.api_key == "env_test_key"
            assert config.base_url == "https://env.api.com"
            assert config.timeout == 45
            assert config.max_retries == 4
            assert config.rate_limit.daily_limit == 500
            assert config.rate_limit.requests_per_second == 3
            assert config.logging.level == "WARNING"
            assert config.logging.log_path == log_path

    def test_from_env_missing_api_key(self):
        """Test from_env raises error when API key missing"""
        with temp_environ() as env:
            env.pop("FMP_API_KEY", None)

            # Updated to expect ConfigError instead of ValueError
            with pytest.raises(ConfigError, match="API key must be provided"):
                ClientConfig.from_env()

    def test_from_env_partial_variables(self):
        """Test from_env with only some variables set"""
        with temp_environ() as env:
            env.clear()
            env["FMP_API_KEY"] = "test_key"
            # Don't set other variables

            config = ClientConfig.from_env()
            assert config.api_key == "test_key"
            # Should use defaults for other values
            assert config.timeout == 30
            assert config.max_retries == 3
            assert config.base_url == "https://financialmodelingprep.com"

    def test_from_env_invalid_numeric_values(self):
        """Test from_env handles invalid numeric environment variables"""
        with temp_environ() as env:
            env.update(
                {
                    "FMP_API_KEY": "test_key",
                    "FMP_TIMEOUT": "invalid",
                    "FMP_MAX_RETRIES": "not_a_number",
                }
            )

            config = ClientConfig.from_env()
            # Should use defaults when conversion fails
            assert config.timeout == 30
            assert config.max_retries == 3

    def test_serialization_round_trip(self):
        """Test configuration serialization and deserialization"""
        original_config = ClientConfig(
            api_key="test_key",
            timeout=45,
            base_url="https://test.api.com",
            rate_limit=RateLimitConfig(daily_limit=1000),
            logging=LoggingConfig(level="DEBUG"),
        )

        # Serialize to dict
        config_dict = original_config.model_dump()

        # Deserialize back
        reconstructed_config = ClientConfig.model_validate(config_dict)

        assert reconstructed_config.api_key == original_config.api_key
        assert reconstructed_config.timeout == original_config.timeout
        assert reconstructed_config.base_url == original_config.base_url
        assert (
            reconstructed_config.rate_limit.daily_limit
            == original_config.rate_limit.daily_limit
        )
        assert reconstructed_config.logging.level == original_config.logging.level

    def test_config_immutability(self):
        """Test config values can be updated (pydantic models are mutable by default)"""
        config = ClientConfig(api_key="test_key")

        # Should be able to modify config values
        config.timeout = 60
        assert config.timeout == 60

    def test_model_validation_error_handling(self):
        """Test handling of pydantic validation errors"""
        with pytest.raises(ValidationError) as exc_info:
            ClientConfig(
                api_key="test_key",
                timeout=-1,  # Invalid value
                base_url="invalid_url",  # Invalid URL
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # Should have multiple validation errors

    def test_repr_and_str(self):
        """Test string representations don't expose sensitive data"""
        config = ClientConfig(api_key="secret_key")

        # Test these don't crash and don't expose the API key
        str_repr = str(config)
        repr_result = repr(config)

        # API key should be redacted or not present in string representation
        assert "secret_key" not in str_repr
        assert "secret_key" not in repr_result
        # Check that some form of masked API key is present
        assert "secr***" in str_repr or "***" in str_repr


class TestConfigEdgeCases:
    """Test edge cases and error scenarios"""

    def test_empty_environment(self):
        """Test behavior with completely empty environment"""
        with temp_environ() as env:
            env.clear()

            # Should raise ConfigError for missing API key
            with pytest.raises(ConfigError):
                ClientConfig.from_env()

    def test_environment_with_extra_variables(self):
        """Test from_env ignores unrelated environment variables"""
        with temp_environ() as env:
            env.update(
                {
                    "FMP_API_KEY": "test_key",
                    "UNRELATED_VAR": "should_be_ignored",
                    "FMP_UNKNOWN_VAR": "also_ignored",
                }
            )

            config = ClientConfig.from_env()
            assert config.api_key == "test_key"
            # Should use defaults and not be affected by unknown vars

    def test_path_handling_edge_cases(self, tmp_path):
        """Test path handling with various path formats"""
        # Test with Path object
        config = LoggingConfig(log_path=tmp_path)
        assert config.log_path == tmp_path

        # Test with string path
        config = LoggingConfig(log_path=str(tmp_path))
        assert config.log_path == Path(str(tmp_path))

    def test_config_with_none_values(self):
        """Test configuration with None values where allowed"""
        config = LoggingConfig(log_path=None)
        assert config.log_path is None

    def test_large_configuration_values(self):
        """Test configuration with large numeric values"""
        config = ClientConfig(
            api_key="test_key",
            timeout=3600,  # 1 hour
            max_retries=100,
            rate_limit=RateLimitConfig(
                daily_limit=1000000, requests_per_second=1000, requests_per_minute=60000
            ),
        )

        assert config.timeout == 3600
        assert config.max_retries == 100
        assert config.rate_limit.daily_limit == 1000000

    def test_unicode_and_special_characters(self):
        """Test configuration with unicode and special characters"""
        config = ClientConfig(
            api_key="test_key_with_特殊字符",
            base_url="https://api-test.example.com",  # Using simple ASCII URL
        )

        assert config.api_key == "test_key_with_特殊字符"

    def test_nested_config_modification(self):
        """Test modifying nested configuration objects"""
        config = ClientConfig(api_key="test_key")

        # Modify nested rate limit config
        config.rate_limit.daily_limit = 2000
        assert config.rate_limit.daily_limit == 2000

        # Modify nested logging config
        config.logging.level = "ERROR"
        assert config.logging.level == "ERROR"
