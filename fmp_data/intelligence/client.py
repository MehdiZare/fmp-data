# fmp_data/intelligence/client.py
from datetime import date

from fmp_data.base import EndpointGroup

from . import endpoints, models


class MarketIntelligenceClient(EndpointGroup):
    """Client for market intelligence endpoints"""

    def get_price_target(self, symbol: str) -> list[models.PriceTarget]:
        """Get price targets"""
        return self.client.request(endpoints.PRICE_TARGET, symbol=symbol)

    def get_price_target_summary(self, symbol: str) -> models.PriceTargetSummary:
        """Get price target summary"""
        result = self.client.request(endpoints.PRICE_TARGET_SUMMARY, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_price_target_consensus(self, symbol: str) -> models.PriceTargetConsensus:
        """Get price target consensus"""
        result = self.client.request(endpoints.PRICE_TARGET_CONSENSUS, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_analyst_estimates(self, symbol: str) -> list[models.AnalystEstimate]:
        """Get analyst estimates"""
        return self.client.request(endpoints.ANALYST_ESTIMATES, symbol=symbol)

    def get_analyst_recommendations(
        self, symbol: str
    ) -> list[models.AnalystRecommendation]:
        """Get analyst recommendations"""
        return self.client.request(endpoints.ANALYST_RECOMMENDATIONS, symbol=symbol)

    def get_upgrades_downgrades(self, symbol: str) -> list[models.UpgradeDowngrade]:
        """Get upgrades and downgrades"""
        return self.client.request(endpoints.UPGRADES_DOWNGRADES, symbol=symbol)

    def get_upgrades_downgrades_consensus(
        self, symbol: str
    ) -> models.UpgradeDowngradeConsensus:
        """Get upgrades and downgrades consensus"""
        result = self.client.request(
            endpoints.UPGRADES_DOWNGRADES_CONSENSUS, symbol=symbol
        )
        return result[0] if isinstance(result, list) else result

    def get_earnings_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[models.EarningEvent]:
        """Get earnings calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(endpoints.EARNINGS_CALENDAR, **params)

    def get_historical_earnings(self, symbol: str) -> list[models.EarningEvent]:
        """Get historical earnings"""
        return self.client.request(endpoints.HISTORICAL_EARNINGS, symbol=symbol)

    def get_earnings_confirmed(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[models.EarningConfirmed]:
        """Get confirmed earnings dates"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(endpoints.EARNINGS_CONFIRMED, **params)

    def get_earnings_surprises(self, symbol: str) -> list[models.EarningSurprise]:
        """Get earnings surprises"""
        return self.client.request(endpoints.EARNINGS_SURPRISES, symbol=symbol)

    def get_dividends_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[models.DividendEvent]:
        """Get dividends calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(endpoints.DIVIDENDS_CALENDAR, **params)

    def get_stock_splits_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[models.StockSplitEvent]:
        """Get stock splits calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(endpoints.STOCK_SPLITS_CALENDAR, **params)

    def get_ipo_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[models.IPOEvent]:
        """Get IPO calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(endpoints.IPO_CALENDAR, **params)
