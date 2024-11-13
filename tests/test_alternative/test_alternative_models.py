# tests/test_alternative/test_alternative_models.py
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from fmp_data.alternative.models import CommodityQuote, CryptoQuote, ForexQuote


def test_crypto_quote_model(mock_crypto_quote):
    """Test CryptoQuote model validation"""
    # Ensure timestamp is in proper format
    mock_crypto_quote["timestamp"] = "2024-01-05T16:00:00"
    quote = CryptoQuote.model_validate(mock_crypto_quote)
    assert quote.symbol == "BTC/USD"
    assert isinstance(quote.price, Decimal)
    assert isinstance(quote.timestamp, datetime)


def test_forex_quote_model(mock_forex_quote):
    """Test ForexQuote model validation"""
    mock_forex_quote["timestamp"] = "2024-01-05T16:00:00"
    quote = ForexQuote.model_validate(mock_forex_quote)
    assert quote.symbol == "EUR/USD"
    assert isinstance(quote.price, Decimal)
    assert isinstance(quote.timestamp, datetime)


def test_commodity_quote_model(mock_commodity_quote):
    """Test CommodityQuote model validation"""
    quote = CommodityQuote.model_validate(mock_commodity_quote)
    assert quote.symbol == "GC"
    assert quote.price == 2050.50
    assert quote.year_high == 2150.00
    assert quote.year_low == 1800.00
    assert isinstance(quote.timestamp, datetime)


@pytest.mark.parametrize(
    "model,data",
    [
        (CryptoQuote, {"symbol": "BTC/USD", "price": 45000}),
        (ForexQuote, {"symbol": "EUR/USD", "price": 1.0950}),
        (CommodityQuote, {"symbol": "GC", "price": 2050.50}),
    ],
)
def test_required_fields(model, data):
    """Test required fields validation"""
    with pytest.raises(ValidationError) as exc_info:
        model.model_validate(data)
    assert "Field required" in str(exc_info.value)
