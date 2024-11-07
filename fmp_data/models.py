from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIVersion(str, Enum):
    """API versions supported by FMP"""

    V3 = "v3"
    V4 = "v4"
    STABLE = "stable"


class ParamType(str, Enum):
    """Parameter types for endpoints"""

    PATH = "path"
    QUERY = "query"


@dataclass
class EndpointParam:
    """Definition of an endpoint parameter"""

    name: str
    param_type: ParamType
    required: bool
    type: type
    description: str
    default: Any = None
    alias: str | None = None
    valid_values: list[Any] | None = None


class Endpoint(BaseModel, Generic[T]):
    """Enhanced endpoint definition with type checking"""

    name: str
    path: str
    version: APIVersion
    description: str
    mandatory_params: list[EndpointParam]
    optional_params: list[EndpointParam] = Field(default_factory=list)
    response_model: type[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def validate_params(self, provided_params: dict) -> dict[str, Any]:
        """Validate provided parameters against endpoint definition"""
        validated = {}

        # Check mandatory parameters
        for param in self.mandatory_params:
            if param.param_type == ParamType.PATH:
                if param.name not in provided_params:
                    raise ValueError(f"Missing mandatory path parameter: {param.name}")
            elif param.name not in provided_params:
                raise ValueError(f"Missing mandatory parameter: {param.name}")

            value = provided_params[param.name]
            if param.valid_values and value not in param.valid_values:
                raise ValueError(
                    f"Invalid value for {param.name}. "
                    f"Must be one of: {param.valid_values}"
                )
            validated[param.name] = value

        # Process optional parameters
        for param in self.optional_params:
            if param.name in provided_params:
                value = provided_params[param.name]
                if param.valid_values and value not in param.valid_values:
                    raise ValueError(
                        f"Invalid value for {param.name}. "
                        f"Must be one of: {param.valid_values}"
                    )
                validated[param.name if not param.alias else param.alias] = value
            elif param.default is not None:
                validated[param.name if not param.alias else param.alias] = (
                    param.default
                )

        return validated

    def build_url(self, base_url: str, params: dict[str, Any]) -> str:
        """Build the complete URL for the endpoint"""
        path = self.path
        for param in self.mandatory_params:
            if param.param_type == ParamType.PATH and param.name in params:
                path = path.replace(f"{{{param.name}}}", str(params[param.name]))
        return f"{base_url}/{self.version.value}/{path}"
