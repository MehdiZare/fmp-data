# base.py
import json
import logging
import time
import warnings
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from fmp_data.config import ClientConfig
from fmp_data.exceptions import (
    AuthenticationError,
    FMPError,
    RateLimitError,
    ValidationError,
)
from fmp_data.logger import FMPLogger, log_api_call
from fmp_data.models import Endpoint
from fmp_data.rate_limit import FMPRateLimiter, QuotaConfig

T = TypeVar("T", bound=BaseModel)

logger = FMPLogger().get_logger(__name__)


class BaseClient:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = FMPLogger().get_logger(__name__)
        self.max_rate_limit_retries = getattr(config, "max_rate_limit_retries", 3)
        self._rate_limit_retry_count = 0

        # Configure logging based on config
        FMPLogger().configure(self.config.logging)

        self._setup_http_client()
        self.logger.info(
            "Initializing API client",
            extra={"base_url": self.config.base_url, "timeout": self.config.timeout},
        )

        # Initialize rate limiter
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

    def close(self):
        """Clean up resources"""
        if hasattr(self, "client") and self.client is not None:
            self.client.close()

    def _handle_rate_limit(self, wait_time: float) -> None:
        """
        Handle rate limiting by waiting or raising an exception based on retry count
        """
        self._rate_limit_retry_count += 1

        if self._rate_limit_retry_count > self.max_rate_limit_retries:
            self._rate_limit_retry_count = 0  # Reset for next request
            raise RateLimitError(
                f"Rate limit exceeded after "
                f"{self.max_rate_limit_retries} retries. "
                f"Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )

        self.logger.warning(
            f"Rate limit reached "
            f"(attempt {self._rate_limit_retry_count}/{self.max_rate_limit_retries}), "
            f"waiting {wait_time:.1f} seconds before retrying"
        )
        time.sleep(wait_time)

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
    def request(self, endpoint: Endpoint[T], **kwargs) -> T | list[T]:
        """Make request with rate limiting and retry logic"""
        # First, check if we're already over the rate limit
        if not self._rate_limiter.should_allow_request():
            wait_time = self._rate_limiter.get_wait_time()
            raise RateLimitError(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )

        self._rate_limit_retry_count = 0  # Reset counter at start of new request

        try:
            self._rate_limiter.record_request()

            # Validate and process parameters
            validated_params = endpoint.validate_params(kwargs)

            # Build URL
            url = endpoint.build_url(self.config.base_url, validated_params)

            # Extract query parameters and add API key
            query_params = endpoint.get_query_params(validated_params)
            query_params["apikey"] = self.config.api_key

            self.logger.debug(
                f"Making request to {endpoint.name}",
                extra={
                    "url": url,
                    "endpoint": endpoint.name,
                    "method": endpoint.method.value,
                },
            )

            response = self.client.request(
                endpoint.method.value, url, params=query_params
            )

            # Handle 429 responses from the API
            if response.status_code == 429:
                self._rate_limiter.handle_response(response.status_code, response.text)
                wait_time = self._rate_limiter.get_wait_time()
                raise RateLimitError(
                    f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                    retry_after=wait_time,
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
    def _process_response(endpoint: Endpoint[T], data: Any) -> T | list[T]:
        """Process the response data with warning handling"""
        if isinstance(data, dict):
            # Check for different forms of error messages
            if "Error Message" in data:
                raise FMPError(data["Error Message"])
            if "message" in data:
                raise FMPError(data["message"])
            if "error" in data:
                raise FMPError(data["error"])

        if isinstance(data, list):
            processed_items: list[T] = []
            for item in data:
                with warnings.catch_warnings(record=True) as w:
                    # Enable all warnings
                    warnings.simplefilter("always")
                    # Process item
                    if isinstance(item, dict):
                        processed_item = endpoint.response_model.model_validate(item)
                    else:
                        # Get the first field info directly from model config
                        model = endpoint.response_model
                        try:
                            # Get first field name from the model
                            first_field = next(iter(model.__annotations__))
                            # Try to get alias from field info
                            field_info = model.model_fields[first_field]
                            field_name = field_info.alias or first_field
                            processed_item = model.model_validate({field_name: item})
                        except (StopIteration, KeyError, AttributeError) as e:
                            raise ValueError(
                                f"Invalid model structure for {model.__name__}"
                            ) from e

                    # Log any warnings
                    for warning in w:
                        logger.warning(f"Validation warning: {warning.message}")
                    processed_items.append(processed_item)
            return processed_items
        return endpoint.response_model.model_validate(data)

    async def request_async(self, endpoint: Endpoint[T], **kwargs) -> T | list[T]:
        """Make async request with rate limiting"""
        validated_params = endpoint.validate_params(kwargs)
        url = endpoint.build_url(self.config.base_url, validated_params)
        query_params = endpoint.get_query_params(validated_params)
        query_params["apikey"] = self.config.api_key

        try:
            # Add timeout and other settings from config
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "FMP-Python-Client/1.0",
                    "Accept": "application/json",
                },
            ) as client:
                response = await client.request(
                    endpoint.method.value, url, params=query_params
                )
                data = self.handle_response(response)
                return self._process_response(endpoint, data)
        except Exception as e:
            self.logger.error(f"Async request failed: {str(e)}")
            raise


class EndpointGroup:
    """Abstract base class for endpoint groups"""

    def __init__(self, client: BaseClient):
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance"""
        return self._client
