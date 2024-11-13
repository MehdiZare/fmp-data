# tests/test_market/test_market_client.py
from unittest.mock import patch

import pytest

from fmp_data.exceptions import FMPError
from fmp_data.market.models import HistoricalPrice, MarketHours, Quote


@patch("httpx.Client.request")
def test_get_quote(mock_request, fmp_client, mock_response, mock_quote_data):
    """Test getting stock quote"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_quote_data]
    )

    quote = fmp_client.market.get_quote("AAPL")
    assert isinstance(quote, Quote)
    assert quote.symbol == "AAPL"
    assert quote.price == 150.25
    assert quote.market_cap == 2500000000000


@patch("httpx.Client.request")
def test_get_historical_prices(
    mock_request, fmp_client, mock_response, mock_historical_data
):
    """Test getting historical prices"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_historical_data
    )

    prices = fmp_client.market.get_historical_prices(
        "AAPL", from_date="2024-01-01", to_date="2024-01-05"
    )
    assert isinstance(prices, list)
    assert len(prices) == 1
    assert isinstance(prices[0], HistoricalPrice)
    assert prices[0].close == 150.25


@patch("httpx.Client.request")
def test_get_market_hours(
    mock_request, fmp_client, mock_response, mock_market_hours_data
):
    """Test getting market hours"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_market_hours_data
    )

    hours = fmp_client.market.get_market_hours()
    assert isinstance(hours, MarketHours)
    assert hours.stockExchangeName == "NYSE"
    assert hours.isTheStockMarketOpen is True


@patch("httpx.Client.request")
def test_error_handling(mock_request, fmp_client, mock_response):
    """Test error handling in market client"""
    error_response = mock_response(
        status_code=404, json_data={"message": "Symbol not found"}, raise_error=True
    )
    mock_request.return_value = error_response

    with pytest.raises(FMPError) as exc_info:
        fmp_client.market.get_quote("INVALID")
    assert "Symbol not found" in str(exc_info.value)
