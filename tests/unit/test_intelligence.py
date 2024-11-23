from datetime import datetime
from unittest.mock import patch

import pytest

from fmp_data.market.models import (
    HistoricalData,
    HistoricalPrice,
    MarketHours,
    StockMarketHours,
)


@pytest.fixture
def mock_market_hours_data():
    """Mock market hours data"""
    return {
        "stockExchangeName": "NYSE",
        "stockMarketHours": {"openingHour": "09:30AM", "closingHour": "04:00PM"},
        "stockMarketHolidays": [
            {"year": 2024, "holidays": [{"name": "New Year", "date": "2024-01-01"}]}
        ],
        "isTheStockMarketOpen": True,
        "isTheEuronextMarketOpen": False,
        "isTheForexMarketOpen": True,
        "isTheCryptoMarketOpen": True,
    }


@pytest.fixture
def mock_historical_data():
    """Mock historical data"""
    return {
        "symbol": "AAPL",
        "historical": [
            {
                "date": "2024-01-05T16:00:00",
                "open": 149.00,
                "high": 151.00,
                "low": 148.50,
                "close": 150.25,
                "adjClose": 150.25,
                "volume": 82034567,
                "unadjustedVolume": 82034567,
                "change": 2.25,
                "changePercent": 1.5,
                "vwap": 149.92,
                "label": "January 05",
                "changeOverTime": 0.015,
            }
        ],
    }


@patch("httpx.Client.request")
def test_get_market_hours(
    mock_request, fmp_client, mock_response, mock_market_hours_data
):
    """Test getting market hours"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_market_hours_data
    )

    hours = fmp_client.market.get_market_hours()

    # Ensure the response is of the correct type
    assert isinstance(hours, MarketHours)

    # Validate fields in the response
    assert hours.stockExchangeName == "NYSE"
    assert hours.isTheStockMarketOpen is True
    assert isinstance(hours.stockMarketHours, StockMarketHours)
    assert hours.stockMarketHours.openingHour == "09:30AM"
    assert hours.stockMarketHours.closingHour == "04:00PM"
    assert isinstance(hours.stockMarketHolidays, list)
    assert len(hours.stockMarketHolidays) > 0
    holiday = hours.stockMarketHolidays[0]
    assert holiday.year == 2024
    assert holiday.holidays == {"New Year": "2024-01-01"}


@patch("httpx.Client.request")
def test_get_historical_prices(
    mock_request, fmp_client, mock_response, mock_historical_data
):
    """Test getting historical prices"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_historical_data
    )

    data = fmp_client.market.get_historical_prices(
        "AAPL", from_date="2024-01-01", to_date="2024-01-05"
    )

    # Ensure the response is of the correct type
    assert isinstance(data, HistoricalData)
    assert data.symbol == "AAPL"

    # Validate the historical prices
    assert isinstance(data.historical, list)
    assert len(data.historical) == 1
    price = data.historical[0]
    assert isinstance(price, HistoricalPrice)
    assert price.date == datetime(2024, 1, 5, 16, 0)
    assert price.open == 149.00
    assert price.close == 150.25
    assert price.volume == 82034567
