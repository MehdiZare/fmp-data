# fmp_data/alternative/schema.py
from datetime import date

from pydantic import Field

from fmp_data.schema import DeprecatedArgModel, Interval


class BaseListArgs(DeprecatedArgModel):
    """Base class for list endpoints that take no arguments.

    .. deprecated:: 2.6
        Removed in 3.0 -- see :data:`fmp_data.schema.ARG_MODEL_DEPRECATION`.
    """

    pass


class BaseQuoteArgs(DeprecatedArgModel):
    """Base class for quote endpoints.

    .. deprecated:: 2.6
        Removed in 3.0 -- see :data:`fmp_data.schema.ARG_MODEL_DEPRECATION`.
    """

    symbol: str = Field(description="Trading symbol for the instrument")


class BaseHistoricalArgs(BaseQuoteArgs):
    """Base class for historical data endpoints"""

    start_date: date | None = Field(  # Changed from from_date
        None,
        description="Start date for historical data (format: YYYY-MM-DD)",
    )
    end_date: date | None = Field(  # Changed from to_date
        None,
        description="End date for historical data (format: YYYY-MM-DD)",
    )


class BaseIntradayArgs(BaseQuoteArgs):
    """Base class for intraday data endpoints"""

    interval: Interval = Field(
        description="Time interval between price points",
    )


# Crypto Arguments
class CryptoListArgs(BaseListArgs):
    """Arguments for listing available cryptocurrencies"""

    pass


class CryptoQuotesArgs(BaseListArgs):
    """Arguments for getting cryptocurrency quotes"""

    pass


class CryptoQuoteArgs(BaseQuoteArgs):
    """Arguments for getting a specific cryptocurrency quote"""

    symbol: str = Field(
        description=(
            "Trading symbol for the cryptocurrency (e.g., 'BTCUSD' for Bitcoin/USD)"
        ),
        pattern=r"^[A-Z]{3,4}USD$",
    )


class CryptoHistoricalArgs(BaseHistoricalArgs):
    """Arguments for getting historical cryptocurrency prices"""

    symbol: str = Field(
        description="Trading symbol for the cryptocurrency (e.g., 'BTCUSD')",
        pattern=r"^[A-Z]{3,4}USD$",
    )


class CryptoIntradayArgs(BaseIntradayArgs):
    """Arguments for getting intraday cryptocurrency prices"""

    symbol: str = Field(
        description="Trading symbol for the cryptocurrency", pattern=r"^[A-Z]{3,4}USD$"
    )


# Forex Arguments
class ForexListArgs(BaseListArgs):
    """Arguments for listing available forex pairs"""

    pass


class ForexQuotesArgs(BaseListArgs):
    """Arguments for getting forex quotes"""

    pass


class ForexQuoteArgs(BaseQuoteArgs):
    """Arguments for getting a specific forex quote"""

    symbol: str = Field(
        description="Trading symbol for the forex pair (e.g., 'EURUSD')",
        pattern=r"^[A-Z]{6}$",
    )


class ForexHistoricalArgs(BaseHistoricalArgs):
    """Arguments for getting historical forex prices"""

    symbol: str = Field(
        description="Trading symbol for the forex pair", pattern=r"^[A-Z]{6}$"
    )


class ForexIntradayArgs(BaseIntradayArgs):
    """Arguments for getting intraday forex prices"""

    symbol: str = Field(
        description="Trading symbol for the forex pair", pattern=r"^[A-Z]{6}$"
    )


# Commodity Arguments
class CommoditiesListArgs(BaseListArgs):
    """Arguments for listing available commodities"""

    pass


class CommoditiesQuotesArgs(BaseListArgs):
    """Arguments for getting commodities quotes"""

    pass


class CommodityQuoteArgs(BaseQuoteArgs):
    """Arguments for getting a specific commodity quote"""

    symbol: str = Field(
        description="Trading symbol for the commodity (e.g., 'GC' for Gold)",
        pattern=r"^[A-Z]{2,3}$",
    )


class CommodityHistoricalArgs(BaseHistoricalArgs):
    """Arguments for getting historical commodity prices"""

    symbol: str = Field(
        description="Trading symbol for the commodity", pattern=r"^[A-Z]{2,3}$"
    )


class CommodityIntradayArgs(BaseIntradayArgs):
    """Arguments for getting intraday commodity prices"""

    symbol: str = Field(
        description="Trading symbol for the commodity", pattern=r"^[A-Z]{2,3}$"
    )
