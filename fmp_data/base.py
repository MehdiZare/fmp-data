# fmp_data/base.py
import json
import logging
import time
from typing import Any, TypeVar
import warnings

import httpx
from pydantic import BaseModel
from tenacity import (
    Retrying,
    RetryCallState,
    after_log,
    before_sleep_log,
    retry_if_exception,
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
    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the BaseClient with the provided configuration.
        """
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

    def _setup_http_client(self) -> None:
        """
        Setup HTTP client with default configuration.
        """
        self.client = httpx.Client(
            timeout=self.config.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "FMP-Python-Client/1.0",
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        """
        Clean up resources (close the httpx client).
        """
        if hasattr(self, "client") and self.client is not None:
            self.client.close()

    def _handle_rate_limit(self, wait_time: float) -> None:
        """
        Handle rate limiting by waiting or raising an exception based on retry count.
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

    def _wait_for_retry(self, retry_state: RetryCallState) -> float:
        """
        Prefer retry_after from RateLimitError, otherwise fall back to exponential backoff.
        """
        outcome = retry_state.outcome
        if outcome is not None and outcome.failed:
            exc = outcome.exception()
            if isinstance(exc, RateLimitError) and exc.retry_after is not None:
                return exc.retry_after
        return wait_exponential(multiplier=1, min=4, max=10)(retry_state)

    @staticmethod
    def _is_retryable_error(exc: BaseException) -> bool:
        if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError)):
            return True
        if isinstance(exc, RateLimitError):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code >= 500
        return False

    @log_api_call()
    def request(self, endpoint: Endpoint[T], **kwargs: Any) -> T | list[T]:
        """
        Make request with rate limiting and retry logic.

        Args:
            endpoint: The Endpoint object describing the request (method, path, etc.).
            **kwargs: Arbitrary keyword arguments passed as request parameters.

        Returns:
            Either a single Pydantic model of type T or a list of T.
        """
        self._rate_limit_retry_count = 0  # Reset counter at start of new request

        # Create retryer with configurable max_retries
        retryer = Retrying(
            stop=stop_after_attempt(self.config.max_retries),
            wait=self._wait_for_retry,
            retry=retry_if_exception(self._is_retryable_error),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True,
        )

        for attempt in retryer:
            with attempt:
                return self._execute_request(endpoint, **kwargs)

        # This should never be reached due to reraise=True, but satisfies type checker
        raise FMPError("Request failed after all retry attempts")

    def _execute_request(self, endpoint: Endpoint[T], **kwargs: Any) -> T | list[T]:
        """
        Execute a single request attempt with rate limiting.

        Args:
            endpoint: The Endpoint object describing the request.
            **kwargs: Request parameters.

        Returns:
            Either a single Pydantic model of type T or a list of T.
        """
        # Check rate limit before making request
        if not self._rate_limiter.should_allow_request():
            wait_time = self._rate_limiter.get_wait_time()
            self._handle_rate_limit(wait_time)

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

            data = self.handle_response(response)
            return self._process_response(endpoint, data)

        except RateLimitError:
            # Re-raise rate limit errors to be handled by retry logic
            raise
        except Exception as e:
            self.logger.error(
                f"Request failed: {e!s}",
                extra={"endpoint": endpoint.name, "error": str(e)},
                exc_info=True,
            )
            raise

    def handle_response(self, response: httpx.Response) -> dict[str, Any] | list[Any]:
        """
        Handle API response and errors, returning dict or list from JSON.

        Raises:
            RateLimitError: If status is 429
            AuthenticationError: If status is 401
            ValidationError: If status is 400
            FMPError: For other 4xx/5xx errors or invalid JSON
        """
        try:
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict | list):
                raise FMPError(
                    f"Unexpected response type: {type(data)}. Expected dict or list.",
                    response={"data": data},
                )
            return data  # Now mypy knows this is dict[str, Any] | list[Any]
        except httpx.HTTPStatusError as e:
            error_details: dict[str, Any] = {}
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details["raw_content"] = e.response.content.decode()

            if e.response.status_code == 429:
                self._rate_limiter.handle_response(
                    e.response.status_code, e.response.text
                )
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
                f"Invalid JSON response from API: {e!s}",
                response={"raw_content": response.content.decode()},
            ) from e

    @staticmethod
    def _check_error_response(data: dict[str, Any]) -> None:
        """Check for error messages in response data and raise FMPError if found.

        Args:
            data: Dictionary response data to check

        Raises:
            FMPError: If an error message is found in the data
        """
        if "Error Message" in data:
            raise FMPError(data["Error Message"])
        if "message" in data:
            raise FMPError(data["message"])
        if "error" in data:
            raise FMPError(data["error"])

    @staticmethod
    def _validate_single_item(endpoint: Endpoint[T], item: Any) -> T:
        """Validate a single item against the endpoint's response model.

        Args:
            endpoint: The endpoint containing the response model
            item: The item to validate

        Returns:
            Validated model instance

        Raises:
            ValueError: If the model structure is invalid
        """
        if isinstance(item, dict):
            return endpoint.response_model.model_validate(item)

        # Handle primitive types
        if endpoint.response_model in (str, int, float, bool):
            return endpoint.response_model(item)  # type: ignore[return-value]

        # Try to feed non-dict value into the first field
        model = endpoint.response_model
        try:
            first_field = next(iter(model.__annotations__))
            field_info = model.model_fields[first_field]
            field_name = field_info.alias or first_field
            return model.model_validate({field_name: item})
        except (StopIteration, KeyError, AttributeError) as exc:
            raise ValueError(f"Invalid model structure for {model.__name__}") from exc

    @staticmethod
    def _process_list_response(endpoint: Endpoint[T], data: list[Any]) -> list[T]:
        """Process a list response with validation warnings.

        Args:
            endpoint: The endpoint containing the response model
            data: List of items to process

        Returns:
            List of validated model instances
        """
        processed_items: list[T] = []
        for item in data:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                processed_item = BaseClient._validate_single_item(endpoint, item)
                for warning in w:
                    logger.warning(f"Validation warning: {warning.message}")
                processed_items.append(processed_item)
        return processed_items

    @staticmethod
    def _process_response(endpoint: Endpoint[T], data: Any) -> T | list[T]:
        """Process the response data with warnings, returning T or list[T].

        Args:
            endpoint: The endpoint containing the response model
            data: Response data to process

        Returns:
            Validated model instance or list of instances
        """
        # Check for error messages in dict responses
        if isinstance(data, dict):
            BaseClient._check_error_response(data)

        # Process list responses
        if isinstance(data, list):
            return BaseClient._process_list_response(endpoint, data)

        # Process single item responses
        if endpoint.response_model in (str, int, float, bool):
            return endpoint.response_model(data)  # type: ignore[return-value]
        return endpoint.response_model.model_validate(data)

    async def request_async(self, endpoint: Endpoint[T], **kwargs: Any) -> T | list[T]:
        """
        Make async request with rate limiting, returning T or list[T].
        """
        validated_params = endpoint.validate_params(kwargs)
        url = endpoint.build_url(self.config.base_url, validated_params)
        query_params = endpoint.get_query_params(validated_params)
        query_params["apikey"] = self.config.api_key

        try:
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
            self.logger.error(f"Async request failed: {e!s}")
            raise


class EndpointGroup:
    """Abstract base class for endpoint groups"""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance."""
        return self._client
