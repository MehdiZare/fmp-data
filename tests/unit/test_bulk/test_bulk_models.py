# tests/test_bulk/test_bulk_models.py
from datetime import datetime

import pytest
from pydantic import ValidationError

from fmp_data.bulk.models import BulkEODPrice, BulkIncomeStatement, BulkQuote


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
