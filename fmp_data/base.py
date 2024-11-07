# base.py
import json
import logging
from typing import Any, TypeVar

import httpx
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import ClientConfig
from .exceptions import AuthenticationError, FMPError, RateLimitError, ValidationError
from .logger import FMPLogger, log_api_call
from .models import Endpoint
from .rate_limit import FMPRateLimiter, QuotaConfig

T = TypeVar("T")

logger = FMPLogger().get_logger(__name__)


class BaseClient:
    """Abstract base class for API clients"""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = FMPLogger().get_logger(__name__)

        # Configure logging based on config
        FMPLogger().configure(self.config.logging)

        self._setup_http_client()
        self.logger.info(
            "Initializing API client",
            extra={"base_url": self.config.base_url, "timeout": self.config.timeout},
        )

        # Initialize rate limiter using config
        self._rate_limiter = FMPRateLimiter(
            QuotaConfig(
                daily_limit=self.config.rate_limit.daily_limit,
                requests_per_second=self.config.rate_limit.requests_per_second,
                requests_per_minute=self.config.rate_limit.requests_per_minute,
            )
        )

    def _setup_http_client(self):
        """Setup HTTP client with default configuration"""
        self.client = httpx.Client(
            timeout=self.config.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "FMP-Python-Client/1.0",
                "Accept": "application/json",
            },
        )

    def get_query_params(self, validated_params: dict[str, Any]) -> dict[str, Any]:
        """Get query parameters including API key"""
        query_params = {k: v for k, v in validated_params.items() if v is not None}
        query_params["apikey"] = self.config.api_key
        return query_params

    def handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_details = {}
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details["raw_content"] = e.response.content.decode()

            if e.response.status_code == 429:
                wait_time = self._rate_limiter.get_wait_time()
                raise RateLimitError(
                    f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                    status_code=429,
                    response=error_details,
                    retry_after=wait_time,
                ) from e
            elif e.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key or authentication failed",
                    status_code=401,
                    response=error_details,
                ) from e
            elif e.response.status_code == 400:
                raise ValidationError(
                    f"Invalid request parameters: {error_details}",
                    status_code=400,
                    response=error_details,
                ) from e
            else:
                raise FMPError(
                    f"HTTP {e.response.status_code} error occurred: {error_details}",
                    status_code=e.response.status_code,
                    response=error_details,
                ) from e
        except json.JSONDecodeError as e:
            raise FMPError(
                f"Invalid JSON response from API: {str(e)}",
                response={"raw_content": response.content.decode()},
            ) from e

    @staticmethod
    def _process_response(endpoint: Endpoint[T], data: Any) -> T:
        """Process the response data"""
        if isinstance(data, dict) and "message" in data:  # Error response
            raise FMPError(data["message"])

        if isinstance(data, list):
            return [endpoint.response_model.model_validate(item) for item in data]
        return endpoint.response_model.model_validate(data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
    )
    @log_api_call()
    def request(self, endpoint: Endpoint[T], **kwargs) -> T:
        """Make request with rate limiting"""
        if not self._rate_limiter.should_allow_request():
            wait_time = self._rate_limiter.get_wait_time()
            raise RateLimitError(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )

        try:
            self._rate_limiter.record_request()

            validated_params = endpoint.validate_params(kwargs)
            url = endpoint.build_url(self.config.base_url, validated_params)
            query_params = self.get_query_params(validated_params)

            self.logger.debug(
                f"Making request to {endpoint.name}",
                extra={"url": url, "endpoint": endpoint.name, "method": "GET"},
            )

            response = self.client.request("GET", url, params=query_params)

            # Handle rate limit response
            self._rate_limiter.handle_response(
                response.status_code,
                response.text if response.status_code == 429 else None,
            )

            data = self.handle_response(response)
            return self._process_response(endpoint, data)

        except Exception as e:
            self.logger.error(
                f"Request failed: {str(e)}",
                extra={"endpoint": endpoint.name, "error": str(e)},
                exc_info=True,
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
    )
    @log_api_call()
    async def request_async(self, endpoint: Endpoint[T], **kwargs) -> T:
        """Make async request to API endpoint with retry logic"""
        if not self._rate_limiter.should_allow_request():
            wait_time = self._rate_limiter.get_wait_time()
            raise RateLimitError(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )

        try:
            self._rate_limiter.record_request()

            validated_params = endpoint.validate_params(kwargs)
            url = endpoint.build_url(self.config.base_url, validated_params)
            query_params = self.get_query_params(validated_params)

            logger.debug(f"Making async request to {url}")

            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=True,
                headers=self.client.headers,
            ) as client:
                response = await client.request("GET", url, params=query_params)

                self._rate_limiter.handle_response(
                    response.status_code,
                    response.text if response.status_code == 429 else None,
                )

                data = self.handle_response(response)
                return self._process_response(endpoint, data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait_time = self._rate_limiter.get_wait_time()
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    retry_after=wait_time,
                    response=e.response.json() if e.response.content else None,
                ) from e
            raise

    def close(self) -> None:
        """Clean up resources"""
        self.client.close()

    def __del__(self):
        """Clean up resources on deletion"""
        self.close()


class EndpointGroup:
    """Abstract base class for endpoint groups"""

    def __init__(self, client: BaseClient):
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance"""
        return self._client
