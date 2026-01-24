from collections.abc import Generator
from datetime import datetime
import importlib
import os

import pytest

pytest.importorskip("langchain_core", reason="langchain extra not installed")
pytest.importorskip("langchain_community", reason="langchain extra not installed")
pytest.importorskip("langchain_openai", reason="langchain extra not installed")
pytest.importorskip("faiss", reason="faiss extra not installed")

from fmp_data import FMPDataClient
from fmp_data.lc import EndpointVectorStore, LangChainConfig, create_vector_store


@pytest.fixture(scope="session")
def openai_api_key() -> str:
    """Get OpenAI API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return api_key


@pytest.fixture(scope="session")
def langchain_config(fmp_client: FMPDataClient, openai_api_key: str) -> LangChainConfig:
    """Create LangChain config for testing"""
    return LangChainConfig(
        api_key=fmp_client.config.api_key,
        embedding_api_key=openai_api_key,  # Pass as plain string
        base_url=fmp_client.config.base_url,
    )


@pytest.fixture(scope="session")
def vector_store(
    fmp_client: FMPDataClient,
    openai_api_key: str,
    tmp_path_factory,
) -> Generator[EndpointVectorStore, None, None]:
    """Create temporary vector store for testing"""
    # Use temporary directory for test cache
    cache_dir = tmp_path_factory.mktemp("vector_store_cache")

    # Create store
    store = create_vector_store(
        fmp_api_key=fmp_client.config.api_key,
        openai_api_key=openai_api_key,
        cache_dir=str(cache_dir),
        store_name="test_store",
        force_create=True,
    )

    if not store:
        pytest.fail("Failed to create vector store")

    yield store

    # Cleanup
    try:
        import shutil

        shutil.rmtree(str(cache_dir))
    except Exception as e:
        print(f"Failed to cleanup test cache: {e}")


class TestLangChainIntegration:
    """Test LangChain integration functionality"""

    def test_vector_store_creation(
        self,
        fmp_client: FMPDataClient,
        openai_api_key: str,
        tmp_path,
    ):
        """Test vector store creation and basic functionality"""
        store = create_vector_store(
            fmp_api_key=fmp_client.config.api_key,
            openai_api_key=openai_api_key,
            cache_dir=str(tmp_path),
            store_name="test_store",
            force_create=True,
        )

        # Basic checks
        assert store is not None
        assert isinstance(store, EndpointVectorStore)
        assert store.metadata.embedding_provider == "OpenAIEmbeddings"
        assert store.metadata.dimension > 0
        assert isinstance(store.metadata.created_at, datetime)

        # Verify it has some endpoints
        assert len(store.registry.list_endpoints()) > 0

    def test_error_handling(self, vector_store: EndpointVectorStore):
        """Test error handling scenarios"""
        # Test invalid k value
        with pytest.raises(ValueError):
            vector_store.search("test query", k=0)

        # Test invalid threshold
        with pytest.raises(ValueError):
            vector_store.search("test query", threshold=2.0)

        # Empty query should still return relevant results
        empty_results = vector_store.search("", k=3)
        assert len(empty_results) > 0
        # Verify results are valid
        for result in empty_results:
            assert result.score >= 0 and result.score <= 1
            assert result.name
            assert result.info

    def test_semantic_search(self, vector_store: EndpointVectorStore):
        """Test semantic search functionality"""
        queries = [
            "Get current stock price",
            "Find historical stock data",
            "Show market data",
        ]

        for query in queries:
            results = vector_store.search(query, k=2)
            assert len(results) > 0
            for result in results:
                assert result.score >= 0 and result.score <= 1
                assert result.name
                assert result.info

    def test_tool_generation(self, vector_store: EndpointVectorStore):
        """Test LangChain tool generation"""
        queries = ["Get stock quote", "Get market data"]
        providers = ["openai", "anthropic", None]

        for query in queries:
            for provider in providers:
                tools = vector_store.get_tools(query, k=2, provider=provider)
                assert len(tools) > 0

                if provider == "openai":
                    assert all(isinstance(tool, dict) for tool in tools)
                    assert all(
                        "name" in tool and "description" in tool for tool in tools
                    )
                elif provider == "anthropic":
                    assert all(isinstance(tool, dict) for tool in tools)
                    assert all("parameters" in tool for tool in tools)
                else:
                    StructuredTool = importlib.import_module(
                        "langchain_core.tools"
                    ).StructuredTool

                    assert all(isinstance(tool, StructuredTool) for tool in tools)

    def test_endpoint_validation(self, vector_store: EndpointVectorStore):
        """Test endpoint validation and registration"""
        endpoints = vector_store.registry.list_endpoints()
        assert len(endpoints) > 0

        for name, info in endpoints.items():
            assert info.endpoint is not None
            assert info.semantics is not None
            assert info.semantics.method_name == name
            assert info.semantics.category is not None
            assert info.semantics.natural_description is not None
