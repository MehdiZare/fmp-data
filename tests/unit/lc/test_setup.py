# tests/lc/test_setup.py
from unittest.mock import Mock, patch

import numpy as np
import pytest
from langchain_core.embeddings import Embeddings

from fmp_data.base import BaseClient
from fmp_data.lc.models import EndpointInfo
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.setup import VectorStoreSetup, setup_vector_store


@pytest.fixture
def mock_client():
    """Mock FMP client"""
    return Mock(spec=BaseClient)


@pytest.fixture
def mock_registry():
    """Mock endpoint registry with required data"""
    registry = Mock(spec=EndpointRegistry)
    mock_endpoint_info = Mock(spec=EndpointInfo)
    registry.list_endpoints.return_value = {"test_endpoint": mock_endpoint_info}
    registry.get_endpoint.return_value = mock_endpoint_info
    registry.get_embedding_text.return_value = "Test embedding text"
    return registry


@pytest.fixture
def mock_embeddings():
    class MockEmbeddings(Embeddings):
        def embed_query(self, text: str) -> list[float]:
            return [0.1] * 768

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1] * 768 for _ in texts]

    return MockEmbeddings()


@pytest.fixture
def mock_faiss():
    """Mock FAISS"""
    with patch("faiss.IndexFlatL2") as mock_index:
        mock_instance = Mock()
        mock_instance.xb = np.zeros((0, 768))
        mock_index.return_value = mock_instance
        yield mock_index


def test_store_validation(mock_client, mock_registry, mock_embeddings, tmp_path):
    """Test vector store validation"""
    setup = VectorStoreSetup(
        client=mock_client,
        registry=mock_registry,
        embeddings=mock_embeddings,
        cache_dir=str(tmp_path),
    )

    # Test non-existent store
    assert setup.store_exists() is False

    # Test invalid store
    assert setup.validate_store() is False


def test_setup_vector_store(mock_client, mock_registry, mock_embeddings, tmp_path):
    """Test vector store setup function"""
    store = setup_vector_store(
        client=mock_client,
        registry=mock_registry,
        embeddings=mock_embeddings,
        cache_dir=str(tmp_path),
    )

    assert store is not None
