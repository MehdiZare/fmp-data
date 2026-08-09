# fmp_data/schema.py
from datetime import date
from enum import Enum
from typing import Any
import warnings

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    field_validator,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

#: Deprecated in 2.7, removed in 3.0 (#153). Formatted with the concrete
#: subclass name so the warning names the model the caller actually used.
ARG_MODEL_DEPRECATION = (
    "{name} is deprecated and will be removed in 3.0. The hand-written "
    "argument models are read by nothing: LangChain tool schemas are built "
    "dynamically from each endpoint's mandatory_params/optional_params in "
    "fmp_data.lc.vector_store, and Endpoint.arg_model was never consulted. "
    "See https://github.com/MehdiZare/fmp-data/issues/153."
)


class DeprecatedArgModel(BaseModel):
    """Common base for the deprecated hand-written argument models (#153).

    It adds no fields and no configuration -- only a ``DeprecationWarning``
    on every validation, so importing the class stays silent while *using*
    one says so. ``mode="before"`` covers ``Model(...)`` and
    ``Model.model_validate(...)`` alike.

    Validation is not the only way these models get used: an "argument model"
    a downstream caller kept is most naturally handed to a tool/function
    schema generator, which calls ``model_json_schema()`` and never validates
    anything. ``__get_pydantic_json_schema__`` covers that path so such a
    caller is told too, rather than reaching 3.0 without a single warning.
    JSON-schema generation is lazy in pydantic v2 -- the core schema built at
    class-creation time does not invoke it -- so importing stays silent.

    Scheduled for removal in 3.0 together with every model that inherits it.
    """

    @model_validator(mode="before")
    @classmethod
    def _warn_deprecated_arg_model(cls, data: Any) -> Any:
        # stacklevel=2 does not reach the caller here: construction crosses
        # pydantic-core frames, so the warning reports against pydantic's
        # main.py. The class name is in the message, so per-class filtering
        # and dedup still work; there is no stacklevel that reliably lands on
        # user code through a compiled boundary.
        warnings.warn(
            ARG_MODEL_DEPRECATION.format(name=cls.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        return data

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        warnings.warn(
            ARG_MODEL_DEPRECATION.format(name=cls.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        return handler(core_schema)


class BaseArgModel(DeprecatedArgModel):
    """Base model for all API arguments.

    .. deprecated:: 2.7
        Removed in 3.0 -- see :data:`ARG_MODEL_DEPRECATION`.
    """

    model_config = ConfigDict(
        # Core config settings
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "title": "Base Arguments",
            "description": "Base arguments for FMP API endpoints",
        },
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """
        Override model_dump to ensure proper serialization.

        Args:
            **kwargs: Additional keyword arguments for model_dump

        Returns:
            dict[str, Any]: Serialized model data
        """
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("mode", "json")
        return super().model_dump(**kwargs)


class BaseEnum(str, Enum):
    """Base class for all enums to ensure consistent serialization"""

    @classmethod
    def values(cls) -> list[str]:
        """Get all enum values"""
        return [e.value for e in cls]


class ReportingPeriodEnum(BaseEnum):
    """Standard reporting periods"""

    ANNUAL = "annual"
    QUARTER = "quarter"
    FY = "FY"
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class StructureTypeEnum(BaseEnum):
    """Data structure types"""

    FLAT = "flat"
    NESTED = "nested"


class IntervalEnum(BaseEnum):
    """Standard time intervals"""

    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1hour"
    HOUR_4 = "4hour"


# Base argument models
class SymbolArg(BaseArgModel):
    """Base model for endpoints requiring a symbol"""

    symbol: str = Field(
        description="Stock symbol/ticker",
        pattern=r"^[A-Z]{1,5}$",
        json_schema_extra={
            "examples": ["AAPL", "MSFT", "GOOGL"],
            "description": "Stock ticker symbol (1-5 capital letters)",
        },
    )


class DateRangeArg(BaseArgModel):
    """Base model for date range arguments"""

    start_date: date | None = Field(
        None, description="Start date", json_schema_extra={"examples": ["2024-01-01"]}
    )
    end_date: date | None = Field(
        None, description="End date", json_schema_extra={"examples": ["2024-12-31"]}
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date | None, info: Any) -> date | None:
        if v is None:
            return v
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("end_date must be after start_date")
        return v


class PaginationArg(BaseArgModel):
    """Base model for paginated endpoints"""

    limit: int | None = Field(
        default=10, ge=1, le=1000, description="Maximum number of results"
    )
    page: int | None = Field(default=1, ge=1, description="Page number")


class SearchArg(BaseArgModel):
    """Base model for search endpoints"""

    query: str = Field(
        description="Search query string",
        min_length=2,
        json_schema_extra={"examples": ["Apple Inc", "Microsoft"]},
    )


class ExchangeArg(BaseArgModel):
    """Base model for exchange-related endpoints"""

    exchange: str = Field(
        description="Exchange code",
        pattern=r"^[A-Z]{2,6}$",
        min_length=2,
        max_length=6,
        json_schema_extra={"examples": ["NYSE", "NASDAQ"]},
    )


class NoParamArg(BaseArgModel):
    """Base model for endpoints that take no parameters"""

    pass


class FinancialStatementBaseArg(SymbolArg):
    """Base model for financial statement endpoints"""

    period: ReportingPeriodEnum = Field(
        default=ReportingPeriodEnum.ANNUAL, description="Reporting period"
    )
    limit: int | None = Field(
        default=40, ge=1, le=1000, description="Number of periods"
    )


class TimeSeriesBaseArg(SymbolArg, DateRangeArg):
    """Base model for time series data endpoints"""

    interval: IntervalEnum | None = Field(
        default=IntervalEnum.MIN_5, description="Time interval for data points"
    )
