# fmp_data/bulk/client.py
from datetime import date

from fmp_data.base import EndpointGroup
from fmp_data.bulk.endpoints import (
    BATCH_EOD,
    BULK_BALANCE_SHEETS,
    BULK_CASH_FLOWS,
    BULK_COMPANY_PROFILES,
    BULK_EARNINGS_SURPRISES,
    BULK_FINANCIAL_GROWTH,
    BULK_INCOME_STATEMENTS,
    BULK_KEY_METRICS,
    BULK_QUOTES,
    BULK_RATIOS,
    BULK_STOCK_PEERS,
)
from fmp_data.bulk.models import (
    BulkBalanceSheet,
    BulkCashFlowStatement,
    BulkCompanyProfile,
    BulkEarningSurprise,
    BulkEODPrice,
    BulkFinancialGrowth,
    BulkIncomeStatement,
    BulkKeyMetric,
    BulkQuote,
    BulkRatio,
    BulkStockPeer,
)


class BulkClient(EndpointGroup):
    """Client for bulk data access endpoints"""

    def get_bulk_quotes(self, symbols: list[str]) -> list[BulkQuote]:
        """
        Get quotes for multiple companies

        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT"])
        """
        symbols_str = ",".join(symbols)
        return self.client.request(BULK_QUOTES, symbols=symbols_str)

    def get_batch_eod_prices(self, trading_date: date) -> list[BulkEODPrice]:
        """
        Get end-of-day prices for all stocks on a specific date

        Args:
            trading_date: Trading date to get prices for
        """
        return self.client.request(BATCH_EOD, date=trading_date.strftime("%Y-%m-%d"))

    def get_bulk_income_statements(
        self, year: int, period: str = "annual"
    ) -> list[BulkIncomeStatement]:
        """
        Get income statements for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_INCOME_STATEMENTS, year=year, period=period)

    def get_bulk_balance_sheets(
        self, year: int, period: str = "annual"
    ) -> list[BulkBalanceSheet]:
        """
        Get balance sheets for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_BALANCE_SHEETS, year=year, period=period)

    def get_bulk_cash_flows(
        self, year: int, period: str = "annual"
    ) -> list[BulkCashFlowStatement]:
        """
        Get cash flow statements for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_CASH_FLOWS, year=year, period=period)

    def get_bulk_ratios(self, year: int, period: str = "annual") -> list[BulkRatio]:
        """
        Get financial ratios for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_RATIOS, year=year, period=period)

    def get_bulk_key_metrics(
        self, year: int, period: str = "annual"
    ) -> list[BulkKeyMetric]:
        """
        Get key metrics for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_KEY_METRICS, year=year, period=period)

    def get_bulk_earnings_surprises(self) -> list[BulkEarningSurprise]:
        """Get earnings surprises for all companies"""
        return self.client.request(BULK_EARNINGS_SURPRISES)

    def get_bulk_company_profiles(self, part: int = 0) -> list[BulkCompanyProfile]:
        """
        Get company profiles in bulk

        Args:
            part: Data part number (for pagination)
        """
        return self.client.request(BULK_COMPANY_PROFILES, part=part)

    def get_bulk_stock_peers(self) -> list[BulkStockPeer]:
        """Get stock peers for all companies"""
        return self.client.request(BULK_STOCK_PEERS)

    def get_bulk_financial_growth(
        self, year: int, period: str = "annual"
    ) -> list[BulkFinancialGrowth]:
        """
        Get financial growth data for all companies

        Args:
            year: Filing year
            period: Filing period ("annual" or "quarter")
        """
        return self.client.request(BULK_FINANCIAL_GROWTH, year=year, period=period)
