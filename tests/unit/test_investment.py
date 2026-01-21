from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.client import FMPDataClient
from fmp_data.exceptions import RateLimitError
from fmp_data.investment.models import (
    ETFCountryWeighting,
    ETFHolding,
    ETFInfo,
    ETFSectorWeighting,
    FundDisclosureHolderLatest,
    FundDisclosureHolding,
    FundDisclosureSearchResult,
    MutualFundHolding,
)


class TestInvestmentClient:
    """Tests for InvestmentClient and its ETF and Mutual Fund endpoints"""

    # Fixtures for mock data
    @pytest.fixture
    def etf_holding_data(self):
        """Mock data for ETF holdings"""
        return {
            "symbol": "SPY",
            "asset": "AAPL",
            "name": "Apple Inc",
            "isin": "US0378331005",
            "securityCusip": "037833100",
            "sharesNumber": 1000000,
            "weightPercentage": 7.5,
            "marketValue": 150000000.0,
            "updatedAt": "2023-11-27 17:41:05",
        }

    @pytest.fixture
    def etf_info_data(self):
        """Mock data for ETF information"""
        return {
            "symbol": "SPY",
            "name": "S&P 500 ETF",
            "expenseRatio": 0.09,
            "assetsUnderManagement": 3500000000.0,
            "avgVolume": 5000000,
            "description": "Tracks the S&P 500 index.",
            "inceptionDate": "1993-01-29",
            "holdingsCount": 500,
            "securityCusip": "123456789",
            "isin": "US1234567890",
            "domicile": "US",
            "etfCompany": "SPDR",
            "nav": 420.50,
            "navCurrency": "USD",
            "sectorsList": [
                {
                    "industry": "Software & Services",
                    "exposure": 27.5,
                }
            ],
            "website": "https://www.ssga.com",
        }

    @pytest.fixture
    def sector_weighting_data(self):
        """Mock data for ETF sector weightings"""
        return {"sector": "Technology", "weightPercentage": 27.5}

    @pytest.fixture
    def country_weighting_data(self):
        """Mock data for ETF country weightings"""
        return {"country": "United States", "weightPercentage": 80.0}

    @pytest.fixture
    def mutual_fund_holding_data(self):
        """Mock data for mutual fund holdings"""
        return {
            "symbol": "VFIAX",
            "cik": "0000102909",
            "name": "Vanguard 500 Index Fund",
            "asset": "AAPL",
            "marketValue": 1000000.0,
            "weightPercentage": 5.0,
            "reportedDate": "2024-01-01",
            "cusip": "921937728",
            "isin": "US9219377289",
            "shares": 1000,
        }

    @pytest.fixture
    def fund_disclosure_holder_latest_data(self):
        """Mock data for latest mutual fund/ETF disclosure holders"""
        return {
            "cik": "0000106444",
            "holder": "VANGUARD FIXED INCOME SECURITIES FUNDS",
            "shares": 67030000,
            "dateReported": "2024-07-31",
            "change": 0,
            "weightPercent": 0.03840197,
        }

    @pytest.fixture
    def fund_disclosure_data(self):
        """Mock data for mutual fund/ETF disclosure holdings"""
        return {
            "cik": "0000857489",
            "date": "2023-10-31",
            "acceptedDate": "2023-12-28 09:26:13",
            "symbol": "000089.SZ",
            "name": "Shenzhen Airport Co Ltd",
            "lei": "3003009W045RIKRBZI44",
            "title": "SHENZ AIRPORT-A",
            "cusip": "N/A",
            "isin": "CNE000000VK1",
            "balance": 2438784,
            "units": "NS",
            "cur_cd": "CNY",
            "valUsd": 2255873.6,
            "pctVal": 0.0023838966,
            "payoffProfile": "Long",
            "assetCat": "EC",
            "issuerCat": "CORP",
            "invCountry": "CN",
            "isRestrictedSec": "N",
            "fairValLevel": "2",
            "isCashCollateral": "N",
            "isNonCashCollateral": "N",
            "isLoanByFund": "N",
        }

    @pytest.fixture
    def fund_disclosure_search_result_data(self):
        """Mock data for mutual fund/ETF disclosure holder search"""
        return {
            "symbol": "FGOAX",
            "cik": "0000355691",
            "classId": "C000024574",
            "seriesId": "S000009042",
            "entityName": "Federated Hermes Government Income Securities, Inc.",
            "entityOrgType": "30",
            "seriesName": "Federated Hermes Government Income Securities, Inc.",
            "className": "Class A Shares",
            "reportingFileNumber": "811-03266",
            "address": "4000 ERICSSON DRIVE",
            "city": "WARRENDALE",
            "zipCode": "15086-7561",
            "state": "PA",
        }

    # ETF endpoint tests
    @patch("httpx.Client.request")
    def test_get_etf_holdings(
        self, mock_request, fmp_client, mock_response, etf_holding_data
    ):
        """Test fetching ETF holdings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[etf_holding_data]
        )
        result = fmp_client.investment.get_etf_holdings(symbol="SPY")
        assert len(result) == 1
        holding = result[0]
        assert isinstance(holding, ETFHolding)
        assert holding.symbol == "SPY"
        assert holding.asset == "AAPL"
        assert holding.market_value == 150000000.0

    @patch("httpx.Client.request")
    def test_get_etf_info(self, mock_request, fmp_client, mock_response, etf_info_data):
        """Test fetching ETF information"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[etf_info_data]
        )
        result = fmp_client.investment.get_etf_info(symbol="SPY")
        assert isinstance(result, ETFInfo)
        assert result.symbol == "SPY"
        assert result.expense_ratio == 0.09

    @patch("httpx.Client.request")
    def test_get_etf_sector_weightings(
        self, mock_request, fmp_client, mock_response, sector_weighting_data
    ):
        """Test fetching ETF sector weightings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[sector_weighting_data]
        )
        result = fmp_client.investment.get_etf_sector_weightings(symbol="SPY")
        assert len(result) == 1
        sector = result[0]
        assert isinstance(sector, ETFSectorWeighting)
        assert sector.sector == "Technology"
        # Values > 1 are normalized to 0-1 scale (27.5 -> 0.275)
        assert sector.weight_percentage == 0.275

    @patch("httpx.Client.request")
    def test_get_etf_country_weightings(
        self, mock_request, fmp_client, mock_response, country_weighting_data
    ):
        """Test fetching ETF country weightings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[country_weighting_data]
        )
        result = fmp_client.investment.get_etf_country_weightings(symbol="SPY")
        assert len(result) == 1
        country = result[0]
        assert isinstance(country, ETFCountryWeighting)
        assert country.country == "United States"
        assert country.weight_percentage == 80.0

    # Mutual Fund endpoint tests
    @patch("httpx.Client.request")
    def test_get_mutual_fund_holdings(
        self, mock_request, fmp_client, mock_response, mutual_fund_holding_data
    ):
        """Test fetching mutual fund holdings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[mutual_fund_holding_data]
        )
        result = fmp_client.investment.get_mutual_fund_holdings(
            symbol="VFIAX", holdings_date=date(2024, 1, 1)
        )
        assert len(result) == 1
        holding = result[0]
        assert isinstance(holding, MutualFundHolding)
        assert holding.symbol == "VFIAX"
        assert holding.asset == "AAPL"
        assert holding.market_value == 1000000.0

    @patch("httpx.Client.request")
    def test_get_fund_disclosure_holders_latest(
        self,
        mock_request,
        fmp_client,
        mock_response,
        fund_disclosure_holder_latest_data,
    ):
        """Test fetching latest fund disclosure holders"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[fund_disclosure_holder_latest_data]
        )
        result = fmp_client.investment.get_fund_disclosure_holders_latest(symbol="AAPL")
        assert len(result) == 1
        holder = result[0]
        assert isinstance(holder, FundDisclosureHolderLatest)
        assert holder.holder == "VANGUARD FIXED INCOME SECURITIES FUNDS"
        assert holder.weight_percent == 0.03840197

    @patch("httpx.Client.request")
    def test_get_fund_disclosure(
        self, mock_request, fmp_client, mock_response, fund_disclosure_data
    ):
        """Test fetching mutual fund/ETF disclosure holdings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[fund_disclosure_data]
        )
        result = fmp_client.investment.get_fund_disclosure(
            symbol="VWO", year=2023, quarter=4
        )
        assert len(result) == 1
        holding = result[0]
        assert isinstance(holding, FundDisclosureHolding)
        assert holding.symbol == "000089.SZ"
        assert holding.cur_cd == "CNY"
        assert holding.val_usd == 2255873.6

    @patch("httpx.Client.request")
    def test_search_fund_disclosure_holders(
        self,
        mock_request,
        fmp_client,
        mock_response,
        fund_disclosure_search_result_data,
    ):
        """Test searching fund disclosure holders by name"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[fund_disclosure_search_result_data]
        )
        result = fmp_client.investment.search_fund_disclosure_holders(
            name="Federated Hermes"
        )
        assert len(result) == 1
        entry = result[0]
        assert isinstance(entry, FundDisclosureSearchResult)
        assert entry.symbol == "FGOAX"
        assert entry.reporting_file_number == "811-03266"

    @patch("httpx.Client.request")
    def test_rate_limit_handling(self, mock_request, fmp_client):
        """Test handling rate limit errors for investment endpoints"""
        client = FMPDataClient(
            config=fmp_client.config.model_copy(update={"max_retries": 2})
        )
        with (
            patch.object(
                client._rate_limiter, "should_allow_request", return_value=False
            ),
            patch.object(client._rate_limiter, "get_wait_time", return_value=0.0),
            patch.object(
                client, "_handle_rate_limit", side_effect=RateLimitError("rl")
            ),
        ):
            with pytest.raises(RateLimitError):
                client.investment.get_etf_holdings(
                    symbol="SPY", holdings_date=date(2024, 1, 15)
                )
        client.close()
