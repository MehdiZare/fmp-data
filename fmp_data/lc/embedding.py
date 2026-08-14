# fmp_data/lc/embedding.py
from enum import Enum
import json
import os
from typing import Any

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from fmp_data.exceptions import ConfigError
from fmp_data.lc.utils import check_package_dependency

_SECRET_KWARG_TOKENS = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "authorization",
    "auth",
)


def _is_secret_key(key: str) -> bool:
    """True when a kwargs key name looks like it holds a credential."""
    parts = key.lower().replace("-", "_").split("_")
    return any(part in _SECRET_KWARG_TOKENS for part in parts)


def _redact_value(value: Any, depth: int = 0) -> Any:
    """Redact secret-shaped entries inside nested containers.

    Recursion matters: providers take credential-bearing *nested* kwargs --
    ``OpenAIEmbeddings`` accepts ``default_headers={"Authorization": ...}``
    and ``model_kwargs={"api_key": ...}``, and both are splatted straight
    into the provider below. A top-level-only scan copied those dicts by
    reference, so ``repr`` printed the secret verbatim (#273).

    ``depth`` bounds pathological nesting; deeper values are elided rather
    than walked.
    """
    if depth >= 6:
        return "..."
    if isinstance(value, dict):
        return {
            key: ("***" if _is_secret_key(str(key)) else _redact_value(item, depth + 1))
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return type(value)(_redact_value(item, depth + 1) for item in value)
    if isinstance(value, set):
        return {_redact_value(item, depth + 1) for item in value}
    return value


def _redact_kwargs(data: dict[str, Any]) -> dict[str, Any]:
    """Copy a kwargs map with secret-shaped values replaced, recursively."""
    return {
        key: ("***" if _is_secret_key(key) else _redact_value(value))
        for key, value in data.items()
    }


class EmbeddingProvider(str, Enum):
    """Supported embedding providers"""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings"""

    provider: EmbeddingProvider = Field(
        default=EmbeddingProvider.OPENAI, description="Provider for embeddings"
    )
    model_name: str | None = Field(
        default=None, description="Model name for the embedding provider"
    )
    api_key: SecretStr | None = Field(
        default=None,
        description=(
            "API key for the embedding provider. Read the value with "
            "`config.api_key.get_secret_value()`."
        ),
        repr=False,
    )
    additional_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments for the embedding provider",
        repr=False,
    )

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        """Hide API keys and secret-shaped kwargs from ``repr`` (#273)."""
        return (
            f"{type(self).__name__}("
            f"provider={self.provider!r}, "
            f"model_name={self.model_name!r}, "
            f"additional_kwargs={_redact_kwargs(self.additional_kwargs)!r})"
        )

    def get_embeddings(self) -> Embeddings:
        """
        Get the configured embedding model

        Returns:
            An instance of the configured embedding model

        Raises:
            ConfigError: If required dependencies are
            not installed or configuration is invalid
        """
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                # Check OpenAI dependencies
                check_package_dependency("openai", "OpenAI")
                check_package_dependency("tiktoken", "OpenAI")

                if not self.api_key:
                    raise ConfigError(
                        "OpenAI API key is required for OpenAI embeddings. "
                        "Please provide it in the configuration."
                    )

                from langchain_openai import OpenAIEmbeddings

                return OpenAIEmbeddings(
                    # Providers take a plain string; a SecretStr would be
                    # stringified to its mask and authenticate as nobody (#252).
                    openai_api_key=self.api_key.get_secret_value(),
                    model=self.model_name or "text-embedding-ada-002",
                    **self.additional_kwargs,
                )

            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                check_package_dependency("sentence_transformers", "HuggingFace")
                check_package_dependency("torch", "HuggingFace")

                from langchain_community.embeddings import HuggingFaceEmbeddings

                return HuggingFaceEmbeddings(
                    model_name=self.model_name
                    or "sentence-transformers/all-mpnet-base-v2",
                    **self.additional_kwargs,
                )

            elif self.provider == EmbeddingProvider.COHERE:
                check_package_dependency("cohere", "Cohere")

                if not self.api_key:
                    raise ConfigError(
                        "Cohere API key is required for Cohere embeddings. "
                        "Please provide it in the configuration."
                    )

                from langchain_community.embeddings import CohereEmbeddings

                return CohereEmbeddings(
                    cohere_api_key=self.api_key.get_secret_value(),
                    model=self.model_name or "embed-english-v2.0",
                    **self.additional_kwargs,
                )
            else:
                raise ConfigError(f"Unsupported embedding provider: {self.provider}")

        except ImportError as e:
            raise ConfigError(
                f"Error importing required packages for {self.provider}: {e!s}"
            ) from e
        except Exception as e:
            error_message = f"Error initializing {self.provider} embeddings: {e!s}"
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
                f"Error creating embedding config from environment: {e!s}"
            ) from e
