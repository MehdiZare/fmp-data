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

    # ETF endpoint tests
    @patch("httpx.Client.request")
    def test_get_etf_holdings(
        self, mock_request, fmp_client, mock_response, etf_holding_data
    ):
        """Test fetching ETF holdings"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[etf_holding_data]
        )
        result = fmp_client.investment.get_etf_holdings(
            symbol="SPY", holdings_date=date(2024, 1, 15)
        )
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
            patch.object(client, "_handle_rate_limit", side_effect=RateLimitError("rl")),
        ):
            with pytest.raises(RateLimitError):
                client.investment.get_etf_holdings(
                    symbol="SPY", holdings_date=date(2024, 1, 15)
                )
        client.close()
