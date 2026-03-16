"""Cache configuration models."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class CacheConfig(BaseModel):
    """Configuration for the response cache."""

    enabled: bool = Field(default=True, description="Whether caching is enabled")
    backend: Literal["memory", "file", "redis"] = Field(
        default="memory", description="Cache backend type"
    )
    default_ttl: int = Field(default=300, gt=0, description="Default TTL in seconds")
    ttl_overrides: dict[str, int] = Field(
        default_factory=dict,
        description="Per-endpoint TTL overrides (endpoint_name -> seconds)",
    )
    cache_dir: Path | None = Field(
        default=None, description="Directory for file-based cache"
    )
    redis_url: str | None = Field(default=None, description="Redis connection URL")

    @classmethod
    def from_env(cls) -> CacheConfig | None:
        """Create cache config from environment variables.

        Returns None if FMP_CACHE_ENABLED is not set or is 'false'.
        """
        enabled_str = os.getenv("FMP_CACHE_ENABLED", "").lower()
        if enabled_str not in ("true", "1", "yes"):
            return None

        cache_dir_str = os.getenv("FMP_CACHE_DIR")
        cache_dir = Path(cache_dir_str) if cache_dir_str else None

        try:
            ttl = int(os.getenv("FMP_CACHE_TTL", "300"))
            ttl = max(1, ttl)
        except (ValueError, TypeError):
            ttl = 300

        backend_str = os.getenv("FMP_CACHE_BACKEND", "memory")
        if backend_str not in ("memory", "file", "redis"):
            backend_str = "memory"

        return cls(
            enabled=True,
            backend=backend_str,
            default_ttl=ttl,
            cache_dir=cache_dir,
            redis_url=os.getenv("FMP_CACHE_REDIS_URL"),
        )
