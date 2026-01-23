from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

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
            raise ValueError(f"Unsupported type: {self}")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Failed to convert value '{value}' to type {self.value}: {e!s}"
            ) from e

    def _convert_to_string(self, value: Any) -> str:
        return str(value)

    def _convert_to_integer(self, value: Any) -> int:
        return int(value)

    def _convert_to_float(self, value: Any) -> float:
        return float(value)

    def _convert_to_boolean(self, value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)

    def _convert_to_date(self, value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
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
    arg_model: type[BaseModel] | None = None
    example_queries: list | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        self, provided_params: dict, strict: bool = False
    ) -> dict[str, Any]:
        """
        Validate provided parameters against endpoint definition.

        Args:
            provided_params: Dictionary of parameters provided by the caller
            strict: If True, raise ValidationError on unknown parameter keys

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

        # Process provided parameters
        for key, value in provided_params.items():
            param = param_lookup.get(key)
            if param is None:
                if strict:
                    raise ValidationError(f"Unknown parameter: {key}")
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


class BaseSymbolArg(BaseModel):
    """Base model for any endpoint requiring just a symbol"""

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
