# tests/unit/test_index.py
"""Tests for the index module endpoints"""

from unittest.mock import patch

import pytest

from fmp_data.index.models import HistoricalIndexConstituent, IndexConstituent


class TestIndexModels:
    """Tests for index model validation"""

    @pytest.fixture
    def constituent_data(self):
        """Mock index constituent data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "subSector": "Consumer Electronics",
            "headquarter": "Cupertino, California",
            "dateFirstAdded": "1982-11-30",
            "cik": "0000320193",
            "founded": "1976",
        }

    @pytest.fixture
    def historical_constituent_data(self):
        """Mock historical constituent change data"""
        return {
            "date": "2024-01-15",
            "symbol": "NEW",
            "addedSecurity": "New Company Inc.",
            "removedSecurity": "Old Company Inc.",
            "removedTicker": "OLD",
            "addedTicker": "NEW",
            "reason": "Market capitalization",
        }

    def test_index_constituent_model(self, constituent_data):
        """Test IndexConstituent model validation"""
        constituent = IndexConstituent.model_validate(constituent_data)
        assert constituent.symbol == "AAPL"
        assert constituent.name == "Apple Inc."
        assert constituent.sector == "Technology"
        assert constituent.sub_sector == "Consumer Electronics"
        assert constituent.headquarter == "Cupertino, California"
        assert constituent.cik == "0000320193"
        assert constituent.founded == "1976"

    def test_index_constituent_minimal(self):
        """Test IndexConstituent with only required fields"""
        constituent = IndexConstituent.model_validate({"symbol": "TEST"})
        assert constituent.symbol == "TEST"
        assert constituent.name is None
        assert constituent.sector is None

    def test_historical_index_constituent_model(self, historical_constituent_data):
        """Test HistoricalIndexConstituent model validation"""
        change = HistoricalIndexConstituent.model_validate(historical_constituent_data)
        assert change.symbol == "NEW"
        assert change.added_security == "New Company Inc."
        assert change.removed_security == "Old Company Inc."
        assert change.removed_ticker == "OLD"
        assert change.added_ticker == "NEW"
        assert change.reason == "Market capitalization"

    def test_historical_index_constituent_minimal(self):
        """Test HistoricalIndexConstituent with minimal data"""
        change = HistoricalIndexConstituent.model_validate({"date": "2024-01-15"})
        assert change.date is not None
        assert change.added_security is None
        assert change.removed_security is None


class TestIndexClient:
    """Tests for IndexClient methods"""

    @pytest.fixture
    def constituent_data(self):
        """Mock constituent data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
        }

    @pytest.fixture
    def historical_data(self):
        """Mock historical change data"""
        return {
            "date": "2024-01-15",
            "addedSecurity": "New Company",
            "removedSecurity": "Old Company",
        }

    @patch("httpx.Client.request")
    def test_get_sp500_constituents(
        self, mock_request, fmp_client, mock_response, constituent_data
    ):
        """Test fetching S&P 500 constituents"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[constituent_data]
        )
        result = fmp_client.index.get_sp500_constituents()
        assert len(result) == 1
        assert isinstance(result[0], IndexConstituent)
        assert result[0].symbol == "AAPL"
        assert result[0].sector == "Technology"

    @patch("httpx.Client.request")
    def test_get_nasdaq_constituents(
        self, mock_request, fmp_client, mock_response, constituent_data
    ):
        """Test fetching NASDAQ constituents"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[constituent_data]
        )
        result = fmp_client.index.get_nasdaq_constituents()
        assert len(result) == 1
        assert isinstance(result[0], IndexConstituent)

    @patch("httpx.Client.request")
    def test_get_dowjones_constituents(
        self, mock_request, fmp_client, mock_response, constituent_data
    ):
        """Test fetching Dow Jones constituents"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[constituent_data]
        )
        result = fmp_client.index.get_dowjones_constituents()
        assert len(result) == 1
        assert isinstance(result[0], IndexConstituent)

    @patch("httpx.Client.request")
    def test_get_historical_sp500(
        self, mock_request, fmp_client, mock_response, historical_data
    ):
        """Test fetching historical S&P 500 changes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[historical_data]
        )
        result = fmp_client.index.get_historical_sp500()
        assert len(result) == 1
        assert isinstance(result[0], HistoricalIndexConstituent)
        assert result[0].added_security == "New Company"
        assert result[0].removed_security == "Old Company"

    @patch("httpx.Client.request")
    def test_get_historical_nasdaq(
        self, mock_request, fmp_client, mock_response, historical_data
    ):
        """Test fetching historical NASDAQ changes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[historical_data]
        )
        result = fmp_client.index.get_historical_nasdaq()
        assert len(result) == 1
        assert isinstance(result[0], HistoricalIndexConstituent)

    @patch("httpx.Client.request")
    def test_get_historical_dowjones(
        self, mock_request, fmp_client, mock_response, historical_data
    ):
        """Test fetching historical Dow Jones changes"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[historical_data]
        )
        result = fmp_client.index.get_historical_dowjones()
        assert len(result) == 1
        assert isinstance(result[0], HistoricalIndexConstituent)

    @patch("httpx.Client.request")
    def test_get_multiple_constituents(self, mock_request, fmp_client, mock_response):
        """Test fetching multiple constituents"""
        data = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
        ]
        mock_request.return_value = mock_response(status_code=200, json_data=data)
        result = fmp_client.index.get_sp500_constituents()
        assert len(result) == 3
        symbols = [c.symbol for c in result]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "GOOGL" in symbols
