from datetime import datetime, timedelta

import pytest

from fmp_data.rate_limit import FMPRateLimiter, QuotaConfig


@pytest.fixture
def rate_limiter():
    return FMPRateLimiter(
        QuotaConfig(daily_limit=100, requests_per_second=10, requests_per_minute=60)
    )


def test_quota_config():
    """Test quota configuration"""
    config = QuotaConfig(
        daily_limit=1000, requests_per_second=10, requests_per_minute=300
    )
    assert config.daily_limit == 1000
    assert config.requests_per_second == 10
    assert config.requests_per_minute == 300


def test_rate_limit_initialization(rate_limiter):
    """Test rate limiter initialization"""
    assert rate_limiter.quota_config.daily_limit == 100
    assert rate_limiter.quota_config.requests_per_second == 10
    assert rate_limiter.quota_config.requests_per_minute == 60
    assert rate_limiter._daily_requests == 0


def test_should_allow_request(rate_limiter):
    """Test request allowance logic"""
    # Initial state should allow requests
    assert rate_limiter.should_allow_request() is True

    # Simulate hitting the per-second limit
    rate_limiter._second_requests = [datetime.now() for _ in range(10)]
    assert rate_limiter.should_allow_request() is False

    # Simulate hitting the per-minute limit
    rate_limiter._second_requests = []
    rate_limiter._minute_requests = [datetime.now() for _ in range(60)]
    assert rate_limiter.should_allow_request() is False

    # Simulate hitting the daily limit
    rate_limiter._minute_requests = []
    rate_limiter._daily_requests = 100
    assert rate_limiter.should_allow_request() is False


def test_record_request(rate_limiter):
    """Test request recording"""
    initial_daily = rate_limiter._daily_requests
    initial_minute = len(rate_limiter._minute_requests)
    initial_second = len(rate_limiter._second_requests)

    rate_limiter.record_request()

    assert rate_limiter._daily_requests == initial_daily + 1
    assert len(rate_limiter._minute_requests) == initial_minute + 1
    assert len(rate_limiter._second_requests) == initial_second + 1


def test_cleanup_old_requests(rate_limiter):
    """Test cleanup of old requests"""
    # Add old requests
    old_time = datetime.now() - timedelta(minutes=2)
    rate_limiter._minute_requests = [old_time for _ in range(5)]
    rate_limiter._second_requests = [old_time for _ in range(5)]

    rate_limiter._cleanup_old_requests()

    assert len(rate_limiter._minute_requests) == 0
    assert len(rate_limiter._second_requests) == 0


def test_get_wait_time(rate_limiter):
    """Test wait time calculation"""
    # Test when limits are not exceeded
    assert rate_limiter.get_wait_time() == 0.0

    # Test when per-second limit is exceeded
    now = datetime.now()
    rate_limiter._second_requests = [now for _ in range(10)]
    assert rate_limiter.get_wait_time() > 0

    # Test when daily limit is exceeded
    rate_limiter._daily_requests = 100
    assert rate_limiter.get_wait_time() > 0


def test_handle_response(rate_limiter):
    """Test response handling"""
    # Test normal response
    rate_limiter.handle_response(200, None)

    # Test rate limit response
    response_body = '{"message": "Rate limit exceeded"}'
    rate_limiter.handle_response(429, response_body)

    # Test invalid JSON response
    rate_limiter.handle_response(429, "Invalid JSON")


def test_daily_reset():
    """Test daily counter reset"""
    config = QuotaConfig(daily_limit=100)
    limiter = FMPRateLimiter(config)

    # Set counter and old date
    limiter._daily_requests = 50
    limiter._reset_date = datetime.now().date() - timedelta(days=1)

    # Check should reset counter
    assert limiter.should_allow_request()
    assert limiter._daily_requests == 0
