# fmp_data/market/schema.py


from pydantic import BaseModel, Field

from fmp_data.schema import (
    BaseArgModel,
    DateRangeArg,
    ExchangeArg,
    NoParamArg,
    PaginationArg,
    SearchArg,
    SymbolArg,
    TimeSeriesBaseArg,
)


class SearchArgs(SearchArg, PaginationArg):
    """Arguments for market search"""

    exchange: str | None = Field(
        None,
        description="Filter by stock exchange",
        pattern=r"^[A-Z]{2,6}$",
        json_schema_extra={"examples": ["NYSE", "NASDAQ"]},
    )


class BaseSearchArg(BaseModel):
    """Base model for search-type endpoints"""

    query: str = Field(description="Search query string", min_length=2)


class BaseExchangeArg(BaseModel):
    """Base model for exchange-related queries"""

    exchange: str = Field(
        description="Exchange code (e.g., NYSE, NASDAQ)",
        pattern=r"^[A-Z]{2,6}$",
        min_length=2,
        max_length=6,
        examples=["NYSE", "NASDAQ", "LSE", "TSX"],
    )


class ExchangeArgs(BaseExchangeArg):
    """Arguments for getting exchange symbols

    Extends BaseExchangeArg to potentially add more specific parameters
    in the future while maintaining backward compatibility
    """

    pass


class AvailableIndexesArgs(NoParamArg):
    """Arguments for getting available indexes"""

    pass


class ExchangeSymbolsArgs(ExchangeArg):
    """Arguments for getting exchange symbols"""

    pass


# Market Data Arguments
class MarketQuoteArgs(SymbolArg):
    """Arguments for getting market quotes"""

    pass


class CIKSearchArgs(SearchArg):
    """Arguments for CIK search"""

    pass


class CUSIPSearchArgs(SearchArg):
    """Arguments for CUSIP search"""

    pass


class ISINSearchArgs(SearchArg):
    """Arguments for ISIN search"""

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


class QuoteArgs(BaseModel):
    """Arguments for getting stock quotes"""

    symbol: str = Field(description="Stock symbol (ticker)")


class MarketCapArgs(BaseModel):
    """Arguments for getting market capitalization data"""

    symbol: str = Field(description="Stock symbol (ticker)")


# List Related
class StockListArgs(NoParamArg):
    """Arguments for getting stock list"""

    pass


class ETFListArgs(NoParamArg):
    """Arguments for getting ETF list"""

    pass
