# fmp_data/fundamental/schema.py

from pydantic import Field

from fmp_data.schema import (
    BaseArgModel,
    BaseEnum,
    DateRangeArg,
    FinancialStatementBaseArg,
    SymbolArg,
)


class EconomicIndicatorType(BaseEnum):
    """Types of economic indicators available"""

    GDP = "gdp"
    GDP_GROWTH = "gdp_growth"
    GDP_PER_CAPITA = "gdp_per_capita"
    INFLATION = "inflation"
    INFLATION_RATE = "inflation_rate"
    CPI = "cpi"
    CORE_CPI = "core_cpi"
    PPI = "ppi"
    CORE_PPI = "core_ppi"
    RETAIL_SALES = "retail_sales"
    INDUSTRIAL_PRODUCTION = "industrial_production"
    UNEMPLOYMENT = "unemployment"
    NONFARM_PAYROLL = "nonfarm_payroll"
    BALANCE_OF_TRADE = "balance_of_trade"
    CURRENT_ACCOUNT = "current_account"
    GOVERNMENT_DEBT = "government_debt"
    GOVERNMENT_SPENDING = "government_spending"
    CONSUMER_CONFIDENCE = "consumer_confidence"
    BUSINESS_CONFIDENCE = "business_confidence"
    HOUSING_STARTS = "housing_starts"
    BUILDING_PERMITS = "building_permits"
    DURABLE_GOODS_ORDERS = "durable_goods_orders"


class TreasuryRatesArgs(DateRangeArg):
    """Arguments for getting treasury rates"""

    pass


class EconomicIndicatorsArgs(BaseArgModel):
    """Arguments for getting economic indicators"""

    name: EconomicIndicatorType = Field(
        description="Name of the economic indicator",
        json_schema_extra={"examples": ["gdp", "inflation", "unemployment"]},
    )


class EconomicCalendarArgs(DateRangeArg):
    """Arguments for getting economic calendar events"""

    pass


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


class DateRange(DateRangeArg):
    """Date range for historical data"""

    pass
