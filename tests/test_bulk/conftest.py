# tests/test_bulk/conftest.py
import pytest


@pytest.fixture
def mock_bulk_quotes():
    """Mock bulk quotes data"""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.50,
            "dayHigh": 151.00,
            "yearHigh": 155.00,
            "yearLow": 120.00,
            "marketCap": 2500000000000.0,
            "volume": 82034567,
            "avgVolume": 75000000,
            "exchange": "NASDAQ",
            "open": 149.00,
            "previousClose": 148.00,
            "timestamp": "2024-01-05T16:00:00",
        }
    ]


@pytest.fixture
def mock_eod_prices():
    """Mock end-of-day prices data"""
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-05",
            "open": 149.00,
            "high": 151.00,
            "low": 148.50,
            "close": 150.25,
            "adjClose": 150.25,
            "volume": 82034567,
        }
    ]


@pytest.fixture
def mock_bulk_eod_prices():
    """Mock end-of-day prices data"""
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-05",
            "open": 149.00,
            "high": 151.00,
            "low": 148.50,
            "close": 150.25,
            "adjClose": 150.25,
            "volume": 82034567,
        }
    ]


@pytest.fixture
def mock_bulk_income_statements():
    """Mock bulk income statement data"""
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-05",
            "period": "annual",
            "currency": "USD",
            "filingDate": "2024-02-01",
            "revenue": 394328000000,
            "grossProfit": 170782000000,
            "operatingIncome": 116722000000,
            "netIncome": 96995000000,
            "eps": 6.16,
            "epsDiluted": 6.14,
        }
    ]
