from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


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

    V3 = "v3"
    V4 = "v4"
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
            match self:
                case ParamType.STRING:
                    return self._convert_to_string(value)
                case ParamType.INTEGER:
                    return self._convert_to_integer(value)
                case ParamType.FLOAT:
                    return self._convert_to_float(value)
                case ParamType.BOOLEAN:
                    return self._convert_to_boolean(value)
                case ParamType.DATE:
                    return self._convert_to_date(value)
                case ParamType.DATETIME:
                    return self._convert_to_datetime(value)
            raise ValueError(f"Unsupported type: {self}")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Failed to convert value '{value}' to type {self.value}: {str(e)}"
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
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
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
        """Validate and convert parameter value"""
        if value is None:
            if self.required:
                raise ValueError(f"Missing required parameter: {self.name}")
            return None

        # Convert to correct type
        converted_value = self.param_type.convert_value(value)

        # Validate against allowed values if specified
        if self.valid_values and converted_value not in self.valid_values:
            raise ValueError(
                f"Invalid value for {self.name}. "
                f"Must be one of: {self.valid_values}"
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

    def validate_params(self, provided_params: dict) -> dict[str, Any]:
        """Validate provided parameters against endpoint definition"""
        validated = {}

        # Validate mandatory parameters
        for param in self.mandatory_params:
            if param.name not in provided_params:
                raise ValueError(f"Missing mandatory parameter: {param.name}")

            value = param.validate_value(provided_params[param.name])
            validated[param.name] = value

        # Validate optional parameters
        for param in self.optional_params or []:
            if param.name in provided_params:
                value = param.validate_value(provided_params[param.name])
                key = param.alias or param.name
                validated[key] = value
            elif param.default is not None:
                key = param.alias or param.name
                validated[key] = param.default

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
