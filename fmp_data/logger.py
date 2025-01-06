# fmp_data/logger.py
import inspect
import json
import logging
import os
import re
import sys
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional, TypeVar

from fmp_data.config import LoggingConfig, LogHandlerConfig

T = TypeVar("T")


class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in log records"""

    def __init__(self) -> None:
        super().__init__()
        # Patterns for sensitive data
        self.patterns: dict[str, re.Pattern[str]] = {
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

        self.sensitive_keys: set[str] = {
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
        if not value:
            return value
        if len(value) <= 8:
            return mask_char * len(value)
        return f"{value[:2]}{mask_char * (len(value) - 4)}{value[-2:]}"

    def _mask_dict_recursive(self, d: Any, parent_key: str = "") -> Any:
        """Recursively mask sensitive values in dictionaries and lists"""
        """Recursively mask sensitive values in dictionaries and lists"""
        if isinstance(d, dict):
            result: dict[str, Any] = {}
            for k, v in d.items():
                key = k.lower() if isinstance(k, str) else k
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
                    )
                else:
                    result[k] = v
            return result

        elif isinstance(d, list):
            return [self._mask_dict_recursive(item, parent_key) for item in d]

        return d

    def _mask_patterns_in_string(self, text: Any) -> Any:
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
        if hasattr(record, "msg"):
            record.msg = self._mask_patterns_in_string(str(record.msg))

        if hasattr(record, "extra"):
            record.extra = self._mask_dict_recursive(deepcopy(record.extra))

        if record.args:
            args = list(record.args)
            for i, arg in enumerate(args):
                if isinstance(arg, dict | list):
                    args[i] = self._mask_dict_recursive(arg)
                elif isinstance(arg, str):
                    args[i] = self._mask_patterns_in_string(arg)
            record.args = tuple(args)

        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
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

        if record.exc_info and record.exc_info[0]:
            exc_type = record.exc_info[0]
            exc_value = record.exc_info[1]
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type else "Unknown",
                "message": str(exc_value) if exc_value else "",
                "traceback": self.formatException(record.exc_info),
            }

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data, default=str)


class SecureRotatingFileHandler(RotatingFileHandler):
    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ) -> None:
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        if not delay:
            self._set_secure_permissions()

    def _open(self) -> Any:
        stream = super()._open()
        self._set_secure_permissions()
        return stream

    def _set_secure_permissions(self) -> None:
        if sys.platform != "win32":
            try:
                os.chmod(self.baseFilename, 0o600)
            except OSError as e:
                logging.getLogger(__name__).warning(
                    f"Could not set secure permissions on log file: {e}"
                )


class FMPLogger:
    _instance: Optional["FMPLogger"] = None
    _handler_classes: dict[str, type[logging.Handler]] = {
        "StreamHandler": logging.StreamHandler,
        "FileHandler": logging.FileHandler,
        "RotatingFileHandler": SecureRotatingFileHandler,
        "JsonRotatingFileHandler": SecureRotatingFileHandler,
    }
    _initialized: bool = False

    def __new__(cls) -> "FMPLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._logger = logging.getLogger("fmp_data")
        self._logger.setLevel(logging.INFO)
        self._handlers: dict[str, logging.Handler] = {}

        self._logger.addFilter(SensitiveDataFilter())

        if not self._logger.handlers:
            self._add_default_console_handler()

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """
        Get a logger instance with the given name

        Args:
            name: Optional name for the logger

        Returns:
            logging.Logger: Logger instance
        """
        if name:
            return self._logger.getChild(name)
        return self._logger

    def _add_default_console_handler(self) -> None:
        """Add default console handler with a reasonable format"""
        handler = logging.StreamHandler()  # Initialize without arguments
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._handlers["console"] = handler

    def configure(self, config: LoggingConfig) -> None:
        self._logger.setLevel(getattr(logging, config.level))

        for handler in list(self._handlers.values()):
            self._logger.removeHandler(handler)
            handler.close()
        self._handlers.clear()

        if config.log_path:
            config.log_path.mkdir(parents=True, exist_ok=True)
            if sys.platform != "win32":
                try:
                    os.chmod(config.log_path, 0o700)
                except OSError as e:
                    self._logger.warning(
                        f"Could not set secure permissions on log directory: {e}"
                    )

        for name, handler_config in config.handlers.items():
            self._add_handler(name, handler_config, config.log_path)

    def _add_handler(
        self, name: str, config: LogHandlerConfig, log_path: Path | None = None
    ) -> None:
        """
        Add a handler based on configuration.

        Args:
            name: Handler name
            config: Handler configuration
            log_path: Optional base path for log files
        """
        handler_class = self._handler_classes.get(config.class_name)
        if not handler_class:
            raise ValueError(f"Unknown handler class: {config.class_name}")

        # Use handler_kwargs instead of kwargs
        kwargs = config.handler_kwargs.copy()

        if "filename" in kwargs and log_path:
            kwargs["filename"] = log_path / kwargs["filename"]

        if config.class_name == "StreamHandler":
            handler = handler_class()  # Initialize without arguments
            if hasattr(handler, "stream"):
                handler.stream = sys.stdout  # Set stream after initialization
        else:
            handler = handler_class(**kwargs)

        if config.class_name == "JsonRotatingFileHandler":
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(logging.Formatter(config.format))

        handler.setLevel(getattr(logging, config.level))
        self._logger.addHandler(handler)
        self._handlers[name] = handler


def log_api_call(
    logger: logging.Logger | None = None,
    exclude_args: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal logger
            if logger is None:
                logger = FMPLogger().get_logger()

            current_frame = inspect.currentframe()
            if current_frame:
                back_frame = current_frame.f_back
                module = inspect.getmodule(back_frame) if back_frame else None
                module_name = module.__name__ if module else ""
            else:
                module_name = ""

            log_context: dict[str, Any] = {
                "function_name": func.__name__,
                "module_path": module_name,
            }

            if not exclude_args:
                safe_kwargs = deepcopy(kwargs)
                log_context.update(
                    {
                        "call_args": args[1:],
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
