# tests/lc/test_vector_store.py
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.embeddings import Embeddings  # type: ignore[import-not-found]
import pytest

from fmp_data.company.mapping import COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS
from fmp_data.exceptions import ConfigError
from fmp_data.lc.models import EndpointInfo
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS


@pytest.fixture
def mock_embeddings():
    class MockEmbeddings(Embeddings):
        def embed_query(self, text: str) -> list[float]:
            return [0.1] * 768

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1] * 768 for _ in texts]

    return MockEmbeddings()


@pytest.fixture
def fake_embeddings():
    class FakeEmbeddings(Embeddings):
        def _vector_for(self, text: str) -> list[float]:
            text = text.lower()
            if "profile" in text:
                return [1.0, 0.0, 0.0]
            if "gainers" in text:
                return [0.0, 1.0, 0.0]
            return [0.0, 0.0, 1.0]

        def embed_query(self, text: str) -> list[float]:
            return self._vector_for(text)

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [self._vector_for(text) for text in texts]

    return FakeEmbeddings()


@pytest.fixture
def registry_with_endpoints():
    registry = EndpointRegistry()

    profile_sem = COMPANY_ENDPOINTS_SEMANTICS["profile"]
    gainers_sem = MARKET_ENDPOINTS_SEMANTICS["gainers"]

    endpoints = {
        profile_sem.method_name: (
            COMPANY_ENDPOINT_MAP[profile_sem.method_name],
            profile_sem,
        ),
        gainers_sem.method_name: (
            MARKET_ENDPOINT_MAP[gainers_sem.method_name],
            gainers_sem,
        ),
    }

    registry.register_batch(endpoints)
    return registry


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
        # Verify result has required attributes
        assert results[0].score is not None
        assert results[0].name is not None


def test_save_load(vector_store, tmp_path):
    """Test saving and loading store"""
    # Add test data
    vector_store.add_endpoint("test_endpoint")
    # Save
    vector_store.save()
    # Verify files exist
    assert (tmp_path / "vector_stores/default/faiss_store").exists()
    assert (tmp_path / "vector_stores/default/metadata.json").exists()


def test_search_and_get_tools_with_faiss(
    registry_with_endpoints, fake_embeddings, tmp_path
):
    client = SimpleNamespace(request=Mock())
    store = EndpointVectorStore(
        client=client,
        registry=registry_with_endpoints,
        embeddings=fake_embeddings,
        cache_dir=str(tmp_path),
        store_name="lc-test",
    )

    store.add_endpoints(list(registry_with_endpoints.list_endpoints().keys()))

    results = store.search("company profile", k=2, threshold=0.8)
    assert results
    assert results[0].name == "get_profile"

    tools = store.get_tools(query="company profile", k=1, threshold=0.8)
    assert tools
    assert tools[0].name == "get_profile"
    assert "symbol" in tools[0].args_schema.model_fields

    anthropic_tools = store.get_tools(
        query="company profile", k=1, threshold=0.8, provider="anthropic"
    )
    assert anthropic_tools[0]["name"] == "get_profile"


def test_load_requires_allow_dangerous_deserialization(
    registry_with_endpoints, fake_embeddings, tmp_path
):
    client = SimpleNamespace(request=Mock())
    store = EndpointVectorStore(
        client=client,
        registry=registry_with_endpoints,
        embeddings=fake_embeddings,
        cache_dir=str(tmp_path),
        store_name="lc-cache",
    )
    store.add_endpoints(list(registry_with_endpoints.list_endpoints().keys()))
    store.save()

    with pytest.raises(ConfigError, match="allow_dangerous_deserialization=False"):
        EndpointVectorStore(
            client=client,
            registry=registry_with_endpoints,
            embeddings=fake_embeddings,
            cache_dir=str(tmp_path),
            store_name="lc-cache",
        )

    loaded = EndpointVectorStore(
        client=client,
        registry=registry_with_endpoints,
        embeddings=fake_embeddings,
        cache_dir=str(tmp_path),
        store_name="lc-cache",
        allow_dangerous_deserialization=True,
    )
    assert loaded.metadata.num_vectors > 0
