# fmp_data/intelligence/schema.py


from fmp_data.schema import BaseEnum, DateRangeArg, PaginationArg, SymbolArg


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


# News endpoints
class NewsArgs(PaginationArg):
    """Base arguments for news endpoints"""

    pass


class StockNewsArgs(NewsArgs, SymbolArg, DateRangeArg):
    """Arguments for stock-specific news"""

    pass
