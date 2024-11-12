# fmp_data/investment/models.py
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ETFHolding(BaseModel):
    """ETF holding information"""

    model_config = ConfigDict(populate_by_name=True)

    asset: str = Field(description="Asset name")
    cusip: str | None = Field(description="Asset CUSIP")
    isin: str | None = Field(description="Asset ISIN")
    market_value: Decimal = Field(alias="marketValue", description="Market value")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    shares: int = Field(description="Number of shares")
    updated_at: datetime = Field(alias="updatedAt", description="Last update time")


class ETFInfo(BaseModel):
    """ETF information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="ETF symbol")
    name: str = Field(description="ETF name")
    expense_ratio: Decimal = Field(alias="expenseRatio", description="Expense ratio")
    assets_under_management: Decimal = Field(
        alias="aum", description="Assets under management"
    )
    avg_volume: int = Field(alias="avgVolume", description="Average volume")
    description: str = Field(description="ETF description")
    inception_date: date = Field(alias="inceptionDate", description="Inception date")
    issuer: str = Field(description="ETF issuer")
    investment_category: str = Field(
        alias="investmentCategory", description="Investment category"
    )
    primary_benchmark: str | None = Field(
        alias="primaryBenchmark", description="Primary benchmark"
    )


class ETFSectorWeighting(BaseModel):
    """ETF sector weighting"""

    model_config = ConfigDict(populate_by_name=True)

    sector: str = Field(description="Sector name")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Sector weight percentage"
    )


class ETFCountryWeighting(BaseModel):
    """ETF country weighting"""

    model_config = ConfigDict(populate_by_name=True)

    country: str = Field(description="Country name")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Country weight percentage"
    )


class ETFExposure(BaseModel):
    """ETF stock exposure"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="ETF symbol")
    asset_symbol: str = Field(alias="assetSymbol", description="Stock symbol")
    asset_name: str = Field(alias="assetName", description="Company name")
    shares: int = Field(description="Number of shares")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    market_value: Decimal = Field(alias="marketValue", description="Market value")
    updated_at: datetime = Field(alias="updatedAt", description="Last update time")


class ETFHolder(BaseModel):
    """ETF holder information"""

    model_config = ConfigDict(populate_by_name=True)

    holder: str = Field(description="Holder name")
    shares: int = Field(description="Number of shares")
    date_reported: date = Field(alias="dateReported", description="Report date")
    market_value: Decimal = Field(alias="marketValue", description="Market value")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )


class MutualFundHolding(BaseModel):
    """Mutual fund holding information"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    holder: str = Field(description="Fund name")
    shares: int = Field(description="Number of shares")
    date_reported: date = Field(alias="dateReported", description="Report date")
    market_value: Decimal = Field(alias="marketValue", description="Market value")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
