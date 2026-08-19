"""Response caching for FMP Data API client.

Provides pluggable cache backends (memory, file, redis) to reduce
redundant API calls and improve latency for repeated queries.
"""

from __future__ import annotations

from fmp_data.cache.base import CacheBackend
from fmp_data.cache.config import CacheConfig
from fmp_data.cache.file import FileCache
from fmp_data.cache.memory import MemoryCache

__all__ = [
    "CacheBackend",
    "CacheConfig",
    "FileCache",
    "MemoryCache",
    "create_backend",
]


def create_backend(config: CacheConfig) -> CacheBackend:
    """Instantiate a cache backend from configuration.

    Args:
        config: Cache configuration

    Returns:
        A ready-to-use CacheBackend instance

    Raises:
        ValueError: If the backend type is unknown
        ImportError: If redis backend is requested but redis is not installed
    """
    if config.backend == "memory":
        return MemoryCache(default_ttl=config.default_ttl)
    if config.backend == "file":
        from pathlib import Path

        cache_dir = config.cache_dir or Path.home() / ".cache" / "fmp-data"
        return FileCache(cache_dir=cache_dir, default_ttl=config.default_ttl)
    if config.backend == "redis":
        from fmp_data.cache.redis_backend import RedisCache

        # `redis.from_url` needs the real string; a SecretStr raises
        # AttributeError on `.startswith` (#252).
        redis_url = (
            config.redis_url.get_secret_value()
            if config.redis_url
            else "redis://localhost:6379/0"
        )
        return RedisCache(redis_url=redis_url, default_ttl=config.default_ttl)
    raise ValueError(f"Unknown cache backend: {config.backend!r}")
