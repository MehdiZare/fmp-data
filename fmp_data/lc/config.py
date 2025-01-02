# fmp_data/lc/config.py
import os

from pydantic import ConfigDict, Field

from fmp_data.config import ClientConfig
from fmp_data.lc.embedding import EmbeddingConfig, EmbeddingProvider


class LangChainConfig(ClientConfig):
    """
    Extended client configuration with LangChain support.

    Inherits all base FMP client configuration and adds
    LangChain-specific settings for embeddings and vector search.
    """

    # Embedding configuration
    embedding_provider: EmbeddingProvider = Field(
        default=EmbeddingProvider.OPENAI,
        description="Provider for embeddings (OpenAI, HuggingFace, Cohere)",
    )
    embedding_model: str | None = Field(
        default=None, description="Model name for embeddings"
    )
    embedding_api_key: str | None = Field(
        default=None, description="API key for embedding provider"
    )

    # Vector store settings
    vector_store_path: str | None = Field(
        default=None, description="Path to store vector embeddings"
    )
    similarity_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for endpoint matching",
    )
    max_tools: int = Field(
        default=5, gt=0, description="Maximum number of tools to return in searches"
    )

    @property
    def embedding_config(self) -> EmbeddingConfig | None:
        """Get embedding configuration if provider is configured."""
        if not self.embedding_provider:
            return None

        return EmbeddingConfig(
            provider=self.embedding_provider,
            model_name=self.embedding_model,
            api_key=self.embedding_api_key,
        )

    @classmethod
    def from_env(cls) -> "LangChainConfig":
        """Create LangChain config from environment variables."""
        # Get base config first
        base_config = super().from_env()
        config_dict = base_config.model_dump()

        # Add LangChain specific settings
        config_dict.update(
            {
                "embedding_provider": os.getenv("FMP_EMBEDDING_PROVIDER", "openai"),
                "embedding_model": os.getenv("FMP_EMBEDDING_MODEL"),
                "embedding_api_key": os.getenv("OPENAI_API_KEY"),  # Default to OpenAI
                "vector_store_path": os.getenv("FMP_VECTOR_STORE_PATH"),
                "similarity_threshold": float(
                    os.getenv("FMP_SIMILARITY_THRESHOLD", "0.3")
                ),
                "max_tools": int(os.getenv("FMP_MAX_TOOLS", "5")),
            }
        )

        # Handle provider-specific API keys
        if config_dict["embedding_provider"] == EmbeddingProvider.COHERE:
            config_dict["embedding_api_key"] = os.getenv("COHERE_API_KEY")
        elif config_dict["embedding_provider"] == EmbeddingProvider.HUGGINGFACE:
            config_dict["embedding_api_key"] = os.getenv("HF_API_KEY")

        return cls(**config_dict)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
