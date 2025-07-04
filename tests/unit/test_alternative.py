from datetime import date, datetime

from pydantic import ValidationError
import pytest

from fmp_data.alternative.models import (
    CommodityQuote,
    CryptoHistoricalPrice,
    CryptoQuote,
    ForexQuote,
)


@pytest.fixture
def mock_crypto_quote():
    """Mock cryptocurrency quote data"""
    return {
        "symbol": "BTC/USD",
        "name": "Bitcoin",
        "price": 45000.00,
        "change": 1250.00,
        "changesPercentage": 2.85,
        "timestamp": 1704470400,  # Unix timestamp for "2024-01-05T16:00:00Z"
        "dayLow": 44000.00,
        "dayHigh": 46000.00,
        "yearHigh": 48000.00,
        "yearLow": 40000.00,
        "marketCap": 880000000000,
        "volume": 25000000000,
        "avgVolume": 20000000000,
        "open": 43750.00,
        "previousClose": 43750.00,
        "exchange": "CRYPTO",
        "sharesOutstanding": 19500000,
    }


@pytest.fixture
def mock_forex_quote():
    """Mock forex quote data"""
    return {
        "symbol": "EUR/USD",
        "price": 1.0950,
        "change": 0.0025,
        "changesPercentage": 0.23,
        "timestamp": 1704470400,  # Unix timestamp
        "dayLow": 1.0920,
        "dayHigh": 1.0980,
        "yearHigh": 1.1200,
        "yearLow": 1.0500,
        "volume": 100000,
        "avgVolume": 95000,
        "open": 1.0925,
        "previousClose": 1.0925,
        "exchange": "FOREX",
    }


@pytest.fixture
def mock_commodity_quote():
    """Mock commodity quote data"""
    return {
        "symbol": "GC",
        "name": "Gold Futures",
        "price": 2050.50,
        "change": 15.30,
        "changesPercentage": 0.75,
        "timestamp": 1704470400,  # Unix timestamp
        "yearHigh": 2150.00,
        "yearLow": 1800.00,
        "volume": 245000,
    }


@pytest.fixture
def mock_crypto_historical():
    """Mock cryptocurrency historical price data"""
    return {
        "symbol": "BTC/USD",
        "historical": [
            {
                "date": "2024-01-05",
                "open": 43750.00,
                "high": 45200.00,
                "low": 43500.00,
                "close": 45000.00,
                "adjClose": 45000.00,
                "volume": 25000000000,
                "unadjustedVolume": 25000000000,
                "change": 1250.00,
                "changePercent": 2.85,
                "vwap": 44500.00,
                "label": "January 05, 24",
                "changeOverTime": 0.0285,
            }
        ],
    }


def test_crypto_quote_model(mock_crypto_quote):
    """Test CryptoQuote model validation"""
    quote = CryptoQuote.model_validate(mock_crypto_quote)
    assert quote.symbol == "BTC/USD"
    assert quote.name == "Bitcoin"
    assert quote.price == 45000.00
    assert quote.change == 1250.00
    assert quote.change_percent == 2.85
    assert isinstance(quote.timestamp, datetime)
    # Update test to check timezone agnostic
    assert (
        quote.timestamp.utcoffset().total_seconds() == 0
    )  # Check if it's a UTC timezone


def test_forex_quote_model(mock_forex_quote):
    """Test ForexQuote model validation"""
    quote = ForexQuote.model_validate(mock_forex_quote)
    assert quote.symbol == "EUR/USD"
    assert quote.price == 1.0950
    assert quote.change == 0.0025
    assert quote.change_percent == 0.23
    assert isinstance(quote.timestamp, datetime)
    # Update test to check timezone agnostic
    assert (
        quote.timestamp.utcoffset().total_seconds() == 0
    )  # Check if it's a UTC timezone


@pytest.mark.parametrize(
    "model,data",
    [
        (CryptoQuote, {}),  # Missing required symbol
        (
            ForexQuote,
            {"changesPercentage": 0.5},
        ),  # Missing symbol but has change_percent
        (ForexQuote, {"symbol": "EUR/USD"}),  # Missing required change_percent
        (CommodityQuote, {"symbol": "GC"}),  # Missing required change_percent
    ],
)
def test_required_fields(model, data):
    """Test required fields validation"""
    with pytest.raises(ValidationError):
        model.model_validate(data)


def test_crypto_historical_price_model(mock_crypto_historical):
    """Test CryptoHistoricalPrice model validation"""
    historical_data = mock_crypto_historical["historical"][0]
    price = CryptoHistoricalPrice.model_validate(historical_data)

    assert price.price_date == date(2024, 1, 5)
    assert price.open == 43750.00
    assert price.high == 45200.00
    assert price.low == 43500.00
    assert price.close == 45000.00
    assert price.adj_close == 45000.00
    assert price.volume == 25000000000
    assert price.change == 1250.00
    assert price.change_percent == 2.85
    assert price.vwap == 44500.00
