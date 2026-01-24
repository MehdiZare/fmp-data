from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from fmp_data.company import CompanyClient
from fmp_data.company.models import (
    AnalystEstimate,
    CompanyExecutive,
    CompanyProfile,
    ExecutiveCompensationBenchmark,
    HistoricalData,
    HistoricalPrice,
    MergerAcquisition,
    PriceTarget,
    PriceTargetSummary,
    Quote,
)
from fmp_data.intelligence.models import DividendEvent, EarningEvent, StockSplitEvent
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
        "lastMonthCount": 10,
        "lastMonthAvgPriceTarget": 190.0,
        "lastQuarterCount": 30,
        "lastQuarterAvgPriceTarget": 185.0,
        "lastYearCount": 100,
        "lastYearAvgPriceTarget": 180.0,
        "allTimeCount": 300,
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
        # Use a URL with protocol but invalid hostname (no TLD) to trigger validation
        profile_data["website"] = "https://invalid"
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.website is None

    def test_model_validation_invalid_website_ipv6(self, profile_data):
        """Test CompanyProfile model with malformed URL that breaks urlparse"""
        profile_data["website"] = "ttps://www.tradretfs.com["
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.website is None

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

    @patch("httpx.Client.request")
    def test_get_company_profile_by_cik(self, _mock_request, fmp_client, profile_data):
        """Test getting company profile by CIK through client"""
        # Set up the mock to return the actual response object
        mock_client = fmp_client.client
        mock_client.request.return_value = [CompanyProfile(**profile_data)]

        profile = fmp_client.get_profile_cik("0000320193")
        assert isinstance(profile, CompanyProfile)
        assert profile.symbol == "AAPL"
        assert profile.cik == "0000320193"

    @patch("httpx.Client.request")
    def test_get_company_profile_by_cik_not_found(self, _mock_request, fmp_client):
        """Test getting company profile by CIK when not found"""
        from fmp_data.exceptions import FMPNotFound

        # Set up the mock to return empty list
        mock_client = fmp_client.client
        mock_client.request.return_value = []

        with pytest.raises(FMPNotFound, match="9999999999"):
            fmp_client.get_profile_cik("9999999999")


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
        # Set up mock to return list of HistoricalPrice objects (not HistoricalData)
        mock_client.request.return_value = [
            HistoricalPrice(
                date=datetime(2024, 1, 5, 16, 0),
                open=149.00,
                high=151.00,
                low=148.50,
                close=150.25,
                price=150.25,
                adjClose=150.25,
                volume=82034567,
                change=2.25,
                changePercent=1.5,
                vwap=149.92,
            )
        ]

        data = fmp_client.get_historical_prices(
            "AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 1, 5)
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
    result = fmp_client.get_analyst_estimates(
        symbol="AAPL", period="annual", page=0, limit=10
    )
    assert isinstance(result, list)
    assert isinstance(result[0], AnalystEstimate)
    assert result[0].symbol == "AAPL"
    assert result[0].estimated_revenue_avg == 52500000.0

    call_args = mock_client.request.call_args
    assert call_args[1]["symbol"] == "AAPL"
    assert call_args[1]["period"] == "annual"
    assert call_args[1]["page"] == 0
    assert call_args[1]["limit"] == 10


class TestMergersAcquisitions:
    """Tests for Mergers & Acquisitions endpoints"""

    @pytest.fixture
    def merger_data(self):
        """Mock merger acquisition data"""
        return {
            "companyName": "Apple Inc.",
            "targetedCompanyName": "Beats Electronics",
            "dealDate": "2014-05-28",
            "acceptanceTime": "2014-05-28T09:00:00",
            "url": "https://sec.gov/filing/example",
        }

    def test_model_validation(self, merger_data):
        """Test MergerAcquisition model validation"""
        merger = MergerAcquisition.model_validate(merger_data)
        assert merger.companyName == "Apple Inc."
        assert merger.targetedCompanyName == "Beats Electronics"
        assert merger.dealDate == "2014-05-28"
        assert merger.acceptanceTime == "2014-05-28T09:00:00"
        assert merger.url == "https://sec.gov/filing/example"

    def test_model_validation_minimal(self):
        """Test MergerAcquisition model with minimal data"""
        data = {}
        merger = MergerAcquisition.model_validate(data)
        assert merger.companyName is None
        assert merger.targetedCompanyName is None
        assert merger.dealDate is None

    def test_get_mergers_acquisitions_latest(
        self, fmp_client, mock_client, merger_data
    ):
        """Test fetching latest M&A transactions"""
        mock_client.request.return_value = [MergerAcquisition(**merger_data)]
        result = fmp_client.get_mergers_acquisitions_latest(page=0, limit=10)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], MergerAcquisition)
        assert result[0].companyName == "Apple Inc."

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["page"] == 0
        assert call_args[1]["limit"] == 10

    def test_get_mergers_acquisitions_search(
        self, fmp_client, mock_client, merger_data
    ):
        """Test searching M&A transactions by company name"""
        mock_client.request.return_value = [MergerAcquisition(**merger_data)]
        result = fmp_client.get_mergers_acquisitions_search(
            name="Apple", page=0, limit=20
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], MergerAcquisition)
        assert result[0].targetedCompanyName == "Beats Electronics"

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["name"] == "Apple"
        assert call_args[1]["page"] == 0
        assert call_args[1]["limit"] == 20


class TestExecutiveCompensationBenchmark:
    """Tests for Executive Compensation Benchmark endpoint"""

    @pytest.fixture
    def benchmark_data(self):
        """Mock executive compensation benchmark data"""
        return {
            "year": 2023,
            "industryTitle": "Technology",
            "marketCapitalization": "Large Cap (>10B)",
            "averageTotalCompensation": 15000000.0,
            "averageCashCompensation": 3000000.0,
            "averageEquityCompensation": 10000000.0,
            "averageOtherCompensation": 2000000.0,
        }

    def test_model_validation(self, benchmark_data):
        """Test ExecutiveCompensationBenchmark model validation"""
        benchmark = ExecutiveCompensationBenchmark.model_validate(benchmark_data)
        assert benchmark.year == 2023
        assert benchmark.industryTitle == "Technology"
        assert benchmark.marketCapitalization == "Large Cap (>10B)"
        assert benchmark.averageTotalCompensation == 15000000.0
        assert benchmark.averageCashCompensation == 3000000.0
        assert benchmark.averageEquityCompensation == 10000000.0
        assert benchmark.averageOtherCompensation == 2000000.0

    def test_get_executive_compensation_benchmark(
        self, fmp_client, mock_client, benchmark_data
    ):
        """Test fetching executive compensation benchmark data"""
        mock_client.request.return_value = [
            ExecutiveCompensationBenchmark(**benchmark_data)
        ]
        result = fmp_client.get_executive_compensation_benchmark(year=2023)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ExecutiveCompensationBenchmark)
        assert result[0].year == 2023
        assert result[0].industryTitle == "Technology"

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["year"] == 2023


class TestCompanyClientAsync:
    """Tests for async methods in CompanyClient"""

    @pytest.fixture
    def profile_data(self):
        """Mock company profile data"""
        return {
            "symbol": "AAPL",
            "price": 150.0,
            "beta": 1.2,
            "volAvg": 82034567,
            "mktCap": 2500000000000,
            "lastDiv": 0.88,
            "range": "120-180",
            "changes": 2.5,
            "companyName": "Apple Inc.",
            "currency": "USD",
            "cik": "0000320193",
            "isin": "US0378331005",
            "cusip": "037833100",
            "exchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
            "industry": "Consumer Electronics",
            "website": "https://apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones.",
            "ceo": "Tim Cook",
            "sector": "Technology",
            "country": "US",
            "fullTimeEmployees": "164000",
            "phone": "408-996-1010",
            "address": "One Apple Park Way",
            "city": "Cupertino",
            "state": "CA",
            "zip": "95014",
            "dcfDiff": 10.5,
            "dcf": 160.5,
            "image": "https://example.com/AAPL.png",
            "ipoDate": "1980-12-12",
            "defaultImage": False,
            "isEtf": False,
            "isActivelyTrading": True,
            "isAdr": False,
            "isFund": False,
        }

    @pytest.mark.asyncio
    async def test_async_company_get_profile(self, mock_client, profile_data):
        """Test AsyncCompanyClient get_profile method"""
        from unittest.mock import AsyncMock

        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async = AsyncMock(
            return_value=[CompanyProfile(**profile_data)]
        )

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_profile("AAPL")

        assert isinstance(result, CompanyProfile)
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        mock_client.request_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_company_get_profile_cik(self, mock_client, profile_data):
        """Test AsyncCompanyClient get_profile_cik method"""
        from unittest.mock import AsyncMock

        from fmp_data.company.async_client import AsyncCompanyClient

        mock_client.request_async = AsyncMock(
            return_value=[CompanyProfile(**profile_data)]
        )

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_profile_cik("0000320193")

        assert isinstance(result, CompanyProfile)
        assert result.symbol == "AAPL"
        assert result.cik == "0000320193"
        mock_client.request_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_company_get_profile_cik_not_found(self, mock_client):
        """Test AsyncCompanyClient get_profile_cik method when not found"""
        from unittest.mock import AsyncMock

        from fmp_data.company.async_client import AsyncCompanyClient
        from fmp_data.exceptions import FMPNotFound

        mock_client.request_async = AsyncMock(return_value=[])

        async_client = AsyncCompanyClient(mock_client)

        with pytest.raises(FMPNotFound, match="9999999999"):
            await async_client.get_profile_cik("9999999999")

    @pytest.mark.asyncio
    async def test_async_company_get_quote(self, mock_client):
        """Test AsyncCompanyClient get_quote method"""
        from unittest.mock import AsyncMock

        from fmp_data.company.async_client import AsyncCompanyClient

        quote_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.0,
            "changePercentage": 1.5,
            "change": 2.25,
            "dayLow": 148.0,
            "dayHigh": 151.0,
            "yearHigh": 180.0,
            "yearLow": 120.0,
            "marketCap": 2500000000000,
            "priceAvg50": 145.0,
            "priceAvg200": 140.0,
            "volume": 82034567,
            "avgVolume": 80000000,
            "exchange": "NASDAQ",
            "open": 149.0,
            "previousClose": 147.75,
            "eps": 6.05,
            "pe": 24.79,
            "earningsAnnouncement": "2024-01-25T16:30:00.000+0000",
            "sharesOutstanding": 16700000000,
            "timestamp": 1706198400,
        }

        mock_client.request_async = AsyncMock(return_value=[Quote(**quote_data)])

        async_client = AsyncCompanyClient(mock_client)
        result = await async_client.get_quote("AAPL")

        assert isinstance(result, Quote)
        assert result.symbol == "AAPL"
        assert result.price == 150.0


class TestHistoricalPriceVariants:
    """Tests for different historical price endpoint variants"""

    @pytest.fixture
    def historical_price_data(self):
        """Mock historical price data"""
        return {
            "date": "2024-01-05T00:00:00",
            "open": 149.00,
            "high": 151.00,
            "low": 148.50,
            "close": 150.25,
            "volume": 82034567,
            "change": 2.25,
            "changePercent": 1.5,
            "vwap": 149.92,
        }

    def test_get_historical_prices_passes_dates(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test that get_historical_prices passes correct date parameter names."""
        mock_client.request.return_value = [HistoricalPrice(**historical_price_data)]

        result = fmp_client.get_historical_prices(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 1, 5)
        )

        assert isinstance(result, HistoricalData)

        # Verify the request was made with start_date and end_date keys
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        # These should be start_date and end_date, not from_ and to
        assert call_args[1]["start_date"] == "2024-01-01"
        assert call_args[1]["end_date"] == "2024-01-05"
        # Ensure the old incorrect keys are not used
        assert "from_" not in call_args[1]
        assert "to" not in call_args[1]

    def test_get_historical_prices_light(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test fetching lightweight historical price data"""
        mock_client.request.return_value = [HistoricalPrice(**historical_price_data)]

        result = fmp_client.get_historical_prices_light(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 1, 5)
        )

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        assert result.historical[0].open == 149.00
        assert result.historical[0].close == 150.25

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["start_date"] == "2024-01-01"
        assert call_args[1]["end_date"] == "2024-01-05"

    def test_get_historical_prices_non_split_adjusted(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test fetching non-split-adjusted historical price data"""
        mock_client.request.return_value = [HistoricalPrice(**historical_price_data)]

        result = fmp_client.get_historical_prices_non_split_adjusted(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 1, 5)
        )

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        assert result.historical[0].open == 149.00
        assert result.historical[0].volume == 82034567

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["start_date"] == "2024-01-01"
        assert call_args[1]["end_date"] == "2024-01-05"

    def test_get_historical_prices_dividend_adjusted(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test fetching dividend-adjusted historical price data"""
        mock_client.request.return_value = [HistoricalPrice(**historical_price_data)]

        result = fmp_client.get_historical_prices_dividend_adjusted(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 1, 5)
        )

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        assert result.historical[0].high == 151.00
        assert result.historical[0].low == 148.50

        # Verify the request was made with correct parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["start_date"] == "2024-01-01"
        assert call_args[1]["end_date"] == "2024-01-05"

    def test_historical_price_variants_without_dates(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test historical price variants without date parameters"""
        mock_client.request.return_value = [HistoricalPrice(**historical_price_data)]

        # Test light variant without dates
        result = fmp_client.get_historical_prices_light(symbol="AAPL")
        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"

        # Verify no date parameters were passed
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert "start_date" not in call_args[1]
        assert "end_date" not in call_args[1]

    def test_historical_price_single_result(
        self, fmp_client, mock_client, historical_price_data
    ):
        """Test handling single price result (not a list)"""
        # Return single object instead of list
        mock_client.request.return_value = HistoricalPrice(**historical_price_data)

        result = fmp_client.get_historical_prices_light(symbol="AAPL")

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert len(result.historical) == 1
        assert result.historical[0].close == 150.25


class TestCompanyCalendarEndpoints:
    """Test company calendar endpoints (dividends, earnings, splits)"""

    @pytest.fixture
    def dividend_data(self):
        """Mock dividend event data"""
        return {
            "symbol": "AAPL",
            "date": "2024-02-15",
            "label": "February 15, 24",
            "adjDividend": 0.24,
            "dividend": 0.24,
            "recordDate": "2024-02-12",
            "paymentDate": "2024-02-15",
            "declarationDate": "2024-02-01",
        }

    @pytest.fixture
    def earnings_data(self):
        """Mock earnings event data"""
        return {
            "date": "2024-01-25",
            "symbol": "AAPL",
            "eps": 2.18,
            "epsEstimated": 2.10,
            "time": "amc",
            "revenue": 119575000000,
            "revenueEstimated": 117970000000,
            "fiscalDateEnding": "2023-12-30",
            "updatedFromDate": "2024-01-24",
        }

    @pytest.fixture
    def split_data(self):
        """Mock stock split event data"""
        return {
            "symbol": "AAPL",
            "date": "2020-08-31",
            "label": "August 31, 20",
            "numerator": 4.0,
            "denominator": 1.0,
        }

    def test_get_dividends(self, fmp_client, mock_client, dividend_data):
        """Test fetching dividend history"""
        mock_client.request.return_value = [DividendEvent(**dividend_data)]

        result = fmp_client.get_dividends(
            symbol="AAPL", from_date=date(2024, 1, 1), to_date=date(2024, 12, 31)
        )

        assert len(result) == 1
        assert isinstance(result[0], DividendEvent)
        assert result[0].symbol == "AAPL"
        assert result[0].dividend == 0.24
        assert result[0].adj_dividend == 0.24
        assert result[0].ex_dividend_date.strftime("%Y-%m-%d") == "2024-02-15"
        assert result[0].payment_date.strftime("%Y-%m-%d") == "2024-02-15"

        # Verify request parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["from_date"] == "2024-01-01"
        assert call_args[1]["to_date"] == "2024-12-31"

    def test_get_dividends_without_dates(self, fmp_client, mock_client, dividend_data):
        """Test fetching dividend history without date filters"""
        mock_client.request.return_value = [DividendEvent(**dividend_data)]

        result = fmp_client.get_dividends(symbol="AAPL")

        assert len(result) == 1
        assert isinstance(result[0], DividendEvent)

        # Verify no date parameters were passed
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert "from_date" not in call_args[1]
        assert "to_date" not in call_args[1]

    def test_get_dividends_with_limit(self, fmp_client, mock_client, dividend_data):
        """Test fetching dividend history with limit"""
        mock_client.request.return_value = [DividendEvent(**dividend_data)]

        result = fmp_client.get_dividends(symbol="AAPL", limit=5)

        assert len(result) == 1
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["limit"] == 5

    def test_get_earnings(self, fmp_client, mock_client, earnings_data):
        """Test fetching earnings history"""
        mock_client.request.return_value = [EarningEvent(**earnings_data)]

        result = fmp_client.get_earnings(symbol="AAPL", limit=10)

        assert len(result) == 1
        assert isinstance(result[0], EarningEvent)
        assert result[0].symbol == "AAPL"
        assert result[0].eps == 2.18
        assert result[0].eps_estimated == 2.10
        assert result[0].revenue == 119575000000
        assert result[0].revenue_estimated == 117970000000
        assert result[0].time == "amc"

        # Verify request parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["limit"] == 10

    def test_get_earnings_default_limit(self, fmp_client, mock_client, earnings_data):
        """Test fetching earnings with default limit"""
        mock_client.request.return_value = [EarningEvent(**earnings_data)]

        result = fmp_client.get_earnings(symbol="AAPL")

        assert len(result) == 1

        # Verify default limit is used
        call_args = mock_client.request.call_args
        assert call_args[1]["limit"] == 20

    def test_get_stock_splits(self, fmp_client, mock_client, split_data):
        """Test fetching stock split history"""
        mock_client.request.return_value = [StockSplitEvent(**split_data)]

        result = fmp_client.get_stock_splits(
            symbol="AAPL", from_date=date(2020, 1, 1), to_date=date(2021, 12, 31)
        )

        assert len(result) == 1
        assert isinstance(result[0], StockSplitEvent)
        assert result[0].symbol == "AAPL"
        assert result[0].numerator == 4.0
        assert result[0].denominator == 1.0
        assert result[0].split_event_date.strftime("%Y-%m-%d") == "2020-08-31"
        assert result[0].label == "August 31, 20"

        # Verify request parameters
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["from_date"] == "2020-01-01"
        assert call_args[1]["to_date"] == "2021-12-31"

    def test_get_stock_splits_without_dates(self, fmp_client, mock_client, split_data):
        """Test fetching stock splits without date filters"""
        mock_client.request.return_value = [StockSplitEvent(**split_data)]

        result = fmp_client.get_stock_splits(symbol="AAPL")

        assert len(result) == 1
        assert isinstance(result[0], StockSplitEvent)

        # Verify no date parameters were passed
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert "from_date" not in call_args[1]
        assert "to_date" not in call_args[1]

    def test_get_stock_splits_with_limit(self, fmp_client, mock_client, split_data):
        """Test fetching stock splits with limit"""
        mock_client.request.return_value = [StockSplitEvent(**split_data)]

        result = fmp_client.get_stock_splits(symbol="AAPL", limit=5)

        assert len(result) == 1
        call_args = mock_client.request.call_args
        assert call_args[1]["symbol"] == "AAPL"
        assert call_args[1]["limit"] == 5

    def test_multiple_dividends(self, fmp_client, mock_client):
        """Test handling multiple dividend events"""
        dividend_data_list = [
            {
                "symbol": "AAPL",
                "date": "2024-05-15",
                "label": "May 15, 24",
                "adjDividend": 0.25,
                "dividend": 0.25,
                "recordDate": "2024-05-12",
                "paymentDate": "2024-05-15",
                "declarationDate": "2024-05-01",
            },
            {
                "symbol": "AAPL",
                "date": "2024-02-15",
                "label": "February 15, 24",
                "adjDividend": 0.24,
                "dividend": 0.24,
                "recordDate": "2024-02-12",
                "paymentDate": "2024-02-15",
                "declarationDate": "2024-02-01",
            },
        ]
        mock_client.request.return_value = [
            DividendEvent(**data) for data in dividend_data_list
        ]

        result = fmp_client.get_dividends(symbol="AAPL")

        assert len(result) == 2
        assert all(isinstance(div, DividendEvent) for div in result)
        assert result[0].dividend == 0.25
        assert result[1].dividend == 0.24
