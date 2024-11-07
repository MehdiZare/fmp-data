# tests/test_company/test_company_models.py
from datetime import datetime

from fmp_data.company.models import CompanyExecutive, CompanyProfile


def test_company_profile_model(mock_company_profile):
    """Test CompanyProfile model validation"""
    profile = CompanyProfile.model_validate(mock_company_profile)
    assert profile.symbol == "AAPL"
    assert profile.company_name == "Apple Inc."
    assert profile.price == 150.25
    assert profile.beta == 1.2
    assert isinstance(profile.ipo_date, datetime)


def test_company_executive_model():
    """Test CompanyExecutive model validation"""
    exec_data = {
        "title": "Chief Executive Officer",
        "name": "Tim Cook",
        "pay": 3000000,
        "currencyPay": "USD",
        "gender": "M",
        "yearBorn": 1960,
        "titleSince": "2011-08-24",
    }

    executive = CompanyExecutive.model_validate(exec_data)
    assert executive.name == "Tim Cook"
    assert executive.title == "Chief Executive Officer"
    assert executive.pay == 3000000
    assert isinstance(executive.title_since, datetime)
