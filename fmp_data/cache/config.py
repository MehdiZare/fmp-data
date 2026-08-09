"""Cache configuration models."""

from __future__ import annotations

import difflib
import functools
import os
from pathlib import Path
from typing import Literal
import warnings

from pydantic import BaseModel, Field, model_validator


@functools.lru_cache(maxsize=1)
def _known_endpoint_names() -> frozenset[str]:
    """Every ``Endpoint.name`` declared in the package.

    Imported lazily and walked on first use rather than at module import: this
    module is reached from ``fmp_data/__init__.py``, so importing the endpoint
    catalogue at the top would invert the dependency and import the whole
    package to define a config model. Nothing constructs a ``CacheConfig``
    during ``import fmp_data`` -- ``ClientConfig.from_env`` is a classmethod
    called by user code -- so by the time the walk runs the package is loaded.

    ``BaseException``, not ``Exception``: ``fmp_data/mcp/__main__.py`` raises
    ``SystemExit`` when its extra is absent, and CI installs no extras.
    """
    import importlib
    import pkgutil

    import fmp_data
    from fmp_data.models import Endpoint

    names: set[str] = set()
    for info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not info.name.endswith(".endpoints"):
            continue
        try:
            module = importlib.import_module(info.name)
        except BaseException:  # noqa: S112 - see docstring
            continue
        names.update(
            value.name for value in vars(module).values() if isinstance(value, Endpoint)
        )
    return frozenset(names)


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

    @model_validator(mode="after")
    def _warn_on_unmatched_ttl_overrides(self) -> CacheConfig:
        """Say something when a TTL override matches no endpoint.

        ``_get_cache_ttl`` reads this dict with a plain
        ``.get(endpoint_name, default)``, so a key naming nothing is not an
        error, not a warning and not visible: the override simply never
        applies, and the only symptom is request volume that does not match
        what you configured. A typo, a name from a newer version of the
        library, or a name the library has since changed all fail the same
        silent way.

        Warned rather than raised on purpose. Config is routinely carried
        across versions, and a stale override is not a reason to stop a client
        being constructed -- the entry is kept, exactly as before, and the
        default TTL applies to that endpoint as it already did.

        The catalogue walk is skipped entirely when there are no overrides,
        which is the overwhelmingly common case, so the cost falls only on
        configs that ask for the check. An empty catalogue is treated as "could
        not tell" rather than "everything is wrong": accusing every key because
        the walk found nothing would be worse than the silence it replaces.
        """
        if not self.ttl_overrides:
            return self

        known = _known_endpoint_names()
        if not known:
            return self

        unmatched = sorted(key for key in self.ttl_overrides if key not in known)
        if not unmatched:
            return self

        described = []
        for key in unmatched:
            close = difflib.get_close_matches(key, known, n=1, cutoff=0.7)
            described.append(
                f"{key!r} (closest endpoint: {close[0]!r})" if close else repr(key)
            )

        warnings.warn(
            "cache ttl_overrides names no known endpoint: "
            + ", ".join(described)
            + ". These entries have no effect -- the default TTL applies to "
            "those endpoints. Override keys are Endpoint.name values; "
            "`fmp-mcp list` and docs/api/endpoints.md enumerate them.",
            UserWarning,
            stacklevel=2,
        )
        return self

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
