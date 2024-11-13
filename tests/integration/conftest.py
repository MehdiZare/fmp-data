import os
from datetime import datetime, timedelta

import pytest

from fmp_data import FMPDataClient
from fmp_data.config import ClientConfig


@pytest.fixture(scope="session")
def integration_config():
    """Integration test configuration"""
    # Ensure required environment variables are set
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        pytest.skip("FMP_API_KEY environment variable not set")

    return ClientConfig(
        api_key=api_key,
        timeout=30,
        max_retries=3,
        base_url="https://financialmodelingprep.com/api",
    )


@pytest.fixture(scope="session")
def fmp_client(integration_config):
    """Create FMP client for integration tests"""
    with FMPDataClient(config=integration_config) as client:
        yield client


@pytest.fixture(scope="session")
def test_symbol():
    """Test symbol to use for integration tests"""
    return "AAPL"  # Using Apple as a reliable test case


@pytest.fixture
def date_range():
    """Get date range for historical data tests"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return start_date.date(), end_date.date()
