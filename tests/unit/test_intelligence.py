# tests/unit/test_intelligence_client.py (Enhanced version)
from datetime import date, datetime
from unittest.mock import Mock

import pytest

from fmp_data.helpers import RemovedEndpointError
from fmp_data.intelligence.client import MarketIntelligenceClient
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


@pytest.fixture
def mock_client():
    """Create a mock client for testing"""
    return Mock()


@pytest.fixture
def fmp_client(mock_client):
    """Create FMP client with mocked intelligence client"""
    from fmp_data import ClientConfig, FMPDataClient

    client = FMPDataClient(config=ClientConfig(api_key="dummy"))
    # Replace the intelligence client with our properly mocked one
    mock_base_client = Mock()
    client._intelligence = MarketIntelligenceClient(mock_base_client)
    client._intelligence.client.request = mock_client.request
    return client


# Test Data Fixtures
@pytest.fixture
def earnings_calendar_data():
    return {
        "date": "2024-01-15",
        "symbol": "AAPL",
        "eps": 1.25,
        "epsEstimated": 1.20,
        "time": "amc",
        "revenue": 1000000000,
        "revenueEstimated": 950000000,
        "fiscalDateEnding": "2024-03-31",
        "updatedFromDate": "2024-01-01",
    }


@pytest.fixture
def earnings_confirmed_data():
    return {
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "time": "16:30",
        "when": "post market",
        "date": "2024-01-15T16:30:00",
        "publicationDate": "2024-01-01T10:00:00",
        "title": "Apple Q1 2024 Earnings",
        "url": "https://example.com",
    }


@pytest.fixture
def dividends_calendar_data():
    return {
        "symbol": "AAPL",
        "date": "2024-01-15",
        "label": "Jan 15, 2024",
        "adjDividend": 0.22,
        "dividend": 0.20,
        "recordDate": "2024-01-10",
        "paymentDate": "2024-01-20",
        "declarationDate": "2023-12-15",
    }


@pytest.fixture
def ipo_calendar_data():
    return {
        "symbol": "NEWCO",
        "company": "New Company",
        "date": "2024-02-01",
        "exchange": "NASDAQ",
        "actions": "IPO Scheduled",
        "shares": 1000000,
        "priceRange": "15-18",
        "marketCap": 1700000000,
    }


@pytest.fixture
def esg_data():
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "date": "2024-09-28",
        "environmentalScore": 68.47,
        "socialScore": 47.02,
        "governanceScore": 60.8,
        "ESGScore": 58.76,
        "companyName": "Apple Inc.",
        "industry": "Electronic Computers",
        "formType": "10-K",
        "acceptedDate": "2024-11-01 06:01:36",
        "url": "https://www.sec.gov/example",
    }


@pytest.fixture
def esg_rating_data():
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "companyName": "Apple Inc.",
        "industry": "Technology",
        "year": 2024,
        "ESGRiskRating": "Low Risk",
        "industryRank": "1 of 50",
    }


@pytest.fixture
def stock_news_data():
    return {
        "symbol": "AAPL",
        "publishedDate": "2024-01-15T10:00:00",
        "title": "Apple Announces New Product",
        "image": "https://example.com/image.jpg",
        "site": "Example News",
        "text": "Article text here",
        "url": "https://example.com/article",
    }


@pytest.fixture
def stock_news_sentiment_data():
    return {
        "symbol": "AAPL",
        "publishedDate": "2024-01-15T10:00:00",
        "title": "Apple Stock Analysis",
        "image": "https://example.com/image.jpg",
        "site": "Example News",
        "text": "Article text here",
        "url": "https://example.com/article",
        "sentiment": "Positive",
        "sentimentScore": 0.85,
    }


class TestMarketIntelligenceClientCalendar:
    """Test calendar functionality"""

    def test_get_earnings_calendar_no_dates(
        self, fmp_client, mock_client, earnings_calendar_data
    ):
        """Test get_earnings_calendar without date filters"""
        mock_client.request.return_value = [EarningEvent(**earnings_calendar_data)]

        result = fmp_client.intelligence.get_earnings_calendar()

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert len(kwargs) == 0  # No date parameters when None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

    def test_get_earnings_calendar_with_dates(
        self, fmp_client, mock_client, earnings_calendar_data
    ):
        """Test get_earnings_calendar with date filters"""
        mock_client.request.return_value = [EarningEvent(**earnings_calendar_data)]

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = fmp_client.intelligence.get_earnings_calendar(
            start_date=start_date, end_date=end_date
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        print(kwargs)
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert isinstance(result, list)

    def test_get_historical_earnings(
        self, fmp_client, mock_client, earnings_calendar_data
    ):
        """Test get_historical_earnings"""
        mock_client.request.return_value = [EarningEvent(**earnings_calendar_data)]

        result = fmp_client.intelligence.get_historical_earnings("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, list)

    def test_get_earnings_confirmed(
        self, fmp_client, mock_client, earnings_confirmed_data
    ):
        """Test get_earnings_confirmed"""
        mock_client.request.return_value = [EarningConfirmed(**earnings_confirmed_data)]

        result = fmp_client.intelligence.get_earnings_confirmed(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert isinstance(result, list)

    def test_get_earnings_surprises(self, fmp_client, mock_client):
        """Test get_earnings_surprises"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15",
            "actualEarningResult": 1.25,
            "estimatedEarning": 1.20,
        }
        mock_client.request.return_value = [EarningSurprise(**mock_data)]

        result = fmp_client.intelligence.get_earnings_surprises("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, list)

    def test_get_dividends_calendar(
        self, fmp_client, mock_client, dividends_calendar_data
    ):
        """Test get_dividends_calendar"""
        mock_client.request.return_value = [DividendEvent(**dividends_calendar_data)]

        result = fmp_client.intelligence.get_dividends_calendar(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert isinstance(result, list)
        assert result[0].symbol == "AAPL"

    def test_get_stock_splits_calendar(self, fmp_client, mock_client):
        """Test get_stock_splits_calendar"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15",
            "label": "Jan 15, 2024",
            "numerator": 4,
            "denominator": 1,
        }
        mock_client.request.return_value = [StockSplitEvent(**mock_data)]

        result = fmp_client.intelligence.get_stock_splits_calendar(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert isinstance(result, list)

    def test_get_ipo_calendar(self, fmp_client, mock_client, ipo_calendar_data):
        """Test get_ipo_calendar"""
        mock_client.request.return_value = [IPOEvent(**ipo_calendar_data)]

        result = fmp_client.intelligence.get_ipo_calendar(
            start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert isinstance(result, list)
        assert result[0].symbol == "NEWCO"


class TestMarketIntelligenceClientNews:
    """Test news functionality"""

    def test_stock_news_article_with_null_symbol(self):
        """Test StockNewsArticle accepts null symbol (Issue #62)"""
        data = {
            "symbol": None,
            "publishedDate": "2024-01-15T10:00:00",
            "title": "General Market News",
            "site": "Example News",
            "text": "Article content",
            "url": "https://example.com/article",
        }
        article = StockNewsArticle(**data)
        assert article.symbol is None

    def test_get_fmp_articles_default(self, fmp_client, mock_client):
        """Test get_fmp_articles with default parameters"""
        mock_content = [
            FMPArticle(
                title="Market Analysis",
                date=datetime(2024, 1, 15, 10, 0),
                content="<p>Article content</p>",
                tickers="AAPL,MSFT",
                image="https://example.com/image.jpg",
                link="https://example.com/article",
                author="John Doe",
                site="FMP",
            )
        ]
        mock_response = FMPArticlesResponse(content=mock_content)
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_fmp_articles()

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 20
        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_fmp_articles_custom_params(self, fmp_client, mock_client):
        """Test get_fmp_articles with custom parameters"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_fmp_articles(page=1, limit=10)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 1
        assert kwargs["limit"] == 10

    def test_get_fmp_articles_direct_list(self, fmp_client, mock_client):
        """Test get_fmp_articles when API returns direct list"""
        mock_articles = [
            FMPArticle(
                title="Direct Article",
                date=datetime(2024, 1, 15, 10, 0),
                content="<p>Content</p>",
                tickers="AAPL",
                image="https://example.com/image.jpg",
                link="https://example.com/article",
                author="Jane Doe",
                site="FMP",
            )
        ]
        mock_client.request.return_value = mock_articles

        result = fmp_client.intelligence.get_fmp_articles()

        assert result == mock_articles

    def test_get_general_news(self, fmp_client, mock_client):
        """Test get_general_news"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Market Update",
            "image": "https://example.com/image.jpg",
            "site": "Example News",
            "text": "News content",
            "url": "https://example.com/news",
        }
        mock_client.request.return_value = [GeneralNewsArticle(**mock_data)]

        result = fmp_client.intelligence.get_general_news(page=0)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 20
        assert isinstance(result, list)

    def test_get_general_news_with_dates(self, fmp_client, mock_client):
        """Test get_general_news with date filters"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Market Update",
            "image": "https://example.com/image.jpg",
            "site": "Example News",
            "text": "News content",
            "url": "https://example.com/news",
        }
        mock_client.request.return_value = [GeneralNewsArticle(**mock_data)]

        _ = fmp_client.intelligence.get_general_news(
            page=1,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=10,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 1
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 10

    def test_get_stock_news(self, fmp_client, mock_client, stock_news_data):
        """Test get_stock_news with all parameters"""
        mock_client.request.return_value = [StockNewsArticle(**stock_news_data)]

        _ = fmp_client.intelligence.get_stock_news(
            page=1,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=100,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 1
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 100

    def test_get_stock_news_no_dates(self, fmp_client, mock_client, stock_news_data):
        """Test get_stock_news without date parameters"""
        mock_client.request.return_value = [StockNewsArticle(**stock_news_data)]

        _ = fmp_client.intelligence.get_stock_news("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] is None
        assert kwargs["end_date"] is None

    def test_get_stock_news_sentiments(
        self, fmp_client, mock_client, stock_news_sentiment_data
    ):
        """Test get_stock_news_sentiments emits deprecation warning"""
        import warnings

        # No need to mock request since it won't be called

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = fmp_client.intelligence.get_stock_news_sentiments(page=0)

            # Verify deprecation warning was emitted
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "no longer supports this endpoint" in str(w[0].message)

        # Verify no API call was made
        mock_client.request.assert_not_called()

        # Verify empty result
        assert result == []
        assert isinstance(result, list)

    def test_get_forex_news(self, fmp_client, mock_client):
        """Test get_forex_news"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Forex Update",
            "image": "https://example.com/image.jpg",
            "site": "Forex News",
            "text": "News content",
            "url": "https://example.com/forex",
            "symbol": "EURUSD",
        }
        mock_client.request.return_value = [ForexNewsArticle(**mock_data)]

        _ = fmp_client.intelligence.get_forex_news(
            page=1,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=25,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 25

    def test_get_forex_symbol_news(self, fmp_client, mock_client):
        """Test get_forex_symbol_news"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Forex Update",
            "image": "https://example.com/image.jpg",
            "site": "Forex News",
            "text": "News content",
            "url": "https://example.com/forex",
            "symbol": "EURUSD",
        }
        mock_client.request.return_value = [ForexNewsArticle(**mock_data)]

        _ = fmp_client.intelligence.get_forex_symbol_news(
            symbol="EURUSD",
            page=1,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=25,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "EURUSD"
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 25

    def test_get_crypto_news(self, fmp_client, mock_client):
        """Test get_crypto_news"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Crypto Update",
            "image": "https://example.com/image.jpg",
            "site": "Crypto News",
            "text": "News content",
            "url": "https://example.com/crypto",
            "symbol": "BTCUSD",
        }
        mock_client.request.return_value = [CryptoNewsArticle(**mock_data)]

        _ = fmp_client.intelligence.get_crypto_news(
            page=0,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=20,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 20

    def test_get_crypto_symbol_news(self, fmp_client, mock_client):
        """Test get_crypto_symbol_news"""
        mock_data = {
            "publishedDate": "2024-01-15T10:00:00",
            "title": "Crypto Update",
            "image": "https://example.com/image.jpg",
            "site": "Crypto News",
            "text": "News content",
            "url": "https://example.com/crypto",
            "symbol": "BTC",
        }
        mock_client.request.return_value = [CryptoNewsArticle(**mock_data)]

        _ = fmp_client.intelligence.get_crypto_symbol_news(
            symbol="BTCUSD",
            page=0,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=20,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "BTCUSD"
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 20


class TestMarketIntelligenceClientPressReleases:
    """Test press release functionality"""

    def test_get_press_releases(self, fmp_client, mock_client):
        """Test get_press_releases"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15T10:00:00",
            "title": "Company Update",
            "text": "Press release content",
        }
        mock_client.request.return_value = [PressRelease(**mock_data)]

        _ = fmp_client.intelligence.get_press_releases(
            page=0,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=10,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 10

    def test_get_press_releases_by_symbol(self, fmp_client, mock_client):
        """Test get_press_releases_by_symbol"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15T10:00:00",
            "title": "Company Update",
            "text": "Press release content",
        }
        mock_client.request.return_value = [PressReleaseBySymbol(**mock_data)]

        _ = fmp_client.intelligence.get_press_releases_by_symbol(
            "AAPL",
            page=1,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            limit=15,
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["page"] == 1
        assert kwargs["start_date"] == "2024-01-01"
        assert kwargs["end_date"] == "2024-01-31"
        assert kwargs["limit"] == 15


class TestMarketIntelligenceClientSocialSentiment:
    """Test social sentiment functionality (removed endpoints)"""

    def test_get_historical_social_sentiment_raises_error(
        self, fmp_client, mock_client
    ):
        """Test get_historical_social_sentiment raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_historical_social_sentiment("AAPL", page=0)
        assert "get_historical_social_sentiment" in str(exc_info.value)
        assert "removed" in str(exc_info.value).lower()

    def test_get_trending_social_sentiment_raises_error(self, fmp_client, mock_client):
        """Test get_trending_social_sentiment raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_trending_social_sentiment(
                "bullish", "stocktwits"
            )
        assert "get_trending_social_sentiment" in str(exc_info.value)
        assert "removed" in str(exc_info.value).lower()

    def test_get_social_sentiment_changes_raises_error(self, fmp_client, mock_client):
        """Test get_social_sentiment_changes raises RemovedEndpointError"""
        with pytest.raises(RemovedEndpointError) as exc_info:
            fmp_client.intelligence.get_social_sentiment_changes("bearish", "twitter")
        assert "get_social_sentiment_changes" in str(exc_info.value)
        assert "removed" in str(exc_info.value).lower()

    def test_get_esg_benchmark(self, fmp_client, mock_client):
        """Test get_esg_benchmark"""
        mock_data = {
            "sector": "Technology",
            "environmentalScore": 70.0,  # NOT "averageEnvironmentalScore"
            "socialScore": 60.0,  # NOT "averageSocialScore"
            "governanceScore": 66.5,  # NOT "averageGovernanceScore"
            "ESGScore": 65.5,  # NOT "averageESGScore"
        }
        mock_client.request.return_value = [ESGBenchmark(**mock_data)]

        result = fmp_client.intelligence.get_esg_benchmark()

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert "year" not in kwargs
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].sector == "Technology"
        assert result[0].esg_score == 65.5


class TestMarketIntelligenceClientESG:
    """Test ESG functionality"""

    def test_get_esg_data_single_item(self, fmp_client, mock_client, esg_data):
        """Test get_esg_data when API returns single item"""
        mock_response = ESGData(**esg_data)
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_esg_data("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, ESGData)
        assert result.symbol == "AAPL"

    def test_get_esg_data_list_response(self, fmp_client, mock_client, esg_data):
        """Test get_esg_data when API returns list"""
        mock_response = [ESGData(**esg_data)]
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_esg_data("AAPL")

        assert isinstance(result, ESGData)
        assert result.symbol == "AAPL"

    def test_get_esg_ratings(self, fmp_client, mock_client, esg_rating_data):
        """Test get_esg_ratings"""
        mock_response = [ESGRating(**esg_rating_data)]
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_esg_ratings("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, ESGRating)

    def test_get_esg_benchmark(self, fmp_client, mock_client):
        """Test get_esg_benchmark"""
        mock_data = {
            "sector": "Technology",
            "ESGScore": 65.5,
            "numberOfCompanies": 100,
            "averageESGScore": 65.5,
            "averageEnvironmentalScore": 70.0,
            "averageSocialScore": 60.0,
            "averageGovernanceScore": 66.5,
        }
        mock_client.request.return_value = [ESGBenchmark(**mock_data)]

        _ = fmp_client.intelligence.get_esg_benchmark()

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert "year" not in kwargs


class TestMarketIntelligenceClientGovernment:
    """Test government trading functionality"""

    def test_get_senate_latest(self, fmp_client, mock_client):
        """Test get_senate_latest"""
        mock_data = {
            "symbol": "AAPL",
            "disclosureDate": "2025-01-08",
            "transactionDate": "2024-12-19",
            "firstName": "Sheldon",
            "lastName": "Whitehouse",
            "office": "Sheldon Whitehouse",
            "district": "RI",
            "owner": "Self",
            "assetDescription": "Apple Inc",
            "assetType": "Stock",
            "type": "Sale (Partial)",
            "amount": "$15,001 - $50,000",
            "capitalGainsOver200USD": "False",
            "comment": "--",
            "link": "https://example.com/filing",
        }
        mock_client.request.return_value = [SenateTrade(**mock_data)]

        _ = fmp_client.intelligence.get_senate_latest(page=0, limit=100)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 100

    def test_get_senate_trading(self, fmp_client, mock_client):
        """Test get_senate_trading"""
        mock_data = {
            "firstName": "John",
            "lastName": "Doe",
            "office": "Senate Office",
            "link": "https://example.com/filing",
            "disclosureDate": "2024-01-15T10:00:00",
            "transactionDate": "2024-01-10T10:00:00",
            "owner": "Self",
            "assetDescription": "Apple Inc Common Stock",
            "assetType": "Stock",
            "type": "Purchase",
            "amount": "$15,001-$50,000",
            "comment": "",
            "symbol": "AAPL",
        }
        mock_client.request.return_value = [SenateTrade(**mock_data)]

        _ = fmp_client.intelligence.get_senate_trading("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"

    def test_get_senate_trades_by_name(self, fmp_client, mock_client):
        """Test get_senate_trades_by_name"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_senate_trades_by_name("Jerry")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["name"] == "Jerry"

    def test_get_senate_trading_rss(self, fmp_client, mock_client):
        """Test get_senate_trading_rss"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_senate_trading_rss(page=0)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0

    def test_get_house_latest(self, fmp_client, mock_client):
        """Test get_house_latest"""
        mock_data = {
            "symbol": "AAPL",
            "disclosureDate": "2025-02-03",
            "transactionDate": "2025-01-03",
            "firstName": "Michael",
            "lastName": "Collins",
            "office": "Michael Collins",
            "district": "GA10",
            "owner": "",
            "assetDescription": "VIRTUALS PROTOCOL",
            "assetType": "Cryptocurrency",
            "type": "Purchase",
            "amount": "$1,001 - $15,000",
            "capitalGainsOver200USD": "False",
            "comment": "",
            "link": "https://example.com/filing",
        }
        mock_client.request.return_value = [HouseDisclosure(**mock_data)]

        _ = fmp_client.intelligence.get_house_latest(page=0, limit=100)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 100

    def test_get_house_disclosure(self, fmp_client, mock_client):
        """Test get_house_disclosure"""
        mock_data = {
            "disclosureDate": "2024-01-15T10:00:00",
            "transactionDate": "2024-01-10T10:00:00",
            "owner": "Self",
            "symbol": "AAPL",
            "assetDescription": "Apple Inc Common Stock",
            "type": "Purchase",
            "amount": "$15,001-$50,000",
            "firstName": "Jane",
            "lastName": "Doe",
            "office": "Jane Doe",
            "district": "NY-1",
            "link": "https://example.com/filing",
            "capitalGainsOver200USD": False,
        }
        mock_client.request.return_value = [HouseDisclosure(**mock_data)]

        _ = fmp_client.intelligence.get_house_disclosure("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"

    def test_get_house_trades_by_name(self, fmp_client, mock_client):
        """Test get_house_trades_by_name"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_house_trades_by_name("James")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["name"] == "James"


class TestMarketIntelligenceClientFundraising:
    """Test fundraising functionality"""

    def test_get_crowdfunding_rss(self, fmp_client, mock_client):
        """Test get_crowdfunding_rss"""
        mock_data = {
            # Basic required fields
            "cik": "0001234567",
            "acceptedDate": "2024-01-15T10:00:00",
            "formType": "C",
            "formSignification": "Offering Statement",
            "filingDate": "2024-01-15T00:00:00.000Z",
            # Additional required offering fields
            "offeringAmount": 1000000,  # Added missing required field
            "offeringPrice": 10.0,  # Added missing required field
            # Required offering fields
            "securityOfferedOtherDescription": "Common Stock",
            "numberOfSecurityOffered": 100000,
            "overSubscriptionAccepted": "No",  # String value, not boolean
            "maximumOfferingAmount": 1000000,
            "currentNumberOfEmployees": 10,
            # Required fiscal year financial data (most recent)
            "totalAssetMostRecentFiscalYear": 500000,
            "cashAndCashEquiValentMostRecentFiscalYear": 100000,
            "accountsReceivableMostRecentFiscalYear": 50000,
            "shortTermDebtMostRecentFiscalYear": 20000,
            "longTermDebtMostRecentFiscalYear": 100000,
            "revenueMostRecentFiscalYear": 800000,
            "costGoodsSoldMostRecentFiscalYear": 400000,
            "taxesPaidMostRecentFiscalYear": 50000,
            "netIncomeMostRecentFiscalYear": 150000,
            # Required fiscal year financial data (prior)
            "totalAssetPriorFiscalYear": 400000,
            "cashAndCashEquiValentPriorFiscalYear": 80000,
            "accountsReceivablePriorFiscalYear": 40000,
            "shortTermDebtPriorFiscalYear": 15000,
            "longTermDebtPriorFiscalYear": 80000,
            "revenuePriorFiscalYear": 600000,
            "costGoodsSoldPriorFiscalYear": 300000,
            "taxesPaidPriorFiscalYear": 40000,
            "netIncomePriorFiscalYear": 100000,
        }
        mock_client.request.return_value = [CrowdfundingOffering(**mock_data)]

        result = fmp_client.intelligence.get_crowdfunding_rss(page=0, limit=100)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 100
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].cik == "0001234567"

    def test_search_crowdfunding(self, fmp_client, mock_client):
        """Test search_crowdfunding"""
        mock_client.request.return_value = [
            CrowdfundingOfferingSearchItem(
                cik="0001234567", name="Startup Inc", date="2024-01-15"
            )
        ]

        result = fmp_client.intelligence.search_crowdfunding("startup")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["name"] == "startup"
        assert isinstance(result, list)
        assert isinstance(result[0], CrowdfundingOfferingSearchItem)

    def test_get_crowdfunding_by_cik(self, fmp_client, mock_client):
        """Test get_crowdfunding_by_cik"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_crowdfunding_by_cik("0001234567")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["cik"] == "0001234567"

    def test_get_equity_offering_rss(self, fmp_client, mock_client):
        """Test get_equity_offering_rss"""
        mock_data = {
            # Basic required fields
            "formType": "D",
            "formSignification": "Notice of Exempt Offering",
            "acceptedDate": "2024-01-15T10:00:00",
            "cik": "0001234567",
            "entityName": "Company Inc",
            "entityType": "Corporation",
            "jurisdictionOfIncorporation": "Delaware",
            "yearOfIncorporation": "2020",
            # Required financial amounts
            "totalOfferingAmount": 10000000,
            "totalAmountSold": 5000000,
            "totalAmountRemaining": 5000000,
            # Required issuer information
            "industryGroupType": "Technology",
            "revenueRange": "$1M - $5M",
            "issuerStreet": "123 Main St",
            "issuerCity": "Wilmington",
            "issuerStateOrCountry": "DE",
            "issuerStateOrCountryDescription": "Delaware",
            "issuerZipCode": "19801",
            "issuerPhoneNumber": "555-0123",
            # Required related person information
            "relatedPersonFirstName": "John",
            "relatedPersonLastName": "Doe",
            "relatedPersonStreet": "456 Executive Ave",
            "relatedPersonCity": "Wilmington",
            "relatedPersonStateOrCountry": "DE",
            "relatedPersonStateOrCountryDescription": "Delaware",
            "relatedPersonZipCode": "19801",
            "relatedPersonRelationship": "Director",
            # Required offering details
            "federalExemptionsExclusions": "3(c)(7)",
            "dateOfFirstSale": "2024-01-01",
            "minimumInvestmentAccepted": 250000,
            "totalNumberAlreadyInvested": 25,
            "salesCommissions": 500000,
            "findersFees": 100000,
            "grossProceedsUsed": 8000000,
        }
        mock_client.request.return_value = [EquityOffering(**mock_data)]

        result = fmp_client.intelligence.get_equity_offering_rss(page=0, limit=10)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert kwargs["limit"] == 10
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].cik == "0001234567"
        assert result[0].entity_name == "Company Inc"

    def test_search_equity_offering(self, fmp_client, mock_client):
        """Test search_equity_offering"""
        mock_client.request.return_value = [
            EquityOfferingSearchItem(
                cik="0001234567", name="Company Inc", date=datetime(2024, 1, 1)
            )
        ]

        result = fmp_client.intelligence.search_equity_offering("company")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["name"] == "company"
        assert isinstance(result, list)
        assert isinstance(result[0], EquityOfferingSearchItem)

    def test_get_equity_offering_by_cik(self, fmp_client, mock_client):
        """Test get_equity_offering_by_cik"""
        mock_client.request.return_value = []

        _ = fmp_client.intelligence.get_equity_offering_by_cik("0001234567")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["cik"] == "0001234567"


class TestMarketIntelligenceClientEdgeCases:
    """Test edge cases and error scenarios"""

    def test_empty_responses(self, fmp_client, mock_client):
        """Test handling of empty responses"""
        mock_client.request.return_value = []

        result = fmp_client.intelligence.get_earnings_calendar()
        assert result == []

        result = fmp_client.intelligence.get_general_news()
        assert result == []

    def test_none_dates_handling(self, fmp_client, mock_client):
        """Test handling of None date parameters"""
        mock_client.request.return_value = []

        # Test that None dates don't add parameters
        fmp_client.intelligence.get_stock_news("AAPL", from_date=None, to_date=None)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] is None
        assert kwargs["end_date"] is None

    def test_calendar_methods_no_dates(self, fmp_client, mock_client):
        """Test calendar methods without date parameters"""
        mock_client.request.return_value = []

        # Test various calendar methods without dates
        fmp_client.intelligence.get_earnings_calendar()
        fmp_client.intelligence.get_dividends_calendar()
        fmp_client.intelligence.get_stock_splits_calendar()
        fmp_client.intelligence.get_ipo_calendar()

        # Should have been called 4 times
        assert mock_client.request.call_count == 4

    def test_date_formatting_edge_cases(self, fmp_client, mock_client):
        """Test date formatting with various dates"""
        mock_client.request.return_value = []

        # Test edge dates
        fmp_client.intelligence.get_earnings_calendar(
            start_date=date(2024, 12, 31), end_date=date(2024, 1, 1)
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["start_date"] == "2024-12-31"
        assert kwargs["end_date"] == "2024-01-01"

    def test_fmp_articles_various_responses(self, fmp_client, mock_client):
        """Test FMP articles with various response types"""
        # Test empty response
        mock_client.request.return_value = FMPArticlesResponse(content=[])
        result = fmp_client.intelligence.get_fmp_articles()
        assert result == []

        # Test direct list response
        mock_client.request.return_value = []
        result = fmp_client.intelligence.get_fmp_articles()
        assert result == []

    def test_parameter_combinations(self, fmp_client, mock_client):
        """Test methods with various parameter combinations"""
        mock_client.request.return_value = []

        # Test forex news with all optional parameters
        fmp_client.intelligence.get_forex_news(
            page=None, symbol=None, from_date=None, to_date=None, limit=None
        )

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] is None
        assert kwargs["start_date"] is None
        assert kwargs["end_date"] is None
        assert kwargs["limit"] is None


class TestMarketIntelligenceClientAnalyst:
    """Test analyst ratings and grades functionality"""

    def test_get_ratings_snapshot(self, fmp_client, mock_client):
        """Test get_ratings_snapshot"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15T10:00:00",
            "rating": "Buy",
            "ratingScore": 4,
            "ratingRecommendation": "Strong Buy",
            "ratingDetailsDCFScore": 4,
            "ratingDetailsDCFRecommendation": "Buy",
            "ratingDetailsROEScore": 5,
            "ratingDetailsROERecommendation": "Strong Buy",
            "ratingDetailsROAScore": 4,
            "ratingDetailsROARecommendation": "Buy",
            "ratingDetailsDEScore": 3,
            "ratingDetailsDERecommendation": "Hold",
            "ratingDetailsPEScore": 3,
            "ratingDetailsPERecommendation": "Hold",
            "ratingDetailsPBScore": 4,
            "ratingDetailsPBRecommendation": "Buy",
        }
        mock_response = RatingsSnapshot(**mock_data)
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_ratings_snapshot("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, RatingsSnapshot)
        assert result.symbol == "AAPL"
        assert result.rating == "Buy"

    def test_get_ratings_snapshot_list_response(self, fmp_client, mock_client):
        """Test get_ratings_snapshot when API returns list"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15T10:00:00",
            "rating": "Buy",
            "ratingScore": 4,
            "ratingRecommendation": "Strong Buy",
            "ratingDetailsDCFScore": 4,
            "ratingDetailsDCFRecommendation": "Buy",
            "ratingDetailsROEScore": 5,
            "ratingDetailsROERecommendation": "Strong Buy",
            "ratingDetailsROAScore": 4,
            "ratingDetailsROARecommendation": "Buy",
            "ratingDetailsDEScore": 3,
            "ratingDetailsDERecommendation": "Hold",
            "ratingDetailsPEScore": 3,
            "ratingDetailsPERecommendation": "Hold",
            "ratingDetailsPBScore": 4,
            "ratingDetailsPBRecommendation": "Buy",
        }
        mock_response = [RatingsSnapshot(**mock_data)]
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_ratings_snapshot("AAPL")

        assert isinstance(result, RatingsSnapshot)
        assert result.symbol == "AAPL"

    def test_get_ratings_historical(self, fmp_client, mock_client):
        """Test get_ratings_historical"""
        mock_data = {
            "symbol": "AAPL",
            "date": "2024-01-15T10:00:00",
            "rating": "Buy",
            "ratingScore": 4,
            "ratingRecommendation": "Strong Buy",
            "ratingDetailsDCFScore": 4,
            "ratingDetailsDCFRecommendation": "Buy",
            "ratingDetailsROEScore": 5,
            "ratingDetailsROERecommendation": "Strong Buy",
            "ratingDetailsROAScore": 4,
            "ratingDetailsROARecommendation": "Buy",
            "ratingDetailsDEScore": 3,
            "ratingDetailsDERecommendation": "Hold",
            "ratingDetailsPEScore": 3,
            "ratingDetailsPERecommendation": "Hold",
            "ratingDetailsPBScore": 4,
            "ratingDetailsPBRecommendation": "Buy",
        }
        mock_client.request.return_value = [HistoricalRating(**mock_data)]

        result = fmp_client.intelligence.get_ratings_historical("AAPL", limit=50)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["limit"] == 50
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].symbol == "AAPL"

    def test_get_price_target_news(self, fmp_client, mock_client):
        """Test get_price_target_news"""
        mock_data = {
            "symbol": "AAPL",
            "publishedDate": "2024-01-15T10:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Analyst Raises Price Target for AAPL",
            "analystName": "John Doe",
            "priceTarget": 200.0,
            "adjPriceTarget": 200.0,
            "priceWhenPosted": 180.0,
            "newsPublisher": "Financial Times",
            "newsBaseURL": "https://example.com",
            "analystCompany": "Morgan Stanley",
        }
        mock_client.request.return_value = [PriceTargetNews(**mock_data)]

        result = fmp_client.intelligence.get_price_target_news("AAPL", page=1)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["page"] == 1
        assert isinstance(result, list)
        assert result[0].price_target == 200.0

    def test_get_price_target_latest_news(self, fmp_client, mock_client):
        """Test get_price_target_latest_news"""
        mock_data = {
            "symbol": "AAPL",
            "publishedDate": "2024-01-15T10:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Latest Price Target Updates",
            "analystName": "Jane Smith",
            "priceTarget": 210.0,
            "adjPriceTarget": 210.0,
            "priceWhenPosted": 185.0,
            "newsPublisher": "Reuters",
            "newsBaseURL": "https://reuters.com",
            "analystCompany": "Goldman Sachs",
        }
        mock_client.request.return_value = [PriceTargetNews(**mock_data)]

        result = fmp_client.intelligence.get_price_target_latest_news(page=0)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert isinstance(result, list)

    def test_get_grades(self, fmp_client, mock_client):
        """Test get_grades"""
        mock_data = {
            "symbol": "AAPL",
            "publishedDate": "2024-01-15T10:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "AAPL Upgraded to Buy",
            "newsBaseURL": "https://example.com",
            "newsPublisher": "MarketWatch",
            "newGrade": "Buy",
            "previousGrade": "Hold",
            "gradingCompany": "JP Morgan",
            "action": "upgrade",
            "priceWhenPosted": 180.50,
        }
        mock_client.request.return_value = [StockGrade(**mock_data)]

        result = fmp_client.intelligence.get_grades("AAPL", page=2)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["page"] == 2
        assert isinstance(result, list)
        assert result[0].new_grade == "Buy"

    def test_get_grades_historical(self, fmp_client, mock_client):
        """Test get_grades_historical"""
        mock_data = {
            "symbol": "AAPL",
            "publishedDate": "2024-01-15T10:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Historical Grade Change",
            "newsBaseURL": "https://example.com",
            "newsPublisher": "Bloomberg",
            "newGrade": "Strong Buy",
            "previousGrade": "Buy",
            "gradingCompany": "Bank of America",
            "action": "upgrade",
            "priceWhenPosted": 175.25,
        }
        mock_client.request.return_value = [HistoricalStockGrade(**mock_data)]

        result = fmp_client.intelligence.get_grades_historical("AAPL", limit=200)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["limit"] == 200
        assert isinstance(result, list)

    def test_get_grades_consensus(self, fmp_client, mock_client):
        """Test get_grades_consensus"""
        mock_data = {
            "symbol": "AAPL",
            "consensus": "Buy",
            "strongBuy": 15,
            "buy": 20,
            "hold": 5,
            "sell": 2,
            "strongSell": 1,
        }
        mock_response = StockGradesConsensus(**mock_data)
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_grades_consensus("AAPL")

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert isinstance(result, StockGradesConsensus)
        assert result.consensus == "Buy"

    def test_get_grades_consensus_list_response(self, fmp_client, mock_client):
        """Test get_grades_consensus when API returns list"""
        mock_data = {
            "symbol": "AAPL",
            "consensus": "Hold",
            "strongBuy": 10,
            "buy": 15,
            "hold": 10,
            "sell": 3,
            "strongSell": 2,
        }
        mock_response = [StockGradesConsensus(**mock_data)]
        mock_client.request.return_value = mock_response

        result = fmp_client.intelligence.get_grades_consensus("AAPL")

        assert isinstance(result, StockGradesConsensus)
        assert result.consensus == "Hold"

    def test_get_grades_news(self, fmp_client, mock_client):
        """Test get_grades_news"""
        mock_data = {
            "symbol": "AAPL",
            "publishedDate": "2024-01-15T10:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Grade News for AAPL",
            "newsBaseURL": "https://example.com",
            "newsPublisher": "CNBC",
            "newGrade": "Neutral",
            "previousGrade": "Buy",
            "gradingCompany": "Citigroup",
            "action": "downgrade",
            "priceWhenPosted": 182.75,
        }
        mock_client.request.return_value = [StockGradeNews(**mock_data)]

        result = fmp_client.intelligence.get_grades_news("AAPL", page=1)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["symbol"] == "AAPL"
        assert kwargs["page"] == 1
        assert isinstance(result, list)
        assert result[0].action == "downgrade"

    def test_get_grades_latest_news(self, fmp_client, mock_client):
        """Test get_grades_latest_news"""
        mock_data = {
            "symbol": "MSFT",
            "publishedDate": "2024-01-15T12:00:00",
            "newsURL": "https://example.com/latest",
            "newsTitle": "Latest Grade Updates",
            "newsBaseURL": "https://example.com",
            "newsPublisher": "WSJ",
            "newGrade": "Strong Buy",
            "previousGrade": "Buy",
            "gradingCompany": "Wells Fargo",
            "action": "upgrade",
            "priceWhenPosted": 395.50,
        }
        mock_client.request.return_value = [StockGradeNews(**mock_data)]

        result = fmp_client.intelligence.get_grades_latest_news(page=0)

        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["page"] == 0
        assert isinstance(result, list)
        assert result[0].symbol == "MSFT"
