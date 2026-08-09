"""A TTL override naming no endpoint must say so (#166, follow-up).

``BaseClient._get_cache_ttl`` reads ``CacheConfig.ttl_overrides`` with a plain
``.get(endpoint_name, default)``. A key that matches no endpoint is therefore
not an error, not a warning and not visible -- the override just never applies,
and the only symptom is request volume that quietly disagrees with the config.

This was found while establishing the blast radius of #166, which proposes
renaming ``market.search-name``. That rename cannot be made safely while a
newly-unmatched override key fails silently: the user would lose their TTL
setting with nothing to tell them. The rename is deferred to 3.0; this half is
worth having on its own, and it is what turns the rename from silent into
announced.

Warned, never raised: config is carried across versions, and a stale override
is not a reason to stop a client being constructed.
"""

from __future__ import annotations

import warnings

import pytest

from fmp_data.cache.config import CacheConfig, _known_endpoint_names


def test_the_catalogue_is_not_empty() -> None:
    """Without this the whole check passes vacuously in the other direction.

    An empty catalogue makes ``CacheConfig`` treat every key as valid (it bails
    out rather than accusing everything), so a walk that stopped yielding would
    turn every assertion below into a silent no-op.
    """
    known = _known_endpoint_names()
    assert len(known) >= 250, (
        f"only {len(known)} endpoint names found; has the walk stopped working?"
    )
    assert "search-name" in known


def test_unknown_key_warns_and_names_it() -> None:
    with pytest.warns(UserWarning) as record:
        CacheConfig(ttl_overrides={"totally-bogus-endpoint": 3600})

    message = str(record[0].message)
    assert "totally-bogus-endpoint" in message
    assert "no effect" in message
    assert "Endpoint.name" in message
    assert "docs/api/endpoints.md" in message
    assert "fmp-mcp list" not in message


def test_a_typo_suggests_the_endpoint_it_nearly_matched() -> None:
    """The failure mode this exists for is a typo, so name the near miss.

    ``serch-name`` against ``search-name`` is the shape a user actually hits,
    and it is one character from working.
    """
    with pytest.warns(UserWarning) as record:
        CacheConfig(ttl_overrides={"serch-name": 60})

    message = str(record[0].message)
    assert "serch-name" in message
    assert "search-name" in message


def test_a_key_with_no_near_match_is_still_reported() -> None:
    """No suggestion is not a reason to stay quiet."""
    with pytest.warns(UserWarning) as record:
        CacheConfig(ttl_overrides={"zzzzzzzzzzzz": 60})

    assert "zzzzzzzzzzzz" in str(record[0].message)


def test_known_keys_stay_silent() -> None:
    """The common case must not become noise users learn to filter."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        config = CacheConfig(ttl_overrides={"search-name": 900, "quote": 30})

    assert config.ttl_overrides == {"search-name": 900, "quote": 30}


def test_no_overrides_skips_the_catalogue_walk_entirely() -> None:
    """The check must cost nothing for the config almost everyone has.

    Asserted by making the walk explode: if the empty-dict path reached it,
    this raises rather than fails an assertion.
    """
    import fmp_data.cache.config as cache_config

    original = cache_config._known_endpoint_names

    def _boom() -> frozenset[str]:
        raise AssertionError("catalogue walked for a config with no overrides")

    cache_config._known_endpoint_names = _boom  # type: ignore[assignment]
    try:
        CacheConfig()
        CacheConfig(ttl_overrides={})
    finally:
        cache_config._known_endpoint_names = original


def test_an_unmatched_key_is_kept_not_dropped() -> None:
    """Warning, not raising, and not silently repairing either.

    Deleting the entry would be a second silent behaviour on top of the one
    being fixed, and the user may be running config that a future version will
    match again.
    """
    with pytest.warns(UserWarning):
        config = CacheConfig(ttl_overrides={"nope": 42, "quote": 30})

    assert config.ttl_overrides == {"nope": 42, "quote": 30}


def test_an_empty_catalogue_accuses_nobody(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unreadable catalogue means "cannot tell", not "everything is wrong".

    The walk swallows import failures, so a broken environment yields an empty
    set. Warning on every key there would be worse than the silence this
    replaces.
    """
    import fmp_data.cache.config as cache_config

    monkeypatch.setattr(cache_config, "_known_endpoint_names", lambda: frozenset())
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        CacheConfig(ttl_overrides={"anything-at-all": 5})


def test_the_ttl_lookup_still_reads_the_key_it_warned_about() -> None:
    """The warning is advisory; the plumbing is untouched.

    Pins that this change did not quietly alter which TTL an endpoint gets --
    the override still applies for a matching name, and the default still
    applies for a non-matching one.
    """
    from fmp_data.base import BaseClient

    client = object.__new__(BaseClient)
    client._cache_ttl_overrides = {"search-name": 900}
    client._cache_default_ttl = 300

    assert client._get_cache_ttl("search-name") == 900
    assert client._get_cache_ttl("serch-name") == 300
