# fmp_data/market/schema.py

from enum import Enum

from pydantic import BaseModel, Field

from fmp_data.schema import (
    BaseArgModel,
    DateRangeArg,
    NoParamArg,
    SymbolArg,
    TimeSeriesBaseArg,
)


# Market Data Arguments
class MarketQuoteArgs(SymbolArg):
    """Arguments for getting market quotes"""

    pass


class MarketHoursArgs(SymbolArg):
    """Arguments for getting market hours"""

    pass


class HistoricalPriceArgs(TimeSeriesBaseArg):
    """Arguments for getting historical price data"""

    pass


class IntradayPriceArgs(TimeSeriesBaseArg):
    """Arguments for getting intraday price data"""

    pass


class SectorPriceArgs(DateRangeArg):
    """Arguments for getting sector performance"""

    pass


# Index Arguments
class IndexQuoteArgs(SymbolArg):
    """Arguments for getting index quotes"""

    pass


class IndexCompositionArgs(SymbolArg):
    """Arguments for getting index composition"""

    pass


class IndexHistoricalArgs(TimeSeriesBaseArg):
    """Arguments for getting historical index data"""

    pass


# Market Analysis
class MarketBreadthArgs(NoParamArg):
    """Arguments for getting market breadth data"""

    pass


class SectorPerformanceArgs(NoParamArg):
    """Arguments for getting sector performance"""

    pass


class MarketMoversArgs(BaseArgModel):
    """Arguments for getting market movers"""

    direction: str | None = Field(
        None,
        description="Direction of movement",
        json_schema_extra={
            "enum": ["gainers", "losers", "active"],
            "examples": ["gainers"],
        },
    )
    limit: int | None = Field(default=10, ge=1, le=100, description="Number of results")


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


class MarketCapArgs(BaseModel):
    """Arguments for getting market capitalization data"""

    symbol: str = Field(description="Stock symbol (ticker)")
