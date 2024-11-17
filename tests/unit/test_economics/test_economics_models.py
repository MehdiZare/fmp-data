# tests/test_economics/test_economics_models.py
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)


def test_treasury_rate_model(mock_treasury_rate):
    """Test TreasuryRate model validation"""
    mock_treasury_rate["date"] = "2024-01-05"

    rate = TreasuryRate.model_validate(mock_treasury_rate)

    assert isinstance(rate.rate_date, date)
    assert isinstance(rate.year_10, float)
    assert rate.year_10 == 6.15
    assert isinstance(rate.year_30, float)
    assert rate.year_30 == 6.35


def test_economic_indicator_model(mock_economic_indicator):
    """Test EconomicIndicator model validation"""
    mock_economic_indicator["date"] = "2024-01-05"

    indicator = EconomicIndicator.model_validate(mock_economic_indicator)

    assert isinstance(indicator.indicator_date, date)
    assert indicator.indicator == "GDP"
    assert isinstance(indicator.value, float)
    assert indicator.value == 24000.5
    assert indicator.unit == "Billion USD"
    assert indicator.country == "United States"


def test_economic_event_model(mock_economic_event):
    """Test EconomicEvent model validation"""
    mock_economic_event["date"] = "2024-01-05T08:30:00"

    event = EconomicEvent.model_validate(mock_economic_event)

    assert isinstance(event.event_date, datetime)
    assert event.event == "GDP Release"
    assert isinstance(event.actual, float)
    assert event.actual == 2.5
    assert event.impact == "High"


def test_market_risk_premium_model(mock_risk_premium):
    """Test MarketRiskPremium model validation"""
    mock_risk_premium["date"] = "2024-01-05"

    premium = MarketRiskPremium.model_validate(mock_risk_premium)

    assert isinstance(premium.risk_premium, float)
    assert premium.risk_premium == 5.5
    assert premium.country == "United States"


def test_invalid_treasury_rate():
    """Test TreasuryRate model with invalid data"""
    invalid_data = {"date": "invalid date", "10year": "not a number"}

    with pytest.raises(ValidationError) as exc_info:
        TreasuryRate.model_validate(invalid_data)
    assert "Input should be a valid date" in str(exc_info.value)


def test_invalid_economic_indicator():
    """Test EconomicIndicator model with invalid data"""
    invalid_data = {"date": "invalid date", "value": "not a number"}

    with pytest.raises(ValidationError) as exc_info:
        EconomicIndicator.model_validate(invalid_data)
    assert any(
        [
            "Input should be a valid date" in str(exc_info.value),
            "Input should be a valid number" in str(exc_info.value),
        ]
    )
