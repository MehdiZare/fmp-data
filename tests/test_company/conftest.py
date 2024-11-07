# tests/test_company/conftest.py
import pytest


@pytest.fixture
def mock_company_profile():
    """Mock company profile data"""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "beta": 1.2,
        "volAvg": 82034567,
        "mktCap": 2500000000000,
        "lastDiv": 0.88,
        "range": "120.5-155.75",
        "changes": 2.35,
        "companyName": "Apple Inc.",
        "currency": "USD",
        "cik": "0000320193",
        "isin": "US0378331005",
        "cusip": "037833100",
        "exchange": "NASDAQ",
        "exchangeShortName": "NASDAQ",
        "industry": "Consumer Electronics",
        "website": "https://www.apple.com",
        "description": "Apple Inc. designs, manufactures, and markets smartphones...",
        "ceo": "Tim Cook",
        "sector": "Technology",
        "country": "US",
        "fullTimeEmployees": "147000",
        "phone": "14089961010",
        "address": "One Apple Park Way",
        "city": "Cupertino",
        "state": "CA",
        "zip": "95014",
        "dcfDiff": 0.0,
        "dcf": 0.0,
        "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
        "ipoDate": "1980-12-12",
        "defaultImage": False,
        "isEtf": False,
        "isActivelyTrading": True,
        "isAdr": False,
        "isFund": False,
    }
