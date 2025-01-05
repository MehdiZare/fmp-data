# tests/integration/base.py
import time
from collections.abc import Callable
from typing import Any, TypeVar

from fmp_data.exceptions import RateLimitError

T = TypeVar("T")


class BaseTestCase:
    """Base test class with rate limit handling"""

    @staticmethod
    def _handle_rate_limit(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Helper to handle rate limiting.

        Args:
            func: Function to execute with rate limit handling
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The result from the executed function

        Raises:
            RateLimitError: If max retries are exceeded
        """
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

        raise RateLimitError("Max retries exceeded")
