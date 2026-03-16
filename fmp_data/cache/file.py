"""File-based cache backend using JSON files."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any

from fmp_data.cache.base import CacheBackend

logger = logging.getLogger(__name__)


class FileCache(CacheBackend):
    """File-based cache that stores each entry as a JSON file.

    Each cache entry is stored as a JSON file in the configured directory.
    File names are derived from a SHA-256 hash of the cache key.
    """

    def __init__(self, cache_dir: Path, default_ttl: int = 300) -> None:
        self._cache_dir = cache_dir
        self._default_ttl = default_ttl
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / f"{hashed}.json"

    def get(self, key: str) -> Any | None:
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            expires_at = raw.get("expires_at", 0)
            if time.time() > expires_at:
                path.unlink(missing_ok=True)
                return None
            return raw["value"]
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            logger.debug("Cache read error for key %s: %s", key, exc)
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        effective_ttl = ttl if ttl is not None else self._default_ttl
        path = self._key_to_path(key)
        payload = {
            "key": key,
            "value": value,
            "expires_at": time.time() + effective_ttl,
        }
        try:
            path.write_text(json.dumps(payload, default=str), encoding="utf-8")
        except OSError as exc:
            logger.warning("Cache write error for key %s: %s", key, exc)

    def delete(self, key: str) -> None:
        path = self._key_to_path(key)
        path.unlink(missing_ok=True)

    def clear(self) -> None:
        for path in self._cache_dir.glob("*.json"):
            path.unlink(missing_ok=True)
