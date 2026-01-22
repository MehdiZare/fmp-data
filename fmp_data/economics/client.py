# fmp_data/economics/client.py
from datetime import date

from fmp_data.base import EndpointGroup
from fmp_data.economics.endpoints import (
    COMMITMENT_OF_TRADERS_ANALYSIS,
    COMMITMENT_OF_TRADERS_LIST,
    COMMITMENT_OF_TRADERS_REPORT,
    ECONOMIC_CALENDAR,
    ECONOMIC_INDICATORS,
    MARKET_RISK_PREMIUM,
    TREASURY_RATES,
)
from fmp_data.economics.models import (
    CommitmentOfTradersAnalysis,
    CommitmentOfTradersListItem,
    CommitmentOfTradersReport,
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
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(TREASURY_RATES, **params)

    def get_economic_indicators(self, indicator_name: str) -> list[EconomicIndicator]:
        """Get economic indicator data"""
        return self.client.request(ECONOMIC_INDICATORS, name=indicator_name)

    def get_economic_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[EconomicEvent]:
        """Get economic calendar events"""
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(ECONOMIC_CALENDAR, **params)

    def get_market_risk_premium(self) -> list[MarketRiskPremium]:
        """Get market risk premium data"""
        return self.client.request(MARKET_RISK_PREMIUM)

    def get_commitment_of_traders_report(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[CommitmentOfTradersReport]:
        """Get Commitment of Traders (COT) report data"""
        params = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        return self.client.request(COMMITMENT_OF_TRADERS_REPORT, **params)

    def get_commitment_of_traders_analysis(
        self, symbol: str, start_date: date, end_date: date
    ) -> list[CommitmentOfTradersAnalysis]:
        """Get Commitment of Traders (COT) analysis data"""
        params = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        return self.client.request(COMMITMENT_OF_TRADERS_ANALYSIS, **params)

    def get_commitment_of_traders_list(self) -> list[CommitmentOfTradersListItem]:
        """Get list of available Commitment of Traders (COT) symbols"""
        return self.client.request(COMMITMENT_OF_TRADERS_LIST)
