from datetime import datetime
import logging
import time

import pytest

from fmp_data import FMPDataClient, ValidationError
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
                if statement.investing_cash_flow is not None:
                    assert isinstance(statement.investing_cash_flow, float)
                if statement.financing_cash_flow is not None:
                    assert isinstance(statement.financing_cash_flow, float)

    def test_get_latest_financial_statements(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting latest financial statements metadata"""
        with vcr_instance.use_cassette("fundamental/latest_financial_statements.yaml"):
            statements = self._handle_rate_limit(
                fmp_client.fundamental.get_latest_financial_statements,
                page=0,
                limit=250,
            )

            assert isinstance(statements, list)
            if statements:
                assert isinstance(statements[0], LatestFinancialStatement)

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
                if metric.revenue_per_share is not None:
                    assert isinstance(metric.revenue_per_share, float)
                if metric.net_income_per_share is not None:
                    assert isinstance(metric.net_income_per_share, float)
                if metric.operating_cash_flow_per_share is not None:
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
                if ratio.current_ratio is not None:
                    assert isinstance(ratio.current_ratio, float)
                if ratio.quick_ratio is not None:
                    assert isinstance(ratio.quick_ratio, float)
                if ratio.debt_equity_ratio is not None:
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
                if statement.revenue is not None:
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
                    assert isinstance(date_obj.fiscal_year, int)
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
            with pytest.raises(ValidationError) as exc_info:
                self._handle_rate_limit(
                    fmp_client.fundamental.get_income_statement,
                    symbol=self.TEST_SYMBOL,
                    period="invalid_period",
                )
        assert (
            "Must be one of: ['annual', 'quarter', 'FY', 'Q1', 'Q2', 'Q3', 'Q4']"
            in str(exc_info.value)
        )

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

    def test_get_owner_earnings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting owner earnings metrics"""
        with vcr_instance.use_cassette("fundamental/owner_earnings.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_owner_earnings, self.TEST_SYMBOL
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], OwnerEarnings)

    def test_get_levered_dcf(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting levered DCF valuation"""
        with vcr_instance.use_cassette("fundamental/levered_dcf.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_levered_dcf, self.TEST_SYMBOL
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], LeveredDCF)

    def test_get_historical_rating(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical ratings"""
        with vcr_instance.use_cassette("fundamental/historical_rating.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_historical_rating, self.TEST_SYMBOL
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalRating)

    def test_get_discounted_cash_flow(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting discounted cash flow valuation"""
        with vcr_instance.use_cassette("fundamental/discounted_cash_flow.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_discounted_cash_flow, self.TEST_SYMBOL
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], DCF)

    def test_get_custom_discounted_cash_flow(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting custom DCF analysis"""
        with vcr_instance.use_cassette("fundamental/custom_discounted_cash_flow.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_custom_discounted_cash_flow,
                self.TEST_SYMBOL,
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], CustomDCF)

    def test_get_custom_levered_dcf(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting custom levered DCF analysis"""
        with vcr_instance.use_cassette("fundamental/custom_levered_dcf.yaml"):
            results = self._handle_rate_limit(
                fmp_client.fundamental.get_custom_levered_dcf, self.TEST_SYMBOL
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], CustomLeveredDCF)
