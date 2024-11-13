# tests/test_fundamental/test_fundamental_client.py
from unittest.mock import Mock, patch

import httpx
import pytest

from fmp_data.fundamental.models import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    KeyMetrics,
)


@pytest.fixture
def mock_income_statement():
    """Mock income statement data"""
    return {
        "date": "2024-01-05",
        "symbol": "AAPL",
        "reportedCurrency": "USD",
        "period": "annual",
        "fillingDate": "2024-02-01",
        "acceptedDate": "2024-02-01",
        "calendarYear": 2023,
        "periodLength": "12 months",
        "revenue": 394328000000,
        "costOfRevenue": 223546000000,
        "grossProfit": 170782000000,
        "operatingExpenses": 54060000000,
        "operatingIncome": 116722000000,
        "netIncome": 96995000000,
        "eps": 6.16,
        "ebitda": 130508000000,
    }


@pytest.fixture
def mock_balance_sheet():
    """Mock balance sheet data"""
    return {
        "date": "2024-01-05",
        "symbol": "AAPL",
        "reportedCurrency": "USD",
        "period": "annual",
        "fillingDate": "2024-02-01",
        "acceptedDate": "2024-02-01",
        "calendarYear": 2023,
        "periodLength": "12 months",
        "totalAssets": 352755000000,
        "totalLiabilities": 287912000000,
        "totalEquity": 64843000000,
        "cashAndEquivalents": 29965000000,
        "shortTermDebt": 15982000000,
        "longTermDebt": 109280000000,
    }


@pytest.fixture
def mock_cash_flow():
    """Mock cash flow statement data"""
    return {
        "date": "2024-01-05",
        "symbol": "AAPL",
        "reportedCurrency": "USD",
        "period": "annual",
        "fillingDate": "2024-02-01",
        "acceptedDate": "2024-02-01",
        "calendarYear": 2023,
        "periodLength": "12 months",
        "operatingCashFlow": 122151000000,
        "investingCashFlow": -10731000000,
        "financingCashFlow": -111647000000,
        "netCashFlow": -227000000,
    }


@pytest.fixture
def mock_key_metrics():
    """Mock key metrics data"""
    return {
        "date": "2024-01-05",
        "revenuePerShare": 25.04,
        "netIncomePerShare": 6.16,
        "operatingCashFlowPerShare": 7.75,
        "freeCashFlowPerShare": 6.43,
    }


@patch("httpx.Client.request")
def test_get_income_statement(
    mock_request, fmp_client, mock_response, mock_income_statement
):
    """Test getting income statement"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_income_statement]
    )

    statements = fmp_client.fundamental.get_income_statement(
        "AAPL", period="annual", limit=1
    )
    assert isinstance(statements, list)
    assert len(statements) == 1
    assert isinstance(statements[0], IncomeStatement)
    assert statements[0].revenue == 394328000000
    assert statements[0].net_income == 96995000000


@patch("httpx.Client.request")
def test_get_balance_sheet(mock_request, fmp_client, mock_response, mock_balance_sheet):
    """Test getting balance sheet"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_balance_sheet]
    )

    statements = fmp_client.fundamental.get_balance_sheet(
        "AAPL", period="annual", limit=1
    )
    assert isinstance(statements, list)
    assert len(statements) == 1
    assert isinstance(statements[0], BalanceSheet)
    assert statements[0].total_assets == 352755000000
    assert statements[0].total_liabilities == 287912000000


@patch("httpx.Client.request")
def test_get_cash_flow(mock_request, fmp_client, mock_response, mock_cash_flow):
    """Test getting cash flow statement"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_cash_flow]
    )

    statements = fmp_client.fundamental.get_cash_flow("AAPL", period="annual", limit=1)
    assert isinstance(statements, list)
    assert len(statements) == 1
    assert isinstance(statements[0], CashFlowStatement)
    assert statements[0].operating_cash_flow == 122151000000
    assert statements[0].net_cash_flow == -227000000


@patch("httpx.Client.request")
def test_get_key_metrics(mock_request, fmp_client, mock_response, mock_key_metrics):
    """Test getting key metrics"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_key_metrics]
    )

    metrics = fmp_client.fundamental.get_key_metrics("AAPL", period="annual", limit=1)
    assert isinstance(metrics, list)
    assert len(metrics) == 1
    assert isinstance(metrics[0], KeyMetrics)
    assert metrics[0].revenue_per_share == 25.04
    assert metrics[0].net_income_per_share == 6.16


@patch("httpx.Client.request")
def test_period_parameter_validation(mock_request, fmp_client, mock_response):
    """Test period parameter validation"""
    error_response = httpx.HTTPStatusError(
        "Invalid period parameter",
        request=Mock(),
        response=Mock(
            status_code=400,
            text='Invalid value for period. Must be one of: ["annual", "quarter"]',
        ),
    )
    mock_request.side_effect = error_response

    with pytest.raises(Exception) as exc_info:
        fmp_client.fundamental.get_income_statement("AAPL", period="invalid")
    assert "annual" in str(exc_info.value)
    assert "quarter" in str(exc_info.value)
