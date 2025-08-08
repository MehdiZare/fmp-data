"""Additional tests for alternative client to improve coverage"""

from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.alternative.models import (
    CommodityQuote,
    CryptoQuote,
    ForexQuote,
)


class TestAlternativeClientCoverage:
    """Tests to improve coverage for AlternativeClient"""

    @pytest.fixture
    def crypto_quote_data(self):
        """Mock crypto quote data"""
        return {
            "symbol": "BTCUSD",
            "name": "Bitcoin USD",
            "price": 45000.50,
            "changesPercentage": 2.5,
            "change": 1100.25,
            "dayLow": 44000.00,
            "dayHigh": 46000.00,
            "yearHigh": 69000.00,
            "yearLow": 30000.00,
            "marketCap": 880000000000,
            "priceAvg50": 43000.00,
            "priceAvg200": 40000.00,
            "volume": 25000000000,
            "avgVolume": 20000000000,
            "exchange": "CRYPTO",
            "open": 44500.00,
            "previousClose": 43900.25,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def forex_quote_data(self):
        """Mock forex quote data"""
        return {
            "symbol": "EURUSD",
            "name": "EUR/USD",
            "price": 1.0950,
            "changesPercentage": 0.15,
            "change": 0.0016,
            "dayLow": 1.0920,
            "dayHigh": 1.0980,
            "yearHigh": 1.1200,
            "yearLow": 1.0500,
            "priceAvg50": 1.0900,
            "priceAvg200": 1.0850,
            "exchange": "FOREX",
            "open": 1.0934,
            "previousClose": 1.0934,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def commodity_quote_data(self):
        """Mock commodity quote data"""
        return {
            "symbol": "GCUSD",
            "name": "Gold",
            "price": 2050.30,
            "changesPercentage": 0.8,
            "change": 16.20,
            "dayLow": 2035.00,
            "dayHigh": 2065.00,
            "yearHigh": 2150.00,
            "yearLow": 1850.00,
            "priceAvg50": 2030.00,
            "priceAvg200": 1980.00,
            "exchange": "COMEX",
            "open": 2034.10,
            "previousClose": 2034.10,
            "timestamp": 1704067200,
        }

    @patch("httpx.Client.request")
    def test_get_crypto_quote(
        self, mock_request, fmp_client, mock_response, crypto_quote_data
    ):
        """Test fetching crypto quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[crypto_quote_data]
        )

        result = fmp_client.alternative.get_crypto_quote("BTCUSD")

        assert len(result) == 1
        quote = result[0]
        assert isinstance(quote, CryptoQuote)
        assert quote.symbol == "BTCUSD"
        assert quote.price == 45000.50
        assert quote.market_cap == 880000000000

    @patch("httpx.Client.request")
    def test_get_forex_quote(
        self, mock_request, fmp_client, mock_response, forex_quote_data
    ):
        """Test fetching forex quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[forex_quote_data]
        )

        result = fmp_client.alternative.get_forex_quote("EURUSD")

        assert len(result) == 1
        quote = result[0]
        assert isinstance(quote, ForexQuote)
        assert quote.symbol == "EURUSD"
        assert quote.price == 1.0950

    @patch("httpx.Client.request")
    def test_get_commodity_quote(
        self, mock_request, fmp_client, mock_response, commodity_quote_data
    ):
        """Test fetching commodity quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[commodity_quote_data]
        )

        result = fmp_client.alternative.get_commodity_quote("GCUSD")

        assert len(result) == 1
        quote = result[0]
        assert isinstance(quote, CommodityQuote)
        assert quote.symbol == "GCUSD"
        assert quote.price == 2050.30

    @patch("httpx.Client.request")
    def test_get_crypto_historical(self, mock_request, fmp_client, mock_response):
        """Test fetching crypto historical data"""
        historical_data = {
            "date": "2024-01-01",
            "open": 44000.00,
            "high": 45500.00,
            "low": 43500.00,
            "close": 45000.00,
            "volume": 28000000000,
            "unadjustedVolume": 28000000000,
            "change": 1000.00,
            "changePercent": 2.27,
            "vwap": 44500.00,
            "label": "January 01, 24",
            "changeOverTime": 0.0227,
        }

        mock_request.return_value = mock_response(
            status_code=200,
            json_data={"symbol": "BTCUSD", "historical": [historical_data]},
        )

        result = fmp_client.alternative.get_crypto_historical(
            symbol="BTCUSD", start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        assert result["symbol"] == "BTCUSD"
        assert len(result["historical"]) == 1
        assert result["historical"][0]["close"] == 45000.00

    @patch("httpx.Client.request")
    def test_get_forex_historical(self, mock_request, fmp_client, mock_response):
        """Test fetching forex historical data"""
        historical_data = {
            "date": "2024-01-01",
            "open": 1.0920,
            "high": 1.0980,
            "low": 1.0910,
            "close": 1.0950,
            "adjClose": 1.0950,
            "volume": 0,
            "unadjustedVolume": 0,
            "change": 0.0030,
            "changePercent": 0.27,
            "vwap": 1.0945,
            "label": "January 01, 24",
            "changeOverTime": 0.0027,
        }

        mock_request.return_value = mock_response(
            status_code=200,
            json_data={"symbol": "EURUSD", "historical": [historical_data]},
        )

        result = fmp_client.alternative.get_forex_historical(
            symbol="EURUSD", start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        assert result["symbol"] == "EURUSD"
        assert len(result["historical"]) == 1
        assert result["historical"][0]["close"] == 1.0950

    @patch("httpx.Client.request")
    def test_get_commodity_historical(self, mock_request, fmp_client, mock_response):
        """Test fetching commodity historical data"""
        historical_data = {
            "date": "2024-01-01",
            "open": 2030.00,
            "high": 2065.00,
            "low": 2025.00,
            "close": 2050.30,
            "adjClose": 2050.30,
            "volume": 150000,
            "unadjustedVolume": 150000,
            "change": 20.30,
            "changePercent": 1.00,
            "vwap": 2045.00,
            "label": "January 01, 24",
            "changeOverTime": 0.01,
        }

        mock_request.return_value = mock_response(
            status_code=200,
            json_data={"symbol": "GCUSD", "historical": [historical_data]},
        )

        result = fmp_client.alternative.get_commodity_historical(
            symbol="GCUSD", start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        assert result["symbol"] == "GCUSD"
        assert len(result["historical"]) == 1
        assert result["historical"][0]["close"] == 2050.30
