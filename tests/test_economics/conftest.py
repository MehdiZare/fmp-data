import pytest


@pytest.fixture
def mock_treasury_rate():
    """Mock treasury rate data"""
    return {
        "date": "2024-01-05",
        "1month": 5.25,
        "2month": 5.35,
        "3month": 5.45,
        "6month": 5.55,
        "1year": 5.65,
        "2year": 5.75,
        "3year": 5.85,
        "5year": 5.95,
        "7year": 6.05,
        "10year": 6.15,
        "20year": 6.25,
        "30year": 6.35,
    }


@pytest.fixture
def mock_economic_indicator():
    """Mock economic indicator data"""
    return {
        "date": "2024-01-05",
        "indicator": "GDP",
        "value": 24000.5,
        "unit": "Billion USD",
        "frequency": "Quarterly",
        "country": "United States",
        "category": "Economic Growth",
        "description": "Gross Domestic Product",
        "source": "Bureau of Economic Analysis",
    }


@pytest.fixture
def mock_economic_event():
    """Mock economic calendar event"""
    return {
        "event": "GDP Release",
        "date": "2024-01-05T08:30:00",
        "country": "United States",
        "actual": 2.5,
        "previous": 2.3,
        "estimate": 2.4,
        "change": 0.2,
        "changePercentage": 8.7,
        "impact": "High",
    }


@pytest.fixture
def mock_risk_premium():
    """Mock market risk premium data"""
    return {
        "date": "2024-01-05",
        "country": "United States",
        "riskPremium": 5.5,
        "marketReturn": 10.5,
        "riskFreeRate": 5.0,
        "equityRiskPremium": 5.5,
        "countryRiskPremium": 0.0,
    }
