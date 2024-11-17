import pytest


@pytest.fixture
def mock_market_hours_data():
    """Mock market hours data"""
    return {
        "stockExchangeName": "NYSE",
        "stockMarketHours": "09:30AM - 04:00PM",
        "stockMarketHolidays": ["2024-01-01", "2024-01-15"],
        "isTheStockMarketOpen": True,
        "isTheEuronextMarketOpen": False,
        "isTheForexMarketOpen": True,
        "isTheCryptoMarketOpen": True,
    }


@pytest.fixture
def mock_quote_data():
    """Mock quote data"""
    return {
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
        "priceAvg50": 145.50,
        "priceAvg200": 140.00,
        "volume": 82034567,
        "avgVolume": 75000000,
        "open": 149.00,
        "previousClose": 148.00,
        "eps": 5.61,
        "pe": 26.75,
        "timestamp": "2024-01-05T16:00:00",
    }


@pytest.fixture
def mock_historical_data():
    """Mock historical price data"""
    return [
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
    ]
