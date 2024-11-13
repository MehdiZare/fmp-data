# tests/test_market/test_market_models.py
from datetime import datetime

from fmp_data.market.models import HistoricalPrice, Quote


def test_quote_model(mock_quote_data):
    """Test Quote model validation"""
    quote = Quote.model_validate(mock_quote_data)
    assert isinstance(quote.price, float)
    assert quote.price == 150.25
    assert isinstance(quote.market_cap, float)
    assert quote.market_cap == 2500000000000.0
    assert isinstance(quote.timestamp, datetime)
    assert quote.price_avg_50 == 145.50
    assert quote.price_avg_200 == 140.00


def test_historical_price_model(mock_historical_data):
    """Test HistoricalPrice model validation"""
    price = HistoricalPrice.model_validate(mock_historical_data[0])
    assert isinstance(price.open, float)
    assert price.open == 149.00
    assert isinstance(price.close, float)
    assert price.close == 150.25
    assert isinstance(price.date, datetime)
    assert price.adj_close == 150.25
