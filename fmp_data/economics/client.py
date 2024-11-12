# fmp_data/economics/client.py
from datetime import date

from fmp_data.base import EndpointGroup
from fmp_data.economics.endpoints import (
    ECONOMIC_CALENDAR,
    ECONOMIC_INDICATORS,
    MARKET_RISK_PREMIUM,
    TREASURY_RATES,
)
from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)


class EconomicsClient(EndpointGroup):
    """Client for economics data endpoints"""

    def get_treasury_rates(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[TreasuryRate]:
        """Get treasury rates"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(TREASURY_RATES, **params)

    def get_economic_indicators(self, indicator_name: str) -> list[EconomicIndicator]:
        """Get economic indicator data"""
        return self.client.request(ECONOMIC_INDICATORS, name=indicator_name)

    def get_economic_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[EconomicEvent]:
        """Get economic calendar events"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(ECONOMIC_CALENDAR, **params)

    def get_market_risk_premium(self) -> list[MarketRiskPremium]:
        """Get market risk premium data"""
        return self.client.request(MARKET_RISK_PREMIUM)
