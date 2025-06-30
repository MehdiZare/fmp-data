import logging
from datetime import date, datetime, timedelta

import pytest

from fmp_data import FMPDataClient
from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.economics.schema import EconomicIndicatorType

from .base import BaseTestCase

logger = logging.getLogger(__name__)


class TestEconomicsEndpoints(BaseTestCase):
    """Test economics endpoints"""

    def test_get_treasury_rates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting treasury rates"""
        with vcr_instance.use_cassette("economics/treasury_rates.yaml"):
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            rates = self._handle_rate_limit(
                fmp_client.economics.get_treasury_rates,
                start_date=start_date,
                end_date=end_date,
            )

            assert isinstance(rates, list)
            assert len(rates) > 0

            for rate in rates:
                assert isinstance(rate, TreasuryRate)
                assert isinstance(rate.rate_date, date)
                assert hasattr(rate, "month_1")
                assert hasattr(rate, "year_10")

    def test_get_economic_indicators(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting economic indicators"""
        with vcr_instance.use_cassette("economics/indicator_gdp.yaml"):
            # Test with GDP indicator
            indicators = self._handle_rate_limit(
                fmp_client.economics.get_economic_indicators, indicator_name="GDP"
            )

            assert isinstance(indicators, list)
            assert len(indicators) > 0

            for indicator in indicators:
                assert isinstance(indicator, EconomicIndicator)
                assert isinstance(indicator.value, float)
                assert isinstance(indicator.indicator_date, date)

    def test_get_economic_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting economic calendar events"""
        with vcr_instance.use_cassette("economics/economic_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = self._handle_rate_limit(
                fmp_client.economics.get_economic_calendar,
                start_date=start_date,
                end_date=end_date,
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(
                        event, EconomicEvent
                    ), "event is not EconomicEvent"
                    assert event.event, "event is empty string"
                    assert isinstance(
                        event.event_date, datetime
                    ), "event_date is not datetime"
                    assert hasattr(event, "country"), "country is missing"
                    assert (
                        isinstance(event.change_percent, float)
                        if event.change_percent is not None
                        else True
                    ), "change_percent is not float"

    def test_get_market_risk_premium(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market risk premium data"""
        with vcr_instance.use_cassette("economics/market_risk_premium.yaml"):
            premiums = self._handle_rate_limit(
                fmp_client.economics.get_market_risk_premium
            )

            assert isinstance(premiums, list)
            assert len(premiums) > 0

            # Test specific example from response
            example = next(p for p in premiums if p.country == "Germany")
            assert isinstance(example.continent, str), "continent is not string"
            assert isinstance(
                example.country_risk_premium, float
            ), "country_risk_premium is not float"
            assert isinstance(
                example.total_equity_risk_premium, float
            ), "total_equity_risk_premium is not float"

            # Test general structure
            for premium in premiums:
                assert isinstance(
                    premium, MarketRiskPremium
                ), "premium is not MarketRiskPremium"
                assert isinstance(premium.country, str), "country is not string"
                assert premium.continent is None or isinstance(
                    premium.continent, str
                ), "continent is not string"
                # Allow for None or float values
                assert premium.country_risk_premium is None or isinstance(
                    premium.country_risk_premium, float
                ), "country_risk_premium is not float"
                assert premium.total_equity_risk_premium is None or isinstance(
                    premium.total_equity_risk_premium, float
                ), "total_equity_risk_premium is not float"

    def test_error_handling(self, fmp_client: FMPDataClient, vcr_instance):
        """Test error handling for invalid inputs"""
        with vcr_instance.use_cassette("economics/error_handling.yaml"):
            # Test with invalid indicator - should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                # Use _handle_rate_limit but preserve the ValueError
                try:
                    self._handle_rate_limit(
                        fmp_client.economics.get_economic_indicators,
                        indicator_name="INVALID_INDICATOR",
                    )
                except ValueError as e:
                    # Re-raise ValueError to be caught by pytest.raises
                    raise ValueError(str(e)) from e

            error_msg = str(exc_info.value)
            assert "Invalid value for name" in error_msg
            assert "Must be one of:" in error_msg

            # Verify the error includes all enum values
            for indicator in EconomicIndicatorType:
                assert str(indicator) in error_msg

    def test_rate_limiting(self, fmp_client: FMPDataClient, vcr_instance):
        """Test rate limiting with simple successful request"""
        with vcr_instance.use_cassette("economics/rate_limit.yaml"):
            rates = self._handle_rate_limit(
                fmp_client.economics.get_treasury_rates,
                start_date=date.today() - timedelta(days=7),
                end_date=date.today(),
            )
            assert isinstance(rates, list)
