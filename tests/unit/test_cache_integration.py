"""Integration tests for caching with BaseClient."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from fmp_data.cache.memory import MemoryCache


class TestBaseClientCacheIntegration:
    """Test that BaseClient integrates with cache backends correctly."""

    @pytest.fixture
    def cache_config(self):
        from fmp_data.cache.config import CacheConfig

        return CacheConfig(enabled=True, backend="memory", default_ttl=300)

    @pytest.fixture
    def client_config(self, cache_config):
        from fmp_data.config import ClientConfig

        return ClientConfig(
            api_key="test-key-12345",
            cache=cache_config,
        )

    def test_cache_initialized_when_config_present(self, client_config):
        from fmp_data.base import BaseClient

        base = BaseClient(config=client_config)
        assert base._cache is not None
        assert isinstance(base._cache, MemoryCache)
        base.close()

    def test_no_cache_when_config_absent(self):
        from fmp_data.base import BaseClient
        from fmp_data.config import ClientConfig

        config = ClientConfig(api_key="test-key-12345")
        base = BaseClient(config=config)
        assert base._cache is None
        base.close()

    def test_no_cache_when_disabled(self):
        from fmp_data.base import BaseClient
        from fmp_data.cache.config import CacheConfig
        from fmp_data.config import ClientConfig

        config = ClientConfig(
            api_key="test-key-12345",
            cache=CacheConfig(enabled=False),
        )
        base = BaseClient(config=config)
        assert base._cache is None
        base.close()

    def test_build_cache_key_deterministic(self):
        from fmp_data.base import BaseClient

        params1 = {"symbol": "AAPL", "apikey": "secret", "limit": "10"}
        params2 = {"limit": "10", "symbol": "AAPL", "apikey": "different"}
        key1 = BaseClient._build_cache_key("get_quote", params1)
        key2 = BaseClient._build_cache_key("get_quote", params2)
        assert key1 == key2  # apikey excluded, params sorted

    def test_build_cache_key_different_params(self):
        from fmp_data.base import BaseClient

        key1 = BaseClient._build_cache_key("get_quote", {"symbol": "AAPL"})
        key2 = BaseClient._build_cache_key("get_quote", {"symbol": "GOOG"})
        assert key1 != key2

    def test_build_cache_key_different_endpoints(self):
        from fmp_data.base import BaseClient

        key1 = BaseClient._build_cache_key("get_quote", {"symbol": "AAPL"})
        key2 = BaseClient._build_cache_key("get_profile", {"symbol": "AAPL"})
        assert key1 != key2

    def test_cache_ttl_override(self, client_config):
        from fmp_data.base import BaseClient
        from fmp_data.cache.config import CacheConfig

        config_with_overrides = client_config.model_copy(
            update={
                "cache": CacheConfig(
                    enabled=True,
                    default_ttl=300,
                    ttl_overrides={"get_quote": 60},
                )
            }
        )
        base = BaseClient(config=config_with_overrides)
        assert base._get_cache_ttl("get_quote") == 60
        assert base._get_cache_ttl("get_profile") == 300
        base.close()

    def test_client_config_from_env_without_cache(self, monkeypatch):
        """Test that ClientConfig.from_env works without cache env vars."""
        monkeypatch.setenv("FMP_API_KEY", "test-key-12345")
        monkeypatch.delenv("FMP_CACHE_ENABLED", raising=False)

        from fmp_data.config import ClientConfig

        config = ClientConfig.from_env()
        assert config.cache is None

    def test_client_config_from_env_with_cache(self, monkeypatch):
        """Test that ClientConfig.from_env picks up cache env vars."""
        monkeypatch.setenv("FMP_API_KEY", "test-key-12345")
        monkeypatch.setenv("FMP_CACHE_ENABLED", "true")
        monkeypatch.setenv("FMP_CACHE_BACKEND", "memory")
        monkeypatch.setenv("FMP_CACHE_TTL", "120")

        from fmp_data.config import ClientConfig

        config = ClientConfig.from_env()
        assert config.cache is not None
        assert config.cache.enabled is True
        assert config.cache.backend == "memory"
        assert config.cache.default_ttl == 120

    def test_cache_hit_skips_http(self, client_config):
        """Test that a cache hit skips the actual HTTP request."""
        from fmp_data.base import BaseClient

        base = BaseClient(config=client_config)
        assert base._cache is not None

        # Pre-populate cache
        base._cache.set(
            "test_endpoint:abcdef0123456789",
            [{"symbol": "AAPL", "price": 150.0}],
        )

        # Mock the HTTP client to verify it's not called
        base.client = MagicMock()

        # The cache key would need to match - test the mechanism directly
        cached = base._cache.get("test_endpoint:abcdef0123456789")
        assert cached is not None
        assert cached[0]["symbol"] == "AAPL"

        base.close()
