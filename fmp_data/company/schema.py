# fmp_data/company/schema.py
from typing import Literal

from pydantic import BaseModel, Field, field_validator


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


# Profile and Core Information
class ProfileArgs(BaseSymbolArg):
    """Arguments for getting company profile"""

    pass


class CoreInformationArgs(BaseSymbolArg):
    """Arguments for getting core company information"""

    pass


# Search Related
class SearchArgs(BaseModel):
    """Arguments for company search"""

    query: str = Field(description="Search term to find companies", min_length=2)
    limit: int = Field(
        default=10, description="Maximum number of results to return", ge=1, le=100
    )
    exchange: str | None = Field(
        None,
        description="Filter results by stock exchange (e.g., NYSE, NASDAQ)",
        pattern=r"^[A-Z]{2,6}$",
    )


class CIKSearchArgs(BaseSearchArg):
    """Arguments for CIK search"""

    pass


class CUSIPSearchArgs(BaseSearchArg):
    """Arguments for CUSIP search"""

    pass


class ISINSearchArgs(BaseSearchArg):
    """Arguments for ISIN search"""

    pass


# Executive Related
class ExecutivesArgs(BaseSymbolArg):
    """Arguments for getting company executives"""

    pass


class ExecutiveCompensationArgs(BaseSymbolArg):
    """Arguments for getting executive compensation"""

    pass


# Company Data
class CompanyNotesArgs(BaseSymbolArg):
    """Arguments for getting company notes"""

    pass


class EmployeeCountArgs(BaseSymbolArg):
    """Arguments for getting employee count"""

    pass


# List Related
class StockListArgs(BaseModel):
    """Arguments for getting stock list - no parameters needed"""

    pass


class ETFListArgs(BaseModel):
    """Arguments for getting ETF list - no parameters needed"""

    pass


class AvailableIndexesArgs(BaseModel):
    """Arguments for getting available indexes - no parameters needed"""

    pass


class ExchangeSymbolsArgs(BaseModel):
    """Arguments for getting exchange symbols"""

    exchange: str = Field(
        description="Exchange code (e.g., NYSE, NASDAQ)", pattern=r"^[A-Z]{2,6}$"
    )


class ExchangeArgs(BaseExchangeArg):
    """Arguments for getting exchange symbols

    Extends BaseExchangeArg to potentially add more specific parameters
    in the future while maintaining backward compatibility
    """

    pass


# Float Related
class ShareFloatArgs(BaseSymbolArg):
    """Arguments for getting share float data"""

    pass


class HistoricalShareFloatArgs(BaseSymbolArg):
    """Arguments for getting historical share float"""

    pass


class AllSharesFloatArgs(BaseModel):
    """Arguments for getting all shares float - no parameters needed"""

    pass


# Revenue Related
class RevenueSegmentationArgs(BaseModel):
    """Base arguments for revenue segmentation"""

    symbol: str = Field(
        description="Company symbol (e.g., AAPL)", pattern=r"^[A-Z]{1,5}$"
    )
    structure: str = Field(default="flat", description="Data structure format")
    period: Literal["annual", "quarter"] = Field(
        default="annual", description="Data period (annual or quarterly)"
    )

    @field_validator("structure")
    def validate_structure(cls, v: str) -> str:
        if v not in ["flat", "nested"]:
            raise ValueError("Structure must be either 'flat' or 'nested'")
        return v


class ProductRevenueArgs(RevenueSegmentationArgs):
    """Arguments for product revenue segmentation"""

    pass


class GeographicRevenueArgs(BaseModel):
    """Arguments for geographic revenue segmentation"""

    symbol: str = Field(
        description="Company symbol (e.g., AAPL)", pattern=r"^[A-Z]{1,5}$"
    )
    structure: str = Field(default="flat", description="Data structure format")

    @field_validator("structure")
    def validate_structure(cls, v: str) -> str:
        if v not in ["flat", "nested"]:
            raise ValueError("Structure must be either 'flat' or 'nested'")
        return v


# Symbol Related
class LogoArgs(BaseSymbolArg):
    """Arguments for company logo endpoint"""

    pass


class SymbolChangesArgs(BaseModel):
    """Arguments for getting symbol changes - no parameters needed"""

    pass
