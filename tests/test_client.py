# tests/test_client.py
"""Tests for FMP client."""
import pytest
import responses

from fmp_data.client import FMPClient
from fmp_data.exceptions import AuthenticationError


@pytest.fixture
def mock_responses():
    """Set up responses mock."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Enable pass_through to allow other requests
        rsps.add_passthru("https://financialmodelingprep.com/api")
        yield rsps


@responses.activate
def test_auth_success():
    """Test successful authentication."""
    responses.add(
        method=responses.GET,
        url="https://financialmodelingprep.com/api/v3/stock/list",
        json=[{"symbol": "AAPL", "name": "Apple Inc"}],
        status=200,
        match_querystring=False,
    )

    client = FMPClient(api_key="dummy_key")  # pragma: allowlist secret
    assert client is not None


@responses.activate
def test_auth_failure():
    """Test authentication failure."""
    responses.add(
        method=responses.GET,
        url="https://financialmodelingprep.com/api/v3/stock/list",
        json={"error": "Invalid API key"},
        status=401,
        match_querystring=False,
    )

    with pytest.raises(AuthenticationError):
        FMPClient(api_key="invalid_key")  # pragma: allowlist secret
