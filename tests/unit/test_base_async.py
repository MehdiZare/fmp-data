# tests/unit/test_base_async.py
"""Tests for async client functionality in BaseClient."""

import inspect
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

    @pytest.mark.asyncio
    async def test_async_client_installs_the_awaitable_redirect_hook(
        self, client_config
    ):
        """The async client must register the *async* SEC-004 hook.

        ``httpx.AsyncClient`` does ``await hook(response)``. Registering the
        plain sync function made httpx await ``None``, which raised
        ``TypeError`` on every async response. Membership alone is not
        enough — assert it is a coroutine function too.
        """
        from fmp_data.base import BaseClient, _areject_cross_origin_redirect

        client = BaseClient(client_config)
        try:
            hooks = client._setup_async_client().event_hooks["response"]
            assert _areject_cross_origin_redirect in hooks
            assert all(inspect.iscoroutinefunction(hook) for hook in hooks), (
                "every async response hook must be awaitable"
            )
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_async_hook_lets_a_normal_response_through(self, client_config):
        """Regression: a plain 200 must not raise (#252 FMP-SEC-004).

        This drives the real ``httpx.AsyncClient`` send path rather than an
        ``AsyncMock``. Before the async wrapper existed this raised
        ``TypeError: object NoneType can't be used in 'await' expression``
        for *every* async request, and the mock-based tests could not see it.
        """
        from fmp_data.base import BaseClient

        client = BaseClient(client_config)
        try:
            async_client = client._setup_async_client()
            async_client._transport = httpx.MockTransport(
                lambda request: httpx.Response(200, json={"symbol": "AAPL"})
            )
            response = await async_client.get("https://financialmodelingprep.com/x")
            assert response.status_code == 200
            assert response.json() == {"symbol": "AAPL"}
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_async_hook_refuses_a_real_cross_origin_redirect(self, client_config):
        """A 302 to another origin is refused before the second hop."""
        from fmp_data.base import BaseClient
        from fmp_data.exceptions import FMPError

        seen: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(str(request.url))
            if request.url.host == "financialmodelingprep.com":
                return httpx.Response(
                    302, headers={"Location": "https://attacker.test/steal"}
                )
            return httpx.Response(200, json={"leaked": True})

        client = BaseClient(client_config)
        try:
            async_client = client._setup_async_client()
            async_client._transport = httpx.MockTransport(handler)
            with pytest.raises(FMPError, match="Refusing cross-origin redirect"):
                await async_client.get("https://financialmodelingprep.com/x")
        finally:
            await client.aclose()

        assert not any("attacker.test" in url for url in seen), (
            f"request reached the attacker origin: {seen}"
        )

    @pytest.mark.asyncio
    async def test_async_hook_allows_a_same_origin_redirect(self, client_config):
        """Same-origin 3xx still follows through to the final response."""
        from fmp_data.base import BaseClient

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/x":
                return httpx.Response(
                    302,
                    headers={"Location": "https://financialmodelingprep.com/y"},
                )
            return httpx.Response(200, json={"ok": True})

        client = BaseClient(client_config)
        try:
            async_client = client._setup_async_client()
            async_client._transport = httpx.MockTransport(handler)
            response = await async_client.get("https://financialmodelingprep.com/x")
            assert response.status_code == 200
            assert response.json() == {"ok": True}
        finally:
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
        # Read through a local so mypy does not pin the property to Literal[False]
        closed_before = async_client.is_closed
        assert not closed_before

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
        """Test that async request retries on transient failures.

        Patches ``asyncio.sleep`` so the Tenacity 4-10s backoff is not a
        real wait (#372 leftover of #358).
        """
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

        with (
            patch.object(client, "_setup_async_client") as mock_setup,
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            mock_async_client = AsyncMock()
            mock_async_client.request = mock_request
            mock_setup.return_value = mock_async_client

            result = await client.request_async(sample_endpoint, symbol="AAPL")

            # Should have been called 3 times (2 failures + 1 success)
            assert call_count == 3
            assert result == {"test": "data"}
            # Two backoffs between the three attempts. Tenacity 9.1.4 async
            # retries go through asyncio.sleep, not tenacity.nap.sleep (#372).
            assert mock_sleep.await_count == 2

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
        client._rate_limiter.get_wait_time = lambda: 0.001  # type: ignore[method-assign]

        try:
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                await client.request_async(sample_endpoint, symbol="AAPL")
        finally:
            client._rate_limiter.get_wait_time = (  # type: ignore[method-assign]
                original_get_wait_time
            )

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

        # Read through locals so mypy does not pin the properties to Literal[False]
        sync_closed_before = sync_client.is_closed
        async_closed_before = async_client.is_closed
        assert not sync_closed_before
        assert not async_closed_before

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
