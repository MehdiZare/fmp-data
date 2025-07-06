"""
Configuration module for FMP Data API client.

This module provides configuration classes for the FMP Data API client,
including logging, rate limiting, and client settings.

File: fmp_data/config.py
"""

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fmp_data.exceptions import ConfigError


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
    def from_env(cls) -> "LoggingConfig":
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
    def from_env(cls) -> "RateLimitConfig":
        """Create rate limit config from environment variables"""

        def safe_int(env_var: str, default: str) -> int:
            """Safely convert environment variable to int, falling back to default"""
            try:
                return int(os.getenv(env_var, default))
            except (ValueError, TypeError):
                return int(default)

        return cls(
            daily_limit=safe_int("FMP_DAILY_LIMIT", "250"),
            requests_per_second=safe_int("FMP_REQUESTS_PER_SECOND", "5"),
            requests_per_minute=safe_int("FMP_REQUESTS_PER_MINUTE", "300"),
        )


class ClientConfig(BaseModel):
    """Base client configuration for FMP Data API"""

    # Configure model
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    api_key: str = Field(
        description="FMP API key. Can be set via FMP_API_KEY environment variable",
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
        default="https://financialmodelingprep.com/api", description="Base API URL"
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limit configuration",
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty"""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format"""
        if not v or not v.strip():
            raise ValueError("Base URL cannot be empty")

        v = v.strip()
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {v}")
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"URL scheme must be http or https: {v}")
        except Exception as e:
            raise ValueError(f"Invalid URL: {v}") from e

        return v

    def __str__(self) -> str:
        """String representation with masked API key"""
        # Create a copy of the model dict with masked API key
        data = self.model_dump()
        if data.get("api_key"):
            # Mask the API key, showing only first 4 characters
            api_key = data["api_key"]
            if len(api_key) > 4:
                data["api_key"] = f"{api_key[:4]}***"
            else:
                data["api_key"] = "***"

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
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables"""
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            raise ConfigError(
                "API key must be provided either "
                "explicitly or via FMP_API_KEY environment variable"
            )

        def safe_int(env_var: str, default: str) -> int:
            """Safely convert environment variable to int, falling back to default"""
            try:
                return int(os.getenv(env_var, default))
            except (ValueError, TypeError):
                return int(default)

        config_dict = {
            "api_key": api_key,
            "timeout": safe_int("FMP_TIMEOUT", "30"),
            "max_retries": safe_int("FMP_MAX_RETRIES", "3"),
            "base_url": os.getenv(
                "FMP_BASE_URL", "https://financialmodelingprep.com/api"
            ),
            "rate_limit": RateLimitConfig.from_env(),
            "logging": LoggingConfig.from_env(),
        }

        return cls(**config_dict)
