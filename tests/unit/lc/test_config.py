# tests/lc/test_config.py
import os
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from fmp_data.lc.config import EmbeddingProvider, LangChainConfig


@pytest.fixture
def lc_env_vars(tmp_path):
    """Fixture to set up and tear down LangChain environment variables"""
    vector_store_path = str(tmp_path / "vector_store")
    test_vars = {
        "FMP_API_KEY": "test-fmp-key",
        "OPENAI_API_KEY": "test-openai-key",
        "FMP_EMBEDDING_PROVIDER": "openai",
        "FMP_EMBEDDING_MODEL": "text-embedding-ada-002",
        "FMP_VECTOR_STORE_PATH": vector_store_path,
        "FMP_SIMILARITY_THRESHOLD": "0.5",
        "FMP_MAX_TOOLS": "10",
    }

    with patch.dict(os.environ, test_vars, clear=True):
        yield test_vars


def test_langchain_config_validation():
    """Test LangChain configuration validation"""
    # Test valid config
    config = LangChainConfig(
        api_key="test-key",
        embedding_provider=EmbeddingProvider.OPENAI,
        embedding_api_key="test-openai-key",
        similarity_threshold=0.5,
        max_tools=5,
    )
    assert config.api_key == "test-key"
    assert config.embedding_provider == EmbeddingProvider.OPENAI
    assert config.similarity_threshold == 0.5

    # Test invalid similarity threshold
    with pytest.raises(ValidationError):
        LangChainConfig(
            api_key="test-key",
            similarity_threshold=1.5,  # Should be between 0 and 1
        )

    # Test invalid max_tools
    with pytest.raises(ValidationError):
        LangChainConfig(api_key="test-key", max_tools=0)  # Should be greater than 0


def test_langchain_config_from_env(lc_env_vars, tmp_path):
    """Test LangChain configuration from environment variables"""
    config = LangChainConfig.from_env()

    assert config.api_key == "test-fmp-key"
    assert config.embedding_provider == EmbeddingProvider.OPENAI
    assert config.embedding_model == "text-embedding-ada-002"
    assert config.embedding_api_key == "test-openai-key"
    assert config.vector_store_path == str(tmp_path / "vector_store")
    assert config.similarity_threshold == 0.5
    assert config.max_tools == 10
