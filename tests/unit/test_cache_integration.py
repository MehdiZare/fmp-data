"""Integration tests for caching with BaseClient."""

from __future__ import annotations

from enum import Enum
from unittest.mock import MagicMock

import pytest

from fmp_data.base import BaseClient
from fmp_data.cache.config import CacheConfig
from fmp_data.cache.memory import MemoryCache
from fmp_data.config import ClientConfig
from fmp_data.models import Endpoint


class _Method(str, Enum):
    GET = "GET"


def _make_endpoint(name: str = "test_ep") -> Endpoint:
    """Create a minimal Endpoint for testing cache integration."""
    from pydantic import BaseModel, Field
    from pydantic.alias_generators import to_camel

    class _FakeModel(BaseModel):
        model_config = {"alias_generator": to_camel, "extra": "allow"}
        symbol: str = Field(description="symbol")
        price: float = Field(description="price")

    ep = MagicMock(spec=Endpoint)
    ep.name = name
    ep.method = _Method.GET
    ep.response_model = _FakeModel
    ep.validate_params.side_effect = lambda kw, **_: kw
    ep.build_url.return_value = "https://example.com/api/v3/test"
    ep.get_query_params.side_effect = lambda params: dict(params)
    ep.allow_empty_on_404 = False
    return ep


class TestBaseClientCacheIntegration:
    """Test that BaseClient integrates with cache backends correctly."""

    @pytest.fixture
    def cache_config(self):
        return CacheConfig(enabled=True, backend="memory", default_ttl=300)

    @pytest.fixture
    def client_config(self, cache_config):
        return ClientConfig(
            api_key="test-key-12345",
            cache=cache_config,
        )

    def test_cache_initialized_when_config_present(self, client_config):
        base = BaseClient(config=client_config)
        assert base._cache is not None
        assert isinstance(base._cache, MemoryCache)
        base.close()

    def test_no_cache_when_config_absent(self):
        config = ClientConfig(api_key="test-key-12345")
        base = BaseClient(config=config)
        assert base._cache is None
        base.close()

    def test_no_cache_when_disabled(self):
        config = ClientConfig(
            api_key="test-key-12345",
            cache=CacheConfig(enabled=False),
        )
        base = BaseClient(config=config)
        assert base._cache is None
        base.close()

    def test_build_cache_key_deterministic(self):
        params1 = {"symbol": "AAPL", "apikey": "secret", "limit": "10"}
        params2 = {"limit": "10", "symbol": "AAPL", "apikey": "different"}
        key1 = BaseClient._build_cache_key("get_quote", params1)
        key2 = BaseClient._build_cache_key("get_quote", params2)
        assert key1 == key2  # apikey excluded, params sorted

    def test_build_cache_key_different_params(self):
        key1 = BaseClient._build_cache_key("get_quote", {"symbol": "AAPL"})
        key2 = BaseClient._build_cache_key("get_quote", {"symbol": "GOOG"})
        assert key1 != key2

    def test_build_cache_key_different_endpoints(self):
        key1 = BaseClient._build_cache_key("get_quote", {"symbol": "AAPL"})
        key2 = BaseClient._build_cache_key("get_profile", {"symbol": "AAPL"})
        assert key1 != key2

    def test_cache_ttl_override(self, client_config):
        config_with_overrides = client_config.model_copy(
            update={
                "cache": CacheConfig(
                    enabled=True,
                    default_ttl=300,
                    ttl_overrides={"quote": 60},
                )
            }
        )
        base = BaseClient(config=config_with_overrides)
        assert base._get_cache_ttl("quote") == 60
        assert base._get_cache_ttl("profile") == 300
        base.close()

    def test_client_config_from_env_without_cache(self, monkeypatch):
        """Test that ClientConfig.from_env works without cache env vars."""
        monkeypatch.setenv("FMP_API_KEY", "test-key-12345")
        monkeypatch.delenv("FMP_CACHE_ENABLED", raising=False)
        config = ClientConfig.from_env()
        assert config.cache is None

    def test_client_config_from_env_with_cache(self, monkeypatch):
        """Test that ClientConfig.from_env picks up cache env vars."""
        monkeypatch.setenv("FMP_API_KEY", "test-key-12345")
        monkeypatch.setenv("FMP_CACHE_ENABLED", "true")
        monkeypatch.setenv("FMP_CACHE_BACKEND", "memory")
        monkeypatch.setenv("FMP_CACHE_TTL", "120")
        config = ClientConfig.from_env()
        assert config.cache is not None
        assert config.cache.enabled is True
        assert config.cache.backend == "memory"
        assert config.cache.default_ttl == 120


class TestCacheHitPath:
    """Test that cache hits skip HTTP and cache misses store results."""

    @pytest.fixture
    def base_client(self):
        config = ClientConfig(
            api_key="test-key-12345",
            cache=CacheConfig(enabled=True, backend="memory", default_ttl=300),
        )
        client = BaseClient(config=config)
        yield client
        client.close()

    def test_cache_miss_stores_result(self, base_client):
        """On a cache miss the HTTP response is stored in cache."""
        ep = _make_endpoint()
        response_payload = [{"symbol": "AAPL", "price": 150.0}]

        # Mock the HTTP client to return a response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_payload
        mock_response.raise_for_status.return_value = None
        base_client.client = MagicMock()
        base_client.client.request.return_value = mock_response

        result = base_client._execute_request(ep, symbol="AAPL")
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

        # Verify the result was stored in cache
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        cached = base_client._cache.get(cache_key)
        assert cached == response_payload

    def test_cache_hit_skips_http(self, base_client):
        """On a cache hit, HTTP client should not be called."""
        ep = _make_endpoint()
        response_payload = [{"symbol": "AAPL", "price": 150.0}]

        # Pre-populate cache with the expected key
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        base_client._cache.set(cache_key, response_payload)

        # Mock the HTTP client — it should NOT be called
        base_client.client = MagicMock()

        result = base_client._execute_request(ep, symbol="AAPL")
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

        # Verify HTTP was never called
        base_client.client.request.assert_not_called()

    def test_cache_hit_returns_isolated_copy(self, base_client):
        """Cache hits should not expose the stored object by reference."""
        ep = _make_endpoint()
        cached_payload = [{"symbol": "AAPL", "price": 150.0}]
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        base_client._cache.set(cache_key, cached_payload)

        result = base_client._execute_request(ep, symbol="AAPL")
        result[0].price = 999.0

        cached_again = base_client._cache.get(cache_key)
        assert cached_again == cached_payload
        assert cached_again[0]["price"] == 150.0

    def test_force_refresh_bypasses_cache(self, base_client):
        """force_refresh=True should skip cache and make HTTP request."""
        ep = _make_endpoint()
        cached_payload = [{"symbol": "AAPL", "price": 100.0}]
        fresh_payload = [{"symbol": "AAPL", "price": 200.0}]

        # Pre-populate cache
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        base_client._cache.set(cache_key, cached_payload)

        # Mock HTTP to return fresh data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fresh_payload
        mock_response.raise_for_status.return_value = None
        base_client.client = MagicMock()
        base_client.client.request.return_value = mock_response

        result = base_client._execute_request(ep, symbol="AAPL", force_refresh=True)
        assert result[0].price == 200.0

        # Verify HTTP was called despite cache having data
        base_client.client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_cache_hit_skips_http(self, base_client):
        """Async cache hit should skip HTTP."""
        from unittest.mock import AsyncMock

        ep = _make_endpoint()
        response_payload = [{"symbol": "AAPL", "price": 150.0}]

        # Pre-populate cache
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        base_client._cache.set(cache_key, response_payload)

        # Mock async client — should NOT be called
        mock_async_client = AsyncMock()
        base_client._async_client = mock_async_client

        result = await base_client._execute_request_async(ep, symbol="AAPL")
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

        mock_async_client.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_cache_miss_stores_result(self, base_client):
        """Async cache miss should store HTTP result in cache."""
        from unittest.mock import AsyncMock, patch

        ep = _make_endpoint()
        response_payload = [{"symbol": "GOOG", "price": 2800.0}]

        # Use MagicMock for response (handle_response calls .json() synchronously)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_payload
        mock_response.raise_for_status.return_value = None
        mock_response.aclose = AsyncMock()

        mock_async_client = AsyncMock()
        mock_async_client.request.return_value = mock_response
        mock_async_client.is_closed = False

        with patch.object(
            base_client, "_setup_async_client", return_value=mock_async_client
        ):
            result = await base_client._execute_request_async(ep, symbol="GOOG")

        assert len(result) == 1
        assert result[0].symbol == "GOOG"

        # Verify result was stored in cache
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "GOOG", "apikey": "test-key-12345"}
        )
        cached = base_client._cache.get(cache_key)
        assert cached == response_payload

    @pytest.mark.asyncio
    async def test_async_cache_hit_returns_isolated_copy(self, base_client):
        """Async cache hits should not expose the stored object by reference."""
        ep = _make_endpoint()
        cached_payload = [{"symbol": "AAPL", "price": 150.0}]
        cache_key = BaseClient._build_cache_key(
            ep.name, {"symbol": "AAPL", "apikey": "test-key-12345"}
        )
        base_client._cache.set(cache_key, cached_payload)

        result = await base_client._execute_request_async(ep, symbol="AAPL")
        result[0].price = 999.0

        cached_again = base_client._cache.get(cache_key)
        assert cached_again == cached_payload
        assert cached_again[0]["price"] == 150.0
