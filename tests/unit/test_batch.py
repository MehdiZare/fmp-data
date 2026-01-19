# tests/unit/test_batch.py
"""Tests for the batch module endpoints"""

from unittest.mock import patch

import pytest

from fmp_data.batch.models import (
    AftermarketQuote,
    AftermarketTrade,
    BatchMarketCap,
    BatchQuote,
    BatchQuoteShort,
)


class TestBatchModels:
    """Tests for batch model validation"""

    @pytest.fixture
    def batch_quote_data(self):
        """Mock batch quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.0,
            "dayHigh": 152.0,
            "yearHigh": 180.0,
            "yearLow": 120.0,
            "marketCap": 2500000000000,
            "priceAvg50": 155.0,
            "priceAvg200": 145.0,
            "exchange": "NASDAQ",
            "volume": 50000000,
            "avgVolume": 80000000,
            "open": 149.0,
            "previousClose": 148.0,
            "eps": 6.05,
            "pe": 24.8,
            "earningsAnnouncement": "2024-02-01T16:30:00.000+0000",
            "sharesOutstanding": 16000000000,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def batch_quote_short_data(self):
        """Mock short batch quote data"""
        return {
            "symbol": "AAPL",
            "price": 150.25,
            "volume": 50000000,
        }

    @pytest.fixture
    def aftermarket_trade_data(self):
        """Mock aftermarket trade data"""
        return {
            "symbol": "AAPL",
            "price": 151.00,
            "size": 100,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def aftermarket_quote_data(self):
        """Mock aftermarket quote data"""
        return {
            "symbol": "AAPL",
            "ask": 151.50,
            "bid": 151.00,
            "asize": 500,
            "bsize": 400,
            "timestamp": 1704067200,
        }

    @pytest.fixture
    def batch_market_cap_data(self):
        """Mock batch market cap data"""
        return {
            "symbol": "AAPL",
            "date": "2024-01-01",
            "marketCap": 2500000000000,
        }

    def test_batch_quote_model(self, batch_quote_data):
        """Test BatchQuote model validation"""
        quote = BatchQuote.model_validate(batch_quote_data)
        assert quote.symbol == "AAPL"
        assert quote.name == "Apple Inc."
        assert quote.price == 150.25
        assert quote.changes_percentage == 1.5
        assert quote.change == 2.25
        assert quote.day_low == 148.0
        assert quote.day_high == 152.0
        assert quote.market_cap == 2500000000000
        assert quote.exchange == "NASDAQ"
        assert quote.volume == 50000000

    def test_batch_quote_model_minimal(self):
        """Test BatchQuote with only required field"""
        quote = BatchQuote.model_validate({"symbol": "TEST"})
        assert quote.symbol == "TEST"
        assert quote.name is None
        assert quote.price is None

    def test_batch_quote_short_model(self, batch_quote_short_data):
        """Test BatchQuoteShort model validation"""
        quote = BatchQuoteShort.model_validate(batch_quote_short_data)
        assert quote.symbol == "AAPL"
        assert quote.price == 150.25
        assert quote.volume == 50000000

    def test_aftermarket_trade_model(self, aftermarket_trade_data):
        """Test AftermarketTrade model validation"""
        trade = AftermarketTrade.model_validate(aftermarket_trade_data)
        assert trade.symbol == "AAPL"
        assert trade.price == 151.00
        assert trade.size == 100
        assert trade.timestamp == 1704067200

    def test_aftermarket_quote_model(self, aftermarket_quote_data):
        """Test AftermarketQuote model validation"""
        quote = AftermarketQuote.model_validate(aftermarket_quote_data)
        assert quote.symbol == "AAPL"
        assert quote.ask == 151.50
        assert quote.bid == 151.00
        assert quote.ask_size == 500
        assert quote.bid_size == 400

    def test_batch_market_cap_model(self, batch_market_cap_data):
        """Test BatchMarketCap model validation"""
        cap = BatchMarketCap.model_validate(batch_market_cap_data)
        assert cap.symbol == "AAPL"
        assert cap.market_cap == 2500000000000


class TestBatchClient:
    """Tests for BatchClient methods"""

    @pytest.fixture
    def batch_quote_data(self):
        """Mock batch quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "volume": 50000000,
        }

    @patch("httpx.Client.request")
    def test_get_quotes(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching batch quotes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data]
        )
        result = fmp_client.batch.get_quotes(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchQuote)
        assert result[0].symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_get_quotes_multiple_symbols(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching batch quotes for multiple symbols"""
        msft_data = {**batch_quote_data, "symbol": "MSFT", "name": "Microsoft"}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data, msft_data]
        )
        result = fmp_client.batch.get_quotes(["AAPL", "MSFT"])
        assert len(result) == 2
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"

    @patch("httpx.Client.request")
    def test_get_quotes_short(
        self, mock_request, fmp_client, mock_response
    ):
        """Test fetching short batch quotes"""
        short_data = {"symbol": "AAPL", "price": 150.25, "volume": 50000000}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[short_data]
        )
        result = fmp_client.batch.get_quotes_short(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchQuoteShort)
        assert result[0].price == 150.25

    @patch("httpx.Client.request")
    def test_get_aftermarket_trades(
        self, mock_request, fmp_client, mock_response
    ):
        """Test fetching aftermarket trades"""
        trade_data = {"symbol": "AAPL", "price": 151.00, "size": 100, "timestamp": 123}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[trade_data]
        )
        result = fmp_client.batch.get_aftermarket_trades(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], AftermarketTrade)
        assert result[0].price == 151.00

    @patch("httpx.Client.request")
    def test_get_aftermarket_quotes(
        self, mock_request, fmp_client, mock_response
    ):
        """Test fetching aftermarket quotes"""
        quote_data = {
            "symbol": "AAPL",
            "ask": 151.50,
            "bid": 151.00,
            "asize": 500,
            "bsize": 400,
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=[quote_data]
        )
        result = fmp_client.batch.get_aftermarket_quotes(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], AftermarketQuote)
        assert result[0].ask == 151.50

    @patch("httpx.Client.request")
    def test_get_exchange_quotes(
        self, mock_request, fmp_client, mock_response, batch_quote_data
    ):
        """Test fetching exchange quotes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[batch_quote_data]
        )
        result = fmp_client.batch.get_exchange_quotes("NASDAQ")
        assert len(result) == 1
        assert isinstance(result[0], BatchQuote)

    @patch("httpx.Client.request")
    def test_get_market_caps(self, mock_request, fmp_client, mock_response):
        """Test fetching batch market caps"""
        cap_data = {"symbol": "AAPL", "date": "2024-01-01", "marketCap": 2500000000000}
        mock_request.return_value = mock_response(
            status_code=200, json_data=[cap_data]
        )
        result = fmp_client.batch.get_market_caps(["AAPL"])
        assert len(result) == 1
        assert isinstance(result[0], BatchMarketCap)
        assert result[0].market_cap == 2500000000000
