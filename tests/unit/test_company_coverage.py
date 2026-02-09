"""Additional tests for company client to improve coverage"""

from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.company.models import (
    AftermarketQuote,
    AftermarketTrade,
    CompanyExecutive,
    CompanyOutlook,
    CompanyPeer,
    CompanyProfile,
    FinancialReportJSON,
    FinancialReportSectionRow,
    GeographicRevenueSegment,
    HistoricalPrice,
    IntradayPrice,
    MergerAcquisition,
    Quote,
    RevenueSegmentItem,
    SimpleQuote,
    StockPriceChange,
)
from fmp_data.market.models import CompanySearchResult


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
            "changePercentage": 1.28,  # Add the required field
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

    @pytest.fixture
    def aftermarket_trade_data(self):
        """Mock aftermarket trade data"""
        return {
            "symbol": "AAPL",
            "price": 232.53,
            "tradeSize": 132,
            "timestamp": 1738715334311,
        }

    @pytest.fixture
    def aftermarket_quote_data(self):
        """Mock aftermarket quote data"""
        return {
            "symbol": "AAPL",
            "bidSize": 1,
            "bidPrice": 232.45,
            "askSize": 3,
            "askPrice": 232.64,
            "volume": 41647042,
            "timestamp": 1738715334311,
        }

    @pytest.fixture
    def stock_price_change_data(self):
        """Mock stock price change data"""
        return {
            "symbol": "AAPL",
            "1D": 2.1008,
            "5D": -2.45946,
            "1M": -4.33925,
            "3M": 4.86014,
            "6M": 5.88556,
            "ytd": -4.53147,
            "1Y": 24.04092,
            "3Y": 35.04264,
            "5Y": 192.05871,
            "10Y": 678.8558,
            "max": 181279.04168,
        }

    @pytest.fixture
    def geographic_revenue_data(self):
        """Mock geographic revenue segmentation data"""
        return {
            "date": "2024-09-28",
            "data": {
                "Americas Segment": 167045000000,
                "Europe Segment": 101328000000,
            },
        }

    @pytest.fixture
    def intraday_price_data(self):
        """Mock intraday price data"""
        return {
            "date": "2025-02-04 15:59:00",
            "open": 233.01,
            "low": 232.72,
            "high": 233.13,
            "close": 232.79,
            "volume": 720121,
        }

    @patch("httpx.Client.request")
    def test_get_company_profile(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profile"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data]
        )

        # get_profile returns a single CompanyProfile, not a list
        result = fmp_client.company.get_profile("AAPL")

        assert isinstance(result, CompanyProfile)
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        assert result.mkt_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_key_executives(
        self, mock_request, fmp_client, mock_response, company_executive_data
    ):
        """Test fetching key executives"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_executive_data]
        )

        # get_executives returns a list of CompanyExecutive
        result = fmp_client.company.get_executives("AAPL")

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

        # get_quote returns a single Quote object
        result = fmp_client.company.get_quote("AAPL")

        assert isinstance(result, Quote)
        assert result.symbol == "AAPL"
        assert result.price == 195.50
        assert result.market_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_aftermarket_trade(
        self, mock_request, fmp_client, mock_response, aftermarket_trade_data
    ):
        """Test fetching aftermarket trades"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[aftermarket_trade_data]
        )

        result = fmp_client.company.get_aftermarket_trade("AAPL")

        assert isinstance(result, AftermarketTrade)
        assert result.symbol == "AAPL"
        assert result.trade_size == 132
        assert result.price == 232.53

    @patch("httpx.Client.request")
    def test_get_aftermarket_quote(
        self, mock_request, fmp_client, mock_response, aftermarket_quote_data
    ):
        """Test fetching aftermarket quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[aftermarket_quote_data]
        )

        result = fmp_client.company.get_aftermarket_quote("AAPL")

        assert isinstance(result, AftermarketQuote)
        assert result.symbol == "AAPL"
        assert result.bid_price == 232.45
        assert result.ask_price == 232.64

    @patch("httpx.Client.request")
    def test_get_stock_price_change(
        self, mock_request, fmp_client, mock_response, stock_price_change_data
    ):
        """Test fetching stock price change data"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[stock_price_change_data]
        )

        result = fmp_client.company.get_stock_price_change("AAPL")

        assert isinstance(result, StockPriceChange)
        assert result.symbol == "AAPL"
        assert result.one_day == 2.1008
        assert result.max_change == 181279.04168

    @patch("httpx.Client.request")
    def test_get_geographic_revenue_segmentation_period(
        self, mock_request, fmp_client, mock_response, geographic_revenue_data
    ):
        """Test geographic revenue segmentation passes period"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[geographic_revenue_data]
        )

        result = fmp_client.company.get_geographic_revenue_segmentation(
            "AAPL", period="annual"
        )

        assert len(result) == 1
        assert isinstance(result[0], GeographicRevenueSegment)
        params = mock_request.call_args.kwargs["params"]
        assert params["symbol"] == "AAPL"
        assert params["period"] == "annual"

    @patch("httpx.Client.request")
    def test_get_intraday_prices_with_filters(
        self, mock_request, fmp_client, mock_response, intraday_price_data
    ):
        """Test intraday price parameters are forwarded"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[intraday_price_data]
        )

        result = fmp_client.company.get_intraday_prices(
            "AAPL",
            interval="1min",
            from_date=date(2025, 2, 1),
            to_date=date(2025, 2, 4),
            nonadjusted=True,
        )

        assert len(result) == 1
        assert isinstance(result[0], IntradayPrice)
        params = mock_request.call_args.kwargs["params"]
        assert params["symbol"] == "AAPL"
        assert params["from"].isoformat() == "2025-02-01"
        assert params["to"].isoformat() == "2025-02-04"
        assert params["nonadjusted"] is True

    @patch("httpx.Client.request")
    def test_get_ttm_statements_with_limit(
        self, mock_request, fmp_client, mock_response
    ):
        """Test forwarding limit for TTM statement endpoints"""
        mock_request.return_value = mock_response(status_code=200, json_data=[])

        fmp_client.company.get_income_statement_ttm("AAPL", limit=5)
        params = mock_request.call_args.kwargs["params"]
        assert params["symbol"] == "AAPL"
        assert params["limit"] == 5

    @patch("httpx.Client.request")
    def test_get_company_profile_with_multiple_symbols(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profiles for multiple symbols"""
        # Modify data for second company
        second_profile = company_profile_data.copy()
        second_profile["symbol"] = "MSFT"
        second_profile["companyName"] = "Microsoft Corporation"

        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data, second_profile]
        )

        # When passing multiple symbols, get_profile could return multiple profiles
        result = fmp_client.company.get_profile("AAPL,MSFT")

        # If multiple profiles returned in a list response
        if isinstance(result, list):
            assert len(result) == 2
            assert result[0].symbol == "AAPL"
            assert result[1].symbol == "MSFT"
        else:
            # Single profile for single symbol
            assert result.symbol == "AAPL"

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

        # search_company is in the market client, not company client
        result = fmp_client.market.search_company("apple", limit=2)

        assert len(result) == 2
        assert isinstance(result[0], CompanySearchResult)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "APLE"

    @patch("httpx.Client.request")
    def test_get_company_peers(self, mock_request, fmp_client, mock_response):
        """Test fetching company peers"""
        # CompanyPeer expects objects with symbol and companyName fields
        peers_data = [
            {
                "symbol": "MSFT",
                "companyName": "Microsoft Corporation",
                "price": 400.0,
                "mktCap": 3000000000000,
            },
            {
                "symbol": "GOOGL",
                "companyName": "Alphabet Inc.",
                "price": 150.0,
                "mktCap": 2000000000000,
            },
            {
                "symbol": "META",
                "companyName": "Meta Platforms Inc.",
                "price": 500.0,
                "mktCap": 1300000000000,
            },
            {
                "symbol": "AMZN",
                "companyName": "Amazon.com Inc.",
                "price": 180.0,
                "mktCap": 1900000000000,
            },
            {
                "symbol": "NVDA",
                "companyName": "NVIDIA Corporation",
                "price": 900.0,
                "mktCap": 2200000000000,
            },
        ]

        mock_request.return_value = mock_response(status_code=200, json_data=peers_data)

        result = fmp_client.company.get_company_peers("AAPL")

        assert len(result) == 5
        assert isinstance(result[0], CompanyPeer)
        assert result[0].symbol == "MSFT"
        assert result[0].name == "Microsoft Corporation"


class TestCompanyOutlook:
    """Tests for CompanyOutlook model and its normalize_profile_block validator."""

    def test_profile_as_dict(self):
        data = {
            "symbol": "AAPL",
            "companyName": "Apple Inc.",
            "profile": {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "price": 195.0,
            },
        }
        outlook = CompanyOutlook(**data)
        assert outlook.symbol == "AAPL"
        assert isinstance(outlook.profile, CompanyProfile)

    def test_profile_as_list_with_single_dict(self):
        data = {
            "symbol": "AAPL",
            "profile": [
                {"symbol": "AAPL", "companyName": "Apple Inc.", "price": 195.0}
            ],
        }
        outlook = CompanyOutlook(**data)
        assert isinstance(outlook.profile, CompanyProfile)
        assert outlook.profile.symbol == "AAPL"

    def test_profile_as_empty_list_returns_none(self):
        data = {"symbol": "AAPL", "profile": []}
        outlook = CompanyOutlook(**data)
        assert outlook.profile is None

    def test_profile_none(self):
        data = {"symbol": "AAPL"}
        outlook = CompanyOutlook(**data)
        assert outlook.profile is None


class TestFinancialReportSectionRow:
    """Tests for FinancialReportSectionRow model validator."""

    def test_dict_with_list_values(self):
        row = FinancialReportSectionRow(**{"Revenue": [100, 200]})
        assert row.row == {"Revenue": [100, 200]}

    def test_dict_with_scalar_values_wrapped_in_list(self):
        row = FinancialReportSectionRow(**{"Revenue": 100})
        assert row.row == {"Revenue": [100]}

    def test_non_dict_raises_value_error(self):
        with pytest.raises((ValueError, TypeError)):
            FinancialReportSectionRow.model_validate("not_a_dict")


class TestFinancialReportJSON:
    """Tests for FinancialReportJSON model and its normalize_sections validator."""

    def test_known_keys_extracted(self):
        data = {
            "symbol": "AAPL",
            "period": "FY",
            "year": 2024,
            "income_statement": [{"Revenue": [100]}],
        }
        report = FinancialReportJSON.model_validate(data)
        assert report.symbol == "AAPL"
        assert report.period == "FY"
        assert report.year == 2024
        assert "income_statement" in report.sections

    def test_dict_item_wrapped_in_list(self):
        data = {
            "symbol": "AAPL",
            "balance_sheet": {"Assets": 500},
        }
        report = FinancialReportJSON.model_validate(data)
        assert len(report.sections["balance_sheet"]) == 1

    def test_primitive_wrapped_in_value_list(self):
        data = {
            "symbol": "AAPL",
            "note": "some text",
        }
        report = FinancialReportJSON.model_validate(data)
        section = report.sections["note"]
        assert len(section) == 1
        assert section[0].row == {"value": ["some text"]}

    def test_non_dict_input_raises(self):
        with pytest.raises(Exception, match="dictionary"):
            FinancialReportJSON.model_validate("not_a_dict")

    def test_model_dump_json(self):
        data = {
            "symbol": "AAPL",
            "period": "FY",
            "year": 2024,
            "income": [{"Revenue": [100]}],
        }
        report = FinancialReportJSON.model_validate(data)
        dumped = report.model_dump(mode="json")
        assert dumped["symbol"] == "AAPL"
        assert "income" in dumped["sections"]


class TestNewModelFields:
    """Tests for new optional fields added to existing models."""

    def test_simple_quote_change_field(self):
        q = SimpleQuote(symbol="AAPL", price=195.0, volume=100, change=2.5)
        assert q.change == 2.5

    def test_simple_quote_change_none(self):
        q = SimpleQuote(symbol="AAPL", price=195.0, volume=100)
        assert q.change is None

    def test_historical_price_adj_fields(self):
        hp = HistoricalPrice.model_validate(
            {
                "date": "2024-01-01",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 104.0,
                "adjClose": 103.5,
                "adjHigh": 104.8,
                "adjLow": 98.5,
                "adjOpen": 99.8,
                "symbol": "AAPL",
            }
        )
        assert hp.adj_high == 104.8
        assert hp.adj_low == 98.5
        assert hp.adj_open == 99.8
        assert hp.symbol == "AAPL"

    def test_revenue_segment_item_metadata_fields(self):
        item = RevenueSegmentItem.model_validate(
            {
                "date": "2024-09-28",
                "data": {"Segment A": 100.0},
                "symbol": "AAPL",
                "fiscalYear": 2024,
                "period": "FY",
                "reportedCurrency": "USD",
            }
        )
        assert item.symbol == "AAPL"
        assert item.fiscal_year == 2024
        assert item.period == "FY"
        assert item.reported_currency == "USD"

    def test_merger_acquisition_new_fields(self):
        ma = MergerAcquisition.model_validate(
            {
                "companyName": "Acme Corp",
                "symbol": "ACME",
                "cik": "0001234567",
                "targetedSymbol": "TGT",
                "targetedCik": "0009876543",
                "transactionDate": "2024-06-15",
                "acceptedDate": "2024-06-10",
                "link": "https://sec.gov/filing/123",
            }
        )
        assert ma.symbol == "ACME"
        assert ma.cik == "0001234567"
        assert ma.targeted_symbol == "TGT"
        assert ma.targeted_cik == "0009876543"
        assert ma.transaction_date == "2024-06-15"
        assert ma.accepted_date == "2024-06-10"
        assert ma.link == "https://sec.gov/filing/123"


class TestFinancialReportsJSONClient:
    """Tests for sync/async financial_reports_json FinancialReportJSON path."""

    @patch("httpx.Client.request")
    def test_sync_returns_dict_from_financial_report_json(
        self, mock_request, fmp_client, mock_response
    ):
        """Test that FinancialReportJSON is converted to dict via model_dump."""
        report_data = {
            "symbol": "AAPL",
            "period": "FY",
            "year": 2024,
            "income": [{"Revenue": [100]}],
        }
        mock_request.return_value = mock_response(
            status_code=200, json_data=report_data
        )
        result = fmp_client.company.get_financial_reports_json(
            "AAPL", 2024, period="FY"
        )
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"

    @patch("httpx.Client.request")
    def test_sync_financial_reports_json_model_dump_path(
        self, mock_request, fmp_client, mock_response
    ):
        """Verify FinancialReportJSON.model_dump is used when model is returned."""
        from fmp_data.company.models import FinancialReportJSON

        report = FinancialReportJSON.model_validate(
            {"symbol": "AAPL", "period": "FY", "year": 2024}
        )
        with patch.object(fmp_client.company.client, "request", return_value=report):
            result = fmp_client.company.get_financial_reports_json(
                "AAPL", 2024, period="FY"
            )
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert result["sections"] == {}

    @pytest.mark.asyncio
    async def test_async_financial_reports_json_model_dump_path(self):
        """Verify async path converts FinancialReportJSON to dict."""
        from unittest.mock import AsyncMock

        from fmp_data.company.async_client import AsyncCompanyClient
        from fmp_data.company.models import FinancialReportJSON

        report = FinancialReportJSON.model_validate(
            {"symbol": "AAPL", "period": "FY", "year": 2024}
        )

        mock_base = AsyncMock()
        mock_base.request_async = AsyncMock(return_value=report)
        async_client = AsyncCompanyClient.__new__(AsyncCompanyClient)
        async_client._client = mock_base

        result = await async_client.get_financial_reports_json(
            "AAPL", 2024, period="FY"
        )
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
