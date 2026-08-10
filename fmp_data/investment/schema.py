# fmp_data/investment/schema.py

from datetime import date as dt_date

from pydantic import Field

from fmp_data.models import CIK
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

    # Optional, matching ETF_HOLDINGS.optional_params (#143). Probed against
    # the live API on 2026-08-08: etf/holdings?symbol=SPY returns 505 rows
    # with and without `date`, so the endpoint is right and this model was
    # the stricter side -- a caller satisfying the endpoint contract was
    # rejected by the tool schema before a request was ever built.
    date: dt_date | None = Field(
        None,
        description="Holdings date (defaults to the latest available)",
        json_schema_extra={"examples": ["2024-01-15"]},
    )


class ETFInfoArgs(SymbolArg):
    """Arguments for getting ETF information"""

    pass


class MutualFundHoldingsArgs(SymbolArg):
    """Arguments for getting mutual fund holdings"""

    # Required, matching MUTUAL_FUND_HOLDINGS.mandatory_params (#143). Unlike
    # ETFHoldingsArgs above, whether that is *correct* could not be settled:
    # the `mutual-fund-holdings` path 404s for every request, so there is no
    # response to check the declaration against. See #152 -- if that endpoint
    # is repointed or removed, revisit this field and the ParamType.STRING on
    # its endpoint param at the same time.
    date: dt_date = Field(
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

    cik: CIK | None = Field(
        None,
        description="CIK number (required for mutual funds)",
        pattern=r"^\d{10}$",
        json_schema_extra={"examples": ["0001234567"]},
    )
    fund_type: FundType = Field(
        description="Type of fund",
        json_schema_extra={"examples": ["ETF", "Mutual Fund"]},
    )
