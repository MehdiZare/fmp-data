# fmp_data/fundamental/models.py
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class FinancialStatementBase(BaseModel):
    """Base model for financial statements"""

    model_config = default_model_config

    date: datetime = Field(description="Statement date")
    symbol: str = Field(description="Company symbol")
    reported_currency: str = Field(
        alias="reportedCurrency", description="Currency used"
    )
    cik: str = Field(description="SEC CIK number")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    accepted_date: datetime = Field(
        alias="acceptedDate", description="SEC acceptance date"
    )
    fiscal_year: str = Field(alias="fiscalYear", description="Fiscal year")
    period: str = Field(description="Reporting period (Q1, Q2, Q3, Q4, FY)")


class IncomeStatement(FinancialStatementBase):
    """Income statement data from FMP API"""

    model_config = default_model_config

    # Revenue and Cost - ALL optional with explicit default=None
    revenue: float | None = Field(default=None, description="Total revenue")
    cost_of_revenue: float | None = Field(
        default=None, alias="costOfRevenue", description="Cost of revenue"
    )
    gross_profit: float | None = Field(
        default=None, alias="grossProfit", description="Gross profit"
    )
    gross_profit_ratio: float | None = Field(
        default=None, alias="grossProfitRatio", description="Gross profit ratio"
    )

    # Operating Expenses - ALL optional with explicit default=None
    research_and_development_expenses: float | None = Field(
        default=None, alias="researchAndDevelopmentExpenses", description="R&D expenses"
    )
    general_and_administrative_expenses: float | None = Field(
        default=None,
        alias="generalAndAdministrativeExpenses",
        description="G&A expenses",
    )
    selling_and_marketing_expenses: float | None = Field(
        default=None,
        alias="sellingAndMarketingExpenses",
        description="Sales and marketing expenses",
    )
    selling_general_and_administrative_expenses: float | None = Field(
        default=None,
        alias="sellingGeneralAndAdministrativeExpenses",
        description="SG&A expenses",
    )
    other_expenses: float | None = Field(
        default=None, alias="otherExpenses", description="Other operating expenses"
    )
    operating_expenses: float | None = Field(
        default=None, alias="operatingExpenses", description="Total operating expenses"
    )
    cost_and_expenses: float | None = Field(
        default=None, alias="costAndExpenses", description="Total costs and expenses"
    )

    # Interest and Income - ALL optional with explicit default=None
    net_interest_income: float | None = Field(
        default=None, alias="netInterestIncome", description="Net interest income"
    )
    interest_income: float | None = Field(
        default=None, alias="interestIncome", description="Interest income"
    )
    interest_expense: float | None = Field(
        default=None, alias="interestExpense", description="Interest expense"
    )

    # Depreciation and EBITDA/EBIT - ALL optional with explicit default=None
    depreciation_and_amortization: float | None = Field(
        default=None,
        alias="depreciationAndAmortization",
        description="Depreciation and amortization",
    )
    ebitda: float | None = Field(default=None, description="EBITDA")
    ebitda_ratio: float | None = Field(
        default=None, alias="ebitdaratio", description="EBITDA ratio"
    )
    ebit: float | None = Field(default=None, description="EBIT")

    # Operating Income - ALL optional with explicit default=None
    non_operating_income_excluding_interest: float | None = Field(
        default=None,
        alias="nonOperatingIncomeExcludingInterest",
        description="Non-operating income excluding interest",
    )
    operating_income: float | None = Field(
        default=None, alias="operatingIncome", description="Operating income"
    )
    operating_income_ratio: float | None = Field(
        default=None, alias="operatingIncomeRatio", description="Operating income ratio"
    )

    # Other Income and Pre-tax - ALL optional with explicit default=None
    total_other_income_expenses_net: float | None = Field(
        default=None,
        alias="totalOtherIncomeExpensesNet",
        description="Total other income/expenses net",
    )
    income_before_tax: float | None = Field(
        default=None, alias="incomeBeforeTax", description="Income before tax"
    )
    income_before_tax_ratio: float | None = Field(
        default=None,
        alias="incomeBeforeTaxRatio",
        description="Income before tax ratio",
    )

    # Tax and Net Income - ALL optional with explicit default=None
    income_tax_expense: float | None = Field(
        default=None, alias="incomeTaxExpense", description="Income tax expense"
    )
    net_income_from_continuing_operations: float | None = Field(
        default=None,
        alias="netIncomeFromContinuingOperations",
        description="Net income from continuing operations",
    )
    net_income_from_discontinued_operations: float | None = Field(
        default=None,
        alias="netIncomeFromDiscontinuedOperations",
        description="Net income from discontinued operations",
    )
    other_adjustments_to_net_income: float | None = Field(
        default=None,
        alias="otherAdjustmentsToNetIncome",
        description="Other adjustments to net income",
    )
    net_income: float | None = Field(
        default=None, alias="netIncome", description="Net income"
    )
    net_income_deductions: float | None = Field(
        default=None, alias="netIncomeDeductions", description="Net income deductions"
    )
    bottom_line_net_income: float | None = Field(
        default=None, alias="bottomLineNetIncome", description="Bottom line net income"
    )
    net_income_ratio: float | None = Field(
        default=None, alias="netIncomeRatio", description="Net income ratio"
    )

    # Earnings Per Share - ALL optional with explicit default=None
    eps: float | None = Field(default=None, description="Basic earnings per share")
    eps_diluted: float | None = Field(
        default=None, alias="epsDiluted", description="Diluted earnings per share"
    )

    # Share Counts - ALL optional with explicit default=None
    weighted_average_shs_out: float | None = Field(
        default=None,
        alias="weightedAverageShsOut",
        description="Weighted average shares outstanding",
    )
    weighted_average_shs_out_dil: float | None = Field(
        default=None,
        alias="weightedAverageShsOutDil",
        description="Diluted weighted average shares outstanding",
    )


class BalanceSheet(FinancialStatementBase):
    """Balance sheet data"""

    model_config = default_model_config

    # Cash and Investments - detailed breakdown
    cash_and_cash_equivalents: float | None = Field(
        default=None,
        alias="cashAndCashEquivalents",
        description="Cash and cash equivalents",
    )
    short_term_investments: float | None = Field(
        default=None, alias="shortTermInvestments", description="Short-term investments"
    )
    cash_and_short_term_investments: float | None = Field(
        default=None,
        alias="cashAndShortTermInvestments",
        description="Cash and short-term investments",
    )

    # Receivables - detailed breakdown
    net_receivables: float | None = Field(
        default=None, alias="netReceivables", description="Net receivables"
    )
    accounts_receivables: float | None = Field(
        default=None, alias="accountsReceivables", description="Accounts receivables"
    )
    other_receivables: float | None = Field(
        default=None, alias="otherReceivables", description="Other receivables"
    )

    # Current Assets
    inventory: float | None = Field(default=None, description="Inventory")
    prepaids: float | None = Field(default=None, description="Prepaid expenses")
    other_current_assets: float | None = Field(
        default=None, alias="otherCurrentAssets", description="Other current assets"
    )
    total_current_assets: float | None = Field(
        default=None, alias="totalCurrentAssets", description="Total current assets"
    )

    # Non-current Assets
    property_plant_equipment_net: float | None = Field(
        default=None, alias="propertyPlantEquipmentNet", description="Net PP&E"
    )
    goodwill: float | None = Field(default=None, description="Goodwill")
    intangible_assets: float | None = Field(
        default=None, alias="intangibleAssets", description="Intangible assets"
    )
    goodwill_and_intangible_assets: float | None = Field(
        default=None,
        alias="goodwillAndIntangibleAssets",
        description="Goodwill and intangible assets",
    )
    long_term_investments: float | None = Field(
        default=None, alias="longTermInvestments", description="Long-term investments"
    )
    tax_assets: float | None = Field(
        default=None, alias="taxAssets", description="Tax assets"
    )
    other_non_current_assets: float | None = Field(
        default=None,
        alias="otherNonCurrentAssets",
        description="Other non-current assets",
    )
    total_non_current_assets: float | None = Field(
        default=None,
        alias="totalNonCurrentAssets",
        description="Total non-current assets",
    )
    other_assets: float | None = Field(
        default=None, alias="otherAssets", description="Other assets"
    )
    total_assets: float | None = Field(
        default=None, alias="totalAssets", description="Total assets"
    )

    # Payables - detailed breakdown
    total_payables: float | None = Field(
        default=None, alias="totalPayables", description="Total payables"
    )
    account_payables: float | None = Field(
        default=None, alias="accountPayables", description="Accounts payable"
    )
    other_payables: float | None = Field(
        default=None, alias="otherPayables", description="Other payables"
    )
    accrued_expenses: float | None = Field(
        default=None, alias="accruedExpenses", description="Accrued expenses"
    )

    # Current Liabilities
    short_term_debt: float | None = Field(
        default=None, alias="shortTermDebt", description="Short-term debt"
    )
    capital_lease_obligations_current: float | None = Field(
        default=None,
        alias="capitalLeaseObligationsCurrent",
        description="Current capital lease obligations",
    )
    tax_payables: float | None = Field(
        default=None, alias="taxPayables", description="Tax payables"
    )
    deferred_revenue: float | None = Field(
        default=None, alias="deferredRevenue", description="Deferred revenue"
    )
    other_current_liabilities: float | None = Field(
        default=None,
        alias="otherCurrentLiabilities",
        description="Other current liabilities",
    )
    total_current_liabilities: float | None = Field(
        default=None,
        alias="totalCurrentLiabilities",
        description="Total current liabilities",
    )

    # Non-current Liabilities
    long_term_debt: float | None = Field(
        default=None, alias="longTermDebt", description="Long-term debt"
    )
    deferred_revenue_non_current: float | None = Field(
        default=None,
        alias="deferredRevenueNonCurrent",
        description="Non-current deferred revenue",
    )
    deferred_tax_liabilities_non_current: float | None = Field(
        default=None,
        alias="deferredTaxLiabilitiesNonCurrent",
        description="Non-current deferred tax liabilities",
    )
    other_non_current_liabilities: float | None = Field(
        default=None,
        alias="otherNonCurrentLiabilities",
        description="Other non-current liabilities",
    )
    total_non_current_liabilities: float | None = Field(
        default=None,
        alias="totalNonCurrentLiabilities",
        description="Total non-current liabilities",
    )
    other_liabilities: float | None = Field(
        default=None, alias="otherLiabilities", description="Other liabilities"
    )
    capital_lease_obligations: float | None = Field(
        default=None,
        alias="capitalLeaseObligations",
        description="Capital lease obligations",
    )
    capital_lease_obligations_non_current: float | None = Field(
        default=None,
        alias="capitalLeaseObligationsNonCurrent",
        description="Non-current capital lease obligations",
    )
    total_liabilities: float | None = Field(
        default=None, alias="totalLiabilities", description="Total liabilities"
    )

    # Equity - detailed breakdown
    treasury_stock: float | None = Field(
        default=None, alias="treasuryStock", description="Treasury stock"
    )
    preferred_stock: float | None = Field(
        default=None, alias="preferredStock", description="Preferred stock"
    )
    common_stock: float | None = Field(
        default=None, alias="commonStock", description="Common stock"
    )
    retained_earnings: float | None = Field(
        default=None, alias="retainedEarnings", description="Retained earnings"
    )
    additional_paid_in_capital: float | None = Field(
        default=None,
        alias="additionalPaidInCapital",
        description="Additional paid-in capital",
    )
    accumulated_other_comprehensive_income_loss: float | None = Field(
        default=None,
        alias="accumulatedOtherComprehensiveIncomeLoss",
        description="Accumulated other comprehensive income/loss",
    )
    other_total_stockholders_equity: float | None = Field(
        default=None,
        alias="otherTotalStockholdersEquity",
        description="Other total stockholders equity",
    )
    total_stockholders_equity: float | None = Field(
        default=None,
        alias="totalStockholdersEquity",
        description="Total stockholders' equity",
    )
    total_equity: float | None = Field(
        default=None, alias="totalEquity", description="Total equity"
    )
    minority_interest: float | None = Field(
        default=None, alias="minorityInterest", description="Minority interest"
    )
    total_liabilities_and_equity: float | None = Field(
        default=None,
        alias="totalLiabilitiesAndTotalEquity",
        description="Total liabilities and equity",
    )

    # Additional metrics
    total_investments: float | None = Field(
        default=None, alias="totalInvestments", description="Total investments"
    )
    total_debt: float | None = Field(
        default=None, alias="totalDebt", description="Total debt"
    )
    net_debt: float | None = Field(
        default=None, alias="netDebt", description="Net debt"
    )


class CashFlowStatement(FinancialStatementBase):
    """Cash flow statement data from FMP API

    Relative path: fmp_data/fundamental/models.py
    """

    model_config = default_model_config

    # Operating Activities
    net_income: float | None = Field(
        default=None, alias="netIncome", description="Net income"
    )
    depreciation_and_amortization: float | None = Field(
        default=None,
        alias="depreciationAndAmortization",
        description="Depreciation and amortization",
    )
    deferred_income_tax: float | None = Field(
        default=None, alias="deferredIncomeTax", description="Deferred income tax"
    )
    stock_based_compensation: float | None = Field(
        default=None,
        alias="stockBasedCompensation",
        description="Stock-based compensation",
    )
    change_in_working_capital: float | None = Field(
        default=None,
        alias="changeInWorkingCapital",
        description="Change in working capital",
    )
    accounts_receivables: float | None = Field(
        default=None,
        alias="accountsReceivables",
        description="Change in accounts receivables",
    )
    inventory: float | None = Field(
        default=None, alias="inventory", description="Change in inventory"
    )
    accounts_payables: float | None = Field(
        default=None,
        alias="accountsPayables",
        description="Change in accounts payables",
    )
    other_working_capital: float | None = Field(
        default=None,
        alias="otherWorkingCapital",
        description="Other working capital changes",
    )
    other_non_cash_items: float | None = Field(
        default=None, alias="otherNonCashItems", description="Other non-cash items"
    )
    net_cash_provided_by_operating_activities: float | None = Field(
        default=None,
        alias="netCashProvidedByOperatingActivities",
        description="Net cash provided by operating activities",
    )
    operating_cash_flow: float | None = Field(
        default=None, alias="operatingCashFlow", description="Operating cash flow"
    )

    # Investing Activities
    investments_in_property_plant_and_equipment: float | None = Field(
        default=None,
        alias="investmentsInPropertyPlantAndEquipment",
        description="Investments in property, plant and equipment",
    )
    capital_expenditure: float | None = Field(
        default=None, alias="capitalExpenditure", description="Capital expenditure"
    )
    acquisitions_net: float | None = Field(
        default=None, alias="acquisitionsNet", description="Net acquisitions"
    )
    purchases_of_investments: float | None = Field(
        default=None,
        alias="purchasesOfInvestments",
        description="Purchases of investments",
    )
    sales_maturities_of_investments: float | None = Field(
        default=None,
        alias="salesMaturitiesOfInvestments",
        description="Sales and maturities of investments",
    )
    other_investing_activities: float | None = Field(
        default=None,
        alias="otherInvestingActivities",
        description="Other investing activities",
    )
    net_cash_provided_by_investing_activities: float | None = Field(
        default=None,
        alias="netCashProvidedByInvestingActivities",
        description="Net cash provided by investing activities",
    )

    # Financing Activities
    net_debt_issuance: float | None = Field(
        default=None, alias="netDebtIssuance", description="Net debt issuance"
    )
    long_term_net_debt_issuance: float | None = Field(
        default=None,
        alias="longTermNetDebtIssuance",
        description="Long-term net debt issuance",
    )
    short_term_net_debt_issuance: float | None = Field(
        default=None,
        alias="shortTermNetDebtIssuance",
        description="Short-term net debt issuance",
    )
    net_stock_issuance: float | None = Field(
        default=None, alias="netStockIssuance", description="Net stock issuance"
    )
    net_common_stock_issuance: float | None = Field(
        default=None,
        alias="netCommonStockIssuance",
        description="Net common stock issuance",
    )
    common_stock_issuance: float | None = Field(
        default=None, alias="commonStockIssuance", description="Common stock issuance"
    )
    common_stock_repurchased: float | None = Field(
        default=None,
        alias="commonStockRepurchased",
        description="Common stock repurchased",
    )
    net_preferred_stock_issuance: float | None = Field(
        default=None,
        alias="netPreferredStockIssuance",
        description="Net preferred stock issuance",
    )
    net_dividends_paid: float | None = Field(
        default=None, alias="netDividendsPaid", description="Net dividends paid"
    )
    common_dividends_paid: float | None = Field(
        default=None, alias="commonDividendsPaid", description="Common dividends paid"
    )
    preferred_dividends_paid: float | None = Field(
        default=None,
        alias="preferredDividendsPaid",
        description="Preferred dividends paid",
    )
    other_financing_activities: float | None = Field(
        default=None,
        alias="otherFinancingActivities",
        description="Other financing activities",
    )
    net_cash_provided_by_financing_activities: float | None = Field(
        default=None,
        alias="netCashProvidedByFinancingActivities",
        description="Net cash provided by financing activities",
    )

    # Net Changes and Cash Position
    effect_of_forex_changes_on_cash: float | None = Field(
        default=None,
        alias="effectOfForexChangesOnCash",
        description="Effect of forex changes on cash",
    )
    net_change_in_cash: float | None = Field(
        default=None, alias="netChangeInCash", description="Net change in cash"
    )
    cash_at_end_of_period: float | None = Field(
        default=None, alias="cashAtEndOfPeriod", description="Cash at end of period"
    )
    cash_at_beginning_of_period: float | None = Field(
        default=None,
        alias="cashAtBeginningOfPeriod",
        description="Cash at beginning of period",
    )

    # Additional Metrics
    free_cash_flow: float | None = Field(
        default=None, alias="freeCashFlow", description="Free cash flow"
    )
    income_taxes_paid: float | None = Field(
        default=None, alias="incomeTaxesPaid", description="Income taxes paid"
    )
    interest_paid: float | None = Field(
        default=None, alias="interestPaid", description="Interest paid"
    )

    @property
    def investing_cash_flow(self) -> float | None:
        """Net cash provided by investing activities."""
        return self.net_cash_provided_by_investing_activities

    @property
    def financing_cash_flow(self) -> float | None:
        """Net cash provided by financing activities."""
        return self.net_cash_provided_by_financing_activities


class KeyMetrics(BaseModel):
    """Key financial metrics"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")
    date: datetime | None = Field(default=None, description="Metrics date")
    fiscal_year: str | None = Field(
        default=None, alias="fiscalYear", description="Fiscal year"
    )
    period: str | None = Field(
        default=None, description="Reporting period (Q1, Q2, Q3, Q4, FY)"
    )
    reported_currency: str | None = Field(
        default=None, alias="reportedCurrency", description="Currency used"
    )

    # Valuation metrics
    market_cap: float | None = Field(
        default=None, alias="marketCap", description="Market capitalization"
    )
    enterprise_value: float | None = Field(
        default=None, alias="enterpriseValue", description="Enterprise value"
    )
    ev_to_sales: float | None = Field(
        default=None, alias="evToSales", description="Enterprise value to sales ratio"
    )
    ev_to_operating_cash_flow: float | None = Field(
        default=None,
        alias="evToOperatingCashFlow",
        description="Enterprise value to operating cash flow ratio",
    )
    ev_to_free_cash_flow: float | None = Field(
        default=None,
        alias="evToFreeCashFlow",
        description="Enterprise value to free cash flow ratio",
    )
    ev_to_ebitda: float | None = Field(
        default=None, alias="evToEBITDA", description="Enterprise value to EBITDA ratio"
    )
    net_debt_to_ebitda: float | None = Field(
        default=None, alias="netDebtToEBITDA", description="Net debt to EBITDA ratio"
    )

    # Liquidity and quality metrics
    current_ratio: float | None = Field(
        default=None, alias="currentRatio", description="Current ratio"
    )
    income_quality: float | None = Field(
        default=None,
        alias="incomeQuality",
        description="Income quality (operating cash flow / net income)",
    )
    graham_number: float | None = Field(
        default=None,
        alias="grahamNumber",
        description="Graham number (fair value estimate)",
    )
    graham_net_net: float | None = Field(
        default=None,
        alias="grahamNetNet",
        description="Graham net-net working capital per share",
    )

    # Tax and interest burden
    tax_burden: float | None = Field(
        default=None, alias="taxBurden", description="Tax burden ratio"
    )
    interest_burden: float | None = Field(
        default=None, alias="interestBurden", description="Interest burden ratio"
    )

    # Capital metrics
    working_capital: float | None = Field(
        default=None,
        alias="workingCapital",
        description="Working capital (current assets - current liabilities)",
    )
    invested_capital: float | None = Field(
        default=None,
        alias="investedCapital",
        description="Invested capital (debt + equity - cash)",
    )

    # Return metrics
    return_on_assets: float | None = Field(
        default=None, alias="returnOnAssets", description="Return on assets (ROA)"
    )
    operating_return_on_assets: float | None = Field(
        default=None,
        alias="operatingReturnOnAssets",
        description="Operating return on assets",
    )
    return_on_tangible_assets: float | None = Field(
        default=None,
        alias="returnOnTangibleAssets",
        description="Return on tangible assets",
    )
    return_on_equity: float | None = Field(
        default=None, alias="returnOnEquity", description="Return on equity (ROE)"
    )
    return_on_invested_capital: float | None = Field(
        default=None,
        alias="returnOnInvestedCapital",
        description="Return on invested capital (ROIC)",
    )
    return_on_capital_employed: float | None = Field(
        default=None,
        alias="returnOnCapitalEmployed",
        description="Return on capital employed (ROCE)",
    )

    # Yield metrics
    earnings_yield: float | None = Field(
        default=None, alias="earningsYield", description="Earnings yield"
    )
    free_cash_flow_yield: float | None = Field(
        default=None, alias="freeCashFlowYield", description="Free cash flow yield"
    )

    # CapEx ratios
    capex_to_operating_cash_flow: float | None = Field(
        default=None,
        alias="capexToOperatingCashFlow",
        description="CapEx to operating cash flow ratio",
    )
    capex_to_depreciation: float | None = Field(
        default=None,
        alias="capexToDepreciation",
        description="CapEx to depreciation ratio",
    )
    capex_to_revenue: float | None = Field(
        default=None, alias="capexToRevenue", description="CapEx to revenue ratio"
    )

    # Expense ratios
    sales_general_and_administrative_to_revenue: float | None = Field(
        default=None,
        alias="salesGeneralAndAdministrativeToRevenue",
        description="SG&A to revenue ratio",
    )
    research_and_developement_to_revenue: float | None = Field(
        default=None,
        alias="researchAndDevelopementToRevenue",
        description="R&D to revenue ratio",
    )
    stock_based_compensation_to_revenue: float | None = Field(
        default=None,
        alias="stockBasedCompensationToRevenue",
        description="Stock-based compensation to revenue ratio",
    )
    intangibles_to_total_assets: float | None = Field(
        default=None,
        alias="intangiblesToTotalAssets",
        description="Intangible assets to total assets ratio",
    )

    # Working capital cycle metrics
    average_receivables: float | None = Field(
        default=None, alias="averageReceivables", description="Average receivables"
    )
    average_payables: float | None = Field(
        default=None, alias="averagePayables", description="Average payables"
    )
    average_inventory: float | None = Field(
        default=None, alias="averageInventory", description="Average inventory"
    )
    days_of_sales_outstanding: float | None = Field(
        default=None,
        alias="daysOfSalesOutstanding",
        description="Days sales outstanding (DSO)",
    )
    days_of_payables_outstanding: float | None = Field(
        default=None,
        alias="daysOfPayablesOutstanding",
        description="Days payables outstanding (DPO)",
    )
    days_of_inventory_outstanding: float | None = Field(
        default=None,
        alias="daysOfInventoryOutstanding",
        description="Days inventory outstanding (DIO)",
    )
    operating_cycle: float | None = Field(
        default=None, alias="operatingCycle", description="Operating cycle in days"
    )
    cash_conversion_cycle: float | None = Field(
        default=None,
        alias="cashConversionCycle",
        description="Cash conversion cycle in days",
    )

    # Free cash flow metrics
    free_cash_flow_to_equity: float | None = Field(
        default=None,
        alias="freeCashFlowToEquity",
        description="Free cash flow to equity",
    )
    free_cash_flow_to_firm: float | None = Field(
        default=None, alias="freeCashFlowToFirm", description="Free cash flow to firm"
    )

    # Asset value metrics
    tangible_asset_value: float | None = Field(
        default=None, alias="tangibleAssetValue", description="Tangible asset value"
    )
    net_current_asset_value: float | None = Field(
        default=None,
        alias="netCurrentAssetValue",
        description="Net current asset value (NCAV)",
    )


class KeyMetricsTTM(BaseModel):
    """Trailing twelve months key metrics"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")
    market_cap: float | None = Field(
        default=None, alias="marketCap", description="Market capitalization"
    )

    # Valuation metrics (TTM)
    enterprise_value_ttm: float | None = Field(
        default=None, alias="enterpriseValueTTM", description="Enterprise value TTM"
    )
    ev_to_sales_ttm: float | None = Field(
        default=None,
        alias="evToSalesTTM",
        description="Enterprise value to sales ratio TTM",
    )
    ev_to_operating_cash_flow_ttm: float | None = Field(
        default=None,
        alias="evToOperatingCashFlowTTM",
        description="Enterprise value to operating cash flow ratio TTM",
    )
    ev_to_free_cash_flow_ttm: float | None = Field(
        default=None,
        alias="evToFreeCashFlowTTM",
        description="Enterprise value to free cash flow ratio TTM",
    )
    ev_to_ebitda_ttm: float | None = Field(
        default=None,
        alias="evToEBITDATTM",
        description="Enterprise value to EBITDA ratio TTM",
    )
    net_debt_to_ebitda_ttm: float | None = Field(
        default=None,
        alias="netDebtToEBITDATTM",
        description="Net debt to EBITDA ratio TTM",
    )

    # Liquidity and quality metrics (TTM)
    current_ratio_ttm: float | None = Field(
        default=None, alias="currentRatioTTM", description="Current ratio TTM"
    )
    income_quality_ttm: float | None = Field(
        default=None, alias="incomeQualityTTM", description="Income quality TTM"
    )
    graham_number_ttm: float | None = Field(
        default=None, alias="grahamNumberTTM", description="Graham number TTM"
    )
    graham_net_net_ttm: float | None = Field(
        default=None,
        alias="grahamNetNetTTM",
        description="Graham net-net working capital per share TTM",
    )

    # Tax and interest burden (TTM)
    tax_burden_ttm: float | None = Field(
        default=None, alias="taxBurdenTTM", description="Tax burden ratio TTM"
    )
    interest_burden_ttm: float | None = Field(
        default=None, alias="interestBurdenTTM", description="Interest burden ratio TTM"
    )

    # Capital metrics (TTM)
    working_capital_ttm: float | None = Field(
        default=None, alias="workingCapitalTTM", description="Working capital TTM"
    )
    invested_capital_ttm: float | None = Field(
        default=None, alias="investedCapitalTTM", description="Invested capital TTM"
    )

    # Return metrics (TTM)
    return_on_assets_ttm: float | None = Field(
        default=None, alias="returnOnAssetsTTM", description="Return on assets TTM"
    )
    operating_return_on_assets_ttm: float | None = Field(
        default=None,
        alias="operatingReturnOnAssetsTTM",
        description="Operating return on assets TTM",
    )
    return_on_tangible_assets_ttm: float | None = Field(
        default=None,
        alias="returnOnTangibleAssetsTTM",
        description="Return on tangible assets TTM",
    )
    return_on_equity_ttm: float | None = Field(
        default=None, alias="returnOnEquityTTM", description="Return on equity TTM"
    )
    return_on_invested_capital_ttm: float | None = Field(
        default=None,
        alias="returnOnInvestedCapitalTTM",
        description="Return on invested capital TTM",
    )
    return_on_capital_employed_ttm: float | None = Field(
        default=None,
        alias="returnOnCapitalEmployedTTM",
        description="Return on capital employed TTM",
    )

    # Yield metrics (TTM)
    earnings_yield_ttm: float | None = Field(
        default=None, alias="earningsYieldTTM", description="Earnings yield TTM"
    )
    free_cash_flow_yield_ttm: float | None = Field(
        default=None,
        alias="freeCashFlowYieldTTM",
        description="Free cash flow yield TTM",
    )

    # CapEx ratios (TTM)
    capex_to_operating_cash_flow_ttm: float | None = Field(
        default=None,
        alias="capexToOperatingCashFlowTTM",
        description="CapEx to operating cash flow ratio TTM",
    )
    capex_to_depreciation_ttm: float | None = Field(
        default=None,
        alias="capexToDepreciationTTM",
        description="CapEx to depreciation ratio TTM",
    )
    capex_to_revenue_ttm: float | None = Field(
        default=None,
        alias="capexToRevenueTTM",
        description="CapEx to revenue ratio TTM",
    )

    # Expense ratios (TTM)
    sales_general_and_administrative_to_revenue_ttm: float | None = Field(
        default=None,
        alias="salesGeneralAndAdministrativeToRevenueTTM",
        description="SG&A to revenue ratio TTM",
    )
    research_and_developement_to_revenue_ttm: float | None = Field(
        default=None,
        alias="researchAndDevelopementToRevenueTTM",
        description="R&D to revenue ratio TTM",
    )
    stock_based_compensation_to_revenue_ttm: float | None = Field(
        default=None,
        alias="stockBasedCompensationToRevenueTTM",
        description="Stock-based compensation to revenue ratio TTM",
    )
    intangibles_to_total_assets_ttm: float | None = Field(
        default=None,
        alias="intangiblesToTotalAssetsTTM",
        description="Intangible assets to total assets ratio TTM",
    )

    # Working capital cycle metrics (TTM)
    average_receivables_ttm: float | None = Field(
        default=None,
        alias="averageReceivablesTTM",
        description="Average receivables TTM",
    )
    average_payables_ttm: float | None = Field(
        default=None, alias="averagePayablesTTM", description="Average payables TTM"
    )
    average_inventory_ttm: float | None = Field(
        default=None, alias="averageInventoryTTM", description="Average inventory TTM"
    )
    days_of_sales_outstanding_ttm: float | None = Field(
        default=None,
        alias="daysOfSalesOutstandingTTM",
        description="Days sales outstanding TTM",
    )
    days_of_payables_outstanding_ttm: float | None = Field(
        default=None,
        alias="daysOfPayablesOutstandingTTM",
        description="Days payables outstanding TTM",
    )
    days_of_inventory_outstanding_ttm: float | None = Field(
        default=None,
        alias="daysOfInventoryOutstandingTTM",
        description="Days inventory outstanding TTM",
    )
    operating_cycle_ttm: float | None = Field(
        default=None, alias="operatingCycleTTM", description="Operating cycle TTM"
    )
    cash_conversion_cycle_ttm: float | None = Field(
        default=None,
        alias="cashConversionCycleTTM",
        description="Cash conversion cycle TTM",
    )

    # Free cash flow metrics (TTM)
    free_cash_flow_to_equity_ttm: float | None = Field(
        default=None,
        alias="freeCashFlowToEquityTTM",
        description="Free cash flow to equity TTM",
    )
    free_cash_flow_to_firm_ttm: float | None = Field(
        default=None,
        alias="freeCashFlowToFirmTTM",
        description="Free cash flow to firm TTM",
    )

    # Asset value metrics (TTM)
    tangible_asset_value_ttm: float | None = Field(
        default=None,
        alias="tangibleAssetValueTTM",
        description="Tangible asset value TTM",
    )
    net_current_asset_value_ttm: float | None = Field(
        default=None,
        alias="netCurrentAssetValueTTM",
        description="Net current asset value TTM",
    )


class FinancialRatios(BaseModel):
    """Financial ratios"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")
    date: datetime | None = Field(default=None, description="Ratios date")
    fiscal_year: str | None = Field(
        default=None, alias="fiscalYear", description="Fiscal year"
    )
    period: str | None = Field(
        default=None, description="Reporting period (Q1, Q2, Q3, Q4, FY)"
    )
    reported_currency: str | None = Field(
        default=None, alias="reportedCurrency", description="Currency used"
    )

    # Profitability margins
    gross_profit_margin: float | None = Field(
        default=None, alias="grossProfitMargin", description="Gross profit margin"
    )
    ebit_margin: float | None = Field(
        default=None, alias="ebitMargin", description="EBIT margin"
    )
    ebitda_margin: float | None = Field(
        default=None, alias="ebitdaMargin", description="EBITDA margin"
    )
    operating_profit_margin: float | None = Field(
        default=None,
        alias="operatingProfitMargin",
        description="Operating profit margin",
    )
    pretax_profit_margin: float | None = Field(
        default=None, alias="pretaxProfitMargin", description="Pre-tax profit margin"
    )
    continuous_operations_profit_margin: float | None = Field(
        default=None,
        alias="continuousOperationsProfitMargin",
        description="Continuous operations profit margin",
    )
    net_profit_margin: float | None = Field(
        default=None, alias="netProfitMargin", description="Net profit margin"
    )
    bottom_line_profit_margin: float | None = Field(
        default=None,
        alias="bottomLineProfitMargin",
        description="Bottom line profit margin",
    )

    # Activity/turnover ratios
    receivables_turnover: float | None = Field(
        default=None, alias="receivablesTurnover", description="Receivables turnover"
    )
    payables_turnover: float | None = Field(
        default=None, alias="payablesTurnover", description="Payables turnover"
    )
    inventory_turnover: float | None = Field(
        default=None, alias="inventoryTurnover", description="Inventory turnover"
    )
    fixed_asset_turnover: float | None = Field(
        default=None, alias="fixedAssetTurnover", description="Fixed asset turnover"
    )
    asset_turnover: float | None = Field(
        default=None, alias="assetTurnover", description="Asset turnover"
    )

    # Liquidity ratios
    current_ratio: float | None = Field(
        default=None, alias="currentRatio", description="Current ratio"
    )
    quick_ratio: float | None = Field(
        default=None, alias="quickRatio", description="Quick ratio"
    )
    solvency_ratio: float | None = Field(
        default=None, alias="solvencyRatio", description="Solvency ratio"
    )
    cash_ratio: float | None = Field(
        default=None, alias="cashRatio", description="Cash ratio"
    )

    # Valuation ratios
    price_to_earnings_ratio: float | None = Field(
        default=None,
        alias="priceToEarningsRatio",
        description="Price to earnings ratio",
    )
    price_to_earnings_growth_ratio: float | None = Field(
        default=None,
        alias="priceToEarningsGrowthRatio",
        description="Price to earnings growth ratio (PEG)",
    )
    forward_price_to_earnings_growth_ratio: float | None = Field(
        default=None,
        alias="forwardPriceToEarningsGrowthRatio",
        description="Forward price to earnings growth ratio",
    )
    price_to_book_ratio: float | None = Field(
        default=None, alias="priceToBookRatio", description="Price to book ratio"
    )
    price_to_sales_ratio: float | None = Field(
        default=None, alias="priceToSalesRatio", description="Price to sales ratio"
    )
    price_to_free_cash_flow_ratio: float | None = Field(
        default=None,
        alias="priceToFreeCashFlowRatio",
        description="Price to free cash flow ratio",
    )
    price_to_operating_cash_flow_ratio: float | None = Field(
        default=None,
        alias="priceToOperatingCashFlowRatio",
        description="Price to operating cash flow ratio",
    )

    # Leverage ratios
    debt_to_assets_ratio: float | None = Field(
        default=None, alias="debtToAssetsRatio", description="Debt to assets ratio"
    )
    debt_to_equity_ratio: float | None = Field(
        default=None, alias="debtToEquityRatio", description="Debt to equity ratio"
    )
    debt_to_capital_ratio: float | None = Field(
        default=None, alias="debtToCapitalRatio", description="Debt to capital ratio"
    )
    long_term_debt_to_capital_ratio: float | None = Field(
        default=None,
        alias="longTermDebtToCapitalRatio",
        description="Long-term debt to capital ratio",
    )
    financial_leverage_ratio: float | None = Field(
        default=None,
        alias="financialLeverageRatio",
        description="Financial leverage ratio",
    )
    working_capital_turnover_ratio: float | None = Field(
        default=None,
        alias="workingCapitalTurnoverRatio",
        description="Working capital turnover ratio",
    )

    # Cash flow ratios
    operating_cash_flow_ratio: float | None = Field(
        default=None,
        alias="operatingCashFlowRatio",
        description="Operating cash flow ratio",
    )
    operating_cash_flow_sales_ratio: float | None = Field(
        default=None,
        alias="operatingCashFlowSalesRatio",
        description="Operating cash flow to sales ratio",
    )
    free_cash_flow_operating_cash_flow_ratio: float | None = Field(
        default=None,
        alias="freeCashFlowOperatingCashFlowRatio",
        description="Free cash flow to operating cash flow ratio",
    )
    debt_service_coverage_ratio: float | None = Field(
        default=None,
        alias="debtServiceCoverageRatio",
        description="Debt service coverage ratio",
    )
    interest_coverage_ratio: float | None = Field(
        default=None,
        alias="interestCoverageRatio",
        description="Interest coverage ratio",
    )
    short_term_operating_cash_flow_coverage_ratio: float | None = Field(
        default=None,
        alias="shortTermOperatingCashFlowCoverageRatio",
        description="Short-term operating cash flow coverage ratio",
    )
    operating_cash_flow_coverage_ratio: float | None = Field(
        default=None,
        alias="operatingCashFlowCoverageRatio",
        description="Operating cash flow coverage ratio",
    )
    capital_expenditure_coverage_ratio: float | None = Field(
        default=None,
        alias="capitalExpenditureCoverageRatio",
        description="Capital expenditure coverage ratio",
    )
    dividend_paid_and_capex_coverage_ratio: float | None = Field(
        default=None,
        alias="dividendPaidAndCapexCoverageRatio",
        description="Dividend paid and CapEx coverage ratio",
    )

    # Dividend metrics
    dividend_payout_ratio: float | None = Field(
        default=None, alias="dividendPayoutRatio", description="Dividend payout ratio"
    )
    dividend_yield: float | None = Field(
        default=None, alias="dividendYield", description="Dividend yield"
    )
    dividend_yield_percentage: float | None = Field(
        default=None,
        alias="dividendYieldPercentage",
        description="Dividend yield percentage",
    )
    dividend_per_share: float | None = Field(
        default=None, alias="dividendPerShare", description="Dividend per share"
    )

    # Per-share metrics
    revenue_per_share: float | None = Field(
        default=None, alias="revenuePerShare", description="Revenue per share"
    )
    net_income_per_share: float | None = Field(
        default=None, alias="netIncomePerShare", description="Net income per share"
    )
    interest_debt_per_share: float | None = Field(
        default=None,
        alias="interestDebtPerShare",
        description="Interest debt per share",
    )
    cash_per_share: float | None = Field(
        default=None, alias="cashPerShare", description="Cash per share"
    )
    book_value_per_share: float | None = Field(
        default=None, alias="bookValuePerShare", description="Book value per share"
    )
    tangible_book_value_per_share: float | None = Field(
        default=None,
        alias="tangibleBookValuePerShare",
        description="Tangible book value per share",
    )
    shareholders_equity_per_share: float | None = Field(
        default=None,
        alias="shareholdersEquityPerShare",
        description="Shareholders equity per share",
    )
    operating_cash_flow_per_share: float | None = Field(
        default=None,
        alias="operatingCashFlowPerShare",
        description="Operating cash flow per share",
    )
    capex_per_share: float | None = Field(
        default=None, alias="capexPerShare", description="CapEx per share"
    )
    free_cash_flow_per_share: float | None = Field(
        default=None,
        alias="freeCashFlowPerShare",
        description="Free cash flow per share",
    )

    # Other metrics
    net_income_per_ebt: float | None = Field(
        default=None, alias="netIncomePerEBT", description="Net income per EBT"
    )
    ebt_per_ebit: float | None = Field(
        default=None, alias="ebtPerEbit", description="EBT per EBIT"
    )
    price_to_fair_value: float | None = Field(
        default=None, alias="priceToFairValue", description="Price to fair value ratio"
    )
    debt_to_market_cap: float | None = Field(
        default=None, alias="debtToMarketCap", description="Debt to market cap ratio"
    )
    effective_tax_rate: float | None = Field(
        default=None, alias="effectiveTaxRate", description="Effective tax rate"
    )
    enterprise_value_multiple: float | None = Field(
        default=None,
        alias="enterpriseValueMultiple",
        description="Enterprise value multiple (EV/EBITDA)",
    )


class FinancialRatiosTTM(BaseModel):
    """Trailing twelve months financial ratios"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")

    # Profitability margins (TTM)
    gross_profit_margin_ttm: float | None = Field(
        default=None,
        alias="grossProfitMarginTTM",
        description="Gross profit margin TTM",
    )
    ebit_margin_ttm: float | None = Field(
        default=None, alias="ebitMarginTTM", description="EBIT margin TTM"
    )
    ebitda_margin_ttm: float | None = Field(
        default=None, alias="ebitdaMarginTTM", description="EBITDA margin TTM"
    )
    operating_profit_margin_ttm: float | None = Field(
        default=None,
        alias="operatingProfitMarginTTM",
        description="Operating profit margin TTM",
    )
    pretax_profit_margin_ttm: float | None = Field(
        default=None,
        alias="pretaxProfitMarginTTM",
        description="Pre-tax profit margin TTM",
    )
    continuous_operations_profit_margin_ttm: float | None = Field(
        default=None,
        alias="continuousOperationsProfitMarginTTM",
        description="Continuous operations profit margin TTM",
    )
    net_profit_margin_ttm: float | None = Field(
        default=None, alias="netProfitMarginTTM", description="Net profit margin TTM"
    )
    bottom_line_profit_margin_ttm: float | None = Field(
        default=None,
        alias="bottomLineProfitMarginTTM",
        description="Bottom line profit margin TTM",
    )

    # Activity/turnover ratios (TTM)
    receivables_turnover_ttm: float | None = Field(
        default=None,
        alias="receivablesTurnoverTTM",
        description="Receivables turnover TTM",
    )
    payables_turnover_ttm: float | None = Field(
        default=None, alias="payablesTurnoverTTM", description="Payables turnover TTM"
    )
    inventory_turnover_ttm: float | None = Field(
        default=None, alias="inventoryTurnoverTTM", description="Inventory turnover TTM"
    )
    fixed_asset_turnover_ttm: float | None = Field(
        default=None,
        alias="fixedAssetTurnoverTTM",
        description="Fixed asset turnover TTM",
    )
    asset_turnover_ttm: float | None = Field(
        default=None, alias="assetTurnoverTTM", description="Asset turnover TTM"
    )

    # Liquidity ratios (TTM)
    current_ratio_ttm: float | None = Field(
        default=None, alias="currentRatioTTM", description="Current ratio TTM"
    )
    quick_ratio_ttm: float | None = Field(
        default=None, alias="quickRatioTTM", description="Quick ratio TTM"
    )
    solvency_ratio_ttm: float | None = Field(
        default=None, alias="solvencyRatioTTM", description="Solvency ratio TTM"
    )
    cash_ratio_ttm: float | None = Field(
        default=None, alias="cashRatioTTM", description="Cash ratio TTM"
    )

    # Valuation ratios (TTM)
    price_to_earnings_ratio_ttm: float | None = Field(
        default=None,
        alias="priceToEarningsRatioTTM",
        description="Price to earnings ratio TTM",
    )
    price_to_earnings_growth_ratio_ttm: float | None = Field(
        default=None,
        alias="priceToEarningsGrowthRatioTTM",
        description="Price to earnings growth ratio TTM",
    )
    forward_price_to_earnings_growth_ratio_ttm: float | None = Field(
        default=None,
        alias="forwardPriceToEarningsGrowthRatioTTM",
        description="Forward price to earnings growth ratio TTM",
    )
    price_to_book_ratio_ttm: float | None = Field(
        default=None, alias="priceToBookRatioTTM", description="Price to book ratio TTM"
    )
    price_to_sales_ratio_ttm: float | None = Field(
        default=None,
        alias="priceToSalesRatioTTM",
        description="Price to sales ratio TTM",
    )
    price_to_free_cash_flow_ratio_ttm: float | None = Field(
        default=None,
        alias="priceToFreeCashFlowRatioTTM",
        description="Price to free cash flow ratio TTM",
    )
    price_to_operating_cash_flow_ratio_ttm: float | None = Field(
        default=None,
        alias="priceToOperatingCashFlowRatioTTM",
        description="Price to operating cash flow ratio TTM",
    )

    # Leverage ratios (TTM)
    debt_to_assets_ratio_ttm: float | None = Field(
        default=None,
        alias="debtToAssetsRatioTTM",
        description="Debt to assets ratio TTM",
    )
    debt_to_equity_ratio_ttm: float | None = Field(
        default=None,
        alias="debtToEquityRatioTTM",
        description="Debt to equity ratio TTM",
    )
    debt_to_capital_ratio_ttm: float | None = Field(
        default=None,
        alias="debtToCapitalRatioTTM",
        description="Debt to capital ratio TTM",
    )
    long_term_debt_to_capital_ratio_ttm: float | None = Field(
        default=None,
        alias="longTermDebtToCapitalRatioTTM",
        description="Long-term debt to capital ratio TTM",
    )
    financial_leverage_ratio_ttm: float | None = Field(
        default=None,
        alias="financialLeverageRatioTTM",
        description="Financial leverage ratio TTM",
    )
    working_capital_turnover_ratio_ttm: float | None = Field(
        default=None,
        alias="workingCapitalTurnoverRatioTTM",
        description="Working capital turnover ratio TTM",
    )

    # Cash flow ratios (TTM)
    operating_cash_flow_ratio_ttm: float | None = Field(
        default=None,
        alias="operatingCashFlowRatioTTM",
        description="Operating cash flow ratio TTM",
    )
    operating_cash_flow_sales_ratio_ttm: float | None = Field(
        default=None,
        alias="operatingCashFlowSalesRatioTTM",
        description="Operating cash flow to sales ratio TTM",
    )
    free_cash_flow_operating_cash_flow_ratio_ttm: float | None = Field(
        default=None,
        alias="freeCashFlowOperatingCashFlowRatioTTM",
        description="Free cash flow to operating cash flow ratio TTM",
    )
    debt_service_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="debtServiceCoverageRatioTTM",
        description="Debt service coverage ratio TTM",
    )
    interest_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="interestCoverageRatioTTM",
        description="Interest coverage ratio TTM",
    )
    short_term_operating_cash_flow_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="shortTermOperatingCashFlowCoverageRatioTTM",
        description="Short-term operating cash flow coverage ratio TTM",
    )
    operating_cash_flow_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="operatingCashFlowCoverageRatioTTM",
        description="Operating cash flow coverage ratio TTM",
    )
    capital_expenditure_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="capitalExpenditureCoverageRatioTTM",
        description="Capital expenditure coverage ratio TTM",
    )
    dividend_paid_and_capex_coverage_ratio_ttm: float | None = Field(
        default=None,
        alias="dividendPaidAndCapexCoverageRatioTTM",
        description="Dividend paid and CapEx coverage ratio TTM",
    )

    # Dividend metrics (TTM)
    dividend_payout_ratio_ttm: float | None = Field(
        default=None,
        alias="dividendPayoutRatioTTM",
        description="Dividend payout ratio TTM",
    )
    dividend_yield_ttm: float | None = Field(
        default=None, alias="dividendYieldTTM", description="Dividend yield TTM"
    )
    dividend_per_share_ttm: float | None = Field(
        default=None, alias="dividendPerShareTTM", description="Dividend per share TTM"
    )

    # Enterprise value (TTM)
    enterprise_value_ttm: float | None = Field(
        default=None, alias="enterpriseValueTTM", description="Enterprise value TTM"
    )

    # Per-share metrics (TTM)
    revenue_per_share_ttm: float | None = Field(
        default=None, alias="revenuePerShareTTM", description="Revenue per share TTM"
    )
    net_income_per_share_ttm: float | None = Field(
        default=None,
        alias="netIncomePerShareTTM",
        description="Net income per share TTM",
    )
    interest_debt_per_share_ttm: float | None = Field(
        default=None,
        alias="interestDebtPerShareTTM",
        description="Interest debt per share TTM",
    )
    cash_per_share_ttm: float | None = Field(
        default=None, alias="cashPerShareTTM", description="Cash per share TTM"
    )
    book_value_per_share_ttm: float | None = Field(
        default=None,
        alias="bookValuePerShareTTM",
        description="Book value per share TTM",
    )
    tangible_book_value_per_share_ttm: float | None = Field(
        default=None,
        alias="tangibleBookValuePerShareTTM",
        description="Tangible book value per share TTM",
    )
    shareholders_equity_per_share_ttm: float | None = Field(
        default=None,
        alias="shareholdersEquityPerShareTTM",
        description="Shareholders equity per share TTM",
    )
    operating_cash_flow_per_share_ttm: float | None = Field(
        default=None,
        alias="operatingCashFlowPerShareTTM",
        description="Operating cash flow per share TTM",
    )
    capex_per_share_ttm: float | None = Field(
        default=None, alias="capexPerShareTTM", description="CapEx per share TTM"
    )
    free_cash_flow_per_share_ttm: float | None = Field(
        default=None,
        alias="freeCashFlowPerShareTTM",
        description="Free cash flow per share TTM",
    )

    # Other metrics (TTM)
    net_income_per_ebt_ttm: float | None = Field(
        default=None, alias="netIncomePerEBTTTM", description="Net income per EBT TTM"
    )
    ebt_per_ebit_ttm: float | None = Field(
        default=None, alias="ebtPerEbitTTM", description="EBT per EBIT TTM"
    )
    price_to_fair_value_ttm: float | None = Field(
        default=None,
        alias="priceToFairValueTTM",
        description="Price to fair value ratio TTM",
    )
    debt_to_market_cap_ttm: float | None = Field(
        default=None,
        alias="debtToMarketCapTTM",
        description="Debt to market cap ratio TTM",
    )
    effective_tax_rate_ttm: float | None = Field(
        default=None, alias="effectiveTaxRateTTM", description="Effective tax rate TTM"
    )
    enterprise_value_multiple_ttm: float | None = Field(
        default=None,
        alias="enterpriseValueMultipleTTM",
        description="Enterprise value multiple TTM",
    )


class FinancialGrowth(BaseModel):
    """Financial growth metrics"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")
    date: datetime | None = Field(default=None, description="Growth metrics date")
    fiscal_year: str | None = Field(
        default=None, alias="fiscalYear", description="Fiscal year"
    )
    period: str | None = Field(
        default=None, description="Reporting period (Q1, Q2, Q3, Q4, FY)"
    )
    reported_currency: str | None = Field(
        default=None, alias="reportedCurrency", description="Currency used"
    )

    # Revenue and profit growth
    revenue_growth: float | None = Field(
        default=None, alias="revenueGrowth", description="Revenue growth"
    )
    gross_profit_growth: float | None = Field(
        default=None, alias="grossProfitGrowth", description="Gross profit growth"
    )

    # Operating metrics growth
    ebit_growth: float | None = Field(
        default=None, alias="ebitgrowth", description="EBIT growth"
    )
    ebitda_growth: float | None = Field(
        default=None, alias="ebitdaGrowth", description="EBITDA growth"
    )
    operating_income_growth: float | None = Field(
        default=None,
        alias="operatingIncomeGrowth",
        description="Operating income growth",
    )

    # Net income and EPS growth
    net_income_growth: float | None = Field(
        default=None, alias="netIncomeGrowth", description="Net income growth"
    )
    eps_growth: float | None = Field(
        default=None,
        validation_alias=AliasChoices("epsGrowth", "epsgrowth"),
        description="EPS growth",
    )
    eps_diluted_growth: float | None = Field(
        default=None, alias="epsdilutedGrowth", description="Diluted EPS growth"
    )

    # Share-related growth
    weighted_average_shares_growth: float | None = Field(
        default=None,
        alias="weightedAverageSharesGrowth",
        description="Weighted average shares growth",
    )
    weighted_average_shares_diluted_growth: float | None = Field(
        default=None,
        alias="weightedAverageSharesDilutedGrowth",
        description="Weighted average diluted shares growth",
    )

    # Dividend and cash flow growth
    dividends_per_share_growth: float | None = Field(
        default=None,
        alias="dividendsPerShareGrowth",
        description="Dividends per share growth",
    )
    operating_cash_flow_growth: float | None = Field(
        default=None,
        alias="operatingCashFlowGrowth",
        description="Operating cash flow growth",
    )
    free_cash_flow_growth: float | None = Field(
        default=None, alias="freeCashFlowGrowth", description="Free cash flow growth"
    )

    # Balance sheet growth
    receivables_growth: float | None = Field(
        default=None, alias="receivablesGrowth", description="Receivables growth"
    )
    inventory_growth: float | None = Field(
        default=None, alias="inventoryGrowth", description="Inventory growth"
    )
    asset_growth: float | None = Field(
        default=None, alias="assetGrowth", description="Asset growth"
    )
    debt_growth: float | None = Field(
        default=None, alias="debtGrowth", description="Debt growth"
    )
    book_value_per_share_growth: float | None = Field(
        default=None,
        alias="bookValueperShareGrowth",
        description="Book value per share growth",
    )

    # Expense growth
    rd_expense_growth: float | None = Field(
        default=None, alias="rdexpenseGrowth", description="R&D expense growth"
    )
    sga_expenses_growth: float | None = Field(
        default=None, alias="sgaexpensesGrowth", description="SG&A expenses growth"
    )

    # Capital expenditure growth
    growth_capital_expenditure: float | None = Field(
        default=None,
        alias="growthCapitalExpenditure",
        description="Capital expenditure growth",
    )

    # Multi-year revenue growth per share
    ten_y_revenue_growth_per_share: float | None = Field(
        default=None,
        alias="tenYRevenueGrowthPerShare",
        description="10-year revenue growth per share",
    )
    five_y_revenue_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYRevenueGrowthPerShare",
        description="5-year revenue growth per share",
    )
    three_y_revenue_growth_per_share: float | None = Field(
        default=None,
        alias="threeYRevenueGrowthPerShare",
        description="3-year revenue growth per share",
    )

    # Multi-year operating cash flow growth per share
    ten_y_operating_cf_growth_per_share: float | None = Field(
        default=None,
        alias="tenYOperatingCFGrowthPerShare",
        description="10-year operating cash flow growth per share",
    )
    five_y_operating_cf_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYOperatingCFGrowthPerShare",
        description="5-year operating cash flow growth per share",
    )
    three_y_operating_cf_growth_per_share: float | None = Field(
        default=None,
        alias="threeYOperatingCFGrowthPerShare",
        description="3-year operating cash flow growth per share",
    )

    # Multi-year net income growth per share
    ten_y_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="tenYNetIncomeGrowthPerShare",
        description="10-year net income growth per share",
    )
    five_y_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYNetIncomeGrowthPerShare",
        description="5-year net income growth per share",
    )
    three_y_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="threeYNetIncomeGrowthPerShare",
        description="3-year net income growth per share",
    )

    # Multi-year shareholders equity growth per share
    ten_y_shareholders_equity_growth_per_share: float | None = Field(
        default=None,
        alias="tenYShareholdersEquityGrowthPerShare",
        description="10-year shareholders equity growth per share",
    )
    five_y_shareholders_equity_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYShareholdersEquityGrowthPerShare",
        description="5-year shareholders equity growth per share",
    )
    three_y_shareholders_equity_growth_per_share: float | None = Field(
        default=None,
        alias="threeYShareholdersEquityGrowthPerShare",
        description="3-year shareholders equity growth per share",
    )

    # Multi-year dividend per share growth per share
    ten_y_dividend_per_share_growth_per_share: float | None = Field(
        default=None,
        alias="tenYDividendperShareGrowthPerShare",
        description="10-year dividend per share growth per share",
    )
    five_y_dividend_per_share_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYDividendperShareGrowthPerShare",
        description="5-year dividend per share growth per share",
    )
    three_y_dividend_per_share_growth_per_share: float | None = Field(
        default=None,
        alias="threeYDividendperShareGrowthPerShare",
        description="3-year dividend per share growth per share",
    )

    # Multi-year bottom line net income growth per share
    ten_y_bottom_line_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="tenYBottomLineNetIncomeGrowthPerShare",
        description="10-year bottom line net income growth per share",
    )
    five_y_bottom_line_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="fiveYBottomLineNetIncomeGrowthPerShare",
        description="5-year bottom line net income growth per share",
    )
    three_y_bottom_line_net_income_growth_per_share: float | None = Field(
        default=None,
        alias="threeYBottomLineNetIncomeGrowthPerShare",
        description="3-year bottom line net income growth per share",
    )

    # Income statement line-item growth
    growth_revenue: float | None = Field(
        default=None, alias="growthRevenue", description="Revenue growth"
    )
    growth_cost_of_revenue: float | None = Field(
        default=None, alias="growthCostOfRevenue", description="Cost of revenue growth"
    )
    growth_gross_profit: float | None = Field(
        default=None, alias="growthGrossProfit", description="Gross profit growth"
    )
    growth_gross_profit_ratio: float | None = Field(
        default=None,
        alias="growthGrossProfitRatio",
        description="Gross profit ratio growth",
    )
    growth_research_and_development_expenses: float | None = Field(
        default=None,
        alias="growthResearchAndDevelopmentExpenses",
        description="Research and development expenses growth",
    )
    growth_general_and_administrative_expenses: float | None = Field(
        default=None,
        alias="growthGeneralAndAdministrativeExpenses",
        description="General and administrative expenses growth",
    )
    growth_selling_and_marketing_expenses: float | None = Field(
        default=None,
        alias="growthSellingAndMarketingExpenses",
        description="Selling and marketing expenses growth",
    )
    growth_other_expenses: float | None = Field(
        default=None,
        alias="growthOtherExpenses",
        description="Other expenses growth",
    )
    growth_operating_expenses: float | None = Field(
        default=None,
        alias="growthOperatingExpenses",
        description="Operating expenses growth",
    )
    growth_operating_income: float | None = Field(
        default=None,
        alias="growthOperatingIncome",
        description="Operating income growth",
    )
    growth_cost_and_expenses: float | None = Field(
        default=None,
        alias="growthCostAndExpenses",
        description="Cost and expenses growth",
    )
    growth_interest_income: float | None = Field(
        default=None,
        alias="growthInterestIncome",
        description="Interest income growth",
    )
    growth_interest_expense: float | None = Field(
        default=None,
        alias="growthInterestExpense",
        description="Interest expense growth",
    )
    growth_depreciation_and_amortization: float | None = Field(
        default=None,
        alias="growthDepreciationAndAmortization",
        description="Depreciation and amortization growth",
    )
    growth_ebitda: float | None = Field(
        default=None, alias="growthEBITDA", description="EBITDA growth"
    )
    growth_ebit: float | None = Field(
        default=None, alias="growthEBIT", description="EBIT growth"
    )
    growth_net_income: float | None = Field(
        default=None, alias="growthNetIncome", description="Net income growth"
    )
    growth_net_income_deductions: float | None = Field(
        default=None,
        alias="growthNetIncomeDeductions",
        description="Net income deductions growth",
    )
    growth_net_income_from_continuing_operations: float | None = Field(
        default=None,
        alias="growthNetIncomeFromContinuingOperations",
        description="Net income from continuing operations growth",
    )
    growth_net_interest_income: float | None = Field(
        default=None,
        alias="growthNetInterestIncome",
        description="Net interest income growth",
    )
    growth_non_operating_income_excluding_interest: float | None = Field(
        default=None,
        alias="growthNonOperatingIncomeExcludingInterest",
        description="Non-operating income excluding interest growth",
    )
    growth_income_before_tax: float | None = Field(
        default=None,
        alias="growthIncomeBeforeTax",
        description="Income before tax growth",
    )
    growth_income_tax_expense: float | None = Field(
        default=None,
        alias="growthIncomeTaxExpense",
        description="Income tax expense growth",
    )
    growth_eps: float | None = Field(
        default=None, alias="growthEPS", description="EPS growth"
    )
    growth_eps_diluted: float | None = Field(
        default=None, alias="growthEPSDiluted", description="Diluted EPS growth"
    )
    growth_weighted_average_shs_out: float | None = Field(
        default=None,
        alias="growthWeightedAverageShsOut",
        description="Weighted average shares outstanding growth",
    )
    growth_weighted_average_shs_out_dil: float | None = Field(
        default=None,
        alias="growthWeightedAverageShsOutDil",
        description="Weighted average diluted shares outstanding growth",
    )
    growth_total_other_income_expenses_net: float | None = Field(
        default=None,
        alias="growthTotalOtherIncomeExpensesNet",
        description="Total other income expenses net growth",
    )
    growth_other_adjustments_to_net_income: float | None = Field(
        default=None,
        alias="growthOtherAdjustmentsToNetIncome",
        description="Other adjustments to net income growth",
    )

    # Balance sheet line-item growth
    growth_cash_and_cash_equivalents: float | None = Field(
        default=None,
        alias="growthCashAndCashEquivalents",
        description="Cash and cash equivalents growth",
    )
    growth_cash_and_short_term_investments: float | None = Field(
        default=None,
        alias="growthCashAndShortTermInvestments",
        description="Cash and short-term investments growth",
    )
    growth_net_receivables: float | None = Field(
        default=None,
        alias="growthNetReceivables",
        description="Net receivables growth",
    )
    growth_inventory: float | None = Field(
        default=None, alias="growthInventory", description="Inventory growth"
    )
    growth_other_current_assets: float | None = Field(
        default=None,
        alias="growthOtherCurrentAssets",
        description="Other current assets growth",
    )
    growth_total_current_assets: float | None = Field(
        default=None,
        alias="growthTotalCurrentAssets",
        description="Total current assets growth",
    )
    growth_property_plant_equipment_net: float | None = Field(
        default=None,
        alias="growthPropertyPlantEquipmentNet",
        description="Property, plant and equipment net growth",
    )
    growth_goodwill: float | None = Field(
        default=None, alias="growthGoodwill", description="Goodwill growth"
    )
    growth_intangible_assets: float | None = Field(
        default=None,
        alias="growthIntangibleAssets",
        description="Intangible assets growth",
    )
    growth_goodwill_and_intangible_assets: float | None = Field(
        default=None,
        alias="growthGoodwillAndIntangibleAssets",
        description="Goodwill and intangible assets growth",
    )
    growth_long_term_investments: float | None = Field(
        default=None,
        alias="growthLongTermInvestments",
        description="Long-term investments growth",
    )
    growth_tax_assets: float | None = Field(
        default=None, alias="growthTaxAssets", description="Tax assets growth"
    )
    growth_tax_payables: float | None = Field(
        default=None, alias="growthTaxPayables", description="Tax payables growth"
    )
    growth_other_non_current_assets: float | None = Field(
        default=None,
        alias="growthOtherNonCurrentAssets",
        description="Other non-current assets growth",
    )
    growth_total_non_current_assets: float | None = Field(
        default=None,
        alias="growthTotalNonCurrentAssets",
        description="Total non-current assets growth",
    )
    growth_other_assets: float | None = Field(
        default=None, alias="growthOtherAssets", description="Other assets growth"
    )
    growth_total_assets: float | None = Field(
        default=None, alias="growthTotalAssets", description="Total assets growth"
    )
    growth_account_payables: float | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "growthAccountPayables", "growthAccountsPayables"
        ),
        alias="growthAccountPayables",
        description="Account payables growth",
    )
    growth_other_payables: float | None = Field(
        default=None,
        alias="growthOtherPayables",
        description="Other payables growth",
    )
    growth_total_payables: float | None = Field(
        default=None,
        alias="growthTotalPayables",
        description="Total payables growth",
    )
    growth_short_term_debt: float | None = Field(
        default=None,
        alias="growthShortTermDebt",
        description="Short-term debt growth",
    )
    growth_deferred_revenue: float | None = Field(
        default=None,
        alias="growthDeferredRevenue",
        description="Deferred revenue growth",
    )
    growth_other_current_liabilities: float | None = Field(
        default=None,
        alias="growthOtherCurrentLiabilities",
        description="Other current liabilities growth",
    )
    growth_total_current_liabilities: float | None = Field(
        default=None,
        alias="growthTotalCurrentLiabilities",
        description="Total current liabilities growth",
    )
    growth_long_term_debt: float | None = Field(
        default=None,
        alias="growthLongTermDebt",
        description="Long-term debt growth",
    )
    growth_deferred_revenue_non_current: float | None = Field(
        default=None,
        alias="growthDeferredRevenueNonCurrent",
        description="Deferred revenue non-current growth",
    )
    growth_deferred_tax_liabilities_non_current: float | None = Field(
        default=None,
        alias="growthDeferredTaxLiabilitiesNonCurrent",
        description="Deferred tax liabilities non-current growth",
    )
    growth_other_non_current_liabilities: float | None = Field(
        default=None,
        alias="growthOtherNonCurrentLiabilities",
        description="Other non-current liabilities growth",
    )
    growth_total_non_current_liabilities: float | None = Field(
        default=None,
        alias="growthTotalNonCurrentLiabilities",
        description="Total non-current liabilities growth",
    )
    growth_other_liabilities: float | None = Field(
        default=None,
        alias="growthOtherLiabilities",
        description="Other liabilities growth",
    )
    growth_capital_lease_obligations_current: float | None = Field(
        default=None,
        alias="growthCapitalLeaseObligationsCurrent",
        description="Capital lease obligations current growth",
    )
    growth_total_liabilities: float | None = Field(
        default=None,
        alias="growthTotalLiabilities",
        description="Total liabilities growth",
    )
    growth_total_liabilities_and_stockholders_equity: float | None = Field(
        default=None,
        alias="growthTotalLiabilitiesAndStockholdersEquity",
        description="Total liabilities and stockholders equity growth",
    )
    growth_common_stock: float | None = Field(
        default=None,
        alias="growthCommonStock",
        description="Common stock growth",
    )
    growth_retained_earnings: float | None = Field(
        default=None,
        alias="growthRetainedEarnings",
        description="Retained earnings growth",
    )
    growth_accumulated_other_comprehensive_income_loss: float | None = Field(
        default=None,
        alias="growthAccumulatedOtherComprehensiveIncomeLoss",
        description="Accumulated other comprehensive income loss growth",
    )
    growth_other_receivables: float | None = Field(
        default=None,
        alias="growthOtherReceivables",
        description="Other receivables growth",
    )
    growth_accounts_receivables: float | None = Field(
        default=None,
        alias="growthAccountsReceivables",
        description="Accounts receivables growth",
    )
    growth_accrued_expenses: float | None = Field(
        default=None,
        alias="growthAccruedExpenses",
        description="Accrued expenses growth",
    )
    growth_additional_paid_in_capital: float | None = Field(
        default=None,
        alias="growthAdditionalPaidInCapital",
        description="Additional paid-in capital growth",
    )
    growth_preferred_stock: float | None = Field(
        default=None,
        alias="growthPreferredStock",
        description="Preferred stock growth",
    )
    growth_prepaids: float | None = Field(
        default=None, alias="growthPrepaids", description="Prepaids growth"
    )
    growth_short_term_investments: float | None = Field(
        default=None,
        alias="growthShortTermInvestments",
        description="Short-term investments growth",
    )
    growth_total_investments: float | None = Field(
        default=None,
        alias="growthTotalInvestments",
        description="Total investments growth",
    )
    growth_net_debt: float | None = Field(
        default=None, alias="growthNetDebt", description="Net debt growth"
    )
    growth_total_debt: float | None = Field(
        default=None, alias="growthTotalDebt", description="Total debt growth"
    )
    growth_total_equity: float | None = Field(
        default=None, alias="growthTotalEquity", description="Total equity growth"
    )
    growth_minority_interest: float | None = Field(
        default=None,
        alias="growthMinorityInterest",
        description="Minority interest growth",
    )
    growth_treasury_stock: float | None = Field(
        default=None,
        alias="growthTreasuryStock",
        description="Treasury stock growth",
    )
    growth_total_stockholders_equity: float | None = Field(
        default=None,
        alias="growthTotalStockholdersEquity",
        description="Total stockholders equity growth",
    )
    growth_other_total_stockholders_equity: float | None = Field(
        default=None,
        alias="growthOthertotalStockholdersEquity",
        description="Other total stockholders equity growth",
    )

    # Cash flow line-item growth
    growth_stock_based_compensation: float | None = Field(
        default=None,
        alias="growthStockBasedCompensation",
        description="Stock-based compensation growth",
    )
    growth_deferred_income_tax: float | None = Field(
        default=None,
        alias="growthDeferredIncomeTax",
        description="Deferred income tax growth",
    )
    growth_change_in_working_capital: float | None = Field(
        default=None,
        alias="growthChangeInWorkingCapital",
        description="Change in working capital growth",
    )
    growth_other_working_capital: float | None = Field(
        default=None,
        alias="growthOtherWorkingCapital",
        description="Other working capital growth",
    )
    growth_other_non_cash_items: float | None = Field(
        default=None,
        alias="growthOtherNonCashItems",
        description="Other non-cash items growth",
    )
    growth_operating_cash_flow: float | None = Field(
        default=None,
        alias="growthOperatingCashFlow",
        description="Operating cash flow growth",
    )
    growth_investments_in_property_plant_and_equipment: float | None = Field(
        default=None,
        alias="growthInvestmentsInPropertyPlantAndEquipment",
        description="Investments in property, plant and equipment growth",
    )
    growth_acquisitions_net: float | None = Field(
        default=None,
        alias="growthAcquisitionsNet",
        description="Acquisitions net growth",
    )
    growth_purchases_of_investments: float | None = Field(
        default=None,
        alias="growthPurchasesOfInvestments",
        description="Purchases of investments growth",
    )
    growth_sales_maturities_of_investments: float | None = Field(
        default=None,
        alias="growthSalesMaturitiesOfInvestments",
        description="Sales and maturities of investments growth",
    )
    growth_other_investing_activites: float | None = Field(
        default=None,
        alias="growthOtherInvestingActivites",
        description="Other investing activities growth",
    )
    growth_net_cash_used_for_investing_activites: float | None = Field(
        default=None,
        alias="growthNetCashUsedForInvestingActivites",
        description="Net cash used for investing activities growth",
    )
    growth_debt_repayment: float | None = Field(
        default=None,
        alias="growthDebtRepayment",
        description="Debt repayment growth",
    )
    growth_common_stock_issued: float | None = Field(
        default=None,
        alias="growthCommonStockIssued",
        description="Common stock issued growth",
    )
    growth_common_stock_repurchased: float | None = Field(
        default=None,
        alias="growthCommonStockRepurchased",
        description="Common stock repurchased growth",
    )
    growth_dividends_paid: float | None = Field(
        default=None,
        alias="growthDividendsPaid",
        description="Dividends paid growth",
    )
    growth_preferred_dividends_paid: float | None = Field(
        default=None,
        alias="growthPreferredDividendsPaid",
        description="Preferred dividends paid growth",
    )
    growth_other_financing_activites: float | None = Field(
        default=None,
        alias="growthOtherFinancingActivites",
        description="Other financing activities growth",
    )
    growth_net_cash_used_provided_by_financing_activities: float | None = Field(
        default=None,
        alias="growthNetCashUsedProvidedByFinancingActivities",
        description="Net cash used/provided by financing activities growth",
    )
    growth_effect_of_forex_changes_on_cash: float | None = Field(
        default=None,
        alias="growthEffectOfForexChangesOnCash",
        description="Effect of forex changes on cash growth",
    )
    growth_net_change_in_cash: float | None = Field(
        default=None,
        alias="growthNetChangeInCash",
        description="Net change in cash growth",
    )
    growth_cash_at_end_of_period: float | None = Field(
        default=None,
        alias="growthCashAtEndOfPeriod",
        description="Cash at end of period growth",
    )
    growth_cash_at_beginning_of_period: float | None = Field(
        default=None,
        alias="growthCashAtBeginningOfPeriod",
        description="Cash at beginning of period growth",
    )
    growth_net_cash_provided_by_operating_activites: float | None = Field(
        default=None,
        alias="growthNetCashProvidedByOperatingActivites",
        description="Net cash provided by operating activities growth",
    )
    growth_free_cash_flow: float | None = Field(
        default=None,
        alias="growthFreeCashFlow",
        description="Free cash flow growth",
    )
    growth_net_debt_issuance: float | None = Field(
        default=None,
        alias="growthNetDebtIssuance",
        description="Net debt issuance growth",
    )
    growth_long_term_net_debt_issuance: float | None = Field(
        default=None,
        alias="growthLongTermNetDebtIssuance",
        description="Long-term net debt issuance growth",
    )
    growth_short_term_net_debt_issuance: float | None = Field(
        default=None,
        alias="growthShortTermNetDebtIssuance",
        description="Short-term net debt issuance growth",
    )
    growth_net_stock_issuance: float | None = Field(
        default=None,
        alias="growthNetStockIssuance",
        description="Net stock issuance growth",
    )
    growth_interest_paid: float | None = Field(
        default=None,
        alias="growthInterestPaid",
        description="Interest paid growth",
    )
    growth_income_taxes_paid: float | None = Field(
        default=None,
        alias="growthIncomeTaxesPaid",
        description="Income taxes paid growth",
    )


class FinancialScore(BaseModel):
    """Company financial score"""

    model_config = default_model_config

    # Metadata
    symbol: str | None = Field(default=None, description="Company symbol")
    reported_currency: str | None = Field(
        default=None, alias="reportedCurrency", description="Currency used"
    )

    # Scores
    altman_z_score: float | None = Field(
        default=None, alias="altmanZScore", description="Altman Z-Score"
    )
    piotroski_score: float | None = Field(
        default=None, alias="piotroskiScore", description="Piotroski Score"
    )

    # Supporting financial metrics used in score calculations
    working_capital: float | None = Field(
        default=None, alias="workingCapital", description="Working capital"
    )
    total_assets: float | None = Field(
        default=None, alias="totalAssets", description="Total assets"
    )
    retained_earnings: float | None = Field(
        default=None, alias="retainedEarnings", description="Retained earnings"
    )
    ebit: float | None = Field(
        default=None, description="Earnings before interest and taxes"
    )
    market_cap: float | None = Field(
        default=None, alias="marketCap", description="Market capitalization"
    )
    total_liabilities: float | None = Field(
        default=None, alias="totalLiabilities", description="Total liabilities"
    )
    revenue: float | None = Field(default=None, description="Revenue")


class DCF(BaseModel):
    """Discounted cash flow valuation"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Valuation date")
    dcf: float | None = Field(None, description="DCF value per share")
    stock_price: float | None = Field(
        None, alias="stockPrice", description="Current stock price"
    )


class CustomDCF(BaseModel):
    """Custom discounted cash flow valuation with detailed components"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    year: str | int | None = Field(default=None, description="Projection year")
    date: datetime | None = Field(default=None, description="Valuation date")
    fcf0: float | None = Field(default=None, description="Current year free cash flow")
    fcf1: float | None = Field(
        default=None,
        description="Year 1 projected free cash flow",
    )
    fcf2: float | None = Field(
        default=None,
        description="Year 2 projected free cash flow",
    )
    fcf3: float | None = Field(
        default=None,
        description="Year 3 projected free cash flow",
    )
    fcf4: float | None = Field(
        default=None,
        description="Year 4 projected free cash flow",
    )
    fcf5: float | None = Field(
        default=None,
        description="Year 5 projected free cash flow",
    )
    fcf6: float | None = Field(
        default=None,
        description="Year 6 projected free cash flow",
    )
    fcf7: float | None = Field(
        default=None,
        description="Year 7 projected free cash flow",
    )
    fcf8: float | None = Field(
        default=None,
        description="Year 8 projected free cash flow",
    )
    fcf9: float | None = Field(
        default=None,
        description="Year 9 projected free cash flow",
    )
    fcf10: float | None = Field(
        default=None,
        description="Year 10 projected free cash flow",
    )
    terminal_value: float | None = Field(
        default=None, alias="terminalValue", description="Terminal value"
    )
    growth_rate: float | None = Field(
        default=None, alias="growthRate", description="Growth rate used"
    )
    terminal_growth_rate: float | None = Field(
        default=None, alias="terminalGrowthRate", description="Terminal growth rate"
    )
    wacc: float | None = Field(
        default=None, description="Weighted average cost of capital"
    )
    present_value_of_fcf: float | None = Field(
        default=None,
        alias="presentValueOfFCF",
        description="Present value of free cash flows",
    )
    present_value_of_terminal_value: float | None = Field(
        default=None,
        alias="presentValueOfTerminalValue",
        description="Present value of terminal value",
    )
    enterprise_value: float | None = Field(
        default=None, alias="enterpriseValue", description="Enterprise value"
    )
    net_debt: float | None = Field(
        default=None, alias="netDebt", description="Net debt"
    )
    equity_value: float | None = Field(
        default=None, alias="equityValue", description="Equity value"
    )
    shares_outstanding: float | None = Field(
        default=None, alias="sharesOutstanding", description="Shares outstanding"
    )
    dcf: float | None = Field(default=None, description="DCF value per share")
    stock_price: float | None = Field(
        default=None, alias="stockPrice", description="Current stock price"
    )
    implied_share_price: float | None = Field(
        default=None,
        alias="impliedSharePrice",
        description="Implied share price from DCF",
    )


class CustomLeveredDCF(BaseModel):
    """Custom levered discounted cash flow valuation with detailed components"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    year: str | int | None = Field(default=None, description="Projection year")
    date: datetime | None = Field(default=None, description="Valuation date")
    fcfe0: float | None = Field(
        default=None, description="Current year free cash flow to equity"
    )
    fcfe1: float | None = Field(
        default=None, description="Year 1 projected free cash flow to equity"
    )
    fcfe2: float | None = Field(
        default=None, description="Year 2 projected free cash flow to equity"
    )
    fcfe3: float | None = Field(
        default=None, description="Year 3 projected free cash flow to equity"
    )
    fcfe4: float | None = Field(
        default=None, description="Year 4 projected free cash flow to equity"
    )
    fcfe5: float | None = Field(
        default=None, description="Year 5 projected free cash flow to equity"
    )
    fcfe6: float | None = Field(
        default=None, description="Year 6 projected free cash flow to equity"
    )
    fcfe7: float | None = Field(
        default=None, description="Year 7 projected free cash flow to equity"
    )
    fcfe8: float | None = Field(
        default=None, description="Year 8 projected free cash flow to equity"
    )
    fcfe9: float | None = Field(
        default=None, description="Year 9 projected free cash flow to equity"
    )
    fcfe10: float | None = Field(
        default=None, description="Year 10 projected free cash flow to equity"
    )
    terminal_value: float | None = Field(
        default=None, alias="terminalValue", description="Terminal value"
    )
    growth_rate: float | None = Field(
        default=None, alias="growthRate", description="Growth rate used"
    )
    terminal_growth_rate: float | None = Field(
        default=None, alias="terminalGrowthRate", description="Terminal growth rate"
    )
    cost_of_equity: float | None = Field(
        default=None, alias="costOfEquity", description="Cost of equity"
    )
    present_value_of_fcfe: float | None = Field(
        default=None,
        alias="presentValueOfFCFE",
        description="Present value of free cash flows to equity",
    )
    present_value_of_terminal_value: float | None = Field(
        default=None,
        alias="presentValueOfTerminalValue",
        description="Present value of terminal value",
    )
    equity_value: float | None = Field(
        default=None, alias="equityValue", description="Equity value"
    )
    shares_outstanding: float | None = Field(
        default=None, alias="sharesOutstanding", description="Shares outstanding"
    )
    dcf: float | None = Field(default=None, description="DCF value per share")
    stock_price: float | None = Field(
        default=None, alias="stockPrice", description="Current stock price"
    )
    implied_share_price: float | None = Field(
        default=None,
        alias="impliedSharePrice",
        description="Implied share price from DCF",
    )


class CompanyRating(BaseModel):
    """Company rating data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Rating date")
    rating: str = Field(description="Overall rating")
    recommendation: str | None = Field(None, description="Investment recommendation")
    # Add more fields as needed


class EnterpriseValue(BaseModel):
    """Enterprise value metrics"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Valuation date")

    # Stock and share data
    stock_price: float | None = Field(
        default=None, alias="stockPrice", description="Stock price"
    )
    number_of_shares: float | None = Field(
        default=None, alias="numberOfShares", description="Number of shares outstanding"
    )

    # Enterprise value components
    market_cap: float | None = Field(
        default=None, alias="marketCapitalization", description="Market capitalization"
    )
    minus_cash_and_cash_equivalents: float | None = Field(
        default=None,
        alias="minusCashAndCashEquivalents",
        description="Cash and cash equivalents (subtracted from EV)",
    )
    add_total_debt: float | None = Field(
        default=None, alias="addTotalDebt", description="Total debt (added to EV)"
    )
    enterprise_value: float | None = Field(
        default=None, alias="enterpriseValue", description="Enterprise value"
    )


class FinancialStatementFull(BaseModel):
    """Full financial statements as reported"""

    model_config = default_model_config

    date: datetime | None = Field(default=None, description="Statement date")
    symbol: str | None = Field(default=None, description="Company symbol")
    period: str | None = Field(default=None, description="Reporting period")

    document_type: str | None = Field(
        default=None, alias="documenttype", description="SEC filing type"
    )
    filing_date: datetime | None = Field(
        default=None, alias="filingdate", description="SEC filing date"
    )

    # Income Statement Items
    revenue: float | None = Field(
        default=None,
        alias="revenuefromcontractwithcustomerexcludingassessedtax",
        description="Total revenue",
    )
    cost_of_revenue: float | None = Field(
        default=None,
        alias="costofgoodsandservicessold",
        description="Cost of goods sold",
    )
    gross_profit: float | None = Field(
        default=None, alias="grossprofit", description="Gross profit"
    )
    operating_expenses: float | None = Field(
        default=None, alias="operatingexpenses", description="Operating expenses"
    )
    research_development: float | None = Field(
        default=None, alias="researchanddevelopmentexpense", description="R&D expenses"
    )
    selling_general_administrative: float | None = Field(
        default=None,
        alias="sellinggeneralandadministrativeexpense",
        description="SG&A expenses",
    )
    operating_income: float | None = Field(
        default=None, alias="operatingincomeloss", description="Operating income/loss"
    )
    net_income: float | None = Field(
        default=None, alias="netincomeloss", description="Net income/loss"
    )
    eps_basic: float | None = Field(
        default=None, alias="earningspersharebasic", description="Basic EPS"
    )
    eps_diluted: float | None = Field(
        default=None, alias="earningspersharediluted", description="Diluted EPS"
    )

    # Balance Sheet Items - Assets
    cash_and_equivalents: float | None = Field(
        default=None,
        alias="cashandcashequivalentsatcarryingvalue",
        description="Cash and cash equivalents",
    )
    marketable_securities_current: float | None = Field(
        default=None,
        alias="marketablesecuritiescurrent",
        description="Current marketable securities",
    )
    accounts_receivable_net_current: float | None = Field(
        default=None,
        alias="accountsreceivablenetcurrent",
        description="Net accounts receivable",
    )
    inventory_net: float | None = Field(
        default=None, alias="inventorynet", description="Net inventory"
    )
    assets_current: float | None = Field(
        default=None, alias="assetscurrent", description="Total current assets"
    )
    property_plant_equipment_net: float | None = Field(
        default=None, alias="propertyplantandequipmentnet", description="Net PP&E"
    )
    assets_noncurrent: float | None = Field(
        default=None, alias="assetsnoncurrent", description="Total non-current assets"
    )
    total_assets: float | None = Field(
        default=None, alias="assets", description="Total assets"
    )

    # Balance Sheet Items - Liabilities
    accounts_payable_current: float | None = Field(
        default=None,
        alias="accountspayablecurrent",
        description="Current accounts payable",
    )
    liabilities_current: float | None = Field(
        default=None,
        alias="liabilitiescurrent",
        description="Total current liabilities",
    )
    long_term_debt_noncurrent: float | None = Field(
        default=None, alias="longtermdebtnoncurrent", description="Long-term debt"
    )
    liabilities_noncurrent: float | None = Field(
        default=None,
        alias="liabilitiesnoncurrent",
        description="Total non-current liabilities",
    )
    total_liabilities: float | None = Field(
        default=None, alias="liabilities", description="Total liabilities"
    )

    # Balance Sheet Items - Equity
    common_stock_shares_outstanding: float | None = Field(
        default=None,
        alias="commonstocksharesoutstanding",
        description="Common stock shares outstanding",
    )
    common_stock_value: float | None = Field(
        default=None,
        alias="commonstocksincludingadditionalpaidincapital",
        description="Common stock and additional paid-in capital",
    )
    retained_earnings: float | None = Field(
        default=None,
        alias="retainedearningsaccumulateddeficit",
        description="Retained earnings/accumulated deficit",
    )
    accumulated_other_comprehensive_income: float | None = Field(
        default=None,
        alias="accumulatedothercomprehensiveincomelossnetoftax",
        description="Accumulated other comprehensive income",
    )
    stockholders_equity: float | None = Field(
        default=None,
        alias="stockholdersequity",
        description="Total stockholders' equity",
    )

    # Cash Flow Items
    operating_cash_flow: float | None = Field(
        default=None,
        alias="netcashprovidedbyusedinoperatingactivities",
        description="Net cash from operating activities",
    )
    investing_cash_flow: float | None = Field(
        default=None,
        alias="netcashprovidedbyusedininvestingactivities",
        description="Net cash from investing activities",
    )
    financing_cash_flow: float | None = Field(
        default=None,
        alias="netcashprovidedbyusedinfinancingactivities",
        description="Net cash from financing activities",
    )
    depreciation_amortization: float | None = Field(
        default=None,
        alias="depreciationdepletionandamortization",
        description="Depreciation and amortization",
    )

    # Additional Metrics
    market_cap: float | None = Field(
        default=None, alias="marketcap", description="Market capitalization"
    )
    employees: int | None = Field(
        default=None,
        alias="fullTimeEmployees",
        description="Number of full-time employees",
    )


class FinancialReport(BaseModel):
    """Financial report summary"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Report year")
    period: str = Field(description="Report period")
    url: str = Field(description="Report URL")
    filing_date: datetime = Field(alias="filingDate", description="Filing date")


class OwnerEarnings(BaseModel):
    """Owner earnings data"""

    model_config = default_model_config

    # Metadata
    date: datetime = Field(description="Date")
    symbol: str = Field(description="Company symbol")
    reported_currency: str | None = Field(
        default=None, alias="reportedCurrency", description="Currency used"
    )
    fiscal_year: str | None = Field(
        default=None, alias="fiscalYear", description="Fiscal year"
    )
    period: str | None = Field(
        default=None, description="Reporting period (Q1, Q2, Q3, Q4, FY)"
    )

    # Owner earnings calculations
    average_ppe: float | None = Field(
        default=None, alias="averagePPE", description="Average PP&E ratio"
    )
    maintenance_capex: float | None = Field(
        default=None,
        alias="maintenanceCapex",
        description="Maintenance capital expenditure",
    )
    growth_capex: float | None = Field(
        default=None,
        alias="growthCapex",
        description="Growth capital expenditure",
    )
    reported_owner_earnings: float | None = Field(
        default=None,
        validation_alias=AliasChoices("reportedOwnerEarnings", "ownersEarnings"),
        description="Reported owner earnings",
    )
    owner_earnings_per_share: float | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "ownerEarningsPerShare",
            "ownersEarningsPerShare",
        ),
        description="Owner earnings per share",
    )


class HistoricalRating(BaseModel):
    """Historical company rating data"""

    model_config = default_model_config

    date: datetime = Field(description="Rating date")
    rating: str = Field(description="Overall rating grade")
    rating_score: int = Field(alias="ratingScore", description="Numerical rating score")
    rating_recommendation: str = Field(
        alias="ratingRecommendation", description="Investment recommendation"
    )
    rating_details: dict = Field(
        alias="ratingDetails", description="Detailed rating breakdown"
    )


class LeveredDCF(BaseModel):
    """Levered discounted cash flow valuation"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Valuation date")
    levered_dcf: float | None = Field(
        default=None,
        validation_alias=AliasChoices("leveredDCF", "dcf"),
        description="Levered DCF value",
    )
    stock_price: float | None = Field(
        default=None,
        validation_alias=AliasChoices("stockPrice", "Stock Price"),
        description="Current stock price",
    )
    growth_rate: float | None = Field(
        default=None, alias="growthRate", description="Growth rate used"
    )
    cost_of_equity: float | None = Field(
        default=None, alias="costOfEquity", description="Cost of equity used"
    )


class AsReportedFinancialStatementBase(BaseModel):
    """Base model for as-reported financial statements"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Statement date")
    symbol: str | None = Field(None, description="Company symbol")
    period: str | None = Field(None, description="Reporting period (annual/quarter)")
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="SEC filing date"
    )
    form_type: str | None = Field(None, alias="formType", description="SEC form type")
    source_filing_url: str | None = Field(
        None, alias="sourceFilingURL", description="Source SEC filing URL"
    )
    start_date: datetime | None = Field(
        None, alias="startDate", description="Period start date"
    )
    end_date: datetime | None = Field(
        None, alias="endDate", description="Period end date"
    )
    fiscal_year: int | None = Field(None, alias="fiscalYear", description="Fiscal year")
    fiscal_period: str | None = Field(
        None, alias="fiscalPeriod", description="Fiscal period"
    )
    units: str | None = Field(None, description="Currency units")
    reported_currency: str | None = Field(
        None, alias="reportedCurrency", description="Reported currency code"
    )
    audited: bool | None = Field(None, description="Whether statement is audited")
    original_filing_url: str | None = Field(
        None, alias="originalFilingUrl", description="Original SEC filing URL"
    )
    filing_date_time: datetime | None = Field(
        None, alias="filingDateTime", description="Exact filing date and time"
    )

    @model_validator(mode="before")
    @classmethod
    def merge_data_payload(cls, values: dict[str, Any]) -> dict[str, Any]:
        if isinstance(values, dict) and "data" in values:
            data = values.get("data") or {}
            if isinstance(data, dict):
                merged = dict(values)
                merged.pop("data", None)
                merged.update(data)
                return merged
        return values


class AsReportedIncomeStatement(AsReportedFinancialStatementBase):
    """As-reported income statement data directly from SEC filings"""

    model_config = default_model_config

    revenues: float | None = Field(default=None, description="Total revenues")
    cost_of_revenue: float | None = Field(
        alias="costOfRevenue", default=None, description="Cost of revenue"
    )
    gross_profit: float | None = Field(
        alias="grossProfit", default=None, description="Gross profit"
    )
    operating_expenses: float | None = Field(
        alias="operatingExpenses", default=None, description="Operating expenses"
    )
    selling_general_administrative: float | None = Field(
        alias="sellingGeneralAndAdministrative",
        default=None,
        description="Selling, general and administrative expenses",
    )
    research_development: float | None = Field(
        alias="researchAndDevelopment",
        default=None,
        description="Research and development expenses",
    )
    operating_income: float | None = Field(
        alias="operatingIncome", default=None, description="Operating income"
    )
    interest_expense: float | None = Field(
        alias="interestExpense", default=None, description="Interest expense"
    )
    interest_income: float | None = Field(
        alias="interestIncome", default=None, description="Interest income"
    )
    other_income_expense: float | None = Field(
        alias="otherIncomeExpense", default=None, description="Other income or expenses"
    )
    income_before_tax: float | None = Field(
        alias="incomeBeforeTax", default=None, description="Income before income taxes"
    )
    income_tax_expense: float | None = Field(
        alias="incomeTaxExpense", default=None, description="Income tax expense"
    )
    net_income: float | None = Field(
        alias="netIncome", default=None, description="Net income"
    )
    net_income_to_common: float | None = Field(
        alias="netIncomeToCommon",
        default=None,
        description="Net income available to common shareholders",
    )
    preferred_dividends: float | None = Field(
        alias="preferredDividends",
        default=None,
        description="Preferred stock dividends",
    )
    earnings_per_share_basic: float | None = Field(
        alias="earningsPerShareBasic",
        default=None,
        description="Basic earnings per share",
    )
    earnings_per_share_diluted: float | None = Field(
        alias="earningsPerShareDiluted",
        default=None,
        description="Diluted earnings per share",
    )
    weighted_average_shares_outstanding: float | None = Field(
        alias="weightedAverageShares",
        default=None,
        description="Weighted average shares outstanding",
    )
    weighted_average_shares_outstanding_diluted: float | None = Field(
        alias="weightedAverageSharesDiluted",
        default=None,
        description="Diluted weighted average shares outstanding",
    )


class AsReportedBalanceSheet(AsReportedFinancialStatementBase):
    """As-reported balance sheet data directly from SEC filings"""

    model_config = default_model_config

    # Assets
    cash_and_equivalents: float | None = Field(
        alias="cashAndEquivalents",
        default=None,
        description="Cash and cash equivalents",
    )
    short_term_investments: float | None = Field(
        alias="shortTermInvestments", default=None, description="Short-term investments"
    )
    accounts_receivable: float | None = Field(
        alias="accountsReceivable", default=None, description="Accounts receivable"
    )
    inventory: float | None = Field(default=None, description="Inventory")
    other_current_assets: float | None = Field(
        alias="otherCurrentAssets", default=None, description="Other current assets"
    )
    total_current_assets: float | None = Field(
        alias="totalCurrentAssets", default=None, description="Total current assets"
    )
    property_plant_equipment: float | None = Field(
        alias="propertyPlantAndEquipment",
        default=None,
        description="Property, plant and equipment",
    )
    long_term_investments: float | None = Field(
        alias="longTermInvestments", default=None, description="Long-term investments"
    )
    goodwill: float | None = Field(default=None, description="Goodwill")
    intangible_assets: float | None = Field(
        alias="intangibleAssets", default=None, description="Intangible assets"
    )
    other_assets: float | None = Field(
        alias="otherAssets", default=None, description="Other assets"
    )
    total_assets: float | None = Field(
        alias="totalAssets", default=None, description="Total assets"
    )

    # Liabilities
    accounts_payable: float | None = Field(
        alias="accountsPayable", default=None, description="Accounts payable"
    )
    accrued_expenses: float | None = Field(
        alias="accruedExpenses", default=None, description="Accrued expenses"
    )
    short_term_debt: float | None = Field(
        alias="shortTermDebt", default=None, description="Short-term debt"
    )
    current_portion_long_term_debt: float | None = Field(
        alias="currentPortionLongTermDebt",
        default=None,
        description="Current portion of long-term debt",
    )
    other_current_liabilities: float | None = Field(
        alias="otherCurrentLiabilities",
        default=None,
        description="Other current liabilities",
    )
    total_current_liabilities: float | None = Field(
        alias="totalCurrentLiabilities",
        default=None,
        description="Total current liabilities",
    )
    long_term_debt: float | None = Field(
        alias="longTermDebt", default=None, description="Long-term debt"
    )
    deferred_taxes: float | None = Field(
        alias="deferredTaxes", default=None, description="Deferred taxes"
    )
    other_liabilities: float | None = Field(
        alias="otherLiabilities", default=None, description="Other liabilities"
    )
    total_liabilities: float | None = Field(
        alias="totalLiabilities", default=None, description="Total liabilities"
    )

    # Shareholders' Equity
    common_stock: float | None = Field(
        alias="commonStock", default=None, description="Common stock"
    )
    additional_paid_in_capital: float | None = Field(
        alias="additionalPaidInCapital",
        default=None,
        description="Additional paid-in capital",
    )
    retained_earnings: float | None = Field(
        alias="retainedEarnings", default=None, description="Retained earnings"
    )
    treasury_stock: float | None = Field(
        alias="treasuryStock", default=None, description="Treasury stock"
    )
    accumulated_other_comprehensive_income: float | None = Field(
        alias="accumulatedOtherComprehensiveIncome",
        default=None,
        description="Accumulated other comprehensive income",
    )
    total_shareholders_equity: float | None = Field(
        alias="totalShareholdersEquity",
        default=None,
        description="Total shareholders' equity",
    )


class AsReportedCashFlowStatement(AsReportedFinancialStatementBase):
    """As-reported cash flow statement data directly from SEC filings"""

    model_config = default_model_config

    # Operating Activities
    net_income: float | None = Field(
        alias="netIncome", default=None, description="Net income"
    )
    depreciation_amortization: float | None = Field(
        alias="depreciationAmortization",
        default=None,
        description="Depreciation and amortization",
    )
    stock_based_compensation: float | None = Field(
        alias="stockBasedCompensation",
        default=None,
        description="Stock-based compensation",
    )
    deferred_taxes: float | None = Field(
        alias="deferredTaxes", default=None, description="Deferred taxes"
    )
    changes_in_working_capital: float | None = Field(
        alias="changesInWorkingCapital",
        default=None,
        description="Changes in working capital",
    )
    accounts_receivable_changes: float | None = Field(
        alias="accountsReceivableChanges",
        default=None,
        description="Changes in accounts receivable",
    )
    inventory_changes: float | None = Field(
        alias="inventoryChanges", default=None, description="Changes in inventory"
    )
    accounts_payable_changes: float | None = Field(
        alias="accountsPayableChanges",
        default=None,
        description="Changes in accounts payable",
    )
    other_operating_activities: float | None = Field(
        alias="otherOperatingActivities",
        default=None,
        description="Other operating activities",
    )
    net_cash_from_operating_activities: float | None = Field(
        alias="netCashFromOperatingActivities",
        default=None,
        description="Net cash from operating activities",
    )

    # Investing Activities
    capital_expenditures: float | None = Field(
        alias="capitalExpenditures", default=None, description="Capital expenditures"
    )
    acquisitions: float | None = Field(default=None, description="Acquisitions")
    purchases_of_investments: float | None = Field(
        alias="purchasesOfInvestments",
        default=None,
        description="Purchases of investments",
    )
    sales_of_investments: float | None = Field(
        alias="salesOfInvestments",
        default=None,
        description="Sales/maturities of investments",
    )
    other_investing_activities: float | None = Field(
        alias="otherInvestingActivities",
        default=None,
        description="Other investing activities",
    )
    net_cash_used_in_investing_activities: float | None = Field(
        alias="netCashUsedInInvestingActivities",
        default=None,
        description="Net cash used in investing activities",
    )

    # Financing Activities
    debt_repayment: float | None = Field(
        alias="debtRepayment", default=None, description="Repayment of debt"
    )
    common_stock_issued: float | None = Field(
        alias="commonStockIssued", default=None, description="Common stock issued"
    )
    common_stock_repurchased: float | None = Field(
        alias="commonStockRepurchased",
        default=None,
        description="Common stock repurchased",
    )
    dividends_paid: float | None = Field(
        alias="dividendsPaid", default=None, description="Dividends paid"
    )
    other_financing_activities: float | None = Field(
        alias="otherFinancingActivities",
        default=None,
        description="Other financing activities",
    )
    net_cash_used_in_financing_activities: float | None = Field(
        alias="netCashUsedInFinancingActivities",
        default=None,
        description="Net cash used in financing activities",
    )

    # Net Changes
    effect_of_exchange_rates: float | None = Field(
        alias="effectOfExchangeRates",
        default=None,
        description="Effect of exchange rates on cash",
    )
    net_change_in_cash: float | None = Field(
        alias="netChangeInCash", default=None, description="Net change in cash"
    )
    cash_at_beginning_of_period: float | None = Field(
        alias="cashAtBeginningOfPeriod",
        default=None,
        description="Cash at beginning of period",
    )
    cash_at_end_of_period: float | None = Field(
        alias="cashAtEndOfPeriod", default=None, description="Cash at end of period"
    )


class FinancialReportDate(BaseModel):
    """Financial report date"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    fiscal_year: int | None = Field(None, alias="fiscalYear", description="Fiscal year")
    report_date: str | None = Field(None, description="Report date", alias="date")
    period: str = Field(description="Reporting period")
    link_xlsx: str = Field(alias="linkXlsx", description="XLSX report link")
    link_json: str = Field(alias="linkJson", description="JSON report link")


class FinancialReportDates(BaseModel):
    """Financial report date"""

    model_config = default_model_config

    financial_reports_dates: list[FinancialReportDate]


class LatestFinancialStatement(BaseModel):
    """Latest financial statement metadata"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    calendar_year: int | None = Field(
        None, alias="calendarYear", description="Calendar year"
    )
    period: str = Field(description="Reporting period")
    date: datetime = Field(description="Statement date")
    date_added: datetime = Field(alias="dateAdded", description="Date added")
