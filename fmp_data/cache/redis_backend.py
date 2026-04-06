"""Redis cache backend (requires optional redis dependency)."""

from __future__ import annotations

import json
import logging
from typing import Any, cast

from fmp_data.cache.base import CacheBackend

logger = logging.getLogger(__name__)


class RedisCache(CacheBackend):
    """Redis-backed cache. Requires the ``redis`` package.

    Install via::

        pip install 'fmp-data[cache-redis]'
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,
        key_prefix: str = "fmp:",
    ) -> None:
        try:
            import redis
        except ImportError as exc:
            raise ImportError(
                "Redis cache backend requires the 'redis' package. "
                "Install via: pip install 'fmp-data[cache-redis]'"
            ) from exc

        self._client: redis.Redis[str] = redis.from_url(
            redis_url, decode_responses=True
        )
        self._default_ttl = default_ttl
        self._key_prefix = key_prefix

    def _prefixed(self, key: str) -> str:
        return f"{self._key_prefix}{key}"

    def get(self, key: str) -> Any | None:
        try:
            raw = cast(str | None, self._client.get(self._prefixed(key)))
        except Exception:
            logger.warning("Redis get error for key %s", key, exc_info=True)
            return None
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        effective_ttl = ttl if ttl is not None else self._default_ttl
        serialized = json.dumps(value, default=str)
        try:
            self._client.setex(self._prefixed(key), effective_ttl, serialized)
        except Exception:
            logger.warning("Redis set error for key %s", key, exc_info=True)

    def delete(self, key: str) -> None:
        try:
            self._client.delete(self._prefixed(key))
        except Exception:
            logger.warning("Redis delete error for key %s", key, exc_info=True)

    def clear(self) -> None:
        pattern = f"{self._key_prefix}*"
        cursor: int = 0
        try:
            while True:
                cursor, keys = cast(
                    tuple[int, list[str]],
                    self._client.scan(cursor, match=pattern, count=100),
                )
                if keys:
                    self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            logger.warning("Redis clear error", exc_info=True)
