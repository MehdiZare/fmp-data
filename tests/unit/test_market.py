from unittest.mock import patch

import pytest

from fmp_data.market.models import (
    CompanySearchResult,
    ExchangeSymbol,
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


class TestCompanySearch:
    """Tests for CompanySearchResult model and related client functionality"""

    @pytest.fixture
    def search_result_data(self):
        """Mock company search result data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "currency": "USD",
            "stockExchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
        }

    def test_model_validation_complete(self, search_result_data):
        """Test CompanySearchResult model with all fields"""
        result = CompanySearchResult.model_validate(search_result_data)
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.currency == "USD"
        assert result.stock_exchange == "NASDAQ"
        assert result.exchange_short_name == "NASDAQ"

    def test_model_validation_minimal(self):
        """Test CompanySearchResult model with minimal required fields"""
        data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
        }
        result = CompanySearchResult.model_validate(data)
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.currency is None
        assert result.stock_exchange is None

    @patch("httpx.Client.request")
    def test_search_companies(
        self, mock_request, fmp_client, mock_response, search_result_data
    ):
        """Test company search through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_result_data]
        )

        results = fmp_client.market.search("Apple", limit=1)
        assert len(results) == 1
        result = results[0]
        assert isinstance(result, CompanySearchResult)
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."


class TestExchangeSymbol:
    """Tests for ExchangeSymbol model"""

    @pytest.fixture
    def exchange_symbol_data(self):
        """Mock exchange symbol data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "changesPercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.50,
            "dayHigh": 151.00,
            "yearHigh": 182.94,
            "yearLow": 124.17,
            "marketCap": 2500000000000,
            "priceAvg50": 145.80,
            "priceAvg200": 140.50,
            "exchange": "NASDAQ",
            "volume": 82034567,
            "avgVolume": 75000000,
            "open": 149.00,
            "previousClose": 148.00,
            "eps": 6.05,
            "pe": 24.83,
            "sharesOutstanding": 16500000000,
        }

    def test_model_validation_complete(self, exchange_symbol_data):
        """Test ExchangeSymbol model with all fields"""
        symbol = ExchangeSymbol.model_validate(exchange_symbol_data)
        assert symbol.symbol == "AAPL"
        assert symbol.name == "Apple Inc."
        assert symbol.price == 150.25
        assert symbol.change_percentage == 1.5
        assert symbol.market_cap == 2500000000000
        assert symbol.eps == 6.05
        assert symbol.pe == 24.83

    def test_model_validation_minimal(self):
        """Test ExchangeSymbol model with minimal fields"""
        data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
        }
        symbol = ExchangeSymbol.model_validate(data)
        assert symbol.symbol == "AAPL"
        assert symbol.name == "Apple Inc."
        assert symbol.price is None
        assert symbol.market_cap is None

    def test_model_validation_optional_fields(self):
        """Test ExchangeSymbol model with optional fields set to None"""
        test_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": None,
            "marketCap": None,
            "eps": None,
            "pe": None,
        }

        symbol = ExchangeSymbol.model_validate(test_data)
        assert symbol.symbol == "AAPL"
        assert all(
            getattr(symbol, field) is None
            for field in ["price", "market_cap", "eps", "pe"]
        )

    def test_model_validation_with_defaults(self):
        """Test ExchangeSymbol model with fields defaulting to None"""
        symbol = ExchangeSymbol.model_validate({"symbol": "AAPL", "name": "Apple Inc."})
        assert all(
            getattr(symbol, field) is None
            for field in [
                "price",
                "change_percentage",
                "day_low",
                "day_high",
                "market_cap",
                "volume",
                "eps",
                "pe",
            ]
        )
