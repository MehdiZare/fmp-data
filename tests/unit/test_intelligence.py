from datetime import date, datetime
from unittest.mock import Mock

import pytest
from pydantic import HttpUrl

from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    DividendEvent,
    FMPArticle,
    FMPArticlesResponse,
    GeneralNewsArticle,
    IPOEvent,
    PressRelease,
    PriceTarget,
    PriceTargetSummary,
    StockNewsArticle,
    StockNewsSentiment,
)


# Fixtures for mock client and fmp_client
@pytest.fixture
def mock_client():
    """Fixture to mock the API client."""
    return Mock()


@pytest.fixture
def fmp_client(mock_client):
    """Fixture to create an instance of MarketIntelligenceClient
    with a mocked client."""
    return MarketIntelligenceClient(client=mock_client)


# Fixtures for mock data
@pytest.fixture
def price_target_data():
    return [
        {
            "symbol": "AAPL",
            "publishedDate": "2024-01-01T12:00:00",
            "newsURL": "https://example.com/news",
            "newsTitle": "Apple price target increased",
            "analystName": "John Doe",
            "priceTarget": 200.0,
            "adjPriceTarget": 198.0,
            "priceWhenPosted": 150.0,
            "newsPublisher": "Example News",
            "newsBaseURL": "example.com",
            "analystCompany": "Big Bank",
        }
    ]


@pytest.fixture
def price_target_summary_data():
    return {
        "symbol": "AAPL",
        "lastMonth": 10,
        "lastMonthAvgPriceTarget": 190.0,
        "lastQuarter": 30,
        "lastQuarterAvgPriceTarget": 185.0,
        "lastYear": 100,
        "lastYearAvgPriceTarget": 180.0,
        "allTime": 300,
        "allTimeAvgPriceTarget": 175.0,
        "publishers": '["Example News", "Tech Daily"]',
    }


@pytest.fixture
def analyst_estimates_data():
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-01T12:00:00",
            "estimatedRevenueLow": 50000000.0,
            "estimatedRevenueHigh": 55000000.0,
            "estimatedRevenueAvg": 52500000.0,
            "estimatedEbitdaLow": 12000000.0,
            "estimatedEbitdaHigh": 13000000.0,
            "estimatedEbitdaAvg": 12500000.0,
            "estimatedEbitLow": 10000000.0,
            "estimatedEbitHigh": 11000000.0,
            "estimatedEbitAvg": 10500000.0,
            "estimatedNetIncomeLow": 8000000.0,
            "estimatedNetIncomeHigh": 9000000.0,
            "estimatedNetIncomeAvg": 8500000.0,
            "estimatedSgaExpenseLow": 2000000.0,
            "estimatedSgaExpenseHigh": 2500000.0,
            "estimatedSgaExpenseAvg": 2250000.0,
            "estimatedEpsLow": 3.5,
            "estimatedEpsHigh": 4.0,
            "estimatedEpsAvg": 3.75,
            "numberAnalystEstimatedRevenue": 10,
            "numberAnalystsEstimatedEps": 8,
        }
    ]


@pytest.fixture
def dividends_calendar_data():
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-15",
            "label": "Jan 15, 2024",
            "adjDividend": 0.22,
            "dividend": 0.2,
            "recordDate": "2024-01-10",
            "paymentDate": "2024-01-20",
            "declarationDate": "2023-12-15",
        }
    ]


@pytest.fixture
def ipo_calendar_data():
    return [
        {
            "symbol": "NEWCO",
            "company": "New Company",
            "date": "2024-02-01",
            "exchange": "NASDAQ",
            "actions": "IPO Scheduled",
            "shares": 1000000,
            "priceRange": "15-18",
            "marketCap": 17000000,
        }
    ]


# Tests
def test_get_price_target(fmp_client, mock_client, price_target_data):
    """Test fetching price targets"""
    mock_client.request.return_value = [PriceTarget(**price_target_data[0])]
    result = fmp_client.get_price_target(symbol="AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], PriceTarget)
    assert result[0].symbol == "AAPL"


def test_get_price_target_summary(fmp_client, mock_client, price_target_summary_data):
    """Test fetching price target summary"""
    mock_client.request.return_value = PriceTargetSummary(**price_target_summary_data)
    result = fmp_client.get_price_target_summary(symbol="AAPL")
    assert isinstance(result, PriceTargetSummary)
    assert result.symbol == "AAPL"
    assert result.last_month_avg_price_target == 190.0


def test_get_analyst_estimates(fmp_client, mock_client, analyst_estimates_data):
    """Test fetching analyst estimates"""
    mock_client.request.return_value = [AnalystEstimate(**analyst_estimates_data[0])]
    result = fmp_client.get_analyst_estimates(symbol="AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], AnalystEstimate)
    assert result[0].symbol == "AAPL"
    assert result[0].estimated_revenue_avg == 52500000.0


def test_get_dividends_calendar(fmp_client, mock_client, dividends_calendar_data):
    """Test fetching dividends calendar"""
    mock_client.request.return_value = [DividendEvent(**dividends_calendar_data[0])]
    result = fmp_client.get_dividends_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )
    assert isinstance(result, list)
    assert isinstance(result[0], DividendEvent)
    assert result[0].symbol == "AAPL"
    assert result[0].dividend == 0.2


def test_get_ipo_calendar(fmp_client, mock_client, ipo_calendar_data):
    """Test fetching IPO calendar"""
    mock_client.request.return_value = [IPOEvent(**ipo_calendar_data[0])]
    result = fmp_client.get_ipo_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
    )
    assert isinstance(result, list)
    assert isinstance(result[0], IPOEvent)
    assert result[0].symbol == "NEWCO"
    assert result[0].company == "New Company"


@pytest.fixture
def general_news_data():
    return [
        {
            "publishedDate": "2024-12-08T12:00:00.000Z",
            "title": "Major Economic Report Released",
            "image": "https://example.com/image.jpg",
            "site": "financial-news.com",
            "text": "A comprehensive economic report shows...",
            "url": "https://financial-news.com/article",
        }
    ]


@pytest.fixture
def stock_news_data():
    return [
        {
            "symbol": "AAPL",
            "publishedDate": "2024-12-08T14:30:00.000Z",
            "title": "Apple Announces New Product Line",
            "image": "https://example.com/image.jpg",
            "site": "market-news.com",
            "text": "Apple Inc. today announced...",
            "url": "https://market-news.com/article",
        }
    ]


@pytest.fixture
def stock_news_sentiment_data():
    return [
        {
            "symbol": "TSLA",
            "publishedDate": "2024-12-08T15:45:00.000Z",
            "title": "Tesla Beats Delivery Estimates",
            "image": "https://example.com/image.jpg",
            "site": "market-analysis.com",
            "text": "Tesla has exceeded delivery estimates...",
            "url": "https://market-analysis.com/article",
            "sentiment": "Positive",
            "sentimentScore": 0.85,
        }
    ]


@pytest.fixture
def press_release_data():
    return [
        {
            "symbol": "MSFT",
            "date": "2024-12-08T16:00:00",
            "title": "Microsoft Quarterly Results",
            "text": "Microsoft Corporation today announced...",
        }
    ]


@pytest.fixture
def fmp_articles_data():
    return {
        "content": [
            {
                "title": "The AI Opportunity for the Global Telecom Sector",
                "date": "2024-12-08 05:20:23",
                "content": "<p>The global telecom industry is on the verge...</p>",
            }
        ]
    }


def test_get_general_news(fmp_client, mock_client, general_news_data):
    mock_client.request.return_value = [GeneralNewsArticle(**general_news_data[0])]

    result = fmp_client.get_general_news(page=0)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], GeneralNewsArticle)
    assert result[0].site == "financial-news.com"
    assert isinstance(result[0].publishedDate, datetime)
    assert isinstance(result[0].image, HttpUrl)


def test_get_stock_news(fmp_client, mock_client, stock_news_data):
    mock_client.request.return_value = [StockNewsArticle(**stock_news_data[0])]

    result = fmp_client.get_stock_news(
        tickers="AAPL", page=0, from_date=date(2024, 1, 1), to_date=date(2024, 12, 31)
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], StockNewsArticle)
    assert result[0].symbol == "AAPL"
    assert isinstance(result[0].url, HttpUrl)


def test_get_stock_news_sentiment(fmp_client, mock_client, stock_news_sentiment_data):
    mock_client.request.return_value = [
        StockNewsSentiment(**stock_news_sentiment_data[0])
    ]

    result = fmp_client.get_stock_news_sentiments(page=0)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], StockNewsSentiment)
    assert result[0].symbol == "TSLA"
    assert result[0].sentiment == "Positive"
    assert result[0].sentimentScore == 0.85


def test_get_press_releases(fmp_client, mock_client, press_release_data):
    mock_client.request.return_value = [PressRelease(**press_release_data[0])]

    result = fmp_client.get_press_releases(page=0)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], PressRelease)
    assert result[0].symbol == "MSFT"
    assert isinstance(result[0].date, datetime)


def test_get_fmp_articles(fmp_client, mock_client, fmp_articles_data):
    mock_client.request.return_value = FMPArticlesResponse(**fmp_articles_data)

    result = fmp_client.get_fmp_articles(page=0, size=5)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FMPArticle)
    assert result[0].title == "The AI Opportunity for the Global Telecom Sector"
    assert isinstance(result[0].date, datetime)
    assert result[0].content.startswith("<p>")
