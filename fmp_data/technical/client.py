from datetime import date
from typing import TypeVar

from fmp_data.base import EndpointGroup
from fmp_data.technical import endpoints, models

# Generic type variable for technical indicators
T = TypeVar("T", bound=models.TechnicalIndicator)


class TechnicalClient(EndpointGroup):
    """Client for technical analysis endpoints"""

    def _get_indicator(
        self,
        symbol: str,
        indicator_type: models.IndicatorType,
        period: int,
        indicator_model: type[T],
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
        endpoint = endpoints.TECHNICAL_INDICATOR.model_copy()  # Updated to model_copy
        endpoint.response_model = indicator_model

        return self.client.request(endpoint, **params)

    def get_sma(
        self,
        symbol: str,
        period: int = 20,
        interval: str = "daily",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[models.SMAIndicator]:
        """Get Simple Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="sma",
            period=period,
            indicator_model=models.SMAIndicator,
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
    ) -> list[models.EMAIndicator]:
        """Get Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="ema",
            period=period,
            indicator_model=models.EMAIndicator,
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
    ) -> list[models.WMAIndicator]:
        """Get Weighted Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="wma",
            period=period,
            indicator_model=models.WMAIndicator,
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
    ) -> list[models.DEMAIndicator]:
        """Get Double Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="dema",
            period=period,
            indicator_model=models.DEMAIndicator,
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
    ) -> list[models.TEMAIndicator]:
        """Get Triple Exponential Moving Average values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="tema",
            period=period,
            indicator_model=models.TEMAIndicator,
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
    ) -> list[models.WilliamsIndicator]:
        """Get Williams %R values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="williams",
            period=period,
            indicator_model=models.WilliamsIndicator,
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
    ) -> list[models.RSIIndicator]:
        """Get Relative Strength Index values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="rsi",
            period=period,
            indicator_model=models.RSIIndicator,
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
    ) -> list[models.ADXIndicator]:
        """Get Average Directional Index values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="adx",
            period=period,
            indicator_model=models.ADXIndicator,
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
    ) -> list[models.StandardDeviationIndicator]:
        """Get Standard Deviation values"""
        return self._get_indicator(
            symbol=symbol,
            indicator_type="standardDeviation",
            period=period,
            indicator_model=models.StandardDeviationIndicator,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
