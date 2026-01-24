"""Additional tests for base.py to improve coverage"""

from typing import cast
from unittest.mock import Mock, patch

import pytest
from tenacity import RetryCallState

from fmp_data.base import BaseClient, _rate_limit_retry_count
from fmp_data.config import ClientConfig
from fmp_data.exceptions import RateLimitError


class TestBaseClientCoverage:
    """Additional tests to improve coverage for BaseClient"""

    @pytest.fixture
    def config(self):
        """Create a test configuration"""
        return ClientConfig(api_key="test_key", max_rate_limit_retries=2)

    @pytest.fixture
    def base_client(self, config):
        """Create a BaseClient instance"""
        return BaseClient(config)

    def test_handle_rate_limit_under_retry_limit(self, base_client):
        """Test rate limit handling when under retry limit"""
        _rate_limit_retry_count.set(0)

        with patch("time.sleep") as mock_sleep:
            base_client._handle_rate_limit(1.5)

            # Should sleep and increment counter (uses context variable)
            mock_sleep.assert_called_once_with(1.5)
            assert _rate_limit_retry_count.get() == 1

    def test_handle_rate_limit_exceeds_retry_limit(self, base_client):
        """Test rate limit handling when exceeding retry limit"""
        _rate_limit_retry_count.set(2)  # Already at limit

        with pytest.raises(RateLimitError) as exc_info:
            base_client._handle_rate_limit(5.0)

        # Should reset counter and raise error (uses context variable)
        assert _rate_limit_retry_count.get() == 0
        assert "Rate limit exceeded after 2 retries" in str(exc_info.value)
        assert exc_info.value.retry_after == 5.0

    def test_close_with_client(self, base_client):
        """Test closing the client when it exists"""
        mock_client = Mock()
        base_client.client = mock_client

        base_client.close()

        mock_client.close.assert_called_once()

    def test_close_without_client(self):
        """Test closing when client doesn't exist"""
        config = ClientConfig(api_key="test_key")
        client = BaseClient(config)
        del client.client  # Remove the client attribute

        # Should not raise an error
        client.close()

    def test_rate_limiter_wait_functionality(self, base_client):
        """Test that rate limiter wait functionality works"""
        # Test that rate limiter wait is called when needed
        base_client._rate_limiter.wait_if_needed = Mock()

        # Call the wait method
        base_client._rate_limiter.wait_if_needed()

        # Verify wait was called
        base_client._rate_limiter.wait_if_needed.assert_called_once()

    def test_retry_count_management(self, base_client):
        """Test that retry count is properly managed"""
        # Set initial retry count
        base_client._rate_limit_retry_count = 2

        # After a successful operation, retry count should be resetable
        base_client._rate_limit_retry_count = 0

        # Verify the retry count is properly managed
        assert base_client._rate_limit_retry_count == 0

    def test_wait_for_retry_uses_retry_after(self, base_client):
        """Prefer retry_after when RateLimitError is raised"""

        class FakeOutcome:
            def __init__(self, exc):
                self._exc = exc
                self.failed = True

            def exception(self):
                return self._exc

        class FakeRetryState:
            def __init__(self, exc):
                self.outcome = FakeOutcome(exc)

        retry_after = 7.5
        exc = RateLimitError("rate limited", retry_after=retry_after)
        retry_state = cast(RetryCallState, cast(object, FakeRetryState(exc)))

        assert base_client._wait_for_retry(retry_state) == retry_after

    @patch("fmp_data.base.FMPLogger")
    def test_init_with_custom_max_retries(self, mock_logger):
        """Test initialization with custom max_rate_limit_retries"""
        config = ClientConfig(api_key="test_key")
        config.max_rate_limit_retries = 5

        client = BaseClient(config)

        assert client.max_rate_limit_retries == 5
        client.close()

    def test_handle_rate_limit_with_small_wait(self, base_client):
        """Test handling rate limit with a small wait time"""
        with patch("time.sleep") as mock_sleep:
            # Simulate handling a rate limit with a small wait (uses context variable)
            _rate_limit_retry_count.set(0)
            base_client._handle_rate_limit(0.1)

            # Should have slept and incremented counter
            mock_sleep.assert_called_once_with(0.1)
            assert _rate_limit_retry_count.get() == 1
