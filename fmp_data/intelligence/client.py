# fmp_data/intelligence/client.py
from datetime import date

from fmp_data.base import EndpointGroup
from fmp_data.intelligence.endpoints import (
    ANALYST_ESTIMATES,
    ANALYST_RECOMMENDATIONS,
    CRYPTO_NEWS_ENDPOINT,
    DIVIDENDS_CALENDAR,
    EARNINGS_CALENDAR,
    EARNINGS_CONFIRMED,
    EARNINGS_SURPRISES,
    FMP_ARTICLES_ENDPOINT,
    FOREX_NEWS_ENDPOINT,
    GENERAL_NEWS_ENDPOINT,
    HISTORICAL_EARNINGS,
    HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT,
    IPO_CALENDAR,
    PRESS_RELEASES_BY_SYMBOL_ENDPOINT,
    PRESS_RELEASES_ENDPOINT,
    PRICE_TARGET,
    PRICE_TARGET_CONSENSUS,
    PRICE_TARGET_SUMMARY,
    SOCIAL_SENTIMENT_CHANGES_ENDPOINT,
    STOCK_NEWS_ENDPOINT,
    STOCK_NEWS_SENTIMENTS_ENDPOINT,
    STOCK_SPLITS_CALENDAR,
    TRENDING_SOCIAL_SENTIMENT_ENDPOINT,
    UPGRADES_DOWNGRADES,
    UPGRADES_DOWNGRADES_CONSENSUS,
    IPOEvent,
)
from fmp_data.intelligence.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    FMPArticle,
    FMPArticlesResponse,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalSocialSentiment,
    PressRelease,
    PressReleaseBySymbol,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    SocialSentimentChanges,
    StockNewsArticle,
    StockNewsSentiment,
    StockSplitEvent,
    TrendingSocialSentiment,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)


class MarketIntelligenceClient(EndpointGroup):
    """Client for market intelligence endpoints"""

    def get_price_target(self, symbol: str) -> list[PriceTarget]:
        """Get price targets"""
        return self.client.request(PRICE_TARGET, symbol=symbol)

    def get_price_target_summary(self, symbol: str) -> PriceTargetSummary:
        """Get price target summary"""
        result = self.client.request(PRICE_TARGET_SUMMARY, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_price_target_consensus(self, symbol: str) -> PriceTargetConsensus:
        """Get price target consensus"""
        result = self.client.request(PRICE_TARGET_CONSENSUS, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_analyst_estimates(self, symbol: str) -> list[AnalystEstimate]:
        """Get analyst estimates"""
        return self.client.request(ANALYST_ESTIMATES, symbol=symbol)

    def get_analyst_recommendations(self, symbol: str) -> list[AnalystRecommendation]:
        """Get analyst recommendations"""
        return self.client.request(ANALYST_RECOMMENDATIONS, symbol=symbol)

    def get_upgrades_downgrades(self, symbol: str) -> list[UpgradeDowngrade]:
        """Get upgrades and downgrades"""
        return self.client.request(UPGRADES_DOWNGRADES, symbol=symbol)

    def get_upgrades_downgrades_consensus(
        self, symbol: str
    ) -> UpgradeDowngradeConsensus:
        """Get upgrades and downgrades consensus"""
        result = self.client.request(UPGRADES_DOWNGRADES_CONSENSUS, symbol=symbol)
        return result[0] if isinstance(result, list) else result

    def get_earnings_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[EarningEvent]:
        """Get earnings calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(EARNINGS_CALENDAR, **params)

    def get_historical_earnings(self, symbol: str) -> list[EarningEvent]:
        """Get historical earnings"""
        return self.client.request(HISTORICAL_EARNINGS, symbol=symbol)

    def get_earnings_confirmed(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EarningConfirmed]:
        """Get confirmed earnings dates"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(EARNINGS_CONFIRMED, **params)

    def get_earnings_surprises(self, symbol: str) -> list[EarningSurprise]:
        """Get earnings surprises"""
        return self.client.request(EARNINGS_SURPRISES, symbol=symbol)

    def get_dividends_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[DividendEvent]:
        """Get dividends calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(DIVIDENDS_CALENDAR, **params)

    def get_stock_splits_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[StockSplitEvent]:
        """Get stock splits calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(STOCK_SPLITS_CALENDAR, **params)

    def get_ipo_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[IPOEvent]:
        """Get IPO calendar"""
        params = {}
        if start_date:
            params["from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["to"] = end_date.strftime("%Y-%m-%d")

        return self.client.request(IPO_CALENDAR, **params)

    def get_fmp_articles(self, page: int = 0, size: int = 5) -> list[FMPArticle]:
        """Get a list of the latest FMP articles

        Args:
            page: Page number to fetch (default: 0)
            size: Number of articles per page (default: 5)

        Returns:
            list[FMPArticle]: List of FMP articles from the content array
        """
        params = {
            "page": page,
            "size": size,
        }
        response = self.client.request(FMP_ARTICLES_ENDPOINT, **params)
        # Extract articles from the content array in the response
        return (
            response.content if isinstance(response, FMPArticlesResponse) else response
        )

    def get_general_news(self, page: int = 0) -> list[GeneralNewsArticle]:
        """Get a list of the latest general news articles"""
        params = {
            "page": page,
        }
        return self.client.request(GENERAL_NEWS_ENDPOINT, **params)

    def get_stock_news(
        self,
        tickers: str,
        page: int | None | None = 0,
        from_date: date | None | None = None,
        to_date: date | None | None = None,
        limit: int = 50,
    ) -> list[StockNewsArticle]:
        """Get a list of the latest stock news articles"""
        params = {
            "tickers": tickers,
            "page": page,
            "from": from_date.strftime("%Y-%m-%d") if from_date else None,
            "to": to_date.strftime("%Y-%m-%d") if to_date else None,
            "limit": limit,
        }
        return self.client.request(STOCK_NEWS_ENDPOINT, **params)

    def get_stock_news_sentiments(self, page: int = 0) -> list[StockNewsSentiment]:
        """Get a list of the latest stock news articles with sentiment analysis"""
        params = {
            "page": page,
        }
        return self.client.request(STOCK_NEWS_SENTIMENTS_ENDPOINT, **params)

    def get_forex_news(
        self,
        page: int | None = 0,
        symbol: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int | None = 50,
    ) -> list[ForexNewsArticle]:
        """Get a list of the latest forex news articles"""
        params = {
            "page": page,
            "symbol": symbol,
            "from": from_date.strftime("%Y-%m-%d") if from_date else None,
            "to": to_date.strftime("%Y-%m-%d") if to_date else None,
            "limit": limit,
        }
        return self.client.request(FOREX_NEWS_ENDPOINT, **params)

    def get_crypto_news(
        self,
        page: int = 0,
        symbol: str | None | None = None,
        from_date: date | None | None = None,
        to_date: date | None | None = None,
        limit: int = 50,
    ) -> list[CryptoNewsArticle]:
        """Get a list of the latest crypto news articles"""
        params = {
            "page": page,
            "symbol": symbol,
            "from": from_date.strftime("%Y-%m-%d") if from_date else None,
            "to": to_date.strftime("%Y-%m-%d") if to_date else None,
            "limit": limit,
        }
        return self.client.request(CRYPTO_NEWS_ENDPOINT, **params)

    def get_press_releases(self, page: int = 0) -> list[PressRelease]:
        """Get a list of the latest press releases"""
        params = {
            "page": page,
        }
        return self.client.request(PRESS_RELEASES_ENDPOINT, **params)

    def get_press_releases_by_symbol(
        self, symbol: str, page: int = 0
    ) -> list[PressReleaseBySymbol]:
        """Get a list of the latest press releases for a specific company"""
        params = {
            "symbol": symbol,
            "page": page,
        }
        return self.client.request(PRESS_RELEASES_BY_SYMBOL_ENDPOINT, **params)

    def get_historical_social_sentiment(
        self, symbol: str, page: int = 0
    ) -> list[HistoricalSocialSentiment]:
        """Get historical social sentiment data"""
        params = {
            "symbol": symbol,
            "page": page,
        }
        return self.client.request(HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT, **params)

    def get_trending_social_sentiment(
        self, type: str, source: str
    ) -> list[TrendingSocialSentiment]:
        """Get trending social sentiment data"""
        params = {
            "type": type,
            "source": source,
        }
        return self.client.request(TRENDING_SOCIAL_SENTIMENT_ENDPOINT, **params)

    def get_social_sentiment_changes(
        self, type: str, source: str
    ) -> list[SocialSentimentChanges]:
        """Get changes in social sentiment data"""
        params = {
            "type": type,
            "source": source,
        }
        return self.client.request(SOCIAL_SENTIMENT_CHANGES_ENDPOINT, **params)
