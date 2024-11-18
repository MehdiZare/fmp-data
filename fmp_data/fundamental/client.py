# fmp_data/fundamental/client.py
from datetime import datetime

from fmp_data.base import EndpointGroup
from fmp_data.fundamental import endpoints
from fmp_data.fundamental.models import (
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    FinancialStatementFull,
    IncomeStatement,
    KeyMetrics,
)


class FundamentalClient(EndpointGroup):
    """Client for fundamental analysis endpoints"""

    def get_income_statement(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[IncomeStatement]:
        """Get income statements"""
        return self.client.request(
            endpoints.INCOME_STATEMENT, symbol=symbol, period=period, limit=limit
        )

    def get_balance_sheet(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[BalanceSheet]:
        """Get balance sheets"""
        return self.client.request(
            endpoints.BALANCE_SHEET, symbol=symbol, period=period, limit=limit
        )

    def get_cash_flow(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[CashFlowStatement]:
        """Get cash flow statements"""
        return self.client.request(
            endpoints.CASH_FLOW, symbol=symbol, period=period, limit=limit
        )

    def get_key_metrics(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[KeyMetrics]:
        """Get key financial metrics"""
        return self.client.request(
            endpoints.KEY_METRICS, symbol=symbol, period=period, limit=limit
        )

    def get_financial_ratios(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[FinancialRatios]:
        """Get financial ratios"""
        return self.client.request(
            endpoints.FINANCIAL_RATIOS, symbol=symbol, period=period, limit=limit
        )

    def get_full_financial_statement(
        self, symbol: str, period: str = "annual", limit: int | None = None
    ) -> list[FinancialStatementFull]:
        """Get full financial statements as reported"""
        return self.client.request(
            endpoints.FULL_FINANCIAL_STATEMENT,
            symbol=symbol,
            period=period,
            limit=limit,
        )

    def get_financial_report_dates(self, symbol: str) -> list[datetime]:
        """Get list of financial report dates"""
        return self.client.request(endpoints.FINANCIAL_REPORTS_DATES, symbol=symbol)
