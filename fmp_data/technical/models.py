# fmp_data/technical/models.py
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IndicatorType = Literal[
    "sma", "ema", "wma", "dema", "tema", "williams", "rsi", "adx", "standardDeviation"
]


class TechnicalIndicator(BaseModel):
    """Base class for technical indicators"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Data point date")
    value: float = Field(description="Indicator value")


class SMAIndicator(BaseModel):
    """Simple Moving Average indicator with extended fields"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    sma: float = Field(description="Simple Moving Average value")


class EMAIndicator(BaseModel):
    """Exponential Moving Average (EMA) indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    ema: float = Field(description="EMA value")


class WMAIndicator(BaseModel):
    """Weighted Moving Average indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    wma: float = Field(description="Weighted Moving Average value")


class DEMAIndicator(BaseModel):
    """Double Exponential Moving Average (DEMA) indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    dema: float = Field(description="DEMA value")


class TEMAIndicator(BaseModel):
    """Triple Exponential Moving Average (TEMA) indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    tema: float = Field(description="Triple Exponential Moving Average (TEMA) value")


class WilliamsIndicator(BaseModel):
    """Williams %R indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    williams: float = Field(description="Williams %R value")


class RSIIndicator(BaseModel):
    """Relative Strength Index (RSI) indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    rsi: float = Field(description="RSI value")


class ADXIndicator(BaseModel):
    """Average Directional Index (ADX) indicator"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    adx: float = Field(description="ADX value")


class StandardDeviationIndicator(BaseModel):
    """Standard Deviation indicator with extended fields"""

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")
    standard_deviation: float = Field(
        alias="standardDeviation", description="Standard Deviation value"
    )
