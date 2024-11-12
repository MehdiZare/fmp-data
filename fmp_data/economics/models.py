# fmp_data/economics/models.py
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class TreasuryRate(BaseModel):
    """Treasury rate data"""

    model_config = ConfigDict(populate_by_name=True)

    date: date = Field(description="Rate date")
    month_1: float | None = Field(alias="1month", description="1-month rate")
    month_2: float | None = Field(alias="2month", description="2-month rate")
    month_3: float | None = Field(alias="3month", description="3-month rate")
    month_6: float | None = Field(alias="6month", description="6-month rate")
    year_1: float | None = Field(alias="1year", description="1-year rate")
    year_2: float | None = Field(alias="2year", description="2-year rate")
    year_3: float | None = Field(alias="3year", description="3-year rate")
    year_5: float | None = Field(alias="5year", description="5-year rate")
    year_7: float | None = Field(alias="7year", description="7-year rate")
    year_10: float | None = Field(alias="10year", description="10-year rate")
    year_20: float | None = Field(alias="20year", description="20-year rate")
    year_30: float | None = Field(alias="30year", description="30-year rate")


class EconomicIndicator(BaseModel):
    """Economic indicator data"""

    model_config = ConfigDict(populate_by_name=True)

    date: date = Field(description="Data date")
    indicator: str = Field(description="Indicator name")
    value: float = Field(description="Indicator value")
    unit: str = Field(description="Value unit")
    frequency: str = Field(description="Data frequency")
    country: str = Field(description="Country")
    category: str | None = Field(description="Indicator category")
    description: str | None = Field(description="Indicator description")
    source: str | None = Field(description="Data source")


class EconomicEvent(BaseModel):
    """Economic calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    event: str = Field(description="Event name")
    date: datetime = Field(description="Event date")
    country: str = Field(description="Country")
    actual: float | None = Field(description="Actual value")
    previous: float | None = Field(description="Previous value")
    estimate: float | None = Field(description="Estimated value")
    change: float | None = Field(description="Change from previous")
    change_percent: float | None = Field(
        alias="changePercentage", description="Percent change from previous"
    )
    impact: str | None = Field(description="Event impact level")


class MarketRiskPremium(BaseModel):
    """Market risk premium data"""

    model_config = ConfigDict(populate_by_name=True)

    date: date = Field(description="Data date")
    country: str = Field(description="Country")
    risk_premium: float = Field(alias="riskPremium", description="Risk premium")
    market_return: float = Field(alias="marketReturn", description="Market return")
    risk_free_rate: float = Field(alias="riskFreeRate", description="Risk-free rate")
    equity_risk_premium: float = Field(
        alias="equityRiskPremium", description="Equity risk premium"
    )
    country_risk_premium: float | None = Field(
        alias="countryRiskPremium", description="Country risk premium"
    )
