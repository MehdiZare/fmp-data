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
import traceback
from typing import Any, ClassVar, Optional, ParamSpec, TypeVar

from fmp_data.config import LoggingConfig, LogHandlerConfig

P = ParamSpec("P")
R = TypeVar("R")

# Attributes the stdlib puts on every LogRecord. Everything else in
# ``record.__dict__`` came from a caller's ``extra=``, and is therefore fair
# game for redaction. Rewriting the stdlib ones would corrupt formatting --
# ``exc_info`` in particular is a tuple that formatters unpack.
_STANDARD_LOGRECORD_ATTRS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "getMessage",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
)


def _stringify(value: Any) -> str:
    """Render a value for masking, including ``bytes``.

    ``str(b"secret")`` yields ``b'secret'`` -- the credential survives with
    decoration, which is worse than useless when the point is to mask it.
    """
    if isinstance(value, bytes | bytearray):
        return value.decode("utf-8", errors="replace")
    return str(value)


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

            def mask_replacement(match: re.Match[str]) -> str:
                # Group count varies by pattern. The quoted-value patterns
                # capture a trailing quote as group 3, but `authorization`
                # is (prefix)(token) with no delimiter to restore, so
                # reading group 3 unconditionally raised
                # `IndexError: no such group` -- which meant the Bearer rule
                # never redacted *and* the exception escaped through
                # `logger.error(..., exc_info=True)` to replace the caller's
                # own error (#252).
                prefix = match.group(1) or ""
                sensitive_value = match.group(2)
                suffix = (match.group(3) or "") if match.re.groups >= 3 else ""
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
            if key.startswith("_") or key in _STANDARD_LOGRECORD_ATTRS:
                if key in {"exc_text", "stack_info"} and isinstance(value, str):
                    record.__dict__[key] = self._mask_patterns_in_string(value)
                continue

            if self._is_sensitive_key(key):
                record.__dict__[key] = self._mask_value(_stringify(value))
            else:
                # Redact *every* extra, not only the sensitively-named ones.
                # A secret nested under a benign key (`extra={"payload":
                # {"api_key": ...}}`) used to be masked inside
                # ``JsonFormatter.format`` instead of on the record, so any
                # second handler -- ``logging.basicConfig()``, a Sentry or
                # OTel exporter -- emitted the raw value (#252 FMP-SEC-005).
                # Doing it here means every handler inherits the masking.
                record.__dict__[key] = self._mask_dict_recursive(deepcopy(value))

        self._redact_traceback(record)
        return True

    def _is_sensitive_key(self, key: str) -> bool:
        lowered = key.lower()
        return lowered in self.sensitive_keys or any(
            token in lowered for token in ("api_key", "apikey", "redis_url")
        )

    def _redact_traceback(self, record: logging.LogRecord) -> None:
        """Render and mask the traceback before any formatter can emit it.

        Filters run *before* formatting, so ``record.exc_text`` is still
        ``None`` here and the ``exc_text`` branch above never fires on a live
        ``exc_info=True`` call -- the traceback reached the handler
        unredacted, carrying whatever credential the raised exception's
        message held (#252 FMP-SEC-005 called for exception text and
        tracebacks, not just extras).

        ``logging.Formatter.format`` reuses a non-empty ``record.exc_text``
        instead of re-deriving it, so populating it with a masked rendering
        is enough for the stdlib path.
        """
        if not record.exc_info or not record.exc_info[0] or record.exc_text:
            return
        rendered = "".join(traceback.format_exception(*record.exc_info))
        record.exc_text = self._mask_patterns_in_string(rendered.rstrip("\n"))

    def _mask_dict_recursive(self, d: Any, parent_key: str = "", depth: int = 0) -> Any:
        """Recursively mask sensitive values inside any container.

        Type-complete on purpose. The previous version gated on
        ``isinstance(v, str | int | float)`` to mask and ``dict | list`` to
        recurse, so three shapes walked straight through unredacted (#252
        FMP-SEC-005):

        * a sensitive key holding ``bytes``, a ``tuple`` or a ``set``;
        * ``log_api_call``'s ``call_args``, which is a *tuple* of positional
          arguments -- the API key is routinely the first one;
        * any secret reachable only through a tuple or set.
        """
        if depth >= 6:
            return d
        if isinstance(d, dict):
            return {
                k: (
                    self._mask_value(_stringify(v))
                    if isinstance(k, str) and self._is_sensitive_key(k)
                    else self._mask_dict_recursive(v, f"{parent_key}.{k}", depth + 1)
                )
                for k, v in d.items()
            }
        if isinstance(d, list | tuple):
            return type(d)(
                self._mask_dict_recursive(i, parent_key, depth + 1) for i in d
            )
        if isinstance(d, set):
            return {self._mask_dict_recursive(i, parent_key, depth + 1) for i in d}
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
            # Mask here too: this formatter renders the exception from
            # ``record.exc_info`` directly rather than reading the masked
            # ``record.exc_text``, so it would otherwise re-derive the raw
            # traceback the filter just sanitized (#252 FMP-SEC-005).
            masker = SensitiveDataFilter()
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type else "Unknown",
                "message": masker._mask_patterns_in_string(
                    str(exc_value) if exc_value else ""
                ),
                "traceback": masker._mask_patterns_in_string(
                    record.exc_text or self.formatException(record.exc_info)
                ),
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
                        # Types, not values. Positional arguments have no
                        # names, so nothing downstream can tell a credential
                        # from a ticker symbol -- the filter masks by key name
                        # and there is no key here, so a secret passed
                        # positionally was logged verbatim (#252 FMP-SEC-005).
                        # The data worth reading arrives through `call_kwargs`,
                        # which is named and therefore maskable. Skip 'self'.
                        "call_args": [type(a).__name__ for a in args[1:]],
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
