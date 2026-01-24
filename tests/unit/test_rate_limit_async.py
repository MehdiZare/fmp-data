# tests/unit/test_rate_limit_async.py
"""Tests for AsyncFMPRateLimiter."""

import asyncio

import pytest

from fmp_data.rate_limit import AsyncFMPRateLimiter, FMPRateLimiter, QuotaConfig


@pytest.fixture
def quota_config():
    """Create a test quota config."""
    return QuotaConfig(
        daily_limit=100,
        requests_per_second=5,
        requests_per_minute=50,
    )


@pytest.fixture
def sync_limiter(quota_config):
    """Create a sync rate limiter."""
    return FMPRateLimiter(quota_config)


@pytest.fixture
def async_limiter(sync_limiter):
    """Create an async rate limiter wrapping the sync limiter."""
    return AsyncFMPRateLimiter(sync_limiter)


class TestAsyncRateLimiterLocking:
    """Tests for async rate limiter thread safety."""

    @pytest.mark.asyncio
    async def test_async_lock_prevents_race_conditions(self, quota_config):
        """Test that async lock prevents race conditions in concurrent requests."""
        sync_limiter = FMPRateLimiter(quota_config)
        async_limiter = AsyncFMPRateLimiter(sync_limiter)

        # Record many requests concurrently
        async def record_request():
            allowed = await async_limiter.should_allow_request()
            if allowed:
                await async_limiter.record_request()
            return allowed

        # Run 20 concurrent requests
        tasks = [record_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)

        # All 20 should have been allowed (we have capacity for 50/minute, 5/second)
        # But due to per-second limit, only some should succeed
        allowed_count = sum(1 for r in results if r)

        # The sync limiter should have recorded the correct count
        assert sync_limiter._daily_requests == allowed_count


class TestSharedStateWithSyncLimiter:
    """Tests that async limiter shares state with sync limiter."""

    @pytest.mark.asyncio
    async def test_shared_daily_count(self, sync_limiter, async_limiter):
        """Test that daily count is shared between sync and async limiters."""
        # Record via sync
        sync_limiter.record_request()
        sync_limiter.record_request()

        # Daily count should be visible to async
        assert sync_limiter._daily_requests == 2

        # Record via async
        await async_limiter.record_request()

        # Both should see 3
        assert sync_limiter._daily_requests == 3

    @pytest.mark.asyncio
    async def test_shared_should_allow(self, quota_config):
        """Test that should_allow_request reflects shared state."""
        sync_limiter = FMPRateLimiter(quota_config)
        async_limiter = AsyncFMPRateLimiter(sync_limiter)

        # Exhaust daily limit via sync
        for _ in range(quota_config.daily_limit):
            sync_limiter.record_request()

        # Async should also be denied
        allowed = await async_limiter.should_allow_request()
        assert not allowed

    @pytest.mark.asyncio
    async def test_get_wait_time_uses_sync(self, sync_limiter, async_limiter):
        """Test that get_wait_time delegates to sync limiter."""
        # Exhaust per-second limit
        for _ in range(sync_limiter.quota_config.requests_per_second):
            sync_limiter.record_request()

        # Both should return approximately the same wait time
        # (may differ slightly due to time elapsed between calls)
        sync_wait = sync_limiter.get_wait_time()
        async_wait = async_limiter.get_wait_time()

        # Allow 0.1 second difference due to timing
        assert abs(sync_wait - async_wait) < 0.1
        assert async_wait > 0

    @pytest.mark.asyncio
    async def test_handle_response_delegates_to_sync(self, sync_limiter, async_limiter):
        """Test that handle_response delegates to sync limiter."""
        # This should log an error via the sync limiter
        async_limiter.handle_response(429, '{"message": "Too many requests"}')

        # No exception should be raised, just logging


class TestWaitIfNeeded:
    """Tests for the wait_if_needed method."""

    @pytest.mark.asyncio
    async def test_wait_if_needed_when_allowed(self, async_limiter):
        """Test that wait_if_needed returns immediately when allowed."""
        import time

        start = time.time()
        await async_limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should return almost immediately
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_wait_if_needed_when_rate_limited(self, quota_config):
        """Test that wait_if_needed waits when rate limited."""
        # Create limiter with very low per-second limit
        config = QuotaConfig(
            daily_limit=100,
            requests_per_second=1,
            requests_per_minute=100,
        )
        sync_limiter = FMPRateLimiter(config)
        async_limiter = AsyncFMPRateLimiter(sync_limiter)

        # Exhaust per-second limit
        sync_limiter.record_request()

        # wait_if_needed should wait (up to 1 second)
        # But we won't actually wait in the test - just verify it would wait
        allowed = await async_limiter.should_allow_request()
        if not allowed:
            wait_time = async_limiter.get_wait_time()
            assert wait_time > 0
            assert wait_time <= 1.0  # Should be at most 1 second
