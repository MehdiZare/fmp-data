from datetime import date
from typing import TypeVar

from fmp_data.base import EndpointGroup
from fmp_data.technical.endpoints import INDICATOR_MODEL_MAP, TECHNICAL_INDICATOR
from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    EMAIndicator,
    RSIIndicator,
    SMAIndicator,
    StandardDeviationIndicator,
    TechnicalIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)

# Generic type variable for technical indicators
T = TypeVar("T", bound=TechnicalIndicator)


class TechnicalClient(EndpointGroup):
    """Client for technical analysis endpoints"""

    def _get_indicator(
        self,
        symbol: str,
        indicator_type: str,
        period: int,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[T]:
        """Generic method to get technical indicator values"""
        params = {
            "symbol": symbol,
            "type": indicator_type,
            "period": period,
            "interval": interval,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        # Create endpoint copy with specific indicator model
        endpoint = TECHNICAL_INDICATOR.model_copy()
        endpoint.response_model = INDICATOR_MODEL_MAP[indicator_type]

        return self.client.request(endpoint, **params)

    def get_sma(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[SMAIndicator]:
        """Get Simple Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="sma",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_ema(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EMAIndicator]:
        """Get Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="ema",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_wma(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WMAIndicator]:
        """Get Weighted Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="wma",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_dema(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DEMAIndicator]:
        """Get Double Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="dema",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_tema(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TEMAIndicator]:
        """Get Triple Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="tema",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_williams(
        self,
        symbol: str,
        period: int = 14,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WilliamsIndicator]:
        """Get Williams %R values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="williams",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_rsi(
        self,
        symbol: str,
        period: int = 14,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RSIIndicator]:
        """Get Relative Strength Index values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="rsi",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_adx(
        self,
        symbol: str,
        period: int = 14,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ADXIndicator]:
        """Get Average Directional Index values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="adx",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

    def get_standard_deviation(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[StandardDeviationIndicator]:
        """Get Standard Deviation values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="standardDeviation",
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
