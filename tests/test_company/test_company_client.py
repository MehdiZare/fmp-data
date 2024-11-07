# tests/test_company/test_company_client.py
from unittest.mock import patch

from fmp_data.company.models import CompanyProfile


@patch("httpx.Client.request")
def test_get_company_profile(
    mock_request, fmp_client, mock_response, mock_company_profile
):
    """Test getting company profile"""
    mock_request.return_value = mock_response(
        status_code=200,
        json_data=[mock_company_profile],  # API returns list with single item
    )

    profile = fmp_client.company.get_profile("AAPL")
    assert isinstance(profile, CompanyProfile)
    assert profile.symbol == "AAPL"
    assert profile.company_name == "Apple Inc."


@patch("httpx.Client.request")
def test_search_companies(mock_request, fmp_client, mock_response):
    """Test company search"""
    mock_data = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "currency": "USD",
            "stockExchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
        }
    ]

    mock_request.return_value = mock_response(status_code=200, json_data=mock_data)

    results = fmp_client.company.search("Apple", limit=1)
    assert len(results) == 1
    assert results[0].symbol == "AAPL"


@patch("httpx.Client.request")
def test_get_company_executives(mock_request, fmp_client, mock_response):
    """Test getting company executives"""
    mock_data = [
        {
            "title": "Chief Executive Officer",
            "name": "Tim Cook",
            "pay": 3000000,
            "currencyPay": "USD",
            "gender": "M",
            "yearBorn": 1960,
            "titleSince": "2011-08-24",
        }
    ]

    mock_request.return_value = mock_response(status_code=200, json_data=mock_data)

    executives = fmp_client.company.get_executives("AAPL")
    assert len(executives) == 1
    assert executives[0].name == "Tim Cook"
    assert executives[0].title == "Chief Executive Officer"
