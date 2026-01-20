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

    symbol: str = Field(description="ETF symbol")
    asset: str = Field(description="Asset ticker symbol")
    name: str = Field(description="Asset name")
    isin: str | None = Field(None, description="Asset ISIN")
    security_cusip: str | None = Field(
        None, alias="securityCusip", description="Asset CUSIP"
    )
    shares_number: float = Field(
        alias="sharesNumber", description="Number of shares held"
    )
    weight_percentage: float = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: float = Field(alias="marketValue", description="Market value in USD")
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Timestamp of last update"
    )


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
    description: str | None = Field(None, description="ETF description")
    isin: str | None = Field(None, description="ISIN identifier for the ETF")
    asset_class: str | None = Field(
        None, alias="assetClass", description="Asset class"
    )
    security_cusip: str | None = Field(
        None, alias="securityCusip", description="CUSIP identifier for the ETF"
    )
    domicile: str | None = Field(None, description="Country of domicile")
    website: str | None = Field(None, description="ETF website")
    etf_company: str | None = Field(
        None, alias="etfCompany", description="ETF issuer company"
    )
    expense_ratio: float = Field(alias="expenseRatio", description="Expense ratio")
    assets_under_management: float | None = Field(
        None, alias="assetsUnderManagement", description="Assets under management"
    )
    avg_volume: int | None = Field(
        None, alias="avgVolume", description="Average volume"
    )
    inception_date: date | None = Field(
        None, alias="inceptionDate", description="Inception date"
    )
    nav: Decimal | None = Field(None, description="Net Asset Value (NAV)")
    nav_currency: str | None = Field(
        None, alias="navCurrency", description="Currency of NAV"
    )
    holdings_count: int | None = Field(
        None, alias="holdingsCount", description="Number of holdings"
    )
    is_actively_trading: bool | None = Field(
        None, alias="isActivelyTrading", description="Whether ETF is actively trading"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Timestamp of last update"
    )
    sectors_list: list[ETFSectorExposure] | None = Field(
        None, alias="sectorsList", description="List of sector exposures"
    )


class ETFSectorWeighting(BaseModel):
    """ETF sector weighting"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="ETF symbol")
    sector: str = Field(description="Sector name")
    weight_percentage: float = Field(
        alias="weightPercentage", description="Sector weight percentage (0-1 scale)"
    )

    @field_validator("weight_percentage", mode="before")
    def parse_weight_percentage(cls, value: str | float) -> float:
        """Parse percentage string or number into normalized float (0-1 scale)"""
        if isinstance(value, str) and value.endswith("%"):
            return float(value.strip("%")) / 100
        val = float(value)
        # Normalize values > 1 (assume they are on 0-100 scale)
        if val > 1:
            return val / 100
        return val


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

    symbol: str = Field(description="ETF symbol that holds the asset")
    asset: str = Field(description="Asset symbol the ETF is exposed to")
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
    year: int | None = Field(None, description="Year of the disclosure")
    quarter: int | None = Field(None, description="Quarter of the disclosure (1-4)")
