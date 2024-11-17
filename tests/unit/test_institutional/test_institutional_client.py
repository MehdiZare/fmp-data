# tests/test_institutional/test_institutional_client.py
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from fmp_data.institutional.models import Form13F, InsiderTrade, InstitutionalHolder


@pytest.fixture
def mock_13f_filing():
    """Mock 13F filing data"""
    return {
        "cik": "0001067983",
        "filingDate": "2024-01-05",
        "periodOfReport": "2023-12-31",
        "form13FFileNumber": "028-11694",
        "holdings": [
            {
                "cusip": "037833100",
                "ticker": "AAPL",
                "nameOfIssuer": "Apple Inc",
                "shares": 915555,
                "value": 150250000,
                "classTitle": "COM",
                "investmentDiscretion": "SOLE",
                "soleVotingAuthority": 915555,
                "sharedVotingAuthority": 0,
                "noVotingAuthority": 0,
            }
        ],
        "totalValue": 150250000,
    }


@pytest.fixture
def mock_insider_trade():
    """Mock insider trade data"""
    return {
        "symbol": "AAPL",
        "insiderName": "Cook Timothy",
        "insiderTitle": "Chief Executive Officer",
        "transactionDate": "2024-01-05",
        "transactionType": "S",
        "transactionCode": "S",
        "shares": 50000,
        "sharePrice": 150.25,
        "value": 7512500,
        "filingDate": "2024-01-07",
    }


@pytest.fixture
def mock_institutional_holder():
    """Mock institutional holder data"""
    return {
        "cik": "0001067983",
        "name": "Vanguard Group Inc",
        "description": "Investment advisor",
        "website": "https://www.vanguard.com",
        "address": "100 Vanguard Blvd",
        "city": "Malvern",
        "state": "PA",
        "country": "USA",
    }


@patch("httpx.Client.request")
def test_get_form_13f(mock_request, fmp_client, mock_response, mock_13f_filing):
    """Test getting Form 13F filing"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=mock_13f_filing
    )

    filing = fmp_client.institutional.get_form_13f(
        "0001067983", filing_date=date(2024, 1, 5)
    )
    assert isinstance(filing, Form13F)
    assert filing.cik == "0001067983"
    assert len(filing.holdings) == 1
    assert filing.holdings[0].shares == 915555


@patch("httpx.Client.request")
def test_get_insider_trades(
    mock_request, fmp_client, mock_response, mock_insider_trade
):
    """Test getting insider trades"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_insider_trade]
    )

    trades = fmp_client.institutional.get_insider_trades("AAPL")
    assert isinstance(trades, list)
    assert len(trades) == 1
    assert isinstance(trades[0], InsiderTrade)
    assert trades[0].shares == 50000
    assert isinstance(trades[0].share_price, Decimal)


@patch("httpx.Client.request")
def test_get_institutional_holders(
    mock_request, fmp_client, mock_response, mock_institutional_holder
):
    """Test getting institutional holders"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_institutional_holder]
    )

    holders = fmp_client.institutional.get_institutional_holders()
    assert isinstance(holders, list)
    assert len(holders) == 1
    assert isinstance(holders[0], InstitutionalHolder)
    assert holders[0].cik == "0001067983"
