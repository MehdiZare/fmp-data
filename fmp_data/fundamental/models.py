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

    # Cash and Investments
    cash_and_short_term_investments: float = Field(
        alias="cashAndShortTermInvestments",
        description="Cash and short-term investments",
    )
    net_receivables: float = Field(
        alias="netReceivables", description="Net receivables"
    )
    inventory: float = Field(description="Inventory")
    total_current_assets: float = Field(
        alias="totalCurrentAssets", description="Total current assets"
    )
    property_plant_equipment_net: float = Field(
        alias="propertyPlantEquipmentNet", description="Net PP&E"
    )
    total_non_current_assets: float = Field(
        alias="totalNonCurrentAssets", description="Total non-current assets"
    )
    total_assets: float = Field(alias="totalAssets", description="Total assets")

    # Liabilities
    account_payables: float = Field(
        alias="accountPayables", description="Accounts payable"
    )
    short_term_debt: float = Field(alias="shortTermDebt", description="Short-term debt")
    total_current_liabilities: float = Field(
        alias="totalCurrentLiabilities", description="Total current liabilities"
    )
    long_term_debt: float = Field(alias="longTermDebt", description="Long-term debt")
    total_non_current_liabilities: float = Field(
        alias="totalNonCurrentLiabilities", description="Total non-current liabilities"
    )
    total_liabilities: float = Field(
        alias="totalLiabilities", description="Total liabilities"
    )

    # Equity
    total_stockholders_equity: float = Field(
        alias="totalStockholdersEquity", description="Total stockholders' equity"
    )
    total_equity: float = Field(alias="totalEquity", description="Total equity")
    total_liabilities_and_equity: float = Field(
        alias="totalLiabilitiesAndTotalEquity",
        description="Total liabilities and equity",
    )

    # Additional metrics
    total_investments: float = Field(
        alias="totalInvestments", description="Total investments"
    )
    total_debt: float = Field(alias="totalDebt", description="Total debt")
    net_debt: float = Field(alias="netDebt", description="Net debt")


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
        return self.net_cash_provided_by_investing_activities

    @property
    def financing_cash_flow(self) -> float | None:
        return self.net_cash_provided_by_financing_activities


class KeyMetrics(BaseModel):
    """Key financial metrics"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Metrics date")
    revenue_per_share: float | None = Field(
        None, alias="revenuePerShare", description="Revenue per share"
    )
    net_income_per_share: float | None = Field(
        None, alias="netIncomePerShare", description="Net income per share"
    )
    operating_cash_flow_per_share: float | None = Field(
        None,
        alias="operatingCashFlowPerShare",
        description="Operating cash flow per share",
    )
    free_cash_flow_per_share: float | None = Field(
        None, alias="freeCashFlowPerShare", description="Free cash flow per share"
    )


class KeyMetricsTTM(KeyMetrics):
    """Trailing twelve months key metrics"""

    pass


class FinancialRatios(BaseModel):
    """Financial ratios"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Ratios date")
    current_ratio: float | None = Field(
        None, alias="currentRatio", description="Current ratio"
    )
    quick_ratio: float | None = Field(
        None, alias="quickRatio", description="Quick ratio"
    )
    debt_equity_ratio: float | None = Field(
        None, alias="debtEquityRatio", description="Debt to equity ratio"
    )
    return_on_equity: float | None = Field(
        None, alias="returnOnEquity", description="Return on equity"
    )
    # Add more fields as needed


class FinancialRatiosTTM(FinancialRatios):
    """Trailing twelve months financial ratios"""

    pass


class FinancialGrowth(BaseModel):
    """Financial growth metrics"""

    model_config = default_model_config

    date: datetime | None = Field(None, description="Growth metrics date")
    revenue_growth: float | None = Field(
        None, alias="revenueGrowth", description="Revenue growth"
    )
    gross_profit_growth: float | None = Field(
        None, alias="grossProfitGrowth", description="Gross profit growth"
    )
    eps_growth: float | None = Field(
        None,
        validation_alias=AliasChoices("epsGrowth", "epsgrowth"),
        description="EPS growth",
    )
    # Add more fields as needed


class FinancialScore(BaseModel):
    """Company financial score"""

    model_config = default_model_config

    altman_z_score: float | None = Field(
        None, alias="altmanZScore", description="Altman Z-Score"
    )
    piotroski_score: float | None = Field(
        None, alias="piotroskiScore", description="Piotroski Score"
    )
    # Add more fields as needed


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
    enterprise_value: float = Field(
        alias="enterpriseValue", description="Enterprise value"
    )
    market_cap: float = Field(
        alias="marketCapitalization", description="Market capitalization"
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

    date: datetime = Field(description="Date")
    symbol: str = Field(description="Company symbol")
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
    audited: bool | None = Field(None, description="Whether statement is audited")
    original_filing_url: str | None = Field(
        None, alias="originalFilingUrl", description="Original SEC filing URL"
    )
    filing_date_time: datetime | None = Field(
        None, alias="filingDateTime", description="Exact filing date and time"
    )

    @classmethod
    @model_validator(mode="before")
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
