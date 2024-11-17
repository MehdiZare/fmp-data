import pytest


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
