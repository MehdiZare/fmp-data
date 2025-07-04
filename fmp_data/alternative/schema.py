# fmp_data/alternative/schema.py
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Constants
VALID_INTERVALS = Literal["1min", "5min", "15min", "30min", "1hour", "4hour"]


class BaseListArgs(BaseModel):
    """Base class for list endpoints that take no arguments"""

    pass


class BaseQuoteArgs(BaseModel):
    """Base class for quote endpoints"""

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

    interval: VALID_INTERVALS = Field(
        description="Time interval between price points",
    )

    @field_validator("interval")
    def validate_interval(cls, v: str) -> str:
        valid_intervals = ["1min", "5min", "15min", "30min", "1hour", "4hour"]
        if v not in valid_intervals:
            raise ValueError(f"Interval must be one of: {valid_intervals}")
        return v


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
