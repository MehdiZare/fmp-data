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
