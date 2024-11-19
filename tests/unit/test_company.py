from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from fmp_data.company.models import (
    CompanyExecutive,
    CompanyProfile,
    CompanySearchResult,
    CompanySymbol,
    ExchangeSymbol,
)


class TestCompanyProfile:
    """Tests for CompanyProfile model and related client functionality"""

    @pytest.fixture
    def profile_data(self):
        """Mock company profile data matching actual API response"""
        return {
            "symbol": "AAPL",
            "price": 225,
            "beta": 1.24,
            "volAvg": 47719342,
            "mktCap": 3401055000000,
            "lastDiv": 0.99,
            "range": "164.08-237.49",
            "changes": -3.22,
            "companyName": "Apple Inc.",
            "currency": "USD",
            "cik": "0000320193",
            "isin": "US0378331005",
            "cusip": "037833100",
            "exchange": "NASDAQ Global Select",
            "exchangeShortName": "NASDAQ",
            "industry": "Consumer Electronics",
            "website": "https://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, "
            "personal computers, "
            "tablets, wearables, and accessories worldwide. The company "
            "offers iPhone, "
            "a line of smartphones; Mac, a line of personal computers; iPad, "
            "a line of "
            "multi-purpose tablets; and wearables, home, "
            "and accessories comprising AirPods, "
            "Apple TV, Apple Watch, Beats products, and HomePod. "
            "It also provides AppleCare "
            "support and cloud services; and operates various platforms, including the "
            "App Store that allow customers to discover and download "
            "applications and digital "
            "content, such as books, music, video, games, and podcasts.",
            "ceo": "Mr. Timothy D. Cook",
            "sector": "Technology",
            "country": "US",
            "fullTimeEmployees": "164000",
            "phone": "408 996 1010",
            "address": "One Apple Park Way",
            "city": "Cupertino",
            "state": "CA",
            "zip": "95014",
            "dcfDiff": 76.28377,
            "dcf": 148.71622529446276,
            "image": "https://images.financialmodelingprep.com/symbol/AAPL.png",
            "ipoDate": "1980-12-12",
            "defaultImage": False,
            "isEtf": False,
            "isActivelyTrading": True,
            "isAdr": False,
            "isFund": False,
        }

    def test_model_validation_complete(self, profile_data):
        """Test CompanyProfile model with all fields"""
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.symbol == "AAPL"
        assert profile.company_name == "Apple Inc."
        assert profile.price == 225
        assert profile.beta == 1.24
        assert profile.vol_avg == 47719342
        assert profile.mkt_cap == 3401055000000
        assert profile.last_div == 0.99
        assert str(profile.website).rstrip("/") == "https://www.apple.com"
        assert profile.ceo == "Mr. Timothy D. Cook"
        assert profile.exchange == "NASDAQ Global Select"
        assert profile.exchange_short_name == "NASDAQ"
        assert profile.phone == "408 996 1010"
        assert profile.full_time_employees == "164000"
        assert profile.dcf == 148.71622529446276
        assert profile.dcf_diff == 76.28377
        assert (
            str(profile.image).rstrip("/")
            == "https://images.financialmodelingprep.com/symbol/AAPL.png"
        )
        assert isinstance(profile.ipo_date, datetime)
        assert profile.ipo_date.year == 1980
        assert not profile.is_etf
        assert profile.is_actively_trading
        assert not profile.is_adr
        assert not profile.is_fund

    def test_model_validation_invalid_website(self, profile_data):
        """Test CompanyProfile model with invalid website URL"""
        profile_data["website"] = "not-a-url"
        with pytest.raises(ValidationError):
            CompanyProfile.model_validate(profile_data)

    @patch("httpx.Client.request")
    def test_get_company_profile(
        self, mock_request, fmp_client, mock_response, profile_data
    ):
        """Test getting company profile through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[profile_data]
        )

        profile = fmp_client.company.get_profile("AAPL")
        assert isinstance(profile, CompanyProfile)
        assert profile.symbol == "AAPL"
        assert profile.company_name == "Apple Inc."
        assert profile.ceo == "Mr. Timothy D. Cook"


class TestCompanyExecutive:
    """Tests for CompanyExecutive model and related client functionality"""

    @pytest.fixture
    def executive_data(self):
        """Mock company executive data"""
        return {
            "title": "Chief Executive Officer",
            "name": "Tim Cook",
            "pay": 3000000,
            "currencyPay": "USD",
            "gender": "M",
            "yearBorn": 1960,
            "titleSince": "2011-08-24",
        }

    def test_model_validation_complete(self, executive_data):
        """Test CompanyExecutive model with all fields"""
        executive = CompanyExecutive.model_validate(executive_data)
        assert executive.name == "Tim Cook"
        assert executive.title == "Chief Executive Officer"
        assert executive.pay == 3000000
        assert executive.currency_pay == "USD"
        assert executive.year_born == 1960
        assert isinstance(executive.title_since, datetime)
        assert executive.title_since.year == 2011

    def test_model_validation_minimal(self):
        """Test CompanyExecutive model with minimal required fields"""
        data = {
            "title": "CEO",
            "name": "John Doe",
        }
        executive = CompanyExecutive.model_validate(data)
        assert executive.name == "John Doe"
        assert executive.title == "CEO"
        assert executive.pay is None
        assert executive.year_born is None
        assert executive.title_since is None

    @patch("httpx.Client.request")
    def test_get_company_executives(
        self, mock_request, fmp_client, mock_response, executive_data
    ):
        """Test getting company executives through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[executive_data]
        )

        executives = fmp_client.company.get_executives("AAPL")
        assert len(executives) == 1
        executive = executives[0]
        assert isinstance(executive, CompanyExecutive)
        assert executive.name == "Tim Cook"
        assert executive.title == "Chief Executive Officer"
        assert executive.pay == 3000000


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

        results = fmp_client.company.search("Apple", limit=1)
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


class TestCompanySymbol:
    """Tests for CompanySymbol model"""

    @pytest.fixture
    def symbol_data(self):
        """Mock company symbol data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "exchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
            "type": "stock",
        }

    def test_model_validation_complete(self, symbol_data):
        """Test CompanySymbol model with all fields"""
        symbol = CompanySymbol.model_validate(symbol_data)
        assert symbol.symbol == "AAPL"
        assert symbol.name == "Apple Inc."
        assert symbol.price == 150.25
        assert symbol.exchange == "NASDAQ"
        assert symbol.exchange_short_name == "NASDAQ"
        assert symbol.type == "stock"

    def test_model_validation_minimal(self):
        """Test CompanySymbol model with minimal required fields"""
        data = {"symbol": "AAPL"}
        symbol = CompanySymbol.model_validate(data)
        assert symbol.symbol == "AAPL"
        assert symbol.name is None
        assert symbol.price is None
        assert symbol.exchange is None
        assert symbol.type is None
