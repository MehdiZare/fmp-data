"""Optional pytest wrapper around the VCR replay of the client-method sweep.

Deselected by default (``-m not e2e``). Record first::

    uv run python scripts/e2e_endpoints.py record
    uv run pytest tests/e2e/test_client_sweep.py -m e2e
"""

from __future__ import annotations

import os

import pytest

from tests.e2e.harness import (
    CASSETTE_ROOT,
    discover_cases,
    format_report,
    run_cases,
    select_cases,
)

pytestmark = pytest.mark.e2e


def test_client_sweep_replay() -> None:
    """Replay recorded client-method cassettes; never hits the live API."""
    if not any(CASSETTE_ROOT.rglob("*.yaml")):
        pytest.skip(
            "No e2e cassettes. Record with: "
            "uv run python scripts/e2e_endpoints.py record"
        )

    os.environ.setdefault("FMP_VCR_RECORD", "none")
    from fmp_data import ClientConfig, FMPDataClient

    api_key = (
        os.getenv("FMP_TEST_API_KEY")
        or os.getenv("FMP_API_KEY")
        or "DUMMY_API_KEY"  # pragma: allowlist secret
    )
    client = FMPDataClient(config=ClientConfig(api_key=api_key, timeout=10))
    try:
        rows = run_cases(
            select_cases(discover_cases()),
            client=client,
            record_mode="none",
            throttle=0.0,
        )
    finally:
        client.close()

    payload = [row.as_dict() for row in rows]
    bad = [row for row in rows if row.status in {"error", "empty"}]
    assert not bad, format_report(payload)
