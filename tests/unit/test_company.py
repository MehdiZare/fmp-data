from datetime import date, datetime
from typing import Any
from unittest.mock import Mock, patch

from pydantic import ValidationError
import pytest

from fmp_data.base import BaseClient, EndpointGroup
from fmp_data.company import CompanyClient
from fmp_data.company.endpoints import (
    ANALYST_RECOMMENDATIONS,
    COMPANY_OUTLOOK,
    COMPANY_PEERS,
    DELISTED_COMPANIES,
    HISTORICAL_EMPLOYEE_COUNT,
    HISTORICAL_PRICE,
    HISTORICAL_PRICE_DIVIDEND_ADJUSTED,
    HISTORICAL_PRICE_LIGHT,
    HISTORICAL_PRICE_NON_SPLIT_ADJUSTED,
    HISTORICAL_SHARE_FLOAT,
    INCOME_STATEMENT_TTM,
    KEY_EXECUTIVES,
    MERGERS_ACQUISITIONS_LATEST,
    PRICE_TARGET,
    STOCK_SCREENER,
    SYMBOL_CHANGES,
    UPGRADES_DOWNGRADES,
)
from fmp_data.company.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CompanyExecutive,
    CompanyOutlook,
    CompanyPeer,
    CompanyProfile,
    DelistedCompany,
    EmployeeCount,
    ExecutiveCompensationBenchmark,
    HistoricalData,
    HistoricalPrice,
    HistoricalShareFloat,
    IntradayPrice,
    MergerAcquisition,
    PriceTarget,
    PriceTargetSummary,
    Quote,
    SimpleQuote,
    SymbolChange,
    UpgradeDowngrade,
)
from fmp_data.fundamental.models import IncomeStatement
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

    def test_model_validation_float_volume(self, profile_data):
        """Test CompanyProfile handles float averageVolume values (Issue #70).

        The FMP API sometimes returns float values for volume fields
        (e.g., 18459651.1 for XOM), which should be coerced to int.
        """
        profile_data["volAvg"] = 18459651.1
        profile_data["volume"] = 12345678.9
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg == 18459651
        assert profile.volume == 12345678
        assert isinstance(profile.vol_avg, int)
        assert isinstance(profile.volume, int)

    def test_model_validation_int_volume(self, profile_data):
        """Test CompanyProfile handles integer volume values correctly (Issue #70)."""
        profile_data["volAvg"] = 50000000
        profile_data["volume"] = 25000000
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg == 50000000
        assert profile.volume == 25000000
        assert isinstance(profile.vol_avg, int)
        assert isinstance(profile.volume, int)

    def test_model_validation_none_volume(self, profile_data):
        """Test CompanyProfile handles None volume values (Issue #70)."""
        profile_data["volAvg"] = None
        profile_data["volume"] = None
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg is None
        assert profile.volume is None

    def test_model_validation_string_volume(self, profile_data):
        """Test CompanyProfile handles string volume values (Issue #70).

        When API returns numeric strings, Pydantic coerces them to int.
        """
        profile_data["volAvg"] = "50000000"
        profile_data["volume"] = "25000000"
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg == 50000000
        assert profile.volume == 25000000

    def test_model_validation_fractional_string_volume(self, profile_data):
        """Bulk CSV endpoints (e.g. profile-bulk) return volume as a fractional
        STRING such as "475.9"; it must coerce to int instead of failing the
        ``int`` field and silently dropping the whole parsed row (Issue #70)."""
        profile_data["volAvg"] = "7155681.59509"
        profile_data["volume"] = "475.9"
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg == 7155681
        assert profile.volume == 475
        assert isinstance(profile.vol_avg, int)
        assert isinstance(profile.volume, int)

    def test_model_validation_empty_string_volume(self, profile_data):
        """An empty/whitespace volume cell (common in CSV rows) coerces to None,
        not a validation error."""
        profile_data["volAvg"] = ""
        profile_data["volume"] = "   "
        profile = CompanyProfile.model_validate(profile_data)
        assert profile.vol_avg is None
        assert profile.volume is None

    def test_model_validation_non_finite_volume_raises(self, profile_data):
        """Non-finite volume must not raise OverflowError; it surfaces as
        ValidationError so bulk parsers can skip a single row safely."""
        from pydantic import ValidationError

        from fmp_data.company.models import coerce_volume_value

        for bad in ("inf", "-inf", "nan", "NaN", float("inf"), float("nan")):
            # Pass-through (no OverflowError); Pydantic then rejects the value.
            assert coerce_volume_value(bad) is bad
            profile_data["volume"] = bad
            with pytest.raises(ValidationError):
                CompanyProfile.model_validate(profile_data)

    def test_coerce_volume_value_passthrough_edges(self):
        """Cover defensive pass-through arms Codecov flags on the patch.

        - bool is a subclass of int; must not become 0/1
        - non-numeric strings pass through for later ValidationError
        - unknown types fall through unchanged
        """
        from fmp_data.company.models import coerce_volume_value

        assert coerce_volume_value(True) is True
        assert coerce_volume_value(False) is False
        assert coerce_volume_value("not_a_number") == "not_a_number"
        assert coerce_volume_value([1]) == [1]
        assert coerce_volume_value({"v": 1}) == {"v": 1}

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


class TestQuoteModel:
    """Tests for Quote model nullable fields and volume coercion (Issues #82-84)"""

    @pytest.fixture
    def full_quote_data(self):
        """Complete quote data with all fields populated"""
        return {
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
            "exchange": "NASDAQ",
            "open": 149.0,
            "previousClose": 147.75,
            "timestamp": 1706198400,
        }

    def test_quote_with_all_fields(self, full_quote_data):
        """Test Quote parses successfully with all fields populated"""
        quote = Quote.model_validate(full_quote_data)
        assert quote.symbol == "AAPL"
        assert quote.year_high == 180.0
        assert quote.year_low == 120.0
        assert quote.market_cap == 2500000000000
        assert quote.price_avg_50 == 145.0
        assert quote.price_avg_200 == 140.0
        assert quote.open_price == 149.0
        assert quote.previous_close == 147.75
        assert quote.volume == 82034567

    def test_quote_with_null_fields(self, full_quote_data):
        """Test Quote parses successfully when FMP returns null for sparse fields
        (Issues #82, #84)"""
        full_quote_data["yearHigh"] = None
        full_quote_data["yearLow"] = None
        full_quote_data["marketCap"] = None
        full_quote_data["priceAvg50"] = None
        full_quote_data["priceAvg200"] = None
        full_quote_data["volume"] = None
        full_quote_data["open"] = None
        full_quote_data["previousClose"] = None
        quote = Quote.model_validate(full_quote_data)
        assert quote.year_high is None
        assert quote.year_low is None
        assert quote.market_cap is None
        assert quote.price_avg_50 is None
        assert quote.price_avg_200 is None
        assert quote.open_price is None
        assert quote.previous_close is None
        assert quote.volume is None

    def test_quote_with_missing_fields(self):
        """Test Quote parses when optional fields are absent from response"""
        data = {
            "symbol": "DELISTED",
            "name": "Delisted Corp",
            "price": 0.0,
            "changePercentage": 0.0,
            "change": 0.0,
            "dayLow": 0.0,
            "dayHigh": 0.0,
            "volume": 0,
            "exchange": "OTC",
            "timestamp": 1706198400,
        }
        quote = Quote.model_validate(data)
        assert quote.year_high is None
        assert quote.year_low is None
        assert quote.market_cap is None
        assert quote.price_avg_50 is None
        assert quote.price_avg_200 is None
        assert quote.open_price is None
        assert quote.previous_close is None

    def test_quote_float_volume_coerced_to_int(self, full_quote_data):
        """Test Quote coerces float volume to int (Issue #83)"""
        full_quote_data["volume"] = 9549117.83028
        quote = Quote.model_validate(full_quote_data)
        assert quote.volume == 9549117
        assert isinstance(quote.volume, int)

    def test_quote_int_volume_unchanged(self, full_quote_data):
        """Test Quote preserves int volume values"""
        full_quote_data["volume"] = 82034567
        quote = Quote.model_validate(full_quote_data)
        assert quote.volume == 82034567
        assert isinstance(quote.volume, int)

    def test_quote_volume_validator_none(self):
        """Test Quote volume validator handles None input."""
        assert Quote.coerce_volume_to_int(None) is None

    def test_quote_volume_validator_string(self):
        """Test Quote volume validator passes non-numeric values through."""
        assert Quote.coerce_volume_to_int("not_a_number") == "not_a_number"

    def test_quote_datetime_timestamp(self, full_quote_data):
        """Test Quote handles pre-parsed datetime timestamp."""
        full_quote_data["timestamp"] = datetime(2024, 1, 25, 12, 0, 0)
        quote = Quote.model_validate(full_quote_data)
        assert quote.timestamp == datetime(2024, 1, 25, 12, 0, 0)

    def test_quote_datetime_property(self, full_quote_data):
        """Test Quote.quote_datetime property returns timestamp."""
        quote = Quote.model_validate(full_quote_data)
        assert quote.quote_datetime == quote.timestamp


class TestSimpleQuoteModel:
    """Tests for SimpleQuote volume coercion"""

    def test_simple_quote_float_volume(self):
        """Test SimpleQuote coerces float volume to int"""
        data = {"symbol": "AAPL", "price": 150.0, "volume": 1234567.89}
        quote = SimpleQuote.model_validate(data)
        assert quote.volume == 1234567
        assert isinstance(quote.volume, int)

    def test_simple_quote_none_volume(self):
        """Test SimpleQuote accepts null volume from the API."""
        data = {"symbol": "AAPL", "price": 150.0, "volume": None}
        quote = SimpleQuote.model_validate(data)
        assert quote.volume is None

    def test_simple_quote_volume_validator_none(self):
        """Test SimpleQuote volume validator handles None."""
        assert SimpleQuote.coerce_volume_to_int(None) is None


class TestIntradayPriceModel:
    """Tests for intraday price model validation"""

    def test_intraday_price_accepts_float_volume(self):
        """Test intraday prices accept float volume values from the API."""
        data = {
            "date": "2024-01-05T16:00:00",
            "open": 149.00,
            "low": 148.50,
            "high": 151.00,
            "close": 150.25,
            "volume": 28541.004200000316,
        }

        price = IntradayPrice.model_validate(data)

        assert price.volume == pytest.approx(28541.004200000316)
        assert isinstance(price.volume, float)

    def test_intraday_price_normalizes_integer_volume_to_float(self):
        """Test integer intraday volume payloads normalize to float."""
        data = {
            "date": "2024-01-05T16:00:00",
            "open": 149.00,
            "low": 148.50,
            "high": 151.00,
            "close": 150.25,
            "volume": 28541,
        }

        price = IntradayPrice.model_validate(data)

        assert price.volume == pytest.approx(28541.0)
        assert isinstance(price.volume, float)

    def test_simple_quote_volume_validator_string(self):
        """Test SimpleQuote volume validator passes non-numeric values."""
        assert SimpleQuote.coerce_volume_to_int("abc") == "abc"


class TestCompanyProfileMarketCap:
    """Tests for CompanyProfile.market_cap property (Issue #82)"""

    def test_market_cap_property(self):
        """Test CompanyProfile.market_cap returns same as mkt_cap"""
        data = {
            "symbol": "AAPL",
            "mktCap": 2500000000000,
        }
        profile = CompanyProfile.model_validate(data)
        assert profile.market_cap == profile.mkt_cap
        assert profile.market_cap == 2500000000000

    def test_market_cap_property_none(self):
        """Test CompanyProfile.market_cap returns None when mkt_cap is None"""
        data = {"symbol": "AAPL"}
        profile = CompanyProfile.model_validate(data)
        assert profile.market_cap is None
        assert profile.mkt_cap is None


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


def test_get_price_target_is_deprecated(fmp_client, mock_client):
    """``price-target`` 404s, so the request must not be issued.

    The method warns, names the two live aggregate endpoints, and returns an
    empty list rather than spending a rate-limit slot to earn a 404.
    """
    with pytest.warns(DeprecationWarning, match="get_price_target_summary"):
        result = fmp_client.get_price_target(symbol="AAPL")

    assert result == []
    mock_client.request.assert_not_called()


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
        data: dict[str, Any] = {}
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


class TestDelistedCompanies:
    """Tests for the slim delisted-companies list (#229 leftover)."""

    def test_delisted_company_alias_round_trip(self):
        row = DelistedCompany.model_validate(
            {
                "symbol": "2958.HK",
                "companyName": "Vision Values Holdings Limited",
                "exchange": "HKSE",
                "ipoDate": "2026-05-27",
                "delistedDate": "2026-08-17",
            }
        )
        assert row.symbol == "2958.HK"
        assert row.company_name == "Vision Values Holdings Limited"
        assert row.exchange == "HKSE"
        assert row.ipo_date == date(2026, 5, 27)
        assert row.delisted_date == date(2026, 8, 17)
        dumped = row.model_dump(by_alias=True)
        assert dumped["companyName"] == "Vision Values Holdings Limited"
        assert dumped["ipoDate"] == date(2026, 5, 27)
        assert dumped["delistedDate"] == date(2026, 8, 17)

    def test_delisted_endpoint_parses_slim_row_not_profile(self):
        """CI lock: the leftover CompanyProfile binding must not return."""
        slim = {
            "symbol": "2958.HK",
            "companyName": "Vision Values Holdings Limited",
            "exchange": "HKSE",
            "ipoDate": "2026-05-27",
            "delistedDate": "2026-08-17",
        }

        assert DELISTED_COMPANIES.response_model is DelistedCompany
        rows = EndpointGroup._unwrap_list(
            BaseClient._process_response(DELISTED_COMPANIES, [slim]),
            DelistedCompany,
        )

        assert len(rows) == 1
        row = rows[0]
        assert type(row) is DelistedCompany
        assert row.symbol == "2958.HK"
        assert row.company_name == "Vision Values Holdings Limited"
        assert row.ipo_date == date(2026, 5, 27)
        assert row.delisted_date == date(2026, 8, 17)

    def test_delisted_company_optional_fields_may_be_absent(self):
        row = DelistedCompany.model_validate({"symbol": "XYZ"})
        assert row.symbol == "XYZ"
        assert row.company_name is None
        assert row.exchange is None
        assert row.ipo_date is None
        assert row.delisted_date is None

    def test_delisted_company_rejects_empty_symbol(self):
        with pytest.raises(ValidationError):
            DelistedCompany.model_validate({"symbol": ""})
        with pytest.raises(ValidationError):
            DelistedCompany.model_validate({"symbol": "   "})

    def test_delisted_endpoint_applies_page_limit_defaults(self):
        params = DELISTED_COMPANIES.validate_params({})
        assert params["page"] == 0
        assert params["limit"] == 100

    def test_get_delisted_companies(self, fmp_client, mock_client):
        mock_client.request.return_value = [
            DelistedCompany.model_validate(
                {
                    "symbol": "2958.HK",
                    "companyName": "Vision Values Holdings Limited",
                    "exchange": "HKSE",
                    "ipoDate": "2026-05-27",
                    "delistedDate": "2026-08-17",
                }
            )
        ]

        result = fmp_client.get_delisted_companies(page=1, limit=2)

        assert len(result) == 1
        assert isinstance(result[0], DelistedCompany)
        assert result[0].symbol == "2958.HK"
        mock_client.request.assert_called_once_with(DELISTED_COMPANIES, page=1, limit=2)

    def test_get_delisted_companies_defaults(self, fmp_client, mock_client):
        mock_client.request.return_value = []

        fmp_client.get_delisted_companies()

        mock_client.request.assert_called_once_with(
            DELISTED_COMPANIES, page=0, limit=100
        )

    def test_get_delisted_companies_wraps_single_row(self, fmp_client, mock_client):
        """A lone object from request() is still list[DelistedCompany] (#235)."""
        row = DelistedCompany.model_validate(
            {
                "symbol": "2958.HK",
                "companyName": "Vision Values Holdings Limited",
                "exchange": "HKSE",
                "ipoDate": "2026-05-27",
                "delistedDate": "2026-08-17",
            }
        )
        mock_client.request.return_value = row

        result = fmp_client.get_delisted_companies()

        assert result == [row]

    def test_delisted_endpoint_is_parameterized_row_type(self):
        """List endpoints bind T as the row, not list[T] (#235)."""
        assert DELISTED_COMPANIES.response_model is DelistedCompany


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
        payment_date = result[0].payment_date
        assert payment_date is not None
        assert payment_date.strftime("%Y-%m-%d") == "2024-02-15"

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


# Company list methods that go through _unwrap_list. Keep this table in
# lockstep with new list-returning company methods so patch coverage and
# wrap-single stay on the mechanical wrappers.
_COMPANY_LIST_UNWRAP_CASES = [
    ("get_executives", {"symbol": "AAPL"}),
    ("get_employee_count", {"symbol": "AAPL"}),
    ("get_company_notes", {"symbol": "AAPL"}),
    ("get_intraday_prices", {"symbol": "AAPL"}),
    ("get_executive_compensation", {"symbol": "AAPL"}),
    ("get_product_revenue_segmentation", {"symbol": "AAPL"}),
    ("get_geographic_revenue_segmentation", {"symbol": "AAPL"}),
    ("get_symbol_changes", {}),
    ("get_delisted_companies", {}),
    ("get_historical_market_cap", {"symbol": "AAPL"}),
    ("get_analyst_estimates", {"symbol": "AAPL"}),
    ("get_company_peers", {"symbol": "AAPL"}),
    ("get_mergers_acquisitions_latest", {}),
    ("get_mergers_acquisitions_search", {"name": "Apple"}),
    ("get_executive_compensation_benchmark", {"year": 2023}),
    ("get_dividends", {"symbol": "AAPL"}),
    ("get_earnings", {"symbol": "AAPL"}),
    ("get_stock_splits", {"symbol": "AAPL"}),
    ("get_income_statement_ttm", {"symbol": "AAPL"}),
    ("get_balance_sheet_ttm", {"symbol": "AAPL"}),
    ("get_cash_flow_ttm", {"symbol": "AAPL"}),
    ("get_key_metrics_ttm", {"symbol": "AAPL"}),
    ("get_financial_ratios_ttm", {"symbol": "AAPL"}),
    ("get_financial_scores", {"symbol": "AAPL"}),
    ("get_enterprise_values", {"symbol": "AAPL"}),
    ("get_income_statement_growth", {"symbol": "AAPL"}),
    ("get_balance_sheet_growth", {"symbol": "AAPL"}),
    ("get_cash_flow_growth", {"symbol": "AAPL"}),
    ("get_financial_growth", {"symbol": "AAPL"}),
    ("get_income_statement_as_reported", {"symbol": "AAPL"}),
    ("get_balance_sheet_as_reported", {"symbol": "AAPL"}),
    ("get_cash_flow_as_reported", {"symbol": "AAPL"}),
]


class TestCompanyListUnwrap:
    """Mechanical _unwrap_list wrappers on CompanyClient (#235)."""

    @pytest.mark.parametrize("method_name,kwargs", _COMPANY_LIST_UNWRAP_CASES)
    def test_list_methods_wrap_single_and_keep_empty(
        self, fmp_client, mock_client, method_name, kwargs
    ):
        row = object()
        method = getattr(fmp_client, method_name)

        mock_client.request.return_value = row
        assert method(**kwargs) == [row]

        mock_client.request.return_value = []
        assert method(**kwargs) == []
        mock_client.request.assert_called()

    @pytest.mark.parametrize(
        "endpoint,row_type",
        [
            (DELISTED_COMPANIES, DelistedCompany),
            (SYMBOL_CHANGES, SymbolChange),
            (MERGERS_ACQUISITIONS_LATEST, MergerAcquisition),
            (COMPANY_PEERS, CompanyPeer),
            (KEY_EXECUTIVES, CompanyExecutive),
            (INCOME_STATEMENT_TTM, IncomeStatement),
        ],
    )
    def test_list_endpoints_bind_row_type(self, endpoint, row_type):
        """List endpoints bind T as the row, not list[T]."""
        assert endpoint.response_model is row_type


class TestCompanyHistoricalEODUnwrap:
    """Historical EOD helpers unwrap rows then wrap HistoricalData (#242)."""

    @pytest.fixture
    def historical_price_data(self):
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

    @pytest.mark.parametrize(
        "endpoint",
        [
            HISTORICAL_PRICE,
            HISTORICAL_PRICE_LIGHT,
            HISTORICAL_PRICE_NON_SPLIT_ADJUSTED,
            HISTORICAL_PRICE_DIVIDEND_ADJUSTED,
        ],
    )
    def test_historical_price_endpoints_bind_row_type(self, endpoint):
        assert endpoint.response_model is HistoricalPrice

    def test_get_historical_prices_wraps_lone_row(
        self, fmp_client, mock_client, historical_price_data
    ):
        row = HistoricalPrice(**historical_price_data)
        mock_client.request.return_value = row

        result = fmp_client.get_historical_prices("AAPL")

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert result.historical == [row]

    def test_get_historical_prices_empty_list_stays_empty(
        self, fmp_client, mock_client
    ):
        mock_client.request.return_value = []

        result = fmp_client.get_historical_prices("AAPL")

        assert isinstance(result, HistoricalData)
        assert result.symbol == "AAPL"
        assert result.historical == []

    @pytest.mark.parametrize(
        "endpoint,row_type",
        [
            (HISTORICAL_SHARE_FLOAT, HistoricalShareFloat),
            (PRICE_TARGET, PriceTarget),
            (ANALYST_RECOMMENDATIONS, AnalystRecommendation),
            (UPGRADES_DOWNGRADES, UpgradeDowngrade),
            (HISTORICAL_EMPLOYEE_COUNT, EmployeeCount),
            (STOCK_SCREENER, CompanyProfile),
            (COMPANY_OUTLOOK, CompanyOutlook),
        ],
    )
    def test_leftover_company_endpoints_bind_row_type(self, endpoint, row_type):
        """Leftover company declarations bind T as the payload/row type."""
        assert endpoint.response_model is row_type


class TestCompanyLogoUrl:
    """`get_company_logo_url` bypasses `Endpoint.build_url` (#252 FMP-SEC-010).

    The original sweep only covered `build_url` callers, so this raw f-string
    was missed -- and `symbol` reaches it from an LLM through the
    `company_logo_url` MCP tool.
    """

    @staticmethod
    def _client() -> CompanyClient:
        from fmp_data.config import ClientConfig

        config = ClientConfig(
            api_key="test_key",  # pragma: allowlist secret
            base_url="https://example.com",
        )
        return CompanyClient(BaseClient(config))

    def test_normal_symbol_is_unchanged(self) -> None:
        assert (
            self._client().get_company_logo_url("AAPL")
            == "https://example.com/image-stock/AAPL.png"
        )

    def test_dotted_ticker_still_works(self) -> None:
        """`BRK.B` is a real ticker; only `.`/`..` segments are traversal."""
        assert (
            self._client().get_company_logo_url("BRK.B")
            == "https://example.com/image-stock/BRK.B.png"
        )

    @pytest.mark.parametrize(
        "symbol",
        ["../../stable/profile", "a/b", "..", "%2f..%2f", "a\\b"],
    )
    def test_path_escapes_are_rejected(self, symbol: str) -> None:
        with pytest.raises(Exception, match="Invalid path parameter"):
            self._client().get_company_logo_url(symbol)


class TestSegmentationAndReportDefaults:
    """Leftover structure/period defaults apply only as optional_params (#349)."""

    def test_segmentation_structure_and_period_are_optional(self) -> None:
        from fmp_data.company.endpoints import (
            GEOGRAPHIC_REVENUE_SEGMENTATION,
            PRODUCT_REVENUE_SEGMENTATION,
        )
        from fmp_data.exceptions import ValidationError as FMPValidationError
        from fmp_data.schema import STRUCTURE_VALUES

        for endpoint in (
            PRODUCT_REVENUE_SEGMENTATION,
            GEOGRAPHIC_REVENUE_SEGMENTATION,
        ):
            mandatory = {param.name for param in endpoint.mandatory_params}
            optional = {param.name for param in endpoint.optional_params or []}
            assert mandatory == {"symbol"}, endpoint.name
            assert "structure" in optional, endpoint.name
            assert "period" in optional, endpoint.name
            assert "structure" not in mandatory, endpoint.name
            assert "period" not in mandatory, endpoint.name
            injected = endpoint.validate_params({"symbol": "AAPL"})
            assert injected["symbol"] == "AAPL"
            assert injected["structure"] == "flat"
            assert injected["period"] == "annual"
            structure = next(
                param
                for param in (endpoint.optional_params or [])
                if param.name == "structure"
            )
            assert tuple(str(v) for v in (structure.valid_values or ())) == (
                STRUCTURE_VALUES
            )
            with pytest.raises(FMPValidationError, match="Must be one of"):
                endpoint.validate_params({"symbol": "AAPL", "structure": "tree"})

    def test_report_period_is_optional(self) -> None:
        from fmp_data.company.endpoints import (
            FINANCIAL_REPORTS_JSON,
            FINANCIAL_REPORTS_XLSX,
        )
        from fmp_data.exceptions import ValidationError as FMPValidationError

        for endpoint in (FINANCIAL_REPORTS_JSON, FINANCIAL_REPORTS_XLSX):
            mandatory = {param.name for param in endpoint.mandatory_params}
            optional = {param.name for param in endpoint.optional_params or []}
            assert mandatory == {"symbol", "year"}, endpoint.name
            assert "period" in optional, endpoint.name
            assert "period" not in mandatory, endpoint.name
            injected = endpoint.validate_params({"symbol": "AAPL", "year": 2024})
            assert injected["period"] == "FY"
            with pytest.raises(FMPValidationError, match="Missing mandatory parameter"):
                endpoint.validate_params({"symbol": "AAPL"})
