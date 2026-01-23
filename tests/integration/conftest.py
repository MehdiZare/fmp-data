# tests/integration/conftest.py
from collections.abc import Generator
import logging
import os
from pathlib import Path
import re
import time

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

VCR_RECORD_MODE = os.getenv("FMP_VCR_RECORD", "new_episodes")
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
    decode_compressed_response=True,
    filter_query_parameters=["apikey"],  # Add this to filter out apikey from matching
    path_transformer=lambda path: str(CASSETTES_PATH / path),
)
vcr_config.register_persister(SafeFilesystemPersister)
vcr_config.before_playback_response = drop_unauthorized_response

logger.debug(f"VCR cassettes will be saved to: {CASSETTES_PATH}")


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
    api_key = os.getenv("FMP_TEST_API_KEY")
    if not api_key:
        pytest.skip("FMP_TEST_API_KEY environment variable not set")

    # Verify we have a real API key
    if len(api_key.strip()) < 10:  # Adjust minimum length as needed
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
    time.sleep(0.5)  # 500ms delay between tests


@pytest.fixture
def test_symbol() -> str:
    """Provide test symbol for all tests"""
    return "AAPL"


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
