import json
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from fmp_data.config import LoggingConfig, LogHandlerConfig
from fmp_data.logger import (
    FMPLogger,
    JsonFormatter,
    SecureRotatingFileHandler,
    SensitiveDataFilter,
    log_api_call,
)


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary directory for log files"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def basic_config(temp_log_dir):
    """Create basic logging configuration"""
    return LoggingConfig(
        level="DEBUG",
        handlers={
            "console": LogHandlerConfig(
                class_name="StreamHandler",
                level="DEBUG",
                format="%(levelname)s: %(message)s",
            ),
            "file": LogHandlerConfig(
                class_name="RotatingFileHandler",
                level="DEBUG",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handler_kwargs={  # Changed from kwargs to handler_kwargs
                    "filename": str(temp_log_dir / "test.log"),
                    "maxBytes": 1024,
                    "backupCount": 3,
                },
            ),
        },
        log_path=temp_log_dir,
    )


class MockLogRecord:
    def __init__(self, msg):
        self.msg = msg
        self.args = ()


def test_json_formatter():
    """Test JSON log formatter"""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        "test_logger",
        logging.INFO,
        "test.py",
        10,
        "Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    log_data = json.loads(formatted)

    assert log_data["name"] == "test_logger"
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"


def test_secure_rotating_file_handler(temp_log_dir):
    """Test secure file handler creation and permissions"""
    log_file = temp_log_dir / "secure.log"
    handler = SecureRotatingFileHandler(
        filename=str(log_file), maxBytes=1024, backupCount=3
    )

    # Write test log
    logger = logging.getLogger("test")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("Test message")

    # Check file exists and has correct permissions
    assert log_file.exists()
    if os.name != "nt":  # Skip permission check on Windows
        assert (log_file.stat().st_mode & 0o777) == 0o600


@patch("logging.getLogger")
def test_fmp_logger_singleton(mock_get_logger):
    """Test FMPLogger singleton pattern"""
    logger1 = FMPLogger()
    logger2 = FMPLogger()
    assert logger1 is logger2


@pytest.mark.asyncio
async def test_log_api_call_decorator():
    """Test API call logging decorator"""
    mock_logger = MagicMock()

    @log_api_call(logger=mock_logger)
    async def test_func(arg1, arg2=None):
        return f"{arg1}-{arg2}"

    result = await test_func("test", arg2="value")
    assert result == "test-value"

    # Verify logging calls
    mock_logger.debug.assert_called()
    assert "API call" in mock_logger.debug.call_args_list[0][0][0]


def test_logger_configuration(basic_config):
    """Test logger configuration with different handlers"""
    logger = FMPLogger()
    logger.configure(basic_config)

    root_logger = logger.get_logger()
    assert root_logger.level == logging.DEBUG

    # Verify handler types and count
    handlers = root_logger.handlers
    handler_types = {handler.__class__.__name__ for handler in handlers}

    assert len(handlers) == 2  # Should have exactly two handlers
    assert "StreamHandler" in handler_types
    assert "SecureRotatingFileHandler" in handler_types

    # Verify handler levels
    for handler in handlers:
        assert handler.level == logging.DEBUG


def test_logger_message_filtering():
    """Test message filtering for sensitive data"""

    class TestFilter(SensitiveDataFilter):
        def _mask_patterns_in_string(self, text):
            # Override to ensure masking happens
            return text.replace("secret123", "*****")

    filter = TestFilter()

    # Create a record with sensitive data
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="API key: secret123",
        args=(),
        exc_info=None,
    )

    # Apply the filter
    filter.filter(record)

    # Verify the message was modified
    assert record.msg == "API key: *****"


def test_log_rotation(temp_log_dir):
    """Test log file rotation"""
    config = LoggingConfig(
        level="DEBUG",
        handlers={
            "file": LogHandlerConfig(
                class_name="RotatingFileHandler",
                level="DEBUG",
                handler_kwargs={  # Changed from kwargs to handler_kwargs
                    "filename": str(temp_log_dir / "rotating.log"),
                    "maxBytes": 100,  # Small size to trigger rotation
                    "backupCount": 2,
                },
            ),
        },
        log_path=temp_log_dir,
    )

    logger = FMPLogger()
    logger.configure(config)
    test_logger = logger.get_logger("test")

    # Write enough data to trigger rotation
    long_message = "x" * 50
    for _ in range(5):
        test_logger.info(long_message)

    log_files = list(temp_log_dir.glob("rotating.log*"))
    assert len(log_files) > 1  # Main log file plus at least one backup


def test_sensitive_data_filter():
    """Test sensitive data masking"""
    filter = SensitiveDataFilter()

    # Test API key masking
    original = "api_key=secret123"
    masked = filter._mask_patterns_in_string(original)
    assert "secret123" not in masked
    assert "api_key=" in masked
    assert len(masked) > len("api_key=")  # Ensure masking occurred

    # Test with actual API key pattern
    api_key_str = 'api_key="ACTUAL-KEY-12345"'
    masked_api = filter._mask_patterns_in_string(api_key_str)
    assert "ACTUAL-KEY-12345" not in masked_api
    assert 'api_key="' in masked_api


def test_error_handling(basic_config):
    """Test error handling in logger configuration"""
    logger = FMPLogger()

    # Test invalid handler class
    invalid_config = LoggingConfig(
        level="DEBUG",
        handlers={
            "invalid": LogHandlerConfig(
                class_name="NonexistentHandler",
                level="DEBUG",
            ),
        },
    )

    with pytest.raises(ValueError):
        logger.configure(invalid_config)


def test_mask_value():
    """Test the mask_value function directly"""
    filter = SensitiveDataFilter()

    # Test short value
    assert filter._mask_value("123") == "***"

    # Test longer value
    masked = filter._mask_value("abcdef")
    assert len(masked) == len("abcdef")
    assert all(c == "*" for c in masked)


@pytest.mark.asyncio
async def test_async_logging():
    """Test logging in async context"""
    mock_logger = MagicMock()

    @log_api_call(logger=mock_logger)
    async def async_operation():
        return "success"

    result = await async_operation()
    assert result == "success"
    mock_logger.debug.assert_called()
