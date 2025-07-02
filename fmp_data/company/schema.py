# fmp_data/company/schema.py
from __future__ import annotations

from enum import Enum

from pydantic import ConfigDict, Field

from fmp_data.models import BaseSymbolArg
from fmp_data.schema import (
    NoParamArg,
    ReportingPeriodEnum,
    StructureTypeEnum,
    SymbolArg,
)


class IntradayTimeInterval(str, Enum):
    """Available time intervals for intraday data"""

    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    ONE_HOUR = "1hour"
    FOUR_HOURS = "4hour"


# Profile and Core Information
class ProfileArgs(SymbolArg):
    """Arguments for getting company profile"""

    pass


# Executive Related
class ExecutivesArgs(SymbolArg):
    """Arguments for getting company executives"""

    pass


class ExecutiveCompensationArgs(SymbolArg):
    """Arguments for getting executive compensation"""

    pass


# Company Data
class CompanyNotesArgs(SymbolArg):
    """Arguments for getting company notes"""

    pass


class EmployeeCountArgs(SymbolArg):
    """Arguments for getting employee count"""

    pass


# Float Related
class ShareFloatArgs(SymbolArg):
    """Arguments for getting share float data"""

    pass


class HistoricalShareFloatArgs(SymbolArg):
    """Arguments for getting historical share float"""

    pass


class AllSharesFloatArgs(NoParamArg):
    """Arguments for getting all shares float"""

    pass


class RevenueSegmentationArgs(SymbolArg):
    """Base arguments for revenue segmentation"""

    structure: StructureTypeEnum = Field(
        default=StructureTypeEnum.FLAT,
        description="Data structure format",
        json_schema_extra={"enum": ["flat", "nested"], "examples": ["flat"]},
    )
    period: ReportingPeriodEnum = Field(
        default=ReportingPeriodEnum.ANNUAL,
        description="Data period",
        json_schema_extra={"enum": ["annual", "quarter"], "examples": ["annual"]},
    )


class GeographicRevenueArgs(RevenueSegmentationArgs):
    """Arguments for geographic revenue segmentation"""

    pass


# Symbol Related
class LogoArgs(SymbolArg):
    """Arguments for company logo endpoint"""

    pass


class SymbolChangesArgs(NoParamArg):
    """Arguments for getting symbol changes"""

    pass


class CoreInformationArgs(BaseSymbolArg):
    """Arguments for getting core company information"""

    pass


# Revenue Related


class ProductRevenueArgs(RevenueSegmentationArgs):
    """Arguments for product revenue segmentation"""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Product Revenue Arguments",
            "description": "Arguments for getting product revenue data",
            "examples": [{"symbol": "AAPL", "period": "annual", "structure": "flat"}],
        }
    )
