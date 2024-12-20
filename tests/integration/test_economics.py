import logging
import time
from datetime import date, datetime, timedelta

from fmp_data import FMPDataClient
from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.exceptions import RateLimitError

logger = logging.getLogger(__name__)


class TestEconomicsEndpoints:
    """Test economics endpoints"""

    def _handle_rate_limit(self, func, *args, **kwargs):
        """Helper to handle rate limiting"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(e.retry_after or 1)
                continue

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
                    assert isinstance(event, EconomicEvent)
                    assert event.event
                    assert isinstance(event.event_date, datetime)
                    assert hasattr(event, "country")  # May be empty string
                    assert isinstance(event.change_percent, float)

    def test_get_market_risk_premium(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting market risk premium data"""
        with vcr_instance.use_cassette("economics/market_risk_premium.yaml"):
            premiums = self._handle_rate_limit(
                fmp_client.economics.get_market_risk_premium
            )

            assert isinstance(premiums, list)
            assert len(premiums) > 0

            # Test specific example from response
            example = next(p for p in premiums if p.country == "Abu Dhabi")
            assert example.continent == "Asia"
            assert example.country_risk_premium == 0.72
            assert example.total_equity_risk_premium == 5.32

            # Test general structure
            for premium in premiums:
                assert isinstance(premium, MarketRiskPremium)
                assert isinstance(premium.country, str)
                assert premium.continent is None or isinstance(premium.continent, str)
                # Allow for None or float values
                assert premium.country_risk_premium is None or isinstance(
                    premium.country_risk_premium, float
                )
                assert premium.total_equity_risk_premium is None or isinstance(
                    premium.total_equity_risk_premium, float
                )

    def test_error_handling(self, fmp_client: FMPDataClient, vcr_instance):
        """Test error handling for invalid inputs"""
        with vcr_instance.use_cassette("economics/error_handling.yaml"):
            # Test with invalid indicator - should return empty list
            result = fmp_client.economics.get_economic_indicators("INVALID_INDICATOR")
            assert isinstance(result, list)
            assert len(result) == 0

    def test_rate_limiting(self, fmp_client: FMPDataClient, vcr_instance):
        """Test rate limiting with simple successful request"""
        with vcr_instance.use_cassette("economics/rate_limit.yaml"):
            rates = self._handle_rate_limit(
                fmp_client.economics.get_treasury_rates,
                start_date=date.today() - timedelta(days=7),
                end_date=date.today(),
            )
            assert isinstance(rates, list)
