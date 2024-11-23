from datetime import date
from unittest.mock import Mock

import pytest

from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    DividendEvent,
    IPOEvent,
    PriceTarget,
    PriceTargetSummary,
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
