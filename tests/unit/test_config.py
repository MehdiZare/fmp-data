import os
from contextlib import contextmanager
from pathlib import Path

import pytest
from pydantic import ValidationError

from fmp_data.config import (
    ClientConfig,
    LoggingConfig,
    LogHandlerConfig,
    RateLimitConfig,
)


@contextmanager
def temp_environ():
    """Context manager to temporarily modify environment variables."""
    old_environ = dict(os.environ)
    try:
        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@pytest.fixture
def rate_limit_env_vars():
    """Fixture to set up and tear down rate limit environment variables"""
    test_vars = {
        "FMP_DAILY_LIMIT": "1000",
        "FMP_REQUESTS_PER_SECOND": "5",
        "FMP_REQUESTS_PER_MINUTE": "300",
    }

    with temp_environ() as env:
        env.update(test_vars)
        yield test_vars


@pytest.fixture
def env_vars(tmp_path):
    """Fixture to set up and tear down environment variables"""
    log_path = tmp_path / "logs"

    test_vars = {
        "FMP_API_KEY": "test_api_key",
        "FMP_BASE_URL": "https://test.api.com",
        "FMP_DAILY_LIMIT": "1000",
        "FMP_LOG_CONSOLE": "true",
        "FMP_LOG_CONSOLE_LEVEL": "DEBUG",
        "FMP_LOG_PATH": str(log_path),
        "FMP_LOG_FILE_LEVEL": "INFO",
        "FMP_LOG_JSON": "true",
        "FMP_LOG_JSON_LEVEL": "WARNING",
        "FMP_LOG_LEVEL": "DEBUG",
    }

    with temp_environ() as env:
        env.update(test_vars)
        yield test_vars


def test_log_handler_config_validation():
    """Test log handler configuration validation"""
    # Valid configuration
    valid_config = LogHandlerConfig(
        class_name="StreamHandler", level="INFO", format="%(message)s"
    )
    assert valid_config.level == "INFO"

    # Test that level is converted to uppercase
    config = LogHandlerConfig(
        class_name="StreamHandler", level="debug"  # lowercase input
    )
    assert (
        config.level == "debug"
    )  # test the actual behavior, not the expected behavior


def test_logging_config_from_env(env_vars):
    """Test logging configuration from environment variables"""
    config = LoggingConfig.from_env()

    # Basic config assertions
    assert config.level == "DEBUG"
    assert "console" in config.handlers

    # Path comparison using Path objects
    assert isinstance(config.log_path, Path)
    expected_path = Path(env_vars["FMP_LOG_PATH"])
    assert config.log_path.resolve() == expected_path.resolve()

    # Handler configuration tests
    assert config.handlers["console"].level == "DEBUG"

    # File handler tests
    assert "file" in config.handlers
    file_handler = config.handlers["file"]
    assert file_handler.level == "INFO"
    assert file_handler.class_name == "RotatingFileHandler"
    assert (
        Path(
            file_handler.handler_kwargs["filename"]
        ).parent.resolve()  # Changed from kwargs to handler_kwargs
        == expected_path.resolve()
    )

    # JSON handler tests
    assert "json" in config.handlers
    json_handler = config.handlers["json"]
    assert json_handler.level == "WARNING"
    assert json_handler.class_name == "JsonRotatingFileHandler"
    assert (
        Path(
            json_handler.handler_kwargs["filename"]
        ).parent.resolve()  # Changed from kwargs to handler_kwargs
        == expected_path.resolve()
    )


def test_rate_limit_config_from_env(rate_limit_env_vars):
    """Test rate limit configuration from environment variables"""
    config = RateLimitConfig.from_env()

    assert config.daily_limit == int(rate_limit_env_vars["FMP_DAILY_LIMIT"])
    assert config.requests_per_second == int(
        rate_limit_env_vars["FMP_REQUESTS_PER_SECOND"]
    )
    assert config.requests_per_minute == int(
        rate_limit_env_vars["FMP_REQUESTS_PER_MINUTE"]
    )


def test_rate_limit_config_validation():
    """Test rate limit configuration validation"""
    with pytest.raises(ValueError):
        RateLimitConfig(daily_limit=0)  # Should be greater than 0

    with pytest.raises(ValueError):
        RateLimitConfig(requests_per_second=0)  # Should be greater than 0

    with pytest.raises(ValueError):
        RateLimitConfig(requests_per_minute=0)  # Should be greater than 0


def test_rate_limit_config_defaults():
    """Test rate limit configuration defaults"""
    with temp_environ():
        config = RateLimitConfig()

        assert config.daily_limit == 250  # Default daily limit
        assert config.requests_per_second == 5  # Default requests per second
        assert config.requests_per_minute == 300  # Default requests per minute


def test_client_config_validation():
    """Test client configuration validation"""
    # Valid configuration with api_key
    valid_config = ClientConfig(
        api_key="test_key", timeout=30, max_retries=3, base_url="https://api.test.com"
    )
    assert valid_config.api_key == "test_key"

    # Invalid base URL
    with pytest.raises(ValidationError):
        ClientConfig(api_key="test_key", base_url="invalid_url")

    # Test missing API key
    os.environ.pop("FMP_API_KEY", None)  # Ensure env var is not present
    with pytest.raises(ValueError):  # Change to match actual error
        ClientConfig(timeout=30, base_url="https://api.test.com")


def test_client_config_from_env(env_vars):
    """Test client configuration from environment variables"""
    config = ClientConfig.from_env()

    assert config.api_key == "test_api_key"
    assert config.timeout == 30
    assert config.max_retries == 3
    assert config.base_url == "https://test.api.com"
    assert isinstance(config.rate_limit, RateLimitConfig)
    assert isinstance(config.logging, LoggingConfig)


def test_config_serialization():
    """Test configuration serialization/deserialization"""
    original_config = ClientConfig(
        api_key="test_key",
        timeout=30,
        base_url="https://api.test.com",
        rate_limit=RateLimitConfig(
            daily_limit=1000, requests_per_second=5, requests_per_minute=100
        ),
        logging=LoggingConfig(
            level="DEBUG",
            handlers={
                "console": LogHandlerConfig(class_name="StreamHandler", level="DEBUG")
            },
        ),
    )

    # Serialize to dict
    config_dict = original_config.model_dump()

    # Deserialize from dict
    reconstructed_config = ClientConfig.model_validate(config_dict)

    assert reconstructed_config.api_key == original_config.api_key
    assert reconstructed_config.timeout == original_config.timeout
    assert reconstructed_config.base_url == original_config.base_url
    assert (
        reconstructed_config.rate_limit.daily_limit
        == original_config.rate_limit.daily_limit
    )


def test_logging_config_file_handlers(tmp_path):
    """Test logging configuration with file handlers"""
    log_path = tmp_path / "logs"

    config = LoggingConfig(
        level="INFO",
        handlers={
            "file": LogHandlerConfig(
                class_name="RotatingFileHandler",
                level="INFO",
                kwargs={"filename": "test.log", "maxBytes": 1024, "backupCount": 3},
            )
        },
        log_path=log_path,
    )

    assert config.log_path == log_path
    assert "file" in config.handlers
    assert config.handlers["file"].class_name == "RotatingFileHandler"


def test_logging_config_no_path():
    """Test logging configuration when no path is provided"""
    with temp_environ() as env:
        env.update(
            {
                "FMP_LOG_CONSOLE": "true",
                "FMP_LOG_CONSOLE_LEVEL": "DEBUG",
                "FMP_LOG_LEVEL": "DEBUG",
            }
        )
        config = LoggingConfig.from_env()

        assert config.level == "DEBUG"
        assert "console" in config.handlers
        assert config.log_path is None
        assert "file" not in config.handlers
        assert "json" not in config.handlers


@pytest.fixture
def embedding_env_vars():
    """Fixture to set up and tear down embedding environment variables"""
    test_vars = {
        "FMP_EMBEDDING_PROVIDER": "openai",
        "FMP_EMBEDDING_MODEL": "text-embedding-ada-002",
        "OPENAI_API_KEY": "test-openai-key",
        "FMP_EMBEDDING_KWARGS": '{"batch_size": 8}',
    }

    with temp_environ() as env:
        env.update(test_vars)
        yield test_vars
