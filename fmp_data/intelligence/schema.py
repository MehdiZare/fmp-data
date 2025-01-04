# fmp_data/intelligence/schema.py

from datetime import date

from pydantic import BaseModel, Field

from fmp_data.schema import (
    BaseArgModel,
    BaseEnum,
    DateRangeArg,
    PaginationArg,
    SymbolArg,
)


class SentimentSourceEnum(BaseEnum):
    """Sources for sentiment data"""

    STOCKTWITS = "stocktwits"
    TWITTER = "twitter"


class SentimentTypeEnum(BaseEnum):
    """Types of sentiment"""

    BULLISH = "bullish"
    BEARISH = "bearish"


# Analyst endpoints
class PriceTargetArgs(SymbolArg):
    """Arguments for retrieving price targets"""

    pass


class AnalystEstimatesArgs(SymbolArg):
    """Arguments for retrieving analyst estimates"""

    pass


class UpgradeDowngradeArgs(SymbolArg):
    """Arguments for retrieving rating changes"""

    pass


# Calendar endpoints
class CalendarArgs(DateRangeArg):
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
class ESGArgs(SymbolArg):
    """Arguments for ESG data retrieval"""

    pass


class ESGBenchmarkArgs(BaseArgModel):
    """Arguments for ESG benchmark data"""

    year: int = Field(
        description="Year for benchmark data",
        ge=2000,
        le=2100,
        json_schema_extra={"examples": [2023, 2024]},
    )


# News endpoints
class NewsArgs(PaginationArg):
    """Base arguments for news endpoints"""

    pass


class StockNewsArgs(NewsArgs, SymbolArg, DateRangeArg):
    """Arguments for stock-specific news"""

    pass


class CryptoNewsArgs(NewsArgs):
    """Arguments for crypto news"""

    symbol: str | None = Field(
        None,
        description="Cryptocurrency symbol",
        pattern=r"^[A-Z]{3,4}$",
        json_schema_extra={"examples": ["BTC", "ETH"]},
    )


class ForexNewsArgs(NewsArgs):
    """Arguments for forex news"""

    symbol: str | None = Field(
        None,
        description="Forex pair symbol",
        pattern=r"^[A-Z]{6}$",
        json_schema_extra={"examples": ["EURUSD", "GBPUSD"]},
    )


# Government trading endpoints
class SenateTradeArgs(SymbolArg):
    """Arguments for Senate trading data"""

    pass


class HouseDisclosureArgs(SymbolArg):
    """Arguments for House disclosure data"""

    pass


class SentimentArgs(BaseArgModel):
    """Arguments for sentiment endpoints"""

    type: SentimentTypeEnum = Field(description="Type of sentiment to retrieve")
    source: SentimentSourceEnum = Field(description="Source of sentiment data")


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


# Calendar endpoints
class CalendarArgs(DateRangeArgs):
    """Arguments for calendar endpoints"""

    pass


# News endpoints
class NewsArgs(PaginationArgs):
    """Base arguments for news endpoints"""

    pass
