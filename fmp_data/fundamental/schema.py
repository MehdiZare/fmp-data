# fmp_data/fundamental/schema.py

from pydantic import Field

from fmp_data.schema import BaseArgModel, FinancialStatementBaseArg, SymbolArg


# Statement-specific Arguments
class IncomeStatementArgs(FinancialStatementBaseArg):
    """Arguments for retrieving income statements"""

    pass


class BalanceSheetArgs(FinancialStatementBaseArg):
    """Arguments for retrieving balance sheets"""

    pass


class CashFlowArgs(FinancialStatementBaseArg):
    """Arguments for retrieving cash flow statements"""

    pass


class KeyMetricsArgs(FinancialStatementBaseArg):
    """Arguments for retrieving key financial metrics"""

    pass


class FinancialRatiosArgs(FinancialStatementBaseArg):
    """Arguments for retrieving financial ratios"""

    pass


class SimpleSymbolArgs(SymbolArg):
    """Arguments for single symbol endpoints"""

    pass


class OwnerEarningsArgs(SymbolArg):
    """Arguments for owner earnings endpoints"""

    limit: int | None = Field(
        default=None, ge=1, le=1000, description="Number of results"
    )


class LatestFinancialStatementsArgs(BaseArgModel):
    """Arguments for latest financial statements listing"""

    page: int = Field(default=0, ge=0, le=100, description="Page number (max 100)")
    limit: int = Field(
        default=250, ge=1, le=250, description="Records per page (max 250)"
    )
