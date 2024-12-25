# fmp_data/intelligence/schema.py

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# Base schema classes
class SymbolArgs(BaseModel):
    """Base arguments for symbol-based endpoints"""

    symbol: str = Field(
        description="Stock symbol/ticker of the company",
        examples=["AAPL", "MSFT", "GOOGL"],
    )


class DateRangeArgs(BaseModel):
    """Base arguments for date range endpoints"""

    from_date: date | None = Field(
        None, description="Start date for data retrieval", examples=["2023-01-01"]
    )
    to_date: date | None = Field(
        None, description="End date for data retrieval", examples=["2024-01-01"]
    )


class PaginationArgs(BaseModel):
    """Base arguments for paginated endpoints"""

    page: int | None = Field(default=0, description="Page number", ge=0)
    limit: int | None = Field(
        default=50, description="Number of results per page", ge=1, le=500
    )


# Analyst endpoints
class PriceTargetArgs(SymbolArgs):
    """Arguments for retrieving price targets"""

    pass


class AnalystEstimatesArgs(SymbolArgs):
    """Arguments for retrieving analyst estimates"""

    pass


class UpgradeDowngradeArgs(SymbolArgs):
    """Arguments for retrieving rating changes"""

    pass


# Calendar endpoints
class CalendarArgs(DateRangeArgs):
    """Arguments for calendar endpoints"""

    pass


class EarningsCalendarArgs(CalendarArgs):
    """Arguments for earnings calendar"""

    pass


class DividendCalendarArgs(CalendarArgs):
    """Arguments for dividend calendar"""

    pass


class IPOCalendarArgs(CalendarArgs):
    """Arguments for IPO calendar"""

    pass


# ESG endpoints
class ESGArgs(SymbolArgs):
    """Arguments for ESG data retrieval"""

    pass


class ESGBenchmarkArgs(BaseModel):
    """Arguments for ESG benchmark data"""

    year: int = Field(description="Year for benchmark data", examples=[2023, 2024])


# News endpoints
class NewsArgs(PaginationArgs):
    """Base arguments for news endpoints"""

    pass


class StockNewsArgs(NewsArgs, SymbolArgs, DateRangeArgs):
    """Arguments for stock-specific news"""

    pass


class CryptoNewsArgs(NewsArgs):
    """Arguments for crypto news"""

    symbol: str | None = Field(
        None, description="Cryptocurrency symbol", examples=["BTC", "ETH"]
    )


class ForexNewsArgs(NewsArgs):
    """Arguments for forex news"""

    symbol: str | None = Field(
        None, description="Forex pair symbol", examples=["EURUSD", "GBPUSD"]
    )


# Government trading endpoints
class SenateTradeArgs(SymbolArgs):
    """Arguments for Senate trading data"""

    pass


class HouseDisclosureArgs(SymbolArgs):
    """Arguments for House disclosure data"""

    pass


# Sentiment endpoints
class SentimentArgs(BaseModel):
    """Arguments for sentiment endpoints"""

    type: Literal["bullish", "bearish"] = Field(
        description="Type of sentiment to retrieve"
    )
    source: Literal["stocktwits", "twitter"] = Field(
        description="Source of sentiment data"
    )
