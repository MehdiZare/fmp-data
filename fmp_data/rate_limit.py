# fmp_data/rate_limit.py
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
import json
import logging
import time

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

    @staticmethod
    def _normalize_headers(
        response_headers: Mapping[str, str] | None,
    ) -> dict[str, str]:
        if not response_headers or not isinstance(response_headers, Mapping):
            return {}
        try:
            return {key.lower(): value for key, value in response_headers.items()}
        except TypeError:
            return {}

    @staticmethod
    def _parse_retry_after(value: str) -> float | None:
        parsed_value = value.strip()
        if not parsed_value:
            return None
        try:
            seconds = float(parsed_value)
            if seconds >= 0:
                return seconds
        except ValueError:
            pass
        try:
            parsed_date = parsedate_to_datetime(parsed_value)
        except (TypeError, ValueError):
            return None
        now = datetime.now(tz=parsed_date.tzinfo)
        return max(0.0, (parsed_date - now).total_seconds())

    @staticmethod
    def _parse_reset(value: str) -> float | None:
        parsed_value = value.strip()
        if not parsed_value:
            return None
        try:
            reset_value = float(parsed_value)
        except ValueError:
            return None
        now_epoch = time.time()
        if reset_value >= 0:
            if reset_value > 60:
                return max(0.0, reset_value - now_epoch)
            return reset_value
        return None

    def get_retry_after(
        self, response_headers: Mapping[str, str] | None
    ) -> float | None:
        """Extract retry-after from rate limit headers."""
        headers = self._normalize_headers(response_headers)
        retry_after = self._parse_retry_after(headers.get("retry-after", ""))
        if retry_after is not None:
            return retry_after
        reset_header = (
            headers.get("ratelimit-reset")
            or headers.get("x-ratelimit-reset")
            or headers.get("x-rate-limit-reset")
        )
        if reset_header is None:
            return None
        return self._parse_reset(reset_header)

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


class AsyncFMPRateLimiter:
    """
    Async wrapper for FMPRateLimiter that provides thread-safe async operations.
    Shares state with the underlying sync limiter for consistent rate tracking.
    """

    def __init__(self, sync_limiter: FMPRateLimiter) -> None:
        """
        Initialize async rate limiter wrapping a sync limiter.

        Args:
            sync_limiter: The synchronous rate limiter to wrap
        """
        self._sync_limiter = sync_limiter
        self._lock = asyncio.Lock()

    async def should_allow_request(self) -> bool:
        """
        Async check if request should be allowed based on all limits.

        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            return self._sync_limiter.should_allow_request()

    async def record_request(self) -> None:
        """Async record a new request."""
        async with self._lock:
            self._sync_limiter.record_request()

    async def wait_if_needed(self) -> None:
        """
        Wait asynchronously if rate limit would be exceeded.
        """
        if not await self.should_allow_request():
            wait_time = self.get_wait_time()
            await asyncio.sleep(wait_time)

    def get_wait_time(self) -> float:
        """
        Get seconds to wait before next request.

        Returns:
            Number of seconds to wait (non-negative)
        """
        return self._sync_limiter.get_wait_time()

    def handle_response(self, response_status: int, response_body: str | None) -> None:
        """
        Handle API response for rate limit information.

        Args:
            response_status: HTTP status code
            response_body: Response body text
        """
        self._sync_limiter.handle_response(response_status, response_body)
