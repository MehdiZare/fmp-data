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


class SMAIndicator(TechnicalIndicator):
    """Simple Moving Average indicator"""

    pass


class EMAIndicator(TechnicalIndicator):
    """Exponential Moving Average indicator"""

    pass


class WMAIndicator(TechnicalIndicator):
    """Weighted Moving Average indicator"""

    pass


class DEMAIndicator(TechnicalIndicator):
    """Double Exponential Moving Average indicator"""

    pass


class TEMAIndicator(TechnicalIndicator):
    """Triple Exponential Moving Average indicator"""

    pass


class WilliamsIndicator(TechnicalIndicator):
    """Williams %R indicator"""

    pass


class RSIIndicator(TechnicalIndicator):
    """Relative Strength Index indicator"""

    pass


class ADXIndicator(TechnicalIndicator):
    """Average Directional Index indicator"""

    pass


class StandardDeviationIndicator(TechnicalIndicator):
    """Standard Deviation indicator"""

    pass
