import unittest
from unittest.mock import MagicMock

from fmp_data.fundamental.client import FundamentalClient
from fmp_data.fundamental.endpoints import FINANCIAL_REPORTS_DATES, INCOME_STATEMENT
from fmp_data.fundamental.models import (
    FinancialRatios,
    FinancialReportDate,
    FinancialStatementFull,
    IncomeStatement,
)


def dict_to_model(model_class, data):
    """Helper to convert dict to pydantic model instance"""
    if isinstance(data, list):
        return [model_class.model_validate(item) for item in data]
    return model_class.model_validate(data)


class TestFundamentalEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method"""
        self.mock_client = MagicMock()
        self.fundamental_client = FundamentalClient(self.mock_client)
        self.symbol = "AAPL"

        # Sample test data with all required fields
        self.sample_income_statement = {
            "date": "2024-09-28",
            "symbol": "AAPL",
            "reportedCurrency": "USD",
            "cik": "0000320193",
            "fillingDate": "2024-11-01",
            "acceptedDate": "2024-11-01 06:01:36",
            "calendarYear": "2024",
            "period": "Q4",
            "link": "https://www.sec.gov/dummy",
            "finalLink": "https://www.sec.gov/dummy/final",
            # Required operating metrics
            "revenue": 94930000000,
            "costOfRevenue": 51051000000,
            "grossProfit": 43879000000,
            "grossProfitRatio": 0.4622247972,
            "researchAndDevelopmentExpenses": 7765000000,
            "sellingGeneralAndAdministrativeExpenses": 6523000000,
            "operatingExpenses": 14288000000,
            "costAndExpenses": 65339000000,
            "operatingIncome": 29591000000,
            "operatingIncomeRatio": 0.3117138944,
            # Required financial metrics
            "ebitda": 32502000000,
            "ebitdaratio": 0.3423785948,
            "incomeBeforeTax": 29610000000,
            "incomeBeforeTaxRatio": 0.3119140419,
            "incomeTaxExpense": 14874000000,
            "netIncome": 14736000000,
            "netIncomeRatio": 0.1553039293,
            # Required share data
            "eps": 0.96,
            "epsdiluted": 0.96,
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
                "linkXlsx": "https://fmpcloud.io/api/v4/financial-reports-xlsx?symbol=AAPL&year=2024&period=Q4",
                "linkJson": "https://fmpcloud.io/api/v4/financial-reports-json?symbol=AAPL&year=2024&period=Q4",
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

    def test_get_income_statement(self):
        """Test getting income statements"""
        # Configure mock to return model instance
        mock_response = dict_to_model(IncomeStatement, self.sample_income_statement)
        self.mock_client.request.return_value = [mock_response]

        # Execute request
        result = self.fundamental_client.get_income_statement(
            symbol=self.symbol, period="quarter"
        )

        # Verify request
        self.mock_client.request.assert_called_once_with(
            INCOME_STATEMENT, symbol=self.symbol, period="quarter", limit=None
        )

        # Verify response
        self.assertEqual(len(result), 1)
        income_stmt = result[0]
        self.assertIsInstance(income_stmt, IncomeStatement)
        self.assertEqual(income_stmt.symbol, self.symbol)
        self.assertEqual(income_stmt.revenue, 94930000000)
        self.assertEqual(income_stmt.period, "Q4")

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
            self.fundamental_client.get_income_statement(symbol=None)
        self.assertIn("Missing required parameter", str(context.exception))

    def tearDown(self):
        """Clean up after each test"""
        self.mock_client.reset_mock()


if __name__ == "__main__":
    unittest.main()
