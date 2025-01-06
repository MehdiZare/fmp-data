# tests/lc/test_vector_store.py
from unittest.mock import Mock, patch

import pytest
from langchain_core.embeddings import Embeddings

from fmp_data.lc.models import EndpointInfo
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.vector_store import EndpointVectorStore


@pytest.fixture
def mock_embeddings():
    class MockEmbeddings(Embeddings):
        def embed_query(self, text: str) -> list[float]:
            return [0.1] * 768

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1] * 768 for _ in texts]

    return MockEmbeddings()


@pytest.fixture
def vector_store(mock_client, mock_registry, mock_embeddings, tmp_path):
    store = EndpointVectorStore(
        client=mock_client,
        registry=mock_registry,
        embeddings=mock_embeddings,
        cache_dir=str(tmp_path),
    )
    # Make sure registry returns data
    mock_registry.list_endpoints.return_value = {
        "test_endpoint": Mock(spec=EndpointInfo)
    }
    mock_registry.get_endpoint.return_value = Mock(spec=EndpointInfo)
    mock_registry.get_embedding_text.return_value = "Test embedding text"
    return store


@pytest.fixture
def mock_faiss_store():
    """Mock FAISS store"""
    with patch("langchain_community.vectorstores.faiss.FAISS") as mock_faiss:
        mock_instance = Mock()
        mock_instance.add_texts.return_value = None
        mock_instance.similarity_search_with_score.return_value = [
            (Mock(page_content="test", metadata={"endpoint": "test"}), 0.5)
        ]
        mock_faiss.return_value = mock_instance
        yield mock_faiss


@pytest.fixture
def mock_client():
    return Mock(spec="BaseClient")


@pytest.fixture
def mock_registry():
    """Mock registry with proper info returns"""
    registry = Mock(spec=EndpointRegistry)
    registry.get_endpoint.return_value = Mock()
    registry.get_embedding_text.return_value = "Test embedding text"
    return registry


def test_vector_store_initialization(vector_store):
    """Test vector store initialization"""
    assert vector_store.client is not None
    assert vector_store.registry is not None
    assert vector_store.embeddings is not None


def test_add_endpoint(vector_store, mock_registry):
    """Test adding single endpoint"""
    vector_store.add_endpoint("test_endpoint")
    mock_registry.get_endpoint.assert_called_with("test_endpoint")
    mock_registry.get_embedding_text.assert_called_with("test_endpoint")


def test_search(vector_store):
    """Test searching endpoints"""
    results = vector_store.search("test query")
    assert isinstance(results, list)
    if results:
        assert hasattr(results[0], "score")
        assert hasattr(results[0], "name")


def test_save_load(vector_store, tmp_path):
    """Test saving and loading store"""
    # Add test data
    vector_store.add_endpoint("test_endpoint")
    # Save
    vector_store.save()
    # Verify files exist
    assert (tmp_path / "vector_stores/default/faiss_store").exists()
    assert (tmp_path / "vector_stores/default/metadata.json").exists()
