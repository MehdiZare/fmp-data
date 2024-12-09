from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import HttpUrl

from fmp_data import FMPDataClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    FMPArticle,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalSocialSentiment,
    IPOEvent,
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


class TestIntelligenceEndpoints:
    """Test market intelligence endpoints"""

    def test_get_price_target(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price targets"""
        with vcr_instance.use_cassette("intelligence/price_target.yaml"):
            targets = fmp_client.intelligence.get_price_target("AAPL")

            assert isinstance(targets, list)
            assert len(targets) > 0

            for target in targets:
                assert isinstance(target, PriceTarget)
                assert isinstance(target.published_date, datetime)
                assert isinstance(target.price_target, float)
                assert target.symbol == "AAPL"
                assert isinstance(target.adj_price_target, float)
                assert isinstance(target.price_when_posted, float)

    def test_get_price_target_summary(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target summary"""
        with vcr_instance.use_cassette("intelligence/price_target_summary.yaml"):
            summary = fmp_client.intelligence.get_price_target_summary("AAPL")

            assert isinstance(summary, PriceTargetSummary)
            assert summary.symbol == "AAPL"
            assert isinstance(summary.last_month, int)
            assert isinstance(summary.last_month_avg_price_target, float)
            assert isinstance(summary.last_quarter_avg_price_target, float)
            assert isinstance(summary.last_year, int)
            assert isinstance(summary.all_time_avg_price_target, float)

    def test_get_price_target_consensus(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target consensus"""
        with vcr_instance.use_cassette("intelligence/price_target_consensus.yaml"):
            consensus = fmp_client.intelligence.get_price_target_consensus("AAPL")

            assert isinstance(consensus, PriceTargetConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.target_consensus, float)
            assert isinstance(consensus.target_high, float)
            assert isinstance(consensus.target_low, float)

    def test_get_analyst_estimates(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst estimates"""
        with vcr_instance.use_cassette("intelligence/analyst_estimates.yaml"):
            estimates = fmp_client.intelligence.get_analyst_estimates("AAPL")

            assert isinstance(estimates, list)
            assert len(estimates) > 0

            for estimate in estimates:
                assert isinstance(estimate, AnalystEstimate)
                assert isinstance(estimate.date, datetime)
                assert isinstance(estimate.estimated_revenue_high, float)
                assert estimate.symbol == "AAPL"
                assert isinstance(estimate.estimated_ebitda_avg, float)
                assert isinstance(estimate.number_analyst_estimated_revenue, int)

    def test_get_analyst_recommendations(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting analyst recommendations"""
        with vcr_instance.use_cassette("intelligence/analyst_recommendations.yaml"):
            recommendations = fmp_client.intelligence.get_analyst_recommendations(
                "AAPL"
            )

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0

            for rec in recommendations:
                assert isinstance(rec, AnalystRecommendation)
                assert isinstance(rec.date, datetime)
                assert rec.symbol == "AAPL"
                assert isinstance(rec.analyst_ratings_buy, int)
                assert isinstance(rec.analyst_ratings_strong_sell, int)

    def test_get_upgrades_downgrades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting upgrades and downgrades"""
        with vcr_instance.use_cassette("intelligence/upgrades_downgrades.yaml"):
            changes = fmp_client.intelligence.get_upgrades_downgrades("AAPL")

            assert isinstance(changes, list)
            assert len(changes) > 0

            for change in changes:
                assert isinstance(change, UpgradeDowngrade)
                assert isinstance(change.published_date, datetime)
                assert change.symbol == "AAPL"
                assert isinstance(change.action, str)
                assert (
                    isinstance(change.previous_grade, str)
                    if change.previous_grade is not None
                    else True
                )
                assert isinstance(change.new_grade, str)

    def test_get_upgrades_downgrades_consensus(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting upgrades/downgrades consensus"""
        with vcr_instance.use_cassette(
            "intelligence/upgrades_downgrades_consensus.yaml"
        ):
            consensus = fmp_client.intelligence.get_upgrades_downgrades_consensus(
                "AAPL"
            )

            assert isinstance(consensus, UpgradeDowngradeConsensus)
            assert consensus.symbol == "AAPL"
            assert isinstance(consensus.strong_buy, int)
            assert isinstance(consensus.buy, int)
            assert isinstance(consensus.hold, int)
            assert isinstance(consensus.sell, int)
            assert isinstance(consensus.strong_sell, int)

    def test_get_earnings_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings calendar"""
        with vcr_instance.use_cassette("intelligence/earnings_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_earnings_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, EarningEvent)
                assert isinstance(event.event_date, date)
                assert isinstance(event.symbol, str)
                assert isinstance(event.fiscal_date_ending, date)
                assert isinstance(event.updated_from_date, date)
                if event.eps_estimated is not None:
                    assert isinstance(event.eps_estimated, float)

    def test_get_earnings_confirmed(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting confirmed earnings"""
        with vcr_instance.use_cassette("intelligence/earnings_confirmed.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_earnings_confirmed(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, EarningConfirmed)
                    assert isinstance(event.time, str)
                    if event.event_date is not None:
                        assert isinstance(event.event_date, datetime)

    def test_get_historical_earnings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical earnings"""
        with vcr_instance.use_cassette("intelligence/historical_earnings.yaml"):
            events = fmp_client.intelligence.get_historical_earnings("AAPL")

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, EarningEvent)
                assert event.symbol == "AAPL"
                assert isinstance(event.event_date, date)
                assert isinstance(event.time, str)

    def test_get_earnings_surprises(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings surprises"""
        with vcr_instance.use_cassette("intelligence/earnings_surprises.yaml"):
            surprises = fmp_client.intelligence.get_earnings_surprises("AAPL")

            assert isinstance(surprises, list)
            assert len(surprises) > 0

            for surprise in surprises:
                assert isinstance(surprise, EarningSurprise)
                assert surprise.symbol == "AAPL"
                assert isinstance(surprise.surprise_date, date)
                assert isinstance(surprise.actual_earning_result, float)
                assert isinstance(surprise.estimated_earning, float)

    def test_get_dividends_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting dividends calendar"""
        with vcr_instance.use_cassette("intelligence/dividends_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_dividends_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, DividendEvent)
                assert isinstance(event.symbol, str)
                assert isinstance(event.dividend, float)
                assert (
                    isinstance(event.record_date, date) if event.record_date else True
                )
                assert (
                    isinstance(event.payment_date, date) if event.payment_date else True
                )
                assert isinstance(event.ex_dividend_date, date)

    def test_get_stock_splits_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock splits calendar"""
        with vcr_instance.use_cassette("intelligence/stock_splits_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_stock_splits_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, StockSplitEvent)
                    assert isinstance(event.symbol, str)
                    assert isinstance(event.split_event_date, date)
                    assert isinstance(event.label, str)
                    assert isinstance(event.numerator, int)
                    assert isinstance(event.denominator, int)

    def test_get_ipo_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting IPO calendar"""
        with vcr_instance.use_cassette("intelligence/ipo_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = fmp_client.intelligence.get_ipo_calendar(
                start_date=start_date, end_date=end_date
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, IPOEvent)
                    assert isinstance(event.symbol, str)
                    assert isinstance(event.company, str)
                    assert isinstance(event.ipo_event_date, date)
                    assert isinstance(event.exchange, str)
                    if event.shares is not None:
                        assert isinstance(event.shares, int)
                    if event.market_cap is not None:
                        assert isinstance(event.market_cap, Decimal)

    def test_get_fmp_articles(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting FMP articles"""
        with vcr_instance.use_cassette("intelligence/fmp_articles.yaml"):
            articles = fmp_client.intelligence.get_fmp_articles(page=0, size=5)

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, FMPArticle)
                assert isinstance(article.title, str)
                assert isinstance(article.date, datetime)
                assert isinstance(article.content, str)
                assert isinstance(article.tickers, str)
                assert isinstance(article.image, HttpUrl)
                assert isinstance(article.link, HttpUrl)
                assert isinstance(article.author, str)
                assert isinstance(article.site, str)

    def test_get_general_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting general news articles"""
        with vcr_instance.use_cassette("intelligence/general_news.yaml"):
            articles = fmp_client.intelligence.get_general_news(page=0)

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, GeneralNewsArticle)
                assert isinstance(article.publishedDate, datetime)
                assert isinstance(article.title, str)
                assert isinstance(article.image, HttpUrl)
                assert isinstance(article.site, str)
                assert isinstance(article.text, str)
                assert isinstance(article.url, HttpUrl)

    def test_get_stock_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock news articles"""
        with vcr_instance.use_cassette("intelligence/stock_news.yaml"):
            articles = fmp_client.intelligence.get_stock_news(
                tickers="AAPL,MSFT",
                page=0,
                from_date=date(2024, 1, 1),
                to_date=date(2024, 1, 31),
                limit=10,
            )

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, StockNewsArticle)
                assert isinstance(article.symbol, str)
                assert isinstance(article.publishedDate, datetime)
                assert isinstance(article.title, str)
                assert isinstance(article.image, HttpUrl)
                assert isinstance(article.site, str)
                assert isinstance(article.text, str)
                assert isinstance(article.url, HttpUrl)

    def test_get_stock_news_sentiments(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock news articles with sentiment"""
        with vcr_instance.use_cassette("intelligence/stock_news_sentiments.yaml"):
            articles = fmp_client.intelligence.get_stock_news_sentiments(page=0)

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, StockNewsSentiment)
                assert isinstance(article.symbol, str)
                assert isinstance(article.publishedDate, datetime)
                assert isinstance(article.sentiment, str)
                assert isinstance(article.sentimentScore, float)
                assert isinstance(article.title, str)
                assert isinstance(article.text, str)

    def test_get_forex_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting forex news articles"""
        with vcr_instance.use_cassette("intelligence/forex_news.yaml"):
            articles = fmp_client.intelligence.get_forex_news(
                page=0,
                symbol="EURUSD",
                from_date=date(2024, 1, 1),
                to_date=date(2024, 1, 31),
            )

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, ForexNewsArticle)
                assert isinstance(article.publishedDate, datetime)
                assert isinstance(article.title, str)
                assert isinstance(article.site, str)
                assert isinstance(article.text, str)
                assert isinstance(article.symbol, str)

    def test_get_crypto_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting crypto news articles"""
        with vcr_instance.use_cassette("intelligence/crypto_news.yaml"):
            articles = fmp_client.intelligence.get_crypto_news(
                symbol="BTC",
                from_date=date(2024, 1, 1),
            )

            assert isinstance(articles, list)
            assert len(articles) > 0

            for article in articles:
                assert isinstance(article, CryptoNewsArticle)
                assert isinstance(article.publishedDate, datetime)
                assert isinstance(article.title, str)
                if article.image is not None:
                    assert isinstance(article.image, HttpUrl)
                assert isinstance(article.site, str)
                assert isinstance(article.text, str)
                assert isinstance(article.url, HttpUrl)
                assert isinstance(article.symbol, str)

    def test_get_press_releases(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting press releases"""
        with vcr_instance.use_cassette("intelligence/press_releases.yaml"):
            releases = fmp_client.intelligence.get_press_releases(page=0)

            assert isinstance(releases, list)
            assert len(releases) > 0

            for release in releases:
                assert isinstance(release, PressRelease)
                assert isinstance(release.symbol, str)
                assert isinstance(release.date, datetime)
                assert isinstance(release.title, str)
                assert isinstance(release.text, str)

    def test_get_press_releases_by_symbol(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting press releases by symbol"""
        with vcr_instance.use_cassette("intelligence/press_releases_by_symbol.yaml"):
            releases = fmp_client.intelligence.get_press_releases_by_symbol(
                symbol="AAPL", page=0
            )

            assert isinstance(releases, list)
            assert len(releases) > 0

            for release in releases:
                assert isinstance(release, PressReleaseBySymbol)
                assert release.symbol == "AAPL"
                assert isinstance(release.date, datetime)
                assert isinstance(release.title, str)
                assert isinstance(release.text, str)

    def test_get_historical_social_sentiment(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting historical social sentiment"""
        with vcr_instance.use_cassette("intelligence/historical_social_sentiment.yaml"):
            sentiments = fmp_client.intelligence.get_historical_social_sentiment(
                symbol="AAPL", page=0
            )

            assert isinstance(sentiments, list)
            assert len(sentiments) > 0

            for sentiment in sentiments:
                assert isinstance(sentiment, HistoricalSocialSentiment)
                assert isinstance(sentiment.date, datetime)
                assert sentiment.symbol == "AAPL"
                assert isinstance(sentiment.stocktwitsPosts, int)
                assert isinstance(sentiment.twitterPosts, int)
                assert isinstance(sentiment.stocktwitsSentiment, float)
                assert isinstance(sentiment.twitterSentiment, float)

    def test_get_trending_social_sentiment(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting trending social sentiment"""
        with vcr_instance.use_cassette("intelligence/trending_social_sentiment.yaml"):
            sentiments = fmp_client.intelligence.get_trending_social_sentiment(
                type="bullish", source="stocktwits"
            )

            assert isinstance(sentiments, list)
            assert len(sentiments) > 0

            for sentiment in sentiments:
                assert isinstance(sentiment, TrendingSocialSentiment)
                assert isinstance(sentiment.symbol, str)
                assert isinstance(sentiment.name, str)
                assert isinstance(sentiment.rank, int)
                assert isinstance(sentiment.sentiment, float)
                assert isinstance(sentiment.lastSentiment, float)

    def test_get_social_sentiment_changes(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting social sentiment changes"""
        with vcr_instance.use_cassette("intelligence/social_sentiment_changes.yaml"):
            changes = fmp_client.intelligence.get_social_sentiment_changes(
                type="bullish", source="stocktwits"
            )

            assert isinstance(changes, list)
            assert len(changes) > 0

            for change in changes:
                assert isinstance(change, SocialSentimentChanges)
                assert isinstance(change.symbol, str)
                assert isinstance(change.name, str)
                assert isinstance(change.rank, int)
                assert isinstance(change.sentiment, float)
                assert isinstance(change.sentimentChange, float)
