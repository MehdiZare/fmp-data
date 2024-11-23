# config.py
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

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
    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional arguments for handler initialization",
    )

    @classmethod
    @field_validator("level")
    def validate_level(cls, v: str) -> str:
        """Validate logging level"""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = Field(default="INFO", description="Root logger level")
    handlers: dict[str, LogHandlerConfig] = Field(
        default_factory=lambda: {
            "console": LogHandlerConfig(
                class_name="StreamHandler",
                level="INFO",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        },
        description="Log handlers configuration",
    )
    log_path: Path | None = Field(default=None, description="Base path for log files")

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create logging config from environment variables"""
        handlers = {}

        # Console handler
        if os.getenv("FMP_LOG_CONSOLE", "true").lower() == "true":
            handlers["console"] = LogHandlerConfig(
                class_name="StreamHandler",
                level=os.getenv("FMP_LOG_CONSOLE_LEVEL", "INFO"),
            )

        # Process log path
        log_path_str = os.getenv("FMP_LOG_PATH")
        log_path = Path(log_path_str) if log_path_str else None

        if log_path:
            # File handler
            handlers["file"] = LogHandlerConfig(
                class_name="RotatingFileHandler",
                level=os.getenv("FMP_LOG_FILE_LEVEL", "INFO"),
                kwargs={
                    "filename": str(log_path / "fmp.log"),
                    "maxBytes": int(
                        os.getenv("FMP_LOG_MAX_BYTES", str(10 * 1024 * 1024))
                    ),
                    "backupCount": int(os.getenv("FMP_LOG_BACKUP_COUNT", "5")),
                },
            )

            # JSON handler
            if os.getenv("FMP_LOG_JSON", "false").lower() == "true":
                handlers["json"] = LogHandlerConfig(
                    class_name="JsonRotatingFileHandler",
                    level=os.getenv("FMP_LOG_JSON_LEVEL", "INFO"),
                    kwargs={
                        "filename": str(log_path / "fmp.json"),
                        "maxBytes": int(
                            os.getenv("FMP_LOG_MAX_BYTES", str(10 * 1024 * 1024))
                        ),
                        "backupCount": int(os.getenv("FMP_LOG_BACKUP_COUNT", "5")),
                    },
                )

        return cls(
            level=os.getenv("FMP_LOG_LEVEL", "INFO"),
            handlers=handlers,
            log_path=log_path,
        )

    def model_post_init(self, __context) -> None:
        """Post-initialization validation and setup"""
        if self.log_path:
            try:
                self.log_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise ValueError(f"Could not create log directory: {e}") from e


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""

    daily_limit: int = Field(default=250, gt=0, description="Maximum daily API calls")
    requests_per_second: int = Field(
        default=5,  # Default value aligned with test expectation
        gt=0,
        description="Maximum requests per second",
    )
    requests_per_minute: int = Field(
        default=300, gt=0, description="Maximum requests per minute"
    )

    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        """Create rate limit config from environment variables"""
        return cls(
            daily_limit=int(os.getenv("FMP_DAILY_LIMIT", "250")),
            requests_per_second=int(
                os.getenv("FMP_REQUESTS_PER_SECOND", "5")
            ),  # Default aligned with Field default
            requests_per_minute=int(os.getenv("FMP_REQUESTS_PER_MINUTE", "300")),
        )


class ClientConfig(BaseModel):
    """Client configuration using Pydantic v2"""

    api_key: str = Field(
        description="FMP API key. Can be set via FMP_API_KEY environment variable"
    )
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(
        default=3, ge=0, description="Maximum number of request retries"
    )
    max_rate_limit_retries: int = Field(
        default=3, ge=0, description="Maximum number of rate limit retries"
    )
    base_url: str = Field(
        default="https://financialmodelingprep.com/api",
        pattern=r"^https?://.*",
        description="FMP API base URL",
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig, description="Rate limit configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )

    @classmethod
    @field_validator("api_key", mode="before")
    def validate_api_key(cls, v: str | None) -> str:
        """Validate and populate API key from env if not provided"""
        if v:
            return v

        env_key = os.getenv("FMP_API_KEY")
        if env_key:
            return env_key

        raise ConfigError(
            "API key must be provided either "
            "explicitly or via FMP_API_KEY environment variable"
        )

    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables"""
        # Ensure API key is validated
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            raise ConfigError(
                "API key must be provided either "
                "explicitly or via FMP_API_KEY environment variable"
            )

        return cls(
            api_key=api_key,
            timeout=int(os.getenv("FMP_TIMEOUT", "30")),
            max_retries=int(os.getenv("FMP_MAX_RETRIES", "3")),
            base_url=os.getenv("FMP_BASE_URL", "https://financialmodelingprep.com/api"),
            rate_limit=RateLimitConfig.from_env(),
            logging=LoggingConfig.from_env(),
        )
