# fmp_data/alternative/models.py
import warnings
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator

UTC = ZoneInfo("UTC")


# Base Models
class PriceQuote(BaseModel):
    """Base model for price quotes"""

    model_config = ConfigDict(populate_by_name=True)

    # Required fields
    symbol: str = Field(description="Trading symbol")
    price: float | None = Field(None, description="Current price")
    change: float | None = Field(None, description="Price change")
    change_percent: float = Field(
        alias="changesPercentage", description="Percent change"
    )

    # Optional fields
    name: str | None | None = Field(None, description="Symbol name or pair name")

    # Day range
    day_low: float | None | None = Field(
        None, alias="dayLow", description="Day low price"
    )
    day_high: float | None | None = Field(
        None, alias="dayHigh", description="Day high price"
    )

    # Year range
    year_high: float | None | None = Field(
        None, alias="yearHigh", description="52-week high"
    )
    year_low: float | None | None = Field(
        None, alias="yearLow", description="52-week low"
    )

    # Moving averages
    price_avg_50: float | None | None = Field(
        None, alias="priceAvg50", description="50-day average"
    )
    price_avg_200: float | None | None = Field(
        None, alias="priceAvg200", description="200-day average"
    )

    # Volume
    volume: float | None | None = Field(None, description="Trading volume")
    avg_volume: float | None | None = Field(
        None, alias="avgVolume", description="Average volume"
    )

    # Other price points
    open: float | None | None = Field(None, description="Opening price")
    previous_close: float | None | None = Field(
        None, alias="previousClose", description="Previous close"
    )

    # Market data
    market_cap: float | None | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )
    eps: float | None | None = Field(None, description="Earnings per share")
    pe: float | None | None = Field(None, description="Price to earnings ratio")
    shares_outstanding: float | None | None = Field(
        None, alias="sharesOutstanding", description="Shares outstanding"
    )
    earnings_announcement: datetime | None | None = Field(
        None, alias="earningsAnnouncement", description="Next earnings date"
    )
    exchange: str | None | None = Field(None, description="Exchange name")

    timestamp: datetime | None | None = Field(
        None,
        description="Quote timestamp",
        json_schema_extra={"format": "unix-timestamp"},
    )

    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value):
        """Parse Unix timestamp to datetime"""
        if value is None:
            return None
        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except Exception as e:
            warnings.warn(f"Failed to parse timestamp {value}: {e}", stacklevel=2)
            return None


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

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value: int) -> datetime | None:
        """Convert Unix timestamp to datetime"""
        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except (ValueError, TypeError) as e:
            warnings.warn(f"Failed to parse timestamp {value}: {e}", stacklevel=2)
            return None


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
