# tests/test_logger.py
import asyncio
import json
import logging
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from fmp_data.config import LoggingConfig, LogHandlerConfig
from fmp_data.logger import (
    FMPLogger,
    JsonFormatter,
    SecureRotatingFileHandler,
    SensitiveDataFilter,
    log_api_call,
)


class TestSensitiveDataFilter:
    """Test SensitiveDataFilter functionality"""

    def test_filter_basic_functionality(self):
        """Test basic filter functionality"""
        filter_instance = SensitiveDataFilter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with api_key=secret123",
            args=(),
            exc_info=None,
        )

        # Filter should return True (allow record)
        assert filter_instance.filter(record) is True

        # Message should be modified to mask sensitive data
        assert "secret123" not in record.getMessage()
        assert "api_key=" in record.getMessage()

    def test_mask_patterns_in_string(self):
        """Test pattern masking in strings"""
        filter_instance = SensitiveDataFilter()

        test_cases = [
            ("api_key=secret123", "secret123"),
            ("password=mypassword", "mypassword"),
            ('apikey="test-key-12345"', "test-key-12345"),
            ("token=bearer-token-xyz", "bearer-token-xyz"),
            ("key=somekey", "somekey"),
        ]

        for original, sensitive_part in test_cases:
            masked = filter_instance._mask_patterns_in_string(original)
            assert sensitive_part not in masked
            assert "=" in masked  # The key part should remain

    def test_mask_value(self):
        """Test value masking function"""
        filter_instance = SensitiveDataFilter()

        # Short values
        assert filter_instance._mask_value("123") == "***"
        assert filter_instance._mask_value("ab") == "**"

        # Medium values (should be fully masked)
        assert filter_instance._mask_value("test") == "****"
        assert filter_instance._mask_value("secret") == "******"

        # Longer values (should show first 2 and last 2 chars)
        assert filter_instance._mask_value("longvalue") == "lo*****ue"
        assert filter_instance._mask_value("verylongvalue") == "ve*********ue"

    def test_filter_with_dict_args(self):
        """Test filter with dictionary arguments"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request with data: %s",
            args=({"api_key": "secret123", "symbol": "AAPL"},),
            exc_info=None,
        )

        assert filter_instance.filter(record) is True
        message = record.getMessage()
        assert "secret123" not in message
        assert "symbol" in message or "AAPL" in message

    def test_filter_with_nested_dict(self):
        """Test filter with nested dictionary structures"""
        filter_instance = SensitiveDataFilter()

        nested_data = {
            "config": {"api_key": "nested_secret", "timeout": 30},
            "symbol": "AAPL",
        }

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Nested data: %s",
            args=(nested_data,),
            exc_info=None,
        )

        assert filter_instance.filter(record) is True
        message = record.getMessage()
        assert "nested_secret" not in message
        assert "timeout" in message or "30" in message

    def test_filter_with_list_args(self):
        """Test filter with list arguments containing sensitive data"""
        filter_instance = SensitiveDataFilter()

        list_data = ["AAPL", {"api_key": "list_secret"}, "MSFT"]

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="List data: %s",
            args=(list_data,),
            exc_info=None,
        )

        assert filter_instance.filter(record) is True
        message = record.getMessage()
        assert "list_secret" not in message
        assert "AAPL" in message

    def test_no_sensitive_data(self):
        """Test filter with no sensitive data"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal log message with symbol=AAPL",
            args=(),
            exc_info=None,
        )

        original_message = record.getMessage()
        assert filter_instance.filter(record) is True
        assert record.getMessage() == original_message  # Should be unchanged


class TestJsonFormatter:
    """Test JsonFormatter functionality"""

    def test_format_basic_record(self):
        """Test basic JSON formatting"""
        formatter = JsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        json_data = json.loads(formatted)

        assert json_data["level"] == "INFO"
        assert json_data["message"] == "Test message"
        assert json_data["module"] == "test_logger"
        assert json_data["line"] == 42
        assert "timestamp" in json_data

    def test_format_with_extra_fields(self):
        """Test JSON formatting with extra fields"""
        formatter = JsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.request_id = "12345"
        record.user_id = "user_abc"

        formatted = formatter.format(record)
        json_data = json.loads(formatted)

        assert json_data["request_id"] == "12345"
        assert json_data["user_id"] == "user_abc"

    def test_format_with_exception(self):
        """Test JSON formatting with exception information"""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info,
        )

        formatted = formatter.format(record)
        json_data = json.loads(formatted)

        assert "exception" in json_data
        assert "ValueError" in json_data["exception"]["type"]

    def test_format_excludes_private_attributes(self):
        """Test that private attributes are excluded from JSON"""
        formatter = JsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add private attribute
        record._private_attr = "should_not_appear"

        formatted = formatter.format(record)
        json_data = json.loads(formatted)

        assert "_private_attr" not in json_data


class TestSecureRotatingFileHandler:
    """Test SecureRotatingFileHandler functionality"""

    def test_file_creation_with_permissions(self, tmp_path):
        """Test file creation with secure permissions"""
        log_file = tmp_path / "secure.log"

        handler = SecureRotatingFileHandler(
            filename=str(log_file), maxBytes=1024, backupCount=3
        )

        # Write a test message
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Check file exists
        assert log_file.exists()

        # Check permissions on Unix-like systems
        if os.name != "nt":
            stat_info = log_file.stat()
            permissions = stat_info.st_mode & 0o777
            assert permissions == 0o600

    def test_permission_error_handling(self, tmp_path):
        """Test handling of permission errors"""
        log_file = tmp_path / "test.log"

        with patch("os.chmod", side_effect=OSError("Permission denied")):
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                _ = SecureRotatingFileHandler(filename=str(log_file))

                # Should have logged a warning (possibly called once during init)
                assert mock_logger.warning.called
                assert "Could not set secure permissions" in str(
                    mock_logger.warning.call_args_list
                )

    def test_windows_skip_permissions(self, tmp_path):
        """Test that permission setting is skipped on Windows"""
        log_file = tmp_path / "test.log"

        with patch("os.name", "nt"):
            with patch("os.chmod") as mock_chmod:
                handler = SecureRotatingFileHandler(filename=str(log_file))

                # Write a record to trigger file creation
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg="Test",
                    args=(),
                    exc_info=None,
                )
                handler.emit(record)

                # chmod should not be called on Windows
                mock_chmod.assert_not_called()


class TestFMPLogger:
    """Test FMPLogger functionality"""

    def setup_method(self):
        # Reset the singleton instance before each test
        FMPLogger._instance = None

    def test_singleton_pattern(self):
        """Test that FMPLogger implements singleton pattern"""
        logger1 = FMPLogger()
        logger2 = FMPLogger()

        assert logger1 is logger2

    def test_initialization_idempotent(self):
        """Test that multiple initializations don't cause issues"""
        logger = FMPLogger()
        original_initialized = logger._initialized

        # Initialize again
        logger.__init__()

        # Should still be initialized
        assert logger._initialized == original_initialized

    def test_get_logger_with_name(self):
        """Test getting logger with specific name"""
        fmp_logger = FMPLogger()

        named_logger = fmp_logger.get_logger("test.module")
        assert named_logger.name == "fmp_data.test.module"

    def test_get_logger_without_name(self):
        """Test getting logger without name"""
        fmp_logger = FMPLogger()

        default_logger = fmp_logger.get_logger()
        assert default_logger.name == "fmp_data"

    def test_get_logger_none_name(self):
        """Test getting logger with None name"""
        fmp_logger = FMPLogger()

        logger = fmp_logger.get_logger(None)
        assert logger.name == "fmp_data"

    def test_default_console_handler_added(self):
        """Test that default console handler is added"""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            _ = FMPLogger()

            # Should have added console handler
            assert mock_logger.addHandler.called

    def test_sensitive_data_filter_added(self):
        """Test that sensitive data filter is added to logger"""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            _ = FMPLogger()

            # Should have added filter
            assert mock_logger.addFilter.called
            filter_arg = mock_logger.addFilter.call_args[0][0]
            assert isinstance(filter_arg, SensitiveDataFilter)

    def test_configure_removes_existing_handlers(self):
        """Test that configure removes existing handlers"""
        fmp_logger = FMPLogger()

        # Add a mock handler
        mock_handler = Mock()
        fmp_logger._handlers["test"] = mock_handler
        fmp_logger._logger.addHandler(mock_handler)

        config = LoggingConfig(
            level="DEBUG",
            handlers={"console": LogHandlerConfig(class_name="StreamHandler")},
        )

        fmp_logger.configure(config)

        # Old handler should be removed and closed
        mock_handler.close.assert_called_once()
        assert "test" not in fmp_logger._handlers

    def test_configure_sets_log_level(self):
        """Test that configure sets the correct log level"""
        fmp_logger = FMPLogger()

        config = LoggingConfig(level="WARNING")
        fmp_logger.configure(config)

        assert fmp_logger._logger.level == logging.WARNING

    def test_configure_creates_log_directory(self, tmp_path):
        """Test that configure creates log directory when specified"""
        log_path = tmp_path / "logs" / "nested"

        config = LoggingConfig(
            level="INFO",
            log_path=log_path,
            handlers={
                "file": LogHandlerConfig(
                    class_name="FileHandler", handler_kwargs={"filename": "test.log"}
                )
            },
        )

        fmp_logger = FMPLogger()
        fmp_logger.configure(config)

        assert log_path.exists()
        assert log_path.is_dir()

    def test_configure_sets_directory_permissions(self, tmp_path):
        """Test that configure sets secure directory permissions"""
        log_path = tmp_path / "secure_logs"

        config = LoggingConfig(level="INFO", log_path=log_path, handlers={})

        with patch("os.chmod") as mock_chmod:
            with patch("sys.platform", "linux"):
                fmp_logger = FMPLogger()
                fmp_logger.configure(config)

                if os.name != "nt":
                    mock_chmod.assert_called_with(log_path, 0o700)

    def test_configure_handles_permission_error(self, tmp_path):
        """Test configure handles directory permission errors"""
        log_path = tmp_path / "logs"

        config = LoggingConfig(level="INFO", log_path=log_path, handlers={})

        with patch("os.chmod", side_effect=OSError("Permission denied")):
            with patch.object(FMPLogger()._logger, "warning") as mock_warning:
                fmp_logger = FMPLogger()
                fmp_logger.configure(config)

                mock_warning.assert_called_once()

    def test_add_handler_stream_handler(self):
        """Test adding StreamHandler"""
        fmp_logger = FMPLogger()
        config = LogHandlerConfig(class_name="StreamHandler", level="INFO")

        fmp_logger._add_handler("console", config)

        assert "console" in fmp_logger._handlers
        handler = fmp_logger._handlers["console"]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.level == logging.INFO

    def test_add_handler_file_handler(self, tmp_path):
        """Test adding FileHandler"""
        log_file = tmp_path / "test.log"
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(
            class_name="FileHandler",
            level="DEBUG",
            handler_kwargs={"filename": str(log_file)},
        )

        fmp_logger._add_handler("file", config, tmp_path)

        assert "file" in fmp_logger._handlers
        handler = fmp_logger._handlers["file"]
        assert isinstance(handler, logging.FileHandler)

    def test_add_handler_rotating_file_handler(self, tmp_path):
        """Test adding RotatingFileHandler"""
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(
            class_name="RotatingFileHandler",
            level="INFO",
            handler_kwargs={
                "filename": "rotating.log",
                "maxBytes": 1024,
                "backupCount": 3,
            },
        )

        fmp_logger._add_handler("rotating", config, tmp_path)

        assert "rotating" in fmp_logger._handlers
        handler = fmp_logger._handlers["rotating"]
        assert isinstance(handler, SecureRotatingFileHandler)

    def test_add_handler_json_handler(self, tmp_path):
        """Test adding JSON handler with JsonFormatter"""
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(
            class_name="JsonRotatingFileHandler",
            level="DEBUG",
            handler_kwargs={"filename": "json.log", "maxBytes": 2048},
        )

        fmp_logger._add_handler("json", config, tmp_path)

        assert "json" in fmp_logger._handlers
        handler = fmp_logger._handlers["json"]
        assert isinstance(handler.formatter, JsonFormatter)

    def test_add_handler_unknown_class(self):
        """Test adding handler with unknown class raises error"""
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(class_name="UnknownHandler")

        with pytest.raises(ValueError, match="Unknown handler class"):
            fmp_logger._add_handler("unknown", config)

    def test_add_handler_with_log_path(self, tmp_path):
        """Test adding handler with log path modifies filename"""
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(
            class_name="FileHandler", handler_kwargs={"filename": "test.log"}
        )

        fmp_logger._add_handler("file", config, tmp_path)

        handler = fmp_logger._handlers["file"]
        # Should have combined log_path with filename
        assert str(tmp_path) in handler.baseFilename

    def test_add_handler_with_relative_filename(self, tmp_path):
        """Test adding handler with relative filename prepends log_path."""
        fmp_logger = FMPLogger()

        config = LogHandlerConfig(
            class_name="FileHandler", handler_kwargs={"filename": "relative.log"}
        )

        fmp_logger._add_handler("file", config, tmp_path)

        handler = fmp_logger._handlers["file"]
        # Should have prepended log_path to relative filename
        assert handler.baseFilename == str(tmp_path / "relative.log")

    def test_add_handler_with_absolute_filename(self, tmp_path):
        """Test adding handler with absolute filename does NOT prepend log_path."""
        fmp_logger = FMPLogger()

        absolute_path = tmp_path / "absolute_logs" / "absolute.log"
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        config = LogHandlerConfig(
            class_name="FileHandler", handler_kwargs={"filename": str(absolute_path)}
        )

        other_log_path = tmp_path / "other_logs"
        other_log_path.mkdir(parents=True, exist_ok=True)

        fmp_logger._add_handler("file", config, other_log_path)

        handler = fmp_logger._handlers["file"]
        # Should NOT have prepended other_log_path - should use the absolute path as-is
        assert handler.baseFilename == str(absolute_path)
        assert str(other_log_path) not in handler.baseFilename

    def test_add_handler_no_log_path(self, tmp_path):
        """Test adding handler without log_path uses filename as-is."""
        fmp_logger = FMPLogger()

        log_file = tmp_path / "standalone.log"

        config = LogHandlerConfig(
            class_name="FileHandler", handler_kwargs={"filename": str(log_file)}
        )

        fmp_logger._add_handler("file", config, log_path=None)

        handler = fmp_logger._handlers["file"]
        # Should use the filename as provided
        assert handler.baseFilename == str(log_file)


class TestLogApiCallDecorator:
    """Test log_api_call decorator functionality"""

    def test_decorator_basic_usage(self):
        """Test basic decorator usage"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        def test_function(arg1, arg2="default"):
            return f"{arg1}-{arg2}"

        result = test_function("test", arg2="value")

        assert result == "test-value"
        assert mock_logger.debug.call_count >= 1

    def test_decorator_with_default_logger(self):
        """Test decorator with default logger"""
        with patch.object(FMPLogger(), "get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            @log_api_call()
            def test_function():
                return "success"

            result = test_function()

            assert result == "success"
            mock_logger.debug.assert_called()

    def test_decorator_exclude_args(self):
        """Test decorator with exclude_args=True"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger, exclude_args=True)
        def test_function(sensitive_arg):
            return "result"

        result = test_function("secret_data")

        assert result == "result"
        # Should still log function call but without args
        mock_logger.debug.assert_called()

    def test_decorator_logs_success(self):
        """Test decorator logs successful execution"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        def successful_function():
            return "success"

        result = successful_function()

        assert result == "success"
        # Should have logged both start and success
        assert mock_logger.debug.call_count >= 2

    def test_decorator_logs_error(self):
        """Test decorator logs errors"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Should have logged error
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_decorator_async_function(self):
        """Test decorator with async function"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        async def async_function(value):
            await asyncio.sleep(0.01)
            return f"async-{value}"

        result = await async_function("test")

        assert result == "async-test"
        mock_logger.debug.assert_called()

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        def documented_function():
            """This is a test function."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function."

    def test_decorator_with_frame_inspection(self):
        """Test decorator with frame inspection for module name"""
        mock_logger = Mock()

        @log_api_call(logger=mock_logger)
        def test_function():
            return "result"

        test_function()

        # Check that module information was logged
        debug_calls = mock_logger.debug.call_args_list
        assert len(debug_calls) >= 1

        # The call should include module information
        call_args = debug_calls[0]
        assert "API call:" in call_args[0][0]

    def test_decorator_no_frame_available(self):
        """Test decorator when frame inspection fails"""
        mock_logger = Mock()

        with patch("inspect.currentframe", return_value=None):

            @log_api_call(logger=mock_logger)
            def test_function():
                return "result"

            result = test_function()
            assert result == "result"
            mock_logger.debug.assert_called()


class TestLoggerIntegration:
    """Test logger integration scenarios"""

    def setup_method(self):
        # Reset the singleton instance before each test
        FMPLogger._instance = None

    def test_complete_logging_setup(self, tmp_path):
        """Test complete logging setup with multiple handlers"""
        log_path = tmp_path / "logs"

        config = LoggingConfig(
            level="DEBUG",
            log_path=log_path,
            handlers={
                "console": LogHandlerConfig(class_name="StreamHandler", level="INFO"),
                "file": LogHandlerConfig(
                    class_name="RotatingFileHandler",
                    level="DEBUG",
                    handler_kwargs={
                        "filename": "app.log",
                        "maxBytes": 1024,
                        "backupCount": 2,
                    },
                ),
                "json": LogHandlerConfig(
                    class_name="JsonRotatingFileHandler",
                    level="WARNING",
                    handler_kwargs={"filename": "app.json"},
                ),
            },
        )

        fmp_logger = FMPLogger()
        fmp_logger.configure(config)

        # Test that all handlers were created
        assert len(fmp_logger._handlers) == 3
        assert "console" in fmp_logger._handlers
        assert "file" in fmp_logger._handlers
        assert "json" in fmp_logger._handlers

        # Test that log directory was created
        assert log_path.exists()

    def test_reconfiguration(self):
        """Test that logger can be reconfigured with _force flag"""
        fmp_logger = FMPLogger()

        # Initial configuration
        config1 = LoggingConfig(
            level="INFO",
            handlers={"console": LogHandlerConfig(class_name="StreamHandler")},
        )
        fmp_logger.configure(config1, _force=True)

        # Reconfigure (with _force flag for testing)
        config2 = LoggingConfig(
            level="DEBUG",
            handlers={
                "console": LogHandlerConfig(class_name="StreamHandler"),
                "new_handler": LogHandlerConfig(class_name="StreamHandler"),
            },
        )
        fmp_logger.configure(config2, _force=True)

        # Should have new handlers
        assert len(fmp_logger._handlers) == 2
        assert "new_handler" in fmp_logger._handlers

    def test_filter_integration(self):
        """Test sensitive data filter integration"""
        fmp_logger = FMPLogger()
        logger = fmp_logger.get_logger("test")

        # Ensure filter is added to the child logger as well
        filter_instance = SensitiveDataFilter()
        logger.addFilter(filter_instance)

        # Create a test handler to capture output
        import io

        test_stream = io.StringIO()
        test_handler = logging.StreamHandler(test_stream)
        test_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(test_handler)
        logger.setLevel(logging.INFO)

        # Log sensitive data
        logger.info("Request with api_key=secret123")

        # Check that data was masked
        output = test_stream.getvalue()
        assert "secret123" not in output
        assert "api_key=" in output
