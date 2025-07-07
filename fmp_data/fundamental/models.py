# fmp_data/fundamental/models.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
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
    filling_date: datetime = Field(alias="fillingDate", description="SEC filing date")
    accepted_date: datetime = Field(
        alias="acceptedDate", description="SEC acceptance date"
    )
    calendar_year: str = Field(alias="calendarYear", description="Calendar year")
    period: str = Field(description="Reporting period (Q1, Q2, Q3, Q4, FY)")
    link: str = Field(description="Filing URL")
    final_link: str = Field(alias="finalLink", description="Final filing URL")


class IncomeStatement(FinancialStatementBase):
    """Income statement data"""

    model_config = default_model_config

    revenue: float | None = Field(None, description="Total revenue")
    cost_of_revenue: float | None = Field(
        alias="costOfRevenue", description="Cost of revenue"
    )
    gross_profit: float | None = Field(alias="grossProfit", description="Gross profit")
    gross_profit_ratio: float | None = Field(
        alias="grossProfitRatio", description="Gross profit ratio"
    )

    # Operating expenses
    research_and_development_expenses: float | None = Field(
        alias="researchAndDevelopmentExpenses", description="R&D expenses"
    )
    selling_general_and_administrative_expenses: float | None = Field(
        alias="sellingGeneralAndAdministrativeExpenses", description="SG&A expenses"
    )
    operating_expenses: float | None = Field(
        alias="operatingExpenses", description="Operating expenses"
    )
    cost_and_expenses: float | None = Field(
        alias="costAndExpenses", description="Total costs and expenses"
    )

    # Profitability metrics
    operating_income: float = Field(
        alias="operatingIncome", description="Operating income"
    )
    operating_income_ratio: float = Field(
        alias="operatingIncomeRatio", description="Operating income ratio"
    )

    ebitda: float = Field(description="EBITDA")
    ebitda_ratio: float = Field(alias="ebitdaratio", description="EBITDA ratio")

    # Income metrics
    income_before_tax: float = Field(
        alias="incomeBeforeTax", description="Income before tax"
    )
    income_before_tax_ratio: float = Field(
        alias="incomeBeforeTaxRatio", description="Income before tax ratio"
    )
    income_tax_expense: float = Field(
        alias="incomeTaxExpense", description="Income tax expense"
    )
    net_income: float = Field(alias="netIncome", description="Net income")
    net_income_ratio: float = Field(
        alias="netIncomeRatio", description="Net income ratio"
    )

    # Share data
    eps: float = Field(description="Earnings per share")
    eps_diluted: float = Field(alias="epsdiluted", description="Diluted EPS")
    weighted_average_shares_out: float = Field(
        alias="weightedAverageShsOut", description="Weighted average shares"
    )
    weighted_average_shares_out_dil: float = Field(
        alias="weightedAverageShsOutDil", description="Diluted weighted average shares"
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
    """Cash flow statement data"""

    model_config = default_model_config

    # Operating activities
    net_income: float | None = Field(alias="netIncome", description="Net income")
    depreciation_and_amortization: float | None = Field(
        alias="depreciationAndAmortization", description="Depreciation and amortization"
    )

    stock_based_compensation: float = Field(
        alias="stockBasedCompensation", description="Stock-based compensation"
    )
    operating_cash_flow: float | None = Field(
        alias="operatingCashFlow", description="Operating cash flow"
    )
    net_cash_provided_by_operating_activities: float | None = Field(
        alias="netCashProvidedByOperatingActivities",
        description="Net cash from operating activities",
    )

    # Investing activities
    capital_expenditure: float | None = Field(
        None, alias="capitalExpenditure", description="Capital expenditure"
    )
    investing_cash_flow: float | None = Field(
        None,
        alias="netCashUsedForInvestingActivites",
        description="Net cash used in investing activities",
    )

    acquisitions_net: float = Field(
        alias="acquisitionsNet", description="Net acquisitions"
    )
    investments_in_property_plant_and_equipment: float = Field(
        alias="investmentsInPropertyPlantAndEquipment", description="PP&E investments"
    )

    # Financing activities
    debt_repayment: float = Field(alias="debtRepayment", description="Debt repayment")
    common_stock_repurchased: float = Field(
        alias="commonStockRepurchased", description="Stock repurchases"
    )
    dividends_paid: float = Field(alias="dividendsPaid", description="Dividends paid")
    financing_cash_flow: float | None = Field(
        alias="netCashUsedProvidedByFinancingActivities",
        description="Net cash used in financing activities",
    )

    net_change_in_cash: float | None = Field(
        alias="netChangeInCash", description="Net change in cash"
    )

    # Cash position
    free_cash_flow: float | None = Field(
        alias="freeCashFlow", description="Free cash flow"
    )
    cash_at_beginning_of_period: float | None = Field(
        alias="cashAtBeginningOfPeriod", description="Beginning cash balance"
    )
    cash_at_end_of_period: float | None = Field(
        alias="cashAtEndOfPeriod", description="Ending cash balance"
    )


class KeyMetrics(BaseModel):
    """Key financial metrics"""

    model_config = default_model_config

    date: datetime = Field(description="Metrics date")
    revenue_per_share: float = Field(
        alias="revenuePerShare", description="Revenue per share"
    )
    net_income_per_share: float = Field(
        alias="netIncomePerShare", description="Net income per share"
    )
    operating_cash_flow_per_share: float = Field(
        alias="operatingCashFlowPerShare", description="Operating cash flow per share"
    )
    free_cash_flow_per_share: float = Field(
        alias="freeCashFlowPerShare", description="Free cash flow per share"
    )


class KeyMetricsTTM(KeyMetrics):
    """Trailing twelve months key metrics"""

    pass


class FinancialRatios(BaseModel):
    """Financial ratios"""

    model_config = default_model_config

    date: datetime = Field(description="Ratios date")
    current_ratio: float = Field(alias="currentRatio", description="Current ratio")
    quick_ratio: float = Field(alias="quickRatio", description="Quick ratio")
    debt_equity_ratio: float = Field(
        alias="debtEquityRatio", description="Debt to equity ratio"
    )
    return_on_equity: float = Field(
        alias="returnOnEquity", description="Return on equity"
    )
    # Add more fields as needed


class FinancialRatiosTTM(FinancialRatios):
    """Trailing twelve months financial ratios"""

    pass


class FinancialGrowth(BaseModel):
    """Financial growth metrics"""

    model_config = default_model_config

    date: datetime = Field(description="Growth metrics date")
    revenue_growth: float = Field(alias="revenueGrowth", description="Revenue growth")
    gross_profit_growth: float = Field(
        alias="grossProfitGrowth", description="Gross profit growth"
    )
    eps_growth: float = Field(alias="epsGrowth", description="EPS growth")
    # Add more fields as needed


class FinancialScore(BaseModel):
    """Company financial score"""

    model_config = default_model_config

    altman_z_score: float = Field(alias="altmanZScore", description="Altman Z-Score")
    piotroski_score: float = Field(
        alias="piotroskiScore", description="Piotroski Score"
    )
    # Add more fields as needed


class DCF(BaseModel):
    """Discounted cash flow valuation"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Valuation date")
    dcf: float = Field(description="DCF value")
    stock_price: float = Field(alias="stockPrice", description="Current stock price")
    # Add more fields as needed


class AdvancedDCF(DCF):
    """Advanced discounted cash flow valuation"""

    # Add additional fields specific to advanced DCF


class CompanyRating(BaseModel):
    """Company rating data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Rating date")
    rating: str = Field(description="Overall rating")
    recommendation: str = Field(description="Investment recommendation")
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

    date: datetime | None = Field(None, description="Statement date")
    symbol: str | None = Field(None, description="Company symbol")
    period: str | None = Field(None, description="Reporting period")

    document_type: str | None = Field(
        None, alias="documenttype", description="SEC filing type"
    )
    filing_date: datetime | None = Field(
        None, alias="filingdate", description="SEC filing date"
    )

    # Income Statement Items
    revenue: float | None = Field(
        None,
        alias="revenuefromcontractwithcustomerexcludingassessedtax",
        description="Total revenue",
    )
    cost_of_revenue: float | None = Field(
        None, alias="costofgoodsandservicessold", description="Cost of goods sold"
    )
    gross_profit: float | None = Field(
        None, alias="grossprofit", description="Gross profit"
    )
    operating_expenses: float | None = Field(
        None, alias="operatingexpenses", description="Operating expenses"
    )
    research_development: float | None = Field(
        None, alias="researchanddevelopmentexpense", description="R&D expenses"
    )
    selling_general_administrative: float | None = Field(
        None,
        alias="sellinggeneralandadministrativeexpense",
        description="SG&A expenses",
    )
    operating_income: float | None = Field(
        None, alias="operatingincomeloss", description="Operating income/loss"
    )
    net_income: float | None = Field(
        None, alias="netincomeloss", description="Net income/loss"
    )
    eps_basic: float | None = Field(
        None, alias="earningspersharebasic", description="Basic EPS"
    )
    eps_diluted: float | None = Field(
        None, alias="earningspersharediluted", description="Diluted EPS"
    )

    # Balance Sheet Items - Assets
    cash_and_equivalents: float | None = Field(
        None,
        alias="cashandcashequivalentsatcarryingvalue",
        description="Cash and cash equivalents",
    )
    marketable_securities_current: float | None = Field(
        None,
        alias="marketablesecuritiescurrent",
        description="Current marketable securities",
    )
    accounts_receivable_net_current: float | None = Field(
        None,
        alias="accountsreceivablenetcurrent",
        description="Net accounts receivable",
    )
    inventory_net: float | None = Field(
        None, alias="inventorynet", description="Net inventory"
    )
    assets_current: float | None = Field(
        None, alias="assetscurrent", description="Total current assets"
    )
    property_plant_equipment_net: float | None = Field(
        None, alias="propertyplantandequipmentnet", description="Net PP&E"
    )
    assets_noncurrent: float | None = Field(
        None, alias="assetsnoncurrent", description="Total non-current assets"
    )
    total_assets: float | None = Field(None, alias="assets", description="Total assets")

    # Balance Sheet Items - Liabilities
    accounts_payable_current: float | None = Field(
        None, alias="accountspayablecurrent", description="Current accounts payable"
    )
    liabilities_current: float | None = Field(
        None, alias="liabilitiescurrent", description="Total current liabilities"
    )
    long_term_debt_noncurrent: float | None = Field(
        None, alias="longtermdebtnoncurrent", description="Long-term debt"
    )
    liabilities_noncurrent: float | None = Field(
        None, alias="liabilitiesnoncurrent", description="Total non-current liabilities"
    )
    total_liabilities: float | None = Field(
        None, alias="liabilities", description="Total liabilities"
    )

    # Balance Sheet Items - Equity
    common_stock_shares_outstanding: float | None = Field(
        None,
        alias="commonstocksharesoutstanding",
        description="Common stock shares outstanding",
    )
    common_stock_value: float | None = Field(
        None,
        alias="commonstocksincludingadditionalpaidincapital",
        description="Common stock and additional paid-in capital",
    )
    retained_earnings: float | None = Field(
        None,
        alias="retainedearningsaccumulateddeficit",
        description="Retained earnings/accumulated deficit",
    )
    accumulated_other_comprehensive_income: float | None = Field(
        None,
        alias="accumulatedothercomprehensiveincomelossnetoftax",
        description="Accumulated other comprehensive income",
    )
    stockholders_equity: float | None = Field(
        None, alias="stockholdersequity", description="Total stockholders' equity"
    )

    # Cash Flow Items
    operating_cash_flow: float | None = Field(
        None,
        alias="netcashprovidedbyusedinoperatingactivities",
        description="Net cash from operating activities",
    )
    investing_cash_flow: float | None = Field(
        None,
        alias="netcashprovidedbyusedininvestingactivities",
        description="Net cash from investing activities",
    )
    financing_cash_flow: float | None = Field(
        None,
        alias="netcashprovidedbyusedinfinancingactivities",
        description="Net cash from financing activities",
    )
    depreciation_amortization: float | None = Field(
        None,
        alias="depreciationdepletionandamortization",
        description="Depreciation and amortization",
    )

    # Additional Metrics
    market_cap: float | None = Field(
        None, alias="marketcap", description="Market capitalization"
    )
    employees: int | None = Field(
        None, alias="fullTimeEmployees", description="Number of full-time employees"
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
    reported_owner_earnings: float = Field(
        alias="reportedOwnerEarnings", description="Reported owner earnings"
    )
    owner_earnings_per_share: float = Field(
        alias="ownerEarningsPerShare", description="Owner earnings per share"
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
    levered_dcf: float = Field(alias="leveredDCF", description="Levered DCF value")
    stock_price: float = Field(alias="stockPrice", description="Current stock price")
    growth_rate: float = Field(alias="growthRate", description="Growth rate used")
    cost_of_equity: float = Field(
        alias="costOfEquity", description="Cost of equity used"
    )


class AsReportedFinancialStatementBase(BaseModel):
    """Base model for as-reported financial statements"""

    model_config = default_model_config

    date: datetime = Field(description="Statement date")
    symbol: str = Field(description="Company symbol")
    period: str = Field(description="Reporting period (annual/quarter)")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    form_type: str = Field(alias="formType", description="SEC form type")
    source_filing_url: str = Field(
        alias="sourceFilingURL", description="Source SEC filing URL"
    )
    start_date: datetime = Field(alias="startDate", description="Period start date")
    end_date: datetime = Field(alias="endDate", description="Period end date")
    fiscal_year: int = Field(alias="fiscalYear", description="Fiscal year")
    fiscal_period: str = Field(alias="fiscalPeriod", description="Fiscal period")
    units: str = Field(description="Currency units")
    audited: bool = Field(description="Whether statement is audited")
    original_filing_url: str = Field(
        alias="originalFilingUrl", description="Original SEC filing URL"
    )
    filing_date_time: datetime = Field(
        alias="filingDateTime", description="Exact filing date and time"
    )


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
    report_date: str = Field(description="Report date", alias="date")
    period: str = Field(description="Reporting period")
    link_xlsx: str = Field(alias="linkXlsx", description="XLSX report link")
    link_json: str = Field(alias="linkJson", description="JSON report link")


class FinancialReportDates(BaseModel):
    """Financial report date"""

    model_config = default_model_config

    financial_reports_dates: list[FinancialReportDate]
