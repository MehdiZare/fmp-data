from datetime import date, datetime
from unittest.mock import patch

import pytest

from fmp_data.market.models import (
    CIKListEntry,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    IPODisclosure,
    IPOProspectus,
    ISINResult,
    MarketHoliday,
    MarketHours,
)
from fmp_data.models import CompanySymbol


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


@pytest.fixture
def mock_market_holidays_data():
    """Mock market holidays data"""
    return [
        {
            "date": "2024-12-25",
            "exchange": "NYSE",
            "holiday": "Christmas Day",
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


def test_get_all_exchange_market_hours(fmp_client, mock_market_hours_data):
    """Test getting market hours for all exchanges"""
    market_hours_objs = [MarketHours(**item) for item in mock_market_hours_data]

    with patch.object(
        fmp_client.market.client, "request", return_value=market_hours_objs
    ):
        hours = fmp_client.market.get_all_exchange_market_hours()

    assert isinstance(hours, list)
    assert len(hours) == 1
    assert isinstance(hours[0], MarketHours)


def test_get_holidays_by_exchange(fmp_client, mock_market_holidays_data):
    """Test getting market holidays for a specific exchange"""
    holiday_objs = [MarketHoliday(**item) for item in mock_market_holidays_data]

    with patch.object(
        fmp_client.market.client, "request", return_value=holiday_objs
    ) as mock_request:
        holidays = fmp_client.market.get_holidays_by_exchange("NYSE")

    assert isinstance(holidays, list)
    assert len(holidays) == 1
    assert isinstance(holidays[0], MarketHoliday)
    assert holidays[0].exchange == "NYSE"
    assert holidays[0].holiday == "Christmas Day"
    mock_request.assert_called_once()
    assert mock_request.call_args[1]["exchange"] == "NYSE"


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

    @patch("httpx.Client.request")
    def test_search_symbols(
        self, mock_request, fmp_client, mock_response, search_result_data
    ):
        """Test symbol search through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_result_data]
        )

        results = fmp_client.market.search_symbol("Apple", limit=2, exchange="NASDAQ")
        assert len(results) == 1
        assert isinstance(results[0], CompanySearchResult)

        params = mock_request.call_args[1]["params"]
        assert params["query"] == "Apple"
        assert params["limit"] == 2
        assert params["exchange"] == "NASDAQ"

    @patch("httpx.Client.request")
    def test_search_exchange_variants(
        self, mock_request, fmp_client, mock_response, search_result_data
    ):
        """Test exchange variants search through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[search_result_data]
        )

        results = fmp_client.market.search_exchange_variants("Apple")
        assert len(results) == 1
        assert isinstance(results[0], CompanySearchResult)

        params = mock_request.call_args[1]["params"]
        assert params["query"] == "Apple"

    @patch("httpx.Client.request")
    def test_search_by_cik(self, mock_request, fmp_client, mock_response):
        """Test CIK search through client"""
        response_data = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "cik": "0000320193",
            }
        ]
        mock_request.return_value = mock_response(
            status_code=200, json_data=response_data
        )

        results = fmp_client.market.search_by_cik("320193")
        assert len(results) == 1
        assert isinstance(results[0], CIKResult)

        params = mock_request.call_args[1]["params"]
        assert params["cik"] == "320193"

    @patch("httpx.Client.request")
    def test_search_by_cusip(self, mock_request, fmp_client, mock_response):
        """Test CUSIP search through client"""
        response_data = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "cusip": "037833100"}
        ]
        mock_request.return_value = mock_response(
            status_code=200, json_data=response_data
        )

        results = fmp_client.market.search_by_cusip("037833100")
        assert len(results) == 1
        assert isinstance(results[0], CUSIPResult)

        params = mock_request.call_args[1]["params"]
        assert params["cusip"] == "037833100"

    @patch("httpx.Client.request")
    def test_search_by_isin(self, mock_request, fmp_client, mock_response):
        """Test ISIN search through client"""
        response_data = [
            {"symbol": "AAPL", "name": "Apple Inc.", "isin": "US0378331005"}
        ]
        mock_request.return_value = mock_response(
            status_code=200, json_data=response_data
        )

        results = fmp_client.market.search_by_isin("US0378331005")
        assert len(results) == 1
        assert isinstance(results[0], ISINResult)

        params = mock_request.call_args[1]["params"]
        assert params["isin"] == "US0378331005"


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


@patch("httpx.Client.request")
def test_get_financial_statement_symbol_list(mock_request, fmp_client, mock_response):
    """Test getting financial statement symbol list"""
    response_data = [{"symbol": "AAPL", "name": "Apple Inc."}]
    mock_request.return_value = mock_response(status_code=200, json_data=response_data)

    symbols = fmp_client.market.get_financial_statement_symbol_list()
    assert len(symbols) == 1
    assert isinstance(symbols[0], CompanySymbol)
    assert symbols[0].symbol == "AAPL"


@patch("httpx.Client.request")
def test_get_actively_trading_list(mock_request, fmp_client, mock_response):
    """Test getting actively trading list"""
    response_data = [{"symbol": "AAPL", "name": "Apple Inc."}]
    mock_request.return_value = mock_response(status_code=200, json_data=response_data)

    symbols = fmp_client.market.get_actively_trading_list()
    assert len(symbols) == 1
    assert isinstance(symbols[0], CompanySymbol)
    assert symbols[0].symbol == "AAPL"


@patch("httpx.Client.request")
def test_get_tradable_list(mock_request, fmp_client, mock_response):
    """Test getting tradable list"""
    response_data = [{"symbol": "AAPL", "name": "Apple Inc."}]
    mock_request.return_value = mock_response(status_code=200, json_data=response_data)

    symbols = fmp_client.market.get_tradable_list(limit=5, offset=10)
    assert len(symbols) == 1
    assert isinstance(symbols[0], CompanySymbol)

    params = mock_request.call_args[1]["params"]
    assert params["limit"] == 5
    assert params["offset"] == 10


@patch("httpx.Client.request")
def test_get_cik_list(mock_request, fmp_client, mock_response):
    """Test getting CIK list"""
    response_data = [
        {
            "cik": "0000320193",
            "companyName": "Apple Inc.",
        }
    ]
    mock_request.return_value = mock_response(status_code=200, json_data=response_data)

    results = fmp_client.market.get_cik_list(page=1, limit=20)
    assert len(results) == 1
    assert isinstance(results[0], CIKListEntry)
    assert results[0].cik == "0000320193"

    params = mock_request.call_args[1]["params"]
    assert params["page"] == 1
    assert params["limit"] == 20


@patch("httpx.Client.request")
def test_get_company_screener(mock_request, fmp_client, mock_response):
    """Test getting company screener results"""
    response_data = [{"symbol": "AAPL", "name": "Apple Inc.", "currency": "USD"}]
    mock_request.return_value = mock_response(status_code=200, json_data=response_data)

    results = fmp_client.market.get_company_screener(
        market_cap_more_than=1_000_000_000,
        is_etf=False,
        sector="Technology",
        limit=5,
    )
    assert len(results) == 1
    assert isinstance(results[0], CompanySearchResult)
    assert results[0].symbol == "AAPL"

    params = mock_request.call_args[1]["params"]
    assert params["marketCapMoreThan"] == 1_000_000_000
    assert params["isEtf"] is False
    assert params["sector"] == "Technology"
    assert params["limit"] == 5


class TestIPOEndpoints:
    """Tests for IPO disclosure and prospectus endpoints"""

    @pytest.fixture
    def mock_ipo_disclosure_data(self):
        """Mock IPO disclosure data"""
        return {
            "symbol": "RDDT",
            "filingDate": "2024-02-22",
            "acceptedDate": "2024-02-22",
            "effectivenessDate": "2024-03-21",
            "cik": "0001234567",
            "form": "S-1",
            "url": "https://www.sec.gov/Archives/edgar/data/123456/...",
        }

    @pytest.fixture
    def mock_ipo_prospectus_data(self):
        """Mock IPO prospectus data"""
        return {
            "symbol": "RDDT",
            "acceptedDate": "2024-02-22",
            "filingDate": "2024-02-22",
            "ipoDate": "2024-03-21",
            "cik": "0001234567",
            "pricePublicPerShare": 34.00,
            "pricePublicTotal": 748000000.0,
            "discountsAndCommissionsPerShare": 0.50,
            "discountsAndCommissionsTotal": 11000000.0,
            "proceedsBeforeExpensesPerShare": 33.50,
            "proceedsBeforeExpensesTotal": 737000000.0,
            "form": "424B4",
            "url": "https://www.sec.gov/Archives/edgar/data/123456/...",
        }

    def test_ipo_disclosure_model_validation(self, mock_ipo_disclosure_data):
        """Test IPODisclosure model validation"""
        disclosure = IPODisclosure.model_validate(mock_ipo_disclosure_data)
        assert disclosure.symbol == "RDDT"
        assert disclosure.cik == "0001234567"
        assert disclosure.form == "S-1"
        assert disclosure.url is not None
        assert isinstance(disclosure.filing_date, datetime)

    def test_ipo_prospectus_model_validation(self, mock_ipo_prospectus_data):
        """Test IPOProspectus model validation"""
        prospectus = IPOProspectus.model_validate(mock_ipo_prospectus_data)
        assert prospectus.symbol == "RDDT"
        assert isinstance(prospectus.ipo_date, datetime)
        assert prospectus.cik == "0001234567"
        assert prospectus.price_public_per_share == 34.00
        assert prospectus.price_public_total == 748000000.0
        assert prospectus.discounts_and_commissions_total == 11000000.0
        assert prospectus.proceeds_before_expenses_total == 737000000.0
        assert prospectus.form == "424B4"

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

        # Verify request parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        # Dates can be string or date objects depending on client params
        from_param = call_args[1]["params"]["from"]
        to_param = call_args[1]["params"]["to"]
        assert str(from_param) == "2024-01-01"
        assert str(to_param) == "2024-12-31"
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
        assert prospectuses[0].price_public_per_share == 34.00
        assert prospectuses[0].price_public_total == 748000000.0

        # Verify request was made with only limit parameter
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["limit"] == 5
        assert "from" not in call_args[1]["params"]
        assert "to" not in call_args[1]["params"]


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected_params"),
    [
        (
            "get_sector_performance",
            {"sector": "Energy", "date": date(2024, 2, 1), "exchange": "NASDAQ"},
            {"sector": "Energy", "date": "2024-02-01", "exchange": "NASDAQ"},
        ),
        (
            "get_industry_performance_snapshot",
            {
                "industry": "Biotechnology",
                "date": date(2024, 2, 1),
                "exchange": "NASDAQ",
            },
            {"industry": "Biotechnology", "date": "2024-02-01", "exchange": "NASDAQ"},
        ),
        (
            "get_historical_sector_performance",
            {
                "sector": "Energy",
                "from_date": date(2024, 2, 1),
                "to_date": date(2024, 3, 1),
                "exchange": "NASDAQ",
            },
            {
                "sector": "Energy",
                "from": "2024-02-01",
                "to": "2024-03-01",
                "exchange": "NASDAQ",
            },
        ),
        (
            "get_historical_industry_performance",
            {
                "industry": "Biotechnology",
                "from_date": date(2024, 2, 1),
                "to_date": date(2024, 3, 1),
                "exchange": "NASDAQ",
            },
            {
                "industry": "Biotechnology",
                "from": "2024-02-01",
                "to": "2024-03-01",
                "exchange": "NASDAQ",
            },
        ),
        (
            "get_sector_pe_snapshot",
            {"sector": "Energy", "date": date(2024, 2, 1), "exchange": "NASDAQ"},
            {"sector": "Energy", "date": "2024-02-01", "exchange": "NASDAQ"},
        ),
        (
            "get_industry_pe_snapshot",
            {
                "industry": "Biotechnology",
                "date": date(2024, 2, 1),
                "exchange": "NASDAQ",
            },
            {"industry": "Biotechnology", "date": "2024-02-01", "exchange": "NASDAQ"},
        ),
        (
            "get_historical_sector_pe",
            {
                "sector": "Energy",
                "from_date": date(2024, 2, 1),
                "to_date": date(2024, 3, 1),
                "exchange": "NASDAQ",
            },
            {
                "sector": "Energy",
                "from": "2024-02-01",
                "to": "2024-03-01",
                "exchange": "NASDAQ",
            },
        ),
        (
            "get_historical_industry_pe",
            {
                "industry": "Biotechnology",
                "from_date": date(2024, 2, 1),
                "to_date": date(2024, 3, 1),
                "exchange": "NASDAQ",
            },
            {
                "industry": "Biotechnology",
                "from": "2024-02-01",
                "to": "2024-03-01",
                "exchange": "NASDAQ",
            },
        ),
    ],
)
def test_market_performance_requests(fmp_client, method_name, kwargs, expected_params):
    """Test market performance request parameters"""
    with patch.object(fmp_client.market.client, "request", return_value=[]) as mock_req:
        getattr(fmp_client.market, method_name)(**kwargs)
        call_args = mock_req.call_args
    for key, value in expected_params.items():
        assert call_args[1][key] == value
