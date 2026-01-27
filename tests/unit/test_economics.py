from datetime import date, datetime
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from fmp_data.economics.models import (
    CommitmentOfTradersAnalysis,
    CommitmentOfTradersListItem,
    CommitmentOfTradersReport,
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.economics.schema import EconomicIndicatorType


# Test data moved to class-level fixtures
class TestTreasuryRate:
    """Tests for TreasuryRate model and related client functionality"""

    @pytest.fixture
    def treasury_rate_data(self):
        """Mock treasury rate data with all possible fields"""
        return {
            "date": "2024-01-05",
            "month1": 5.25,
            "month2": 5.35,
            "month3": 5.45,
            "month6": 5.55,
            "year1": 5.65,
            "year2": 5.75,
            "year3": 5.85,
            "year5": 5.95,
            "year7": 6.05,
            "year10": 6.15,
            "year20": 6.25,
            "year30": 6.35,
        }

    def test_model_validation_minimal(self):
        """Test TreasuryRate model with minimal required fields"""
        data = {"date": "2024-01-05"}
        rate = TreasuryRate.model_validate(data)
        assert rate.rate_date == date(2024, 1, 5)
        assert all(
            getattr(rate, f) is None
            for f in [
                "month_1",
                "month_2",
                "month_3",
                "month_6",
                "year_1",
                "year_2",
                "year_3",
                "year_5",
                "year_7",
                "year_10",
                "year_20",
                "year_30",
            ]
        )

    def test_model_validation_complete(self, treasury_rate_data):
        """Test TreasuryRate model with all fields"""
        rate = TreasuryRate.model_validate(treasury_rate_data)
        assert rate.rate_date == date(2024, 1, 5)
        assert rate.month_1 == 5.25
        assert rate.year_30 == 6.35

    def test_model_validation_invalid_date(self):
        """Test TreasuryRate model with invalid date"""
        with pytest.raises(ValidationError):
            TreasuryRate.model_validate({"date": "invalid-date"})

    @patch("httpx.Client.request")
    def test_get_treasury_rates(
        self, mock_request, fmp_client, mock_response, treasury_rate_data
    ):
        """Test getting treasury rates through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[treasury_rate_data]
        )

        rates = fmp_client.economics.get_treasury_rates(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 5)
        )

        assert len(rates) == 1
        rate = rates[0]
        assert isinstance(rate, TreasuryRate)
        assert rate.rate_date == date(2024, 1, 5)
        assert rate.month_1 == 5.25
        assert rate.year_30 == 6.35


class TestEconomicIndicator:
    """Tests for EconomicIndicator model and related client functionality"""

    @pytest.fixture
    def indicator_data(self):
        """Mock economic indicator data"""
        return {
            "date": "2024-01-05",
            "value": 24000.5,
            "name": "GDP",
        }

    def test_model_validation_minimal(self):
        """Test EconomicIndicator model with minimal required fields"""
        data = {
            "date": "2024-01-05",
            "value": 100.0,
        }
        indicator = EconomicIndicator.model_validate(data)
        assert indicator.indicator_date == date(2024, 1, 5)
        assert indicator.value == 100.0
        assert indicator.name is None

    def test_model_validation_complete(self, indicator_data):
        """Test EconomicIndicator model with all fields"""
        indicator = EconomicIndicator.model_validate(indicator_data)
        assert indicator.indicator_date == date(2024, 1, 5)
        assert indicator.value == 24000.5
        assert indicator.name == "GDP"

    @patch("httpx.Client.request")
    def test_get_economic_indicators(
        self, mock_request, fmp_client, mock_response, indicator_data
    ):
        """Test getting economic indicators through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[indicator_data]
        )

        # Use EconomicIndicatorType.GDP.value instead of "GDP"
        indicators = fmp_client.economics.get_economic_indicators(
            EconomicIndicatorType.GDP.value
        )
        assert len(indicators) == 1
        indicator = indicators[0]
        assert isinstance(indicator, EconomicIndicator)
        assert indicator.value == 24000.5
        assert indicator.name == "GDP"


class TestEconomicEvent:
    """Tests for EconomicEvent model and related client functionality"""

    @pytest.fixture
    def event_data(self):
        """Mock economic calendar event with all fields"""
        return {
            "event": "GDP Release",
            "date": "2024-01-05T08:30:00",
            "country": "US",
            "currency": "USD",
            "actual": 2.5,
            "previous": 2.3,
            "estimate": 2.4,
            "change": 0.2,
            "changePercentage": 8.7,
            "impact": "High",
        }

    def test_model_validation_minimal(self):
        """Test EconomicEvent model with minimal required fields"""
        data = {
            "event": "Test Event",
            "date": "2024-01-05T08:30:00",
        }
        event = EconomicEvent.model_validate(data)
        assert event.event == "Test Event"
        assert event.event_date == datetime(2024, 1, 5, 8, 30)
        assert event.country is None
        assert event.change_percent is None

    def test_model_validation_complete(self, event_data):
        """Test EconomicEvent model with all fields"""
        event = EconomicEvent.model_validate(event_data)
        assert event.event == "GDP Release"
        assert event.event_date == datetime(2024, 1, 5, 8, 30)
        assert event.actual == 2.5
        assert event.impact == "High"

    def test_model_validation_invalid_event(self):
        """Test EconomicEvent model with missing required field"""
        with pytest.raises(ValidationError):
            EconomicEvent.model_validate({"date": "2024-01-05T08:30:00"})

    @patch("httpx.Client.request")
    def test_get_economic_calendar(
        self, mock_request, fmp_client, mock_response, event_data
    ):
        """Test getting economic calendar through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[event_data]
        )

        events = fmp_client.economics.get_economic_calendar(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 5)
        )
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, EconomicEvent)
        assert event.event == "GDP Release"
        assert event.change_percent == 8.7


class TestMarketRiskPremium:
    """Tests for MarketRiskPremium model and related client functionality"""

    @pytest.fixture
    def risk_premium_data(self):
        """Mock market risk premium data"""
        return {
            "country": "United States",
            "continent": "North America",
            "countryRiskPremium": 0.5,
            "totalEquityRiskPremium": 5.5,
        }

    def test_model_validation_minimal(self):
        """Test MarketRiskPremium model with minimal required fields"""
        data = {"country": "United States"}
        premium = MarketRiskPremium.model_validate(data)
        assert premium.country == "United States"
        assert premium.continent is None
        assert premium.country_risk_premium is None
        assert premium.total_equity_risk_premium is None

    def test_model_validation_complete(self, risk_premium_data):
        """Test MarketRiskPremium model with all fields"""
        premium = MarketRiskPremium.model_validate(risk_premium_data)
        assert premium.country == "United States"
        assert premium.continent == "North America"
        assert premium.country_risk_premium == 0.5
        assert premium.total_equity_risk_premium == 5.5

    @patch("httpx.Client.request")
    def test_get_market_risk_premium(
        self, mock_request, fmp_client, mock_response, risk_premium_data
    ):
        """Test getting market risk premium through client"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[risk_premium_data]
        )

        premiums = fmp_client.economics.get_market_risk_premium()
        assert len(premiums) == 1
        premium = premiums[0]
        assert isinstance(premium, MarketRiskPremium)
        assert premium.country == "United States"
        assert premium.total_equity_risk_premium == 5.5


class TestCommitmentOfTraders:
    """Tests for Commitment of Traders endpoints"""

    @pytest.fixture
    def cot_report_data(self):
        return {
            "symbol": "KC",
            "date": "2024-02-27 00:00:00",
            "name": "Coffee (KC)",
            "sector": "SOFTS",
            "marketAndExchangeNames": "COFFEE C - ICE FUTURES U.S.",
            "openInterestAll": 209453,
            "noncommPositionsLongAll": 75330,
            "noncommPositionsShortAll": 23630,
            "commPositionsLongAll": 79690,
            "commPositionsShortAll": 132114,
            "contractUnits": "(CONTRACTS OF 37,500 POUNDS)",
        }

    @pytest.fixture
    def cot_analysis_data(self):
        return {
            "symbol": "B6",
            "date": "2024-02-27 00:00:00",
            "name": "British Pound (B6)",
            "sector": "CURRENCIES",
            "exchange": "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
            "currentLongMarketSituation": 66.85,
            "currentShortMarketSituation": 33.15,
            "marketSituation": "Bullish",
            "previousLongMarketSituation": 67.97,
            "previousShortMarketSituation": 32.03,
            "previousMarketSituation": "Bullish",
            "netPostion": 46358,
            "previousNetPosition": 46312,
            "changeInNetPosition": 0.1,
            "marketSentiment": "Increasing Bullish",
            "reversalTrend": False,
        }

    @pytest.fixture
    def cot_list_data(self):
        return {"symbol": "NG", "name": "Natural Gas (NG)"}

    def test_cot_report_model(self, cot_report_data):
        report = CommitmentOfTradersReport.model_validate(cot_report_data)
        assert report.symbol == "KC"
        assert report.sector == "SOFTS"
        assert report.open_interest_all == 209453

    def test_cot_analysis_model(self, cot_analysis_data):
        analysis = CommitmentOfTradersAnalysis.model_validate(cot_analysis_data)
        assert analysis.symbol == "B6"
        assert analysis.market_situation == "Bullish"
        assert analysis.net_position == 46358

    def test_cot_list_model(self, cot_list_data):
        item = CommitmentOfTradersListItem.model_validate(cot_list_data)
        assert item.symbol == "NG"
        assert item.name == "Natural Gas (NG)"

    @patch("httpx.Client.request")
    def test_get_commitment_of_traders_report(
        self, mock_request, fmp_client, mock_response, cot_report_data
    ):
        mock_request.return_value = mock_response(
            status_code=200, json_data=[cot_report_data]
        )

        reports = fmp_client.economics.get_commitment_of_traders_report(
            "KC", date(2024, 1, 1), date(2024, 3, 1)
        )

        assert isinstance(reports, list)
        assert isinstance(reports[0], CommitmentOfTradersReport)
        params = mock_request.call_args[1]["params"]
        assert params["symbol"] == "KC"
        assert params["from"] == date(2024, 1, 1)
        assert params["to"] == date(2024, 3, 1)

    @patch("httpx.Client.request")
    def test_get_commitment_of_traders_analysis(
        self, mock_request, fmp_client, mock_response, cot_analysis_data
    ):
        mock_request.return_value = mock_response(
            status_code=200, json_data=[cot_analysis_data]
        )

        analysis = fmp_client.economics.get_commitment_of_traders_analysis(
            "B6", date(2024, 1, 1), date(2024, 3, 1)
        )

        assert isinstance(analysis, list)
        assert isinstance(analysis[0], CommitmentOfTradersAnalysis)
        params = mock_request.call_args[1]["params"]
        assert params["symbol"] == "B6"
        assert params["from"] == date(2024, 1, 1)
        assert params["to"] == date(2024, 3, 1)

    @patch("httpx.Client.request")
    def test_get_commitment_of_traders_list(
        self, mock_request, fmp_client, mock_response, cot_list_data
    ):
        mock_request.return_value = mock_response(
            status_code=200, json_data=[cot_list_data]
        )

        items = fmp_client.economics.get_commitment_of_traders_list()

        assert isinstance(items, list)
        assert isinstance(items[0], CommitmentOfTradersListItem)
