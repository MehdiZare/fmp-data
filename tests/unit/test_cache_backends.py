"""Unit tests for cache backends."""

from __future__ import annotations

from pathlib import Path
import time

import pytest

from fmp_data.cache.config import CacheConfig
from fmp_data.cache.file import FileCache
from fmp_data.cache.memory import MemoryCache


class TestMemoryCache:
    """Tests for the in-memory cache backend."""

    def test_get_set(self):
        cache = MemoryCache(default_ttl=60)
        cache.set("key1", {"data": "value"})
        assert cache.get("key1") == {"data": "value"}

    def test_get_missing_key(self):
        cache = MemoryCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        cache = MemoryCache(default_ttl=1)
        cache.set("key1", "value", ttl=1)
        assert cache.get("key1") == "value"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_custom_ttl_override(self):
        cache = MemoryCache(default_ttl=60)
        cache.set("short", "value", ttl=1)
        assert cache.get("short") == "value"
        time.sleep(1.1)
        assert cache.get("short") is None

    def test_delete(self):
        cache = MemoryCache()
        cache.set("key1", "value")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_delete_nonexistent(self):
        cache = MemoryCache()
        cache.delete("nonexistent")  # Should not raise

    def test_clear(self):
        cache = MemoryCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.size == 0

    def test_size(self):
        cache = MemoryCache()
        assert cache.size == 0
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.size == 2

    def test_overwrite_key(self):
        cache = MemoryCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"

    def test_stores_complex_data(self):
        cache = MemoryCache()
        data = [{"symbol": "AAPL", "price": 150.0}, {"symbol": "GOOG", "price": 2800}]
        cache.set("quotes", data)
        assert cache.get("quotes") == data


class TestFileCache:
    """Tests for the file-based cache backend."""

    def test_get_set(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path, default_ttl=60)
        cache.set("key1", {"data": "value"})
        assert cache.get("key1") == {"data": "value"}

    def test_get_missing_key(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path)
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path, default_ttl=1)
        cache.set("key1", "value", ttl=1)
        assert cache.get("key1") == "value"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path)
        cache.set("key1", "value")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_clear(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert len(list(tmp_path.glob("*.json"))) == 0

    def test_creates_directory(self, tmp_path: Path):
        cache_dir = tmp_path / "nested" / "cache"
        cache = FileCache(cache_dir=cache_dir)
        cache.set("key", "value")
        assert cache.get("key") == "value"
        assert cache_dir.exists()

    def test_write_error_does_not_raise(self, tmp_path: Path):
        from unittest.mock import patch

        cache = FileCache(cache_dir=tmp_path)
        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            cache.set("key", "value")  # Should not raise

    def test_corrupted_file_returns_none(self, tmp_path: Path):
        cache = FileCache(cache_dir=tmp_path)
        cache.set("key", "value")
        # Corrupt the file
        for f in tmp_path.glob("*.json"):
            f.write_text("not valid json", encoding="utf-8")
        assert cache.get("key") is None


class TestCacheConfig:
    """Tests for CacheConfig model."""

    def test_defaults(self):
        config = CacheConfig()
        assert config.enabled is True
        assert config.backend == "memory"
        assert config.default_ttl == 300
        assert config.ttl_overrides == {}
        assert config.cache_dir is None
        assert config.redis_url is None

    def test_custom_values(self, tmp_path: Path):
        cache_dir = tmp_path / "fmp-cache"
        config = CacheConfig(
            backend="file",
            default_ttl=600,
            ttl_overrides={"quote": 60},
            cache_dir=cache_dir,
        )
        assert config.backend == "file"
        assert config.default_ttl == 600
        assert config.ttl_overrides == {"quote": 60}
        assert config.cache_dir == cache_dir

    def test_from_env_disabled(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("FMP_CACHE_ENABLED", raising=False)
        assert CacheConfig.from_env() is None

    def test_from_env_enabled(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        cache_dir = str(tmp_path / "fmp-cache")
        monkeypatch.setenv("FMP_CACHE_ENABLED", "true")
        monkeypatch.setenv("FMP_CACHE_BACKEND", "file")
        monkeypatch.setenv("FMP_CACHE_TTL", "600")
        monkeypatch.setenv("FMP_CACHE_DIR", cache_dir)
        config = CacheConfig.from_env()
        assert config is not None
        assert config.enabled is True
        assert config.backend == "file"
        assert config.default_ttl == 600
        assert config.cache_dir == Path(cache_dir)

    def test_from_env_invalid_ttl_defaults(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("FMP_CACHE_ENABLED", "true")
        monkeypatch.setenv("FMP_CACHE_TTL", "not_a_number")
        config = CacheConfig.from_env()
        assert config is not None
        assert config.default_ttl == 300

    def test_from_env_invalid_backend_defaults(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("FMP_CACHE_ENABLED", "true")
        monkeypatch.setenv("FMP_CACHE_BACKEND", "unknown")
        config = CacheConfig.from_env()
        assert config is not None
        assert config.backend == "memory"


class TestAsyncCacheBackendDefaults:
    """Tests for async method defaults on CacheBackend."""

    @pytest.mark.asyncio
    async def test_async_get_delegates_to_sync(self):
        cache = MemoryCache(default_ttl=60)
        cache.set("k", "v")
        result = await cache.aget("k")
        assert result == "v"

    @pytest.mark.asyncio
    async def test_async_set_delegates_to_sync(self):
        cache = MemoryCache(default_ttl=60)
        await cache.aset("k", "v")
        assert cache.get("k") == "v"

    @pytest.mark.asyncio
    async def test_async_delete_delegates_to_sync(self):
        cache = MemoryCache(default_ttl=60)
        cache.set("k", "v")
        await cache.adelete("k")
        assert cache.get("k") is None

    @pytest.mark.asyncio
    async def test_async_clear_delegates_to_sync(self):
        cache = MemoryCache(default_ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        await cache.aclear()
        assert cache.size == 0


class TestCreateBackend:
    """Tests for create_backend factory."""

    def test_memory_backend(self):
        from fmp_data.cache import create_backend

        config = CacheConfig(backend="memory", default_ttl=120)
        backend = create_backend(config)
        assert isinstance(backend, MemoryCache)

    def test_file_backend(self, tmp_path: Path):
        from fmp_data.cache import create_backend

        config = CacheConfig(backend="file", cache_dir=tmp_path)
        backend = create_backend(config)
        assert isinstance(backend, FileCache)

    def test_unknown_backend_raises(self):
        from fmp_data.cache import create_backend

        config = CacheConfig(backend="memory")
        # Monkeypatch the backend to an invalid value
        object.__setattr__(config, "backend", "unknown")
        with pytest.raises(ValueError, match="Unknown cache backend"):
            create_backend(config)
