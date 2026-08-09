from __future__ import annotations

from dataclasses import dataclass
from datetime import date as dt_date
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Generic, Literal, TypeVar
import warnings

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from fmp_data.schema import DeprecatedArgModel

if TYPE_CHECKING:
    pass


def _get_validation_error() -> type[Exception]:
    """
    Lazily import ValidationError to avoid circular imports.
    Returns the FMP ValidationError class.
    """
    from fmp_data.exceptions import ValidationError

    return ValidationError


T = TypeVar("T")

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


def _coerce_cik(value: Any) -> Any:
    """Coerce an integer CIK to its canonical zero-padded string form.

    A CIK is a fixed-width 10-digit zero-padded identifier. Every FMP
    endpoint observed returning one returns a string (probed 2026-08-07),
    but JSON producers drop leading zeros routinely, so an int is coerced
    rather than rejected.

    Strings pass through untouched: re-padding would rewrite whatever the
    API actually sent, which is a larger claim than the evidence supports.
    ``bool`` is excluded because it subclasses ``int``.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return f"{value:010d}"
    return value


# SEC Central Index Key, coerced from int to a 10-digit zero-padded string.
CIK = Annotated[str, BeforeValidator(_coerce_cik)]


class HTTPMethod(str, Enum):
    """HTTP methods supported by the API"""

    GET = "GET"
    POST = "POST"


class URLType(str, Enum):
    """Types of URL endpoints"""

    API = "api"  # Regular API endpoint with version prefix
    IMAGE = "image-stock"  # Image endpoint (e.g., company logos)
    DIRECT = "direct"  # Direct endpoint without version prefix


class APIVersion(str, Enum):
    """API versions supported by FMP"""

    V3 = "v3"  # Deprecated
    V4 = "v4"  # Deprecated
    STABLE = "stable"


class ParamLocation(str, Enum):
    """Parameter location in the request"""

    PATH = "path"  # URL path parameter
    QUERY = "query"  # Query string parameter


class ParamType(str, Enum):
    """Parameter data types"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    CIK = "cik"

    def convert_value(self, value: Any) -> Any:
        """Convert value to the appropriate type"""
        if value is None:
            return None

        try:
            if self is ParamType.STRING:
                return self._convert_to_string(value)
            if self is ParamType.INTEGER:
                return self._convert_to_integer(value)
            if self is ParamType.FLOAT:
                return self._convert_to_float(value)
            if self is ParamType.BOOLEAN:
                return self._convert_to_boolean(value)
            if self is ParamType.DATE:
                return self._convert_to_date(value)
            if self is ParamType.DATETIME:
                return self._convert_to_datetime(value)
            if self is ParamType.CIK:
                return self._convert_to_cik(value)
            raise ValueError(f"Unsupported type: {self}")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Failed to convert value '{value}' to type {self.value}: {e!s}"
            ) from e

    def _convert_to_string(self, value: Any) -> str:
        return str(value)

    def _convert_to_cik(self, value: Any) -> str:
        """Convert a CIK request parameter to its canonical wire form.

        FMP matches a CIK as a fixed-width 10-digit zero-padded string, so
        ``str(320193)`` -- what a plain STRING param would produce -- is a
        lookup that succeeds and returns nothing.

        This pads *numeric strings* too, which the response-side coercer
        deliberately does not: inbound, re-padding would misreport what the
        API actually sent, but outbound the padded form is simply the
        correct request and there is nothing to misreport. A non-numeric
        string is passed through so a bad value surfaces as an API error
        rather than being silently mangled into one.

        ``bool`` is rejected rather than stringified, matching the response
        side where pydantic refuses it: ``cik=True`` is never a real lookup.
        """
        if isinstance(value, bool):
            raise ValueError("CIK must be a string or an integer, not a bool")
        if isinstance(value, int):
            return f"{value:010d}"
        text = str(value)
        return text.zfill(10) if text.isdigit() else text

    def _convert_to_integer(self, value: Any) -> int:
        return int(value)

    def _convert_to_float(self, value: Any) -> float:
        return float(value)

    def _convert_to_boolean(self, value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)

    def _convert_to_date(self, value: Any) -> dt_date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, dt_date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    def _convert_to_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)


@dataclass
class EndpointParam:
    """Definition of an endpoint parameter"""

    name: str
    location: ParamLocation  # Changed from param_type to location
    param_type: ParamType  # Added to specify data type
    required: bool
    description: str
    default: Any = None
    alias: str | None = None
    valid_values: list[Any] | None = None

    def __post_init__(self) -> None:
        """Normalise ``valid_values`` to the values that travel over the wire.

        Endpoints may declare ``valid_values`` as enum members
        (``valid_values=list(EconomicIndicatorType)``). Every consumer wants
        the wire value, not the member: ``validate_value`` compares against a
        converted request value, and ``EndpointBasedRule._get_type_pattern``
        builds a regex from them. Unwrapping once here means neither consumer
        has to special-case ``Enum``.

        Only ``Enum`` is unwrapped -- values keep their native type. Coercing
        everything to ``str`` would break the membership check below for
        integer-typed params such as ``transcripts.quarter``
        (``valid_values=[1, 2, 3, 4]``), whose converted value is an ``int``.
        """
        if self.valid_values is not None:
            self.valid_values = [
                value.value if isinstance(value, Enum) else value
                for value in self.valid_values
            ]

    def validate_value(self, value: Any) -> Any:
        """Validate and convert parameter value.

        Raises:
            ValidationError: If value is None for required param or not in valid_values
        """
        ValidationError = _get_validation_error()

        if value is None:
            if self.required:
                raise ValidationError(f"Missing required parameter: {self.name}")
            return None

        # Convert to correct type
        try:
            converted_value = self.param_type.convert_value(value)
        except ValueError as e:
            raise ValidationError(f"Invalid value for {self.name}: {e}") from e

        # Validate against allowed values if specified
        if self.valid_values and converted_value not in self.valid_values:
            raise ValidationError(
                f"Invalid value for {self.name}. Must be one of: {self.valid_values}"
            )

        return converted_value


class Endpoint(BaseModel, Generic[T]):
    """Enhanced endpoint definition with type checking"""

    name: str
    path: str
    version: APIVersion | None = None
    url_type: URLType = URLType.API
    method: HTTPMethod = HTTPMethod.GET
    description: str
    mandatory_params: list[EndpointParam]
    optional_params: list[EndpointParam] | None
    response_model: type[T]
    allow_empty_on_404: bool = True
    #: .. deprecated:: 2.7
    #:     Removed in 3.0 (#153). Read by nothing: LangChain builds argument
    #:     schemas dynamically from ``mandatory_params``/``optional_params``
    #:     in ``fmp_data.lc.vector_store``, so setting this changes nothing.
    #:     No endpoint in this package sets it any more.
    arg_model: type[BaseModel] | None = None
    example_queries: list | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def _warn_deprecated_arg_model(cls, data: Any) -> Any:
        """Warn only when a caller actually supplies an ``arg_model``.

        ``arg_model=None`` is the default and stays silent, so passing it
        explicitly -- as a few tests do to pin the field's absence -- is not
        flagged as use of the deprecated mechanism.
        """
        if isinstance(data, dict) and data.get("arg_model") is not None:
            warnings.warn(
                "Endpoint.arg_model is deprecated and will be removed in 3.0. "
                "It is read by nothing -- LangChain tool schemas are built "
                "dynamically from mandatory_params/optional_params in "
                "fmp_data.lc.vector_store. Drop the argument; no behaviour "
                "depends on it. "
                "See https://github.com/MehdiZare/fmp-data/issues/153.",
                DeprecationWarning,
                stacklevel=2,
            )
        return data

    def build_url(self, base_url: str, params: dict[str, Any]) -> str:
        """Build the complete URL for the endpoint based on URL type"""
        path = self.path
        for param in self.mandatory_params:
            if param.location == ParamLocation.PATH and param.name in params:
                path = path.replace(f"{{{param.name}}}", str(params[param.name]))

        if self.url_type == URLType.API and self.version:
            return f"{base_url}/{self.version.value}/{path}"
        elif self.url_type == URLType.IMAGE:
            return f"{base_url}/{self.url_type.value}/{path}"
        else:
            return f"{base_url}/{path}"

    def _build_param_lookup(self) -> dict[str, EndpointParam]:
        """Build a lookup dict mapping both param names and aliases to params."""
        lookup: dict[str, EndpointParam] = {}
        for param in self.mandatory_params + (self.optional_params or []):
            lookup[param.name] = param
            if param.alias:
                lookup[param.alias] = param
        return lookup

    def validate_params(  # noqa: C901
        self,
        provided_params: dict[str, Any],
        strict: bool = False,
        unknown_param_policy: Literal["ignore", "warn", "error"] | None = None,
    ) -> dict[str, Any]:
        """
        Validate provided parameters against endpoint definition.

        Args:
            provided_params: Dictionary of parameters provided by the caller
            strict: If True, raise ValidationError on unknown parameter keys
            unknown_param_policy: Policy for unknown keys ('ignore', 'warn', 'error').
                If not provided, strict=True maps to 'error' and strict=False to
                'ignore'.

        Returns:
            Dictionary of validated parameters with wire keys (aliases where defined)

        Raises:
            ValidationError: If required params missing or unknown keys in strict
        """
        ValidationError = _get_validation_error()

        validated: dict[str, Any] = {}
        param_lookup = self._build_param_lookup()
        mandatory_names = {p.name for p in self.mandatory_params}
        seen_params: set[str] = set()
        policy: Literal["ignore", "warn", "error"]
        if strict:
            policy = "error"
        elif unknown_param_policy is None:
            policy = "ignore"
        else:
            policy = unknown_param_policy

        # Process provided parameters
        for key, value in provided_params.items():
            param = param_lookup.get(key)
            if param is None:
                if policy == "error":
                    raise ValidationError(f"Unknown parameter: {key}")
                if policy == "warn":
                    warnings.warn(
                        (
                            f"Unknown parameter '{key}' ignored for endpoint "
                            f"'{self.name}'."
                        ),
                        stacklevel=2,
                    )
                continue  # Silently ignore in non-strict mode

            # Skip if we've already processed this param (via name or alias)
            if param.name in seen_params:
                continue
            seen_params.add(param.name)

            # Skip None values for optional params
            if value is None and param.name not in mandatory_names:
                continue

            validated_value = param.validate_value(value)
            if validated_value is not None or param.name in mandatory_names:
                wire_key = param.alias or param.name
                validated[wire_key] = validated_value

        # Check mandatory params are present
        for param in self.mandatory_params:
            if param.name not in seen_params:
                raise ValidationError(f"Missing mandatory parameter: {param.name}")

        # Apply validated defaults for optional params not provided
        for param in self.optional_params or []:
            if param.name not in seen_params and param.default is not None:
                # Validate the default value
                validated_default = param.validate_value(param.default)
                wire_key = param.alias or param.name
                validated[wire_key] = validated_default

        return validated

    def get_query_params(self, validated_params: dict) -> dict[str, Any]:
        """Extract query parameters from validated parameters"""
        return {
            k: v
            for k, v in validated_params.items()
            if any(
                p.location == ParamLocation.QUERY and (p.name == k or p.alias == k)
                for p in self.mandatory_params + (self.optional_params or [])
            )
        }


class BaseSymbolArg(DeprecatedArgModel):
    """Base model for any endpoint requiring just a symbol.

    .. deprecated:: 2.7
        Removed in 3.0 -- see :data:`fmp_data.schema.ARG_MODEL_DEPRECATION`.
    """

    model_config = default_model_config

    symbol: str = Field(
        description="Stock symbol/ticker of the company (e.g., AAPL, MSFT)",
        pattern=r"^[A-Z]{1,5}$",
    )


class ShareFloat(BaseModel):
    """Share float information"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime | None = Field(
        None, description="Data date"
    )  # Example: "2024-12-09 12:10:05"
    free_float: float | None = Field(
        None, description="Free float percentage"
    )  # Example: 55.73835
    float_shares: float | None = Field(
        None, description="Number of floating shares"
    )  # Example: 36025816
    outstanding_shares: float | None = Field(
        None, description="Total outstanding shares"
    )
    source: str | None = Field(None, description="Data source")


class MarketCapitalization(BaseModel):
    """Market capitalization data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    date: datetime | None = Field(None, description="Date")
    market_cap: float | None = Field(None, description="Market capitalization")


class CompanySymbol(BaseModel):
    """Company symbol information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current stock price")
    exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Exchange short name"
    )
    type: str | None = Field(None, description="Security type")
    company_name: str | None = Field(default=None)
    reporting_currency: str | None = Field(default=None)
    trading_currency: str | None = Field(default=None)
