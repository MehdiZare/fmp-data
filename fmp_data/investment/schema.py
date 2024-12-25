# fmp_data/investment/schema.py

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class ETFAssetCategory(str, Enum):
    """Categories of ETF assets"""

    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    COMMODITY = "Commodity"
    REAL_ESTATE = "Real Estate"
    CURRENCY = "Currency"
    MULTI_ASSET = "Multi-Asset"
    ALTERNATIVE = "Alternative"


class FundType(str, Enum):
    """Types of investment funds"""

    ETF = "ETF"
    MUTUAL_FUND = "Mutual Fund"
    CLOSED_END = "Closed End Fund"
    HEDGE_FUND = "Hedge Fund"


class ETFHoldingsArgs(BaseModel):
    """Arguments for getting ETF holdings"""

    symbol: str = Field(description="ETF symbol")
    date: date = Field(description="Holdings date")


class ETFInfoArgs(BaseModel):
    """Arguments for getting ETF information"""

    symbol: str = Field(description="ETF symbol")


class MutualFundHoldingsArgs(BaseModel):
    """Arguments for getting mutual fund holdings"""

    symbol: str = Field(description="Fund symbol")
    date: date = Field(description="Holdings date")


class MutualFundSearchArgs(BaseModel):
    """Arguments for searching mutual funds by name"""

    name: str = Field(description="Fund name or partial name to search")


class FundHolderArgs(BaseModel):
    """Arguments for getting fund holder information"""

    symbol: str = Field(description="Fund symbol")
    fund_type: FundType = Field(description="Type of fund (ETF or Mutual Fund)")


class WeightingType(str, Enum):
    """Types of portfolio weightings"""

    SECTOR = "sector"
    COUNTRY = "country"
    ASSET_CLASS = "asset_class"
    MARKET_CAP = "market_cap"
    CURRENCY = "currency"


class WeightingArgs(BaseModel):
    """Arguments for getting fund weightings"""

    symbol: str = Field(description="Fund symbol")
    weighting_type: WeightingType = Field(description="Type of weighting to retrieve")


class PortfolioDateArgs(BaseModel):
    """Arguments for getting portfolio dates"""

    symbol: str = Field(description="Fund symbol")
    cik: str | None = Field(None, description="CIK number (required for mutual funds)")
    fund_type: FundType = Field(description="Type of fund (ETF or Mutual Fund)")
