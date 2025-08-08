"""Additional tests for base.py to improve coverage"""

from unittest.mock import Mock, patch

import httpx
import pytest

from fmp_data.base import BaseClient
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
        base_client._rate_limit_retry_count = 0

        with patch("time.sleep") as mock_sleep:
            base_client._handle_rate_limit(1.5)

            # Should sleep and increment counter
            mock_sleep.assert_called_once_with(1.5)
            assert base_client._rate_limit_retry_count == 1

    def test_handle_rate_limit_exceeds_retry_limit(self, base_client):
        """Test rate limit handling when exceeding retry limit"""
        base_client._rate_limit_retry_count = 2  # Already at limit

        with pytest.raises(RateLimitError) as exc_info:
            base_client._handle_rate_limit(5.0)

        # Should reset counter and raise error
        assert base_client._rate_limit_retry_count == 0
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

    def test_request_with_rate_limit_wait(self, base_client):
        """Test request handling when rate limit requires waiting"""
        base_client._rate_limiter.should_allow_request = Mock(return_value=False)
        base_client._rate_limiter.get_wait_time = Mock(return_value=0.1)

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        base_client.client.request = Mock(return_value=mock_response)

        with patch("time.sleep") as mock_sleep:
            result = base_client.request("GET", "/test")

            # Should wait for rate limit
            mock_sleep.assert_called_with(0.1)
            assert result == {"data": "test"}

    def test_request_resets_retry_count_on_success(self, base_client):
        """Test that successful request resets rate limit retry count"""
        base_client._rate_limit_retry_count = 2

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        base_client.client.request = Mock(return_value=mock_response)
        base_client._rate_limiter.should_allow_request = Mock(return_value=True)

        base_client.request("GET", "/test")

        # Should reset retry count on success
        assert base_client._rate_limit_retry_count == 0

    @patch("fmp_data.base.FMPLogger")
    def test_init_with_custom_max_retries(self, mock_logger):
        """Test initialization with custom max_rate_limit_retries"""
        config = ClientConfig(api_key="test_key")
        config.max_rate_limit_retries = 5

        client = BaseClient(config)

        assert client.max_rate_limit_retries == 5
        client.close()

    def test_request_handles_429_with_wait(self, base_client):
        """Test handling 429 response with rate limit wait"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"

        # First call returns 429, second call succeeds
        success_response = Mock(spec=httpx.Response)
        success_response.status_code = 200
        success_response.json.return_value = {"data": "success"}

        base_client.client.request = Mock(side_effect=[mock_response, success_response])
        base_client._rate_limiter.should_allow_request = Mock(return_value=True)
        base_client._rate_limiter.get_wait_time = Mock(return_value=0.1)

        with patch("time.sleep") as mock_sleep:
            result = base_client.request("GET", "/test")

            # Should handle 429 and retry
            assert mock_sleep.called
            assert result == {"data": "success"}
            assert base_client.client.request.call_count == 2
