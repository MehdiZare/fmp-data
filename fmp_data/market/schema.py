# fmp_data/market/schema.py

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class TimeInterval(str, Enum):
    """Available time intervals for intraday data"""

    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    ONE_HOUR = "1hour"
    FOUR_HOURS = "4hour"


class QuoteArgs(BaseModel):
    """Arguments for getting stock quotes"""

    symbol: str = Field(description="Stock symbol (ticker)")


class HistoricalPriceArgs(BaseModel):
    """Arguments for getting historical price data"""

    symbol: str = Field(description="Stock symbol (ticker)")
    from_date: date | None = Field(None, description="Start date for historical data")
    to_date: date | None = Field(None, description="End date for historical data")


class IntradayPriceArgs(BaseModel):
    """Arguments for getting intraday price data"""

    symbol: str = Field(description="Stock symbol (ticker)")
    interval: TimeInterval = Field(
        default=TimeInterval.ONE_MINUTE, description="Time interval for intraday data"
    )


class MarketCapArgs(BaseModel):
    """Arguments for getting market capitalization data"""

    symbol: str = Field(description="Stock symbol (ticker)")
