# tests/unit/lc/conftest.py
"""
LangChain-specific test configuration.

This conftest handles:
- Safe imports for LangChain dependencies
- Automatic test skipping if LangChain not available
- Mock fixtures for LangChain components
- Environment variables for LangChain testing
"""
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from unittest.mock import Mock, patch

import pytest

# Check if LangChain is available before importing anything
try:
    import importlib.util

    langchain_available = importlib.util.find_spec("langchain") is not None
except ImportError:
    langchain_available = False

# Skip all tests in this directory if LangChain not available
if not langchain_available:
    pytest.skip("LangChain dependencies not available", allow_module_level=True)

# Now safely import LangChain modules
try:
    from fmp_data.lc.config import EmbeddingProvider, LangChainConfig
    from fmp_data.lc.utils import (
        DependencyError,
        check_embedding_requirements,
        check_package_dependency,
        is_langchain_available,
    )
except ImportError as e:
    pytest.skip(f"LangChain modules not available: {e}", allow_module_level=True)


@contextmanager
def temp_environ(**kwargs: str) -> Generator[dict[str, str], None, None]:
    """Context manager for temporarily setting environment variables."""
    old_environ = os.environ.copy()
    try:
        os.environ.update(kwargs)
        yield kwargs
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@pytest.fixture
def mock_openai_api_key() -> str:
    """Provide a mock OpenAI API key for testing."""
    return "sk-test_openai_key_12345"


@pytest.fixture
def mock_fmp_api_key() -> str:
    """Provide a mock FMP API key for testing."""
    return "test_fmp_key_12345"


@pytest.fixture
def lc_env_vars(tmp_path: Path, mock_fmp_api_key: str, mock_openai_api_key: str) -> Generator[
    dict[str, str], None, None]:
    """Fixture to set up and tear down LangChain environment variables"""
    vector_store_path = str(tmp_path / "vector_store")
    test_vars = {
        "FMP_API_KEY": mock_fmp_api_key,
        "OPENAI_API_KEY": mock_openai_api_key,
        "FMP_EMBEDDING_PROVIDER": "openai",
        "FMP_EMBEDDING_MODEL": "text-embedding-ada-002",
        "FMP_VECTOR_STORE_PATH": vector_store_path,
        "FMP_SIMILARITY_THRESHOLD": "0.5",
        "FMP_MAX_TOOLS": "10",
    }

    with temp_environ(**test_vars):
        yield test_vars


@pytest.fixture
def mock_langchain_config(mock_fmp_api_key: str, mock_openai_api_key: str) -> LangChainConfig:
    """Provide a mock LangChain configuration."""
    return LangChainConfig(
        api_key=mock_fmp_api_key,
        embedding_provider=EmbeddingProvider.OPENAI,
        embedding_api_key=mock_openai_api_key,
        similarity_threshold=0.7,
        max_tools=15,
    )


@pytest.fixture
def mock_embeddings() -> Mock:
    """Provide a mock embeddings instance."""
    mock = Mock()
    mock.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(5)]
    mock.embed_query.return_value = [0.1, 0.2, 0.3]
    return mock


@pytest.fixture
def mock_vector_store() -> Mock:
    """Provide a mock vector store instance."""
    mock = Mock()
    mock.similarity_search.return_value = []
    mock.similarity_search_with_score.return_value = []
    mock.add_documents.return_value = None
    return mock


@pytest.fixture
def mock_fmp_client() -> Mock:
    """Provide a mock FMP client for LangChain tests."""
    mock = Mock()
    mock.company = Mock()
    mock.market = Mock()
    mock.fundamental = Mock()
    return mock


@pytest.fixture
def temp_vector_store_path(tmp_path: Path) -> Path:
    """Provide a temporary path for vector store testing."""
    path = tmp_path / "test_vector_store"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture
def mock_endpoint_registry() -> Mock:
    """Provide a mock endpoint registry."""
    mock = Mock()
    mock.get_all_endpoints.return_value = {}
    mock.register_endpoint.return_value = None
    mock.get_endpoint.return_value = None
    return mock


# Patches for external dependencies
@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings to avoid external API calls."""
    with patch("langchain_openai.OpenAIEmbeddings") as mock:
        instance = Mock()
        instance.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(5)]
        instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_faiss():
    """Mock FAISS to avoid dependency issues."""
    with patch("faiss.IndexFlatL2") as mock_index, \
            patch("langchain_community.vectorstores.FAISS") as mock_faiss:
        # Mock FAISS index
        index_instance = Mock()
        mock_index.return_value = index_instance

        # Mock FAISS vector store
        faiss_instance = Mock()
        faiss_instance.similarity_search.return_value = []
        faiss_instance.similarity_search_with_score.return_value = []
        mock_faiss.return_value = faiss_instance

        yield mock_faiss


@pytest.fixture(autouse=True)
def ensure_langchain_available():
    """Automatically ensure LangChain is available for all tests in this directory."""
    if not is_langchain_available():
        pytest.skip("LangChain not available for this test")


# Mark all tests in this directory as langchain tests
def pytest_collection_modifyitems(
        config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Auto-mark all tests in lc directory as langchain tests."""
    for item in items:
        # Add langchain marker to all tests in this directory
        if "/lc/" in str(item.fspath):
            item.add_marker(pytest.mark.langchain)

        # Add requirement markers
        if "openai" in item.name.lower() or "embedding" in item.name.lower():
            item.add_marker(pytest.mark.requires_openai_key)