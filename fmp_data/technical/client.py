from datetime import date

from fmp_data.base import EndpointGroup
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


class TechnicalClient(EndpointGroup):
    """Client for technical analysis endpoints"""

    def get_sma(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[SMAIndicator]:
        """Get Simple Moving Average values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(SMA, **params)

    def get_ema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EMAIndicator]:
        """Get Exponential Moving Average values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(EMA, **params)

    def get_wma(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WMAIndicator]:
        """Get Weighted Moving Average values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(WMA, **params)

    def get_dema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DEMAIndicator]:
        """Get Double Exponential Moving Average values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(DEMA, **params)

    def get_tema(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TEMAIndicator]:
        """Get Triple Exponential Moving Average values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(TEMA, **params)

    def get_williams(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WilliamsIndicator]:
        """Get Williams %R values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(WILLIAMS, **params)

    def get_rsi(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[RSIIndicator]:
        """Get Relative Strength Index values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(RSI, **params)

    def get_adx(
        self,
        symbol: str,
        period_length: int = 14,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ADXIndicator]:
        """Get Average Directional Index values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(ADX, **params)

    def get_standard_deviation(
        self,
        symbol: str,
        period_length: int = 20,
        timeframe: str = "1day",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[StandardDeviationIndicator]:
        """Get Standard Deviation values"""
        params = {
            "symbol": symbol,
            "periodLength": period_length,
            "timeframe": timeframe,
        }

        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(STANDARD_DEVIATION, **params)
