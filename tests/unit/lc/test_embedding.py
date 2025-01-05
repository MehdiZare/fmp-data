# tests/lc/test_embedding.py
from unittest.mock import patch

import pytest

from fmp_data.exceptions import ConfigError
from fmp_data.lc.embedding import EmbeddingConfig, EmbeddingProvider


@pytest.fixture
def mock_openai():
    with patch("langchain_openai.OpenAIEmbeddings") as mock:
        yield mock


@pytest.fixture
def mock_huggingface():
    with patch("langchain.embeddings.HuggingFaceEmbeddings") as mock:
        yield mock


def test_embedding_config_validation():
    """Test embedding configuration validation"""
    # Test valid OpenAI config
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        api_key="test-key",
        model_name="text-embedding-ada-002",
    )
    assert config.provider == EmbeddingProvider.OPENAI
    assert config.api_key == "test-key"

    # Test valid HuggingFace config without API key
    config = EmbeddingConfig(
        provider=EmbeddingProvider.HUGGINGFACE,
        model_name="sentence-transformers/all-mpnet-base-v2",
    )
    assert config.provider == EmbeddingProvider.HUGGINGFACE


def test_get_embeddings_openai(mock_openai):
    """Test getting OpenAI embeddings"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        api_key="test-key",
        model_name="text-embedding-ada-002",
    )

    config.get_embeddings()
    mock_openai.assert_called_once_with(
        openai_api_key="test-key", model="text-embedding-ada-002"
    )


def test_get_embeddings_error_handling():
    """Test embedding error handling"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        model_name="text-embedding-ada-002",
        # Missing API key
    )

    with pytest.raises(ConfigError):
        config.get_embeddings()
