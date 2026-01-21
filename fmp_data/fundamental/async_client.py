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


class AsyncFundamentalClient(AsyncEndpointGroup):
    """Async client for fundamental analysis endpoints."""

    async def get_income_statement(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[IncomeStatement]:
        """Get income statements"""
        return await self.client.request_async(
            endpoints.INCOME_STATEMENT, symbol=symbol, period=period, limit=limit
        )

    async def get_balance_sheet(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[BalanceSheet]:
        """Get balance sheets"""
        return await self.client.request_async(
            endpoints.BALANCE_SHEET, symbol=symbol, period=period, limit=limit
        )

    async def get_cash_flow(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[CashFlowStatement]:
        """Get cash flow statements"""
        return await self.client.request_async(
            endpoints.CASH_FLOW, symbol=symbol, period=period, limit=limit
        )

    async def get_latest_financial_statements(
        self, page: int = 0, limit: int = 250
    ) -> list[LatestFinancialStatement]:
        """Get latest financial statement metadata across symbols"""
        return await self.client.request_async(
            endpoints.LATEST_FINANCIAL_STATEMENTS, page=page, limit=limit
        )

    async def get_key_metrics(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[KeyMetrics]:
        """Get key financial metrics"""
        return await self.client.request_async(
            endpoints.KEY_METRICS, symbol=symbol, period=period, limit=limit
        )

    async def get_financial_ratios(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[FinancialRatios]:
        """Get financial ratios"""
        return await self.client.request_async(
            endpoints.FINANCIAL_RATIOS, symbol=symbol, period=period, limit=limit
        )

    async def get_full_financial_statement(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[FinancialStatementFull]:
        """Get full financial statements as reported"""
        return await self.client.request_async(
            endpoints.FULL_FINANCIAL_STATEMENT,
            symbol=symbol,
            period=period,
            limit=limit,
        )

    async def get_financial_reports_dates(
        self, symbol: str
    ) -> list[FinancialReportDate]:
        """Get list of financial reports dates"""
        return await self.client.request_async(
            endpoints.FINANCIAL_REPORTS_DATES, symbol=symbol
        )

    async def get_owner_earnings(
        self, symbol: str, limit: int | None = None
    ) -> list[OwnerEarnings]:
        """Get owner earnings metrics"""
        return await self.client.request_async(
            endpoints.OWNER_EARNINGS, symbol=symbol, limit=limit
        )

    async def get_levered_dcf(self, symbol: str) -> list[LeveredDCF]:
        """Get levered DCF valuation"""
        return await self.client.request_async(endpoints.LEVERED_DCF, symbol=symbol)

    async def get_historical_rating(self, symbol: str) -> list[HistoricalRating]:
        """Get historical company ratings"""
        return await self.client.request_async(
            endpoints.HISTORICAL_RATING, symbol=symbol
        )

    async def get_discounted_cash_flow(self, symbol: str) -> list[DCF]:
        """Get discounted cash flow valuation"""
        return await self.client.request_async(
            endpoints.DISCOUNTED_CASH_FLOW, symbol=symbol
        )

    async def get_custom_discounted_cash_flow(self, symbol: str) -> list[CustomDCF]:
        """Get advanced DCF analysis with detailed projections"""
        return await self.client.request_async(
            endpoints.CUSTOM_DISCOUNTED_CASH_FLOW, symbol=symbol
        )

    async def get_custom_levered_dcf(self, symbol: str) -> list[CustomLeveredDCF]:
        """Get levered DCF analysis using FCFE"""
        return await self.client.request_async(
            endpoints.CUSTOM_LEVERED_DCF, symbol=symbol
        )
