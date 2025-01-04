# tests/integration/base.py
import time

from fmp_data.exceptions import RateLimitError


class BaseTestCase:
    """Base test class with rate limit handling"""

    def _handle_rate_limit(self, func, *args, **kwargs):
        """Helper to handle rate limiting"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                sleep_time = e.retry_after or 1
                time.sleep(sleep_time)
                continue
