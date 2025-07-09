# fmp_data/rate_limit.py
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuotaConfig:
    """FMP API quota configuration"""

    daily_limit: int
    requests_per_second: int = 10  # Default concurrent request limit
    requests_per_minute: int = 300  # Conservative default


class FMPRateLimiter:
    """
    FMP API rate limiter that tracks:
    1. Daily quota
    2. Per-second rate limiting
    3. Per-minute rate limiting
    """

    def __init__(self, quota_config: QuotaConfig):
        self.quota_config = quota_config

        # Daily tracking
        self._daily_requests: int = 0
        self._reset_date: date = datetime.now().date()

        # Per-minute tracking
        self._minute_requests: list[datetime] = []

        # Per-second tracking
        self._second_requests: list[datetime] = []

    def _cleanup_old_requests(self) -> None:
        """Remove old requests from tracking"""
        now = datetime.now()

        # Clean minute tracking (keep requests from last minute)
        minute_ago = now - timedelta(minutes=1)
        self._minute_requests = [ts for ts in self._minute_requests if ts > minute_ago]

        # Clean second tracking (keep requests from last second)
        second_ago = now - timedelta(seconds=1)
        self._second_requests = [ts for ts in self._second_requests if ts > second_ago]

    def should_allow_request(self) -> bool:
        """Check if request should be allowed based on all limits"""
        now = datetime.now()

        # Reset daily counter if needed
        if now.date() > self._reset_date:
            self._daily_requests = 0
            self._reset_date = now.date()

        # Clean up old request timestamps
        self._cleanup_old_requests()

        # Check all limits - return False if ANY limit is exceeded
        if self._daily_requests >= self.quota_config.daily_limit:
            logger.warning("Daily quota exceeded")
            return False

        if len(self._minute_requests) >= self.quota_config.requests_per_minute:
            logger.warning("Per-minute rate limit exceeded")
            return False

        if len(self._second_requests) >= self.quota_config.requests_per_second:
            logger.warning("Per-second rate limit exceeded")
            return False

        return True

    def record_request(self) -> None:
        """Record a new request"""
        now = datetime.now()

        # Record request in all trackers
        self._daily_requests += 1
        self._minute_requests.append(now)
        self._second_requests.append(now)

    def handle_response(self, response_status: int, response_body: str | None) -> None:
        """Handle API response for rate limit information"""
        if response_status == 429:
            if response_body:
                try:
                    error_data = json.loads(response_body)
                    error_message = error_data.get("message", "") or ""
                    logger.error(f"Rate limit exceeded: {error_message}")
                except json.JSONDecodeError:
                    logger.error("Rate limit exceeded (no details available)")
            else:
                logger.error("Rate limit exceeded: ")

    def get_wait_time(self) -> float:
        """Get seconds to wait before next request"""
        now = datetime.now()
        wait_time = 0.0

        # Check per-second limit
        if len(self._second_requests) >= self.quota_config.requests_per_second:
            oldest = min(self._second_requests)
            wait_time = max(
                wait_time, (oldest + timedelta(seconds=1) - now).total_seconds()
            )

        # Check per-minute limit
        if len(self._minute_requests) >= self.quota_config.requests_per_minute:
            oldest = min(self._minute_requests)
            wait_time = max(
                wait_time, (oldest + timedelta(minutes=1) - now).total_seconds()
            )

        # Check daily limit
        if self._daily_requests >= self.quota_config.daily_limit:
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            wait_time = max(wait_time, (tomorrow - now).total_seconds())

        return max(0.0, wait_time)  # Ensure non-negative wait time

    def log_status(self) -> None:
        """Log current rate limit status"""
        self._cleanup_old_requests()
        logger.info(
            f"Rate Limits: "
            f"Daily: {self._daily_requests}/{self.quota_config.daily_limit}, "
            f"Per-minute: "
            f"{len(self._minute_requests)}/{self.quota_config.requests_per_minute}, "
            f"Per-second: "
            f"{len(self._second_requests)}/{self.quota_config.requests_per_second}"
        )
