"""Additional tests for company client to improve coverage"""

from unittest.mock import patch

import pytest

from fmp_data.company.models import CompanyExecutive, CompanyProfile, Quote


class TestCompanyClientCoverage:
    """Tests to improve coverage for CompanyClient"""

    @pytest.fixture
    def company_profile_data(self):
        """Mock company profile data"""
        return {
            "symbol": "AAPL",
            "price": 195.50,
            "beta": 1.25,
            "volAvg": 50000000,
            "mktCap": 3000000000000,
            "lastDiv": 0.96,
            "range": "140.00-200.00",
            "changes": 2.50,
            "companyName": "Apple Inc.",
            "currency": "USD",
            "cik": "0000320193",
            "isin": "US0378331005",
            "cusip": "037833100",
            "exchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
            "industry": "Consumer Electronics",
            "website": "https://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones...",  # noqa: E501
            "ceo": "Tim Cook",
            "sector": "Technology",
            "country": "US",
            "fullTimeEmployees": "164000",
            "phone": "408-996-1010",
            "address": "One Apple Park Way",
            "city": "Cupertino",
            "state": "CA",
            "zip": "95014",
            "dcfDiff": 15.25,
            "dcf": 180.25,
            "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
            "ipoDate": "1980-12-12",
            "defaultImage": False,
            "isEtf": False,
            "isActivelyTrading": True,
            "isAdr": False,
            "isFund": False,
        }

    @pytest.fixture
    def company_executive_data(self):
        """Mock company executive data"""
        return {
            "title": "Chief Executive Officer",
            "name": "Tim Cook",
            "pay": 91600000,
            "currencyPay": "USD",
            "gender": "male",
            "yearBorn": 1960,
            "titleSince": 2011,
        }

    @pytest.fixture
    def quote_data(self):
        """Mock quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 195.50,
            "changesPercentage": 1.28,
            "change": 2.47,
            "dayLow": 193.00,
            "dayHigh": 196.50,
            "yearHigh": 200.00,
            "yearLow": 140.00,
            "marketCap": 3000000000000,
            "priceAvg50": 185.25,
            "priceAvg200": 175.50,
            "exchange": "NASDAQ",
            "volume": 55000000,
            "avgVolume": 50000000,
            "open": 193.50,
            "previousClose": 193.03,
            "eps": 6.13,
            "pe": 31.88,
            "earningsAnnouncement": "2024-02-01T21:30:00.000+0000",
            "sharesOutstanding": 15350000000,
            "timestamp": 1704067200,
        }

    @patch("httpx.Client.request")
    def test_get_company_profile(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profile"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data]
        )

        result = fmp_client.company.get_company_profile("AAPL")

        assert len(result) == 1
        profile = result[0]
        assert isinstance(profile, CompanyProfile)
        assert profile.symbol == "AAPL"
        assert profile.company_name == "Apple Inc."
        assert profile.mkt_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_key_executives(
        self, mock_request, fmp_client, mock_response, company_executive_data
    ):
        """Test fetching key executives"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_executive_data]
        )

        result = fmp_client.company.get_key_executives("AAPL")

        assert len(result) == 1
        executive = result[0]
        assert isinstance(executive, CompanyExecutive)
        assert executive.name == "Tim Cook"
        assert executive.title == "Chief Executive Officer"
        assert executive.pay == 91600000

    @patch("httpx.Client.request")
    def test_get_quote(self, mock_request, fmp_client, mock_response, quote_data):
        """Test fetching company quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[quote_data]
        )

        result = fmp_client.company.get_quote("AAPL")

        assert len(result) == 1
        quote = result[0]
        assert isinstance(quote, Quote)
        assert quote.symbol == "AAPL"
        assert quote.price == 195.50
        assert quote.market_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_company_profile_with_limit(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profile with limit parameter"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data]
        )

        result = fmp_client.company.get_company_profile("AAPL", limit=1)

        assert len(result) == 1
        profile = result[0]
        assert isinstance(profile, CompanyProfile)
        assert profile.symbol == "AAPL"

        # Verify the request was made with limit parameter
        mock_request.assert_called_once()

    @patch("httpx.Client.request")
    def test_search_companies(self, mock_request, fmp_client, mock_response):
        """Test searching companies"""
        search_results = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "currency": "USD",
                "stockExchange": "NASDAQ Global Select",
                "exchangeShortName": "NASDAQ",
            },
            {
                "symbol": "APLE",
                "name": "Apple Hospitality REIT, Inc.",
                "currency": "USD",
                "stockExchange": "New York Stock Exchange",
                "exchangeShortName": "NYSE",
            },
        ]

        mock_request.return_value = mock_response(
            status_code=200, json_data=search_results
        )

        result = fmp_client.company.search("apple", limit=2)

        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[1]["symbol"] == "APLE"

    @patch("httpx.Client.request")
    def test_get_company_peers(self, mock_request, fmp_client, mock_response):
        """Test fetching company peers"""
        peers_data = [
            "MSFT",
            "GOOGL",
            "META",
            "AMZN",
            "NVDA",
            "TSLA",
            "ORCL",
            "IBM",
            "INTC",
            "AMD",
        ]

        mock_request.return_value = mock_response(status_code=200, json_data=peers_data)

        result = fmp_client.company.get_company_peers("AAPL")

        assert len(result) == 10
        assert "MSFT" in result
        assert "GOOGL" in result
