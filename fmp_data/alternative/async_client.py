# fmp_data/alternative/async_client.py
"""Async client for alternative markets endpoints."""

from datetime import date
from typing import TypeVar

from pydantic import BaseModel

from fmp_data.alternative.endpoints import (
    COMMODITIES_LIST,
    COMMODITY_HISTORICAL,
    COMMODITY_INTRADAY,
    COMMODITY_QUOTE,
    CRYPTO_HISTORICAL,
    CRYPTO_INTRADAY,
    CRYPTO_LIST,
    CRYPTO_QUOTE,
    FOREX_HISTORICAL,
    FOREX_INTRADAY,
    FOREX_LIST,
    FOREX_QUOTE,
)
from fmp_data.alternative.models import (
    Commodity,
    CommodityHistoricalPrice,
    CommodityIntradayPrice,
    CommodityPriceHistory,
    CommodityQuote,
    CryptoHistoricalData,
    CryptoHistoricalPrice,
    CryptoIntradayPrice,
    CryptoPair,
    CryptoQuote,
    ForexHistoricalPrice,
    ForexIntradayPrice,
    ForexPair,
    ForexPriceHistory,
    ForexQuote,
)
from fmp_data.base import AsyncEndpointGroup, EndpointGroup
from fmp_data.helpers import deprecated

ModelT = TypeVar("ModelT", bound=BaseModel)


class AsyncAlternativeMarketsClient(AsyncEndpointGroup):
    """Async client for alternative markets endpoints."""

    @staticmethod
    def _wrap_history(
        symbol: str, result: object, container: type[ModelT], row_type: type
    ) -> ModelT:
        rows = EndpointGroup._unwrap_list(result, row_type)
        return container.model_validate({"symbol": symbol, "historical": rows})

    # Cryptocurrency methods
    async def get_crypto_list(self) -> list[CryptoPair]:
        """Get list of available cryptocurrencies"""
        return self._unwrap_list(
            await self.client.request_async(CRYPTO_LIST), CryptoPair
        )

    @deprecated(
        "quotes/crypto is dead. The live path batch-crypto-quotes is already "
        "shipped as FMPDataClient.batch.get_crypto_quotes(); this method is a "
        "leftover declaration, not a second data source. The payload is "
        "narrower -- symbol, price, change and volume only."
    )
    async def get_crypto_quotes(self) -> list[CryptoQuote]:
        """Get cryptocurrency quotes

        .. deprecated::
            ``quotes/crypto`` 404s and will be removed in a future version. It
            currently returns an empty list. Use
            ``client.batch.get_crypto_quotes()``, which serves the live
            ``batch-crypto-quotes``. It is not a drop-in: that endpoint
            returns only ``symbol``/``price``/``change``/``volume``, so the day
            range, market cap and moving averages declared on
            :class:`~fmp_data.alternative.models.CryptoQuote` are unavailable.
        """
        return []

    async def get_crypto_quote(self, symbol: str) -> CryptoQuote:
        """Get cryptocurrency quote"""
        result = await self.client.request_async(CRYPTO_QUOTE, symbol=symbol)
        return self._unwrap_single(result, CryptoQuote)

    async def get_crypto_historical(
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

        result = await self.client.request_async(CRYPTO_HISTORICAL, **params)
        return self._wrap_history(
            symbol, result, CryptoHistoricalData, CryptoHistoricalPrice
        )

    async def get_crypto_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[CryptoIntradayPrice]:
        """Get cryptocurrency intraday prices"""
        return self._unwrap_list(
            await self.client.request_async(
                CRYPTO_INTRADAY, symbol=symbol, interval=interval
            ),
            CryptoIntradayPrice,
        )

    # Forex methods
    async def get_forex_list(self) -> list[ForexPair]:
        """Get list of available forex pairs"""
        return self._unwrap_list(await self.client.request_async(FOREX_LIST), ForexPair)

    @deprecated(
        "quotes/forex is dead. The live path batch-forex-quotes is already "
        "shipped as FMPDataClient.batch.get_forex_quotes(); this method is a "
        "leftover declaration, not a second data source. The payload is "
        "narrower -- symbol, price, change and volume only."
    )
    async def get_forex_quotes(self) -> list[ForexQuote]:
        """Get forex quotes

        .. deprecated::
            ``quotes/forex`` 404s and will be removed in a future version. It
            currently returns an empty list. Use
            ``client.batch.get_forex_quotes()``, which serves the live
            ``batch-forex-quotes``. It is not a drop-in: that endpoint returns
            only ``symbol``/``price``/``change``/``volume``.
        """
        return []

    async def get_forex_quote(self, symbol: str) -> ForexQuote:
        """Get forex quote"""
        result = await self.client.request_async(FOREX_QUOTE, symbol=symbol)
        return self._unwrap_single(result, ForexQuote)

    async def get_forex_historical(
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

        result = await self.client.request_async(FOREX_HISTORICAL, **params)
        return self._wrap_history(
            symbol, result, ForexPriceHistory, ForexHistoricalPrice
        )

    async def get_forex_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[ForexIntradayPrice]:
        """Get forex intraday prices"""
        return self._unwrap_list(
            await self.client.request_async(
                FOREX_INTRADAY, symbol=symbol, interval=interval
            ),
            ForexIntradayPrice,
        )

    # Commodities methods
    async def get_commodities_list(self) -> list[Commodity]:
        """Get list of available commodities"""
        return self._unwrap_list(
            await self.client.request_async(COMMODITIES_LIST), Commodity
        )

    @deprecated(
        "quotes/commodity is dead. The live path batch-commodity-quotes is "
        "already shipped as FMPDataClient.batch.get_commodity_quotes(); this "
        "method is a leftover declaration, not a second data source. The "
        "payload is narrower -- symbol, price, change and volume only."
    )
    async def get_commodities_quotes(self) -> list[CommodityQuote]:
        """Get commodities quotes

        .. deprecated::
            ``quotes/commodity`` 404s and will be removed in a future version.
            It currently returns an empty list. Use
            ``client.batch.get_commodity_quotes()``, which serves the live
            ``batch-commodity-quotes``. It is not a drop-in: that endpoint
            returns only ``symbol``/``price``/``change``/``volume``.
        """
        return []

    async def get_commodity_quote(self, symbol: str) -> CommodityQuote:
        """Get commodity quote"""
        result = await self.client.request_async(COMMODITY_QUOTE, symbol=symbol)
        return self._unwrap_single(result, CommodityQuote)

    async def get_commodity_historical(
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

        result = await self.client.request_async(COMMODITY_HISTORICAL, **params)
        return self._wrap_history(
            symbol, result, CommodityPriceHistory, CommodityHistoricalPrice
        )

    async def get_commodity_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[CommodityIntradayPrice]:
        """Get commodity intraday prices"""
        return self._unwrap_list(
            await self.client.request_async(
                COMMODITY_INTRADAY, symbol=symbol, interval=interval
            ),
            CommodityIntradayPrice,
        )
