# fmp_data/fundamental/schema.py

from fmp_data.schema import FinancialStatementBaseArg, SymbolArg


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
