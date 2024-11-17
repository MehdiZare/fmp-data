import pytest


@pytest.fixture
def mock_13f_filing():
    """Mock Form 13F filing data"""
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
