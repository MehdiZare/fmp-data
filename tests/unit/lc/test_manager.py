# tests/lc/test_manager.py
from unittest.mock import Mock, patch

import numpy as np
import pytest
from langchain_core.embeddings import Embeddings

from fmp_data.lc.embedding import EmbeddingProvider
from fmp_data.lc.manager import FMPToolManager
from fmp_data.lc.models import EndpointInfo
from fmp_data.lc.utils import DependencyError


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings that properly implement the interface"""

    class MockEmbeddings(Embeddings):
        def __init__(self):
            self.model_name = "mock-embeddings-model"

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            """Embed a list of documents"""
            return [[0.1] * 1536 for _ in texts]

        def embed_query(self, text: str) -> list[float]:
            """Embed a single text"""
            return [0.1] * 1536

    return MockEmbeddings()


@pytest.fixture
def mock_manager_deps(mock_embeddings):
    """Mock all manager dependencies with proper embeddings"""
    with (
        patch("fmp_data.lc.manager.is_langchain_available", return_value=True),
        patch("langchain_openai.OpenAIEmbeddings", return_value=mock_embeddings),
    ):
        mock_registry = Mock()
        mock_endpoint_info = Mock(spec=EndpointInfo)
        mock_registry.list_endpoints.return_value = {
            "test_endpoint": mock_endpoint_info
        }
        mock_registry.get_endpoint.return_value = mock_endpoint_info
        mock_registry.get_embedding_text.return_value = "Test embedding text"

        yield {"embeddings": mock_embeddings, "registry": mock_registry}


@pytest.fixture
def mock_langchain_available():
    """Mock langchain availability check"""
    with patch("fmp_data.lc.manager.is_langchain_available") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    with patch("fmp_data.lc.manager.EndpointVectorStore") as mock:
        yield mock


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings properly"""
    with patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings:
        mock_instance = Mock()
        # Return proper numpy arrays
        mock_instance.embed_query.return_value = np.array([0.1] * 768, dtype=np.float32)
        mock_instance.embed_documents.return_value = [
            np.array([0.1] * 768, dtype=np.float32)
        ]
        mock_embeddings.return_value = mock_instance
        yield mock_embeddings


@pytest.fixture
def mock_openai():
    """Mock OpenAI with working embeddings"""
    with patch("openai.OpenAI") as mock:
        mock.return_value.embeddings.create.return_value = {
            "data": [{"embedding": [0.1] * 768}]
        }
        yield mock


@pytest.fixture
def manager_kwargs():
    """Manager init kwargs with proper embeddings provider"""
    return {
        "fmp_api_key": "test-key",
        "openai_api_key": "test-openai-key",
        "auto_initialize": False,
        "embedding_provider": EmbeddingProvider.OPENAI,
    }


@pytest.fixture
def mock_registry():
    """Create mock registry with endpoints"""
    registry = Mock()
    registry.list_endpoints = Mock(
        return_value={"test_endpoint": Mock(spec=EndpointInfo)}
    )
    registry.get_endpoint = Mock(return_value=Mock(spec=EndpointInfo))
    registry.get_embedding_text = Mock(return_value="Test embedding text")
    return registry


@pytest.fixture
def mock_endpoint_info():
    """Create a properly configured mock EndpointInfo"""
    from fmp_data.lc.models import EndpointSemantics, SemanticCategory
    from fmp_data.models import Endpoint, EndpointParam, ParamLocation, ParamType

    # Create mock endpoint
    endpoint = Mock(spec=Endpoint)
    endpoint.name = "test_endpoint"
    endpoint.path = "/test/{symbol}"
    endpoint.description = "Test endpoint"
    endpoint.mandatory_params = [
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Test param",
        )
    ]
    endpoint.optional_params = []
    endpoint.response_model = dict

    # Create mock semantics with all required attributes
    semantics = Mock(spec=EndpointSemantics)
    semantics.client_name = "test_client"
    semantics.method_name = "test_method"
    semantics.natural_description = "Test description"
    semantics.category = SemanticCategory.MARKET_DATA
    semantics.sub_category = "test_subcategory"  # Add this attribute
    semantics.example_queries = ["test query"]
    semantics.parameter_hints = {}
    semantics.response_hints = {}
    semantics.related_terms = []
    semantics.use_cases = ["test use case"]

    # Create EndpointInfo with proper mock components
    mock_info = Mock(spec=EndpointInfo)
    type(mock_info).endpoint = Mock(return_value=endpoint)
    type(mock_info).semantics = Mock(return_value=semantics)

    # Configure property access
    mock_info.endpoint = endpoint
    mock_info.semantics = semantics

    return mock_info


def test_tool_manager_initialization(manager_kwargs, mock_openai):
    """Test manager initialization with mocked OpenAI"""
    with (
        patch("fmp_data.lc.manager.is_langchain_available", return_value=True),
        patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings,
    ):
        # Configure mock embeddings
        mock_instance = Mock()
        mock_instance.embed_query.return_value = np.array([0.1] * 768)
        mock_instance.embed_documents.return_value = [np.array([0.1] * 768)]
        mock_embeddings.return_value = mock_instance

        manager = FMPToolManager(**manager_kwargs)
        assert manager.client is not None
        assert manager.registry is not None


def test_tool_manager_langchain_dependency():
    """Test langchain dependency check"""
    with patch("fmp_data.lc.manager.is_langchain_available", return_value=False):
        with pytest.raises(DependencyError):
            FMPToolManager(fmp_api_key="test-key")


def test_initialize_vector_store(manager_kwargs, mock_embeddings):
    """Test vector store initialization"""
    with (
        patch("fmp_data.lc.manager.is_langchain_available", return_value=True),
        patch("langchain_openai.OpenAIEmbeddings", return_value=mock_embeddings),
        patch("fmp_data.lc.manager.EndpointRegistry") as mock_registry,
    ):
        # Set up mock registry
        registry_instance = mock_registry.return_value
        mock_endpoint_info = Mock(spec=EndpointInfo)
        registry_instance.list_endpoints.return_value = {
            "test_endpoint": mock_endpoint_info
        }
        registry_instance.get_endpoint.return_value = mock_endpoint_info
        registry_instance.get_embedding_text.return_value = "Test embedding text"

        manager = FMPToolManager(**manager_kwargs)
        manager.initialize_vector_store()
        assert manager.vector_store is not None


def test_get_tools(manager_kwargs, mock_embeddings, mock_endpoint_info):
    """Test getting tools"""
    with (
        patch("fmp_data.lc.manager.is_langchain_available", return_value=True),
        patch("langchain_openai.OpenAIEmbeddings", return_value=mock_embeddings),
        patch("fmp_data.lc.manager.EndpointRegistry") as mock_registry,
    ):
        # Set up mock registry with proper EndpointInfo
        registry_instance = mock_registry.return_value
        registry_instance.list_endpoints.return_value = {
            "test_endpoint": mock_endpoint_info
        }
        registry_instance.get_endpoint.return_value = mock_endpoint_info
        registry_instance.get_embedding_text.return_value = "Test embedding text"

        manager = FMPToolManager(**manager_kwargs)
        manager.initialize_vector_store()
        tools = manager.get_tools("test query")
        assert isinstance(tools, list)
        assert len(tools) > 0


def test_search_endpoints(manager_kwargs, mock_embeddings, mock_endpoint_info):
    """Test searching endpoints"""
    with (
        patch("fmp_data.lc.manager.is_langchain_available", return_value=True),
        patch("langchain_openai.OpenAIEmbeddings", return_value=mock_embeddings),
        patch("fmp_data.lc.manager.EndpointRegistry") as mock_registry,
    ):
        # Set up mock registry with proper EndpointInfo
        registry_instance = mock_registry.return_value
        registry_instance.list_endpoints.return_value = {
            "test_endpoint": mock_endpoint_info
        }
        registry_instance.get_endpoint.return_value = mock_endpoint_info
        registry_instance.get_embedding_text.return_value = "Test embedding text"

        manager = FMPToolManager(**manager_kwargs)
        manager.initialize_vector_store()
        results = manager.search_endpoints("test query")
        assert isinstance(results, list)
        assert len(results) > 0

        # Verify result structure
        result = results[0]
        assert "score" in result
        assert "name" in result
        assert "description" in result
        assert "category" in result
        assert "sub_category" in result
        assert isinstance(
            result["sub_category"], str
        )  # Verify sub_category is a string
