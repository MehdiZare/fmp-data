# fmp_data/company/schema.py

from pydantic import BaseModel, ConfigDict, Field

from fmp_data.schema import (
    ExchangeArg,
    NoParamArg,
    PaginationArg,
    ReportingPeriodEnum,
    SearchArg,
    StructureTypeEnum,
    SymbolArg,
)


# Profile and Core Information
class ProfileArgs(SymbolArg):
    """Arguments for getting company profile"""

    pass


class SearchArgs(SearchArg, PaginationArg):
    """Arguments for company search"""

    exchange: str | None = Field(
        None,
        description="Filter by stock exchange",
        pattern=r"^[A-Z]{2,6}$",
        json_schema_extra={"examples": ["NYSE", "NASDAQ"]},
    )


# Search Related
class CIKSearchArgs(SearchArg):
    """Arguments for CIK search"""

    pass


class CUSIPSearchArgs(SearchArg):
    """Arguments for CUSIP search"""

    pass


class ISINSearchArgs(SearchArg):
    """Arguments for ISIN search"""

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


# List Related
class StockListArgs(NoParamArg):
    """Arguments for getting stock list"""

    pass


class ETFListArgs(NoParamArg):
    """Arguments for getting ETF list"""

    pass


class AvailableIndexesArgs(NoParamArg):
    """Arguments for getting available indexes"""

    pass


class ExchangeSymbolsArgs(ExchangeArg):
    """Arguments for getting exchange symbols"""

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


# Revenue Related
class RevenueSegmentationArgs(SymbolArg):
    """Base arguments for revenue segmentation"""

    structure: StructureTypeEnum = Field(
        default=StructureTypeEnum.FLAT, description="Data structure format"
    )
    period: ReportingPeriodEnum = Field(
        default=ReportingPeriodEnum.ANNUAL, description="Data period"
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


class BaseSymbolArg(BaseModel):
    """Base model for any endpoint requiring just a symbol"""

    symbol: str = Field(
        description="Stock symbol/ticker of the company (e.g., AAPL, MSFT)",
        pattern=r"^[A-Z]{1,5}$",
    )


class BaseSearchArg(BaseModel):
    """Base model for search-type endpoints"""

    query: str = Field(description="Search query string", min_length=2)


class BaseExchangeArg(BaseModel):
    """Base model for exchange-related queries"""

    exchange: str = Field(
        description="Exchange code (e.g., NYSE, NASDAQ)",
        pattern=r"^[A-Z]{2,6}$",
        min_length=2,
        max_length=6,
        examples=["NYSE", "NASDAQ", "LSE", "TSX"],
    )


class CoreInformationArgs(BaseSymbolArg):
    """Arguments for getting core company information"""

    pass


class ExchangeArgs(BaseExchangeArg):
    """Arguments for getting exchange symbols

    Extends BaseExchangeArg to potentially add more specific parameters
    in the future while maintaining backward compatibility
    """

    pass


# Revenue Related
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


class ProductRevenueArgs(RevenueSegmentationArgs):
    """Arguments for product revenue segmentation"""

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Product Revenue Arguments",
            "description": "Arguments for getting product revenue data",
            "examples": [{"symbol": "AAPL", "period": "annual", "structure": "flat"}],
        }
    )
