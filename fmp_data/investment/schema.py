# fmp_data/investment/schema.py

from datetime import date

from pydantic import Field

from fmp_data.schema import BaseArgModel, BaseEnum, SymbolArg


class ETFAssetCategory(BaseEnum):
    """Categories of ETF assets"""

    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    COMMODITY = "Commodity"
    REAL_ESTATE = "Real Estate"
    CURRENCY = "Currency"
    MULTI_ASSET = "Multi-Asset"
    ALTERNATIVE = "Alternative"


class FundType(BaseEnum):
    """Types of investment funds"""

    ETF = "ETF"
    MUTUAL_FUND = "Mutual Fund"
    CLOSED_END = "Closed End Fund"
    HEDGE_FUND = "Hedge Fund"


class WeightingType(BaseEnum):
    """Types of portfolio weightings"""

    SECTOR = "sector"
    COUNTRY = "country"
    ASSET_CLASS = "asset_class"
    MARKET_CAP = "market_cap"
    CURRENCY = "currency"


class ETFHoldingsArgs(SymbolArg):
    """Arguments for getting ETF holdings"""

    date: date = Field(
        description="Holdings date", json_schema_extra={"examples": ["2024-01-15"]}
    )


class ETFInfoArgs(SymbolArg):
    """Arguments for getting ETF information"""

    pass


class MutualFundHoldingsArgs(SymbolArg):
    """Arguments for getting mutual fund holdings"""

    date: date = Field(
        description="Holdings date", json_schema_extra={"examples": ["2024-01-15"]}
    )


class MutualFundSearchArgs(BaseArgModel):
    """Arguments for searching mutual funds by name"""

    name: str = Field(
        description="Fund name or partial name to search",
        min_length=2,
        json_schema_extra={"examples": ["Vanguard 500", "Fidelity Growth"]},
    )


class FundHolderArgs(SymbolArg):
    """Arguments for getting fund holder information"""

    fund_type: FundType = Field(
        description="Type of fund",
        json_schema_extra={
            "examples": ["ETF", "Mutual Fund"],
            "description": "Specifies whether the fund is an ETF or Mutual Fund",
        },
    )


class WeightingArgs(SymbolArg):
    """Arguments for getting fund weightings"""

    weighting_type: WeightingType = Field(
        description="Type of weighting to retrieve",
        json_schema_extra={"examples": ["sector", "country", "asset_class"]},
    )


class PortfolioDateArgs(SymbolArg):
    """Arguments for getting portfolio dates"""

    cik: str | None = Field(
        None,
        description="CIK number (required for mutual funds)",
        pattern=r"^\d{10}$",
        json_schema_extra={"examples": ["0001234567"]},
    )
    fund_type: FundType = Field(
        description="Type of fund",
        json_schema_extra={"examples": ["ETF", "Mutual Fund"]},
    )
