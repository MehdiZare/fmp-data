from __future__ import annotations

import glob
from pathlib import Path
import re

import pytest
from vcr.request import Request

from tests.integration.conftest import scrub_api_key, scrub_response_secrets


def test_scrub_api_key_removes_header_and_uri_value() -> None:
    request = Request(
        method="GET",
        uri="https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey=REAL_KEY",
        body="",
        headers={"apikey": ["REAL_KEY"], "Accept": ["application/json"]},
    )

    scrubbed = scrub_api_key(request)

    assert "apikey=DUMMY_API_KEY" in scrubbed.uri
    assert "REAL_KEY" not in scrubbed.uri
    assert "apikey" not in {k.lower() for k in scrubbed.headers}


def test_scrub_response_secrets_masks_query_json_and_headers(monkeypatch) -> None:
    monkeypatch.setattr("tests.integration.conftest.VCR_RECORD_MODE", "new_episodes")
    monkeypatch.setenv("FMP_TEST_API_KEY", "SECRET_API_KEY")

    response = {
        "status": {"code": 200},
        "headers": {
            "Authorization": ["Bearer SECRET_API_KEY"],
            "x-api-key": ["SECRET_API_KEY"],
            "Content-Type": ["application/json"],
        },
        "body": {
            "string": (
                '{"link":"https://x.test/path?apikey=SECRET_API_KEY&foo=1",'
                '"apikey":"SECRET_API_KEY",'
                '"encoded":"apikey%3DSECRET_API_KEY%26foo%3D1"}'
            )
        },
    }

    scrubbed = scrub_response_secrets(response)
    assert scrubbed is not None

    assert scrubbed["headers"]["Authorization"] == ["Bearer DUMMY_API_KEY"]
    assert scrubbed["headers"]["x-api-key"] == ["DUMMY_API_KEY"]

    body = scrubbed["body"]["string"]
    assert "SECRET_API_KEY" not in body
    assert "apikey=DUMMY_API_KEY" in body
    assert '"apikey":"DUMMY_API_KEY"' in body
    assert "apikey%3DDUMMY_API_KEY" in body


# ---------------------------------------------------------------------------
# Cassette leak guard - scans committed YAML cassettes for real API keys
# ---------------------------------------------------------------------------

_CASSETTES_DIR = Path(__file__).resolve().parents[1] / "integration" / "vcr_cassettes"

# Values that are safe / expected placeholder strings
_SAFE_API_KEY_VALUES = frozenset(
    {
        "DUMMY_API_KEY",
        "YOUR_API_KEY",
    }
)

# Patterns that match apikey=<value> in query strings and "apikey":"<value>" in JSON.
# The query-string regex uses a word-character class to avoid capturing YAML line-
# continuation artefacts (backslashes, quotes, commas) that the serialiser appends.
_APIKEY_QUERY_RE = re.compile(r"apikey=(\w+)", re.IGNORECASE)
_APIKEY_JSON_RE = re.compile(r'"apikey"\s*:\s*"([^"]+)"', re.IGNORECASE)


def test_no_api_key_leaks_in_cassettes() -> None:
    """Ensure no real API keys are present in committed VCR cassettes.

    This is a defense-in-depth check: the VCR recording layer already sanitises
    keys, but if sanitisation ever fails or a cassette is manually edited, this
    test will catch the leak before it reaches the remote.
    """
    cassette_files = sorted(
        glob.glob(str(_CASSETTES_DIR / "**" / "*.yaml"), recursive=True)
    )
    if not cassette_files:
        pytest.skip("No VCR cassette YAML files found to scan")

    violations: list[str] = []

    for filepath in cassette_files:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
        relative = Path(filepath).relative_to(_CASSETTES_DIR)

        for lineno, line in enumerate(content.splitlines(), start=1):
            for match in _APIKEY_QUERY_RE.finditer(line):
                value = match.group(1)
                if value not in _SAFE_API_KEY_VALUES:
                    violations.append(
                        f"{relative}:{lineno}  apikey={value} (query string)"
                    )

            for match in _APIKEY_JSON_RE.finditer(line):
                value = match.group(1)
                if value not in _SAFE_API_KEY_VALUES:
                    violations.append(
                        f"{relative}:{lineno}  apikey={value} (JSON body)"
                    )

    assert (
        not violations
    ), f"Found {len(violations)} API key leak(s) in VCR cassettes:\n" + "\n".join(
        f"  - {v}" for v in violations
    )
