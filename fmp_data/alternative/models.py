# fmp_data/alternative/models.py

from datetime import date, datetime
from typing import Any
import warnings
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

UTC = ZoneInfo("UTC")

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


# Base Models
class PriceQuote(BaseModel):
    """Base model for price quotes"""

    model_config = ConfigDict(populate_by_name=True)

    # Core required fields
    symbol: str = Field(description="Trading symbol")
    price: float = Field(description="Current price")
    change: float = Field(description="Price change")
    change_percent: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )
    timestamp: datetime = Field(description="Quote timestamp")

    # Optional common fields
    name: str | None = Field(None, description="Name or pair name")
    volume: float | None = Field(None, description="Trading volume")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )

    # Day range (optional)
    day_low: float | None = Field(None, alias="dayLow", description="Day low price")
    day_high: float | None = Field(None, alias="dayHigh", description="Day high price")

    # Year range (optional)
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")

    # Moving averages (optional)
    price_avg_50: float | None = Field(
        None, alias="priceAvg50", description="50-day average price"
    )
    price_avg_200: float | None = Field(
        None, alias="priceAvg200", description="200-day average price"
    )

    # Volume metrics (optional)
    avg_volume: float | None = Field(
        None, alias="avgVolume", description="Average trading volume"
    )

    # Exchange and price points (optional)
    exchange: str | None = Field(None, description="Exchange identifier")
    open_price: float | None = Field(None, alias="open", description="Opening price")
    previous_close: float | None = Field(
        None, alias="previousClose", description="Previous close price"
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> datetime:
        """Parse Unix timestamp to datetime with UTC timezone"""
        if value is None:
            raise ValueError("Timestamp cannot be None")

        # Return datetime objects directly
        if isinstance(value, datetime):
            return value

        try:
            if isinstance(value, str | int | float):
                timestamp = float(value)

                # Detect milliseconds timestamp and convert to seconds
                # Timestamps greater than this threshold are likely in milliseconds
                # (corresponds to year 2001, reasonable cutoff for financial data)
                if timestamp > 978307200:  # Jan 1, 2001 in seconds
                    # If timestamp is too large, assume it's in milliseconds
                    if timestamp > 978307200000:  # Jan 1, 2001 in milliseconds
                        timestamp = timestamp / 1000

            else:
                raise ValueError(f"Unexpected type for timestamp: {type(value)}")

            return datetime.fromtimestamp(timestamp, tz=UTC)
        except (TypeError, ValueError) as e:
            warnings.warn(f"Failed to parse timestamp {value}: {e}", stacklevel=2)
            raise ValueError(f"Invalid timestamp format: {value}") from e


class HistoricalPrice(BaseModel):
    """Base model for historical price data"""

    model_config = ConfigDict(populate_by_name=True)

    price_date: date = Field(
        description="The date of the historical record", alias="date"
    )
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price of the day")
    low: float = Field(description="Lowest price of the day")
    close: float = Field(description="Closing price")
    adj_close: float | None = Field(
        None, alias="adjClose", description="Adjusted closing price"
    )
    volume: int = Field(description="Volume traded")
    unadjusted_volume: int | None = Field(
        None, alias="unadjustedVolume", description="Unadjusted trading volume"
    )
    change: float = Field(description="Price change")
    change_percent: float | None = Field(
        None, alias="changePercent", description="Percentage change in price"
    )
    vwap: float | None = Field(None, description="Volume-weighted average price")
    label: str | None = Field(None, description="Formatted label for the date")
    change_over_time: float | None = Field(
        None, alias="changeOverTime", description="Change over time as a percentage"
    )
    symbol: str | None = Field(
        None, description="Trading symbol (for API compatibility)"
    )


class IntradayPrice(BaseModel):
    """Base model for intraday prices"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Price date and time")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    volume: float | None = Field(None, description="Trading volume")


# Cryptocurrency Models
class CryptoPair(BaseModel):
    """Cryptocurrency trading pair information"""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    symbol: str = Field(description="Trading symbol")
    name: str | None = Field(None, description="Cryptocurrency name")
    currency: str | None = Field(None, description="Quote currency")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Full name of the stock exchange"
    )
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Short name of the exchange"
    )
    exchange: str | None = Field(None, description="Exchange identifier")
    ico_date: date | None = Field(None, alias="icoDate", description="ICO date")
    circulating_supply: float | None = Field(
        None, alias="circulatingSupply", description="Circulating supply"
    )
    total_supply: float | None = Field(
        None, alias="totalSupply", description="Total supply"
    )


class CryptoQuote(PriceQuote):
    """Cryptocurrency price quote"""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",  # Allow extra fields from API
    )

    # Override fields to make them required for crypto where available
    name: str | None = Field(None, description="Cryptocurrency name and pair")
    volume: float | None = Field(None, description="24h trading volume")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )
    day_low: float | None = Field(None, alias="dayLow", description="24h low price")
    day_high: float | None = Field(None, alias="dayHigh", description="24h high price")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")
    exchange: str | None = Field(None, description="Exchange identifier")
    open_price: float | None = Field(None, alias="open", description="Opening price")
    previous_close: float | None = Field(
        None, alias="previousClose", description="Previous close price"
    )

    # Keep change_percent optional since API might not always provide it
    change_percent: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )

    # Additional crypto-specific fields
    shares_outstanding: float | None = Field(
        None, alias="sharesOutstanding", description="Circulating supply"
    )


class CryptoHistoricalPrice(HistoricalPrice):
    """Cryptocurrency historical price"""

    pass


class CryptoHistoricalData(BaseModel):
    """Historical price data wrapper"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    historical: list[CryptoHistoricalPrice] = Field(
        description="Historical price records"
    )


class CryptoIntradayPrice(IntradayPrice):
    """Cryptocurrency intraday price"""

    pass


# Forex Models
class ForexPair(BaseModel):
    """Forex trading pair information"""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    symbol: str = Field(description="Trading symbol")
    name: str | None = Field(None, description="Pair name")
    currency: str | None = Field(None, description="Quote currency")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Stock exchange code"
    )
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Exchange short name"
    )
    exchange: str | None = Field(None, description="Exchange identifier")


class ForexQuote(PriceQuote):
    """Forex price quote"""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )

    # Make these fields required for forex
    volume: float | None = Field(None, description="Trading volume")
    day_low: float | None = Field(None, alias="dayLow", description="Day low rate")
    day_high: float | None = Field(None, alias="dayHigh", description="Day high rate")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")
    exchange: str | None = Field(None, description="Exchange identifier")
    open_price: float | None = Field(None, alias="open", description="Opening rate")
    previous_close: float | None = Field(
        None, alias="previousClose", description="Previous close rate"
    )


class ForexHistoricalPrice(HistoricalPrice):
    """Forex historical price"""

    pass


class ForexPriceHistory(BaseModel):
    """Full forex price history"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Symbol for the currency pair")
    historical: list[ForexHistoricalPrice] = Field(
        description="List of historical price data for the forex pair"
    )


class ForexIntradayPrice(IntradayPrice):
    """Forex intraday price"""

    pass


# Commodities Models
class Commodity(BaseModel):
    """Commodity information"""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    symbol: str = Field(description="Trading symbol")
    name: str | None = Field(None, description="Commodity name")
    currency: str | None = Field(None, description="Trading currency")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Full name of the stock exchange"
    )
    exchange_short_name: str | None = Field(
        None,
        alias="exchangeShortName",
        description="Short name of the exchange category",
    )
    exchange: str | None = Field(None, description="Exchange identifier")


class CommodityQuote(PriceQuote):
    """Commodity price quote"""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )

    # Make these fields required for commodities
    name: str | None = Field(None, description="Commodity name")
    volume: float | None = Field(None, description="Trading volume")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")


class CommodityHistoricalPrice(HistoricalPrice):
    """Commodity historical price"""

    pass


class CommodityPriceHistory(BaseModel):
    """Full commodity price history"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Symbol for the commodity")
    historical: list[CommodityHistoricalPrice] = Field(
        description="List of historical price data"
    )


class CommodityIntradayPrice(IntradayPrice):
    """Commodity intraday price"""

    pass
