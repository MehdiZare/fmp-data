# fmp_data/alternative/models.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# Base Models
class PriceQuote(BaseModel):
    """Base model for price quotes"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    price: Decimal = Field(description="Current price")
    change: Decimal = Field(description="Price change")
    change_percent: Decimal = Field(
        alias="changesPercentage", description="Percent change"
    )
    timestamp: datetime = Field(description="Quote timestamp")


class HistoricalPrice(BaseModel):
    """Base model for historical prices"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Price date")
    open: Decimal = Field(description="Opening price")
    high: Decimal = Field(description="High price")
    low: Decimal = Field(description="Low price")
    close: Decimal = Field(description="Closing price")
    volume: int | None = Field(description="Trading volume")
    adj_close: Decimal | None = Field(
        alias="adjClose", description="Adjusted closing price"
    )


class IntradayPrice(BaseModel):
    """Base model for intraday prices"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Price date and time")
    open: Decimal = Field(description="Opening price")
    high: Decimal = Field(description="High price")
    low: Decimal = Field(description="Low price")
    close: Decimal = Field(description="Closing price")
    volume: int | None = Field(description="Trading volume")


# Cryptocurrency Models
class CryptoPair(BaseModel):
    """Cryptocurrency trading pair information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    name: str = Field(description="Cryptocurrency name")
    currency: str = Field(description="Quote currency")
    exchange: str = Field(description="Exchange name")
    available_exchanges: list[str] = Field(
        alias="availableExchanges", description="Available exchanges"
    )


class CryptoQuote(PriceQuote):
    """Cryptocurrency price quote"""

    name: str = Field(description="Cryptocurrency name")
    market_cap: Decimal | None = Field(
        alias="marketCap", description="Market capitalization"
    )
    volume_24h: Decimal | None = Field(
        alias="volume24h", description="24-hour trading volume"
    )
    circulating_supply: Decimal | None = Field(
        alias="circulatingSupply", description="Circulating supply"
    )


class CryptoHistoricalPrice(HistoricalPrice):
    """Cryptocurrency historical price"""

    pass


class CryptoIntradayPrice(IntradayPrice):
    """Cryptocurrency intraday price"""

    pass


# Forex Models
class ForexPair(BaseModel):
    """Forex trading pair information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Trading symbol")
    name: str = Field(description="Pair name")
    base_currency: str = Field(alias="baseCurrency", description="Base currency")
    quote_currency: str = Field(alias="quoteCurrency", description="Quote currency")
    exchange: str = Field(description="Exchange name")


class ForexQuote(PriceQuote):
    """Forex price quote"""

    bid: Decimal = Field(description="Bid price")
    ask: Decimal = Field(description="Ask price")
    spread: Decimal = Field(description="Bid-ask spread")


class ForexHistoricalPrice(HistoricalPrice):
    """Forex historical price"""

    pass


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
    exchange: str = Field(description="Exchange name")
    category: str = Field(description="Commodity category")


class CommodityQuote(PriceQuote):
    """Commodity price quote"""

    name: str = Field(description="Commodity name")
    year_high: Decimal | None = Field(alias="yearHigh", description="52-week high")
    year_low: Decimal | None = Field(alias="yearLow", description="52-week low")
    volume: int | None = Field(description="Trading volume")


class CommodityHistoricalPrice(HistoricalPrice):
    """Commodity historical price"""

    pass


class CommodityIntradayPrice(IntradayPrice):
    """Commodity intraday price"""

    pass
