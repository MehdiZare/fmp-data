# fmp_data/technical/schema.py

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from fmp_data.schema import DateRangeArg, SymbolArg

# Available intervals for technical analysis
TimeInterval = Literal["1min", "5min", "15min", "30min", "1hour", "4hour", "daily"]


class TechnicalIndicatorArgs(SymbolArg, DateRangeArg):
    """Base arguments for technical indicators"""

    period: int = Field(
        default=14,
        description="Period for indicator calculation",
        examples=[14, 20, 50, 200],
        gt=0,
        le=500,
    )
    interval: TimeInterval = Field(
        default="daily",
        description="Time interval for data points",
    )


# Price Indicators
class SMAArgs(TechnicalIndicatorArgs):
    """Arguments for Simple Moving Average"""

    pass


class EMAArgs(TechnicalIndicatorArgs):
    """Arguments for Exponential Moving Average"""

    pass


class WMAArgs(TechnicalIndicatorArgs):
    """Arguments for Weighted Moving Average"""

    pass


# Momentum Indicators
class RSIArgs(TechnicalIndicatorArgs):
    """Arguments for Relative Strength Index"""

    pass


class MACDArgs(TechnicalIndicatorArgs):
    """Arguments for MACD"""

    fast_period: int | None = Field(default=12, ge=1, le=100, description="Fast period")
    slow_period: int | None = Field(default=26, ge=1, le=100, description="Slow period")
    signal_period: int | None = Field(
        default=9, ge=1, le=100, description="Signal period"
    )


# Volatility Indicators
class BollingerBandsArgs(TechnicalIndicatorArgs):
    """Arguments for Bollinger Bands"""

    standard_deviations: float | None = Field(
        default=2.0, ge=0.1, le=10.0, description="Number of standard deviations"
    )


class ATRArgs(TechnicalIndicatorArgs):
    """Arguments for Average True Range"""

    pass


# Volume Indicators
class OBVArgs(TechnicalIndicatorArgs):
    """Arguments for On Balance Volume"""

    pass


# Support/Resistance
class PivotPointsArgs(SymbolArg):
    """Arguments for Pivot Points"""

    method: str | None = Field(
        default="standard",
        description="Calculation method",
        json_schema_extra={
            "enum": ["standard", "fibonacci", "woodie", "camarilla", "demark"],
            "examples": ["standard"],
        },
    )


# Types of technical indicators
class IndicatorType(str, Enum):
    """Types of technical indicators available"""

    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    DEMA = "dema"
    TEMA = "tema"
    WILLIAMS = "williams"
    RSI = "rsi"
    ADX = "adx"
    STANDARD_DEVIATION = "standardDeviation"


# Specific argument schemas for different indicators
class MovingAverageArgs(TechnicalIndicatorArgs):
    """Arguments for moving average calculations"""

    period: int = Field(
        default=20,
        description="Period for moving average calculation",
        examples=[20, 50, 100, 200],
        gt=0,
    )


class MomentumIndicatorArgs(TechnicalIndicatorArgs):
    """Arguments for momentum indicators (RSI, Williams %R)"""

    period: int = Field(
        default=14,
        description="Period for momentum calculation",
        examples=[9, 14, 20],
        gt=0,
    )


class VolatilityIndicatorArgs(TechnicalIndicatorArgs):
    """Arguments for volatility indicators"""

    period: int = Field(
        default=20,
        description="Period for volatility calculation",
        examples=[10, 20, 30],
        gt=0,
    )


# Response schemas for different indicator types
class BaseIndicatorResponse(BaseModel):
    """Base response fields for all indicators"""

    date: date = Field(..., description="Date of the indicator value")
    value: float = Field(..., description="Calculated indicator value")
    symbol: str = Field(..., description="Stock symbol")


class MovingAverageResponse(BaseIndicatorResponse):
    """Response for moving average indicators"""

    ma_type: str = Field(
        ...,
        description="Type of moving average",
        examples=["SMA", "EMA", "WMA", "DEMA", "TEMA"],
    )
    period: int = Field(..., description="Calculation period")


class MomentumResponse(BaseIndicatorResponse):
    """Response for momentum indicators"""

    indicator_type: str = Field(
        ...,
        description="Type of momentum indicator",
        examples=["RSI", "Williams %R"],
    )
    overbought_level: float | None = Field(
        None,
        description="Overbought threshold level",
    )
    oversold_level: float | None = Field(
        None,
        description="Oversold threshold level",
    )


class VolatilityResponse(BaseIndicatorResponse):
    """Response for volatility indicators"""

    indicator_type: str = Field(
        ...,
        description="Type of volatility indicator",
        examples=["Standard Deviation", "ATR"],
    )
    period_high: float | None = Field(
        None,
        description="Highest value in the period",
    )
    period_low: float | None = Field(
        None,
        description="Lowest value in the period",
    )


# Mapping of indicator types to their argument schemas
INDICATOR_ARG_SCHEMAS = {
    IndicatorType.SMA: MovingAverageArgs,
    IndicatorType.EMA: MovingAverageArgs,
    IndicatorType.WMA: MovingAverageArgs,
    IndicatorType.DEMA: MovingAverageArgs,
    IndicatorType.TEMA: MovingAverageArgs,
    IndicatorType.WILLIAMS: MomentumIndicatorArgs,
    IndicatorType.RSI: MomentumIndicatorArgs,
    IndicatorType.ADX: MomentumIndicatorArgs,
    IndicatorType.STANDARD_DEVIATION: VolatilityIndicatorArgs,
}

# Mapping of indicator types to their response schemas
INDICATOR_RESPONSE_SCHEMAS = {
    IndicatorType.SMA: MovingAverageResponse,
    IndicatorType.EMA: MovingAverageResponse,
    IndicatorType.WMA: MovingAverageResponse,
    IndicatorType.DEMA: MovingAverageResponse,
    IndicatorType.TEMA: MovingAverageResponse,
    IndicatorType.WILLIAMS: MomentumResponse,
    IndicatorType.RSI: MomentumResponse,
    IndicatorType.ADX: MomentumResponse,
    IndicatorType.STANDARD_DEVIATION: VolatilityResponse,
}

# Default parameter values for different indicators
DEFAULT_PERIODS = {
    IndicatorType.SMA: 20,
    IndicatorType.EMA: 20,
    IndicatorType.WMA: 20,
    IndicatorType.DEMA: 20,
    IndicatorType.TEMA: 20,
    IndicatorType.WILLIAMS: 14,
    IndicatorType.RSI: 14,
    IndicatorType.ADX: 14,
    IndicatorType.STANDARD_DEVIATION: 20,
}

# Threshold values for various indicators
INDICATOR_THRESHOLDS = {
    IndicatorType.RSI: {
        "overbought": 70,
        "oversold": 30,
    },
    IndicatorType.WILLIAMS: {
        "overbought": -20,
        "oversold": -80,
    },
    IndicatorType.ADX: {
        "strong_trend": 25,
        "very_strong_trend": 50,
    },
}
