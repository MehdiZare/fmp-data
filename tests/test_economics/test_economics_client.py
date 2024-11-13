# tests/test_economics/test_economics_client.py
from datetime import date
from unittest.mock import patch

import pytest

from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)


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


@patch("httpx.Client.request")
def test_get_treasury_rates(
    mock_request, fmp_client, mock_response, mock_treasury_rate
):
    """Test getting treasury rates"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_treasury_rate]
    )

    rates = fmp_client.economics.get_treasury_rates(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 5)
    )
    assert isinstance(rates, list)
    assert len(rates) == 1
    assert isinstance(rates[0], TreasuryRate)
    assert rates[0].year_10 == 6.15
    assert rates[0].year_30 == 6.35


@patch("httpx.Client.request")
def test_get_economic_indicators(
    mock_request, fmp_client, mock_response, mock_economic_indicator
):
    """Test getting economic indicators"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_economic_indicator]
    )

    indicators = fmp_client.economics.get_economic_indicators("GDP")
    assert isinstance(indicators, list)
    assert len(indicators) == 1
    assert isinstance(indicators[0], EconomicIndicator)
    assert indicators[0].value == 24000.5
    assert indicators[0].country == "United States"


@patch("httpx.Client.request")
def test_get_economic_calendar(
    mock_request, fmp_client, mock_response, mock_economic_event
):
    """Test getting economic calendar"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_economic_event]
    )

    events = fmp_client.economics.get_economic_calendar(
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 5)
    )
    assert isinstance(events, list)
    assert len(events) == 1
    assert isinstance(events[0], EconomicEvent)
    assert events[0].actual == 2.5
    assert events[0].impact == "High"


@patch("httpx.Client.request")
def test_get_market_risk_premium(
    mock_request, fmp_client, mock_response, mock_risk_premium
):
    """Test getting market risk premium"""
    mock_request.return_value = mock_response(
        status_code=200, json_data=[mock_risk_premium]
    )

    premiums = fmp_client.economics.get_market_risk_premium()
    assert isinstance(premiums, list)
    assert len(premiums) == 1
    assert isinstance(premiums[0], MarketRiskPremium)
    assert premiums[0].risk_premium == 5.5
    assert premiums[0].market_return == 10.5
