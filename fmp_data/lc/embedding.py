# fmp_data/lc/embedding.py
from enum import Enum
import json
import os
from typing import Any

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict, Field

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


def _redact_kwargs(data: dict[str, Any]) -> dict[str, Any]:
    """Copy a kwargs map with secret-shaped values replaced."""
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        lowered = key.lower()
        if any(token in lowered for token in _SECRET_KWARG_TOKENS):
            redacted[key] = "***"
        else:
            redacted[key] = value
    return redacted


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
    api_key: str | None = Field(
        default=None,
        description="API key for the embedding provider",
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
                    openai_api_key=self.api_key,
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
                    cohere_api_key=self.api_key,
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
