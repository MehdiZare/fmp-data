# tests/test_fundamental/test_fundamental_models.py
from datetime import datetime

import pytest
from pydantic import ValidationError

from fmp_data.fundamental.models import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    KeyMetrics,
)


def test_income_statement_model(mock_income_statement):
    """Test IncomeStatement model validation"""
    statement = IncomeStatement.model_validate(mock_income_statement)
    assert statement.symbol == "AAPL"
    assert statement.revenue == 394328000000
    assert statement.net_income == 96995000000
    assert isinstance(statement.date, datetime)
    assert statement.reported_currency == "USD"


def test_balance_sheet_model(mock_balance_sheet):
    """Test BalanceSheet model validation"""
    statement = BalanceSheet.model_validate(mock_balance_sheet)
    assert statement.symbol == "AAPL"
    assert statement.total_assets == 352755000000
    assert statement.total_liabilities == 287912000000
    assert isinstance(statement.date, datetime)
    assert statement.period == "annual"


def test_cash_flow_model(mock_cash_flow):
    """Test CashFlowStatement model validation"""
    statement = CashFlowStatement.model_validate(mock_cash_flow)
    assert statement.symbol == "AAPL"
    assert statement.operating_cash_flow == 122151000000
    assert statement.net_cash_flow == -227000000
    assert isinstance(statement.date, datetime)
    assert statement.calendar_year == 2023


def test_key_metrics_model(mock_key_metrics):
    """Test KeyMetrics model validation"""
    metrics = KeyMetrics.model_validate(mock_key_metrics)
    assert metrics.revenue_per_share == 25.04
    assert metrics.net_income_per_share == 6.16
    assert metrics.operating_cash_flow_per_share == 7.75
    assert metrics.free_cash_flow_per_share == 6.43


def test_invalid_income_statement():
    """Test IncomeStatement model with invalid data"""
    invalid_data = {"date": "invalid-date", "symbol": "AAPL", "revenue": "not-a-number"}

    with pytest.raises(ValidationError) as exc_info:
        IncomeStatement.model_validate(invalid_data)
    assert any(
        [
            "Input should be a valid date" in str(exc_info.value),
            "Input should be a valid number" in str(exc_info.value),
        ]
    )
