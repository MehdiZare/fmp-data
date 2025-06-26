# tests/integration/conftest.py
"""
Integration test configuration with safe imports.

This conftest handles:
- Safe imports that don't fail when core dependencies are missing
- VCR configuration for recording API responses
- Rate limiting between tests
- Test fixtures for common data
"""
import logging
import os
import re
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
import vcr
from vcr.request import Request

# Safe imports that handle missing dependencies gracefully
try:
    from fmp_data import ClientConfig, FMPDataClient, RateLimitConfig
except ImportError as e:
    # If we can't import core FMP modules, we can't run integration tests
    pytest.skip(f"Core fmp_data modules not available: {e}", allow_module_level=True)

logger = logging.getLogger(__name__)


def scrub_api_key(request: Request) -> Request:
    """Remove API key for recording only"""
    logger.debug(f"Original request URI: {request.uri}")

    # Don't modify the actual request, just create a scrubbed copy for recording
    scrubbed_uri = request.uri
    if "apikey=" in scrubbed_uri:
        scrubbed_uri = re.sub(r"apikey=([^&]+)", "apikey=DUMMY_API_KEY", scrubbed_uri)

    return Request(
        method=request.method,
        uri=scrubbed_uri,
        body=request.body,
        headers=request.headers,
    )


# Create cassettes directory
CASSETTES_PATH = (Path(__file__).parent / "vcr_cassettes").resolve()
CASSETTES_PATH.mkdir(exist_ok=True)

vcr_config = vcr.VCR(
    serializer="yaml",
    cassette_library_dir=str(CASSETTES_PATH),
    record_mode="new_episodes",
    match_on=[
        "method",
        "host",
        "path",
    ],  # Don't match on query to allow different API keys
    filter_headers=["authorization", "x-api-key"],
    before_record_request=scrub_api_key,
    decode_compressed_response=True,
    filter_query_parameters=["apikey"],  # Add this to filter out apikey from matching
    path_transformer=lambda path: str(CASSETTES_PATH / path),
)

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
def fmp_client(rate_limit_config: RateLimitConfig) -> Generator[FMPDataClient, None, None]:
    """Create FMP client for testing"""
    api_key = os.getenv("FMP_TEST_API_KEY")
    if not api_key:
        pytest.skip("FMP_TEST_API_KEY environment variable not set")

    # Verify we have a real API key
    if len(api_key.strip()) < 10:  # Adjust minimum length as needed
        pytest.fail(
            "FMP_TEST_API_KEY appears to be invalid. Please set a valid API key."
        )

    logger.info(f"Using API key starting with: {api_key[:4]}***")

    config = ClientConfig(
        api_key=api_key,
        base_url=os.getenv(
            "FMP_TEST_BASE_URL", "https://financialmodelingprep.com/api"
        ),
        timeout=10,
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
def rate_limit_sleep() -> Generator[None, None, None]:
    """Add small delay between tests to avoid rate limiting"""
    yield
    time.sleep(0.5)  # 500ms delay between tests


@pytest.fixture
def test_symbol() -> str:
    """Provide test symbol for all tests"""
    return "AAPL"


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