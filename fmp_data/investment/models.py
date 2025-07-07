# fmp_data/investment/models.py
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class ETFHolding(BaseModel):
    """ETF holding information"""

    model_config = default_model_config

    cik: str = Field(description="Central Index Key (CIK)")
    acceptance_time: datetime | None = Field(
        None, description="Acceptance time of the filing"
    )
    holding_date: date | None = Field(None, description="Holding date")
    symbol: str = Field(description="Ticker symbol")
    name: str = Field(description="Asset name")
    lei: str | None = Field(description="Legal Entity Identifier (LEI)")
    title: str = Field(description="Asset title")
    cusip: str | None = Field(description="Asset CUSIP")
    isin: str | None = Field(description="Asset ISIN")
    balance: float | None = Field(None, description="Number of shares held")
    units: str = Field(description="Units type")
    currency_code: str = Field(alias="cur_cd", description="Currency code")
    value_usd: Decimal = Field(alias="valUsd", description="Market value in USD")
    percentage_value: Decimal = Field(
        alias="pctVal", description="Percentage of total value"
    )
    payoff_profile: str | None = Field(None, description="Payoff profile")
    asset_category: str = Field(alias="assetCat", description="Asset category")
    issuer_category: str = Field(alias="issuerCat", description="Issuer category")
    investment_country: str = Field(
        alias="invCountry", description="Investment country"
    )
    is_restricted_security: bool = Field(
        alias="isRestrictedSec", description="Is restricted security"
    )
    fair_value_level: str = Field(alias="fairValLevel", description="Fair value level")
    is_cash_collateral: bool = Field(
        alias="isCashCollateral", description="Is cash collateral"
    )
    is_non_cash_collateral: bool = Field(
        alias="isNonCashCollateral", description="Is non-cash collateral"
    )
    is_loan_by_fund: bool = Field(alias="isLoanByFund", description="Is loan by fund")


class ETFSectorExposure(BaseModel):
    """Sector exposure within the ETF"""

    model_config = default_model_config

    industry: str = Field(description="Sector or industry name")
    exposure: float = Field(description="Exposure percentage to the sector")


class ETFInfo(BaseModel):
    """ETF information"""

    model_config = default_model_config

    symbol: str = Field(description="ETF symbol")
    name: str = Field(description="ETF name")
    expense_ratio: float = Field(alias="expenseRatio", description="Expense ratio")
    assets_under_management: float | None = Field(
        None, alias="aum", description="Assets under management"
    )
    avg_volume: int = Field(alias="avgVolume", description="Average volume")
    cusip: str = Field(description="CUSIP identifier for the ETF")
    isin: str = Field(description="ISIN identifier for the ETF")
    description: str = Field(description="ETF description")
    domicile: str = Field(description="Country of domicile")
    etf_company: str = Field(alias="etfCompany", description="ETF issuer company")
    inception_date: date = Field(alias="inceptionDate", description="Inception date")
    nav: Decimal = Field(description="Net Asset Value (NAV)")
    nav_currency: str = Field(alias="navCurrency", description="Currency of NAV")
    sectors_list: list[ETFSectorExposure] | None = Field(
        None, alias="sectorsList", description="List of sector exposures"
    )
    website: str = Field(description="ETF website")
    holdings_count: int = Field(alias="holdingsCount", description="Number of holdings")


class ETFSectorWeighting(BaseModel):
    """ETF sector weighting"""

    model_config = default_model_config

    sector: str = Field(description="Sector name")
    weight_percentage: float = Field(
        alias="weightPercentage", description="Sector weight percentage"
    )

    @field_validator("weight_percentage", mode="before")
    def parse_weight_percentage(cls, value: str) -> float:
        """Parse percentage string into float"""
        if isinstance(value, str) and value.endswith("%"):
            return float(value.strip("%")) / 100
        return float(value)


class ETFCountryWeighting(BaseModel):
    """ETF country weighting"""

    model_config = default_model_config

    country: str = Field(description="Country name")
    weight_percentage: float = Field(
        alias="weightPercentage", description="Country weight percentage"
    )

    @field_validator("weight_percentage", mode="before")
    def parse_weight_percentage(cls, value: str) -> float:
        """Parse percentage string into float"""
        if isinstance(value, str) and value.endswith("%"):
            return float(value.strip("%")) / 100
        return float(value)


class ETFExposure(BaseModel):
    """ETF stock exposure"""

    model_config = default_model_config

    etf_symbol: str = Field(alias="etfSymbol", description="ETF symbol")
    asset_exposure: str = Field(
        alias="assetExposure", description="Asset symbol the ETF is exposed to"
    )
    shares_number: int = Field(
        alias="sharesNumber", description="Number of shares held"
    )
    weight_percentage: float = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: float = Field(
        alias="marketValue", description="Market value of the exposure"
    )


class ETFHolder(BaseModel):
    """ETF holder information"""

    model_config = default_model_config

    asset: str = Field(description="Asset symbol")
    name: str = Field(description="Full name of the asset")
    isin: str = Field(
        description="International Securities Identification Number (ISIN)"
    )
    cusip: str = Field(description="CUSIP identifier for the asset")
    shares_number: float = Field(
        alias="sharesNumber", description="Number of shares held"
    )
    weight_percentage: float = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: float = Field(
        alias="marketValue", description="Market value of the asset"
    )
    updated: datetime = Field(description="Timestamp of the last update")


class MutualFundHolding(BaseModel):
    """Mutual fund holding information"""

    model_config = default_model_config

    symbol: str = Field(description="Fund symbol")
    cik: str = Field(description="Fund CIK")
    name: str = Field(description="Fund name")
    asset: str = Field(description="Asset name")
    cusip: str | None = Field(description="Asset CUSIP")
    isin: str | None = Field(description="Asset ISIN")
    shares: int = Field(description="Number of shares")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: Decimal = Field(alias="marketValue", description="Market value")
    reported_date: date = Field(alias="reportedDate", description="Report date")


class MutualFundHolder(BaseModel):
    """Mutual fund holder information"""

    model_config = default_model_config

    holder: str = Field(description="Fund name")
    shares: float = Field(description="Number of shares")
    date_reported: date = Field(alias="dateReported", description="Report date")
    change: int = Field(description="Change in the number of shares")
    weight_percent: float = Field(
        alias="weightPercent", description="Portfolio weight percentage"
    )


class ETFPortfolioDate(BaseModel):
    """ETF portfolio date model"""

    model_config = default_model_config

    portfolio_date: date = Field(description="Portfolio date", alias="date")


class PortfolioDate(BaseModel):
    """Portfolio date model for ETFs and Mutual Funds"""

    model_config = default_model_config

    portfolio_date: date = Field(description="Portfolio date", alias="date")
