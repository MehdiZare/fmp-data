from datetime import date, datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

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


def test_bulk_quote_model(mock_bulk_quotes):
    """Test BulkQuote model validation"""
    quote_data = mock_bulk_quotes[0]
    quote_data["timestamp"] = "2024-01-05T16:00:00"  # Ensure proper datetime format

    quote = BulkQuote.model_validate(quote_data)

    # Test all fields
    assert quote.symbol == "AAPL"
    assert quote.name == "Apple Inc."
    assert isinstance(quote.price, float)
    assert quote.price == 150.25
    assert isinstance(quote.change_percentage, float)
    assert quote.change_percentage == 1.5
    assert isinstance(quote.timestamp, datetime)


def test_bulk_eod_price_model(mock_eod_prices):
    """Test BulkEODPrice model validation"""
    price_data = mock_eod_prices[0]
    price_data["date"] = "2024-01-05"  # Ensure proper date format

    price = BulkEODPrice.model_validate(price_data)

    # Test all fields
    assert price.symbol == "AAPL"
    assert isinstance(price.open, float)
    assert price.open == 149.00
    assert isinstance(price.close, float)
    assert price.close == 150.25
    assert isinstance(price.volume, int)
    assert price.volume == 82034567


def test_bulk_income_statement_model(mock_bulk_income_statements):
    """Test BulkIncomeStatement model validation"""
    statement_data = mock_bulk_income_statements[0]
    statement_data["date"] = "2024-01-05"  # Ensure proper date format

    statement = BulkIncomeStatement.model_validate(statement_data)

    # Test all fields
    assert statement.symbol == "AAPL"
    assert statement.period == "annual"
    assert statement.currency == "USD"
    assert isinstance(statement.revenue, float)
    assert statement.revenue == 394328000000
    assert isinstance(statement.net_income, float)
    assert statement.net_income == 96995000000


def test_invalid_bulk_quote():
    """Test BulkQuote model with invalid data"""
    invalid_data = {
        "symbol": "AAPL",
        "price": "not a number",  # Invalid type
        "timestamp": "invalid date",  # Invalid date format
    }

    with pytest.raises(ValidationError) as exc_info:
        BulkQuote.model_validate(invalid_data)
    assert "Input should be a valid number" in str(exc_info.value)


def test_invalid_bulk_eod_price():
    """Test BulkEODPrice model with invalid data"""
    invalid_data = {"symbol": "AAPL", "date": "invalid date", "volume": "not a number"}

    with pytest.raises(ValidationError) as exc_info:
        BulkEODPrice.model_validate(invalid_data)
    assert "Input should be a valid date" in str(exc_info.value)


def test_invalid_bulk_income_statement():
    """Test BulkIncomeStatement model with invalid data"""
    invalid_data = {"symbol": "AAPL", "revenue": "not a number", "date": "invalid date"}

    with pytest.raises(ValidationError) as exc_info:
        BulkIncomeStatement.model_validate(invalid_data)
    assert any(
        [
            "Input should be a valid number" in str(exc_info.value),
            "Input should be a valid date" in str(exc_info.value),
        ]
    )


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
