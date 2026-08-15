"""The shared secret-shape rules used by config, embeddings, and console (#252, #316).

``ClientConfig.__str__`` and ``EmbeddingConfig.__repr__`` both need the same
judgement about what looks like a credential. They used to disagree -- the
embedding side recursed into nested containers and the config side did not --
so these rules now live in one module and are tested directly rather than only
through the two callers.

Free-form text (HTTP error bodies, the setup wizard, prompts) used to each
have their own regexes. Error bodies use ``redact_credential_patterns``.
The wizard also runs ``redact_key_shaped_tokens``. Prompts use
``redact_held_secret``.
"""

from __future__ import annotations

import pytest

from fmp_data._redaction import (
    is_secret_key,
    redact_credential_patterns,
    redact_held_secret,
    redact_key_shaped_tokens,
    redact_mapping,
    redact_value,
)


@pytest.mark.parametrize(
    "key",
    [
        "api_key",
        "apikey",
        "API_KEY",
        "client-secret",
        "refreshToken",
        "accessToken",
        "password",
        "passwd",
        "pwd",
        "passphrase",
        "credentials",
        "credential",
        "Authorization",
        "auth",
        "bearer",
        "signature",
        "private_key",
    ],
)
def test_secret_shaped_names_are_recognised(key: str) -> None:
    assert is_secret_key(key)


@pytest.mark.parametrize(
    "key",
    [
        "keyboard",
        "monkey",
        "timeout",
        "base_url",
        "maxBytes",
        "backupCount",
        "level",
        "class_name",
    ],
)
def test_ordinary_names_are_left_alone(key: str) -> None:
    """Over-redaction makes the display useless; whole parts must match."""
    assert not is_secret_key(key)


def test_nested_containers_are_walked_not_copied_by_reference() -> None:
    planted = "PLANTED_aaaaaaaa"
    source = {"outer": {"inner": [{"api_key": planted}]}}

    redacted = redact_value(source)

    assert planted not in repr(redacted)
    # The original must be untouched -- this is a display copy, not a mutation.
    assert source["outer"]["inner"][0]["api_key"] == planted


def test_tuples_and_sets_keep_their_type() -> None:
    assert isinstance(redact_value(("a", "b")), tuple)
    assert isinstance(redact_value(["a"]), list)
    assert isinstance(redact_value({"a"}), set)


def test_recursion_is_bounded() -> None:
    """A `__str__` must not be a place where a deep structure can hang."""
    deep: dict[str, object] = {"k": "v"}
    for _ in range(50):
        deep = {"nest": deep}

    assert "..." in repr(redact_value(deep))


def test_redact_mapping_masks_top_level_secret_names() -> None:
    planted = "PLANTED_bbbbbbbb"
    assert redact_mapping({"api_key": planted, "timeout": 30}) == {
        "api_key": "***",
        "timeout": 30,
    }


def test_non_string_keys_do_not_raise() -> None:
    """Untyped bags can be keyed by anything."""
    assert redact_value({1: "a", None: "b"}) == {1: "a", None: "b"}


def test_pattern_api_redacts_query_assignment_and_encoded() -> None:
    """Shared path covers the former base.py rules (#316)."""
    url = "GET https://fmp.test/v3/profile?apikey=hunter2xyz&symbol=AAPL"
    assert redact_credential_patterns(url) == (
        "GET https://fmp.test/v3/profile?apikey=[REDACTED]&symbol=AAPL"
    )
    assert (
        redact_credential_patterns("denied for apikey=SECRET_FMP_KEY")
        == "denied for apikey=[REDACTED]"
    )
    encoded = "path?apikey%3Dnot-a-real-key-value"  # pragma: allowlist secret
    assert "not-a-real-key-value" not in redact_credential_patterns(encoded)
    assert "[REDACTED]" in redact_credential_patterns(encoded)
    # Wizard instruction copy must survive: the value is a placeholder,
    # not a live token (#316, #330).
    assert (
        redact_credential_patterns('export FMP_API_KEY="[YOUR_API_KEY]"')
        == 'export FMP_API_KEY="[YOUR_API_KEY]"'
    )
    planted = "PLANTED_fmp_api_key_token"
    assert planted not in redact_credential_patterns(f"FMP_API_KEY={planted}")
    assert "[REDACTED]" in redact_credential_patterns(f"FMP_API_KEY={planted}")
    assert planted not in redact_credential_patterns(f"my_api_key={planted}")


def test_pattern_api_leaves_32_char_identifiers() -> None:
    """Error-body path must not blank request ids (#316)."""
    token = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"  # noqa: S105  # pragma: allowlist secret
    assert token in redact_credential_patterns(f"request-id={token} denied")
    assert redact_credential_patterns("saved sk-abcdefgh12345678") == (
        "saved sk-abcdefgh12345678"
    )


def test_key_shaped_api_redacts_wizard_heuristics() -> None:
    """Console-only heuristics; not composed into error-body redaction."""
    assert redact_key_shaped_tokens("saved sk-abcdefgh12345678") == "saved [REDACTED]"
    token = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"  # noqa: S105  # pragma: allowlist secret
    assert redact_key_shaped_tokens(f"request failed for {token} at 401") == (
        "request failed for [REDACTED] at 401"
    )


def test_pattern_api_never_needs_the_held_secret() -> None:
    """Signature is the CodeQL contract: no secret argument on this path."""
    assert redact_credential_patterns.__code__.co_argcount == 1


def test_exact_replace_is_prompt_only() -> None:
    held = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret
    assert (
        redact_held_secret(f"tried {held} then {held}", held)
        == "tried [REDACTED] then [REDACTED]"
    )
    assert redact_held_secret("nothing here", "") == "nothing here"
