# fmp_data/economics/models.py
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class TreasuryRate(BaseModel):
    """Treasury rate data"""

    model_config = default_model_config

    rate_date: date = Field(..., alias="date")
    month_1: float | None = Field(None, alias="month1")
    month_2: float | None = Field(None, alias="month2")
    month_3: float | None = Field(None, alias="month3")
    month_6: float | None = Field(None, alias="month6")
    year_1: float | None = Field(None, alias="year1")
    year_2: float | None = Field(None, alias="year2")
    year_3: float | None = Field(None, alias="year3")
    year_5: float | None = Field(None, alias="year5")
    year_7: float | None = Field(None, alias="year7")
    year_10: float | None = Field(None, alias="year10")
    year_20: float | None = Field(None, alias="year20")
    year_30: float | None = Field(None, alias="year30")


class EconomicIndicator(BaseModel):
    """Economic indicator data"""

    model_config = default_model_config

    indicator_date: date = Field(..., alias="date")
    value: float
    name: str | None = None


class EconomicEvent(BaseModel):
    """Economic calendar event data"""

    model_config = default_model_config

    event: str = Field(..., description="Event name")
    country: str = Field(default="", description="Country code")  # Can be empty string
    event_date: datetime = Field(..., alias="date")
    currency: str | None = Field(None, description="Currency code")
    previous: float | None = Field(None, description="Previous value")
    estimate: float | None = Field(None, description="Estimated value")
    actual: float | None = Field(None, description="Actual value")
    change: float | None = Field(None, description="Change value")
    impact: str | None = Field(None, description="Impact level")
    change_percent: float | None = Field(0, alias="changePercentage")


class MarketRiskPremium(BaseModel):
    """Market risk premium data"""

    model_config = default_model_config

    country: str = Field(..., description="Country name")
    continent: str | None = Field(None, description="Continent name")
    country_risk_premium: float | None = Field(
        None, alias="countryRiskPremium", description="Country risk premium"
    )
    total_equity_risk_premium: float | None = Field(
        None, alias="totalEquityRiskPremium", description="Total equity risk premium"
    )
