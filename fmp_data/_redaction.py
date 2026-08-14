"""Shared rules for hiding credentials in display strings (#252).

Two different places need the same judgement about "does this look like a
secret": ``ClientConfig.__str__`` renders arbitrary nested config for humans,
and ``EmbeddingConfig.__repr__`` renders the kwargs bag it splats into a
provider. Keeping one implementation means the rules cannot drift apart, and
means widening the token list fixes both at once.

This is a *display* safeguard, not an access control. Values are still fully
available on the model; only the rendered text is masked.
"""

from __future__ import annotations

from typing import Any

# Matched against ``_``/``-`` separated parts of a key name, so ``api_key``,
# ``client-secret`` and ``refreshToken`` are caught but ``keyboard`` is not.
_SECRET_KEY_TOKENS = frozenset(
    {
        "key",
        "apikey",
        "token",
        "secret",
        "password",
        "passwd",
        "pwd",
        "passphrase",
        "credential",
        "credentials",
        "authorization",
        "auth",
        "bearer",
        "signature",
        "private",
    }
)

_MASK = "***"

# Deeper structures are elided rather than walked. Config is not expected to
# nest this far, and an unbounded walk on a cyclic or adversarial structure is
# not worth the risk in a `__str__`.
_MAX_DEPTH = 6


def _split_key(key: str) -> list[str]:
    """Split a key name into comparable parts, including camelCase.

    The boundary is a *lower-to-upper* transition, not any capital: splitting
    on every capital shreds an all-caps name, so ``API_KEY`` would become
    ``["a", "p", "i", ...]`` and match nothing.
    """
    normalized = key.replace("-", "_")
    parts: list[str] = []
    for chunk in normalized.split("_"):
        # `refreshToken` -> ["refresh", "Token"]; `API` stays `["API"]`
        current = ""
        for char in chunk:
            if char.isupper() and current and not current[-1].isupper():
                parts.append(current)
                current = char
            else:
                current += char
        if current:
            parts.append(current)
    return [part.lower() for part in parts if part]


def is_secret_key(key: str) -> bool:
    """True when a key name looks like it holds a credential."""
    return any(part in _SECRET_KEY_TOKENS for part in _split_key(key))


def redact_value(value: Any, depth: int = 0) -> Any:
    """Copy a value with secret-shaped entries inside containers replaced.

    Recursion matters: credentials show up in *nested* untyped bags --
    ``OpenAIEmbeddings`` takes ``default_headers={"Authorization": ...}``, and
    ``LogHandlerConfig.handler_kwargs`` is a bare ``dict[str, Any]`` handed
    straight to a logging handler. A top-level-only scan copies those by
    reference and prints the secret verbatim (#273).
    """
    if depth >= _MAX_DEPTH:
        return "..."
    if isinstance(value, dict):
        return {
            key: (
                _MASK
                if isinstance(key, str) and is_secret_key(key)
                else redact_value(item, depth + 1)
            )
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return type(value)(redact_value(item, depth + 1) for item in value)
    if isinstance(value, set):
        return {redact_value(item, depth + 1) for item in value}
    return value


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Copy a mapping with secret-shaped keys masked, recursively."""
    return {
        key: (_MASK if is_secret_key(key) else redact_value(value))
        for key, value in data.items()
    }
