"""
Configuration module for FMP Data API client.

This module provides configuration classes for the FMP Data API client,
including logging, rate limiting, and client settings.

File: fmp_data/config.py
"""

from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse, urlsplit, urlunsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_serializer,
    field_validator,
)

from fmp_data._redaction import redact_mapping
from fmp_data.cache.config import CacheConfig
from fmp_data.exceptions import ConfigError


def _reveal(value: SecretStr | str | None) -> str | None:
    """Unwrap a possibly-``SecretStr`` credential for use at the wire.

    Credential fields are ``SecretStr`` so ``model_dump`` and
    ``model_dump_json`` cannot emit them (#252); every point that actually
    *uses* the value goes through here.
    """
    if value is None:
        return None
    return value.get_secret_value() if isinstance(value, SecretStr) else value


def _is_loopback_host(hostname: str | None) -> bool:
    """True for localhost / loopback literals used by local test servers."""
    if not hostname:
        return False
    host = hostname.strip("[]").lower()
    return host in {"localhost", "127.0.0.1", "::1"} or host.startswith("127.")


def _mask_secret(value: SecretStr | str) -> str:
    revealed = _reveal(value) or ""
    if len(revealed) > 4:
        return f"{revealed[:4]}***"
    return "***"


def _redact_url_userinfo(url: SecretStr | str) -> str:
    """Drop userinfo from a URL so ``redis://:hunter2@host`` cannot leak."""
    revealed = _reveal(url) or ""
    parts = urlsplit(revealed)
    if not (parts.username or parts.password):
        return revealed
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    netloc = f"***@{host}" if (parts.username or parts.password) else host
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def _safe_int_from_env(env_var: str, default: int, *, min_val: int = 0) -> int:
    """Safely convert environment variable to int, falling back to default."""
    try:
        value = int(os.getenv(env_var, str(default)))
        return value if value >= min_val else default
    except (ValueError, TypeError):
        return default


class LogHandlerConfig(BaseModel):
    """Configuration for a single log handler"""

    level: str = Field(default="INFO", description="Logging level for this handler")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    class_name: str = Field(
        description="Handler class name (FileHandler, StreamHandler, etc.)"
    )
    handler_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional arguments for handler initialization",
    )

    @field_serializer("handler_kwargs")
    def _serialize_handler_kwargs(self, value: dict[str, Any]) -> dict[str, Any]:
        """Redact on the dump path too, not only in ``__str__`` (#252).

        ``dict[str, Any]`` is out of reach for ``SecretStr``, and these kwargs
        go straight to a logging handler -- a ``SysLogHandler`` password or an
        HTTP handler's credentials live here. ``__str__`` was fixed to sweep
        them, but ``model_dump()`` / ``model_dump_json()`` still emitted them,
        so anything serializing a config leaked.

        Safe here for the same reason as ``EmbeddingConfig``: the only
        consumer reads the attribute (``config.handler_kwargs.copy()`` in
        ``logger.py``), so nothing rebuilds this model from its own dump.
        """
        return redact_mapping(value)

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate and normalize logging level"""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        v_upper = v.upper()
        if v_upper not in valid_levels:
            valid_levels_str = ", ".join(valid_levels)
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: {valid_levels_str}"
            )
        return v_upper

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v: str) -> str:
        """Validate class name is not empty"""
        if not v or not v.strip():
            raise ValueError("Handler class name cannot be empty")
        return v.strip()


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = Field(default="INFO", description="Root logging level")
    handlers: dict[str, LogHandlerConfig] = Field(
        default_factory=lambda: {
            "console": LogHandlerConfig(
                class_name="StreamHandler",
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        },
        description="Logging handlers configuration",
    )
    log_path: Path | None = Field(default=None, description="Base path for log files")

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook to create log directory if needed"""
        if self.log_path and isinstance(self.log_path, Path):
            try:
                self.log_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise ValueError(f"Could not create log directory: {e}") from e

    @classmethod
    def from_env(cls) -> LoggingConfig:
        """Create logging config from environment variables"""
        handlers = {}
        log_path = None

        # Console handler (enabled by default unless explicitly disabled)
        console_enabled = os.getenv("FMP_LOG_CONSOLE", "true").lower() == "true"
        if console_enabled:
            handlers["console"] = LogHandlerConfig(
                class_name="StreamHandler",
                level=os.getenv("FMP_LOG_CONSOLE_LEVEL", "INFO"),
                format=os.getenv(
                    "FMP_LOG_CONSOLE_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                ),
            )

        # File handler (enabled if log path is provided)
        log_path_env = os.getenv("FMP_LOG_PATH")
        if log_path_env:
            log_path = Path(log_path_env)
            handlers["file"] = LogHandlerConfig(
                class_name="RotatingFileHandler",
                level=os.getenv("FMP_LOG_FILE_LEVEL", "INFO"),
                format=os.getenv(
                    "FMP_LOG_FILE_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                ),
                handler_kwargs={
                    "filename": str(log_path / "fmp.log"),
                    "maxBytes": int(os.getenv("FMP_LOG_MAX_BYTES", "10485760")),
                    "backupCount": int(os.getenv("FMP_LOG_BACKUP_COUNT", "5")),
                },
            )

        # JSON handler (enabled if explicitly requested and log path exists)
        json_enabled = os.getenv("FMP_LOG_JSON", "false").lower() == "true"
        if json_enabled and log_path:
            handlers["json"] = LogHandlerConfig(
                class_name="JsonRotatingFileHandler",
                level=os.getenv("FMP_LOG_JSON_LEVEL", "INFO"),
                format=os.getenv("FMP_LOG_JSON_FORMAT", "json"),
                handler_kwargs={
                    "filename": str(log_path / "fmp.json"),
                    "maxBytes": int(os.getenv("FMP_LOG_MAX_BYTES", "10485760")),
                    "backupCount": int(os.getenv("FMP_LOG_BACKUP_COUNT", "5")),
                },
            )

        return cls(
            level=os.getenv("FMP_LOG_LEVEL", "INFO"),
            handlers=handlers,
            log_path=log_path,
        )


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""

    daily_limit: int = Field(default=250, gt=0, description="Maximum daily API calls")
    requests_per_second: int = Field(
        default=5,
        gt=0,
        description="Maximum requests per second",
    )
    requests_per_minute: int = Field(
        default=300, gt=0, description="Maximum requests per minute"
    )

    @classmethod
    def from_env(cls) -> RateLimitConfig:
        """Create rate limit config from environment variables"""
        return cls(
            daily_limit=_safe_int_from_env("FMP_DAILY_LIMIT", 250, min_val=1),
            requests_per_second=_safe_int_from_env(
                "FMP_REQUESTS_PER_SECOND", 5, min_val=1
            ),
            requests_per_minute=_safe_int_from_env(
                "FMP_REQUESTS_PER_MINUTE", 300, min_val=1
            ),
        )


class ClientConfig(BaseModel):
    """Base client configuration for FMP Data API.

    Adding a credential field, here or on a subclass: type it ``SecretStr``
    and mark it ``repr=False``. ``SecretStr`` keeps it out of ``model_dump``
    and ``model_dump_json``; ``repr=False`` keeps it out of ``__str__`` and
    ``__repr__``. Neither is a name allowlist, so nothing here needs editing
    to make a new field safe -- read the value back with
    ``.get_secret_value()`` (#252).
    """

    # Configure model
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    api_key: SecretStr = Field(
        description=(
            "FMP API key. Can be set via FMP_API_KEY environment variable. "
            "Read the value with `config.api_key.get_secret_value()`."
        ),
        repr=False,  # Exclude API key from repr
    )
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(
        default=3, ge=0, description="Maximum number of request retries"
    )
    max_rate_limit_retries: int = Field(
        default=3, ge=0, description="Maximum number of rate limit retries"
    )
    base_url: str = Field(
        default="https://financialmodelingprep.com", description="Base API URL"
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limit configuration",
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration",
    )
    metrics_callback: Callable[..., None] | None = Field(
        default=None,
        description=(
            "Optional callback(endpoint_name, latency_ms, success, "
            "status_code, retry_count)"
        ),
        exclude=True,  # Don't include in serialization
    )
    validation_mode: Literal["lenient", "warn", "strict"] = Field(
        default="warn",
        description=(
            "Response validation policy for JSON and bulk CSV extras. "
            "'lenient' ignores unknown fields, "
            "'warn' logs unknown fields once per endpoint+field set, "
            "'strict' raises on unknown fields."
        ),
    )
    unknown_param_policy: Literal["ignore", "warn", "error"] = Field(
        default="warn",
        description=(
            "Unknown request parameter handling policy. "
            "'ignore' drops unknown keys, "
            "'warn' logs dropped keys, "
            "'error' raises validation errors."
        ),
    )
    cache: CacheConfig | None = Field(
        default=None,
        description=(
            "Optional response cache configuration. "
            "Set to enable caching of API responses."
        ),
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate API key is not empty.

        Unwraps first: ``model_config``'s ``str_strip_whitespace`` does not
        reach inside a ``SecretStr``, and ``SecretStr`` has no ``.strip()``,
        so the stripping this validator has always done has to be explicit
        now (#252).
        """
        revealed = (_reveal(v) or "").strip()
        if not revealed:
            raise ValueError("API key cannot be empty")
        if set(revealed) == {"*"}:
            # A value of nothing but asterisks is a redaction marker that has
            # been round-tripped back in as if it were real -- e.g. rebuilding
            # a config from `model_dump(mode="json")`. Accepting it produces a
            # client that 401s on every call with no local error, so fail here
            # where the cause is still visible (#252).
            raise ValueError(
                "API key looks like a redaction mask, not a key. It was "
                "probably read back from a masked dump; use "
                "`config.api_key.get_secret_value()` to obtain the real value."
            )
        return SecretStr(revealed)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format.

        HTTPS is required except for loopback HTTP (local mocks). A
        non-loopback ``http://`` origin would send ``apikey`` in the clear
        (#252 FMP-SEC-004).
        """
        if not v or not v.strip():
            raise ValueError("Base URL cannot be empty")

        v = v.strip()
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {v}")
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"URL scheme must be http or https: {v}")
            if parsed.scheme == "http" and not _is_loopback_host(parsed.hostname):
                raise ValueError(
                    f"base_url must use https except for loopback HTTP: {v}"
                )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Invalid URL: {v}") from e

        return v

    def __str__(self) -> str:
        """String representation with credentials masked.

        Redaction is driven by field metadata and key shape, not by a list of
        field names. The previous version dumped the whole model and masked
        three names it knew about, so anything else rendered verbatim: a
        subclass field, or a secret inside ``LogHandlerConfig.handler_kwargs``
        -- a bare ``dict[str, Any]`` that needs no subclass to reach (#252).

        Three passes, narrowest signal first:

        1. ``repr=False`` fields. That is pydantic's own "not for display"
           marker and every credential field already carries it, so a subclass
           gets correct behaviour from the standard idiom rather than from
           being added to a list here.
        2. A recursive sweep for secret-shaped *keys*, which is the only
           handle available on untyped ``dict[str, Any]`` bags.
        3. The two values worth rendering richer than ``***``.

        The richer masks are computed from the *fields*, not from the dump:
        credential fields are ``SecretStr``, so the dump already holds
        ``SecretStr('**********')`` and re-masking that would print a mask of
        a mask -- losing the leading-4-character affordance that makes this
        string useful for telling two keys apart.
        """
        data = self.model_dump()

        for name, field in type(self).model_fields.items():
            if field.repr is False and data.get(name) is not None:
                data[name] = "***"

        data = redact_mapping(data)

        if getattr(self, "api_key", None):
            data["api_key"] = _mask_secret(self.api_key)
        embedding_api_key = getattr(self, "embedding_api_key", None)
        if embedding_api_key:
            data["embedding_api_key"] = _mask_secret(embedding_api_key)
        cache = data.get("cache")
        if isinstance(cache, dict) and self.cache and self.cache.redis_url:
            cache["redis_url"] = _redact_url_userinfo(self.cache.redis_url)

        # Create a string representation from the masked data
        fields = []
        for key, value in data.items():
            if key == "api_key":
                fields.append(f"api_key='{value}'")
            elif isinstance(value, str):
                fields.append(f"{key}='{value}'")
            else:
                fields.append(f"{key}={value}")

        return " ".join(fields)

    def __repr__(self) -> str:
        """Representation with masked API key"""
        return f"{self.__class__.__name__}({self.__str__()})"

    @classmethod
    def from_env(cls) -> ClientConfig:
        """Create configuration from environment variables"""
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            raise ConfigError(
                "API key must be provided either "
                "explicitly or via FMP_API_KEY environment variable"
            )

        validation_mode = os.getenv("FMP_VALIDATION_MODE", "warn").lower()
        if validation_mode not in {"lenient", "warn", "strict"}:
            raise ConfigError(
                f"FMP_VALIDATION_MODE='{validation_mode}' is invalid. "
                "Allowed values: lenient, warn, strict"
            )
        unknown_param_policy = os.getenv("FMP_UNKNOWN_PARAM_POLICY", "warn").lower()
        if unknown_param_policy not in {"ignore", "warn", "error"}:
            raise ConfigError(
                f"FMP_UNKNOWN_PARAM_POLICY='{unknown_param_policy}' "
                "is invalid. "
                "Allowed values: ignore, warn, error"
            )

        config_dict: dict[str, Any] = {
            "api_key": api_key,
            "timeout": _safe_int_from_env("FMP_TIMEOUT", 30, min_val=1),
            "max_retries": _safe_int_from_env("FMP_MAX_RETRIES", 3),
            "base_url": os.getenv("FMP_BASE_URL", "https://financialmodelingprep.com"),
            "rate_limit": RateLimitConfig.from_env(),
            "logging": LoggingConfig.from_env(),
            "validation_mode": validation_mode,
            "unknown_param_policy": unknown_param_policy,
        }

        cache_config = CacheConfig.from_env()
        if cache_config is not None:
            config_dict["cache"] = cache_config

        return cls(**config_dict)
