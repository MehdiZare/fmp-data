# tests/integration/base.py
from collections.abc import Callable
import time
from typing import Any, TypeVar
import warnings

from fmp_data.exceptions import RateLimitError

T = TypeVar("T")


class BaseTestCase:
    """Base test class with rate limit handling"""

    MAX_RETRIES = 5
    BASE_WAIT_TIME = 1.0  # seconds
    MAX_WAIT_TIME = 32.0  # seconds

    @classmethod
    def _handle_rate_limit(cls, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Helper to handle rate limiting with exponential backoff.

        Args:
            func: Function to execute with rate limit handling
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The result from the executed function

        Raises:
            RateLimitError: If max retries are exceeded
        """
        for attempt in range(cls.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == cls.MAX_RETRIES - 1:
                    warnings.warn(
                        f"Rate limit exceeded after "
                        f"{cls.MAX_RETRIES} retries for "
                        f"{func.__name__}",
                        stacklevel=2,
                    )
                    raise

                # Calculate wait time with exponential backoff
                wait_time = min(cls.BASE_WAIT_TIME * (2**attempt), cls.MAX_WAIT_TIME)

                # Use the larger of our calculated wait time
                # or the API's suggested wait time
                if e.retry_after:
                    wait_time = max(wait_time, e.retry_after)

                warnings.warn(
                    f"Rate limit hit for {func.__name__}, "
                    f"attempt {attempt + 1}/{cls.MAX_RETRIES}. "
                    f"Waiting {wait_time:.1f}s before retry...",
                    stacklevel=2,
                )

                time.sleep(wait_time)
                continue

        raise RateLimitError(
            f"Rate limit handling failed after {cls.MAX_RETRIES} retries"
        )
