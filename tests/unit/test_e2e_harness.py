"""Guards for the e2e sweep harness that must run in the default unit suite."""

from tests.e2e.harness import _FIXED_SAMPLES, _METHOD_OVERRIDES, ALLOW_EMPTY


def test_trades_by_id_are_not_allow_empty() -> None:
    """Pinned member ids return rows; empty 200 is a broken path (#337).

    Name-based lookups stay on ALLOW_EMPTY — emptiness there is about
    the entity, not a wrong path or expired docs example.
    """
    assert ("intelligence", "get_senate_trades_by_id") not in ALLOW_EMPTY
    assert ("intelligence", "get_house_trades_by_id") not in ALLOW_EMPTY
    assert ("intelligence", "get_senate_trades_by_name") in ALLOW_EMPTY
    assert ("intelligence", "get_house_trades_by_name") in ALLOW_EMPTY


def test_trades_by_id_keep_known_nonempty_member_pins() -> None:
    """Do not drop the pins while removing ALLOW_EMPTY (#337)."""
    assert _METHOD_OVERRIDES[("intelligence", "get_senate_trades_by_id")] == {
        "senate_id": "W000802"
    }
    assert _FIXED_SAMPLES["senate_id"] == "P000197"
