"""Additional tests for rate_limit module to improve coverage"""

from datetime import datetime, timedelta
import json
from unittest.mock import patch

import pytest

from fmp_data.rate_limit import FMPRateLimiter, QuotaConfig


class TestFMPRateLimiterCoverage:
    """Additional tests to improve coverage for FMPRateLimiter"""

    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter with standard quota"""
        config = QuotaConfig(
            daily_limit=100, requests_per_second=5, requests_per_minute=60
        )
        return FMPRateLimiter(config)

    def test_cleanup_old_requests(self, rate_limiter):
        """Test cleanup of old request timestamps"""
        now = datetime.now()

        # Add old and new requests to trackers
        old_time = now - timedelta(minutes=2)
        recent_time = now - timedelta(seconds=30)

        rate_limiter._minute_requests = [old_time, recent_time, now]
        rate_limiter._second_requests = [old_time, recent_time, now]

        # Call cleanup
        rate_limiter._cleanup_old_requests()

        # Only recent requests should remain in minute tracker
        assert len(rate_limiter._minute_requests) == 2
        assert old_time not in rate_limiter._minute_requests

        # Only the most recent request should remain in second tracker
        assert len(rate_limiter._second_requests) == 1
        assert rate_limiter._second_requests[0] == now

    def test_should_allow_request_daily_limit(self, rate_limiter):
        """Test request blocking when daily limit is exceeded"""
        # Set daily requests to limit
        rate_limiter._daily_requests = 100

        # Should not allow request
        assert not rate_limiter.should_allow_request()

    def test_should_allow_request_minute_limit(self, rate_limiter):
        """Test request blocking when minute limit is exceeded"""
        now = datetime.now()

        # Fill up minute requests
        rate_limiter._minute_requests = [now] * 60

        # Should not allow request
        assert not rate_limiter.should_allow_request()

    def test_should_allow_request_second_limit(self, rate_limiter):
        """Test request blocking when second limit is exceeded"""
        now = datetime.now()

        # Fill up second requests
        rate_limiter._second_requests = [now] * 5

        # Should not allow request
        assert not rate_limiter.should_allow_request()

    def test_should_allow_request_date_reset(self, rate_limiter):
        """Test daily counter reset on new day"""
        # Set yesterday's date and max out requests
        yesterday = datetime.now().date() - timedelta(days=1)
        rate_limiter._reset_date = yesterday
        rate_limiter._daily_requests = 100

        # Should allow request (new day resets counter)
        assert rate_limiter.should_allow_request()
        assert rate_limiter._daily_requests == 0
        assert rate_limiter._reset_date == datetime.now().date()

    def test_record_request(self, rate_limiter):
        """Test recording a new request"""
        initial_daily = rate_limiter._daily_requests
        initial_minute = len(rate_limiter._minute_requests)
        initial_second = len(rate_limiter._second_requests)

        rate_limiter.record_request()

        assert rate_limiter._daily_requests == initial_daily + 1
        assert len(rate_limiter._minute_requests) == initial_minute + 1
        assert len(rate_limiter._second_requests) == initial_second + 1

    def test_handle_response_429_with_json(self, rate_limiter):
        """Test handling 429 response with JSON error message"""
        response_body = json.dumps(
            {"message": "Rate limit exceeded: too many requests"}
        )

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            rate_limiter.handle_response(429, response_body)
            mock_logger.error.assert_called_with(
                "Rate limit exceeded: Rate limit exceeded: too many requests"
            )

    def test_handle_response_429_with_invalid_json(self, rate_limiter):
        """Test handling 429 response with invalid JSON"""
        response_body = "Invalid JSON response"

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            rate_limiter.handle_response(429, response_body)
            mock_logger.error.assert_called_with(
                "Rate limit exceeded (no details available)"
            )

    def test_handle_response_429_no_body(self, rate_limiter):
        """Test handling 429 response without body"""
        with patch("fmp_data.rate_limit.logger") as mock_logger:
            rate_limiter.handle_response(429, None)
            mock_logger.error.assert_called_with("Rate limit exceeded: ")

    def test_handle_response_non_429(self, rate_limiter):
        """Test handling non-429 responses"""
        # Should not raise any errors for non-429 status
        rate_limiter.handle_response(200, None)
        rate_limiter.handle_response(400, None)
        rate_limiter.handle_response(500, None)

    def test_get_wait_time_no_limits(self, rate_limiter):
        """Test wait time when no limits are exceeded"""
        wait_time = rate_limiter.get_wait_time()
        assert wait_time == 0.0

    def test_get_wait_time_second_limit(self, rate_limiter):
        """Test wait time when second limit is exceeded"""
        now = datetime.now()
        rate_limiter._second_requests = [now - timedelta(milliseconds=500)] * 5

        wait_time = rate_limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 1.0

    def test_get_wait_time_minute_limit(self, rate_limiter):
        """Test wait time when minute limit is exceeded"""
        now = datetime.now()
        rate_limiter._minute_requests = [now - timedelta(seconds=30)] * 60

        wait_time = rate_limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 30.0

    def test_get_wait_time_daily_limit(self, rate_limiter):
        """Test wait time when daily limit is exceeded"""
        rate_limiter._daily_requests = 100

        wait_time = rate_limiter.get_wait_time()
        assert wait_time > 0
        # Should wait until tomorrow
        assert wait_time <= 86400  # Max 24 hours

    def test_get_wait_time_multiple_limits(self, rate_limiter):
        """Test wait time when multiple limits are exceeded"""
        now = datetime.now()

        # Exceed all limits
        rate_limiter._daily_requests = 100
        rate_limiter._minute_requests = [now] * 60
        rate_limiter._second_requests = [now] * 5

        wait_time = rate_limiter.get_wait_time()
        assert wait_time > 0

    def test_log_status(self, rate_limiter):
        """Test logging rate limit status"""
        # Add some requests
        rate_limiter._daily_requests = 50
        rate_limiter._minute_requests = [datetime.now()] * 10
        rate_limiter._second_requests = [datetime.now()] * 2

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            rate_limiter.log_status()

            # Check that info was logged with correct format
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "Daily: 50/100" in call_args
            assert "Per-minute: 10/60" in call_args
            assert "Per-second: 2/5" in call_args

    def test_wait_time_negative_protection(self, rate_limiter):
        """Test that wait time is never negative"""
        # Set old timestamps that would result in negative wait time
        old_time = datetime.now() - timedelta(hours=1)
        rate_limiter._second_requests = [old_time] * 5
        rate_limiter._minute_requests = [old_time] * 60

        wait_time = rate_limiter.get_wait_time()
        assert wait_time == 0.0  # Should be 0, not negative
