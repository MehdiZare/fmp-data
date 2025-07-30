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

    # Core fields
    symbol: str = Field(description="Crypto trading pair symbol")
    name: str = Field(description="Cryptocurrency name and pair")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changePercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")

    # Volume and market data
    volume: float = Field(description="24h trading volume")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")

    # Day range
    day_low: float = Field(alias="dayLow", description="24h low price")
    day_high: float = Field(alias="dayHigh", description="24h high price")

    # Year range
    year_high: float = Field(alias="yearHigh", description="52-week high")
    year_low: float = Field(alias="yearLow", description="52-week low")

    # Moving averages
    price_avg_50: float = Field(alias="priceAvg50", description="50-day average price")
    price_avg_200: float = Field(
        alias="priceAvg200", description="200-day average price"
    )

    # Exchange and price points
    exchange: str = Field(description="Exchange identifier")
    open_price: float = Field(alias="open", description="Opening price")
    previous_close: float = Field(
        alias="previousClose", description="Previous close price"
    )

    # Timestamp
    timestamp: datetime = Field(description="Quote timestamp")

    @classmethod
    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value: Any) -> datetime:
        """Parse Unix timestamp to datetime with UTC timezone"""
        if value is None:
            raise ValueError("Timestamp cannot be None")

        try:
            if isinstance(value, str | int | float):
                timestamp = float(value)
            else:
                raise ValueError(f"Unexpected type for timestamp: {type(value)}")

            return datetime.fromtimestamp(timestamp, tz=UTC)
        except Exception as e:
            warnings.warn(f"Failed to parse timestamp {value}: {e}", stacklevel=2)
            raise ValueError(f"Invalid timestamp format: {value}") from e


class HistoricalPrice(BaseModel):
    """Base model for historical price data"""

    price_date: date = Field(
        description="The date of the historical record", alias="date"
    )
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price of the day")
    low: float = Field(description="Lowest price of the day")
    close: float = Field(description="Closing price")
    adj_close: float = Field(alias="adjClose", description="Adjusted closing price")
    volume: int = Field(description="Volume traded")
    unadjusted_volume: int = Field(
        alias="unadjustedVolume", description="Unadjusted trading volume"
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
    )  # ADD THIS


class IntradayPrice(BaseModel):
    """Base model for intraday prices"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Price date and time")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    volume: float | None = Field(None, description="Trading volume")  # Changed to float


# Cryptocurrency Models
class CryptoPair(BaseModel):
    """Cryptocurrency trading pair information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    name: str = Field(description="Cryptocurrency name")
    currency: str = Field(description="Quote currency")
    stock_exchange: str = Field(
        alias="stockExchange", description="Full name of the stock exchange"
    )
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Short name of the exchange"
    )


class CryptoQuote(PriceQuote):
    """Cryptocurrency price quote"""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",  # Allow extra fields from API
    )

    # Override the base class field to make it optional
    change_percent: float | None = Field(
        None, alias="changesPercentage", description="Percent change"
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

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    name: str = Field(description="Pair name")
    currency: str = Field(description="Quote currency")
    stock_exchange: str = Field(
        alias="stockExchange", description="Stock exchange code"
    )
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )


class ForexQuote(PriceQuote):
    """Forex price quote"""

    pass


class ForexHistoricalPrice(HistoricalPrice):
    """Forex historical price"""

    pass


class ForexPriceHistory(BaseModel):
    """Full forex price history"""

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

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    name: str = Field(description="Commodity name")
    currency: str = Field(description="Trading currency")
    stock_exchange: str = Field(
        alias="stockExchange", description="Full name of the stock exchange"
    )
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Short name of the exchange category"
    )


class CommodityQuote(PriceQuote):
    """Commodity price quote"""

    pass


class CommodityHistoricalPrice(HistoricalPrice):
    """Commodity historical price"""

    pass


class CommodityPriceHistory(BaseModel):
    """Full commodity price history"""

    symbol: str = Field(description="Symbol for the commodity")
    historical: list[CommodityHistoricalPrice] = Field(
        description="List of historical price data"
    )


class CommodityIntradayPrice(IntradayPrice):
    """Commodity intraday price"""

    pass
