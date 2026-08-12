# fmp_data/base.py
from __future__ import annotations

import asyncio
from contextvars import ContextVar
import copy
import json
import logging
import re
import time
from typing import Any, Literal, NoReturn, TypeGuard, TypeVar, cast, overload
import warnings

import httpx
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    after_log,
    before_sleep_log,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from fmp_data.cache.base import CacheBackend
from fmp_data.config import ClientConfig
from fmp_data.exceptions import (
    AuthenticationError,
    FMPError,
    RateLimitError,
    ValidationError,
)
from fmp_data.logger import FMPLogger, log_api_call
from fmp_data.models import Endpoint
from fmp_data.rate_limit import AsyncFMPRateLimiter, FMPRateLimiter, QuotaConfig

T = TypeVar("T")
ValidationMode = Literal["lenient", "warn", "strict"]


def _unwrap_list_result(result: T | list[T], _model: type[T]) -> list[T]:
    """Normalize ``request()`` output to ``list[T]``.

    List endpoints are declared ``Endpoint[T]`` (the row type). ``request``
    remains ``T | list[T]`` so single-item callers can still use
    ``_unwrap_single``. Wrapping a lone ``T`` as ``[T]`` matches FMP
    payloads that return one object instead of a one-element array (#235).

    ``_model`` is the row type, kept so callers match ``_unwrap_single``.
    """
    if isinstance(result, list):
        return result
    return [result]


logger = FMPLogger().get_logger(__name__)

# Context variable for request-scoped rate limit retry tracking.
# This ensures each request has its own counter, even with concurrent requests.
_rate_limit_retry_count: ContextVar[int] = ContextVar(
    "rate_limit_retry_count", default=0
)
_extra_field_warnings_seen: set[tuple[str, tuple[str, ...]]] = set()
_API_KEY_ASSIGNMENT_RE = re.compile(
    r"([\"']?api_?key[\"']?\s*[=:]\s*[\"']?)([^&\s\"'<>]+)([\"']?)",
    re.IGNORECASE,
)
_API_KEY_ENCODED_RE = re.compile(r"(apikey%3[Dd])([^&\s\"'<>]+)", re.IGNORECASE)


def _is_pydantic_model(model: type[Any]) -> TypeGuard[type[BaseModel]]:
    return isinstance(model, type) and issubclass(model, BaseModel)


def _redact_api_keys(text: str) -> str:
    """Redact apikey/api_key values embedded in free-form strings.

    Handles common query-string, percent-encoded (``apikey%3D``), and
    assignment/JSON-text patterns. For structured dict payloads, use
    :func:`_sanitize_error_details` (also redacts ``api-key`` keys by name).
    """
    redacted = _API_KEY_ASSIGNMENT_RE.sub(r"\1[REDACTED]\3", text)
    return _API_KEY_ENCODED_RE.sub(r"\1[REDACTED]", redacted)


def _sanitize_error_details(
    value: dict[str, Any] | list[Any] | str,
) -> dict[str, Any] | list[Any] | str:
    """Recursively redact API keys from error payloads that may reflect them."""
    if isinstance(value, str):
        return _redact_api_keys(value)
    if isinstance(value, list):
        return [_sanitize_error_value(item) for item in value]
    return {
        key: (
            "[REDACTED]"
            if key.lower() in {"apikey", "api_key", "api-key"}
            else _sanitize_error_value(item)
        )
        for key, item in value.items()
    }


def _sanitize_error_value(value: Any) -> Any:
    """Sanitize a single error-payload value (dict, list, string, or other)."""
    if isinstance(value, dict):
        return _sanitize_error_details(value)
    if isinstance(value, list):
        return [_sanitize_error_value(item) for item in value]
    if isinstance(value, str):
        return _redact_api_keys(value)
    return value


class BaseClient:
    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the BaseClient with the provided configuration.
        """
        self.config = config
        self.logger = FMPLogger().get_logger(__name__)
        self.max_rate_limit_retries = getattr(config, "max_rate_limit_retries", 3)

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

        # Async rate limiter wraps sync limiter with asyncio.Lock
        self._async_rate_limiter = AsyncFMPRateLimiter(self._rate_limiter)

        # Async client (lazily initialized)
        self._async_client: httpx.AsyncClient | None = None

        # Response cache (optional)
        self._cache: CacheBackend | None = None
        cache_cfg = getattr(config, "cache", None)
        if cache_cfg is not None and getattr(cache_cfg, "enabled", False) is True:
            from fmp_data.cache import create_backend
            from fmp_data.cache.config import CacheConfig

            if isinstance(cache_cfg, CacheConfig):
                self._cache = create_backend(cache_cfg)
                self._cache_ttl_overrides = cache_cfg.ttl_overrides
                self._cache_default_ttl = cache_cfg.default_ttl
                self.logger.info(
                    "Response caching enabled (backend=%s)",
                    cache_cfg.backend,
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
                "apikey": self.config.api_key,
            },
        )

    def close(self) -> None:
        """
        Clean up all sync resources (close the sync httpx client).

        Note: If you've used async methods, call aclose() instead to properly
        close both sync and async clients.
        """
        client = getattr(self, "client", None)
        if client is not None:
            client.close()

    def _setup_async_client(self) -> httpx.AsyncClient:
        """
        Setup or return existing async HTTP client with connection pooling.
        """
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "FMP-Python-Client/1.0",
                    "Accept": "application/json",
                    "apikey": self.config.api_key,
                },
            )
        return self._async_client

    async def aclose(self) -> None:
        """
        Clean up all resources (both async and sync httpx clients).

        This is the recommended cleanup method when using async methods.
        """
        # Close async client
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None
        # Also close sync client
        self.close()

    @staticmethod
    def _build_cache_key(endpoint_name: str, params: dict[str, Any]) -> str:
        """Build a deterministic cache key from endpoint name and params.

        Excludes 'apikey' to avoid leaking secrets in keys.
        Uses urllib.parse.urlencode to properly escape special characters
        and prevent key collisions from values containing '&' or '='.
        """
        import hashlib
        import urllib.parse

        filtered = {k: v for k, v in sorted(params.items()) if k != "apikey"}
        params_str = urllib.parse.urlencode(filtered, doseq=True)

        # codeql[py/weak-sensitive-data-hashing]
        # This hash is only used to shorten cache keys, not for credential storage.
        params_hash = hashlib.sha256(
            params_str.encode(), usedforsecurity=False
        ).hexdigest()[:16]
        return f"{endpoint_name}:{params_hash}"

    def _get_cache_ttl(self, endpoint_name: str) -> int:
        """Get TTL for a given endpoint, checking overrides first."""
        if not hasattr(self, "_cache_ttl_overrides"):
            return 300
        return self._cache_ttl_overrides.get(endpoint_name, self._cache_default_ttl)

    def _cache_get(
        self, endpoint_name: str, cache_key: str
    ) -> dict[str, Any] | list[Any] | None:
        """Read from cache, returning None on any failure."""
        assert self._cache is not None
        try:
            cached = self._cache.get(cache_key)
            return None if cached is None else copy.deepcopy(cached)
        except Exception:
            self.logger.warning(
                "Cache read failed for %s", endpoint_name, exc_info=True
            )
            return None

    async def _cache_aget(
        self, endpoint_name: str, cache_key: str
    ) -> dict[str, Any] | list[Any] | None:
        """Async read from cache, returning None on any failure."""
        assert self._cache is not None
        try:
            cached = await self._cache.aget(cache_key)
            return None if cached is None else copy.deepcopy(cached)
        except Exception:
            self.logger.warning(
                "Cache read failed for %s", endpoint_name, exc_info=True
            )
            return None

    def _cache_set(
        self, endpoint_name: str, cache_key: str, data: Any, ttl: int
    ) -> None:
        """Write to cache, logging on failure."""
        assert self._cache is not None
        try:
            self._cache.set(cache_key, copy.deepcopy(data), ttl)
        except Exception:
            self.logger.warning(
                "Cache write failed for %s", endpoint_name, exc_info=True
            )

    async def _cache_aset(
        self, endpoint_name: str, cache_key: str, data: Any, ttl: int
    ) -> None:
        """Async write to cache, logging on failure."""
        assert self._cache is not None
        try:
            await self._cache.aset(cache_key, copy.deepcopy(data), ttl)
        except Exception:
            self.logger.warning(
                "Cache write failed for %s", endpoint_name, exc_info=True
            )

    def _handle_rate_limit(self, wait_time: float) -> None:
        """
        Handle rate limiting by waiting or raising an exception based on retry count.
        Uses context variable for request-scoped retry tracking.
        """
        current_count = _rate_limit_retry_count.get() + 1
        _rate_limit_retry_count.set(current_count)

        if current_count > self.max_rate_limit_retries:
            _rate_limit_retry_count.set(0)  # Reset for next request
            raise RateLimitError(
                f"Rate limit exceeded after "
                f"{self.max_rate_limit_retries} retries. "
                f"Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )

        self.logger.warning(
            f"Rate limit reached "
            f"(attempt {current_count}/{self.max_rate_limit_retries}), "
            f"waiting {wait_time:.1f} seconds before retrying"
        )
        time.sleep(wait_time)

    def _wait_for_retry(self, retry_state: RetryCallState) -> float:
        """
        Prefer retry_after from RateLimitError, otherwise fall back to exponential
        backoff.
        """
        outcome = retry_state.outcome
        if outcome is not None and outcome.failed:
            exc = outcome.exception()
            if isinstance(exc, RateLimitError) and exc.retry_after is not None:
                return float(exc.retry_after)
        wait = wait_exponential(multiplier=1, min=4, max=10)(retry_state)
        return float(wait)

    @staticmethod
    def _is_retryable_error(exc: BaseException) -> bool:
        if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
            return True
        if isinstance(exc, RateLimitError):
            return True
        # Mapped FMP errors from status conversion (incl. binary endpoints).
        if (
            isinstance(exc, FMPError)
            and exc.status_code is not None
            and exc.status_code >= 500
        ):
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
        _rate_limit_retry_count.set(0)  # Reset counter at start of new request

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

    def request_list(self, endpoint: Endpoint[T], **kwargs: Any) -> list[T]:
        """Request a list-returning endpoint as ``list[T]``.

        ``request`` stays ``Endpoint[T] -> T | list[T]`` so single-item
        callers can keep ``_unwrap_single``. List endpoints should be
        declared ``Endpoint[T]`` (the row type) and go through this
        helper or ``EndpointGroup._unwrap_list`` instead of copying the
        ``PROFILE_CIK`` single-object pattern (#235).
        """
        return _unwrap_list_result(
            self.request(endpoint, **kwargs),
            endpoint.response_model,
        )

    def _execute_request(self, endpoint: Endpoint[T], **kwargs: Any) -> T | list[T]:
        """
        Execute a single request attempt with rate limiting.

        Args:
            endpoint: The Endpoint object describing the request.
            **kwargs: Request parameters.

        Returns:
            Either a single Pydantic model of type T or a list of T.
        """
        request_start = time.perf_counter()
        status_code = 0
        success = False
        force_refresh = kwargs.pop("force_refresh", False)

        try:
            # Validate and process parameters
            validated_params = endpoint.validate_params(
                kwargs,
                unknown_param_policy=self.config.unknown_param_policy,
            )

            # Build URL
            url = endpoint.build_url(self.config.base_url, validated_params)

            # Extract query parameters and add API key
            query_params = endpoint.get_query_params(validated_params)
            query_params["apikey"] = self.config.api_key

            # Check cache before rate limiting — cache hits are free
            cache_key: str | None = None
            if (
                self._cache is not None
                and not force_refresh
                and endpoint.response_model is not bytes
            ):
                cache_key = self._build_cache_key(endpoint.name, query_params)
                cached = self._cache_get(endpoint.name, cache_key)
                if cached is not None:
                    self.logger.debug(
                        "Cache hit for %s",
                        endpoint.name,
                        extra={"endpoint": endpoint.name, "cache_key": cache_key},
                    )
                    success = True
                    return self._process_response(
                        endpoint,
                        cached,
                        validation_mode=self.config.validation_mode,
                    )

            # Check rate limit only when making an actual HTTP request
            if not self._rate_limiter.should_allow_request():
                wait_time = self._rate_limiter.get_wait_time()
                self._handle_rate_limit(wait_time)

            self._rate_limiter.record_request()

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
            status_code = response.status_code

            try:
                data: bytes | dict[str, Any] | list[Any]
                if endpoint.response_model is bytes:
                    self._raise_response_for_status(response)
                    data = response.content
                else:
                    data = self.handle_response(endpoint, response)
                result = self._process_response(
                    endpoint,
                    data,
                    validation_mode=self.config.validation_mode,
                )
                success = True

                # Store in cache
                if self._cache is not None and cache_key is not None:
                    ttl = self._get_cache_ttl(endpoint.name)
                    self._cache_set(endpoint.name, cache_key, data, ttl)

                return result
            finally:
                response.close()

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
        finally:
            # Log timing metrics
            latency_ms = (time.perf_counter() - request_start) * 1000
            self.logger.debug(
                f"Request completed: {endpoint.name}",
                extra={
                    "endpoint": endpoint.name,
                    "latency_ms": round(latency_ms, 2),
                    "status_code": status_code,
                    "success": success,
                },
            )

            # Call metrics callback if configured
            if self.config.metrics_callback is not None:
                try:
                    self.config.metrics_callback(
                        endpoint_name=endpoint.name,
                        latency_ms=round(latency_ms, 2),
                        success=success,
                        status_code=status_code,
                        retry_count=_rate_limit_retry_count.get(),
                    )
                except Exception as callback_exc:
                    self.logger.warning(
                        f"Metrics callback failed: {callback_exc!s}",
                        extra={"error": str(callback_exc)},
                    )

    def handle_response(
        self,
        endpoint: Endpoint[T] | httpx.Response,
        response: httpx.Response | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Handle API response and errors, returning dict or list from JSON.

        Raises:
            RateLimitError: If status is 429
            AuthenticationError: If status is 401
            ValidationError: If status is 400
            FMPError: For other 4xx/5xx errors or invalid JSON
        """
        endpoint_for_error: Endpoint[T] | None = None
        if response is None:
            # Check if endpoint is a Response or Response-like object (for tests)
            if isinstance(endpoint, httpx.Response) or getattr(
                endpoint, "raise_for_status", None
            ):
                response = cast(httpx.Response, endpoint)
            else:
                raise TypeError("handle_response() missing required response argument")
        else:
            if isinstance(endpoint, Endpoint):
                endpoint_for_error = endpoint

        assert response is not None

        try:
            response.raise_for_status()
            return self._parse_json_response(response)
        except httpx.HTTPStatusError as exc:
            return self._handle_http_status_error(endpoint_for_error, exc)
        except json.JSONDecodeError as exc:
            raise FMPError(
                f"Invalid JSON response from API: {exc!s}",
                response={"raw_content": response.content.decode()},
            ) from exc

    @staticmethod
    def _parse_json_response(
        response: httpx.Response,
    ) -> dict[str, Any] | list[Any]:
        data = response.json()
        if not isinstance(data, dict | list):
            raise FMPError(
                f"Unexpected response type: {type(data)}. Expected dict or list.",
                response={"data": data},
            )
        return cast(dict[str, Any] | list[Any], data)

    def _raise_response_for_status(self, response: httpx.Response) -> None:
        """Raise typed FMP errors for non-success binary responses.

        Binary endpoints must not re-raise raw ``httpx.HTTPStatusError``:
        that type stringifies the request URL, which often includes ``apikey``.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._raise_fmp_http_error(
                exc,
                self._safe_error_details(exc.response),
                exc.response.status_code,
            )

    @staticmethod
    def _get_error_details(
        response: httpx.Response,
    ) -> dict[str, Any] | list[Any]:
        """Return response body for error reporting with API keys redacted."""
        try:
            data = response.json()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            raw = response.content.decode("utf-8", errors="replace")
            return {"raw_content": _redact_api_keys(raw)}
        if isinstance(data, dict | list):
            return cast(dict[str, Any] | list[Any], _sanitize_error_details(data))
        return {"raw_content": _redact_api_keys(str(data))}

    @classmethod
    def _safe_error_details(
        cls,
        response: httpx.Response,
    ) -> dict[str, Any] | list[Any]:
        """Best-effort error details; never fail open to unreadable bodies."""
        try:
            return cls._get_error_details(response)
        except Exception:
            return {"raw_content": "[unreadable error body]"}

    def _handle_http_status_error(
        self,
        endpoint: Endpoint[T] | httpx.HTTPStatusError | None,
        error: httpx.HTTPStatusError | None = None,
    ) -> dict[str, Any] | list[Any]:
        if error is None:
            if isinstance(endpoint, httpx.HTTPStatusError):
                error = endpoint
                endpoint = None
            else:
                raise TypeError(
                    "_handle_http_status_error() missing required error argument"
                )

        error_details = self._safe_error_details(error.response)
        status_code = error.response.status_code

        if status_code == 404:
            if endpoint is not None and getattr(endpoint, "allow_empty_on_404", False):
                endpoint_name = (
                    endpoint.name if isinstance(endpoint, Endpoint) else None
                )
                self.logger.warning(
                    "Received 404 for endpoint configured with allow_empty_on_404; "
                    "returning empty list.",
                    extra={"endpoint": endpoint_name, "status_code": status_code},
                )
                return []
            if isinstance(error_details, list) and not error_details:
                self.logger.warning(
                    "Received 404 with empty list payload; returning empty list.",
                    extra={"status_code": status_code},
                )
                return []
            if isinstance(error_details, dict) and not error_details:
                self.logger.warning(
                    "Received 404 with empty object payload; returning empty object.",
                    extra={"status_code": status_code},
                )
                return {}

        self._raise_fmp_http_error(error, error_details, status_code)

    def _raise_fmp_http_error(
        self,
        error: httpx.HTTPStatusError,
        error_details: dict[str, Any] | list[Any],
        status_code: int,
    ) -> NoReturn:
        """Map HTTP status errors to FMP exceptions without chaining httpx.

        ``from None`` is intentional: ``httpx.HTTPStatusError`` stringifies the
        request URL (often including ``apikey``), so chaining would leak keys
        into formatted tracebacks.
        """
        if status_code == 429:
            self._rate_limiter.handle_response(
                status_code, _redact_api_keys(error.response.text)
            )
            retry_after = self._rate_limiter.get_retry_after(error.response.headers)
            wait_time = (
                retry_after
                if retry_after is not None
                else self._rate_limiter.get_wait_time()
            )
            raise RateLimitError(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                status_code=429,
                response=error_details,
                retry_after=wait_time,
            ) from None

        if status_code == 401:
            raise AuthenticationError(
                "Invalid API key or authentication failed",
                status_code=401,
                response=error_details,
            ) from None

        if status_code == 400:
            raise ValidationError(
                f"Invalid request parameters: {error_details}",
                status_code=400,
                response=error_details,
            ) from None

        raise FMPError(
            f"HTTP {status_code} error occurred: {error_details}",
            status_code=status_code,
            response=error_details,
        ) from None

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
    def _validate_model(
        endpoint_name: str,
        model: type[BaseModel],
        payload: Any,
        validation_mode: ValidationMode,
    ) -> BaseModel:
        parsed = model.model_validate(payload)
        extra = getattr(parsed, "__pydantic_extra__", None)
        if not extra:
            return parsed

        unknown_fields = tuple(sorted(str(key) for key in extra))
        if validation_mode == "strict":
            fields_preview = ", ".join(unknown_fields[:10])
            if len(unknown_fields) > 10:
                fields_preview += ", ..."
            raise ValidationError(
                f"Unexpected fields in response for endpoint "
                f"'{endpoint_name}': {fields_preview}"
            )

        if validation_mode == "warn":
            warning_key = (endpoint_name, unknown_fields)
            if warning_key not in _extra_field_warnings_seen:
                _extra_field_warnings_seen.add(warning_key)
                logger.warning(
                    "Unknown response fields detected",
                    extra={
                        "endpoint": endpoint_name,
                        "unknown_fields": list(unknown_fields),
                        "count": len(unknown_fields),
                    },
                )
        return parsed

    @staticmethod
    def _validate_single_item(
        endpoint: Endpoint[T],
        item: Any,
        validation_mode: ValidationMode = "lenient",
    ) -> T:
        """Validate a single item against the endpoint's response model.

        Args:
            endpoint: The endpoint containing the response model
            item: The item to validate

        Returns:
            Validated model instance

        Raises:
            ValueError: If the model structure is invalid
        """
        # Handle primitive types and raw dict/bytes
        model = endpoint.response_model
        if model is str:
            return cast(T, str(item))
        if model is int:
            return cast(T, int(item))
        if model is float:
            return cast(T, float(item))
        if model is bool:
            return cast(T, bool(item))
        if model is dict:
            return cast(T, dict(item) if not isinstance(item, dict) else item)
        if model is bytes:
            return cast(T, bytes(item))

        if _is_pydantic_model(model):
            if isinstance(item, dict):
                return cast(
                    T,
                    BaseClient._validate_model(
                        endpoint.name,
                        model,
                        item,
                        validation_mode=validation_mode,
                    ),
                )

            # Try to feed non-dict value into the first field
            try:
                first_field = next(iter(model.__annotations__))
                field_info = model.model_fields[first_field]
                field_name = field_info.alias or first_field
                return cast(
                    T,
                    BaseClient._validate_model(
                        endpoint.name,
                        model,
                        {field_name: item},
                        validation_mode=validation_mode,
                    ),
                )
            except (StopIteration, KeyError, AttributeError) as exc:
                raise ValueError(
                    f"Invalid model structure for {model.__name__}"
                ) from exc

        raise ValueError(f"Unsupported response model: {model!r}")

    @staticmethod
    def _process_list_response(
        endpoint: Endpoint[T],
        data: list[Any],
        validation_mode: ValidationMode = "lenient",
    ) -> list[T]:
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
                processed_item = BaseClient._validate_single_item(
                    endpoint,
                    item,
                    validation_mode=validation_mode,
                )
                for warning in w:
                    logger.warning(f"Validation warning: {warning.message}")
                processed_items.append(processed_item)
        return processed_items

    @staticmethod
    def _process_response(
        endpoint: Endpoint[T],
        data: Any,
        validation_mode: ValidationMode = "lenient",
    ) -> T | list[T]:
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
            return BaseClient._process_list_response(
                endpoint,
                data,
                validation_mode=validation_mode,
            )

        # Process single item responses
        model = endpoint.response_model
        if model is str:
            return cast(T, str(data))
        if model is int:
            return cast(T, int(data))
        if model is float:
            return cast(T, float(data))
        if model is bool:
            return cast(T, bool(data))
        if model is dict:
            return cast(T, dict(data) if not isinstance(data, dict) else data)
        if model is bytes:
            return cast(T, data)
        if _is_pydantic_model(model):
            return cast(
                T,
                BaseClient._validate_model(
                    endpoint.name,
                    model,
                    data,
                    validation_mode=validation_mode,
                ),
            )
        raise ValueError(f"Unsupported response model: {model!r}")

    async def request_async(self, endpoint: Endpoint[T], **kwargs: Any) -> T | list[T]:
        """
        Make async request with rate limiting and retry logic, returning T or list[T].
        """
        _rate_limit_retry_count.set(0)  # Reset counter at start of new request

        # Create async retryer with configurable max_retries
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.config.max_retries),
            wait=self._wait_for_retry,
            retry=retry_if_exception(self._is_retryable_error),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True,
        )

        async for attempt in retryer:
            with attempt:
                return await self._execute_request_async(endpoint, **kwargs)

        # This should never be reached due to reraise=True
        raise FMPError("Async request failed after all retry attempts")

    async def request_async_list(self, endpoint: Endpoint[T], **kwargs: Any) -> list[T]:
        """Async counterpart of :meth:`request_list` (#235)."""
        return _unwrap_list_result(
            await self.request_async(endpoint, **kwargs),
            endpoint.response_model,
        )

    async def _execute_request_async(
        self, endpoint: Endpoint[T], **kwargs: Any
    ) -> T | list[T]:
        """
        Execute a single async request attempt with rate limiting.

        Args:
            endpoint: The Endpoint object describing the request.
            **kwargs: Request parameters.

        Returns:
            Either a single Pydantic model of type T or a list of T.
        """
        force_refresh = kwargs.pop("force_refresh", False)

        try:
            # Validate and process parameters
            validated_params = endpoint.validate_params(
                kwargs,
                unknown_param_policy=self.config.unknown_param_policy,
            )

            # Build URL
            url = endpoint.build_url(self.config.base_url, validated_params)

            # Extract query parameters and add API key
            query_params = endpoint.get_query_params(validated_params)
            query_params["apikey"] = self.config.api_key

            # Check cache before rate limiting — cache hits are free
            cache_key: str | None = None
            if (
                self._cache is not None
                and not force_refresh
                and endpoint.response_model is not bytes
            ):
                cache_key = self._build_cache_key(endpoint.name, query_params)
                cached = await self._cache_aget(endpoint.name, cache_key)
                if cached is not None:
                    self.logger.debug(
                        "Cache hit for %s",
                        endpoint.name,
                        extra={"endpoint": endpoint.name, "cache_key": cache_key},
                    )
                    return self._process_response(
                        endpoint,
                        cached,
                        validation_mode=self.config.validation_mode,
                    )

            # Check rate limit only when making an actual HTTP request
            if not await self._async_rate_limiter.should_allow_request():
                wait_time = self._async_rate_limiter.get_wait_time()
                current_count = _rate_limit_retry_count.get() + 1
                _rate_limit_retry_count.set(current_count)

                if current_count > self.max_rate_limit_retries:
                    _rate_limit_retry_count.set(0)
                    raise RateLimitError(
                        f"Rate limit exceeded after "
                        f"{self.max_rate_limit_retries} retries. "
                        f"Please wait {wait_time:.1f} seconds",
                        retry_after=wait_time,
                    )

                self.logger.warning(
                    f"Rate limit reached "
                    f"(attempt {current_count}/"
                    f"{self.max_rate_limit_retries}), "
                    f"waiting {wait_time:.1f} seconds before retrying"
                )
                await asyncio.sleep(wait_time)

            await self._async_rate_limiter.record_request()

            self.logger.debug(
                f"Making async request to {endpoint.name}",
                extra={
                    "url": url,
                    "endpoint": endpoint.name,
                    "method": endpoint.method.value,
                },
            )

            # Use persistent async client
            client = self._setup_async_client()
            response = await client.request(
                endpoint.method.value, url, params=query_params
            )
            try:
                data: bytes | dict[str, Any] | list[Any]
                if endpoint.response_model is bytes:
                    self._raise_response_for_status(response)
                    data = response.content
                else:
                    data = self.handle_response(endpoint, response)
                result = self._process_response(
                    endpoint,
                    data,
                    validation_mode=self.config.validation_mode,
                )

                # Store in cache
                if self._cache is not None and cache_key is not None:
                    ttl = self._get_cache_ttl(endpoint.name)
                    await self._cache_aset(endpoint.name, cache_key, data, ttl)

                return result
            finally:
                await response.aclose()

        except RateLimitError:
            # Re-raise rate limit errors to be handled by retry logic
            raise
        except Exception as e:
            self.logger.error(
                f"Async request failed: {e!s}",
                extra={"endpoint": endpoint.name, "error": str(e)},
                exc_info=True,
            )
            raise


class EndpointGroup:
    """Abstract base class for sync endpoint groups"""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance."""
        return self._client

    @staticmethod
    @overload
    def _unwrap_single(
        result: T | list[T],
        model: type[T],
        allow_none: Literal[False] = False,
    ) -> T: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: T | list[T],
        model: type[T],
        allow_none: Literal[True],
    ) -> T | None: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: Literal[False] = False,
    ) -> T: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: Literal[True],
    ) -> T | None: ...

    @staticmethod
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: bool = False,
    ) -> T | None:
        """
        Unwrap single item from potentially list response.

        Args:
            result: The result from client.request(), either a single item or list
            model: The expected model type (for error messages)
            allow_none: If True, return None for empty lists instead of raising

        Returns:
            The single item, or None if allow_none=True and result is empty list

        Raises:
            ValueError: If result is empty list and allow_none=False
        """
        if isinstance(result, list):
            if not result:
                if allow_none:
                    return None
                raise ValueError(
                    f"Expected at least one {model.__name__}, got empty list"
                )
            return cast(T, result[0])
        return cast(T, result)

    @staticmethod
    def _unwrap_list(result: T | list[T], model: type[T]) -> list[T]:
        """Normalize a ``request()`` result to ``list[T]`` (#235)."""
        return _unwrap_list_result(result, model)


class AsyncEndpointGroup:
    """Abstract base class for async endpoint groups.

    This is the async counterpart to EndpointGroup. All methods in subclasses
    should be async and use `await self.client.request_async()` instead of
    `self.client.request()`.
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance."""
        return self._client

    @staticmethod
    @overload
    def _unwrap_single(
        result: T | list[T],
        model: type[T],
        allow_none: Literal[False] = False,
    ) -> T: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: T | list[T],
        model: type[T],
        allow_none: Literal[True],
    ) -> T | None: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: Literal[False] = False,
    ) -> T: ...

    @staticmethod
    @overload
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: Literal[True],
    ) -> T | None: ...

    @staticmethod
    def _unwrap_single(
        result: Any,
        model: type[T],
        allow_none: bool = False,
    ) -> T | None:
        """
        Unwrap single item from potentially list response.

        Args:
            result: The result from client.request_async(), either a single item or list
            model: The expected model type (for error messages)
            allow_none: If True, return None for empty lists instead of raising

        Returns:
            The single item, or None if allow_none=True and result is empty list

        Raises:
            ValueError: If result is empty list and allow_none=False
        """
        if isinstance(result, list):
            if not result:
                if allow_none:
                    return None
                raise ValueError(
                    f"Expected at least one {model.__name__}, got empty list"
                )
            return cast(T, result[0])
        return cast(T, result)

    @staticmethod
    def _unwrap_list(result: T | list[T], model: type[T]) -> list[T]:
        """Normalize a ``request_async()`` result to ``list[T]`` (#235)."""
        return _unwrap_list_result(result, model)
