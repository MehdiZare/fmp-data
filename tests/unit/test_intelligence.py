from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from pydantic import HttpUrl

from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    CrowdfundingOffering,
    DividendEvent,
    EquityOffering,
    ESGBenchmark,
    ESGData,
    ESGRating,
    FMPArticle,
    FMPArticlesResponse,
    GeneralNewsArticle,
    HouseDisclosure,
    IPOEvent,
    PressRelease,
    PriceTarget,
    PriceTargetSummary,
    SenateTrade,
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


# New fixtures for mock data
@pytest.fixture
def esg_data():
    """Mock ESG data"""
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
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/0000320193-24-000123-index.htm",
    }


@pytest.fixture
def esg_rating_data():
    """Mock ESG rating data"""
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "companyName": "Apple Inc.",
        "industry": "CONSUMER ELECTRONICS",
        "year": 2024,
        "ESGRiskRating": "B",
        "industryRank": "4 out of 5",
    }


@pytest.fixture
def esg_benchmark_data():
    """Mock ESG benchmark data"""
    return {
        "year": 2022,
        "sector": "INSURANCE—DIVERSIFIED",
        "environmentalScore": 55.02,
        "socialScore": 60.79,
        "governanceScore": 58.67,
        "ESGScore": 58.16,
    }


@pytest.fixture
def senate_trade_data():
    """Mock Senate trading data"""
    return {
        "firstName": "Tommy",
        "lastName": "Tuberville",
        "office": "Tommy Tuberville",
        "link": "https://efdsearch.senate.gov/search/view/ptr/fb8e7c07-ad6c-48e0-a6af-de9bf58827d6/",
        "dateRecieved": "2024-11-15",
        "transactionDate": "2024-10-29",
        "owner": "Joint",
        "assetDescription": "Apple Inc",
        "assetType": "Stock",
        "type": "Sale",
        "amount": "$15,001 - $50,000",
        "comment": "",
        "symbol": "AAPL",
    }


@pytest.fixture
def house_disclosure_data():
    """Mock House disclosure data"""
    return {
        "disclosureYear": "2024",
        "disclosureDate": "2024-11-22",
        "transactionDate": "2024-10-07",
        "owner": "Spouse",
        "ticker": "AAPL",
        "assetDescription": "Apple Inc",
        "type": "Purchase",
        "amount": "$15,001 - $50,000",
        "representative": "Laurel Lee",
        "district": "FL15",
        "link": "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/20026063.pdf",
        "capitalGainsOver200USD": "False",
    }


@pytest.fixture
def crowdfunding_data():
    """Mock crowdfunding offering data"""
    return {
        "cik": "0002045906",
        "companyName": "ArroFi Inc.",
        "acceptanceTime": "2024-12-10 17:20:17",
        "formType": "C",
        "formSignification": "Offering Statement",
        "fillingDate": "2024-12-10T00:00:00.000Z",
        "date": "12-10-2024",
        "nameOfIssuer": "ArroFi Inc.",
        "legalStatusForm": "Limited Liability Company",
        "jurisdictionOrganization": "DE",
        "issuerStreet": "4104 24TH ST",
        "issuerCity": "San Francisco",
        "issuerStateOrCountry": "CA",
        "issuerZipCode": "94114",
        "issuerWebsite": "https://wefunder.com/",
        "intermediaryCompanyName": "Wefunder Portal LLC",
        "intermediaryCommissionCik": "0001670254",
        "intermediaryCommissionFileNumber": "007-00033",
        "compensationAmount": "5.0% of the offering amount",
        "financialInterest": "No",
        "securityOfferedType": "Other",
        "securityOfferedOtherDescription": "Simple Agreement for Future Equity (SAFE)",
        "numberOfSecurityOffered": 500000,
        "offeringPrice": 1,
        "offeringAmount": 500000,
        "overSubscriptionAccepted": "Y",
        "overSubscriptionAllocationType": "Other",
        "maximumOfferingAmount": 1235000,
        "offeringDeadlineDate": "05-31-2025",
        "currentNumberOfEmployees": 20,
        "totalAssetMostRecentFiscalYear": 4063817,
        "totalAssetPriorFiscalYear": 4817192,
        "cashAndCashEquiValentMostRecentFiscalYear": 3082961,
        "cashAndCashEquiValentPriorFiscalYear": 4782434,
        "accountsReceivableMostRecentFiscalYear": 0,
        "accountsReceivablePriorFiscalYear": 0,
        "shortTermDebtMostRecentFiscalYear": 1315820,
        "shortTermDebtPriorFiscalYear": 51023,
        "longTermDebtMostRecentFiscalYear": 1339232,
        "longTermDebtPriorFiscalYear": 0,
        "revenueMostRecentFiscalYear": 80793,
        "revenuePriorFiscalYear": 0,
        "costGoodsSoldMostRecentFiscalYear": 324251,
        "costGoodsSoldPriorFiscalYear": 0,
        "taxesPaidMostRecentFiscalYear": 0,
        "taxesPaidPriorFiscalYear": 0,
        "netIncomeMostRecentFiscalYear": -3357404,
        "netIncomePriorFiscalYear": -2140057,
    }


@pytest.fixture
def equity_offering_data():
    """Mock equity offering data"""
    return {
        "formType": "D/A",
        "formSignification": "Notice of Exempt Offering of Securities Amendment",
        "acceptanceTime": "2024-12-10 17:26:53",
        "cik": "0001609458",
        "entityName": "TRINITY STREET COMMINGLED GLOBAL EQUITY FUND, LP",
        "entityType": "Limited Partnership",
        "jurisdictionOfIncorporation": "DELAWARE",
        "incorporatedWithinFiveYears": None,
        "yearOfIncorporation": "",  # Added missing required field
        "issuerStreet": "C/O TRINITY STREET ASSET MANAGEMENT LLP",
        "issuerCity": "LONDON",
        "issuerStateOrCountry": "X0",
        "issuerStateOrCountryDescription": "UNITED KINGDOM",
        "issuerZipCode": "W1F 9LU",
        "issuerPhoneNumber": "4402074959114",
        "relatedPersonFirstName": "--",
        "relatedPersonLastName": "Trinity Street Commingled Global Equity Fund GP LLC",
        "relatedPersonStreet": "25 GOLDEN SQUARE",
        "relatedPersonCity": "LONDON",
        "relatedPersonStateOrCountry": "X0",
        "relatedPersonStateOrCountryDescription": "UNITED KINGDOM",
        "relatedPersonZipCode": "W1F 9LU",
        "relatedPersonRelationship": "Executive Officer",
        "industryGroupType": "Pooled Investment Fund",
        "revenueRange": None,  # Added missing required field
        "federalExemptionsExclusions": "06b, 3C, 3C.7",
        "isAmendment": True,
        "dateOfFirstSale": "2014-06-01",
        "durationOfOfferingIsMoreThanYear": True,
        "securitiesOfferedAreOfEquityType": True,
        "isBusinessCombinationTransaction": False,
        "minimumInvestmentAccepted": 0,
        "totalOfferingAmount": 0,
        "totalAmountSold": 186297000,
        "totalAmountRemaining": 0,
        "hasNonAccreditedInvestors": False,
        "totalNumberAlreadyInvested": 28,
        "salesCommissions": 0,
        "findersFees": 0,
        "grossProceedsUsed": 0,
    }


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


# New test methods
def test_get_esg_data(fmp_client, mock_client, esg_data):
    """Test fetching ESG data"""
    mock_client.request.return_value = ESGData(**esg_data)
    result = fmp_client.get_esg_data(symbol="AAPL")

    assert isinstance(result, ESGData)
    assert result.symbol == "AAPL"
    assert result.environmental_score == 68.47
    assert result.social_score == 47.02
    assert result.governance_score == 60.8
    assert result.esg_score == 58.76
    assert isinstance(result.accepted_date, datetime)


def test_get_esg_ratings(fmp_client, mock_client, esg_rating_data):
    """Test fetching ESG ratings"""
    mock_client.request.return_value = ESGRating(**esg_rating_data)
    result = fmp_client.get_esg_ratings(symbol="AAPL")

    assert isinstance(result, ESGRating)
    assert result.symbol == "AAPL"
    assert result.esg_risk_rating == "B"
    assert result.industry_rank == "4 out of 5"
    assert result.year == 2024


def test_get_esg_benchmark(fmp_client, mock_client, esg_benchmark_data):
    """Test fetching ESG benchmark data"""
    mock_client.request.return_value = [ESGBenchmark(**esg_benchmark_data)]
    result = fmp_client.get_esg_benchmark(year=2022)

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], ESGBenchmark)
    assert result[0].year == 2022
    assert result[0].environmental_score == 55.02
    assert result[0].social_score == 60.79
    assert result[0].governance_score == 58.67


def test_get_senate_trading(fmp_client, mock_client, senate_trade_data):
    """Test fetching Senate trading data"""
    mock_client.request.return_value = [SenateTrade(**senate_trade_data)]
    result = fmp_client.get_senate_trading(symbol="AAPL")

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], SenateTrade)
    assert result[0].symbol == "AAPL"
    assert result[0].first_name == "Tommy"
    assert result[0].last_name == "Tuberville"
    assert result[0].asset_type == "Stock"
    assert isinstance(result[0].transaction_date, datetime)


def test_get_house_disclosure(fmp_client, mock_client, house_disclosure_data):
    """Test fetching House disclosure data"""
    mock_client.request.return_value = [HouseDisclosure(**house_disclosure_data)]
    result = fmp_client.get_house_disclosure(symbol="AAPL")

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], HouseDisclosure)
    assert result[0].ticker == "AAPL"
    assert result[0].representative == "Laurel Lee"
    assert result[0].district == "FL15"
    assert isinstance(result[0].transaction_date, datetime)
    assert isinstance(result[0].disclosure_date, datetime)


def test_get_crowdfunding_rss(fmp_client, mock_client, crowdfunding_data):
    """Test fetching crowdfunding RSS feed"""
    mock_client.request.return_value = [CrowdfundingOffering(**crowdfunding_data)]
    result = fmp_client.get_crowdfunding_rss(page=0)

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], CrowdfundingOffering)
    assert result[0].company_name == "ArroFi Inc."
    assert result[0].cik == "0002045906"
    assert isinstance(result[0].filing_date, datetime)
    assert isinstance(result[0].offering_price, Decimal)


def test_get_equity_offering_by_cik(fmp_client, mock_client, equity_offering_data):
    """Test fetching equity offering by CIK"""
    mock_client.request.return_value = [EquityOffering(**equity_offering_data)]
    result = fmp_client.get_equity_offering_by_cik(cik="0001609458")

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], EquityOffering)
    assert result[0].cik == "0001609458"
    assert result[0].entity_type == "Limited Partnership"
    assert isinstance(result[0].total_amount_sold, Decimal)
    assert isinstance(result[0].acceptance_time, datetime)
    assert result[0].is_amendment is True
