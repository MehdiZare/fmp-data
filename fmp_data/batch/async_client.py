# fmp_data/batch/async_client.py
"""Async client for batch data endpoints."""
import csv
import io
from typing import Any, cast

from fmp_data.base import AsyncEndpointGroup
from fmp_data.batch.endpoints import (
    BATCH_AFTERMARKET_QUOTE,
    BATCH_AFTERMARKET_TRADE,
    BATCH_COMMODITY_QUOTES,
    BATCH_CRYPTO_QUOTES,
    BATCH_ETF_QUOTES,
    BATCH_EXCHANGE_QUOTE,
    BATCH_FOREX_QUOTES,
    BATCH_INDEX_QUOTES,
    BATCH_MARKET_CAP,
    BATCH_MUTUALFUND_QUOTES,
    BATCH_QUOTE,
    BATCH_QUOTE_SHORT,
    DCF_BULK,
    PROFILE_BULK,
    RATING_BULK,
    RATIOS_TTM_BULK,
    SCORES_BULK,
)
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
)
from fmp_data.company.models import CompanyProfile
from fmp_data.fundamental.models import (
    DCF,
    CompanyRating,
    FinancialRatiosTTM,
    FinancialScore,
)


class AsyncBatchClient(AsyncEndpointGroup):
    """Async client for batch data endpoints.

    Provides async methods to retrieve data for multiple symbols or entire asset
    classes in a single API call.
    """

    @staticmethod
    def _parse_csv_rows(raw: bytes) -> list[dict[str, Any]]:
        text = raw.decode("utf-8").strip()
        if not text:
            return []
        reader = csv.DictReader(io.StringIO(text))
        rows: list[dict[str, Any]] = []
        for row in reader:
            if not row or all(value in (None, "", " ") for value in row.values()):
                continue
            normalized: dict[str, str | None] = {}
            for key, value in row.items():
                if value is None:
                    normalized[key] = None
                    continue
                stripped = value.strip()
                normalized[key] = stripped if stripped else None
            rows.append(normalized)
        return rows

    @staticmethod
    def _parse_csv_models(raw: bytes, model: type[Any]) -> list[Any]:
        return [
            model.model_validate(row) for row in AsyncBatchClient._parse_csv_rows(raw)
        ]

    async def get_quotes(self, symbols: list[str]) -> list[BatchQuote]:
        """Get real-time quotes for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of quote data for each symbol
        """
        return await self.client.request_async(BATCH_QUOTE, symbols=",".join(symbols))

    async def get_quotes_short(self, symbols: list[str]) -> list[BatchQuoteShort]:
        """Get quick price snapshots for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of short quote data for each symbol
        """
        return await self.client.request_async(
            BATCH_QUOTE_SHORT, symbols=",".join(symbols)
        )

    async def get_aftermarket_trades(
        self, symbols: list[str]
    ) -> list[AftermarketTrade]:
        """Get aftermarket (post-market) trade data for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of aftermarket trade data
        """
        return await self.client.request_async(
            BATCH_AFTERMARKET_TRADE, symbols=",".join(symbols)
        )

    async def get_aftermarket_quotes(
        self, symbols: list[str]
    ) -> list[AftermarketQuote]:
        """Get aftermarket quote data for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of aftermarket quote data
        """
        return await self.client.request_async(
            BATCH_AFTERMARKET_QUOTE, symbols=",".join(symbols)
        )

    async def get_exchange_quotes(self, exchange: str) -> list[BatchQuote]:
        """Get quotes for all stocks on a specific exchange

        Args:
            exchange: Exchange code (e.g., NYSE, NASDAQ)

        Returns:
            List of quotes for all stocks on the exchange
        """
        return await self.client.request_async(BATCH_EXCHANGE_QUOTE, exchange=exchange)

    async def get_mutualfund_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all mutual funds

        Returns:
            List of quotes for all mutual funds
        """
        return await self.client.request_async(BATCH_MUTUALFUND_QUOTES)

    async def get_etf_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all ETFs

        Returns:
            List of quotes for all ETFs
        """
        return await self.client.request_async(BATCH_ETF_QUOTES)

    async def get_commodity_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all commodities

        Returns:
            List of quotes for all commodities
        """
        return await self.client.request_async(BATCH_COMMODITY_QUOTES)

    async def get_crypto_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all cryptocurrencies

        Returns:
            List of quotes for all cryptocurrencies
        """
        return await self.client.request_async(BATCH_CRYPTO_QUOTES)

    async def get_forex_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all forex pairs

        Returns:
            List of quotes for all forex pairs
        """
        return await self.client.request_async(BATCH_FOREX_QUOTES)

    async def get_index_quotes(self) -> list[BatchQuote]:
        """Get batch quotes for all market indexes

        Returns:
            List of quotes for all market indexes
        """
        return await self.client.request_async(BATCH_INDEX_QUOTES)

    async def get_market_caps(self, symbols: list[str]) -> list[BatchMarketCap]:
        """Get market capitalization for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            List of market cap data for each symbol
        """
        return await self.client.request_async(
            BATCH_MARKET_CAP, symbols=",".join(symbols)
        )

    async def get_profile_bulk(self, part: str) -> list[CompanyProfile]:
        """Get company profile data in bulk"""
        raw = cast(bytes, await self.client.request_async(PROFILE_BULK, part=part))
        return self._parse_csv_models(raw, CompanyProfile)

    async def get_dcf_bulk(self) -> list[DCF]:
        """Get discounted cash flow valuations in bulk"""
        raw = cast(bytes, await self.client.request_async(DCF_BULK))
        rows = self._parse_csv_rows(raw)
        for row in rows:
            if "Stock Price" in row and "stockPrice" not in row:
                row["stockPrice"] = row.pop("Stock Price")
        return [DCF.model_validate(row) for row in rows]

    async def get_rating_bulk(self) -> list[CompanyRating]:
        """Get stock ratings in bulk"""
        raw = cast(bytes, await self.client.request_async(RATING_BULK))
        return self._parse_csv_models(raw, CompanyRating)

    async def get_scores_bulk(self) -> list[FinancialScore]:
        """Get financial scores in bulk"""
        raw = cast(bytes, await self.client.request_async(SCORES_BULK))
        return self._parse_csv_models(raw, FinancialScore)

    async def get_ratios_ttm_bulk(self) -> list[FinancialRatiosTTM]:
        """Get trailing twelve month financial ratios in bulk"""
        raw = cast(bytes, await self.client.request_async(RATIOS_TTM_BULK))
        return self._parse_csv_models(raw, FinancialRatiosTTM)
