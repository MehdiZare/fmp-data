from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CryptoListArgs(BaseModel):
    """Arguments for listing available cryptocurrencies"""

    pass


class CryptoQuotesArgs(BaseModel):
    """Arguments for getting cryptocurrency quotes"""

    pass


class CryptoQuoteArgs(BaseModel):
    """Arguments for getting a specific cryptocurrency quote"""

    symbol: str = Field(
        description=(
            "Trading symbol for the cryptocurrency " "(e.g., 'BTCUSD' for Bitcoin/USD)"
        )
    )


class CryptoHistoricalArgs(BaseModel):
    """Arguments for getting historical cryptocurrency prices"""

    symbol: str = Field(
        description="Trading symbol for the cryptocurrency (e.g., 'BTCUSD')"
    )
    from_date: date | None = Field(
        None,
        description="Start date for historical data (format: YYYY-MM-DD)",
    )
    to_date: date | None = Field(
        None,
        description="End date for historical data (format: YYYY-MM-DD)",
    )


class CryptoIntradayArgs(BaseModel):
    """Arguments for getting intraday cryptocurrency prices"""

    symbol: str = Field(description="Trading symbol for the cryptocurrency")
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = Field(
        description="Time interval between price points",
    )


class ForexListArgs(BaseModel):
    """Arguments for listing available forex pairs"""

    pass


class ForexQuotesArgs(BaseModel):
    """Arguments for getting forex quotes"""

    pass


class ForexQuoteArgs(BaseModel):
    """Arguments for getting a specific forex quote"""

    symbol: str = Field(
        description="Trading symbol for the forex pair (e.g., 'EURUSD')"
    )


class ForexHistoricalArgs(BaseModel):
    """Arguments for getting historical forex prices"""

    symbol: str = Field(description="Trading symbol for the forex pair")
    from_date: date | None = Field(
        None,
        description="Start date for historical data",
    )
    to_date: date | None = Field(
        None,
        description="End date for historical data",
    )


class ForexIntradayArgs(BaseModel):
    """Arguments for getting intraday forex prices"""

    symbol: str = Field(description="Trading symbol for the forex pair")
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = Field(
        description="Time interval between price points",
    )


class CommoditiesListArgs(BaseModel):
    """Arguments for listing available commodities"""

    pass


class CommoditiesQuotesArgs(BaseModel):
    """Arguments for getting commodities quotes"""

    pass


class CommodityQuoteArgs(BaseModel):
    """Arguments for getting a specific commodity quote"""

    symbol: str = Field(
        description="Trading symbol for the commodity (e.g., 'GC' for Gold)"
    )


class CommodityHistoricalArgs(BaseModel):
    """Arguments for getting historical commodity prices"""

    symbol: str = Field(description="Trading symbol for the commodity")
    from_date: date | None = Field(
        None,
        description="Start date for historical data",
    )
    to_date: date | None = Field(
        None,
        description="End date for historical data",
    )


class CommodityIntradayArgs(BaseModel):
    """Arguments for getting intraday commodity prices"""

    symbol: str = Field(description="Trading symbol for the commodity")
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour"] = Field(
        description="Time interval between price points",
    )
