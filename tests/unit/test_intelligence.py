from datetime import date, datetime
from unittest.mock import Mock

import pytest

from fmp_data.intelligence.models import (
    CryptoNewsArticle,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    ESGData,
    ESGRating,
    FMPArticle,
    ForexNewsArticle,
    GeneralNewsArticle,
    HistoricalSocialSentiment,
    HouseDisclosure,
    IPOEvent,
    PressRelease,
    PressReleaseBySymbol,
    SenateTrade,
    StockNewsArticle,
    StockNewsSentiment,
    StockSplitEvent,
    TrendingSocialSentiment,
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
    client._intelligence = mock_client  # Use private attribute
    return client


# Calendar Event Test Fixtures
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


# ESG Test Fixtures
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


# News Test Fixtures
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


@pytest.fixture
def earnings_surprises_data():
    return {
        "symbol": "AAPL",
        "date": "2024-01-15",
        "actualEarningResult": 1.25,
        "estimatedEarning": 1.20,
    }


@pytest.fixture
def historical_earnings_data():
    return {
        "symbol": "AAPL",
        "date": "2024-01-15",
        "eps": 1.25,
        "epsEstimated": 1.20,
        "time": "amc",
        "revenue": 1000000000,
        "revenueEstimated": 950000000,
        "fiscalDateEnding": "2024-03-31",
        "updatedFromDate": "2024-01-01",
    }


@pytest.fixture
def stock_splits_calendar_data():
    return {
        "symbol": "AAPL",
        "date": "2024-01-15",
        "label": "Jan 15, 2024",
        "numerator": 4,
        "denominator": 1,
    }


@pytest.fixture
def fmp_articles_data():
    return {
        "content": [
            {
                "title": "Market Analysis",
                "date": "2024-01-15T10:00:00",
                "content": "<p>Article content</p>",
                "tickers": "AAPL,MSFT",
                "image": "https://example.com/image.jpg",
                "link": "https://example.com/article",
                "author": "John Doe",
                "site": "FMP",
            }
        ]
    }


@pytest.fixture
def general_news_data():
    return {
        "publishedDate": "2024-01-15T10:00:00",
        "title": "Market Update",
        "image": "https://example.com/image.jpg",
        "site": "Example News",
        "text": "News content",
        "url": "https://example.com/news",
    }


@pytest.fixture
def forex_news_data():
    return {
        "publishedDate": "2024-01-15T10:00:00",
        "title": "Forex Update",
        "image": "https://example.com/image.jpg",
        "site": "Forex News",
        "text": "News content",
        "url": "https://example.com/forex",
        "symbol": "EURUSD",
    }


@pytest.fixture
def crypto_news_data():
    return {
        "publishedDate": "2024-01-15T10:00:00",
        "title": "Crypto Update",
        "image": "https://example.com/image.jpg",
        "site": "Crypto News",
        "text": "News content",
        "url": "https://example.com/crypto",
        "symbol": "BTC",
    }


@pytest.fixture
def press_release_data():
    return {
        "symbol": "AAPL",
        "date": "2024-01-15T10:00:00",
        "title": "Company Update",
        "text": "Press release content",
    }


@pytest.fixture
def historical_social_sentiment_data():
    return {
        "date": "2024-01-15T10:00:00",
        "symbol": "AAPL",
        "stocktwitsPosts": 1000,
        "twitterPosts": 2000,
        "stocktwitsComments": 500,
        "twitterComments": 1000,
        "stocktwitsLikes": 1500,
        "twitterLikes": 3000,
        "stocktwitsImpressions": 5000,
        "twitterImpressions": 10000,
        "stocktwitsSentiment": 0.75,
        "twitterSentiment": 0.80,
    }


@pytest.fixture
def trending_social_sentiment_data():
    return {
        "symbol": "AAPL",
        "name": "Apple Inc",
        "rank": 1,
        "sentiment": 0.85,
        "lastSentiment": 0.80,
    }


@pytest.fixture
def senate_trade_data():
    return {
        "firstName": "John",
        "lastName": "Doe",
        "office": "Senate Office",
        "link": "https://example.com/filing",
        "dateRecieved": "2024-01-15T10:00:00",
        "transactionDate": "2024-01-10T10:00:00",
        "owner": "Self",
        "assetDescription": "Apple Inc Common Stock",
        "assetType": "Stock",
        "type": "Purchase",
        "amount": "$15,001-$50,000",
        "comment": "",
        "symbol": "AAPL",
    }


@pytest.fixture
def house_disclosure_data():
    return {
        "disclosureYear": "2024",
        "disclosureDate": "2024-01-15T10:00:00",
        "transactionDate": "2024-01-10T10:00:00",
        "owner": "Self",
        "ticker": "AAPL",
        "assetDescription": "Apple Inc Common Stock",
        "type": "Purchase",
        "amount": "$15,001-$50,000",
        "representative": "Jane Doe",
        "district": "NY-1",
        "link": "https://example.com/filing",
        "capitalGainsOver200USD": False,
    }


@pytest.fixture
def crowdfunding_data():
    return {
        "cik": "0001234567",
        "companyName": "Startup Inc",
        "acceptanceTime": "2024-01-15T10:00:00",
        "formType": "C",
        "formSignification": "Offering Statement",
        "fillingDate": "2024-01-15T00:00:00.000Z",
        "nameOfIssuer": "Startup Inc",
        "offeringAmount": 1000000,
        "offeringPrice": 10,
    }


@pytest.fixture
def equity_offering_data():
    return {
        "formType": "D",
        "formSignification": "Notice of Exempt Offering",
        "acceptanceTime": "2024-01-15T10:00:00",
        "cik": "0001234567",
        "entityName": "Company Inc",
        "entityType": "Corporation",
        "jurisdictionOfIncorporation": "Delaware",
        "yearOfIncorporation": "2020",
        "totalOfferingAmount": 10000000,
        "totalAmountSold": 5000000,
        "totalAmountRemaining": 5000000,
    }


# Calendar Event Tests
def test_get_earnings_calendar(fmp_client, mock_client, earnings_calendar_data):
    mock_client.get_earnings_calendar.return_value = [
        EarningEvent(**earnings_calendar_data)
    ]

    result = fmp_client.intelligence.get_earnings_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], EarningEvent)
    assert result[0].symbol == "AAPL"
    assert result[0].eps == 1.25


def test_get_earnings_confirmed(fmp_client, mock_client, earnings_confirmed_data):
    mock_client.get_earnings_confirmed.return_value = [
        EarningConfirmed(**earnings_confirmed_data)
    ]

    result = fmp_client.intelligence.get_earnings_confirmed(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], EarningConfirmed)
    assert result[0].symbol == "AAPL"
    assert result[0].exchange == "NASDAQ"


def test_get_dividends_calendar(fmp_client, mock_client, dividends_calendar_data):
    mock_client.get_dividends_calendar.return_value = [
        DividendEvent(**dividends_calendar_data)
    ]

    result = fmp_client.intelligence.get_dividends_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], DividendEvent)
    assert result[0].symbol == "AAPL"
    assert result[0].dividend == 0.20


def test_get_ipo_calendar(fmp_client, mock_client, ipo_calendar_data):
    mock_client.get_ipo_calendar.return_value = [IPOEvent(**ipo_calendar_data)]

    result = fmp_client.intelligence.get_ipo_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], IPOEvent)
    assert result[0].symbol == "NEWCO"
    assert result[0].company == "New Company"


# ESG Tests
def test_get_esg_data(fmp_client, mock_client, esg_data):
    mock_client.get_esg_data.return_value = ESGData(**esg_data)

    result = fmp_client.intelligence.get_esg_data(symbol="AAPL")

    assert isinstance(result, ESGData)
    assert result.symbol == "AAPL"
    assert result.environmental_score == 68.47
    assert result.social_score == 47.02
    assert result.governance_score == 60.8


def test_get_esg_ratings(fmp_client, mock_client, esg_rating_data):
    mock_client.get_esg_ratings.return_value = ESGRating(**esg_rating_data)

    result = fmp_client.intelligence.get_esg_ratings(symbol="AAPL")

    assert isinstance(result, ESGRating)
    assert result.symbol == "AAPL"
    assert result.esg_risk_rating == "Low Risk"
    assert result.industry_rank == "1 of 50"


# News Tests
def test_get_stock_news(fmp_client, mock_client, stock_news_data):
    mock_client.get_stock_news.return_value = [StockNewsArticle(**stock_news_data)]

    result = fmp_client.intelligence.get_stock_news(
        tickers="AAPL", page=0, from_date=date(2024, 1, 1), to_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], StockNewsArticle)
    assert result[0].symbol == "AAPL"
    assert result[0].title == "Apple Announces New Product"


def test_get_stock_news_sentiments(fmp_client, mock_client, stock_news_sentiment_data):
    mock_client.get_stock_news_sentiments.return_value = [
        StockNewsSentiment(**stock_news_sentiment_data)
    ]

    result = fmp_client.intelligence.get_stock_news_sentiments(page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], StockNewsSentiment)
    assert result[0].symbol == "AAPL"
    assert result[0].sentiment == "Positive"
    assert result[0].sentimentScore == 0.85


# Error Cases
def test_get_earnings_calendar_empty(fmp_client, mock_client):
    mock_client.get_earnings_calendar.return_value = []

    result = fmp_client.intelligence.get_earnings_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_esg_data_none_response(fmp_client, mock_client):
    mock_client.get_esg_data.return_value = None

    result = fmp_client.intelligence.get_esg_data(symbol="INVALID")

    assert result is None


def test_get_earnings_surprises(fmp_client, mock_client, earnings_surprises_data):
    mock_client.get_earnings_surprises.return_value = [
        EarningSurprise(**earnings_surprises_data)
    ]

    result = fmp_client.intelligence.get_earnings_surprises(symbol="AAPL")

    assert isinstance(result, list)
    assert isinstance(result[0], EarningSurprise)
    assert result[0].symbol == "AAPL"
    assert result[0].actual_earning_result == 1.25


def test_get_historical_earnings(fmp_client, mock_client, historical_earnings_data):
    mock_client.get_historical_earnings.return_value = [
        EarningEvent(**historical_earnings_data)
    ]

    result = fmp_client.intelligence.get_historical_earnings(symbol="AAPL")

    assert isinstance(result, list)
    assert isinstance(result[0], EarningEvent)
    assert result[0].symbol == "AAPL"
    assert result[0].eps == 1.25


def test_get_stock_splits_calendar(fmp_client, mock_client, stock_splits_calendar_data):
    mock_client.get_stock_splits_calendar.return_value = [
        StockSplitEvent(**stock_splits_calendar_data)
    ]

    result = fmp_client.intelligence.get_stock_splits_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )

    assert isinstance(result, list)
    assert isinstance(result[0], StockSplitEvent)
    assert result[0].symbol == "AAPL"
    assert result[0].numerator == 4


def test_get_fmp_articles(fmp_client, mock_client, fmp_articles_data):
    mock_client.get_fmp_articles.return_value = [
        FMPArticle(**fmp_articles_data["content"][0])
    ]

    result = fmp_client.intelligence.get_fmp_articles(page=0, size=5)

    assert isinstance(result, list)
    assert isinstance(result[0], FMPArticle)
    assert result[0].title == "Market Analysis"
    assert result[0].author == "John Doe"


def test_get_general_news(fmp_client, mock_client, general_news_data):
    mock_client.get_general_news.return_value = [
        GeneralNewsArticle(**general_news_data)
    ]

    result = fmp_client.intelligence.get_general_news(page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], GeneralNewsArticle)
    assert result[0].title == "Market Update"
    assert isinstance(result[0].publishedDate, datetime)


def test_get_forex_news(fmp_client, mock_client, forex_news_data):
    mock_client.get_forex_news.return_value = [ForexNewsArticle(**forex_news_data)]

    result = fmp_client.intelligence.get_forex_news(symbol="EURUSD", page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], ForexNewsArticle)
    assert result[0].symbol == "EURUSD"
    assert isinstance(result[0].publishedDate, datetime)


def test_get_crypto_news(fmp_client, mock_client, crypto_news_data):
    mock_client.get_crypto_news.return_value = [CryptoNewsArticle(**crypto_news_data)]

    result = fmp_client.intelligence.get_crypto_news(symbol="BTC", page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], CryptoNewsArticle)
    assert result[0].symbol == "BTC"
    assert isinstance(result[0].publishedDate, datetime)


def test_get_press_releases(fmp_client, mock_client, press_release_data):
    mock_client.get_press_releases.return_value = [PressRelease(**press_release_data)]

    result = fmp_client.intelligence.get_press_releases(page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], PressRelease)
    assert result[0].symbol == "AAPL"
    assert isinstance(result[0].date, datetime)


def test_get_press_releases_by_symbol(fmp_client, mock_client, press_release_data):
    mock_client.get_press_releases_by_symbol.return_value = [
        PressReleaseBySymbol(**press_release_data)
    ]

    result = fmp_client.intelligence.get_press_releases_by_symbol(symbol="AAPL", page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], PressReleaseBySymbol)
    assert result[0].symbol == "AAPL"
    assert isinstance(result[0].date, datetime)


def test_get_historical_social_sentiment(
    fmp_client, mock_client, historical_social_sentiment_data
):
    mock_client.get_historical_social_sentiment.return_value = [
        HistoricalSocialSentiment(**historical_social_sentiment_data)
    ]

    result = fmp_client.intelligence.get_historical_social_sentiment(
        symbol="AAPL", page=0
    )

    assert isinstance(result, list)
    assert isinstance(result[0], HistoricalSocialSentiment)
    assert result[0].symbol == "AAPL"
    assert result[0].stocktwitsSentiment == 0.75


def test_get_trending_social_sentiment(
    fmp_client, mock_client, trending_social_sentiment_data
):
    mock_client.get_trending_social_sentiment.return_value = [
        TrendingSocialSentiment(**trending_social_sentiment_data)
    ]

    result = fmp_client.intelligence.get_trending_social_sentiment(
        type="bullish", source="stocktwits"
    )

    assert isinstance(result, list)
    assert isinstance(result[0], TrendingSocialSentiment)
    assert result[0].symbol == "AAPL"
    assert result[0].sentiment == 0.85


def test_get_senate_trading(fmp_client, mock_client, senate_trade_data):
    mock_client.get_senate_trading.return_value = [SenateTrade(**senate_trade_data)]

    result = fmp_client.intelligence.get_senate_trading(symbol="AAPL")

    assert isinstance(result, list)
    assert isinstance(result[0], SenateTrade)
    assert result[0].symbol == "AAPL"
    assert result[0].asset_type == "Stock"


def test_get_senate_trading_rss(fmp_client, mock_client, senate_trade_data):
    mock_client.get_senate_trading_rss.return_value = [SenateTrade(**senate_trade_data)]

    result = fmp_client.intelligence.get_senate_trading_rss(page=0)

    assert isinstance(result, list)
    assert isinstance(result[0], SenateTrade)
    assert result[0].symbol == "AAPL"
    assert result[0].asset_type == "Stock"


def test_get_house_disclosure(fmp_client, mock_client, house_disclosure_data):
    mock_client.get_house_disclosure.return_value = [
        HouseDisclosure(**house_disclosure_data)
    ]

    result = fmp_client.intelligence.get_house_disclosure(symbol="AAPL")

    assert isinstance(result, list)
    assert isinstance(result[0], HouseDisclosure)
    assert result[0].ticker == "AAPL"
    assert result[0].representative == "Jane Doe"
