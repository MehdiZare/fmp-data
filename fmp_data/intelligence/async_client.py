# fmp_data/intelligence/async_client.py
"""Async client for market intelligence endpoints."""

from datetime import date

from fmp_data.base import AsyncEndpointGroup
from fmp_data.helpers import RemovedEndpointError, removed
from fmp_data.intelligence.endpoints import (
    CROWDFUNDING_BY_CIK,
    CROWDFUNDING_RSS,
    CROWDFUNDING_SEARCH,
    CRYPTO_NEWS_ENDPOINT,
    CRYPTO_SYMBOL_NEWS_ENDPOINT,
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
    FOREX_SYMBOL_NEWS_ENDPOINT,
    GENERAL_NEWS_ENDPOINT,
    GRADES,
    GRADES_CONSENSUS,
    GRADES_HISTORICAL,
    GRADES_LATEST_NEWS,
    GRADES_NEWS,
    HISTORICAL_EARNINGS,
    HOUSE_DISCLOSURE,
    HOUSE_LATEST,
    HOUSE_TRADES_BY_NAME,
    IPO_CALENDAR,
    PRESS_RELEASES_BY_SYMBOL_ENDPOINT,
    PRESS_RELEASES_ENDPOINT,
    PRICE_TARGET_LATEST_NEWS,
    PRICE_TARGET_NEWS,
    RATINGS_HISTORICAL,
    RATINGS_SNAPSHOT,
    SENATE_LATEST,
    SENATE_TRADES_BY_NAME,
    SENATE_TRADING,
    SENATE_TRADING_RSS,
    STOCK_NEWS_ENDPOINT,
    STOCK_SPLITS_CALENDAR,
    STOCK_SYMBOL_NEWS_ENDPOINT,
)
from fmp_data.intelligence.models import (
    CrowdfundingOffering,
    CrowdfundingOfferingSearchItem,
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    EquityOffering,
    EquityOfferingSearchItem,
    ESGBenchmark,
    ESGData,
    ESGRating,
    FMPArticle,
    FMPArticlesResponse,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalRating,
    HistoricalSocialSentiment,
    HistoricalStockGrade,
    HouseDisclosure,
    IPOEvent,
    PressRelease,
    PressReleaseBySymbol,
    PriceTargetNews,
    RatingsSnapshot,
    SenateTrade,
    SocialSentimentChanges,
    StockGrade,
    StockGradeNews,
    StockGradesConsensus,
    StockNewsArticle,
    StockNewsSentiment,
    StockSplitEvent,
    TrendingSocialSentiment,
)


class AsyncMarketIntelligenceClient(AsyncEndpointGroup):
    """Async client for market intelligence endpoints."""

    @staticmethod
    def _format_date(value: date | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")

    @staticmethod
    def _build_date_params(
        start_date: date | None = None,
        end_date: date | None = None,
        start_key: str = "start_date",
        end_key: str = "end_date",
    ) -> dict[str, str]:
        """Build date parameters dict from optional date values

        Args:
            start_date: Start date for the date range
            end_date: End date for the date range
            start_key: Parameter key for start date (default: 'start_date')
            end_key: Parameter key for end date (default: 'end_date')

        Returns:
            Dictionary with formatted date parameters
        """
        params: dict[str, str] = {}
        if start_date:
            formatted_start = AsyncMarketIntelligenceClient._format_date(start_date)
            if formatted_start is not None:
                params[start_key] = formatted_start
        if end_date:
            formatted_end = AsyncMarketIntelligenceClient._format_date(end_date)
            if formatted_end is not None:
                params[end_key] = formatted_end
        return params

    async def get_earnings_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[EarningEvent]:
        """Get earnings calendar"""
        params = self._build_date_params(start_date, end_date)
        return await self.client.request_async(EARNINGS_CALENDAR, **params)

    async def get_historical_earnings(self, symbol: str) -> list[EarningEvent]:
        """Get historical earnings"""
        return await self.client.request_async(HISTORICAL_EARNINGS, symbol=symbol)

    async def get_earnings_confirmed(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EarningConfirmed]:
        """Get confirmed earnings dates"""
        params = self._build_date_params(start_date, end_date)
        return await self.client.request_async(EARNINGS_CONFIRMED, **params)

    async def get_earnings_surprises(self, symbol: str) -> list[EarningSurprise]:
        """Get earnings surprises"""
        return await self.client.request_async(EARNINGS_SURPRISES, symbol=symbol)

    async def get_dividends_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[DividendEvent]:
        """Get dividends calendar"""
        params = self._build_date_params(start_date, end_date)
        return await self.client.request_async(DIVIDENDS_CALENDAR, **params)

    async def get_stock_splits_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[StockSplitEvent]:
        """Get stock splits calendar"""
        params = self._build_date_params(start_date, end_date)
        return await self.client.request_async(STOCK_SPLITS_CALENDAR, **params)

    async def get_ipo_calendar(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[IPOEvent]:
        """Get IPO calendar"""
        params = self._build_date_params(start_date, end_date)
        return await self.client.request_async(IPO_CALENDAR, **params)

    async def get_fmp_articles(
        self, page: int = 0, limit: int = 20, size: int | None = None
    ) -> list[FMPArticle]:
        """Get a list of the latest FMP articles

        Args:
            page: Page number to fetch (default: 0)
            limit: Number of articles per page (default: 20)
            size: Deprecated alias for limit (default: None)

        Returns:
            list[FMPArticle]: List of FMP articles from the content array
        """
        if size is not None:
            limit = size
        params = {
            "page": page,
            "limit": limit,
        }
        response = await self.client.request_async(FMP_ARTICLES_ENDPOINT, **params)
        # Extract articles from the content array in the response
        return (
            response.content if isinstance(response, FMPArticlesResponse) else response
        )

    async def get_general_news(
        self,
        page: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[GeneralNewsArticle]:
        """Get a list of the latest general news articles"""
        params = {
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(GENERAL_NEWS_ENDPOINT, **params)

    async def get_stock_symbol_news(
        self,
        symbol: str,
        page: int | None = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[StockNewsArticle]:
        """Get a list of the latest stock news articles"""
        params = {
            "symbol": symbol,
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(STOCK_SYMBOL_NEWS_ENDPOINT, **params)

    async def get_stock_news(
        self,
        symbol: str | None = None,
        page: int | None = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[StockNewsArticle]:
        """Get a list of the latest stock news articles"""
        if symbol:
            return await self.get_stock_symbol_news(
                symbol=symbol,
                page=page,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
            )
        params = {
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(STOCK_NEWS_ENDPOINT, **params)

    async def get_stock_news_sentiments(
        self, page: int = 0
    ) -> list[StockNewsSentiment]:
        """Get a list of the latest stock news articles with sentiment analysis

        .. deprecated::
            This endpoint is no longer available on the FMP API and will be removed
            in a future version. It currently returns an empty list.
        """
        import warnings

        warnings.warn(
            "get_stock_news_sentiments is deprecated and will be removed in a "
            "future version. The FMP API no longer supports this endpoint.",
            DeprecationWarning,
            stacklevel=2,
        )
        return []

    async def get_forex_news(
        self,
        page: int | None = 0,
        symbol: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int | None = 20,
    ) -> list[ForexNewsArticle]:
        """Get a list of the latest forex news articles (or search by symbol)"""
        if symbol:
            return await self.get_forex_symbol_news(
                symbol=symbol,
                page=page,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
            )
        params = {
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(FOREX_NEWS_ENDPOINT, **params)

    async def get_forex_symbol_news(
        self,
        symbol: str,
        page: int | None = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int | None = 20,
    ) -> list[ForexNewsArticle]:
        """Search forex news articles by symbol"""
        params = {
            "symbol": symbol,
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(FOREX_SYMBOL_NEWS_ENDPOINT, **params)

    async def get_crypto_news(
        self,
        page: int = 0,
        symbol: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[CryptoNewsArticle]:
        """Get a list of the latest crypto news articles (or search by symbol)"""
        if from_date and to_date is None:
            to_date = date.today()
        if symbol:
            return await self.get_crypto_symbol_news(
                symbol=symbol,
                page=page,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
            )
        params = {
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(CRYPTO_NEWS_ENDPOINT, **params)

    async def get_crypto_symbol_news(
        self,
        symbol: str,
        page: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[CryptoNewsArticle]:
        """Search crypto news articles by symbol"""
        params = {
            "symbol": symbol,
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(CRYPTO_SYMBOL_NEWS_ENDPOINT, **params)

    async def get_press_releases(
        self,
        page: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[PressRelease]:
        """Get a list of the latest press releases"""
        params = {
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(PRESS_RELEASES_ENDPOINT, **params)

    async def get_press_releases_by_symbol(
        self,
        symbol: str,
        page: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
    ) -> list[PressReleaseBySymbol]:
        """Get a list of the latest press releases for a specific company"""
        params = {
            "symbol": symbol,
            "page": page,
            "start_date": self._format_date(from_date),
            "end_date": self._format_date(to_date),
            "limit": limit,
        }
        return await self.client.request_async(
            PRESS_RELEASES_BY_SYMBOL_ENDPOINT, **params
        )

    @removed("Social sentiment endpoints were discontinued by FMP.")
    async def get_historical_social_sentiment(
        self, symbol: str, page: int = 0
    ) -> list[HistoricalSocialSentiment]:
        """Get historical social sentiment data (REMOVED)"""
        raise RemovedEndpointError(
            "get_historical_social_sentiment",
            "Social sentiment endpoints were discontinued by FMP.",
        )  # pragma: no cover

    @removed("Social sentiment endpoints were discontinued by FMP.")
    async def get_trending_social_sentiment(
        self, type: str, source: str
    ) -> list[TrendingSocialSentiment]:
        """Get trending social sentiment data (REMOVED)"""
        raise RemovedEndpointError(
            "get_trending_social_sentiment",
            "Social sentiment endpoints were discontinued by FMP.",
        )  # pragma: no cover

    @removed("Social sentiment endpoints were discontinued by FMP.")
    async def get_social_sentiment_changes(
        self, type: str, source: str
    ) -> list[SocialSentimentChanges]:
        """Get changes in social sentiment data (REMOVED)"""
        raise RemovedEndpointError(
            "get_social_sentiment_changes",
            "Social sentiment endpoints were discontinued by FMP.",
        )  # pragma: no cover

    # ESG methods
    async def get_esg_data(self, symbol: str) -> ESGData | None:
        """Get ESG data for a company"""
        result = await self.client.request_async(ESG_DATA, symbol=symbol)
        return self._unwrap_single(result, ESGData, allow_none=True)

    async def get_esg_ratings(self, symbol: str) -> ESGRating | None:
        """Get ESG ratings for a company"""
        result = await self.client.request_async(ESG_RATINGS, symbol=symbol)
        return self._unwrap_single(result, ESGRating, allow_none=True)

    async def get_esg_benchmark(self) -> list[ESGBenchmark]:
        """Get ESG benchmark data"""
        return await self.client.request_async(ESG_BENCHMARK)

    # Government trading methods
    async def get_senate_latest(
        self, page: int = 0, limit: int = 100
    ) -> list[SenateTrade]:
        """Get latest Senate financial disclosures"""
        return await self.client.request_async(SENATE_LATEST, page=page, limit=limit)

    async def get_senate_trading(self, symbol: str) -> list[SenateTrade]:
        """Get Senate trading data"""
        return await self.client.request_async(SENATE_TRADING, symbol=symbol)

    async def get_senate_trades_by_name(self, name: str) -> list[SenateTrade]:
        """Get Senate trading data by name"""
        return await self.client.request_async(SENATE_TRADES_BY_NAME, name=name)

    async def get_senate_trading_rss(self, page: int = 0) -> list[SenateTrade]:
        """Get Senate trading RSS feed"""
        return await self.client.request_async(SENATE_TRADING_RSS, page=page)

    async def get_house_latest(
        self, page: int = 0, limit: int = 100
    ) -> list[HouseDisclosure]:
        """Get latest House financial disclosures"""
        return await self.client.request_async(HOUSE_LATEST, page=page, limit=limit)

    async def get_house_disclosure(self, symbol: str) -> list[HouseDisclosure]:
        """Get House disclosure data"""
        return await self.client.request_async(HOUSE_DISCLOSURE, symbol=symbol)

    async def get_house_trades_by_name(self, name: str) -> list[HouseDisclosure]:
        """Get House trading data by name"""
        return await self.client.request_async(HOUSE_TRADES_BY_NAME, name=name)

    # Fundraising methods
    async def get_crowdfunding_rss(
        self, page: int = 0, limit: int = 100
    ) -> list[CrowdfundingOffering]:
        """Get latest crowdfunding offerings"""
        return await self.client.request_async(CROWDFUNDING_RSS, page=page, limit=limit)

    async def search_crowdfunding(
        self, name: str
    ) -> list[CrowdfundingOfferingSearchItem]:
        """Search crowdfunding offerings"""
        return await self.client.request_async(CROWDFUNDING_SEARCH, name=name)

    async def get_crowdfunding_by_cik(self, cik: str) -> list[CrowdfundingOffering]:
        """Get crowdfunding offerings by CIK"""
        return await self.client.request_async(CROWDFUNDING_BY_CIK, cik=cik)

    async def get_equity_offering_rss(
        self, page: int = 0, limit: int = 10, cik: str | None = None
    ) -> list[EquityOffering]:
        """Get latest equity offerings"""
        params: dict[str, int | str] = {"page": page, "limit": limit}
        if cik is not None:
            params["cik"] = cik
        return await self.client.request_async(EQUITY_OFFERING_RSS, **params)

    async def search_equity_offering(self, name: str) -> list[EquityOfferingSearchItem]:
        """Search equity offerings"""
        return await self.client.request_async(EQUITY_OFFERING_SEARCH, name=name)

    async def get_equity_offering_by_cik(self, cik: str) -> list[EquityOffering]:
        """Get equity offerings by CIK"""
        return await self.client.request_async(EQUITY_OFFERING_BY_CIK, cik=cik)

    # Analyst Ratings and Grades methods
    async def get_ratings_snapshot(self, symbol: str) -> RatingsSnapshot | None:
        """Get current analyst ratings snapshot"""
        result = await self.client.request_async(RATINGS_SNAPSHOT, symbol=symbol)
        return self._unwrap_single(result, RatingsSnapshot, allow_none=True)

    async def get_ratings_historical(
        self, symbol: str, limit: int = 100
    ) -> list[HistoricalRating]:
        """Get historical analyst ratings"""
        return await self.client.request_async(
            RATINGS_HISTORICAL, symbol=symbol, limit=limit
        )

    async def get_price_target_news(
        self, symbol: str, page: int = 0
    ) -> list[PriceTargetNews]:
        """Get price target news"""
        return await self.client.request_async(
            PRICE_TARGET_NEWS, symbol=symbol, page=page
        )

    async def get_price_target_latest_news(
        self, page: int = 0
    ) -> list[PriceTargetNews]:
        """Get latest price target news"""
        return await self.client.request_async(PRICE_TARGET_LATEST_NEWS, page=page)

    async def get_grades(self, symbol: str, page: int = 0) -> list[StockGrade]:
        """Get stock grades from analysts"""
        return await self.client.request_async(GRADES, symbol=symbol, page=page)

    async def get_grades_historical(
        self, symbol: str, limit: int = 100
    ) -> list[HistoricalStockGrade]:
        """Get historical stock grades"""
        return await self.client.request_async(
            GRADES_HISTORICAL, symbol=symbol, limit=limit
        )

    async def get_grades_consensus(self, symbol: str) -> StockGradesConsensus | None:
        """Get stock grades consensus summary"""
        result = await self.client.request_async(GRADES_CONSENSUS, symbol=symbol)
        return self._unwrap_single(result, StockGradesConsensus, allow_none=True)

    async def get_grades_news(self, symbol: str, page: int = 0) -> list[StockGradeNews]:
        """Get stock grade news"""
        return await self.client.request_async(GRADES_NEWS, symbol=symbol, page=page)

    async def get_grades_latest_news(self, page: int = 0) -> list[StockGradeNews]:
        """Get latest stock grade news"""
        return await self.client.request_async(GRADES_LATEST_NEWS, page=page)
