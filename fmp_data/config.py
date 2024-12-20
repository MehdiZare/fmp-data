# config.py
import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fmp_data.exceptions import ConfigError
from fmp_data.lc.utils import check_dependency, check_langchain_dependency


class EmbeddingProvider(str, Enum):
    """Supported embedding providers"""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"


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


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings"""

    provider: EmbeddingProvider = Field(
        default=EmbeddingProvider.OPENAI, description="Provider for embeddings"
    )
    model_name: str | None = Field(
        default=None, description="Model name for the embedding provider"
    )
    api_key: str | None = Field(
        default=None, description="API key for the embedding provider"
    )
    additional_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments for the embedding provider",
    )

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        """Post initialization validation"""
        check_langchain_dependency()

    def get_embeddings(self):
        """
        Get the configured embedding model

        Returns:
            An instance of the configured embedding model

        Raises:
            ConfigError: If required dependencies are not
            installed or configuration is invalid
        """
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                # Check OpenAI dependencies
                check_dependency("openai", "OpenAI")
                check_dependency("tiktoken", "OpenAI")

                if not self.api_key:
                    raise ConfigError(
                        "OpenAI API key is required for OpenAI embeddings. "
                        "Please provide it in the configuration."
                    )

                from langchain_openai import OpenAIEmbeddings

                return OpenAIEmbeddings(
                    openai_api_key=self.api_key,
                    model=self.model_name or "text-embedding-ada-002",
                    **self.additional_kwargs,
                )

            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                # Check HuggingFace dependencies
                check_dependency("sentence_transformers", "HuggingFace")
                check_dependency("torch", "HuggingFace")

                from langchain.embeddings import HuggingFaceEmbeddings

                return HuggingFaceEmbeddings(
                    model_name=self.model_name
                    or "sentence-transformers/all-mpnet-base-v2",
                    **self.additional_kwargs,
                )

            elif self.provider == EmbeddingProvider.COHERE:
                # Check Cohere dependencies
                check_dependency("cohere", "Cohere")

                if not self.api_key:
                    raise ConfigError(
                        "Cohere API key is required for Cohere embeddings. "
                        "Please provide it in the configuration."
                    )

                from langchain.embeddings import CohereEmbeddings

                return CohereEmbeddings(
                    cohere_api_key=self.api_key,
                    model=self.model_name or "embed-english-v2.0",
                    **self.additional_kwargs,
                )
            else:
                raise ConfigError(f"Unsupported embedding provider: {self.provider}")

        except ImportError as e:
            raise ConfigError(
                f"Error importing required packages for {self.provider}: {str(e)}"
            ) from e
        except Exception as e:
            error_message = f"Error initializing {self.provider} embeddings: {str(e)}"
            raise ConfigError(error_message) from e

    @classmethod
    def from_env(cls) -> "EmbeddingConfig | None":
        """Create embedding configuration from environment variables if configured"""
        provider_str = os.getenv("FMP_EMBEDDING_PROVIDER")

        # Return None if no embedding configuration is found
        if not provider_str:
            return None

        try:
            config_dict = {
                "provider": EmbeddingProvider(provider_str.lower()),
                "model_name": os.getenv("FMP_EMBEDDING_MODEL"),
                "additional_kwargs": json.loads(
                    os.getenv("FMP_EMBEDDING_KWARGS", "{}")
                ),
            }

            # Get API key based on provider
            if config_dict["provider"] == EmbeddingProvider.OPENAI:
                config_dict["api_key"] = os.getenv("OPENAI_API_KEY")
            elif config_dict["provider"] == EmbeddingProvider.COHERE:
                config_dict["api_key"] = os.getenv("COHERE_API_KEY")

            return cls(**config_dict)

        except (ValueError, json.JSONDecodeError) as e:
            raise ConfigError(
                f"Error creating embedding config from environment: {str(e)}"
            ) from e


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
    embedding: EmbeddingConfig | None = Field(
        default=None,
        description="Optional embedding configuration",
    )

    model_config = ConfigDict(protected_namespaces=(), arbitrary_types_allowed=True)

    @classmethod
    @field_validator("embedding")
    def validate_embedding(cls, v: Any) -> EmbeddingConfig | None:
        if v is None:
            return None
        if isinstance(v, EmbeddingConfig):
            return v
        if isinstance(v, dict):
            return EmbeddingConfig(**v)
        raise ValueError("Invalid embedding configuration")

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
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            raise ConfigError(
                "API key must be provided either "
                "explicitly or via FMP_API_KEY environment variable"
            )

        config_dict = {
            "api_key": api_key,
            "timeout": int(os.getenv("FMP_TIMEOUT", "30")),
            "max_retries": int(os.getenv("FMP_MAX_RETRIES", "3")),
            "base_url": os.getenv(
                "FMP_BASE_URL", "https://financialmodelingprep.com/api"
            ),
            "rate_limit": RateLimitConfig.from_env(),
            "logging": LoggingConfig.from_env(),
            "embedding": EmbeddingConfig.from_env(),
        }

        return cls(**config_dict)
