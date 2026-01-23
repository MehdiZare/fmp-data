# tests/unit/test_rate_limit.py
from datetime import date, datetime, timedelta
import time
from unittest.mock import patch

import pytest

from fmp_data.rate_limit import FMPRateLimiter, QuotaConfig


class TestQuotaConfig:
    """Test QuotaConfig functionality"""

    def test_basic_initialization(self):
        """Test basic quota config initialization"""
        config = QuotaConfig(
            daily_limit=1000, requests_per_second=10, requests_per_minute=300
        )

        assert config.daily_limit == 1000
        assert config.requests_per_second == 10
        assert config.requests_per_minute == 300

    def test_default_values(self):
        """Test default values in quota config"""
        config = QuotaConfig(daily_limit=500)

        assert config.daily_limit == 500
        assert config.requests_per_second == 10  # Default
        assert config.requests_per_minute == 300  # Default

    def test_custom_values(self):
        """Test custom quota config values"""
        config = QuotaConfig(
            daily_limit=2000, requests_per_second=20, requests_per_minute=1200
        )

        assert config.daily_limit == 2000
        assert config.requests_per_second == 20
        assert config.requests_per_minute == 1200

    def test_zero_values(self):
        """Test quota config with zero values"""
        config = QuotaConfig(
            daily_limit=0, requests_per_second=0, requests_per_minute=0
        )

        assert config.daily_limit == 0
        assert config.requests_per_second == 0
        assert config.requests_per_minute == 0


class TestFMPRateLimiterInitialization:
    """Test FMPRateLimiter initialization"""

    def test_basic_initialization(self):
        """Test basic rate limiter initialization"""
        config = QuotaConfig(
            daily_limit=100, requests_per_second=5, requests_per_minute=60
        )

        limiter = FMPRateLimiter(config)

        assert limiter.quota_config is config
        assert limiter._daily_requests == 0
        assert limiter._reset_date == datetime.now().date()
        assert limiter._minute_requests == []
        assert limiter._second_requests == []

    def test_initialization_sets_current_date(self):
        """Test initialization sets current date for reset"""
        config = QuotaConfig(daily_limit=100)

        with patch("fmp_data.rate_limit.datetime") as mock_datetime:
            mock_date = date(2023, 12, 25)
            mock_datetime.now.return_value.date.return_value = mock_date

            limiter = FMPRateLimiter(config)
            assert limiter._reset_date == mock_date

    def test_initialization_with_different_configs(self):
        """Test initialization with various config values"""
        configs = [
            QuotaConfig(daily_limit=50, requests_per_second=2, requests_per_minute=30),
            QuotaConfig(
                daily_limit=1000, requests_per_second=50, requests_per_minute=3000
            ),
            QuotaConfig(daily_limit=1, requests_per_second=1, requests_per_minute=1),
        ]

        for config in configs:
            limiter = FMPRateLimiter(config)
            assert limiter.quota_config.daily_limit == config.daily_limit
            assert (
                limiter.quota_config.requests_per_second == config.requests_per_second
            )
            assert (
                limiter.quota_config.requests_per_minute == config.requests_per_minute
            )


class TestFMPRateLimiterCleanup:
    """Test cleanup functionality"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(QuotaConfig(daily_limit=100))

    def test_cleanup_old_minute_requests(self, limiter):
        """Test cleanup of old minute requests"""
        now = datetime.now()
        old_time = now - timedelta(minutes=2)
        recent_time = now - timedelta(seconds=30)

        limiter._minute_requests = [old_time, recent_time, now]
        limiter._cleanup_old_requests()

        # Only recent and current requests should remain
        assert len(limiter._minute_requests) == 2
        assert old_time not in limiter._minute_requests
        assert recent_time in limiter._minute_requests
        assert now in limiter._minute_requests

    def test_cleanup_old_second_requests(self, limiter):
        """Test cleanup of old second requests"""
        now = datetime.now()
        old_time = now - timedelta(seconds=2)
        recent_time = now - timedelta(milliseconds=500)

        limiter._second_requests = [old_time, recent_time, now]
        limiter._cleanup_old_requests()

        # Only recent and current requests should remain
        assert len(limiter._second_requests) == 2
        assert old_time not in limiter._second_requests
        assert recent_time in limiter._second_requests

    def test_cleanup_empty_lists(self, limiter):
        """Test cleanup with empty request lists"""
        limiter._minute_requests = []
        limiter._second_requests = []

        limiter._cleanup_old_requests()

        assert limiter._minute_requests == []
        assert limiter._second_requests == []

    def test_cleanup_all_old_requests(self, limiter):
        """Test cleanup when all requests are old"""
        old_time = datetime.now() - timedelta(hours=1)

        limiter._minute_requests = [old_time, old_time, old_time]
        limiter._second_requests = [old_time, old_time]

        limiter._cleanup_old_requests()

        assert limiter._minute_requests == []
        assert limiter._second_requests == []


class TestFMPRateLimiterShouldAllowRequest:
    """Test request allowance logic"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(
            QuotaConfig(daily_limit=10, requests_per_second=2, requests_per_minute=5)
        )

    def test_should_allow_request_initial_state(self, limiter):
        """Test request is allowed in initial state"""
        assert limiter.should_allow_request() is True

    def test_should_allow_request_daily_limit_exceeded(self, limiter):
        """Test request denied when daily limit exceeded"""
        limiter._daily_requests = 10  # At limit

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            assert limiter.should_allow_request() is False
            mock_logger.warning.assert_called_with("Daily quota exceeded")

    def test_should_allow_request_daily_limit_exceeded_by_one(self, limiter):
        """Test request denied when daily limit exceeded by one"""
        limiter._daily_requests = 11  # Over limit

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            assert limiter.should_allow_request() is False
            mock_logger.warning.assert_called_with("Daily quota exceeded")

    def test_should_allow_request_minute_limit_exceeded(self, limiter):
        """Test request denied when per-minute limit exceeded"""
        now = datetime.now()
        limiter._minute_requests = [now for _ in range(5)]  # At limit

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            assert limiter.should_allow_request() is False
            mock_logger.warning.assert_called_with("Per-minute rate limit exceeded")

    def test_should_allow_request_second_limit_exceeded(self, limiter):
        """Test request denied when per-second limit exceeded"""
        now = datetime.now()
        limiter._second_requests = [now for _ in range(2)]  # At limit

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            assert limiter.should_allow_request() is False
            mock_logger.warning.assert_called_with("Per-second rate limit exceeded")

    def test_should_allow_request_multiple_limits_exceeded(self, limiter):
        """Test request denied when multiple limits exceeded"""
        now = datetime.now()
        limiter._daily_requests = 10
        limiter._minute_requests = [now for _ in range(5)]
        limiter._second_requests = [now for _ in range(2)]

        # Should check daily limit first
        with patch("fmp_data.rate_limit.logger") as mock_logger:
            assert limiter.should_allow_request() is False
            mock_logger.warning.assert_called_with("Daily quota exceeded")

    def test_should_allow_request_after_cleanup(self, limiter):
        """Test request allowed after cleanup removes old requests"""
        old_time = datetime.now() - timedelta(minutes=2)

        # Fill with old requests
        limiter._minute_requests = [old_time for _ in range(5)]
        limiter._second_requests = [old_time for _ in range(2)]

        # Should be allowed after cleanup
        assert limiter.should_allow_request() is True

    def test_should_allow_request_daily_reset(self, limiter):
        """Test request allowed after daily reset"""
        # Set up yesterday's state
        yesterday = datetime.now().date() - timedelta(days=1)
        limiter._daily_requests = 10  # At limit
        limiter._reset_date = yesterday

        with patch("fmp_data.rate_limit.datetime") as mock_datetime:
            today = datetime.now().date()
            mock_datetime.now.return_value.date.return_value = today

            assert limiter.should_allow_request() is True
            assert limiter._daily_requests == 0
            assert limiter._reset_date == today

    def test_should_allow_request_edge_case_limits(self, limiter):
        """Test request allowance at edge cases"""
        # Just under limits
        limiter._daily_requests = 9  # Under limit
        now = datetime.now()
        limiter._minute_requests = [now for _ in range(4)]  # Under limit
        limiter._second_requests = [now for _ in range(1)]  # Under limit

        assert limiter.should_allow_request() is True


class TestFMPRateLimiterRecordRequest:
    """Test request recording functionality"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(QuotaConfig(daily_limit=100))

    def test_record_request_increments_counters(self, limiter):
        """Test record_request increments all counters"""
        initial_daily = limiter._daily_requests
        initial_minute_count = len(limiter._minute_requests)
        initial_second_count = len(limiter._second_requests)

        limiter.record_request()

        assert limiter._daily_requests == initial_daily + 1
        assert len(limiter._minute_requests) == initial_minute_count + 1
        assert len(limiter._second_requests) == initial_second_count + 1

    def test_record_request_adds_current_timestamp(self, limiter):
        """Test record_request adds current timestamp"""
        before_time = datetime.now()
        limiter.record_request()
        after_time = datetime.now()

        # Check that timestamp is within reasonable range
        recorded_time = limiter._minute_requests[-1]
        assert before_time <= recorded_time <= after_time

        recorded_time = limiter._second_requests[-1]
        assert before_time <= recorded_time <= after_time

    def test_record_request_multiple_calls(self, limiter):
        """Test multiple record_request calls"""
        for i in range(5):
            limiter.record_request()

            assert limiter._daily_requests == i + 1
            assert len(limiter._minute_requests) == i + 1
            assert len(limiter._second_requests) == i + 1

    def test_record_request_preserves_existing_requests(self, limiter):
        """Test record_request preserves existing request records"""
        # Add some existing requests
        existing_time = datetime.now() - timedelta(seconds=30)
        limiter._minute_requests.append(existing_time)
        limiter._second_requests.append(existing_time)
        limiter._daily_requests = 3

        limiter.record_request()

        assert limiter._daily_requests == 4
        assert len(limiter._minute_requests) == 2
        assert len(limiter._second_requests) == 2
        assert existing_time in limiter._minute_requests
        assert existing_time in limiter._second_requests


class TestFMPRateLimiterHandleResponse:
    """Test response handling functionality"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(QuotaConfig(daily_limit=100))

    def test_handle_response_normal_status(self, limiter):
        """Test handle_response with normal status codes"""
        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(200, None)
            limiter.handle_response(201, '{"data": "success"}')
            limiter.handle_response(404, '{"error": "not found"}')

            # Should not log anything for non-429 responses
            mock_logger.error.assert_not_called()

    def test_handle_response_rate_limit_with_valid_json(self, limiter):
        """Test handle_response with 429 and valid JSON"""
        response_body = '{"message": "Rate limit exceeded - too many requests"}'

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(429, response_body)

            mock_logger.error.assert_called_once_with(
                "Rate limit exceeded: Rate limit exceeded - too many requests"
            )

    def test_handle_response_rate_limit_with_invalid_json(self, limiter):
        """Test handle_response with 429 and invalid JSON"""
        response_body = "Invalid JSON response"

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(429, response_body)

            mock_logger.error.assert_called_once_with(
                "Rate limit exceeded (no details available)"
            )

    def test_handle_response_rate_limit_with_none_body(self, limiter):
        """Test handle_response with 429 and None body"""
        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(429, None)

            mock_logger.error.assert_called_once_with("Rate limit exceeded: ")

    def test_handle_response_rate_limit_with_empty_message(self, limiter):
        """Test handle_response with 429 and empty message"""
        response_body = '{"other_field": "value"}'

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(429, response_body)

            mock_logger.error.assert_called_once_with("Rate limit exceeded: ")

    def test_handle_response_rate_limit_with_nested_message(self, limiter):
        """Test handle_response with 429 and nested JSON structure"""
        response_body = '{"error": {"message": "Nested rate limit message"}}'

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.handle_response(429, response_body)

            # Should only look for top-level message
            mock_logger.error.assert_called_once_with("Rate limit exceeded: ")

    def test_handle_response_rate_limit_with_different_structures(self, limiter):
        """Test handle_response with various JSON structures"""
        test_cases = [
            ('{"message": "Custom message"}', "Custom message"),
            ('{"msg": "Different field"}', ""),  # Wrong field name
            ('{"message": ""}', ""),  # Empty message
            ('{"message": null}', ""),  # Null message
        ]

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            for response_body, expected_message in test_cases:
                mock_logger.reset_mock()
                limiter.handle_response(429, response_body)

                mock_logger.error.assert_called_once_with(
                    f"Rate limit exceeded: {expected_message}"
                )


class TestFMPRateLimiterRetryAfter:
    """Test retry-after header parsing"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(QuotaConfig(daily_limit=100))

    def test_retry_after_seconds_header(self, limiter):
        """Use Retry-After seconds when provided."""
        headers = {"Retry-After": "15"}

        assert limiter.get_retry_after(headers) == 15

    def test_retry_after_prefers_retry_after_over_reset(self, limiter):
        """Retry-After should win over reset headers."""
        headers = {"Retry-After": "10", "RateLimit-Reset": "20"}

        assert limiter.get_retry_after(headers) == 10

    def test_retry_after_from_reset_seconds(self, limiter):
        """Use RateLimit-Reset seconds when Retry-After is absent."""
        headers = {"RateLimit-Reset": "12"}

        assert limiter.get_retry_after(headers) == 12

    def test_retry_after_from_reset_epoch(self, limiter):
        """Parse RateLimit-Reset epoch timestamps."""
        reset_epoch = str(int(time.time()) + 5)
        headers = {"RateLimit-Reset": reset_epoch}

        retry_after = limiter.get_retry_after(headers)

        assert retry_after is not None
        assert 0.0 < retry_after <= 5.0


class TestFMPRateLimiterGetWaitTime:
    """Test wait time calculation functionality"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(
            QuotaConfig(daily_limit=10, requests_per_second=2, requests_per_minute=5)
        )

    def test_get_wait_time_no_limits_exceeded(self, limiter):
        """Test wait time is zero when no limits exceeded"""
        assert limiter.get_wait_time() == 0.0

    def test_get_wait_time_per_second_limit(self, limiter):
        """Test wait time calculation for per-second limit"""
        now = datetime.now()
        old_request = now - timedelta(milliseconds=500)  # 0.5 seconds ago

        limiter._second_requests = [old_request, now]  # At limit

        wait_time = limiter.get_wait_time()

        # Should wait until 1 second after oldest request
        expected_wait = (old_request + timedelta(seconds=1) - now).total_seconds()
        assert abs(wait_time - expected_wait) < 0.1  # Allow small timing differences

    def test_get_wait_time_per_minute_limit(self, limiter):
        """Test wait time calculation for per-minute limit"""
        now = datetime.now()
        old_request = now - timedelta(seconds=30)  # 30 seconds ago

        limiter._minute_requests = [old_request] + [now for _ in range(4)]  # At limit

        wait_time = limiter.get_wait_time()

        # Should wait until 1 minute after oldest request
        expected_wait = (old_request + timedelta(minutes=1) - now).total_seconds()
        assert abs(wait_time - expected_wait) < 1.0

    def test_get_wait_time_daily_limit(self, limiter):
        """Test wait time calculation for daily limit"""
        limiter._daily_requests = 10  # At daily limit

        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        wait_time = limiter.get_wait_time()
        expected_wait = (tomorrow - now).total_seconds()

        assert abs(wait_time - expected_wait) < 1.0

    def test_get_wait_time_multiple_limits_returns_max(self, limiter):
        """Test wait time returns maximum when multiple limits exceeded"""
        now = datetime.now()

        # Set up multiple limit violations
        limiter._daily_requests = 10  # Daily limit
        limiter._second_requests = [
            now - timedelta(milliseconds=100),
            now,
        ]  # Second limit
        limiter._minute_requests = [now - timedelta(seconds=30)] + [
            now for _ in range(4)
        ]  # Minute limit

        wait_time = limiter.get_wait_time()

        # Daily wait time should be much longer than others
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        expected_daily_wait = (tomorrow - now).total_seconds()

        assert (
            wait_time >= expected_daily_wait - 1.0
        )  # Should be close to daily wait time

    def test_get_wait_time_edge_cases(self, limiter):
        """Test wait time calculation edge cases"""
        now = datetime.now()

        # Test with request exactly at limit boundaries
        one_second_ago = now - timedelta(seconds=1)
        one_minute_ago = now - timedelta(minutes=1)

        limiter._second_requests = [one_second_ago, now]
        wait_time = limiter.get_wait_time()
        assert wait_time < 0.1  # Should be very small

        limiter._second_requests = []
        limiter._minute_requests = [one_minute_ago, now, now, now, now]
        wait_time = limiter.get_wait_time()
        assert wait_time < 1.0  # Should be very small

    def test_get_wait_time_precision(self, limiter):
        """Test wait time calculation precision"""
        now = datetime.now()
        recent_request = now - timedelta(milliseconds=100)  # Very recent

        limiter._second_requests = [recent_request, now]

        wait_time = limiter.get_wait_time()

        # Should be close to 0.9 seconds (1.0 - 0.1)
        assert 0.8 <= wait_time <= 1.0


class TestFMPRateLimiterLogStatus:
    """Test status logging functionality"""

    @pytest.fixture
    def limiter(self):
        return FMPRateLimiter(
            QuotaConfig(daily_limit=100, requests_per_second=10, requests_per_minute=60)
        )

    def test_log_status_empty_state(self, limiter):
        """Test status logging in empty state"""
        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.log_status()

            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]

            assert "Daily: 0/100" in log_message
            assert "Per-minute: 0/60" in log_message
            assert "Per-second: 0/10" in log_message

    def test_log_status_with_requests(self, limiter):
        """Test status logging with some requests recorded"""
        now = datetime.now()

        limiter._daily_requests = 25
        limiter._minute_requests = [now for _ in range(15)]
        limiter._second_requests = [now for _ in range(3)]

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.log_status()

            log_message = mock_logger.info.call_args[0][0]

            assert "Daily: 25/100" in log_message
            assert "Per-minute: 15/60" in log_message
            assert "Per-second: 3/10" in log_message

    def test_log_status_at_limits(self, limiter):
        """Test status logging when at limits"""
        now = datetime.now()

        limiter._daily_requests = 100
        limiter._minute_requests = [now for _ in range(60)]
        limiter._second_requests = [now for _ in range(10)]

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.log_status()

            log_message = mock_logger.info.call_args[0][0]

            assert "Daily: 100/100" in log_message
            assert "Per-minute: 60/60" in log_message
            assert "Per-second: 10/10" in log_message

    def test_log_status_calls_cleanup(self, limiter):
        """Test that log_status calls cleanup before logging"""
        old_time = datetime.now() - timedelta(hours=1)

        limiter._minute_requests = [old_time, old_time]
        limiter._second_requests = [old_time, old_time, old_time]

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.log_status()

            # After cleanup, old requests should be gone
            log_message = mock_logger.info.call_args[0][0]
            assert "Per-minute: 0/60" in log_message
            assert "Per-second: 0/10" in log_message

    def test_log_status_message_format(self, limiter):
        """Test that log_status message format is correct"""
        limiter._daily_requests = 42

        with patch("fmp_data.rate_limit.logger") as mock_logger:
            limiter.log_status()

            log_message = mock_logger.info.call_args[0][0]

            # Check message structure
            assert log_message.startswith("Rate Limits: Daily:")
            assert "Per-minute:" in log_message
            assert "Per-second:" in log_message


class TestFMPRateLimiterIntegration:
    """Test rate limiter integration scenarios"""

    def test_full_request_cycle(self):
        """Test complete request cycle with rate limiting"""
        limiter = FMPRateLimiter(
            QuotaConfig(
                daily_limit=5,
                requests_per_second=10,  # High enough to not interfere
                requests_per_minute=2,  # This will be the limiting factor
            )
        )

        # First request should be allowed
        assert limiter.should_allow_request() is True
        limiter.record_request()

        # Second request should be allowed (under per-minute limit)
        assert limiter.should_allow_request() is True
        limiter.record_request()

        # Third request should be blocked by per-minute limit
        with patch("fmp_data.rate_limit.logger"):
            assert limiter.should_allow_request() is False

    def test_time_based_recovery(self):
        """Test that rate limits recover over time"""
        limiter = FMPRateLimiter(
            QuotaConfig(daily_limit=10, requests_per_second=1, requests_per_minute=2)
        )

        # Fill up per-second limit
        now = datetime.now()
        limiter._second_requests = [now]

        # Should be blocked
        with patch("fmp_data.rate_limit.logger"):
            assert limiter.should_allow_request() is False

        # Simulate time passing
        future_time = now + timedelta(seconds=2)
        with patch("fmp_data.rate_limit.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_time

            # Should be allowed after time passes
            assert limiter.should_allow_request() is True

    def test_daily_reset_functionality(self):
        """Test daily reset functionality"""
        limiter = FMPRateLimiter(QuotaConfig(daily_limit=5))

        # Max out daily requests
        limiter._daily_requests = 5
        yesterday = datetime.now().date() - timedelta(days=1)
        limiter._reset_date = yesterday

        # After daily reset check, should be allowed
        today = datetime.now().date()
        with patch("fmp_data.rate_limit.datetime") as mock_datetime:
            mock_datetime.now.return_value.date.return_value = today

            # Should be allowed after reset
            assert limiter.should_allow_request() is True
            assert limiter._daily_requests == 0
            assert limiter._reset_date == today

    def test_realistic_usage_pattern(self):
        """Test realistic API usage pattern"""
        limiter = FMPRateLimiter(
            QuotaConfig(daily_limit=250, requests_per_second=5, requests_per_minute=300)
        )

        # Simulate burst of requests
        for _ in range(4):
            assert limiter.should_allow_request() is True
            limiter.record_request()

        # 5th request should be allowed (under per-second limit)
        assert limiter.should_allow_request() is True
        limiter.record_request()

        # 6th request should be blocked by per-second limit
        with patch("fmp_data.rate_limit.logger"):
            assert limiter.should_allow_request() is False

        # Check daily count is correct
        assert limiter._daily_requests == 5

    def test_error_handling_edge_cases(self):
        """Test error handling in edge cases"""
        limiter = FMPRateLimiter(QuotaConfig(daily_limit=1))

        # Test with malformed response
        with patch("fmp_data.rate_limit.logger"):
            limiter.handle_response(429, "{broken json")

        # Test with extremely old timestamps
        ancient_time = datetime.now() - timedelta(days=365)
        limiter._minute_requests = [ancient_time]
        limiter._second_requests = [ancient_time]

        limiter._cleanup_old_requests()
        assert len(limiter._minute_requests) == 0
        assert len(limiter._second_requests) == 0
