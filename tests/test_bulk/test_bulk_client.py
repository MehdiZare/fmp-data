# tests/test_bulk/test_bulk_client.py
from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.bulk.models import BulkEODPrice, BulkIncomeStatement, BulkQuote


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
            "marketCap": 2500000000000,
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
def mock_bulk_income_statements():
    """Mock bulk income statements data"""
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


@patch("httpx.Client.request")
def test_get_bulk_quotes(mock_request, fmp_client, mock_response, mock_bulk_quotes):
    """Test getting bulk quotes"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_bulk_quotes
    )

    quotes = fmp_client.bulk.get_bulk_quotes(["AAPL"])
    assert isinstance(quotes, list)
    assert len(quotes) == 1
    assert isinstance(quotes[0], BulkQuote)
    assert quotes[0].symbol == "AAPL"
    assert quotes[0].price == 150.25


@patch("httpx.Client.request")
def test_get_batch_eod_prices(mock_request, fmp_client, mock_response, mock_eod_prices):
    """Test getting batch end-of-day prices"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_eod_prices
    )

    prices = fmp_client.bulk.get_batch_eod_prices(date(2024, 1, 5))
    assert isinstance(prices, list)
    assert len(prices) == 1
    assert isinstance(prices[0], BulkEODPrice)
    assert prices[0].close == 150.25


@patch("httpx.Client.request")
def test_get_bulk_income_statements(
    mock_request, fmp_client, mock_response, mock_bulk_income_statements
):
    """Test getting bulk income statements"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_bulk_income_statements
    )

    statements = fmp_client.bulk.get_bulk_income_statements(2023)
    assert isinstance(statements, list)
    assert len(statements) == 1
    assert isinstance(statements[0], BulkIncomeStatement)
    assert statements[0].revenue == 394328000000
