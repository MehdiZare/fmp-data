"""The shared secret-shape rules used by config and embedding display (#252).

``ClientConfig.__str__`` and ``EmbeddingConfig.__repr__`` both need the same
judgement about what looks like a credential. They used to disagree -- the
embedding side recursed into nested containers and the config side did not --
so these rules now live in one module and are tested directly rather than only
through the two callers.
"""

from __future__ import annotations

import pytest

from fmp_data._redaction import is_secret_key, redact_mapping, redact_value


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
