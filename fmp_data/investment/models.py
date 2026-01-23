# fmp_data/investment/models.py
from datetime import date as dt_date
from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
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
        None,
        validation_alias=AliasChoices("securityCusip", "cusip"),
        description="Asset CUSIP",
    )
    shares_number: float = Field(
        alias="sharesNumber", description="Number of shares held"
    )
    weight_percentage: float = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: float = Field(alias="marketValue", description="Market value in USD")
    updated_at: datetime | None = Field(
        None,
        validation_alias=AliasChoices("updatedAt", "lastUpdated"),
        description="Timestamp of last update",
    )
    updated: datetime | None = Field(None, description="Last refresh timestamp")


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
    asset_class: str | None = Field(None, alias="assetClass", description="Asset class")
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
    inception_date: dt_date | None = Field(
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
    reported_date: dt_date = Field(alias="reportedDate", description="Report date")


class MutualFundHolder(BaseModel):
    """Mutual fund holder information"""

    model_config = default_model_config

    holder: str = Field(description="Fund name")
    shares: float = Field(description="Number of shares")
    date_reported: dt_date = Field(alias="dateReported", description="Report date")
    change: int = Field(description="Change in the number of shares")
    weight_percent: float = Field(
        alias="weightPercent", description="Portfolio weight percentage"
    )


class FundDisclosureHolderLatest(BaseModel):
    """Latest mutual fund/ETF disclosure holder information"""

    model_config = default_model_config

    cik: str | None = Field(None, description="Fund CIK")
    holder: str = Field(description="Fund name")
    shares: float = Field(description="Number of shares")
    date_reported: dt_date = Field(alias="dateReported", description="Report date")
    change: float = Field(description="Change in the number of shares")
    weight_percent: float = Field(
        alias="weightPercent", description="Portfolio weight percentage"
    )


class FundDisclosureHolding(BaseModel):
    """Mutual fund/ETF disclosure holding data"""

    model_config = default_model_config

    cik: str | None = Field(None, description="Fund CIK")
    date: dt_date | None = Field(None, description="Disclosure date")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Accepted timestamp"
    )
    symbol: str | None = Field(None, description="Holding symbol")
    name: str | None = Field(None, description="Holding name")
    lei: str | None = Field(None, description="Legal entity identifier")
    title: str | None = Field(None, description="Holding title")
    cusip: str | None = Field(None, description="CUSIP identifier")
    isin: str | None = Field(None, description="ISIN identifier")
    balance: float | None = Field(None, description="Holding balance")
    units: str | None = Field(None, description="Holding units")
    cur_cd: str | None = Field(
        None,
        alias="cur_cd",
        validation_alias=AliasChoices("cur_cd", "curCd"),
        description="Currency code",
    )
    val_usd: float | None = Field(
        None,
        alias="valUsd",
        validation_alias=AliasChoices("valUsd", "val_usd"),
        description="Value in USD",
    )
    pct_val: float | None = Field(
        None,
        alias="pctVal",
        validation_alias=AliasChoices("pctVal", "pct_val"),
        description="Percent of portfolio value",
    )
    payoff_profile: str | None = Field(
        None, alias="payoffProfile", description="Payoff profile"
    )
    asset_cat: str | None = Field(None, alias="assetCat", description="Asset category")
    issuer_cat: str | None = Field(
        None, alias="issuerCat", description="Issuer category"
    )
    inv_country: str | None = Field(
        None, alias="invCountry", description="Investment country"
    )
    is_restricted_sec: str | None = Field(
        None, alias="isRestrictedSec", description="Restricted security flag"
    )
    fair_val_level: str | None = Field(
        None, alias="fairValLevel", description="Fair value level"
    )
    is_cash_collateral: str | None = Field(
        None, alias="isCashCollateral", description="Cash collateral flag"
    )
    is_non_cash_collateral: str | None = Field(
        None, alias="isNonCashCollateral", description="Non-cash collateral flag"
    )
    is_loan_by_fund: str | None = Field(
        None, alias="isLoanByFund", description="Loan by fund flag"
    )


class FundDisclosureSearchResult(BaseModel):
    """Mutual fund/ETF disclosure holder search result"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Fund or ETF symbol")
    cik: str | None = Field(None, description="Fund CIK")
    class_id: str | None = Field(None, alias="classId", description="Class ID")
    series_id: str | None = Field(None, alias="seriesId", description="Series ID")
    entity_name: str | None = Field(None, alias="entityName", description="Entity name")
    entity_org_type: str | None = Field(
        None, alias="entityOrgType", description="Entity organization type"
    )
    series_name: str | None = Field(None, alias="seriesName", description="Series name")
    class_name: str | None = Field(None, alias="className", description="Class name")
    reporting_file_number: str | None = Field(
        None, alias="reportingFileNumber", description="Reporting file number"
    )
    address: str | None = Field(None, description="Entity address")
    city: str | None = Field(None, description="Entity city")
    zip_code: str | None = Field(None, alias="zipCode", description="ZIP code")
    state: str | None = Field(None, description="State")


class ETFPortfolioDate(BaseModel):
    """ETF portfolio date model"""

    model_config = default_model_config

    portfolio_date: dt_date = Field(description="Portfolio date", alias="date")


class PortfolioDate(BaseModel):
    """Portfolio date model for ETFs and Mutual Funds"""

    model_config = default_model_config

    portfolio_date: dt_date = Field(description="Portfolio date", alias="date")
    year: int | None = Field(None, description="Year of the disclosure")
    quarter: int | None = Field(None, description="Quarter of the disclosure (1-4)")
