"""Shared rules for hiding credentials in display strings (#252, #316).

Two jobs live here:

1. **Key-name walk** (``is_secret_key`` / ``redact_value``): ``ClientConfig.__str__``
   and ``EmbeddingConfig.__repr__`` need the same judgement about what looks
   like a credential in a structured mapping.
2. **Free-form text**: query/assignment/encoded patterns
   (``redact_credential_patterns``) are shared by HTTP error bodies and the
   setup wizard. Wizard console also runs ``redact_key_shaped_tokens``
   (sk-/32-char heuristics). Those stay off the error-body path — they
   blank request ids. Prompts use ``redact_held_secret``.

This is a *display* safeguard, not an access control. Values are still fully
available on the model; only the rendered text is masked.

CodeQL ``py/clear-text-logging-sensitive-data`` treats ``print`` / stdout as
a logging sink. Sinks may call :func:`redact_credential_patterns` (it never
takes the live secret). They must not call :func:`redact_held_secret` — that
API is for ``input`` / ``getpass`` prompts only.
"""

from __future__ import annotations

import re
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


# --- Free-form text -------------------------------------------------------
# Pattern-only. Never take the live secret as an argument. Safe for
# logging sinks / stdout (CodeQL py/clear-text-logging-sensitive-data).
_URL_CREDENTIAL_RE = re.compile(
    r"([?&](?:api[_-]?key|token|secret)=)[^&\s]+",
    re.IGNORECASE,
)
_URL_APIKEY_RE = re.compile(r"([?&]apikey=)[^&\s]+", re.IGNORECASE)
# Prefixed ``*_API_KEY=`` / hyphenated ``*-API-KEY=`` must match
# (#330, #339). Only the wizard's instruction value is skipped so
# ``export FMP_API_KEY="[YOUR_API_KEY]"`` stays readable.
_ASSIGNMENT_RE = re.compile(
    r"([\"']?(?<![A-Za-z0-9])(?:[A-Za-z0-9]+[_-])*api[_-]?key[\"']?\s*[=:]\s*[\"']?)"
    r"([^&\s\"'<>]+)([\"']?)",
    re.IGNORECASE,
)
_PLACEHOLDER_ASSIGNMENT_VALUE = re.compile(
    r"^\[YOUR_API_KEY\]$",
    re.IGNORECASE,
)
_ENCODED_RE = re.compile(r"(apikey%3[Dd])([^&\s\"'<>]+)", re.IGNORECASE)
# Wizard-console only. ``[a-zA-Z0-9]{32,}`` matches request ids; do not
# run these on HTTP error bodies (``base._redact_api_keys``).
_KEY_SHAPED_RES = (
    re.compile(r"\b(?:sk-|pk_)[a-zA-Z0-9_-]{8,}\b"),
    re.compile(r"\bapi_key=[a-zA-Z0-9_-]{8,}(?=\s|:|;|$)"),
    re.compile(r"\b[a-zA-Z0-9]{32,}\b"),
    re.compile(r"[a-fA-F0-9]{40,}"),
)
_TEXT_MASK = "[REDACTED]"


def _redact_assignment(match: re.Match[str]) -> str:
    """Redact an assignment unless the value is ``[YOUR_API_KEY]``."""
    value = match.group(2)
    if _PLACEHOLDER_ASSIGNMENT_VALUE.match(value):
        return match.group(0)
    return f"{match.group(1)}{_TEXT_MASK}{match.group(3)}"


def redact_credential_patterns(text: str) -> str:
    """Redact query/assignment/encoded credentials without the live secret.

    Safe for logging sinks, stdout, and HTTP error bodies. Does not apply
    wizard key-shaped heuristics (those blank request ids). Do not pass
    the held secret; use :func:`redact_held_secret` at prompt sites only.
    """
    result = _URL_CREDENTIAL_RE.sub(rf"\1{_TEXT_MASK}", text)
    result = _URL_APIKEY_RE.sub(rf"\1{_TEXT_MASK}", result)
    result = _ASSIGNMENT_RE.sub(_redact_assignment, result)
    return _ENCODED_RE.sub(rf"\1{_TEXT_MASK}", result)


def redact_key_shaped_tokens(text: str) -> str:
    """Redact sk-/pk_/32-char tokens. Wizard console only.

    Not for HTTP error bodies. Pair with :func:`redact_credential_patterns`
    at console sinks that must also catch keys the wizard never held.
    """
    result = text
    for pattern in _KEY_SHAPED_RES:
        result = pattern.sub(_TEXT_MASK, result)
    return result


def redact_held_secret(text: str, secret: str) -> str:
    """Exact-replace a caller-held secret. Prompts / getpass only.

    Never feed the result to a logging sink or stdout writer that CodeQL
    treats as clear-text logging (``py/clear-text-logging-sensitive-data``).
    """
    if not secret:
        return text
    return text.replace(secret, _TEXT_MASK)
