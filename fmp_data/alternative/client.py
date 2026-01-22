# fmp_data/alternative/client.py
from datetime import date
from typing import TypeVar

from pydantic import BaseModel

from fmp_data.alternative.endpoints import (
    COMMODITIES_LIST,
    COMMODITIES_QUOTES,
    COMMODITY_HISTORICAL,
    COMMODITY_INTRADAY,
    COMMODITY_QUOTE,
    CRYPTO_HISTORICAL,
    CRYPTO_INTRADAY,
    CRYPTO_LIST,
    CRYPTO_QUOTE,
    CRYPTO_QUOTES,
    FOREX_HISTORICAL,
    FOREX_INTRADAY,
    FOREX_LIST,
    FOREX_QUOTE,
    FOREX_QUOTES,
)
from fmp_data.alternative.models import (
    Commodity,
    CommodityIntradayPrice,
    CommodityPriceHistory,
    CommodityQuote,
    CryptoHistoricalData,
    CryptoIntradayPrice,
    CryptoPair,
    CryptoQuote,
    ForexIntradayPrice,
    ForexPair,
    ForexPriceHistory,
    ForexQuote,
)
from fmp_data.base import EndpointGroup

ModelT = TypeVar("ModelT", bound=BaseModel)


class AlternativeMarketsClient(EndpointGroup):
    """Client for alternative markets endpoints"""

    @staticmethod
    def _wrap_history(symbol: str, result: object, model: type[ModelT]) -> ModelT:
        if isinstance(result, list):
            return model.model_validate({"symbol": symbol, "historical": result})
        return model.model_validate(result)

    # Cryptocurrency methods
    def get_crypto_list(self) -> list[CryptoPair]:
        """Get list of available cryptocurrencies"""
        return self.client.request(CRYPTO_LIST)

    def get_crypto_quotes(self) -> list[CryptoQuote]:
        """Get cryptocurrency quotes"""
        return self.client.request(CRYPTO_QUOTES)

    def get_crypto_quote(self, symbol: str) -> CryptoQuote:
        """Get cryptocurrency quote"""
        result = self.client.request(CRYPTO_QUOTE, symbol=symbol)
        return self._unwrap_single(result, CryptoQuote)

    def get_crypto_historical(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> CryptoHistoricalData:
        """Get cryptocurrency historical prices"""
        params: dict[str, str] = {"symbol": symbol}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        result = self.client.request(CRYPTO_HISTORICAL, **params)
        return self._wrap_history(symbol, result, CryptoHistoricalData)

    def get_crypto_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[CryptoIntradayPrice]:
        """Get cryptocurrency intraday prices"""
        return self.client.request(CRYPTO_INTRADAY, symbol=symbol, interval=interval)

    # Forex methods
    def get_forex_list(self) -> list[ForexPair]:
        """Get list of available forex pairs"""
        return self.client.request(FOREX_LIST)

    def get_forex_quotes(self) -> list[ForexQuote]:
        """Get forex quotes"""
        return self.client.request(FOREX_QUOTES)

    def get_forex_quote(self, symbol: str) -> ForexQuote:
        """Get forex quote"""
        result = self.client.request(FOREX_QUOTE, symbol=symbol)
        return self._unwrap_single(result, ForexQuote)

    def get_forex_historical(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ForexPriceHistory:
        """Get forex historical prices"""
        params: dict[str, str] = {"symbol": symbol}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        result = self.client.request(FOREX_HISTORICAL, **params)
        return self._wrap_history(symbol, result, ForexPriceHistory)

    def get_forex_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[ForexIntradayPrice]:
        """Get forex intraday prices"""
        return self.client.request(FOREX_INTRADAY, symbol=symbol, interval=interval)

    # Commodities methods
    def get_commodities_list(self) -> list[Commodity]:
        """Get list of available commodities"""
        return self.client.request(COMMODITIES_LIST)

    def get_commodities_quotes(self) -> list[CommodityQuote]:
        """Get commodities quotes"""
        return self.client.request(COMMODITIES_QUOTES)

    def get_commodity_quote(self, symbol: str) -> CommodityQuote:
        """Get commodity quote"""
        result = self.client.request(COMMODITY_QUOTE, symbol=symbol)
        return self._unwrap_single(result, CommodityQuote)

    def get_commodity_historical(
        self,
        symbol: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> CommodityPriceHistory:
        """Get commodity historical prices"""
        params: dict[str, str] = {"symbol": symbol}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        result = self.client.request(COMMODITY_HISTORICAL, **params)
        return self._wrap_history(symbol, result, CommodityPriceHistory)

    def get_commodity_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[CommodityIntradayPrice]:
        """Get commodity intraday prices"""
        return self.client.request(COMMODITY_INTRADAY, symbol=symbol, interval=interval)
