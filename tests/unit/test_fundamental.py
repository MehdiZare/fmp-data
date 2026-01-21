import unittest
from unittest.mock import MagicMock

from fmp_data.fundamental.client import FundamentalClient
from fmp_data.fundamental.endpoints import (
    FINANCIAL_REPORTS_DATES,
    INCOME_STATEMENT,
    KEY_METRICS,
    LATEST_FINANCIAL_STATEMENTS,
    OWNER_EARNINGS,
)
from fmp_data.fundamental.models import (
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    IncomeStatement,
    LatestFinancialStatement,
    OwnerEarnings,
)


def dict_to_model(model_class, data):
    """Helper to convert dict to pydantic model instance"""
    if isinstance(data, list):
        return [model_class.model_validate(item) for item in data]
    return model_class.model_validate(data)


class TestFundamentalEndpoints(unittest.TestCase):
    """
    Test suite for fundamental analysis endpoints.

    Note: The FMP client has internal logic that converts limit=None to limit=12
    for certain endpoints. Tests should expect this behavior.
    """

    def setUp(self):
        """Set up test environment before each test method"""
        self.mock_client = MagicMock()
        self.fundamental_client = FundamentalClient(self.mock_client)
        self.symbol = "AAPL"

        # Sample test data matching actual FMP API response format
        self.sample_income_statement = {
            "date": "2024-09-28",
            "symbol": "AAPL",
            "reportedCurrency": "USD",
            "cik": "0000320193",
            "filingDate": "2024-11-01",  # Fixed typo: was "fillingDate"
            "acceptedDate": "2024-11-01 06:01:36",
            "fiscalYear": "2024",  # Fixed: was "calendarYear"
            "period": "FY",
            # Revenue and Cost
            "revenue": 391035000000,
            "costOfRevenue": 210352000000,
            "grossProfit": 180683000000,
            # Operating Expenses - all fields now included
            "researchAndDevelopmentExpenses": 31370000000,
            "generalAndAdministrativeExpenses": 0,
            "sellingAndMarketingExpenses": 0,
            "sellingGeneralAndAdministrativeExpenses": 26097000000,
            "otherExpenses": 0,
            "operatingExpenses": 57467000000,
            "costAndExpenses": 267819000000,
            # Interest and Income - all fields now included
            "netInterestIncome": 0,
            "interestIncome": 0,
            "interestExpense": 0,
            # Depreciation and EBITDA/EBIT - all fields now included
            "depreciationAndAmortization": 11445000000,
            "ebitda": 134661000000,
            "ebit": 123216000000,
            # Operating Income
            "nonOperatingIncomeExcludingInterest": 0,
            "operatingIncome": 123216000000,
            # Other Income and Pre-tax
            "totalOtherIncomeExpensesNet": 269000000,
            "incomeBeforeTax": 123485000000,
            # Tax and Net Income - all fields now included
            "incomeTaxExpense": 29749000000,
            "netIncomeFromContinuingOperations": 93736000000,
            "netIncomeFromDiscontinuedOperations": 0,
            "otherAdjustmentsToNetIncome": 0,
            "netIncome": 93736000000,
            "netIncomeDeductions": 0,
            "bottomLineNetIncome": 93736000000,
            # Earnings Per Share - fixed field names
            "eps": 6.11,
            "epsDiluted": 6.08,  # Fixed: was "epsdiluted"
            # Share Counts
            "weightedAverageShsOut": 15343783000,
            "weightedAverageShsOutDil": 15408095000,
        }

        self.sample_financial_ratios = {
            "symbol": "AAPL",
            "date": "2024-09-28",
            "currentRatio": 0.8673125765340832,
            "quickRatio": 0.8260068483831466,
            "debtEquityRatio": 1.872326602282704,
            "returnOnEquity": 1.6459350307287095,
        }

        self.sample_financial_reports_dates = [
            {
                "symbol": "AAPL",
                "date": "2024",
                "period": "Q4",
                "linkXlsx": "https://fmpcloud.io/stable/financial-reports-xlsx?symbol=AAPL&year=2024&period=Q4",
                "linkJson": "https://fmpcloud.io/stable/financial-reports-json?symbol=AAPL&year=2024&period=Q4",
            }
        ]

        self.sample_full_financial_statement = {
            "date": "2024-09-27",
            "symbol": "AAPL",
            "period": "FY",
            "documenttype": "10-K",
            "revenuefromcontractwithcustomerexcludingassessedtax": 391035000000,
            "costofgoodsandservicessold": 210352000000,
            "grossprofit": 180683000000,
        }
        self.sample_latest_financial_statement = {
            "symbol": "FGFI",
            "calendarYear": 2024,
            "period": "Q4",
            "date": "2024-12-31",
            "dateAdded": "2025-03-13 17:03:59",
        }
        self.sample_owner_earnings = {
            "date": "2024-12-28",
            "symbol": "AAPL",
            "ownersEarnings": 27655035250,
            "ownersEarningsPerShare": 1.83,
        }

    def test_get_income_statement(self):
        """Test getting income statements"""
        # Configure mock to return model instance
        mock_response = dict_to_model(IncomeStatement, self.sample_income_statement)
        self.mock_client.request.return_value = [mock_response]

        # Execute request
        result = self.fundamental_client.get_income_statement(
            symbol=self.symbol, period="annual"
        )

        # Verify the request was made correctly
        self.mock_client.request.assert_called_once_with(
            INCOME_STATEMENT, symbol=self.symbol, period="annual", limit=None
        )

        # Verify response
        self.assertEqual(len(result), 1)
        income_stmt = result[0]
        self.assertIsInstance(income_stmt, IncomeStatement)
        self.assertEqual(income_stmt.symbol, self.symbol)
        self.assertEqual(income_stmt.revenue, 391035000000)
        self.assertEqual(income_stmt.period, "FY")
        self.assertEqual(income_stmt.eps, 6.11)
        self.assertEqual(income_stmt.eps_diluted, 6.08)

    def test_get_income_statement_quarterly(self):
        """Test getting quarterly income statements"""
        # Configure mock to return model instance
        mock_response = dict_to_model(IncomeStatement, self.sample_income_statement)
        self.mock_client.request.return_value = [mock_response]

        # Execute request with explicit limit
        result = self.fundamental_client.get_income_statement(
            symbol=self.symbol, period="quarter", limit=4
        )

        # Verify the request was made correctly
        # (explicit limit should be passed through)
        self.mock_client.request.assert_called_once_with(
            INCOME_STATEMENT, symbol=self.symbol, period="quarter", limit=4
        )

        # Verify response
        self.assertEqual(len(result), 1)
        income_stmt = result[0]
        self.assertIsInstance(income_stmt, IncomeStatement)
        self.assertEqual(income_stmt.symbol, self.symbol)
        self.assertEqual(income_stmt.fiscal_year, "2024")

    def test_income_statement_period_validation(self):
        """Test period validation for income statements"""
        params = INCOME_STATEMENT.validate_params(
            {"symbol": self.symbol, "period": "Q1", "limit": 5}
        )
        self.assertEqual(params["period"], "Q1")

    def test_key_metrics_period_validation(self):
        """Test period validation for key metrics"""
        params = KEY_METRICS.validate_params(
            {"symbol": self.symbol, "period": "FY", "limit": 5}
        )
        self.assertEqual(params["period"], "FY")

    def test_income_statement_field_validation(self):
        """Test that income statement validates all required fields correctly"""
        # Test with minimal required data (base fields only)
        minimal_data = {
            "date": "2024-09-28",
            "symbol": "AAPL",
            "reportedCurrency": "USD",
            "cik": "0000320193",
            "filingDate": "2024-11-01",
            "acceptedDate": "2024-11-01 06:01:36",
            "fiscalYear": "2024",
            "period": "FY",
        }

        # This should work since all financial fields are optional with default=None
        income_stmt = IncomeStatement.model_validate(minimal_data)
        self.assertEqual(income_stmt.symbol, "AAPL")
        self.assertEqual(income_stmt.fiscal_year, "2024")
        self.assertIsNone(income_stmt.revenue)  # Optional field should be None
        self.assertIsNone(income_stmt.cost_of_revenue)
        self.assertIsNone(income_stmt.operating_income)

    def test_get_latest_financial_statements(self):
        """Test getting latest financial statements metadata"""
        mock_response = dict_to_model(
            LatestFinancialStatement, self.sample_latest_financial_statement
        )
        self.mock_client.request.return_value = [mock_response]

        result = self.fundamental_client.get_latest_financial_statements(
            page=0, limit=250
        )

        self.mock_client.request.assert_called_once_with(
            LATEST_FINANCIAL_STATEMENTS, page=0, limit=250
        )
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], LatestFinancialStatement)

    def test_get_financial_ratios(self):
        """Test getting financial ratios"""
        # Configure mock to return model instance
        mock_response = dict_to_model(FinancialRatios, self.sample_financial_ratios)
        self.mock_client.request.return_value = [mock_response]

        # Execute request
        result = self.fundamental_client.get_financial_ratios(
            symbol=self.symbol, period="annual"
        )

        # Verify response
        self.assertEqual(len(result), 1)
        ratio = result[0]
        self.assertIsInstance(ratio, FinancialRatios)
        self.assertAlmostEqual(ratio.current_ratio, 0.8673125765340832)

    def test_get_financial_reports_dates(self):
        """Test getting financial report dates"""
        # Configure mock to return model instances
        mock_response = dict_to_model(
            FinancialReportDate, self.sample_financial_reports_dates[0]
        )
        self.mock_client.request.return_value = [mock_response]

        # Execute request
        result = self.fundamental_client.get_financial_reports_dates(symbol=self.symbol)

        # Verify request and response
        self.mock_client.request.assert_called_once_with(
            FINANCIAL_REPORTS_DATES, symbol=self.symbol
        )

        self.assertEqual(len(result), 1)
        report_date = result[0]
        self.assertIsInstance(report_date, FinancialReportDate)
        self.assertEqual(report_date.symbol, self.symbol)
        self.assertEqual(report_date.period, "Q4")

    def test_get_owner_earnings_with_limit(self):
        """Test getting owner earnings with limit"""
        mock_response = dict_to_model(OwnerEarnings, self.sample_owner_earnings)
        self.mock_client.request.return_value = [mock_response]

        result = self.fundamental_client.get_owner_earnings(symbol=self.symbol, limit=5)

        self.mock_client.request.assert_called_once_with(
            OWNER_EARNINGS, symbol=self.symbol, limit=5
        )
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], OwnerEarnings)

    def test_get_full_financial_statement(self):
        """Test getting full financial statements"""
        # Configure mock to return model instance
        mock_response = dict_to_model(
            FinancialStatementFull, self.sample_full_financial_statement
        )
        self.mock_client.request.return_value = [mock_response]

        # Execute request
        result = self.fundamental_client.get_full_financial_statement(
            symbol=self.symbol, period="annual"
        )

        # Verify result
        self.assertEqual(len(result), 1)
        stmt = result[0]
        self.assertIsInstance(stmt, FinancialStatementFull)
        self.assertEqual(stmt.symbol, self.symbol)
        self.assertEqual(stmt.revenue, 391035000000)

    def test_income_statement_with_zero_values(self):
        """Test that income statement handles zero values correctly"""
        data_with_zeros = self.sample_income_statement.copy()
        data_with_zeros.update(
            {
                "generalAndAdministrativeExpenses": 0,
                "sellingAndMarketingExpenses": 0,
                "otherExpenses": 0,
                "netInterestIncome": 0,
                "interestIncome": 0,
                "interestExpense": 0,
            }
        )

        income_stmt = IncomeStatement.model_validate(data_with_zeros)
        self.assertEqual(income_stmt.general_and_administrative_expenses, 0)
        self.assertEqual(income_stmt.selling_and_marketing_expenses, 0)
        self.assertEqual(income_stmt.net_interest_income, 0)

    def test_income_statement_with_full_data(self):
        """Test that income statement parses full API response correctly"""
        # Use the complete sample data
        income_stmt = IncomeStatement.model_validate(self.sample_income_statement)

        # Verify all key fields are parsed correctly
        self.assertEqual(income_stmt.symbol, "AAPL")
        self.assertEqual(income_stmt.revenue, 391035000000)
        self.assertEqual(income_stmt.cost_of_revenue, 210352000000)
        self.assertEqual(income_stmt.gross_profit, 180683000000)
        self.assertEqual(income_stmt.operating_income, 123216000000)
        self.assertEqual(income_stmt.net_income, 93736000000)
        self.assertEqual(income_stmt.eps, 6.11)
        self.assertEqual(income_stmt.eps_diluted, 6.08)
        self.assertEqual(income_stmt.fiscal_year, "2024")
        self.assertEqual(income_stmt.period, "FY")

    def test_income_statement_with_missing_optional_fields(self):
        """Test that income statement works with missing optional fields"""
        minimal_data = {
            "date": "2024-09-28",
            "symbol": "AAPL",
            "reportedCurrency": "USD",
            "cik": "0000320193",
            "filingDate": "2024-11-01",
            "acceptedDate": "2024-11-01 06:01:36",
            "fiscalYear": "2024",
            "period": "FY",
            # Include only some financial fields
            "revenue": 391035000000,
            "netIncome": 93736000000,
            "eps": 6.11,
        }

        income_stmt = IncomeStatement.model_validate(minimal_data)
        self.assertEqual(income_stmt.revenue, 391035000000)
        self.assertEqual(income_stmt.net_income, 93736000000)
        self.assertEqual(income_stmt.eps, 6.11)
        # Optional fields should be None when not provided
        self.assertIsNone(income_stmt.cost_of_revenue)
        self.assertIsNone(income_stmt.ebitda)
        self.assertIsNone(income_stmt.eps_diluted)
        self.assertIsNone(income_stmt.operating_income)
        self.assertIsNone(income_stmt.gross_profit)

    def test_invalid_period_parameter(self):
        """Test handling of invalid period parameter"""
        with self.assertRaises(ValueError) as context:
            self.mock_client.request.side_effect = ValueError(
                "Invalid value for period. Must be one of: ['annual', 'quarter']"
            )
            self.fundamental_client.get_income_statement(
                symbol=self.symbol, period="invalid"
            )
        self.assertIn("Must be one of: ['annual', 'quarter']", str(context.exception))

    def test_missing_required_parameter(self):
        """Test handling of missing required parameter"""
        with self.assertRaises(ValueError) as context:
            self.mock_client.request.side_effect = ValueError(
                "Missing required parameter: symbol"
            )
            self.fundamental_client.get_income_statement(symbol=None)  # type: ignore[arg-type]
        self.assertIn("Missing required parameter", str(context.exception))

    def tearDown(self):
        """Clean up after each test"""
        self.mock_client.reset_mock()


if __name__ == "__main__":
    unittest.main()
