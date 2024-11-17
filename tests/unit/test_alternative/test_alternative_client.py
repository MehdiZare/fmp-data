# tests/test_alternative/test_alternative_client.py
from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.alternative.models import (
    CommodityQuote,
    CryptoHistoricalPrice,
    CryptoQuote,
    ForexQuote,
)
from fmp_data.exceptions import FMPError


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
    assert quote.symbol == "EUR/USD"
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
