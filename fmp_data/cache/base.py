"""Abstract cache backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from typing import Any


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found / expired
        """

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use backend default)
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a key from the cache."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from the cache."""

    async def aget(self, key: str) -> Any | None:
        """Async variant of get. Offloads to a thread by default."""
        return await asyncio.to_thread(self.get, key)

    async def aset(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Async variant of set. Offloads to a thread by default."""
        await asyncio.to_thread(self.set, key, value, ttl)

    async def adelete(self, key: str) -> None:
        """Async variant of delete. Offloads to a thread by default."""
        await asyncio.to_thread(self.delete, key)

    async def aclear(self) -> None:
        """Async variant of clear. Offloads to a thread by default."""
        await asyncio.to_thread(self.clear)
