# fmp_data/schema.py
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseArgModel(BaseModel):
    """Base model for all API arguments"""

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
    limit: int | None = Field(default=40, ge=1, le=100, description="Number of periods")


class TimeSeriesBaseArg(SymbolArg, DateRangeArg):
    """Base model for time series data endpoints"""

    interval: IntervalEnum | None = Field(
        default=IntervalEnum.MIN_5, description="Time interval for data points"
    )
