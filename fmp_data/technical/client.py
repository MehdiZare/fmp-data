# fmp_data/technical/client.py
from datetime import date
from typing import Any, TypeVar

from pydantic import BaseModel

from fmp_data.base import EndpointGroup
from fmp_data.models import Endpoint
from fmp_data.technical.endpoints import (
    ADX,
    DEMA,
    EMA,
    RSI,
    SMA,
    STANDARD_DEVIATION,
    TEMA,
    WILLIAMS,
    WMA,
)
from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    EMAIndicator,
    RSIIndicator,
    SMAIndicator,
    StandardDeviationIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)

T = TypeVar("T", bound=BaseModel)


class TechnicalClient(EndpointGroup):
    """Client for technical analysis endpoints"""

    @staticmethod
    def _normalize_timeframe(timeframe: str, interval: str | None) -> str:
        if interval is None:
            return timeframe
        normalized = interval.lower()
        mapping = {
            "daily": "1day",
            "hourly": "1hour",
        }
        return mapping.get(normalized, normalized)

    def _get_indicator(
        self,
        endpoint: Endpoint[T],
        symbol: str,
        period_length: int,
        timeframe: str,
        interval: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Any]:
        """Generic helper to fetch technical indicator data

        Args:
            endpoint: The endpoint to call
            symbol: Stock symbol
            period_length: Period length for the indicator
            timeframe: Timeframe for the data (e.g., '1day', '4hour')
            start_date: Start date for the data range
            end_date: End date for the data range

        Returns:
            List of indicator values
        """
        timeframe = self._normalize_timeframe(timeframe, interval)
        params: dict[str, str | int] = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")
        return self.client.request(endpoint, **params)

    def get_sma(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[SMAIndicator]:
        """Get Simple Moving Average values"""
        return self._get_indicator(
            SMA, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_ema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EMAIndicator]:
        """Get Exponential Moving Average values"""
        return self._get_indicator(
            EMA, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_wma(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WMAIndicator]:
        """Get Weighted Moving Average values"""
        return self._get_indicator(
            WMA, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_dema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DEMAIndicator]:
        """Get Double Exponential Moving Average values"""
        return self._get_indicator(
            DEMA, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_tema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TEMAIndicator]:
        """Get Triple Exponential Moving Average values"""
        return self._get_indicator(
            TEMA, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_williams(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WilliamsIndicator]:
        """Get Williams %R values"""
        return self._get_indicator(
            WILLIAMS, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_rsi(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RSIIndicator]:
        """Get Relative Strength Index values"""
        return self._get_indicator(
            RSI, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_adx(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ADXIndicator]:
        """Get Average Directional Index values"""
        return self._get_indicator(
            ADX, symbol, period_length, timeframe, interval, start_date, end_date
        )

    def get_standard_deviation(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        interval: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[StandardDeviationIndicator]:
        """Get Standard Deviation values"""
        return self._get_indicator(
            STANDARD_DEVIATION,
            symbol,
            period_length,
            timeframe,
            interval,
            start_date,
            end_date,
        )
