# fmp_data/economics/models.py
from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
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
    country: str | None = Field(None, description="Country code")
    event_date: datetime = Field(..., alias="date")
    currency: str | None = Field(None, description="Currency code")
    previous: float | None = Field(None, description="Previous value")
    estimate: float | None = Field(None, description="Estimated value")
    actual: float | None = Field(None, description="Actual value")
    change: float | None = Field(None, description="Change value")
    impact: str | None = Field(None, description="Impact level")
    change_percent: float | None = Field(None, alias="changePercentage")


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


class CommitmentOfTradersReport(BaseModel):
    """Commitment of Traders (COT) report data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="COT report symbol")
    date: datetime | None = Field(None, description="Report date")
    name: str | None = Field(None, description="Contract name")
    sector: str | None = Field(None, description="Sector")
    market_and_exchange_names: str | None = Field(
        None, description="Market and exchange names"
    )
    cftc_contract_market_code: str | None = Field(
        None, description="CFTC contract market code"
    )
    cftc_market_code: str | None = Field(None, description="CFTC market code")
    cftc_region_code: str | None = Field(None, description="CFTC region code")
    cftc_commodity_code: str | None = Field(None, description="CFTC commodity code")
    open_interest_all: int | None = Field(None, description="Open interest (all)")
    noncomm_positions_long_all: int | None = Field(
        None, description="Non-commercial long positions (all)"
    )
    noncomm_positions_short_all: int | None = Field(
        None, description="Non-commercial short positions (all)"
    )
    comm_positions_long_all: int | None = Field(
        None, description="Commercial long positions (all)"
    )
    comm_positions_short_all: int | None = Field(
        None, description="Commercial short positions (all)"
    )
    contract_units: str | None = Field(None, description="Contract units")


class CommitmentOfTradersAnalysis(BaseModel):
    """Commitment of Traders (COT) analysis data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="COT report symbol")
    date: datetime | None = Field(None, description="Report date")
    name: str | None = Field(None, description="Contract name")
    sector: str | None = Field(None, description="Sector")
    exchange: str | None = Field(None, description="Exchange")
    current_long_market_situation: float | None = Field(
        None, description="Current long market situation"
    )
    current_short_market_situation: float | None = Field(
        None, description="Current short market situation"
    )
    market_situation: str | None = Field(None, description="Market situation")
    previous_long_market_situation: float | None = Field(
        None, description="Previous long market situation"
    )
    previous_short_market_situation: float | None = Field(
        None, description="Previous short market situation"
    )
    previous_market_situation: str | None = Field(
        None, description="Previous market situation"
    )
    net_position: float | None = Field(
        None,
        validation_alias=AliasChoices("netPostion", "netPosition"),
        description="Net position",
    )
    previous_net_position: float | None = Field(
        None, description="Previous net position"
    )
    change_in_net_position: float | None = Field(
        None, description="Change in net position"
    )
    market_sentiment: str | None = Field(None, description="Market sentiment")
    reversal_trend: bool | None = Field(None, description="Reversal trend")


class CommitmentOfTradersListItem(BaseModel):
    """Commitment of Traders (COT) report list item"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="COT report symbol")
    name: str | None = Field(None, description="Contract name")
