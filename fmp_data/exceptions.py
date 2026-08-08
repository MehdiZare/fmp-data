# exceptions.py
from typing import Any


class FMPError(Exception):
    """Base exception for FMP API errors"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | list[Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class RateLimitError(FMPError):
    """Raised when API rate limit is exceeded"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | list[Any] | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after is not None:
            return f"{base_msg} (retry after {self.retry_after:.1f} seconds)"
        return base_msg


class AuthenticationError(FMPError):
    """Raised when API key is invalid or missing"""

    pass


class ValidationError(FMPError):
    """Raised when request parameters are invalid"""

    pass


class ConfigError(FMPError):
    """Raised when there's a configuration error"""

    pass


class InvalidSymbolError(ValidationError):
    """Raised when a required symbol is missing or blank."""

    def __init__(self, message: str = "Symbol is required and cannot be blank"):
        super().__init__(message)


class InvalidResponseTypeError(FMPError):
    """Raised when an API response has an unexpected type."""

    def __init__(
        self,
        endpoint_name: str,
        expected_type: str,
        actual_type: str | None = None,
    ):
        msg = f"Invalid response type for {endpoint_name}: expected {expected_type}"
        if actual_type:
            msg += f", got {actual_type}"
        super().__init__(msg)


class DependencyError(ConfigError):
    """Raised when a required optional dependency is not installed."""

    def __init__(self, feature: str, install_command: str):
        msg = (
            f"{feature} dependencies are not installed. "
            f"Install them with: {install_command}"
        )
        super().__init__(msg)
        self.feature = feature
        self.install_command = install_command


class FMPNotFound(FMPError):
    """Raised when a requested symbol or resource cannot be found."""

    def __init__(self, symbol: str):
        super().__init__(f"Symbol {symbol} not found")


class VectorStoreCreationError(FMPError):
    """Raised when ``fmp_data.lc.create_vector_store`` cannot build a store.

    Replaces the ``None`` that function used to return on any failure (#133).
    ``None`` was reachable from exactly one place -- a blanket
    ``except Exception`` -- so it meant "something threw" and nothing more,
    which also cancelled out the loud-failure behaviour #121/#127 added to
    ``setup_registry``.

    Attributes:
        cause: the exception that actually stopped the build. Also set as
            ``__cause__``; exposed as a named attribute so callers can branch
            on it without reaching into dunders.
        failures: endpoint name -> validation error, for endpoints
            ``EndpointRegistry.register_batch`` skipped before the failure.
            Always a dict, never ``None``. Empty when the build failed before
            registration, or when nothing was skipped.

    Lives in the core exceptions module, not under ``fmp_data.lc``, so
    ``except VectorStoreCreationError`` is importable without the ``langchain``
    extra installed.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        failures: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.cause = cause
        self.failures: dict[str, str] = dict(failures or {})

    def __str__(self) -> str:
        """Include the skipped endpoints, so ``log.error(exc)`` keeps them.

        ``failures`` is the data #133 made programmatically reachable; leaving
        it out of the string form loses it again for every caller that logs the
        exception rather than destructuring it. Follows ``RateLimitError``,
        which appends ``retry_after`` the same way.
        """
        base = super().__str__()
        if not self.failures:
            return base
        skipped = ", ".join(
            f"{name}: {error}" for name, error in sorted(self.failures.items())
        )
        return f"{base} ({len(self.failures)} endpoint(s) skipped -- {skipped})"
