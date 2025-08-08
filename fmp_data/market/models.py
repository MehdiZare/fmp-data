# fmp_data/market/models.py
from datetime import datetime
from typing import Any
import warnings

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
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
            except Exception as e:
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

    sector: str = Field(description="Sector name")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Change percentage as a float"
    )

    @field_validator("change_percentage", mode="before")
    def parse_percentage(cls, value: Any) -> float:
        """
        Convert percentage string to a float.

        Args:
            value: Value to parse, expected to be a string ending with '%'

        Returns:
            float: Parsed percentage value as decimal

        Raises:
            ValueError: If value cannot be parsed as a percentage
        """
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.strip("%")) / 100
            except ValueError as e:
                raise ValueError(f"Invalid percentage format: {value}") from e
        raise ValueError(f"Expected a percentage string, got: {value}")


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
    name: str = Field(description="Company name")
    symbol: str = Field(description="Stock symbol")


class CUSIPResult(BaseModel):
    """CUSIP search result"""

    model_config = default_model_config

    cusip: str = Field(description="CUSIP number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")


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
    currency: str = Field(description="Trading currency")
    stock_exchange: str = Field(alias="stockExchange", description="Stock exchange")
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )


class CompanySearchResult(BaseModel):
    """Company search result"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    name: str = Field(description="Company name")
    currency: str | None = Field(None, description="Trading currency")
    stock_exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(None, description="Exchange short name")


class IPODisclosure(BaseModel):
    """IPO disclosure information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    company_name: str = Field(alias="companyName", description="Company name")
    ipo_date: datetime = Field(alias="ipoDate", description="IPO date")
    exchange: str = Field(description="Stock exchange")
    price_range: str | None = Field(
        None, alias="priceRange", description="IPO price range"
    )
    shares_offered: int | None = Field(
        None, alias="sharesOffered", description="Number of shares offered"
    )
    disclosure_url: str | None = Field(
        None, alias="disclosureUrl", description="Disclosure document URL"
    )
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="Filing date"
    )
    status: str | None = Field(None, description="IPO status")
    underwriters: str | None = Field(None, description="Lead underwriters")


class IPOProspectus(BaseModel):
    """IPO prospectus information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    company_name: str = Field(alias="companyName", description="Company name")
    ipo_date: datetime = Field(alias="ipoDate", description="IPO date")
    exchange: str = Field(description="Stock exchange")
    prospectus_url: str = Field(
        alias="prospectusUrl", description="Prospectus document URL"
    )
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="Filing date"
    )
    status: str | None = Field(None, description="IPO status")
    shares_offered: int | None = Field(
        None, alias="sharesOffered", description="Number of shares offered"
    )
    offer_price: float | None = Field(
        None, alias="offerPrice", description="IPO offer price"
    )
    gross_proceeds: float | None = Field(
        None, alias="grossProceeds", description="Gross proceeds from IPO"
    )


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
