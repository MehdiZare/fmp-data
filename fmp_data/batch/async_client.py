# fmp_data/batch/async_client.py
"""Async client for batch data endpoints."""

from datetime import date
import logging
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from fmp_data.base import AsyncEndpointGroup
from fmp_data.batch._csv_utils import parse_csv_models, parse_csv_rows
from fmp_data.batch.endpoints import (
    BALANCE_SHEET_STATEMENT_BULK,
    BALANCE_SHEET_STATEMENT_GROWTH_BULK,
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
    CASH_FLOW_STATEMENT_BULK,
    CASH_FLOW_STATEMENT_GROWTH_BULK,
    DCF_BULK,
    EARNINGS_SURPRISES_BULK,
    EOD_BULK,
    ETF_HOLDER_BULK,
    INCOME_STATEMENT_BULK,
    INCOME_STATEMENT_GROWTH_BULK,
    KEY_METRICS_TTM_BULK,
    PEERS_BULK,
    PRICE_TARGET_SUMMARY_BULK,
    PROFILE_BULK,
    RATING_BULK,
    RATIOS_TTM_BULK,
    SCORES_BULK,
    UPGRADES_DOWNGRADES_CONSENSUS_BULK,
)
from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
    EarningsSurpriseBulk,
    EODBulk,
    PeersBulk,
)
from fmp_data.company.models import (
    CompanyProfile,
    PriceTargetSummary,
    UpgradeDowngradeConsensus,
)
from fmp_data.exceptions import InvalidResponseTypeError
from fmp_data.fundamental.models import (
    DCF,
    BalanceSheet,
    CashFlowStatement,
    CompanyRating,
    FinancialGrowth,
    FinancialRatiosTTM,
    FinancialScore,
    IncomeStatement,
    KeyMetricsTTM,
)
from fmp_data.investment.models import ETFHolding
from fmp_data.models import Endpoint

logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class AsyncBatchClient(AsyncEndpointGroup):
    """Async client for batch data endpoints.

    Provides async methods to retrieve data for multiple symbols or entire asset
    classes in a single API call.
    """

    async def _request_csv(self, endpoint: Endpoint, **params: Any) -> bytes:
        result = await self.client.request_async(endpoint, **params)
        if isinstance(result, bytearray):
            return bytes(result)
        if not isinstance(result, bytes):
            raise InvalidResponseTypeError(
                endpoint_name=endpoint.name,
                expected_type="bytes",
                actual_type=type(result).__name__,
            )
        return result

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

    async def get_exchange_quotes(
        self, exchange: str, short: bool | None = None
    ) -> list[BatchQuote]:
        """Get quotes for all stocks on a specific exchange

        Args:
            exchange: Exchange code (e.g., NYSE, NASDAQ)
            short: Whether to return short quote data

        Returns:
            List of quotes for all stocks on the exchange
        """
        params: dict[str, object] = {"exchange": exchange}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_EXCHANGE_QUOTE, **params)

    async def get_mutualfund_quotes(
        self, short: bool | None = None
    ) -> list[BatchQuote]:
        """Get batch quotes for all mutual funds

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all mutual funds
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_MUTUALFUND_QUOTES, **params)

    async def get_etf_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all ETFs

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all ETFs
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_ETF_QUOTES, **params)

    async def get_commodity_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all commodities

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all commodities
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_COMMODITY_QUOTES, **params)

    async def get_crypto_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all cryptocurrencies

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all cryptocurrencies
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_CRYPTO_QUOTES, **params)

    async def get_forex_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all forex pairs

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all forex pairs
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_FOREX_QUOTES, **params)

    async def get_index_quotes(self, short: bool | None = None) -> list[BatchQuote]:
        """Get batch quotes for all market indexes

        Args:
            short: Whether to return short quote data

        Returns:
            List of quotes for all market indexes
        """
        params: dict[str, object] = {}
        if short is not None:
            params["short"] = short
        return await self.client.request_async(BATCH_INDEX_QUOTES, **params)

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
        raw = await self._request_csv(PROFILE_BULK, part=part)
        return parse_csv_models(raw, CompanyProfile)

    async def get_dcf_bulk(self) -> list[DCF]:
        """Get discounted cash flow valuations in bulk"""
        raw = await self._request_csv(DCF_BULK)
        rows = parse_csv_rows(raw)
        results: list[DCF] = []
        for row in rows:
            if "Stock Price" in row and "stockPrice" not in row:
                row["stockPrice"] = row.pop("Stock Price")
            try:
                results.append(DCF.model_validate(row))
            except PydanticValidationError as exc:
                logger.warning("Skipping invalid DCF row %s: %s", row, exc)
        return results

    async def get_rating_bulk(self) -> list[CompanyRating]:
        """Get stock ratings in bulk"""
        raw = await self._request_csv(RATING_BULK)
        return parse_csv_models(raw, CompanyRating)

    async def get_scores_bulk(self) -> list[FinancialScore]:
        """Get financial scores in bulk"""
        raw = await self._request_csv(SCORES_BULK)
        return parse_csv_models(raw, FinancialScore)

    async def get_ratios_ttm_bulk(self) -> list[FinancialRatiosTTM]:
        """Get trailing twelve month financial ratios in bulk"""
        raw = await self._request_csv(RATIOS_TTM_BULK)
        return parse_csv_models(raw, FinancialRatiosTTM)

    async def get_price_target_summary_bulk(self) -> list[PriceTargetSummary]:
        """Get bulk price target summaries"""
        raw = await self._request_csv(PRICE_TARGET_SUMMARY_BULK)
        return parse_csv_models(raw, PriceTargetSummary)

    async def get_etf_holder_bulk(self, part: str) -> list[ETFHolding]:
        """Get bulk ETF holdings"""
        raw = await self._request_csv(ETF_HOLDER_BULK, part=part)
        return parse_csv_models(raw, ETFHolding)

    async def get_upgrades_downgrades_consensus_bulk(
        self,
    ) -> list[UpgradeDowngradeConsensus]:
        """Get bulk upgrades/downgrades consensus data"""
        raw = await self._request_csv(UPGRADES_DOWNGRADES_CONSENSUS_BULK)
        # Filter for rows with symbols before parsing to models
        rows = [row for row in parse_csv_rows(raw) if row.get("symbol")]
        # Use parse_csv_models pattern for graceful error handling
        results: list[UpgradeDowngradeConsensus] = []
        for row in rows:
            try:
                results.append(UpgradeDowngradeConsensus.model_validate(row))
            except PydanticValidationError as e:
                symbol = row.get("symbol", "unknown")
                self.client.logger.warning(
                    f"Failed to parse upgrade/downgrade row for {symbol}: {e}"
                )
        return results

    async def get_key_metrics_ttm_bulk(self) -> list[KeyMetricsTTM]:
        """Get bulk trailing twelve month key metrics"""
        raw = await self._request_csv(KEY_METRICS_TTM_BULK)
        return parse_csv_models(raw, KeyMetricsTTM)

    async def get_peers_bulk(self) -> list[PeersBulk]:
        """Get bulk peer lists"""
        raw = await self._request_csv(PEERS_BULK)
        return parse_csv_models(raw, PeersBulk)

    async def get_earnings_surprises_bulk(
        self, year: int
    ) -> list[EarningsSurpriseBulk]:
        """Get bulk earnings surprises for a given year"""
        raw = await self._request_csv(EARNINGS_SURPRISES_BULK, year=year)
        return parse_csv_models(raw, EarningsSurpriseBulk)

    async def get_income_statement_bulk(
        self, year: int, period: str
    ) -> list[IncomeStatement]:
        """Get bulk income statements"""
        raw = await self._request_csv(INCOME_STATEMENT_BULK, year=year, period=period)
        return parse_csv_models(raw, IncomeStatement)

    async def get_income_statement_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk income statement growth data"""
        raw = await self._request_csv(
            INCOME_STATEMENT_GROWTH_BULK, year=year, period=period
        )
        return parse_csv_models(raw, FinancialGrowth)

    async def get_balance_sheet_bulk(
        self, year: int, period: str
    ) -> list[BalanceSheet]:
        """Get bulk balance sheet statements"""
        raw = await self._request_csv(
            BALANCE_SHEET_STATEMENT_BULK, year=year, period=period
        )
        return parse_csv_models(raw, BalanceSheet)

    async def get_balance_sheet_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk balance sheet growth data"""
        raw = await self._request_csv(
            BALANCE_SHEET_STATEMENT_GROWTH_BULK, year=year, period=period
        )
        return parse_csv_models(raw, FinancialGrowth)

    async def get_cash_flow_bulk(
        self, year: int, period: str
    ) -> list[CashFlowStatement]:
        """Get bulk cash flow statements"""
        raw = await self._request_csv(
            CASH_FLOW_STATEMENT_BULK, year=year, period=period
        )
        return parse_csv_models(raw, CashFlowStatement)

    async def get_cash_flow_growth_bulk(
        self, year: int, period: str
    ) -> list[FinancialGrowth]:
        """Get bulk cash flow growth data"""
        raw = await self._request_csv(
            CASH_FLOW_STATEMENT_GROWTH_BULK, year=year, period=period
        )
        return parse_csv_models(raw, FinancialGrowth)

    async def get_eod_bulk(self, target_date: date) -> list[EODBulk]:
        """Get bulk end-of-day prices"""
        date_param = target_date.strftime("%Y-%m-%d")
        raw = await self._request_csv(EOD_BULK, date=date_param)
        return parse_csv_models(raw, EODBulk)
