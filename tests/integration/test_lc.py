import os
from collections.abc import Generator
from datetime import datetime

import pytest
from langchain_openai import OpenAIEmbeddings

from fmp_data import FMPDataClient
from fmp_data.lc import EndpointVectorStore, create_vector_store, setup_registry


@pytest.fixture(scope="session")
def openai_api_key() -> str:
    """Get OpenAI API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return api_key


@pytest.fixture(scope="session")
def embeddings(openai_api_key: str) -> OpenAIEmbeddings:
    """Create OpenAI embeddings instance"""
    return OpenAIEmbeddings(
        openai_api_key=openai_api_key, model="text-embedding-3-small"
    )


@pytest.fixture(scope="session")
def vector_store(
    fmp_client: FMPDataClient, embeddings: OpenAIEmbeddings, tmp_path_factory
) -> Generator[EndpointVectorStore, None, None]:
    """Create temporary vector store for testing"""
    # Use temporary directory for test cache
    cache_dir = tmp_path_factory.mktemp("vector_store_cache")

    # Set up registry
    registry = setup_registry(fmp_client)

    # Create vector store
    store = EndpointVectorStore(
        client=fmp_client,
        registry=registry,
        embeddings=embeddings,
        cache_dir=str(cache_dir),
        store_name="test_store",
    )

    # Add test endpoints
    endpoint_names = list(registry.list_endpoints().keys())[
        :5
    ]  # Start with 5 endpoints for testing
    store.add_endpoints(endpoint_names)

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
        self, fmp_client: FMPDataClient, embeddings: OpenAIEmbeddings, tmp_path
    ):
        """Test vector store creation"""
        store = create_vector_store(
            fmp_api_key=fmp_client.config.api_key,
            openai_api_key=embeddings.openai_api_key,
            cache_dir=str(tmp_path),
            store_name="test_store",
            force_create=True,
        )

        assert store is not None
        assert isinstance(store, EndpointVectorStore)
        assert store.validate()

        # Test metadata
        assert store.metadata.embedding_provider == "OpenAIEmbeddings"
        assert store.metadata.dimension > 0
        assert isinstance(store.metadata.created_at, datetime)

    def test_semantic_search(self, vector_store: EndpointVectorStore):
        """Test semantic search functionality"""
        # Test various queries
        queries = [
            "Get real-time stock price",
            "Find historical market data",
            "Get company financials",
        ]

        for query in queries:
            results = vector_store.search(query, k=3)
            assert len(results) > 0
            for result in results:
                assert result.score >= 0 and result.score <= 1
                assert result.name
                assert result.info

    def test_tool_generation(self, vector_store: EndpointVectorStore):
        """Test LangChain tool generation"""
        # Test tool creation for different providers
        queries = [
            "Get stock quote",
            "Find company profile",
        ]

        providers = ["openai", "anthropic", None]

        for query in queries:
            for provider in providers:
                tools = vector_store.get_tools(query, k=2, provider=provider)
                assert len(tools) > 0

                # Check tool format based on provider
                if provider == "openai":
                    assert all(isinstance(tool, dict) for tool in tools)
                    assert all(
                        "name" in tool and "description" in tool for tool in tools
                    )
                elif provider == "anthropic":
                    assert all(isinstance(tool, dict) for tool in tools)
                    assert all("parameters" in tool for tool in tools)
                else:
                    from langchain.tools import StructuredTool

                    assert all(isinstance(tool, StructuredTool) for tool in tools)

    def test_error_handling(self, vector_store: EndpointVectorStore):
        """Test error handling scenarios"""
        # Test invalid k value
        with pytest.raises(ValueError):
            vector_store.search("test query", k=0)

        # Test invalid threshold
        with pytest.raises(ValueError):
            vector_store.search("test query", threshold=2.0)

        # Test empty query
        empty_results = vector_store.search("", k=3)
        assert len(empty_results) == 0

    def test_endpoint_validation(self, vector_store: EndpointVectorStore):
        """Test endpoint validation and registration"""
        # Get all registered endpoints
        endpoints = vector_store.registry.list_endpoints()
        assert len(endpoints) > 0

        # Verify endpoint information
        for name, info in endpoints.items():
            assert info.endpoint is not None
            assert info.semantics is not None
            assert info.semantics.method_name == name
            assert info.semantics.category is not None
            assert info.semantics.natural_description is not None
