# tests/unit/test_base_async.py
"""Tests for async client functionality in BaseClient."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from fmp_data.config import ClientConfig, LoggingConfig, RateLimitConfig
from fmp_data.exceptions import RateLimitError
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
)


@pytest.fixture
def client_config():
    """Create a test client configuration"""
    return ClientConfig(
        api_key="test_api_key",
        timeout=5,
        max_retries=3,
        max_rate_limit_retries=2,
        base_url="https://test.financialmodelingprep.com",
        logging=LoggingConfig(
            level="ERROR",
            handlers={
                "console": {
                    "class_name": "StreamHandler",
                    "level": "ERROR",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }
            },
        ),
        rate_limit=RateLimitConfig(
            daily_limit=1000, requests_per_second=10, requests_per_minute=300
        ),
    )


@pytest.fixture
def sample_endpoint():
    """Create a sample endpoint for testing."""
    return Endpoint(
        name="test_endpoint",
        path="test/path",
        version=APIVersion.STABLE,
        method=HTTPMethod.GET,
        description="A test endpoint",
        mandatory_params=[
            EndpointParam(
                name="symbol",
                location=ParamLocation.QUERY,
                param_type=ParamType.STRING,
                required=True,
                description="Stock symbol",
            )
        ],
        optional_params=[],
        response_model=dict,
    )


class TestAsyncClientReuse:
    """Tests for async client connection pooling."""

    @pytest.mark.asyncio
    async def test_async_client_is_reused(self, client_config):
        """Test that the same async client is reused across multiple calls."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Get async client twice
        async_client_1 = client._setup_async_client()
        async_client_2 = client._setup_async_client()

        # Should be the same instance
        assert async_client_1 is async_client_2

        # Cleanup
        await client.aclose()

    @pytest.mark.asyncio
    async def test_async_client_recreated_after_close(self, client_config):
        """Test that async client is recreated after being closed."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Get async client
        async_client_1 = client._setup_async_client()

        # Close it
        await client.aclose()

        # Get new async client
        async_client_2 = client._setup_async_client()

        # Should be different instances
        assert async_client_1 is not async_client_2

        # Cleanup
        await client.aclose()


class TestAclose:
    """Tests for async close functionality."""

    @pytest.mark.asyncio
    async def test_aclose_closes_async_client(self, client_config):
        """Test that aclose properly closes the async client."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Initialize async client
        async_client = client._setup_async_client()
        assert not async_client.is_closed

        # Close it
        await client.aclose()

        # Should be closed and cleared
        assert async_client.is_closed
        assert client._async_client is None

    @pytest.mark.asyncio
    async def test_aclose_is_idempotent(self, client_config):
        """Test that calling aclose multiple times is safe."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Initialize async client
        client._setup_async_client()

        # Close multiple times - should not raise
        await client.aclose()
        await client.aclose()
        await client.aclose()


class TestAsyncContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager_basic(self, client_config):
        """Test basic async context manager usage."""
        from fmp_data import FMPDataClient

        async with FMPDataClient(config=client_config) as client:
            assert client._initialized
            # Initialize async client
            client._setup_async_client()
            assert client._async_client is not None

        # After exiting, async client should be closed
        assert client._async_client is None


class TestAsyncRetry:
    """Tests for async retry functionality."""

    @pytest.mark.asyncio
    async def test_request_async_with_retry_on_transient_failure(
        self, client_config, sample_endpoint
    ):
        """Test that async request retries on transient failures."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Mock the async client to fail twice then succeed
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        mock_response.aclose = AsyncMock()

        call_count = 0

        async def mock_request(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return mock_response

        with patch.object(client, "_setup_async_client") as mock_setup:
            mock_async_client = AsyncMock()
            mock_async_client.request = mock_request
            mock_setup.return_value = mock_async_client

            result = await client.request_async(sample_endpoint, symbol="AAPL")

            # Should have been called 3 times (2 failures + 1 success)
            assert call_count == 3
            assert result == {"test": "data"}

        await client.aclose()


class TestAsyncRateLimitHandling:
    """Tests for async rate limit handling."""

    @pytest.mark.asyncio
    async def test_request_async_rate_limit_raises_after_retries(
        self, client_config, sample_endpoint
    ):
        """Test that rate limit error is raised after max retries."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Force rate limiter to always deny and make wait time 0
        # to avoid actual waiting in tests
        client._rate_limiter._daily_requests = (
            client._rate_limiter.quota_config.daily_limit
        )

        # Mock get_wait_time to return 0 so we don't actually wait
        original_get_wait_time = client._rate_limiter.get_wait_time
        client._rate_limiter.get_wait_time = lambda: 0.001

        try:
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                await client.request_async(sample_endpoint, symbol="AAPL")
        finally:
            client._rate_limiter.get_wait_time = original_get_wait_time

        await client.aclose()


class TestAcloseCleanup:
    """Tests for aclose properly cleaning up all resources."""

    @pytest.mark.asyncio
    async def test_aclose_closes_both_clients(self, client_config):
        """Test that aclose closes both sync and async clients."""
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)

        # Use both sync and async clients
        sync_client = client.client  # Access sync client
        async_client = client._setup_async_client()  # Create async client

        assert not sync_client.is_closed
        assert not async_client.is_closed

        # aclose should close both
        await client.aclose()

        assert sync_client.is_closed
        assert async_client.is_closed
        assert client._async_client is None

    @pytest.mark.asyncio
    async def test_fmp_client_aclose_logs_message(self, client_config):
        """Test that FMPDataClient.aclose logs the close message."""
        from fmp_data import FMPDataClient

        client = FMPDataClient(config=client_config)

        # Initialize async client
        client._setup_async_client()

        with patch.object(client.logger, "info") as mock_info:
            await client.aclose()

            # Should have logged the close message
            mock_info.assert_called_with("FMP Data client closed")
