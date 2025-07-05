# fmp_data/technical/models.py
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)

IndicatorType = Literal[
    "sma", "ema", "wma", "dema", "tema", "williams", "rsi", "adx", "standardDeviation"
]


class TechnicalIndicator(BaseModel):
    """Base class for technical indicators"""

    model_config = default_model_config

    date: datetime = Field(description="Data point date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class SMAIndicator(TechnicalIndicator):
    """Simple Moving Average indicator with extended fields"""

    sma: float = Field(description="Simple Moving Average value")


class EMAIndicator(TechnicalIndicator):
    """Exponential Moving Average (EMA) indicator"""

    ema: float = Field(description="EMA value")


class WMAIndicator(TechnicalIndicator):
    """Weighted Moving Average indicator"""

    wma: float = Field(description="Weighted Moving Average value")


class DEMAIndicator(TechnicalIndicator):
    """Double Exponential Moving Average (DEMA) indicator"""

    dema: float = Field(description="DEMA value")


class TEMAIndicator(TechnicalIndicator):
    """Triple Exponential Moving Average (TEMA) indicator"""

    tema: float = Field(description="Triple Exponential Moving Average (TEMA) value")


class WilliamsIndicator(TechnicalIndicator):
    """Williams %R indicator"""

    williams: float = Field(description="Williams %R value")


class RSIIndicator(TechnicalIndicator):
    """Relative Strength Index (RSI) indicator"""

    rsi: float = Field(description="RSI value")


class ADXIndicator(TechnicalIndicator):
    """Average Directional Index (ADX) indicator"""

    adx: float = Field(description="ADX value")


class StandardDeviationIndicator(TechnicalIndicator):
    """Standard Deviation indicator with extended fields"""

    standard_deviation: float = Field(
        alias="standardDeviation", description="Standard Deviation value"
    )
