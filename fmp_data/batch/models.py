# fmp_data/batch/models.py
from datetime import date as dt_date
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class BatchQuote(BaseModel):
    """Batch quote data for multiple symbols"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current price")
    changes_percentage: float | None = Field(
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
    price_avg_50: float | None = Field(
        None, alias="priceAvg50", description="50-day moving average"
    )
    price_avg_200: float | None = Field(
        None, alias="priceAvg200", description="200-day moving average"
    )
    exchange: str | None = Field(None, description="Stock exchange")
    volume: float | None = Field(None, description="Trading volume")
    avg_volume: float | None = Field(
        None, alias="avgVolume", description="Average volume"
    )
    open: float | None = Field(None, description="Opening price")
    previous_close: float | None = Field(
        None, alias="previousClose", description="Previous closing price"
    )
    eps: float | None = Field(None, description="Earnings per share")
    pe: float | None = Field(None, description="Price to earnings ratio")
    earnings_announcement: datetime | None = Field(
        None, alias="earningsAnnouncement", description="Next earnings announcement"
    )
    shares_outstanding: int | None = Field(
        None, alias="sharesOutstanding", description="Shares outstanding"
    )
    timestamp: int | None = Field(None, description="Quote timestamp")


class BatchQuoteShort(BaseModel):
    """Short batch quote data (quick snapshot)"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    price: float | None = Field(None, description="Current price")
    change: float | None = Field(None, description="Price change")
    volume: float | None = Field(None, description="Trading volume")


class AftermarketTrade(BaseModel):
    """Aftermarket trade data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    price: float | None = Field(None, description="Trade price")
    size: int | None = Field(None, description="Trade size")
    timestamp: int | None = Field(None, description="Trade timestamp")


class AftermarketQuote(BaseModel):
    """Aftermarket quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    ask: float | None = Field(None, description="Ask price")
    bid: float | None = Field(None, description="Bid price")
    ask_size: int | None = Field(None, alias="asize", description="Ask size")
    bid_size: int | None = Field(None, alias="bsize", description="Bid size")
    timestamp: int | None = Field(None, description="Quote timestamp")


class BatchMarketCap(BaseModel):
    """Batch market capitalization data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    date: datetime | None = Field(None, description="Date of market cap")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )


class PeersBulk(BaseModel):
    """Bulk peer list data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Company symbol")
    peers: str | None = Field(None, description="Comma-separated peer symbols")

    @property
    def peers_list(self) -> list[str] | None:
        """Return peers as a list of symbols."""
        if not self.peers:
            return None
        return [peer.strip() for peer in self.peers.split(",") if peer.strip()]


class EarningsSurpriseBulk(BaseModel):
    """Bulk earnings surprise data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Company symbol")
    date: dt_date | None = Field(None, description="Earnings date")
    eps_actual: float | None = Field(
        None, alias="epsActual", description="Reported EPS"
    )
    eps_estimated: float | None = Field(
        None, alias="epsEstimated", description="Estimated EPS"
    )
    last_updated: dt_date | None = Field(
        None, alias="lastUpdated", description="Last updated date"
    )


class EODBulk(BaseModel):
    """Bulk end-of-day price data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Symbol")
    date: dt_date | None = Field(None, description="End-of-day date")
    open: float | None = Field(None, description="Open price")
    low: float | None = Field(None, description="Low price")
    high: float | None = Field(None, description="High price")
    close: float | None = Field(None, description="Close price")
    adj_close: float | None = Field(
        None, alias="adjClose", description="Adjusted close price"
    )
    volume: float | None = Field(None, description="Trading volume")
