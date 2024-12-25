# fmp_data/fundamental/schema.py

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# Base Arguments
class FinancialStatementArgs(BaseModel):
    """Base arguments for financial statement endpoints"""

    symbol: str = Field(
        description="Stock symbol/ticker of the company",
        examples=["AAPL", "MSFT", "GOOGL"],
    )
    period: Literal["annual", "quarter"] | None = Field(
        default="annual",
        description="Reporting period (annual or quarterly statements)",
    )
    limit: int | None = Field(
        default=40, description="Number of periods to return", ge=1, le=100
    )


# Statement-specific Arguments
class IncomeStatementArgs(FinancialStatementArgs):
    """Arguments for retrieving income statements"""

    pass


class BalanceSheetArgs(FinancialStatementArgs):
    """Arguments for retrieving balance sheets"""

    pass


class CashFlowArgs(FinancialStatementArgs):
    """Arguments for retrieving cash flow statements"""

    pass


class KeyMetricsArgs(FinancialStatementArgs):
    """Arguments for retrieving key financial metrics"""

    pass


class FinancialRatiosArgs(FinancialStatementArgs):
    """Arguments for retrieving financial ratios"""

    pass


class SimpleSymbolArgs(BaseModel):
    """Arguments for single symbol endpoints"""

    symbol: str = Field(
        description="Stock symbol/ticker of the company",
        examples=["AAPL", "MSFT", "GOOGL"],
    )


# Reporting Period
ReportingPeriod = Literal["annual", "quarter"]


# Date Range
class DateRange(BaseModel):
    """Date range for historical data"""

    start_date: date | None = Field(None, description="Start date for the data range")
    end_date: date | None = Field(None, description="End date for the data range")
