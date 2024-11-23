# logging.py
import inspect
import json
import logging
import os
import re
import sys
from copy import deepcopy
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fmp_data.config import LoggingConfig, LogHandlerConfig


class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in log records"""

    def __init__(self):
        super().__init__()
        # Patterns for sensitive data
        self.patterns = {
            "api_key": re.compile(
                r'([\'"]?api_?key[\'"]?\s*[=:]\s*[\'"]?)([^\'"\s&]+)([\'"]?)',
                re.IGNORECASE,
            ),
            "authorization": re.compile(
                r"(Authorization:\s*Bearer\s+)(\S+)", re.IGNORECASE
            ),
            "password": re.compile(
                r'([\'"]?password[\'"]?\s*[=:]\s*[\'"]?)([^\'"\s&]+)([\'"]?)',
                re.IGNORECASE,
            ),
            "token": re.compile(
                r'([\'"]?token[\'"]?\s*[=:]\s*[\'"]?)([^\'"\s&]+)([\'"]?)',
                re.IGNORECASE,
            ),
            "secret": re.compile(
                r'([\'"]?\w*secret\w*[\'"]?\s*[=:]\s*[\'"]?)([^\'"\s&]+)([\'"]?)',
                re.IGNORECASE,
            ),
        }

        # Additional exact match keywords to mask
        self.sensitive_keys = {
            "api_key",
            "apikey",
            "api-key",
            "token",
            "password",
            "secret",
            "access_token",
            "refresh_token",
            "auth_token",
            "bearer_token",
        }

    @staticmethod
    def _mask_value(value: str, mask_char: str = "*") -> str:
        """Mask a sensitive value, keeping first 2 and last 2 characters visible"""
        if not value:
            return value
        if len(value) <= 8:
            return mask_char * len(value)
        return f"{value[:2]}{mask_char * (len(value) - 4)}{value[-2:]}"

    def _mask_dict_recursive(self, d: dict | list, parent_key: str = "") -> dict | list:
        """Recursively mask sensitive values in dictionaries and lists"""
        if isinstance(d, dict):
            result = {}
            for k, v in d.items():
                key = k.lower() if isinstance(k, str) else k

                # Check if this key or its path contains sensitive information
                is_sensitive = any(
                    sensitive in str(key).lower() for sensitive in self.sensitive_keys
                ) or any(
                    sensitive in f"{parent_key}.{key}".lower()
                    for sensitive in self.sensitive_keys
                )

                if is_sensitive and isinstance(v, str | int | float):
                    result[k] = self._mask_value(str(v))
                elif isinstance(v, dict | list):
                    result[k] = json.dumps(
                        self._mask_dict_recursive(v, f"{parent_key}.{k}")
                    )  # Convert to string
                else:
                    result[k] = v
            return result
        elif isinstance(d, list):
            return [self._mask_dict_recursive(item, parent_key) for item in d]
        return d

    def _mask_patterns_in_string(self, text: str) -> str:
        """Mask sensitive patterns in a string"""
        if not isinstance(text, str):
            return text

        masked_text = text
        for pattern in self.patterns.values():
            masked_text = pattern.sub(
                lambda m: f"{m.group(1)}{self._mask_value(m.group(2))}{m.group(3)}",
                masked_text,
            )
        return masked_text

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask sensitive data in log records"""
        if hasattr(record, "msg"):
            record.msg = self._mask_patterns_in_string(str(record.msg))

        if hasattr(record, "extra"):
            record.extra = self._mask_dict_recursive(deepcopy(record.extra))

        if record.args:
            args = list(record.args)
            for i, arg in enumerate(args):
                if isinstance(arg, dict | list):
                    args[i] = self._mask_dict_recursive(deepcopy(arg))
                elif isinstance(arg, str):
                    args[i] = self._mask_patterns_in_string(arg)
            record.args = tuple(args)

        return True


class JsonFormatter(logging.Formatter):
    """JSON log formatter with sensitive data masking"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
            "threadId": record.thread,
            "threadName": record.threadName,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add custom fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data, default=str)


class SecureRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler with added security measures"""

    def __init__(
        self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None, delay=False
    ):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        if not delay:
            self._set_secure_permissions()

    def _open(self):
        """Open the file with secure permissions"""
        stream = super()._open()
        self._set_secure_permissions()
        return stream

    def _set_secure_permissions(self):
        """Set secure file permissions"""
        if sys.platform != "win32":
            try:
                os.chmod(self.baseFilename, 0o600)
            except OSError as e:
                logging.getLogger(__name__).warning(
                    f"Could not set secure permissions on log file: {e}"
                )


class FMPLogger:
    """Centralized logging configuration for FMP Data package"""

    _instance = None
    _handler_classes = {
        "StreamHandler": logging.StreamHandler,
        "FileHandler": logging.FileHandler,
        "RotatingFileHandler": SecureRotatingFileHandler,
        "JsonRotatingFileHandler": SecureRotatingFileHandler,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._logger = logging.getLogger("fmp_data")
        self._logger.setLevel(logging.INFO)
        self._handlers = {}

        # Add sensitive data filter to root logger
        self._logger.addFilter(SensitiveDataFilter())

        # Add default console handler if no handlers exist
        if not self._logger.handlers:
            self._add_default_console_handler()

    def _add_default_console_handler(self):
        """Add default console handler with a reasonable format"""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._handlers["console"] = handler

    def configure(self, config: LoggingConfig) -> None:
        """Configure logging based on provided configuration"""
        # Set root logger level
        self._logger.setLevel(getattr(logging, config.level))

        # Remove existing handlers
        for handler in list(self._handlers.values()):
            self._logger.removeHandler(handler)
            handler.close()
        self._handlers.clear()

        # Create log directory if specified
        if config.log_path:
            config.log_path.mkdir(parents=True, exist_ok=True)
            # Secure log directory permissions
            if sys.platform != "win32":
                try:
                    os.chmod(config.log_path, 0o700)
                except OSError as e:
                    self._logger.warning(
                        f"Could not set secure permissions on log directory: {e}"
                    )

        # Add configured handlers
        for name, handler_config in config.handlers.items():
            self._add_handler(name, handler_config, config.log_path)

    def _add_handler(
        self, name: str, config: LogHandlerConfig, log_path: Path | None = None
    ) -> None:
        """Add a handler based on configuration"""
        if not (handler_class := self._handler_classes.get(config.class_name)):
            raise ValueError(f"Unknown handler class: {config.class_name}")

        kwargs = config.kwargs.copy()

        # Handle filename for file-based handlers
        if "filename" in kwargs and log_path:
            kwargs["filename"] = log_path / kwargs["filename"]

        # Create handler
        if config.class_name == "StreamHandler":
            handler = handler_class(sys.stdout)
        else:
            handler = handler_class(**kwargs)

        # Set formatter
        if config.class_name == "JsonRotatingFileHandler":
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(logging.Formatter(config.format))

        # Set level and add handler
        handler.setLevel(getattr(logging, config.level))
        self._logger.addHandler(handler)
        self._handlers[name] = handler

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance with the given name"""
        if name:
            return self._logger.getChild(name)
        return self._logger


def log_api_call(logger: logging.Logger | None = None, exclude_args: bool = False):
    """
    Decorator to log API calls with parameters and response

    Args:
        logger: Optional logger instance to use
        exclude_args: Whether to exclude arguments from logs (useful for large payloads)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = FMPLogger().get_logger()

            frame = inspect.currentframe().f_back
            module = inspect.getmodule(frame)
            module_name = module.__name__ if module else ""

            # Create logging context - avoid using 'module' key
            log_context = {"function_name": func.__name__, "module_path": module_name}

            if not exclude_args:
                # Create a sanitized copy of kwargs for logging
                safe_kwargs = deepcopy(kwargs)
                log_context.update(
                    {
                        "call_args": args[1:],  # Skip self argument
                        "call_kwargs": safe_kwargs,
                    }
                )

            logger.debug(f"API call: {module_name}.{func.__name__}", extra=log_context)

            try:
                result = func(*args, **kwargs)
                logger.debug(
                    f"API response: {module_name}.{func.__name__}",
                    extra={**log_context, "status": "success"},
                )
                return result
            except Exception as e:
                logger.error(
                    f"API error in {module_name}.{func.__name__}: {str(e)}",
                    extra={
                        **log_context,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator
