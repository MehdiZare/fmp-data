# fmp_data/logger.py
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from functools import wraps
import inspect
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
from typing import Any, ClassVar, Optional, ParamSpec, TypeVar

from fmp_data.config import LoggingConfig, LogHandlerConfig

P = ParamSpec("P")
R = TypeVar("R")


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
            "key": re.compile(
                r'([\'"]?key[\'"]?\s*[=:]\s*[\'"]?)([^\'"\s&]+)([\'"]?)',
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
            "key",
        }

    @staticmethod
    def _mask_value(value: str, mask_char: str = "*") -> str:
        """Mask a sensitive value"""
        if not value:
            return value
        if len(value) <= 3:
            return mask_char * len(value)
        elif len(value) <= 8:
            return mask_char * len(value)
        else:
            # For longer values, show first 2 and last 2 characters, mask the middle
            return f"{value[:2]}{mask_char * (len(value) - 4)}{value[-2:]}"

    def _mask_patterns_in_string(self, text: Any) -> Any:
        """Mask patterns in a string"""
        if not isinstance(text, str):
            return text

        masked_text = text
        for pattern in self.patterns.values():

            def mask_replacement(match: Any) -> Any:
                prefix = match.group(1) if match.group(1) else ""
                sensitive_value = match.group(2)
                suffix = match.group(3) if match.group(3) else ""
                masked_value = self._mask_value(sensitive_value)
                return f"{prefix}{masked_value}{suffix}"

            masked_text = pattern.sub(mask_replacement, masked_text)
        return masked_text

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to mask sensitive data.

        Format the message *before* masking. Mutating ``api_key=%s`` first
        treats ``%s`` as the secret, then leaves ``record.args`` intact so
        logging raises and the error handler prints the raw key (#252
        FMP-SEC-005).
        """
        try:
            formatted = record.getMessage()
        except Exception:
            formatted = str(record.msg)
        record.msg = self._mask_patterns_in_string(formatted)
        record.args = ()

        for key, value in list(record.__dict__.items()):
            if key.startswith("_"):
                continue
            lowered = key.lower()
            if lowered in self.sensitive_keys or any(
                token in lowered for token in ("api_key", "apikey", "redis_url")
            ):
                if isinstance(value, str | int | float):
                    record.__dict__[key] = self._mask_value(str(value))
                elif isinstance(value, dict | list):
                    record.__dict__[key] = self._mask_dict_recursive(deepcopy(value))
            elif key in {"exc_text", "stack_info"} and isinstance(value, str):
                record.__dict__[key] = self._mask_patterns_in_string(value)

        return True

    def _mask_dict_recursive(self, d: Any, parent_key: str = "") -> Any:
        """Recursively mask sensitive values in dictionaries and lists"""
        if isinstance(d, dict):
            result: dict[str, Any] = {}
            for k, v in d.items():
                key = k.lower() if isinstance(k, str) else k
                is_sensitive = any(
                    sensitive in str(key).lower() for sensitive in self.sensitive_keys
                )

                if is_sensitive and isinstance(v, str | int | float):
                    result[k] = self._mask_value(str(v))
                elif isinstance(v, dict):
                    result[k] = self._mask_dict_recursive(v, f"{parent_key}.{k}")
                elif isinstance(v, list):
                    result[k] = self._mask_dict_recursive(v, parent_key)
                else:
                    result[k] = v
            return result
        elif isinstance(d, list):
            return [self._mask_dict_recursive(item, parent_key) for item in d]
        return d


class JsonFormatter(logging.Formatter):
    """JSON formatter for log records"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Get the module name from the logger name, not pathname
        module_name = record.name.split(".")[-1] if "." in record.name else record.name

        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": module_name,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            exc_type = record.exc_info[0]
            exc_value = record.exc_info[1]
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type else "Unknown",
                "message": str(exc_value) if exc_value else "",
                "traceback": self.formatException(record.exc_info),
            }

        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "message",
            } and not key.startswith("_"):
                log_data[key] = value

        redactor = SensitiveDataFilter()
        if "exception" in log_data:
            log_data["exception"]["message"] = redactor._mask_patterns_in_string(
                log_data["exception"]["message"]
            )
            log_data["exception"]["traceback"] = redactor._mask_patterns_in_string(
                log_data["exception"]["traceback"]
            )
        for extra_key, extra_value in list(log_data.items()):
            if extra_key in {
                "timestamp",
                "level",
                "message",
                "module",
                "line",
                "exception",
            }:
                continue
            if isinstance(extra_value, str):
                log_data[extra_key] = redactor._mask_patterns_in_string(extra_value)
            elif isinstance(extra_value, dict | list):
                log_data[extra_key] = redactor._mask_dict_recursive(
                    deepcopy(extra_value)
                )

        return json.dumps(log_data, default=str)


class SecureRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler with secure permissions"""

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ) -> None:
        # Initialize _permissions_set before calling parent constructor
        # because parent constructor may call _open() which uses this attribute
        self._permissions_set = False
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        if not delay:
            self._set_secure_permissions()

    def _open(self) -> Any:
        """Override to set permissions when file is opened"""
        stream = super()._open()
        if not self._permissions_set:
            self._set_secure_permissions()
        return stream

    def _set_secure_permissions(self) -> None:
        """Set secure permissions on log file"""
        if self._permissions_set:
            return

        if os.name != "nt":  # Not Windows
            try:
                os.chmod(self.baseFilename, 0o600)
                self._permissions_set = True
            except OSError as e:
                FMPLogger().get_logger(__name__).warning(
                    f"Could not set secure permissions on log file: {e}"
                )


class FMPLogger:
    """Singleton logger for FMP Data package"""

    _instance: ClassVar[Optional["FMPLogger"]] = None
    _handler_classes: ClassVar[dict[str, type[logging.Handler]]] = {
        "StreamHandler": logging.StreamHandler,
        "FileHandler": logging.FileHandler,
        "RotatingFileHandler": SecureRotatingFileHandler,
        "JsonRotatingFileHandler": SecureRotatingFileHandler,
    }

    def __new__(cls) -> "FMPLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Check if already initialized
        if getattr(self, "_initialized", False):
            return

        self._initialized: bool = True
        self._configured: bool = False  # Track if configure() has been called
        self._logger = logging.getLogger("fmp_data")
        self._logger.setLevel(logging.INFO)
        self._handlers: dict[str, logging.Handler] = {}

        # Add sensitive data filter
        self._ensure_redaction_filter(self._logger)

        # Add default console handler if no handlers exist
        if not self._logger.handlers:
            self._add_default_console_handler()

    @staticmethod
    def _ensure_redaction_filter(
        target: logging.Logger | logging.Handler,
    ) -> None:
        """Attach ``SensitiveDataFilter`` once. Child loggers skip ancestor
        filters; handler filters run on every emit (#252 FMP-SEC-005).
        """
        if any(
            isinstance(existing, SensitiveDataFilter) for existing in target.filters
        ):
            return
        target.addFilter(SensitiveDataFilter())

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Return a child of the package logger.

        ``get_logger(__name__)`` must land on ``fmp_data.base``, not
        ``fmp_data.fmp_data.base``. The root is already
        ``logging.getLogger("fmp_data")``; ``getChild("fmp_data.base")``
        would prefix an already-qualified module name (#238).

        Handlers stay on the root logger. Each child also gets a
        ``SensitiveDataFilter`` because ancestor logger filters are not
        applied to descendant records.

        Args:
            name: Optional logger name. A fully-qualified ``fmp_data.*``
                name (or ``"fmp_data"`` itself) is used as-is. Any other
                name is added as a child of ``fmp_data``.

        Returns:
            logging.Logger: Logger instance
        """
        if not name or name == "fmp_data":
            return self._logger
        prefix = "fmp_data."
        if name.startswith(prefix):
            child = self._logger.getChild(name[len(prefix) :])
        else:
            child = self._logger.getChild(name)
        self._ensure_redaction_filter(child)
        return child

    def _add_default_console_handler(self) -> None:
        """Add default console handler with a reasonable format"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self._ensure_redaction_filter(handler)
        self._logger.addHandler(handler)
        self._handlers["console"] = handler

    def configure(self, config: LoggingConfig, *, _force: bool = False) -> None:
        """Configure logger with the given configuration.

        Note: This method only applies configuration on the first call.
        Subsequent calls are ignored to prevent multiple clients from
        overwriting each other's logging configuration.

        Args:
            config: The logging configuration to apply.
            _force: Internal flag for testing purposes. If True, forces
                reconfiguration even if already configured. Do not use
                in production code.
        """
        if self._configured and not _force:
            return  # Skip reconfiguration; first client's config wins

        self._configured = True
        self._logger.setLevel(getattr(logging, config.level))

        # Remove existing handlers
        for handler in list(self._handlers.values()):
            self._logger.removeHandler(handler)
            handler.close()
        self._handlers.clear()

        # Create log directory if specified
        if config.log_path:
            config.log_path.mkdir(parents=True, exist_ok=True)
            if os.name != "nt":  # Not Windows
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

        # Prepend log_path only if filename is not already absolute
        if "filename" in kwargs and log_path:
            filename = Path(kwargs["filename"])
            if not filename.is_absolute():
                kwargs["filename"] = log_path / kwargs["filename"]

        # Create handler
        if config.class_name == "StreamHandler":
            handler = handler_class()
        else:
            handler = handler_class(**kwargs)

        # Set formatter
        if config.class_name == "JsonRotatingFileHandler":
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(logging.Formatter(config.format))

        handler.setLevel(getattr(logging, config.level))
        self._ensure_redaction_filter(handler)
        self._logger.addHandler(handler)
        self._handlers[name] = handler


def log_api_call(
    logger: logging.Logger | None = None,
    exclude_args: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to log API calls with sensitive data filtering

    Args:
        logger: Optional logger instance
        exclude_args: Whether to exclude arguments from logging

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal logger
            if logger is None:
                logger = FMPLogger().get_logger()

            # Get module information
            current_frame = inspect.currentframe()
            if current_frame and current_frame.f_back:
                back_frame = current_frame.f_back
                module = inspect.getmodule(back_frame)
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
                        "call_args": args[1:],  # Skip 'self' argument
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
                    f"API error in {module_name}.{func.__name__}: {e!s}",
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
