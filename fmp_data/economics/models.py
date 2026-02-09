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
    unit: str | None = Field(None, description="Unit of measurement")


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

    # Position breakdown by report type (old/other)
    comm_positions_long_old: int | None = Field(
        None, description="Commercial long positions (old)"
    )
    comm_positions_long_other: int | None = Field(
        None, description="Commercial long positions (other)"
    )
    comm_positions_short_old: int | None = Field(
        None, description="Commercial short positions (old)"
    )
    comm_positions_short_other: int | None = Field(
        None, description="Commercial short positions (other)"
    )
    noncomm_positions_long_old: int | None = Field(
        None, description="Non-commercial long positions (old)"
    )
    noncomm_positions_long_other: int | None = Field(
        None, description="Non-commercial long positions (other)"
    )
    noncomm_positions_short_old: int | None = Field(
        None, description="Non-commercial short positions (old)"
    )
    noncomm_positions_short_other: int | None = Field(
        None, description="Non-commercial short positions (other)"
    )
    noncomm_positions_spread_all: int | None = Field(
        None, description="Non-commercial spread positions (all)"
    )
    noncomm_positions_spread_old: int | None = Field(
        None, description="Non-commercial spread positions (old)"
    )
    noncomm_positions_spread_other: int | None = Field(
        None, description="Non-commercial spread positions (other)"
    )
    nonrept_positions_long_all: int | None = Field(
        None, description="Non-reportable long positions (all)"
    )
    nonrept_positions_long_old: int | None = Field(
        None, description="Non-reportable long positions (old)"
    )
    nonrept_positions_long_other: int | None = Field(
        None, description="Non-reportable long positions (other)"
    )
    nonrept_positions_short_all: int | None = Field(
        None, description="Non-reportable short positions (all)"
    )
    nonrept_positions_short_old: int | None = Field(
        None, description="Non-reportable short positions (old)"
    )
    nonrept_positions_short_other: int | None = Field(
        None, description="Non-reportable short positions (other)"
    )
    tot_rept_positions_long_all: int | None = Field(
        None, description="Total reportable long positions (all)"
    )
    tot_rept_positions_long_old: int | None = Field(
        None, description="Total reportable long positions (old)"
    )
    tot_rept_positions_long_other: int | None = Field(
        None, description="Total reportable long positions (other)"
    )
    tot_rept_positions_short_all: int | None = Field(
        None, description="Total reportable short positions (all)"
    )
    tot_rept_positions_short_old: int | None = Field(
        None, description="Total reportable short positions (old)"
    )
    tot_rept_positions_short_other: int | None = Field(
        None, description="Total reportable short positions (other)"
    )
    open_interest_old: int | None = Field(None, description="Open interest (old)")
    open_interest_other: int | None = Field(None, description="Open interest (other)")

    # Changes in positions
    change_in_open_interest_all: int | None = Field(
        None, description="Change in open interest (all)"
    )
    change_in_noncomm_long_all: int | None = Field(
        None, description="Change in non-commercial long positions (all)"
    )
    change_in_noncomm_short_all: int | None = Field(
        None, description="Change in non-commercial short positions (all)"
    )
    change_in_noncomm_spead_all: int | None = Field(
        None,
        alias="changeInNoncommSpeadAll",
        description="Change in non-commercial spread positions (all)",
    )
    change_in_comm_long_all: int | None = Field(
        None, description="Change in commercial long positions (all)"
    )
    change_in_comm_short_all: int | None = Field(
        None, description="Change in commercial short positions (all)"
    )
    change_in_tot_rept_long_all: int | None = Field(
        None, description="Change in total reportable long positions (all)"
    )
    change_in_tot_rept_short_all: int | None = Field(
        None, description="Change in total reportable short positions (all)"
    )
    change_in_nonrept_long_all: int | None = Field(
        None, description="Change in non-reportable long positions (all)"
    )
    change_in_nonrept_short_all: int | None = Field(
        None, description="Change in non-reportable short positions (all)"
    )

    # Trader counts
    traders_comm_long_all: int | None = Field(
        None, description="Number of commercial long traders (all)"
    )
    traders_comm_long_ol: int | None = Field(
        None, description="Number of commercial long traders (old)"
    )
    traders_comm_long_other: int | None = Field(
        None, description="Number of commercial long traders (other)"
    )
    traders_comm_short_all: int | None = Field(
        None, description="Number of commercial short traders (all)"
    )
    traders_comm_short_ol: int | None = Field(
        None, description="Number of commercial short traders (old)"
    )
    traders_comm_short_other: int | None = Field(
        None, description="Number of commercial short traders (other)"
    )
    traders_noncomm_long_all: int | None = Field(
        None, description="Number of non-commercial long traders (all)"
    )
    traders_noncomm_long_ol: int | None = Field(
        None, description="Number of non-commercial long traders (old)"
    )
    traders_noncomm_long_other: int | None = Field(
        None, description="Number of non-commercial long traders (other)"
    )
    traders_noncomm_short_all: int | None = Field(
        None, description="Number of non-commercial short traders (all)"
    )
    traders_noncomm_short_ol: int | None = Field(
        None, description="Number of non-commercial short traders (old)"
    )
    traders_noncomm_short_other: int | None = Field(
        None, description="Number of non-commercial short traders (other)"
    )
    traders_noncomm_spread_all: int | None = Field(
        None, description="Number of non-commercial spread traders (all)"
    )
    traders_noncomm_spead_ol: int | None = Field(
        None,
        alias="tradersNoncommSpeadOl",
        description="Number of non-commercial spread traders (old)",
    )
    traders_noncomm_spread_other: int | None = Field(
        None, description="Number of non-commercial spread traders (other)"
    )
    traders_tot_all: int | None = Field(
        None, description="Total number of traders (all)"
    )
    traders_tot_ol: int | None = Field(
        None, description="Total number of traders (old)"
    )
    traders_tot_other: int | None = Field(
        None, description="Total number of traders (other)"
    )
    traders_tot_rept_long_all: int | None = Field(
        None, description="Total reportable long traders (all)"
    )
    traders_tot_rept_long_ol: int | None = Field(
        None, description="Total reportable long traders (old)"
    )
    traders_tot_rept_long_other: int | None = Field(
        None, description="Total reportable long traders (other)"
    )
    traders_tot_rept_short_all: int | None = Field(
        None, description="Total reportable short traders (all)"
    )
    traders_tot_rept_short_ol: int | None = Field(
        None, description="Total reportable short traders (old)"
    )
    traders_tot_rept_short_other: int | None = Field(
        None, description="Total reportable short traders (other)"
    )

    # Concentration ratios
    conc_gross_le_4_tdr_long_all: float | None = Field(
        None, description="Gross long concentration ratio, top 4 traders (all)"
    )
    conc_gross_le_4_tdr_long_ol: float | None = Field(
        None, description="Gross long concentration ratio, top 4 traders (old)"
    )
    conc_gross_le_4_tdr_long_other: float | None = Field(
        None, description="Gross long concentration ratio, top 4 traders (other)"
    )
    conc_gross_le_4_tdr_short_all: float | None = Field(
        None, description="Gross short concentration ratio, top 4 traders (all)"
    )
    conc_gross_le_4_tdr_short_ol: float | None = Field(
        None, description="Gross short concentration ratio, top 4 traders (old)"
    )
    conc_gross_le_4_tdr_short_other: float | None = Field(
        None, description="Gross short concentration ratio, top 4 traders (other)"
    )
    conc_gross_le_8_tdr_long_all: float | None = Field(
        None, description="Gross long concentration ratio, top 8 traders (all)"
    )
    conc_gross_le_8_tdr_long_ol: float | None = Field(
        None, description="Gross long concentration ratio, top 8 traders (old)"
    )
    conc_gross_le_8_tdr_long_other: float | None = Field(
        None, description="Gross long concentration ratio, top 8 traders (other)"
    )
    conc_gross_le_8_tdr_short_all: float | None = Field(
        None, description="Gross short concentration ratio, top 8 traders (all)"
    )
    conc_gross_le_8_tdr_short_ol: float | None = Field(
        None, description="Gross short concentration ratio, top 8 traders (old)"
    )
    conc_gross_le_8_tdr_short_other: float | None = Field(
        None, description="Gross short concentration ratio, top 8 traders (other)"
    )
    conc_net_le_4_tdr_long_all: float | None = Field(
        None, description="Net long concentration ratio, top 4 traders (all)"
    )
    conc_net_le_4_tdr_long_ol: float | None = Field(
        None, description="Net long concentration ratio, top 4 traders (old)"
    )
    conc_net_le_4_tdr_long_other: float | None = Field(
        None, description="Net long concentration ratio, top 4 traders (other)"
    )
    conc_net_le_4_tdr_short_all: float | None = Field(
        None, description="Net short concentration ratio, top 4 traders (all)"
    )
    conc_net_le_4_tdr_short_ol: float | None = Field(
        None, description="Net short concentration ratio, top 4 traders (old)"
    )
    conc_net_le_4_tdr_short_other: float | None = Field(
        None, description="Net short concentration ratio, top 4 traders (other)"
    )
    conc_net_le_8_tdr_long_all: float | None = Field(
        None, description="Net long concentration ratio, top 8 traders (all)"
    )
    conc_net_le_8_tdr_long_ol: float | None = Field(
        None, description="Net long concentration ratio, top 8 traders (old)"
    )
    conc_net_le_8_tdr_long_other: float | None = Field(
        None, description="Net long concentration ratio, top 8 traders (other)"
    )
    conc_net_le_8_tdr_short_all: float | None = Field(
        None, description="Net short concentration ratio, top 8 traders (all)"
    )
    conc_net_le_8_tdr_short_ol: float | None = Field(
        None, description="Net short concentration ratio, top 8 traders (old)"
    )
    conc_net_le_8_tdr_short_other: float | None = Field(
        None, description="Net short concentration ratio, top 8 traders (other)"
    )

    # Percent of open interest
    pct_of_oi_comm_long_all: float | None = Field(
        None, description="Percent of OI, commercial long (all)"
    )
    pct_of_oi_comm_long_ol: float | None = Field(
        None, description="Percent of OI, commercial long (old)"
    )
    pct_of_oi_comm_long_other: float | None = Field(
        None, description="Percent of OI, commercial long (other)"
    )
    pct_of_oi_comm_short_all: float | None = Field(
        None, description="Percent of OI, commercial short (all)"
    )
    pct_of_oi_comm_short_ol: float | None = Field(
        None, description="Percent of OI, commercial short (old)"
    )
    pct_of_oi_comm_short_other: float | None = Field(
        None, description="Percent of OI, commercial short (other)"
    )
    pct_of_oi_noncomm_long_all: float | None = Field(
        None, description="Percent of OI, non-commercial long (all)"
    )
    pct_of_oi_noncomm_long_ol: float | None = Field(
        None, description="Percent of OI, non-commercial long (old)"
    )
    pct_of_oi_noncomm_long_other: float | None = Field(
        None, description="Percent of OI, non-commercial long (other)"
    )
    pct_of_oi_noncomm_short_all: float | None = Field(
        None, description="Percent of OI, non-commercial short (all)"
    )
    pct_of_oi_noncomm_short_ol: float | None = Field(
        None, description="Percent of OI, non-commercial short (old)"
    )
    pct_of_oi_noncomm_short_other: float | None = Field(
        None, description="Percent of OI, non-commercial short (other)"
    )
    pct_of_oi_noncomm_spread_all: float | None = Field(
        None, description="Percent of OI, non-commercial spread (all)"
    )
    pct_of_oi_noncomm_spread_ol: float | None = Field(
        None, description="Percent of OI, non-commercial spread (old)"
    )
    pct_of_oi_noncomm_spread_other: float | None = Field(
        None, description="Percent of OI, non-commercial spread (other)"
    )
    pct_of_oi_nonrept_long_all: float | None = Field(
        None, description="Percent of OI, non-reportable long (all)"
    )
    pct_of_oi_nonrept_long_ol: float | None = Field(
        None, description="Percent of OI, non-reportable long (old)"
    )
    pct_of_oi_nonrept_long_other: float | None = Field(
        None, description="Percent of OI, non-reportable long (other)"
    )
    pct_of_oi_nonrept_short_all: float | None = Field(
        None, description="Percent of OI, non-reportable short (all)"
    )
    pct_of_oi_nonrept_short_ol: float | None = Field(
        None, description="Percent of OI, non-reportable short (old)"
    )
    pct_of_oi_nonrept_short_other: float | None = Field(
        None, description="Percent of OI, non-reportable short (other)"
    )
    pct_of_oi_tot_rept_long_all: float | None = Field(
        None, description="Percent of OI, total reportable long (all)"
    )
    pct_of_oi_tot_rept_long_ol: float | None = Field(
        None, description="Percent of OI, total reportable long (old)"
    )
    pct_of_oi_tot_rept_long_other: float | None = Field(
        None, description="Percent of OI, total reportable long (other)"
    )
    pct_of_oi_tot_rept_short_all: float | None = Field(
        None, description="Percent of OI, total reportable short (all)"
    )
    pct_of_oi_tot_rept_short_ol: float | None = Field(
        None, description="Percent of OI, total reportable short (old)"
    )
    pct_of_oi_tot_rept_short_other: float | None = Field(
        None, description="Percent of OI, total reportable short (other)"
    )
    pct_of_open_interest_all: float | None = Field(
        None, description="Percent of total open interest (all)"
    )
    pct_of_open_interest_ol: float | None = Field(
        None, description="Percent of total open interest (old)"
    )
    pct_of_open_interest_other: float | None = Field(
        None, description="Percent of total open interest (other)"
    )


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
