# fmp_data/fundamental/async_client.py
"""Async client for fundamental analysis endpoints."""

from fmp_data.base import AsyncEndpointGroup
from fmp_data.fundamental import endpoints
from fmp_data.fundamental.models import (
    DCF,
    BalanceSheet,
    CashFlowStatement,
    CustomDCF,
    CustomLeveredDCF,
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    HistoricalRating,
    IncomeStatement,
    KeyMetrics,
    LatestFinancialStatement,
    LeveredDCF,
    OwnerEarnings,
)
from fmp_data.helpers import deprecated
from fmp_data.schema import Period


class AsyncFundamentalClient(AsyncEndpointGroup):
    """Async client for fundamental analysis endpoints."""

    async def get_income_statement(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[IncomeStatement]:
        """Get income statements"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.INCOME_STATEMENT, symbol=symbol, period=period, limit=limit
            ),
            IncomeStatement,
        )

    async def get_balance_sheet(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[BalanceSheet]:
        """Get balance sheets"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.BALANCE_SHEET, symbol=symbol, period=period, limit=limit
            ),
            BalanceSheet,
        )

    async def get_cash_flow(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[CashFlowStatement]:
        """Get cash flow statements"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CASH_FLOW, symbol=symbol, period=period, limit=limit
            ),
            CashFlowStatement,
        )

    async def get_latest_financial_statements(
        self, page: int = 0, limit: int = 250
    ) -> list[LatestFinancialStatement]:
        """Get latest financial statement metadata across symbols"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.LATEST_FINANCIAL_STATEMENTS, page=page, limit=limit
            ),
            LatestFinancialStatement,
        )

    async def get_key_metrics(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[KeyMetrics]:
        """Get key financial metrics"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.KEY_METRICS, symbol=symbol, period=period, limit=limit
            ),
            KeyMetrics,
        )

    async def get_financial_ratios(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[FinancialRatios]:
        """Get financial ratios"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FINANCIAL_RATIOS, symbol=symbol, period=period, limit=limit
            ),
            FinancialRatios,
        )

    async def get_full_financial_statement(
        self, symbol: str, period: Period = "annual", limit: int | None = None
    ) -> list[FinancialStatementFull]:
        """Get full financial statements as reported"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FULL_FINANCIAL_STATEMENT,
                symbol=symbol,
                period=period,
                limit=limit,
            ),
            FinancialStatementFull,
        )

    async def get_financial_reports_dates(
        self, symbol: str
    ) -> list[FinancialReportDate]:
        """Get list of financial reports dates"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.FINANCIAL_REPORTS_DATES, symbol=symbol
            ),
            FinancialReportDate,
        )

    async def get_owner_earnings(
        self, symbol: str, limit: int | None = None
    ) -> list[OwnerEarnings]:
        """Get owner earnings metrics"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.OWNER_EARNINGS, symbol=symbol, limit=limit
            ),
            OwnerEarnings,
        )

    async def get_levered_dcf(self, symbol: str) -> list[LeveredDCF]:
        """Get levered DCF valuation"""
        return self._unwrap_list(
            await self.client.request_async(endpoints.LEVERED_DCF, symbol=symbol),
            LeveredDCF,
        )

    @deprecated(
        "historical-rating is dead. The live path ratings-historical is "
        "already shipped as FMPDataClient.intelligence.get_ratings_historical"
        "(symbol); this method is a leftover declaration. The scoring fields "
        "differ -- overallScore and per-metric scores, not ratingScore."
    )
    async def get_historical_rating(self, symbol: str) -> list[HistoricalRating]:
        """Get historical company ratings

        .. deprecated::
            ``historical-rating`` 404s and will be removed in a future
            version. It currently returns an empty list. Use
            ``client.intelligence.get_ratings_historical(symbol)``, which
            serves the live ``ratings-historical``. It is not a drop-in: that
            payload carries ``overallScore`` plus per-metric scores
            (``discountedCashFlowScore``, ``returnOnEquityScore``, …) where
            this model declared ``ratingScore``, ``ratingDetails`` and
            ``ratingRecommendation``.
        """
        return []

    async def get_discounted_cash_flow(self, symbol: str) -> list[DCF]:
        """Get discounted cash flow valuation"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.DISCOUNTED_CASH_FLOW, symbol=symbol
            ),
            DCF,
        )

    async def get_custom_discounted_cash_flow(self, symbol: str) -> list[CustomDCF]:
        """Get advanced DCF analysis with detailed projections"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CUSTOM_DISCOUNTED_CASH_FLOW, symbol=symbol
            ),
            CustomDCF,
        )

    async def get_custom_levered_dcf(self, symbol: str) -> list[CustomLeveredDCF]:
        """Get levered DCF analysis using FCFE"""
        return self._unwrap_list(
            await self.client.request_async(
                endpoints.CUSTOM_LEVERED_DCF, symbol=symbol
            ),
            CustomLeveredDCF,
        )
