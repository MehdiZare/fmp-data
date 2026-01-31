from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import HttpUrl
import pytest

from fmp_data import FMPDataClient
from fmp_data.helpers import RemovedEndpointError
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
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalRating,
    HistoricalStockGrade,
    HouseDisclosure,
    IPOEvent,
    PressRelease,
    PressReleaseBySymbol,
    PriceTargetNews,
    RatingsSnapshot,
    SenateTrade,
    StockGrade,
    StockGradeNews,
    StockGradesConsensus,
    StockNewsArticle,
    StockSplitEvent,
)

from .base import BaseTestCase


class TestIntelligenceEndpoints(BaseTestCase):
    """Test market intelligence endpoints"""

    def test_get_earnings_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings calendar"""
        with vcr_instance.use_cassette("intelligence/earnings_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = self._handle_rate_limit(
                fmp_client.intelligence.get_earnings_calendar,
                start_date=start_date,
                end_date=end_date,
            )

            assert isinstance(events, list)
            assert len(events) > 0

            for event in events:
                assert isinstance(event, EarningEvent)
                assert isinstance(event.event_date, date)
                assert isinstance(event.symbol, str)
                if event.fiscal_date_ending is not None:
                    assert isinstance(event.fiscal_date_ending, date)
                if event.updated_from_date is not None:
                    assert isinstance(event.updated_from_date, date)
                if event.eps_estimated is not None:
                    assert isinstance(event.eps_estimated, float)

    def test_get_earnings_confirmed(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting confirmed earnings"""
        with vcr_instance.use_cassette("intelligence/earnings_confirmed.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = self._handle_rate_limit(
                fmp_client.intelligence.get_earnings_confirmed,
                start_date=start_date,
                end_date=end_date,
            )

            assert isinstance(events, list), "events is not a list"
            if len(events) > 0:
                for event in events:
                    assert isinstance(
                        event, EarningConfirmed
                    ), "event tpye is not Earning Confirmed"
                    if event.time is not None:
                        assert isinstance(
                            event.time, str
                        ), "event time is not of type string, it"
                    if event.event_date is not None:
                        assert isinstance(
                            event.event_date, datetime
                        ), "event date is not of datetime type"

    def test_get_historical_earnings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical earnings"""
        with vcr_instance.use_cassette("intelligence/historical_earnings.yaml"):
            events = self._handle_rate_limit(
                fmp_client.intelligence.get_historical_earnings, "AAPL"
            )

            assert isinstance(events, list)
            # API may return empty array if no historical data available
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, EarningEvent)
                    assert event.symbol == "AAPL"
                    assert isinstance(event.event_date, date)
                    if event.time is not None:
                        assert isinstance(event.time, str)

    def test_get_earnings_surprises(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting earnings surprises"""
        with vcr_instance.use_cassette("intelligence/earnings_surprises.yaml"):
            surprises = self._handle_rate_limit(
                fmp_client.intelligence.get_earnings_surprises, "AAPL"
            )

            assert isinstance(surprises, list)
            # API may return empty array if no data available
            if len(surprises) > 0:
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

            events = self._handle_rate_limit(
                fmp_client.intelligence.get_dividends_calendar,
                start_date=start_date,
                end_date=end_date,
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

            events = self._handle_rate_limit(
                fmp_client.intelligence.get_stock_splits_calendar,
                start_date=start_date,
                end_date=end_date,
            )

            assert isinstance(events, list)
            if len(events) > 0:
                for event in events:
                    assert isinstance(event, StockSplitEvent)
                    assert isinstance(event.symbol, str)
                    assert isinstance(event.split_event_date, date)
                    if event.label is not None:
                        assert isinstance(event.label, str)
                    assert isinstance(event.numerator, float)
                    assert isinstance(event.denominator, float)

    def test_get_ipo_calendar(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting IPO calendar"""
        with vcr_instance.use_cassette("intelligence/ipo_calendar.yaml"):
            start_date = date.today()
            end_date = start_date + timedelta(days=30)

            events = self._handle_rate_limit(
                fmp_client.intelligence.get_ipo_calendar,
                start_date=start_date,
                end_date=end_date,
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
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_fmp_articles, page=0, limit=5
            )

            assert isinstance(articles, list)
            # API may return empty array if no data available
            if len(articles) > 0:
                for article in articles:
                    assert isinstance(article, FMPArticle)
                    if article.title is not None:
                        assert isinstance(article.title, str)
                    assert isinstance(article.date, datetime)
                    if article.content is not None:
                        assert isinstance(article.content, str)
                    if article.tickers is not None:
                        assert isinstance(article.tickers, str)
                    if article.image is not None:
                        assert isinstance(article.image, HttpUrl)
                    if article.link is not None:
                        assert isinstance(article.link, HttpUrl)
                    if article.author is not None:
                        assert isinstance(article.author, str)
                    if article.site is not None:
                        assert isinstance(article.site, str)

    def test_get_general_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting general news articles"""
        with vcr_instance.use_cassette("intelligence/general_news.yaml"):
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_general_news,
                page=0,
                limit=20,
            )

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
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_stock_news,
                symbol="AAPL",
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
        """Test getting stock news articles with sentiment

        Note: This endpoint is deprecated and returns empty results.
        """
        with vcr_instance.use_cassette("intelligence/stock_news_sentiments.yaml"):
            # Expect deprecation warning
            with pytest.warns(
                DeprecationWarning, match="no longer supports this endpoint"
            ):
                articles = self._handle_rate_limit(
                    fmp_client.intelligence.get_stock_news_sentiments,
                    page=0,
                )

            # Endpoint is deprecated - should return empty list
            assert isinstance(articles, list)
            assert len(articles) == 0, "Deprecated endpoint should return empty list"

    def test_get_forex_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting forex news articles"""
        with vcr_instance.use_cassette("intelligence/forex_news.yaml"):
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_forex_symbol_news,
                symbol="EURUSD",
                from_date=date(2024, 1, 1),
                to_date=date(2024, 1, 31),
                limit=20,
            )

            assert isinstance(articles, list)
            # API may return empty array if no data available
            if len(articles) > 0:
                for article in articles:
                    assert isinstance(article, ForexNewsArticle)
                    assert isinstance(article.publishedDate, datetime)
                    assert isinstance(article.title, str)
                    assert isinstance(article.site, str)
                    assert isinstance(article.text, str)
                    if article.symbol is not None:
                        assert isinstance(article.symbol, str)

    def test_get_crypto_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting crypto news articles"""
        with vcr_instance.use_cassette("intelligence/crypto_news.yaml"):
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_crypto_symbol_news,
                symbol="BTCUSD",
                from_date=date(2024, 1, 1),
                limit=20,
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
            releases = self._handle_rate_limit(
                fmp_client.intelligence.get_press_releases,
                page=0,
                limit=20,
            )

            assert isinstance(releases, list)
            assert len(releases) > 0

            for release in releases:
                assert isinstance(release, PressRelease)
                if release.symbol is not None:
                    assert isinstance(release.symbol, str)
                if release.date is not None:
                    assert isinstance(release.date, datetime)
                assert isinstance(release.title, str)
                assert isinstance(release.text, str)

    def test_get_press_releases_by_symbol(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting press releases by symbol"""
        with vcr_instance.use_cassette("intelligence/press_releases_by_symbol.yaml"):
            releases = self._handle_rate_limit(
                fmp_client.intelligence.get_press_releases_by_symbol,
                symbol="AAPL",
                page=0,
                limit=20,
            )

            assert isinstance(releases, list)
            assert len(releases) > 0

            for release in releases:
                assert isinstance(release, PressReleaseBySymbol)
                if release.symbol is not None:
                    assert release.symbol == "AAPL"
                if release.date is not None:
                    assert isinstance(release.date, datetime)
                assert isinstance(release.title, str)
                assert isinstance(release.text, str)

    def test_get_esg_data(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ESG data"""
        with vcr_instance.use_cassette("intelligence/esg_data.yaml"):
            data = self._handle_rate_limit(
                fmp_client.intelligence.get_esg_data,
                "AAPL",
            )

            # API may return None if no data available
            if data is not None:
                assert isinstance(data, ESGData)
                if data.symbol is not None:
                    assert data.symbol == "AAPL"
                if data.environmental_score is not None:
                    assert isinstance(data.environmental_score, float)
                if data.social_score is not None:
                    assert isinstance(data.social_score, float)
                if data.governance_score is not None:
                    assert isinstance(data.governance_score, float)
                if data.company_name is not None:
                    assert isinstance(data.company_name, str)
                if data.date is not None:
                    assert isinstance(data.date, datetime)

    def test_get_esg_ratings(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ESG ratings"""
        with vcr_instance.use_cassette("intelligence/esg_ratings.yaml"):
            rating = self._handle_rate_limit(
                fmp_client.intelligence.get_esg_ratings,
                "AAPL",
            )

            # API may return None if no data available
            if rating is not None:
                assert isinstance(rating, ESGRating)
                if rating.symbol is not None:
                    assert rating.symbol == "AAPL"
                if rating.year is not None:
                    assert isinstance(rating.year, int)
                if rating.esg_risk_rating is not None:
                    assert isinstance(rating.esg_risk_rating, str)

    def test_get_esg_benchmark(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ESG benchmark data"""
        with vcr_instance.use_cassette("intelligence/esg_benchmark.yaml"):
            benchmarks = self._handle_rate_limit(
                fmp_client.intelligence.get_esg_benchmark,
            )

            assert isinstance(benchmarks, list)
            # API may return empty array if no data available
            if len(benchmarks) > 0:
                for benchmark in benchmarks:
                    assert isinstance(benchmark, ESGBenchmark)
                    if benchmark.sector is not None:
                        assert isinstance(benchmark.sector, str)
                    if benchmark.environmental_score is not None:
                        assert isinstance(benchmark.environmental_score, float)
                    if benchmark.social_score is not None:
                        assert isinstance(benchmark.social_score, float)
                    if benchmark.governance_score is not None:
                        assert isinstance(benchmark.governance_score, float)
                    if benchmark.esg_score is not None:
                        assert isinstance(benchmark.esg_score, float)

    def test_get_senate_trading(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting senate trading data"""
        with vcr_instance.use_cassette("intelligence/senate_trading.yaml"):
            trades = self._handle_rate_limit(
                fmp_client.intelligence.get_senate_trading,
                "AAPL",
            )

            assert isinstance(trades, list)
            # API may return empty array if no data available
            if len(trades) > 0:
                for trade in trades:
                    assert isinstance(trade, SenateTrade)
                    assert isinstance(trade.disclosure_date, datetime)
                    assert isinstance(trade.amount, str)
                    assert isinstance(trade.first_name, str)
                    assert isinstance(trade.last_name, str)

    def test_get_senate_latest(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest senate disclosures"""
        with vcr_instance.use_cassette("intelligence/senate_latest.yaml"):
            trades = self._handle_rate_limit(
                fmp_client.intelligence.get_senate_latest,
                page=0,
                limit=100,
            )

            assert isinstance(trades, list)
            if len(trades) > 0:
                for trade in trades:
                    assert isinstance(trade, SenateTrade)
                    assert trade.disclosure_date
                    assert trade.symbol

    def test_get_senate_trades_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting senate trades by name"""
        with vcr_instance.use_cassette("intelligence/senate_trades_by_name.yaml"):
            trades = self._handle_rate_limit(
                fmp_client.intelligence.get_senate_trades_by_name,
                "Jerry",
            )

            assert isinstance(trades, list)
            if len(trades) > 0:
                for trade in trades:
                    assert isinstance(trade, SenateTrade)
                    assert trade.first_name
                    assert trade.last_name

    def test_get_senate_trading_rss(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting senate trading RSS feed"""
        with vcr_instance.use_cassette("intelligence/senate_trading_rss.yaml"):
            trades = self._handle_rate_limit(
                fmp_client.intelligence.get_senate_trading_rss,
                page=0,
            )

            assert isinstance(trades, list)
            # API may return empty array if no data available
            if len(trades) > 0:
                for trade in trades:
                    assert isinstance(trade, SenateTrade)
                    assert isinstance(trade.disclosure_date, datetime)
                    assert isinstance(trade.amount, str)
                    assert isinstance(trade.first_name, str)
                    assert isinstance(trade.last_name, str)

    def test_get_house_latest(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest house disclosures"""
        with vcr_instance.use_cassette("intelligence/house_latest.yaml"):
            disclosures = self._handle_rate_limit(
                fmp_client.intelligence.get_house_latest,
                page=0,
                limit=100,
            )

            assert isinstance(disclosures, list)
            if len(disclosures) > 0:
                for disclosure in disclosures:
                    assert isinstance(disclosure, HouseDisclosure)
                    assert disclosure.disclosure_date
                    assert disclosure.symbol

    def test_get_house_disclosure(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting house disclosure data"""
        with vcr_instance.use_cassette("intelligence/house_disclosure.yaml"):
            disclosures = self._handle_rate_limit(
                fmp_client.intelligence.get_house_disclosure,
                "AAPL",
            )

            assert isinstance(disclosures, list)
            # API may return empty array if no data available
            if len(disclosures) > 0:
                for disclosure in disclosures:
                    assert isinstance(disclosure, HouseDisclosure)
                    assert isinstance(disclosure.disclosure_date, datetime)
                    assert isinstance(disclosure.transaction_date, datetime)
                    assert isinstance(disclosure.amount, str)
                    assert isinstance(disclosure.first_name, str)
                    assert isinstance(disclosure.last_name, str)
                    assert isinstance(disclosure.district, str)
                    assert isinstance(disclosure.asset_description, str)

    def test_get_house_trades_by_name(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting house trades by name"""
        with vcr_instance.use_cassette("intelligence/house_trades_by_name.yaml"):
            disclosures = self._handle_rate_limit(
                fmp_client.intelligence.get_house_trades_by_name,
                "James",
            )

            assert isinstance(disclosures, list)
            if len(disclosures) > 0:
                for disclosure in disclosures:
                    assert isinstance(disclosure, HouseDisclosure)
                    assert disclosure.first_name
                    assert disclosure.last_name

    def test_get_crowdfunding_rss(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest crowdfunding offerings"""
        with vcr_instance.use_cassette("intelligence/crowdfunding_rss.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.get_crowdfunding_rss,
                page=0,
                limit=100,
            )

            assert isinstance(offerings, list)
            # API may return empty array if no data available
            if len(offerings) > 0:
                for offering in offerings:
                    assert isinstance(offering, CrowdfundingOffering)
                    assert isinstance(offering.filing_date, datetime)
                    assert isinstance(offering.form_type, str)

    def test_search_crowdfunding(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching crowdfunding offerings"""
        with vcr_instance.use_cassette("intelligence/crowdfunding_search.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.search_crowdfunding,
                "NJOY",
            )

            assert isinstance(offerings, list)
            if len(offerings) > 0:
                for offering in offerings:
                    assert isinstance(offering, CrowdfundingOfferingSearchItem)
                    assert isinstance(offering.cik, str)

    def test_get_crowdfunding_by_cik(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting crowdfunding offerings by CIK"""
        with vcr_instance.use_cassette("intelligence/crowdfunding_by_cik.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.get_crowdfunding_by_cik,
                "0001388838",
            )

            assert isinstance(offerings, list)
            if len(offerings) > 0:
                for offering in offerings:
                    assert offering.cik == "0001388838"
                    assert isinstance(offering, CrowdfundingOffering)
                    assert isinstance(offering.company_name, str)
                    assert isinstance(offering.filing_date, datetime)
                    assert isinstance(offering.name_of_issuer, str)

    def test_get_equity_offering_rss(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest equity offerings"""
        with vcr_instance.use_cassette("intelligence/equity_offering_rss.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.get_equity_offering_rss,
                page=0,
                limit=10,
            )

            assert isinstance(offerings, list)
            # API may return empty array if no data available
            if len(offerings) > 0:
                for offering in offerings:
                    assert isinstance(offering, EquityOffering)
                    assert isinstance(offering.entity_name, str)
                    assert isinstance(offering.year_of_incorporation, str)
                    assert isinstance(offering.related_person_first_name, str)
                    assert isinstance(offering.date_of_first_sale, str)
                    assert isinstance(offering.industry_group_type, str)

    def test_search_equity_offering(self, fmp_client: FMPDataClient, vcr_instance):
        """Test searching equity offerings"""
        with vcr_instance.use_cassette("intelligence/equity_offering_search.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.search_equity_offering,
                "AAPL",
            )

            assert isinstance(offerings, list)
            if len(offerings) > 0:
                for offering in offerings:
                    assert isinstance(offering, EquityOfferingSearchItem)
                    assert isinstance(offering.cik, str)
                    assert isinstance(offering.name, str)

    def test_get_equity_offering_by_cik(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting equity offerings by CIK"""
        with vcr_instance.use_cassette("intelligence/equity_offering_by_cik.yaml"):
            offerings = self._handle_rate_limit(
                fmp_client.intelligence.get_equity_offering_by_cik,
                "0001388838",
            )

            assert isinstance(offerings, list)
            if len(offerings) > 0:
                for offering in offerings:
                    assert offering.cik == "0001388838"
                    assert isinstance(offering, EquityOffering)
                    assert isinstance(offering.entity_name, str)
                    assert isinstance(offering.year_of_incorporation, str)
                    assert isinstance(offering.related_person_first_name, str)
                    assert isinstance(offering.date_of_first_sale, str)
                    assert isinstance(offering.form_signification, str)

    def test_get_stock_symbol_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock symbol news"""
        with vcr_instance.use_cassette("intelligence/stock_symbol_news.yaml"):
            articles = self._handle_rate_limit(
                fmp_client.intelligence.get_stock_symbol_news,
                "AAPL",
                page=0,
                limit=5,
            )
            assert isinstance(articles, list)
            if articles:
                assert isinstance(articles[0], StockNewsArticle)

    def test_get_historical_social_sentiment(self, fmp_client: FMPDataClient):
        """Test that historical social sentiment raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_historical_social_sentiment("AAPL", page=0)
        assert "get_historical_social_sentiment" in str(exc_info.value)

    def test_get_trending_social_sentiment(self, fmp_client: FMPDataClient):
        """Test that trending social sentiment raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_trending_social_sentiment(
                "bullish", "stocktwits"
            )
        assert "get_trending_social_sentiment" in str(exc_info.value)

    def test_get_social_sentiment_changes(self, fmp_client: FMPDataClient):
        """Test that social sentiment changes raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_social_sentiment_changes(
                "bullish", "stocktwits"
            )
        assert "get_social_sentiment_changes" in str(exc_info.value)

    def test_get_ratings_snapshot(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting ratings snapshot"""
        with vcr_instance.use_cassette("intelligence/ratings_snapshot.yaml"):
            snapshot = self._handle_rate_limit(
                fmp_client.intelligence.get_ratings_snapshot, "AAPL"
            )
            assert isinstance(snapshot, RatingsSnapshot)

    def test_get_ratings_historical(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical ratings"""
        with vcr_instance.use_cassette("intelligence/ratings_historical.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_ratings_historical, "AAPL", limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalRating)

    def test_get_price_target_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting price target news"""
        with vcr_instance.use_cassette("intelligence/price_target_news.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_price_target_news, "AAPL", page=0
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], PriceTargetNews)

    def test_get_price_target_latest_news(
        self, fmp_client: FMPDataClient, vcr_instance
    ):
        """Test getting latest price target news"""
        with vcr_instance.use_cassette("intelligence/price_target_latest_news.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_price_target_latest_news, page=0
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], PriceTargetNews)

    def test_get_grades(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock grades"""
        with vcr_instance.use_cassette("intelligence/grades.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_grades, "AAPL", page=0
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], StockGrade)

    def test_get_grades_historical(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting historical stock grades"""
        with vcr_instance.use_cassette("intelligence/grades_historical.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_grades_historical, "AAPL", limit=5
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], HistoricalStockGrade)

    def test_get_grades_consensus(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock grades consensus"""
        with vcr_instance.use_cassette("intelligence/grades_consensus.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_grades_consensus, "AAPL"
            )
            assert isinstance(results, StockGradesConsensus)

    def test_get_grades_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting stock grades news"""
        with vcr_instance.use_cassette("intelligence/grades_news.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_grades_news, "AAPL", page=0
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], StockGradeNews)

    def test_get_grades_latest_news(self, fmp_client: FMPDataClient, vcr_instance):
        """Test getting latest stock grades news"""
        with vcr_instance.use_cassette("intelligence/grades_latest_news.yaml"):
            results = self._handle_rate_limit(
                fmp_client.intelligence.get_grades_latest_news, page=0
            )
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], StockGradeNews)
