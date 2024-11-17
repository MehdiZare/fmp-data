import pytest


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
