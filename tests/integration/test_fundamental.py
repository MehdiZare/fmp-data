import logging
import time
from datetime import datetime

import pytest

from fmp_data import FMPDataClient
from fmp_data.fundamental.models import (
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    IncomeStatement,
    KeyMetrics,
)

from .base import BaseTestCase

logger = logging.getLogger(__name__)


class TestFundamentalEndpoints(BaseTestCase):
    """Test fundamental data endpoints"""

    TEST_SYMBOL = "AAPL"  # Use a stable stock for testing

    def test_get_income_statement(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting income statements"""
        with vcr_instance.use_cassette("fundamental/income_statement.yaml"):
            statements = self._handle_rate_limit(
                fmp_client.fundamental.get_income_statement,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(statements, list)
            assert len(statements) > 0

            for statement in statements:
                assert isinstance(statement, IncomeStatement)
                assert isinstance(statement.date, datetime)
                assert isinstance(statement.revenue, float)
                assert isinstance(statement.gross_profit, float)
                assert isinstance(statement.net_income, float)
                assert isinstance(statement.eps, float)

    def test_get_balance_sheet(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting balance sheets"""
        with vcr_instance.use_cassette("fundamental/balance_sheet.yaml"):
            sheets = self._handle_rate_limit(
                fmp_client.fundamental.get_balance_sheet,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(sheets, list)
            assert len(sheets) > 0

            for sheet in sheets:
                assert isinstance(sheet, BalanceSheet)
                assert isinstance(sheet.date, datetime)
                assert isinstance(sheet.total_assets, float)
                assert isinstance(sheet.total_liabilities, float)
                assert isinstance(sheet.total_equity, float)

    def test_get_cash_flow(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting cash flow statements"""
        with vcr_instance.use_cassette("fundamental/cash_flow.yaml"):
            statements = self._handle_rate_limit(
                fmp_client.fundamental.get_cash_flow,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(statements, list)
            assert len(statements) > 0

            for statement in statements:
                assert isinstance(statement, CashFlowStatement)
                assert isinstance(statement.date, datetime)
                assert isinstance(statement.operating_cash_flow, float)
                assert isinstance(statement.investing_cash_flow, float)
                assert isinstance(statement.financing_cash_flow, float)

    def test_get_key_metrics(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting key metrics"""
        with vcr_instance.use_cassette("fundamental/key_metrics.yaml"):
            metrics = self._handle_rate_limit(
                fmp_client.fundamental.get_key_metrics,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(metrics, list)
            assert len(metrics) > 0

            for metric in metrics:
                assert isinstance(metric, KeyMetrics)
                assert isinstance(metric.date, datetime)
                assert isinstance(metric.revenue_per_share, float)
                assert isinstance(metric.net_income_per_share, float)
                assert isinstance(metric.operating_cash_flow_per_share, float)

    def test_get_financial_ratios(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting financial ratios"""
        with vcr_instance.use_cassette("fundamental/financial_ratios.yaml"):
            ratios = self._handle_rate_limit(
                fmp_client.fundamental.get_financial_ratios,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(ratios, list)
            assert len(ratios) > 0

            for ratio in ratios:
                assert isinstance(ratio, FinancialRatios)
                assert isinstance(ratio.date, datetime)
                assert isinstance(ratio.current_ratio, float)
                assert isinstance(ratio.quick_ratio, float)
                assert isinstance(ratio.debt_equity_ratio, float)

    def test_get_full_financial_statement(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting full financial statements"""
        with vcr_instance.use_cassette("fundamental/full_financial_statement.yaml"):
            statements = self._handle_rate_limit(
                fmp_client.fundamental.get_full_financial_statement,
                symbol=self.TEST_SYMBOL,
                period="annual",
                limit=5,
            )

            assert isinstance(statements, list)
            assert len(statements) > 0

            for statement in statements:
                assert isinstance(statement, FinancialStatementFull)
                assert isinstance(statement.date, datetime)
                assert isinstance(statement.symbol, str)
                assert isinstance(statement.period, str)
                assert isinstance(statement.revenue, float)

    def test_get_financial_reports_dates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting financial report dates"""
        with vcr_instance.use_cassette("fundamental/financial_reports_dates.yaml"):
            dates = self._handle_rate_limit(
                fmp_client.fundamental.get_financial_reports_dates,
                symbol=self.TEST_SYMBOL,
            )

            assert isinstance(dates, list)
            if len(dates) > 0:
                for date_obj in dates:
                    assert isinstance(date_obj, FinancialReportDate)
                    assert date_obj.symbol == self.TEST_SYMBOL
                    assert isinstance(date_obj.report_date, str)
                    assert isinstance(date_obj.period, str)

    def test_period_parameter(self, fmp_client: FMPDataClient, vcr_instance):
        """Test different period parameters"""
        with vcr_instance.use_cassette("fundamental/quarterly_data.yaml"):
            # Test with quarterly data
            statements = self._handle_rate_limit(
                fmp_client.fundamental.get_income_statement,
                symbol=self.TEST_SYMBOL,
                period="quarter",
                limit=4,
            )

            assert isinstance(statements, list)
            assert len(statements) > 0
            for statement in statements:
                # Check that period indicates a quarter (Q1-Q4)
                assert statement.period in ["Q1", "Q2", "Q3", "Q4"]

    def test_error_handling_invalid_period(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test error handling for invalid period parameter"""
        with vcr_instance.use_cassette("fundamental/error_invalid_period.yaml"):
            with pytest.raises(ValueError) as exc_info:
                self._handle_rate_limit(
                    fmp_client.fundamental.get_income_statement,
                    symbol=self.TEST_SYMBOL,
                    period="invalid_period",
                )
            assert "Must be one of: ['annual', 'quarter']" in str(exc_info.value)

    def test_rate_limiting(self, fmp_client: FMPDataClient, vcr_instance):
        """Test rate limiting handling"""
        with vcr_instance.use_cassette("fundamental/rate_limit.yaml"):
            # Make multiple requests to test rate limiting
            for _ in range(3):
                result = self._handle_rate_limit(
                    fmp_client.fundamental.get_income_statement,
                    symbol=self.TEST_SYMBOL,
                    limit=1,
                )
                assert isinstance(result, list)
                time.sleep(1)  # Add small delay between requests
