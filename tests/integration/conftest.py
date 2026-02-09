# tests/integration/conftest.py
from collections.abc import Generator
from datetime import date, timedelta
import logging
import os
from pathlib import Path
import re
import time
from typing import Any

from dotenv import load_dotenv
import pytest
import vcr
from vcr.persisters.filesystem import (
    CassetteDecodeError,
    CassetteNotFoundError,
    FilesystemPersister,
)
from vcr.request import Request
from vcr.serialize import deserialize

from fmp_data import ClientConfig, FMPDataClient, RateLimitConfig

logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=False)

if not os.getenv("FMP_TEST_API_KEY") and os.getenv("FMP_API_KEY"):
    os.environ["FMP_TEST_API_KEY"] = os.environ["FMP_API_KEY"]

if not os.getenv("FMP_API_KEY") and os.getenv("FMP_TEST_API_KEY"):
    os.environ["FMP_API_KEY"] = os.environ["FMP_TEST_API_KEY"]

VCR_RECORD_MODE = os.getenv("FMP_VCR_RECORD", "none")
if VCR_RECORD_MODE not in {"none", "once", "new_episodes", "all"}:
    logger.warning(
        "Invalid FMP_VCR_RECORD=%s; falling back to new_episodes", VCR_RECORD_MODE
    )
    VCR_RECORD_MODE = "new_episodes"


class SafeFilesystemPersister(FilesystemPersister):
    """Treat empty or invalid cassettes like missing ones for replay."""

    @classmethod
    def load_cassette(cls, cassette_path: str | Path, serializer):  # type: ignore[override]
        cassette_path = Path(cassette_path)
        if not cassette_path.is_file():
            raise CassetteNotFoundError()
        try:
            with cassette_path.open() as f:
                data = f.read()
        except UnicodeDecodeError as err:
            raise CassetteDecodeError(
                "Can't read Cassette, Encoding is broken"
            ) from err
        if not data.strip():
            raise CassetteDecodeError("Cassette is empty")
        try:
            return deserialize(data, serializer)
        except Exception as err:
            raise CassetteDecodeError(
                "Can't read Cassette, unable to deserialize"
            ) from err


def drop_unauthorized_response(response: dict | None) -> dict | None:
    """Skip replaying stale 401 responses so they get re-recorded."""
    if response and response.get("status", {}).get("code") == 401:
        return None
    return response


def scrub_api_key(request: Request) -> Request:
    """Remove API key for recording only"""
    logger.debug(f"Original request URI: {request.uri}")

    # Don't modify the actual request, just create a scrubbed copy for recording
    scrubbed_uri = request.uri
    if "apikey=" in scrubbed_uri:
        scrubbed_uri = re.sub(r"apikey=([^&]+)", "apikey=DUMMY_API_KEY", scrubbed_uri)

    scrubbed_headers = {
        key: value for key, value in request.headers.items() if key.lower() != "apikey"
    }

    return Request(
        method=request.method,
        uri=scrubbed_uri,
        body=request.body,
        headers=scrubbed_headers,
    )


def _candidate_api_keys() -> set[str]:
    """Collect key-like values that should always be scrubbed."""
    candidates = {
        os.getenv("FMP_TEST_API_KEY", "").strip(),
        os.getenv("FMP_API_KEY", "").strip(),
    }
    return {c for c in candidates if c}


def _sanitize_secret_text(value: str) -> str:
    """Sanitize API keys from arbitrary response text."""
    scrubbed = value

    # Replace known key values from env with a stable placeholder.
    for key in _candidate_api_keys():
        scrubbed = scrubbed.replace(key, "DUMMY_API_KEY")

    # Scrub query-string and URL-encoded API key parameters.
    scrubbed = re.sub(
        r"(?i)(apikey=)([^&\"'\s]+)",
        r"\1DUMMY_API_KEY",
        scrubbed,
    )
    scrubbed = re.sub(
        r"(?i)(apikey%3D)([^%&\"'\s]+)",
        r"\1DUMMY_API_KEY",
        scrubbed,
    )

    # Scrub JSON / JSON-like key fields.
    scrubbed = re.sub(
        r'(?i)("apikey"\s*:\s*")([^"]+)(")',
        r"\1DUMMY_API_KEY\3",
        scrubbed,
    )
    scrubbed = re.sub(
        r"(?i)('apikey'\s*:\s*')([^']+)(')",
        r"\1DUMMY_API_KEY\3",
        scrubbed,
    )

    return scrubbed


def scrub_response_secrets(  # noqa: C901
    response: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Sanitize sensitive values in responses before writing cassette files."""
    if response is None:
        return None
    if VCR_RECORD_MODE == "none":
        # Keep replay mode untouched so existing cassette serialization semantics
        # are preserved.
        return response

    headers = response.get("headers")
    if isinstance(headers, dict):
        for header_name in list(headers.keys()):
            lower_name = str(header_name).lower()
            if lower_name in {"authorization", "x-api-key", "apikey"}:
                header_values = headers.get(header_name)
                if isinstance(header_values, list):
                    sanitized_values = []
                    for value in header_values:
                        text = str(value)
                        if lower_name == "authorization" and text.lower().startswith(
                            "bearer "
                        ):
                            sanitized_values.append("Bearer DUMMY_API_KEY")
                        else:
                            sanitized_values.append("DUMMY_API_KEY")
                    headers[header_name] = sanitized_values
                else:
                    headers[header_name] = "DUMMY_API_KEY"

    body = response.get("body")
    if isinstance(body, dict) and "string" in body:
        body_str = body.get("string")
        if isinstance(body_str, bytes):
            try:
                decoded = body_str.decode()
            except UnicodeDecodeError:
                decoded = body_str.decode(errors="ignore")
            body["string"] = _sanitize_secret_text(decoded)
        elif isinstance(body_str, str):
            body["string"] = _sanitize_secret_text(body_str)

    return response


# Create cassettes directory
CASSETTES_PATH = (Path(__file__).parent / "vcr_cassettes").resolve()
CASSETTES_PATH.mkdir(exist_ok=True)
vcr_config = vcr.VCR(
    serializer="yaml",
    cassette_library_dir=str(CASSETTES_PATH),
    record_mode=VCR_RECORD_MODE,
    match_on=[
        "method",
        "host",
        "path",
        "query",
    ],  # Match on query with apikey filtered for stable replays
    filter_headers=["authorization", "x-api-key", "apikey"],
    before_record_request=scrub_api_key,
    before_record_response=scrub_response_secrets,
    decode_compressed_response=True,
    filter_query_parameters=["apikey"],  # Add this to filter out apikey from matching
    path_transformer=lambda path: str(CASSETTES_PATH / path),
)
vcr_config.register_persister(SafeFilesystemPersister)
vcr_config.before_playback_response = drop_unauthorized_response

logger.debug(f"VCR cassettes will be saved to: {CASSETTES_PATH}")

# Anchored date used by date-sensitive integration tests. This must match
# date windows already present in committed cassettes for deterministic replay.
VCR_ANCHORED_TODAY = date(2026, 2, 6)


@pytest.fixture(scope="session")
def vcr_instance() -> vcr.VCR:
    """Provide VCR instance"""
    return vcr_config


@pytest.fixture(scope="session")
def rate_limit_config() -> RateLimitConfig:
    """Provide relaxed but conservative rate limits for testing"""
    return RateLimitConfig(
        daily_limit=1000, requests_per_second=2, requests_per_minute=45
    )


@pytest.fixture(scope="session")
def fmp_client(rate_limit_config: RateLimitConfig) -> Generator[FMPDataClient]:
    """Create FMP client for testing"""
    if VCR_RECORD_MODE == "none" and not any(CASSETTES_PATH.rglob("*.yaml")):
        pytest.skip(
            "No VCR cassettes found for replay mode. "
            "Record with FMP_VCR_RECORD=new_episodes first."
        )

    api_key = os.getenv("FMP_TEST_API_KEY")
    if not api_key and VCR_RECORD_MODE == "none":
        # Replay mode never hits the network. A dummy key keeps tests runnable
        # on fresh environments that only have checked-in cassettes.
        api_key = "DUMMY_API_KEY"

    if not api_key:
        pytest.skip("FMP_TEST_API_KEY environment variable not set")

    # Verify we have a real API key
    if VCR_RECORD_MODE != "none" and len(api_key.strip()) < 10:
        pytest.fail(
            "FMP_TEST_API_KEY appears to be invalid. Please set a valid API key."
        )

    logger.debug("FMP_TEST_API_KEY configured")

    config = ClientConfig(
        api_key=api_key,
        base_url=os.getenv("FMP_TEST_BASE_URL", "https://financialmodelingprep.com"),
        timeout=int(float(os.getenv("FMP_TEST_TIMEOUT", "10"))),
        max_retries=2,
        rate_limit=rate_limit_config,
    )

    client = FMPDataClient(config=config)

    # Verify client configuration
    logger.debug(f"Client config: base_url={config.base_url}, timeout={config.timeout}")

    try:
        yield client
    finally:
        client.close()


@pytest.fixture(autouse=True)
def rate_limit_sleep() -> Generator:
    """Add small delay between tests to avoid rate limiting"""
    yield
    # Replay mode does not call the API and should be as fast as possible.
    if VCR_RECORD_MODE != "none":
        time.sleep(0.5)  # 500ms delay between tests


@pytest.fixture
def test_symbol() -> str:
    """Provide test symbol for all tests"""
    return "AAPL"


@pytest.fixture(scope="session")
def frozen_today() -> date:
    """Provide a deterministic 'today' for VCR-matched date range tests."""
    return VCR_ANCHORED_TODAY


@pytest.fixture(scope="session")
def frozen_future_date(frozen_today: date) -> date:
    """Provide deterministic future date used by invalid-date tests."""
    return frozen_today + timedelta(days=50)


# Additional fixtures for test data
@pytest.fixture
def test_exchange() -> str:
    """Provide test exchange"""
    return "NASDAQ"


@pytest.fixture
def test_cik() -> str:
    """Provide test CIK number"""
    return "0000320193"  # Apple's CIK


@pytest.fixture
def test_cusip() -> str:
    """Provide test CUSIP"""
    return "037833100"  # Apple's CUSIP


@pytest.fixture
def test_isin() -> str:
    """Provide test ISIN"""
    return "US0378331005"  # Apple's ISIN
