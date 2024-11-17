# tests/test_institutional/test_institutional_models.py
from datetime import date
from decimal import Decimal

from fmp_data.institutional.models import Form13F, InsiderTrade, InstitutionalHolder


def test_form_13f_model(mock_13f_filing):
    """Test Form13F model validation"""
    filing = Form13F.model_validate(mock_13f_filing)
    assert filing.cik == "0001067983"
    assert isinstance(filing.filing_date, date)
    assert len(filing.holdings) == 1
    assert isinstance(filing.total_value, Decimal)


def test_insider_trade_model(mock_insider_trade):
    """Test InsiderTrade model validation"""
    trade = InsiderTrade.model_validate(mock_insider_trade)
    assert trade.symbol == "AAPL"
    assert isinstance(trade.transaction_date, date)
    assert isinstance(trade.share_price, Decimal)
    assert trade.shares == 50000


def test_institutional_holder_model(mock_institutional_holder):
    """Test InstitutionalHolder model validation"""
    holder = InstitutionalHolder.model_validate(mock_institutional_holder)
    assert holder.cik == "0001067983"
    assert holder.name == "Vanguard Group Inc"
    assert holder.country == "USA"
