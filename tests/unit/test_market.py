from datetime import date, datetime
from unittest.mock import patch

import pytest

from fmp_data.market.models import (
    CompanySearchResult,
    ExchangeSymbol,
    IPODisclosure,
    IPOProspectus,
    MarketHours,
)


@pytest.fixture
def mock_market_hours_data():
    """Mock market hours data (new API format)"""
    return [
        {
            "exchange": "NYSE",
            "name": "New York Stock Exchange",
            "openingHour": "09:30 AM -04:00",
            "closingHour": "04:00 PM -04:00",
            "timezone": "America/New_York",
            "isMarketOpen": False,
        }
    ]


def test_get_market_hours_default_exchange(fmp_client, mock_market_hours_data):
    """Test getting market hours with default exchange (NYSE)"""
    # Create MarketHours object from mock data
    market_hours_obj = MarketHours(**mock_market_hours_data[0])

    # Mock the client.request method to return list of MarketHours objects
    with patch.object(
        fmp_client.market.client, "request", return_value=[market_hours_obj]
    ):
        hours = fmp_client.market.get_market_hours()

    # Ensure the response is of the correct type
    assert isinstance(hours, MarketHours)

    # Validate fields in the response (new structure)
    assert hours.exchange == "NYSE"
    assert hours.name == "New York Stock Exchange"
    assert hours.opening_hour == "09:30 AM -04:00"
    assert hours.closing_hour == "04:00 PM -04:00"
    assert hours.timezone == "America/New_York"
    assert hours.is_market_open is False


def test_get_market_hours_specific_exchange(fmp_client):
    """Test getting market hours for a specific exchange"""
    nasdaq_data = {
        "exchange": "NASDAQ",
        "name": "NASDAQ",
        "openingHour": "09:30 AM -04:00",
        "closingHour": "04:00 PM -04:00",
        "timezone": "America/New_York",
        "isMarketOpen": True,
    }

    # Create MarketHours object
    nasdaq_hours_obj = MarketHours(**nasdaq_data)

    # Mock the client.request method
    with patch.object(
        fmp_client.market.client, "request", return_value=[nasdaq_hours_obj]
    ):
        hours = fmp_client.market.get_market_hours("NASDAQ")

    # Ensure the response is of the correct type
    assert isinstance(hours, MarketHours)
    assert hours.exchange == "NASDAQ"
    assert hours.name == "NASDAQ"
    assert hours.is_market_open is True


def test_get_market_hours_empty_response(fmp_client):
    """Test getting market hours with empty response"""
    # Mock the client.request to return empty list directly
    with patch.object(fmp_client.market.client, "request", return_value=[]):
        with pytest.raises(ValueError, match="No market hours data returned from API"):
            fmp_client.market.get_market_hours()


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

        results = fmp_client.market.search_company("Apple", limit=1)
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


class TestDirectoryEndpoints:
    """Tests for directory endpoints"""

    @patch("httpx.Client.request")
    def test_get_available_exchanges(self, mock_request, fmp_client, mock_response):
        """Test getting available exchanges"""
        exchange_data = [
            {
                "symbol": "NYSE",
                "name": "New York Stock Exchange",
                "price": None,
                "changesPercentage": None,
                "change": None,
                "dayLow": None,
                "dayHigh": None,
                "yearHigh": None,
                "yearLow": None,
                "marketCap": None,
                "priceAvg50": None,
                "priceAvg200": None,
                "exchange": "NYSE",
                "volume": None,
                "avgVolume": None,
                "open": None,
                "previousClose": None,
                "eps": None,
                "pe": None,
                "sharesOutstanding": None,
            }
        ]
        mock_request.return_value = mock_response(
            status_code=200, json_data=exchange_data
        )

        exchanges = fmp_client.market.get_available_exchanges()
        assert len(exchanges) == 1
        assert isinstance(exchanges[0], ExchangeSymbol)
        assert exchanges[0].symbol == "NYSE"
        assert exchanges[0].name == "New York Stock Exchange"

    @patch("httpx.Client.request")
    def test_get_available_sectors(self, mock_request, fmp_client, mock_response):
        """Test getting available sectors"""
        sectors_data = ["Technology", "Healthcare", "Financial Services", "Energy"]
        mock_request.return_value = mock_response(
            status_code=200, json_data=sectors_data
        )

        sectors = fmp_client.market.get_available_sectors()
        assert len(sectors) == 4
        assert all(isinstance(sector, str) for sector in sectors)
        assert "Technology" in sectors
        assert "Healthcare" in sectors

    @patch("httpx.Client.request")
    def test_get_available_industries(self, mock_request, fmp_client, mock_response):
        """Test getting available industries"""
        industries_data = [
            "Software",
            "Biotechnology",
            "Banks",
            "Oil & Gas E&P",
            "Semiconductors",
        ]
        mock_request.return_value = mock_response(
            status_code=200, json_data=industries_data
        )

        industries = fmp_client.market.get_available_industries()
        assert len(industries) == 5
        assert all(isinstance(industry, str) for industry in industries)
        assert "Software" in industries
        assert "Biotechnology" in industries

    @patch("httpx.Client.request")
    def test_get_available_countries(self, mock_request, fmp_client, mock_response):
        """Test getting available countries"""
        countries_data = ["US", "CA", "GB", "DE", "JP", "CN"]
        mock_request.return_value = mock_response(
            status_code=200, json_data=countries_data
        )

        countries = fmp_client.market.get_available_countries()
        assert len(countries) == 6
        assert all(isinstance(country, str) for country in countries)
        assert "US" in countries
        assert "JP" in countries


class TestIPOEndpoints:
    """Tests for IPO disclosure and prospectus endpoints"""

    @pytest.fixture
    def mock_ipo_disclosure_data(self):
        """Mock IPO disclosure data"""
        return {
            "symbol": "RDDT",
            "companyName": "Reddit Inc",
            "ipoDate": "2024-03-21T00:00:00",
            "exchange": "NYSE",
            "priceRange": "$31.00 - $34.00",
            "sharesOffered": 22000000,
            "disclosureUrl": "https://www.sec.gov/Archives/edgar/data/123456/...",
            "filingDate": "2024-02-22T00:00:00",
            "status": "Priced",
            "underwriters": "Morgan Stanley, Goldman Sachs",
        }

    @pytest.fixture
    def mock_ipo_prospectus_data(self):
        """Mock IPO prospectus data"""
        return {
            "symbol": "RDDT",
            "companyName": "Reddit Inc",
            "ipoDate": "2024-03-21T00:00:00",
            "exchange": "NYSE",
            "prospectusUrl": "https://www.sec.gov/Archives/edgar/data/123456/...",
            "filingDate": "2024-02-22T00:00:00",
            "status": "Effective",
            "sharesOffered": 22000000,
            "offerPrice": 34.00,
            "grossProceeds": 748000000.0,
        }

    def test_ipo_disclosure_model_validation(self, mock_ipo_disclosure_data):
        """Test IPODisclosure model validation"""
        disclosure = IPODisclosure.model_validate(mock_ipo_disclosure_data)
        assert disclosure.symbol == "RDDT"
        assert disclosure.company_name == "Reddit Inc"
        assert isinstance(disclosure.ipo_date, datetime)
        assert disclosure.exchange == "NYSE"
        assert disclosure.price_range == "$31.00 - $34.00"
        assert disclosure.shares_offered == 22000000
        assert disclosure.disclosure_url is not None
        assert disclosure.status == "Priced"
        assert disclosure.underwriters == "Morgan Stanley, Goldman Sachs"

    def test_ipo_prospectus_model_validation(self, mock_ipo_prospectus_data):
        """Test IPOProspectus model validation"""
        prospectus = IPOProspectus.model_validate(mock_ipo_prospectus_data)
        assert prospectus.symbol == "RDDT"
        assert prospectus.company_name == "Reddit Inc"
        assert isinstance(prospectus.ipo_date, datetime)
        assert prospectus.exchange == "NYSE"
        assert prospectus.prospectus_url is not None
        assert prospectus.shares_offered == 22000000
        assert prospectus.offer_price == 34.00
        assert prospectus.gross_proceeds == 748000000.0

    @patch("httpx.Client.request")
    def test_get_ipo_disclosure(
        self, mock_request, fmp_client, mock_response, mock_ipo_disclosure_data
    ):
        """Test getting IPO disclosure documents"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_ipo_disclosure_data]
        )

        disclosures = fmp_client.market.get_ipo_disclosure(
            from_date=date(2024, 1, 1), to_date=date(2024, 12, 31), limit=10
        )
        assert len(disclosures) == 1
        assert isinstance(disclosures[0], IPODisclosure)
        assert disclosures[0].symbol == "RDDT"
        assert disclosures[0].company_name == "Reddit Inc"

        # Verify request parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["from"] == date(2024, 1, 1)
        assert call_args[1]["params"]["to"] == date(2024, 12, 31)
        assert call_args[1]["params"]["limit"] == 10

    @patch("httpx.Client.request")
    def test_get_ipo_prospectus(
        self, mock_request, fmp_client, mock_response, mock_ipo_prospectus_data
    ):
        """Test getting IPO prospectus documents"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mock_ipo_prospectus_data]
        )

        prospectuses = fmp_client.market.get_ipo_prospectus(limit=5)
        assert len(prospectuses) == 1
        assert isinstance(prospectuses[0], IPOProspectus)
        assert prospectuses[0].symbol == "RDDT"
        assert prospectuses[0].offer_price == 34.00
        assert prospectuses[0].gross_proceeds == 748000000.0

        # Verify request was made with only limit parameter
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["limit"] == 5
        assert "from" not in call_args[1]["params"]
        assert "to" not in call_args[1]["params"]
