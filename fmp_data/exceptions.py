# fmp_data/exceptions.py
"""Exceptions for FMP client."""
from typing import Any


class FMPException(Exception):
    """Base exception for FMP API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(FMPException):
    """Raised when API key is invalid or expired."""

    pass


class RateLimitExceeded(FMPException):
    """Raised when API rate limit is exceeded."""

    pass


class ValidationError(FMPException):
    """Raised when request validation fails."""

    pass


class APIError(FMPException):
    """Raised for general API errors."""

    pass
