from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from fmp_data.alternative.models import (
    CommodityQuote,
    CryptoHistoricalPrice,
    CryptoQuote,
    ForexQuote,
)
from fmp_data.exceptions import FMPError


# Mock Data Fixtures
@pytest.fixture
def mock_crypto_quote():
    """Mock cryptocurrency quote data"""
    return {
        "symbol": "BTC/USD",
        "name": "Bitcoin",
        "price": 45000.00,
        "change": 1250.00,
        "changesPercentage": 2.85,
        "timestamp": "2024-01-05T16:00:00",
        "marketCap": 880000000000,
        "volume24h": 25000000000,
        "circulatingSupply": 19500000,
    }


@pytest.fixture
def mock_forex_quote():
    """Mock forex quote data"""
    return {
        "symbol": "EUR/USD",
        "price": 1.0950,
        "change": 0.0025,
        "changesPercentage": 0.23,
        "timestamp": "2024-01-05T16:00:00",
        "bid": 1.0948,
        "ask": 1.0952,
        "spread": 0.0004,
    }


@pytest.fixture
def mock_commodity_quote():
    """Mock commodity quote data"""
    return {
        "symbol": "GC",
        "price": 2050.50,
        "change": 15.30,
        "changesPercentage": 0.75,
        "timestamp": "2024-01-05T16:00:00",
        "name": "Gold Futures",
        "yearHigh": 2150.00,
        "yearLow": 1800.00,
        "volume": 245000,
    }


@pytest.fixture
def mock_crypto_historical():
    """Mock cryptocurrency historical price data"""
    return [
        {
            "date": "2024-01-05",
            "open": 43750.00,
            "high": 45200.00,
            "low": 43500.00,
            "close": 45000.00,
            "volume": 25000000000,
            "adjClose": 45000.00,
        }
    ]


# Model Tests
def test_crypto_quote_model(mock_crypto_quote):
    """Test CryptoQuote model validation"""
    mock_crypto_quote["timestamp"] = (
        "2024-01-05T16:00:00"  # Ensure proper timestamp format
    )
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


# Client Tests
@patch("httpx.Client.request")
def test_get_crypto_quote(mock_request, fmp_client, mock_response, mock_crypto_quote):
    """Test getting cryptocurrency quote"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_crypto_quote]
    )

    quote = fmp_client.alternative.get_crypto_quote("BTC/USD")
    assert isinstance(quote, CryptoQuote)
    assert quote.symbol == "BTC/USD"
    assert quote.price == 45000.00
    assert quote.market_cap == 880000000000


@patch("httpx.Client.request")
def test_get_forex_quote(mock_request, fmp_client, mock_response, mock_forex_quote):
    """Test getting forex quote"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_forex_quote]
    )

    quote = fmp_client.alternative.get_forex_quote("EUR/USD")
    assert isinstance(quote, ForexQuote)
    assert float(quote.price) == 1.0950
    assert float(quote.spread) == 0.0004


@patch("httpx.Client.request")
def test_get_commodity_quote(
    mock_request, fmp_client, mock_response, mock_commodity_quote
):
    """Test getting commodity quote"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_commodity_quote]
    )

    quote = fmp_client.alternative.get_commodity_quote("GC")
    assert isinstance(quote, CommodityQuote)
    assert quote.symbol == "GC"
    assert quote.price == 2050.50
    assert quote.year_high == 2150.00


@patch("httpx.Client.request")
def test_get_crypto_historical(
    mock_request, fmp_client, mock_response, mock_crypto_historical
):
    """Test getting cryptocurrency historical prices"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_crypto_historical
    )

    prices = fmp_client.alternative.get_crypto_historical(
        "BTC/USD", start_date=date(2024, 1, 1), end_date=date(2024, 1, 5)
    )
    assert isinstance(prices, list)
    assert len(prices) == 1
    assert isinstance(prices[0], CryptoHistoricalPrice)
    assert prices[0].close == 45000.00


@patch("httpx.Client.request")
def test_invalid_symbol(mock_request, fmp_client, mock_response):
    """Test handling of invalid symbol"""
    error_response = mock_response(
        status_code=404, json_data={"message": "Symbol not found"}, raise_error=True
    )
    mock_request.return_value = error_response

    with pytest.raises(FMPError) as exc_info:
        fmp_client.alternative.get_crypto_quote("INVALID")
    assert "Symbol not found" in str(exc_info.value)
