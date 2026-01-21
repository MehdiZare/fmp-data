# fmp_data/market/models.py
from datetime import datetime
from typing import Any
import warnings

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class ExchangeSymbol(BaseModel):
    """Exchange symbol information matching actual API response"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current price")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )
    change: float | None = Field(None, description="Price change")
    day_low: float | None = Field(None, alias="dayLow", description="Day low price")
    day_high: float | None = Field(None, alias="dayHigh", description="Day high price")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )
    price_avg_50: float | None = Field(None, description="50-day moving average")
    price_avg_200: float | None = Field(None, description="200-day moving average")
    exchange: str | None = Field(None, description="Stock exchange")
    volume: float | None = Field(None, description="Trading volume")
    avg_volume: float | None = Field(None, description="Average volume")
    open: float | None = Field(None, description="Opening price")
    previous_close: float | None = Field(None, description="Previous closing price")
    eps: float | None = Field(None, description="Earnings per share")
    pe: float | None = Field(None, description="Price to earnings ratio")
    earnings_announcement: datetime | None = Field(None, alias="earningsAnnouncement")
    shares_outstanding: float | None = Field(None, description="Shares outstanding")
    timestamp: int | None = Field(None, description="Quote timestamp")

    @classmethod
    @model_validator(mode="before")
    def validate_data(cls, data: Any) -> dict[str, Any]:
        """
        Validate data and convert invalid values to None with warnings.

        Args:
            data: Raw data to validate

        Returns:
            Dict[str, Any]: Cleaned data with invalid values converted to None
        """
        if not isinstance(data, dict):
            # Convert non-dict data to an empty dict or raise an error
            warnings.warn(
                f"Expected dict data but got {type(data)}. Converting to empty dict.",
                stacklevel=2,
            )
            return {}

        cleaned_data: dict[str, Any] = {}
        for field_name, field_value in data.items():
            try:
                # Check if field exists and is a float type
                field_info = cls.model_fields.get(field_name)
                if field_info and field_info.annotation in (float, float | None):
                    try:
                        if field_value is not None:
                            cleaned_data[field_name] = float(field_value)
                        else:
                            cleaned_data[field_name] = None
                    except (ValueError, TypeError):
                        warnings.warn(
                            f"Invalid value for {field_name}: "
                            f"{field_value}. Setting to None",
                            stacklevel=2,
                        )
                        cleaned_data[field_name] = None
                else:
                    cleaned_data[field_name] = field_value
            except (AttributeError, TypeError, ValueError) as e:
                warnings.warn(
                    f"Error processing field {field_name}: {e!s}. Setting to None",
                    stacklevel=2,
                )
                cleaned_data[field_name] = None

        return cleaned_data


class MarketHours(BaseModel):
    """Market trading hours for a single exchange

    Relative path: fmp_data/market/models.py
    """

    model_config = default_model_config

    exchange: str = Field(description="Exchange code (e.g., NYSE, NASDAQ)")
    name: str = Field(description="Full exchange name")
    opening_hour: str = Field(
        alias="openingHour", description="Market opening time with timezone offset"
    )
    closing_hour: str = Field(
        alias="closingHour", description="Market closing time with timezone offset"
    )
    timezone: str = Field(description="Exchange timezone")
    is_market_open: bool = Field(
        alias="isMarketOpen", description="Whether the market is currently open"
    )


class MarketHoliday(BaseModel):
    """Market holiday for a single exchange"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Holiday date")
    exchange: str | None = Field(None, description="Exchange code")
    holiday: str | None = Field(
        None,
        validation_alias=AliasChoices("holiday", "name", "description"),
        description="Holiday name",
    )


class MarketMover(BaseModel):
    """Market mover (gainer/loser) data"""

    model_config = ConfigDict(
        populate_by_name=True, validate_assignment=True, extra="ignore"
    )

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    change: float = Field(description="Price change")
    price: float = Field(description="Current price")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )


class SectorPerformance(BaseModel):
    """Sector performance data"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Snapshot date")
    sector: str = Field(description="Sector name")
    exchange: str | None = Field(None, description="Exchange code")
    change_percentage: float | None = Field(
        None,
        validation_alias=AliasChoices("changesPercentage", "averageChange"),
        description="Change percentage as a float",
    )

    @field_validator("change_percentage", mode="before")
    def parse_percentage(cls, value: Any) -> float | None:
        """
        Convert percentage string or float to a float.

        Args:
            value: Value to parse, can be a string ending with '%' or a float

        Returns:
            float | None: Parsed percentage value as decimal, or None if value is None

        Raises:
            ValueError: If value cannot be parsed as a percentage
        """
        if value is None:
            return None
        # Handle float values directly (API may return decimal like 0.054)
        if isinstance(value, int | float):
            return float(value)
        # Handle percentage string like "5.5%"
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.strip("%")) / 100
            except ValueError as e:
                raise ValueError(f"Invalid percentage format: {value}") from e
        # Try to convert string to float
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError as e:
                raise ValueError(f"Invalid percentage value: {value}") from e
        raise ValueError(f"Expected a percentage string or float, got: {value}")


class IndustryPerformance(BaseModel):
    """Industry performance data"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Snapshot date")
    industry: str = Field(description="Industry name")
    exchange: str | None = Field(None, description="Exchange code")
    change_percentage: float | None = Field(
        None,
        validation_alias=AliasChoices("changesPercentage", "averageChange"),
        description="Change percentage as a float",
    )

    @field_validator("change_percentage", mode="before")
    def parse_percentage(cls, value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.strip("%")) / 100
            except ValueError as e:
                raise ValueError(f"Invalid percentage format: {value}") from e
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError as e:
                raise ValueError(f"Invalid percentage value: {value}") from e
        raise ValueError(f"Expected a percentage string or float, got: {value}")


class SectorPESnapshot(BaseModel):
    """Sector price-to-earnings snapshot data"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Snapshot date")
    sector: str = Field(description="Sector name")
    exchange: str | None = Field(None, description="Exchange code")
    pe: float | None = Field(None, description="Price to earnings ratio")


class IndustryPESnapshot(BaseModel):
    """Industry price-to-earnings snapshot data"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Snapshot date")
    industry: str = Field(description="Industry name")
    exchange: str | None = Field(None, description="Exchange code")
    pe: float | None = Field(None, description="Price to earnings ratio")


class PrePostMarketQuote(BaseModel):
    """Pre/Post market quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    timestamp: datetime = Field(description="Quote timestamp")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")
    session: str = Field(description="Trading session (pre/post)")


class CIKResult(BaseModel):
    """CIK search result"""

    model_config = default_model_config

    cik: str = Field(description="CIK number")
    symbol: str = Field(description="Stock symbol")
    company_name: str = Field(alias="companyName", description="Company name")
    exchange_full_name: str | None = Field(
        None, alias="exchangeFullName", description="Full exchange name"
    )
    exchange: str | None = Field(None, description="Exchange abbreviation")
    currency: str | None = Field(None, description="Currency")


class CUSIPResult(BaseModel):
    """CUSIP search result"""

    model_config = default_model_config

    cusip: str = Field(description="CUSIP number")
    symbol: str = Field(description="Stock symbol")
    name: str | None = Field(None, alias="companyName", description="Company name")
    market_cap: float | None = Field(None, alias="marketCap", description="Market cap")


class ISINResult(BaseModel):
    """ISIN search result"""

    model_config = default_model_config

    isin: str = Field(description="ISIN number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")


class AvailableIndex(BaseModel):
    """Market index information"""

    model_config = default_model_config

    symbol: str = Field(description="Index symbol")
    name: str = Field(description="Index name")
    currency: str | None = Field(None, description="Trading currency")
    exchange: str | None = Field(None, alias="exchange", description="Exchange code")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Stock exchange"
    )
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Exchange short name"
    )


class CompanySearchResult(BaseModel):
    """Company search result"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    name: str = Field(
        description="Company name",
        validation_alias=AliasChoices("name", "companyName"),
    )
    currency: str | None = Field(None, description="Trading currency")
    stock_exchange: str | None = Field(
        None,
        description="Stock exchange",
        validation_alias=AliasChoices("stockExchange", "exchange"),
    )
    exchange_short_name: str | None = Field(None, description="Exchange short name")


class CIKListEntry(BaseModel):
    """CIK list entry"""

    model_config = default_model_config

    cik: str = Field(description="CIK number")
    company_name: str | None = Field(None, description="Company name")
    symbol: str | None = Field(None, description="Stock symbol")


class IPODisclosure(BaseModel):
    """IPO disclosure information"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="Filing date"
    )
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Accepted date"
    )
    effectiveness_date: datetime | None = Field(
        None, alias="effectivenessDate", description="Effectiveness date"
    )
    cik: str | None = Field(None, description="CIK number")
    form: str | None = Field(None, description="SEC form type")
    url: str | None = Field(None, description="Disclosure document URL")


class IPOProspectus(BaseModel):
    """IPO prospectus information"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Accepted date"
    )
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="Filing date"
    )
    ipo_date: datetime | None = Field(alias="ipoDate", description="IPO date")
    cik: str | None = Field(None, description="CIK number")
    price_public_per_share: float | None = Field(
        None, alias="pricePublicPerShare", description="Public price per share"
    )
    price_public_total: float | None = Field(
        None, alias="pricePublicTotal", description="Total public price"
    )
    discounts_and_commissions_per_share: float | None = Field(
        None,
        alias="discountsAndCommissionsPerShare",
        description="Discounts/commissions per share",
    )
    discounts_and_commissions_total: float | None = Field(
        None,
        alias="discountsAndCommissionsTotal",
        description="Total discounts/commissions",
    )
    proceeds_before_expenses_per_share: float | None = Field(
        None,
        alias="proceedsBeforeExpensesPerShare",
        description="Proceeds before expenses per share",
    )
    proceeds_before_expenses_total: float | None = Field(
        None,
        alias="proceedsBeforeExpensesTotal",
        description="Total proceeds before expenses",
    )
    form: str | None = Field(None, description="SEC form type")
    url: str | None = Field(None, description="Prospectus URL")


class IndexQuote(BaseModel):
    """Index quote information"""

    model_config = default_model_config

    symbol: str = Field(description="Index symbol")
    name: str = Field(description="Index name")
    price: float = Field(description="Current index value")
    changes_percentage: float = Field(
        alias="changesPercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")
    day_low: float = Field(alias="dayLow", description="Day low")
    day_high: float = Field(alias="dayHigh", description="Day high")
    year_high: float = Field(alias="yearHigh", description="52-week high")
    year_low: float = Field(alias="yearLow", description="52-week low")
    timestamp: int = Field(description="Quote timestamp")


class IndexShortQuote(BaseModel):
    """Index short quote information"""

    model_config = default_model_config

    symbol: str = Field(description="Index symbol")
    price: float = Field(description="Current index value")
    volume: int = Field(description="Trading volume")


class IndexHistoricalPrice(BaseModel):
    """Historical index price data"""

    model_config = default_model_config

    date: datetime = Field(description="Price date")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    adj_close: float = Field(alias="adjClose", description="Adjusted closing price")
    volume: int = Field(description="Trading volume")
    unadjusted_volume: int = Field(
        alias="unadjustedVolume", description="Unadjusted volume"
    )
    change: float = Field(description="Price change")
    change_percent: float = Field(
        alias="changePercent", description="Price change percentage"
    )
    vwap: float = Field(description="Volume weighted average price")
    label: str = Field(description="Date label")
    change_over_time: float = Field(
        alias="changeOverTime", description="Change over time"
    )


class IndexHistoricalLight(BaseModel):
    """Light historical index price data"""

    model_config = default_model_config

    date: datetime = Field(description="Price date")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class IndexIntraday(BaseModel):
    """Intraday index price data"""

    model_config = default_model_config

    date: datetime = Field(description="Price timestamp")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class IndexConstituent(BaseModel):
    """Index constituent information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    sector: str | None = Field(None, description="Company sector")
    sub_sector: str | None = Field(None, alias="subSector", description="Sub-sector")
    headquarter: str | None = Field(None, description="Company headquarters")
    date_first_added: datetime | None = Field(
        None, alias="dateFirstAdded", description="Date added to index"
    )
    cik: str | None = Field(None, description="CIK number")
    founded: str | None = Field(None, description="Year founded")
