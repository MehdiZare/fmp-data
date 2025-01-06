# fmp_data/intelligence/client.py
from datetime import date
from typing import cast

from fmp_data.base import EndpointGroup
from fmp_data.intelligence.endpoints import (
    CROWDFUNDING_BY_CIK,
    CROWDFUNDING_RSS,
    CROWDFUNDING_SEARCH,
    CRYPTO_NEWS_ENDPOINT,
    DIVIDENDS_CALENDAR,
    EARNINGS_CALENDAR,
    EARNINGS_CONFIRMED,
    EARNINGS_SURPRISES,
    EQUITY_OFFERING_BY_CIK,
    EQUITY_OFFERING_RSS,
    EQUITY_OFFERING_SEARCH,
    ESG_BENCHMARK,
    ESG_DATA,
    ESG_RATINGS,
    FMP_ARTICLES_ENDPOINT,
    FOREX_NEWS_ENDPOINT,
    GENERAL_NEWS_ENDPOINT,
    HISTORICAL_EARNINGS,
    HISTORICAL_SOCIAL_SENTIMENT_ENDPOINT,
    HOUSE_DISCLOSURE,
    HOUSE_DISCLOSURE_RSS,
    IPO_CALENDAR,
    PRESS_RELEASES_BY_SYMBOL_ENDPOINT,
    PRESS_RELEASES_ENDPOINT,
    SENATE_TRADING,
    SENATE_TRADING_RSS,
    SOCIAL_SENTIMENT_CHANGES_ENDPOINT,
    STOCK_NEWS_ENDPOINT,
    STOCK_NEWS_SENTIMENTS_ENDPOINT,
    STOCK_SPLITS_CALENDAR,
    TRENDING_SOCIAL_SENTIMENT_ENDPOINT,
    IPOEvent,
)
from fmp_data.intelligence.models import (
    CrowdfundingOffering,
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    EquityOffering,
    ESGBenchmark,
    ESGData,
    ESGRating,
    FMPArticle,
    FMPArticlesResponse,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalSocialSentiment,
    HouseDisclosure,
    PressRelease,
    PressReleaseBySymbol,
    SenateTrade,
    SocialSentimentChanges,
    StockNewsArticle,
    StockNewsSentiment,
    StockSplitEvent,
    TrendingSocialSentiment,
)


class MarketIntelligenceClient(EndpointGroup):
    """Client for market intelligence endpoints"""

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

    # ESG methods
    def get_esg_data(self, symbol: str) -> ESGData:
        """Get ESG data for a company"""
        result = self.client.request(ESG_DATA, symbol=symbol)
        return cast(ESGData, result[0] if isinstance(result, list) else result)

    def get_esg_ratings(self, symbol: str) -> ESGRating:
        """Get ESG ratings for a company"""
        result = self.client.request(ESG_RATINGS, symbol=symbol)
        return cast(ESGRating, result[0] if isinstance(result, list) else result)

    def get_esg_benchmark(self, year: int) -> list[ESGBenchmark]:
        """Get ESG sector benchmark data"""
        return self.client.request(ESG_BENCHMARK, year=year)

    # Government trading methods
    def get_senate_trading(self, symbol: str) -> list[SenateTrade]:
        """Get Senate trading data"""
        return self.client.request(SENATE_TRADING, symbol=symbol)

    def get_senate_trading_rss(self, page: int = 0) -> list[SenateTrade]:
        """Get Senate trading RSS feed"""
        return self.client.request(SENATE_TRADING_RSS, page=page)

    def get_house_disclosure(self, symbol: str) -> list[HouseDisclosure]:
        """Get House disclosure data"""
        return self.client.request(HOUSE_DISCLOSURE, symbol=symbol)

    def get_house_disclosure_rss(self, page: int = 0) -> list[HouseDisclosure]:
        """Get House disclosure RSS feed"""
        return self.client.request(HOUSE_DISCLOSURE_RSS, page=page)

    # Fundraising methods
    def get_crowdfunding_rss(self, page: int = 0) -> list[CrowdfundingOffering]:
        """Get crowdfunding offerings RSS feed"""
        return self.client.request(CROWDFUNDING_RSS, page=page)

    def search_crowdfunding(self, name: str) -> list[CrowdfundingOffering]:
        """Search crowdfunding offerings"""
        return self.client.request(CROWDFUNDING_SEARCH, name=name)

    def get_crowdfunding_by_cik(self, cik: str) -> list[CrowdfundingOffering]:
        """Get crowdfunding offerings by CIK"""
        return self.client.request(CROWDFUNDING_BY_CIK, cik=cik)

    def get_equity_offering_rss(self, page: int = 0) -> list[EquityOffering]:
        """Get equity offering RSS feed"""
        return self.client.request(EQUITY_OFFERING_RSS, page=page)

    def search_equity_offering(self, name: str) -> list[EquityOffering]:
        """Search equity offerings"""
        return self.client.request(EQUITY_OFFERING_SEARCH, name=name)

    def get_equity_offering_by_cik(self, cik: str) -> list[EquityOffering]:
        """Get equity offerings by CIK"""
        return self.client.request(EQUITY_OFFERING_BY_CIK, cik=cik)
