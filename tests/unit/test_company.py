from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from fmp_data.company import CompanyClient
from fmp_data.company.models import (
    AnalystEstimate,
    CompanyExecutive,
    CompanyProfile,
    HistoricalData,
    HistoricalPrice,
    PriceTarget,
    PriceTargetSummary,
)
from fmp_data.models import CompanySymbol


# Fixtures for mock client and fmp_client
@pytest.fixture
def mock_client():
    """Fixture to mock the API client."""
    return Mock()


@pytest.fixture
def fmp_client(mock_client):
    """Fixture to create an instance of CompanyClient,
    with a mocked client."""
    return CompanyClient(client=mock_client)


# Fixtures for mock data
@pytest.fixture
def price_target_data():
    return [
        {
            "symbol": "AAPL",
            "publishedDate": "2024-01-01T12:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Apple price target increased",
            "analystName": "John Doe",
            "priceTarget": 200.0,
            "adjPriceTarget": 198.0,
            "priceWhenPosted": 150.0,
            "newsPublisher": "Example News",
            "newsBaseURL": "example.com",
            "analystCompany": "Big Bank",
        }
    ]


@pytest.fixture
def price_target_summary_data():
    return {
        "symbol": "AAPL",
        "lastMonth": 10,
        "lastMonthAvgPriceTarget": 190.0,
        "lastQuarter": 30,
        "lastQuarterAvgPriceTarget": 185.0,
        "lastYear": 100,
        "lastYearAvgPriceTarget": 180.0,
        "allTime": 300,
        "allTimeAvgPriceTarget": 175.0,
        "publishers": '["Example News", "Tech Daily"]',
    }


@pytest.fixture
def analyst_estimates_data():
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-01T12:00:00",
            "estimatedRevenueLow": 50000000.0,
            "estimatedRevenueHigh": 55000000.0,
            "estimatedRevenueAvg": 52500000.0,
            "estimatedEbitdaLow": 12000000.0,
            "estimatedEbitdaHigh": 13000000.0,
            "estimatedEbitdaAvg": 12500000.0,
            "estimatedEbitLow": 10000000.0,
            "estimatedEbitHigh": 11000000.0,
            "estimatedEbitAvg": 10500000.0,
            "estimatedNetIncomeLow": 8000000.0,
            "estimatedNetIncomeHigh": 9000000.0,
            "estimatedNetIncomeAvg": 8500000.0,
            "estimatedSgaExpenseLow": 2000000.0,
            "estimatedSgaExpenseHigh": 2500000.0,
            "estimatedSgaExpenseAvg": 2250000.0,
            "estimatedEpsLow": 3.5,
            "estimatedEpsHigh": 4.0,
            "estimatedEpsAvg": 3.75,
            "numberAnalystEstimatedRevenue": 10,
            "numberAnalystsEstimatedEps": 8,
        }
    ]


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
        # Set up the mock to return the actual response object
        mock_client = fmp_client.client
        mock_client.request.return_value = [CompanyProfile(**profile_data)]

        profile = fmp_client.get_profile("AAPL")
        assert isinstance(profile, CompanyProfile)
        assert profile.symbol == "AAPL"


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
        # Set up mock to return list of executives
        mock_client = fmp_client.client
        mock_client.request.return_value = [CompanyExecutive(**executive_data)]

        executives = fmp_client.get_executives("AAPL")
        assert len(executives) == 1
        assert isinstance(executives[0], CompanyExecutive)


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

    def test_get_historical_prices(self, mock_client, fmp_client, mock_historical_data):
        """Test getting historical prices"""
        # Set up mock to return properly structured historical data
        mock_client.request.return_value = HistoricalData(
            symbol="AAPL",
            historical=[
                HistoricalPrice(
                    date=datetime(2024, 1, 5, 16, 0),
                    open=149.00,
                    high=151.00,
                    low=148.50,
                    close=150.25,
                    adj_close=150.25,
                    volume=82034567,
                    unadjusted_volume=82034567,
                    change=2.25,
                    change_percent=1.5,
                    vwap=149.92,
                    label="January 05",
                    change_over_time=0.015,
                )
            ],
        )

        data = fmp_client.get_historical_prices(
            "AAPL", from_date="2024-01-01", to_date="2024-01-05"
        )

        # Verify results
        assert isinstance(data, HistoricalData)
        assert data.symbol == "AAPL"
        assert len(data.historical) == 1

        # Check the first price entry
        price = data.historical[0]
        assert isinstance(price, HistoricalPrice)
        assert price.open == 149.00
        assert price.close == 150.25
        assert price.volume == 82034567


def test_get_price_target(fmp_client, mock_client, price_target_data):
    """Test fetching price targets"""
    mock_client.request.return_value = [PriceTarget(**price_target_data[0])]
    result = fmp_client.get_price_target(symbol="AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], PriceTarget)
    assert result[0].symbol == "AAPL"


def test_get_price_target_summary(fmp_client, mock_client, price_target_summary_data):
    """Test fetching price target summary"""
    mock_client.request.return_value = PriceTargetSummary(**price_target_summary_data)
    result = fmp_client.get_price_target_summary(symbol="AAPL")
    assert isinstance(result, PriceTargetSummary)
    assert result.symbol == "AAPL"
    assert result.last_month_avg_price_target == 190.0


def test_get_analyst_estimates(fmp_client, mock_client, analyst_estimates_data):
    """Test fetching analyst estimates"""
    mock_client.request.return_value = [AnalystEstimate(**analyst_estimates_data[0])]
    result = fmp_client.get_analyst_estimates(symbol="AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], AnalystEstimate)
    assert result[0].symbol == "AAPL"
    assert result[0].estimated_revenue_avg == 52500000.0
