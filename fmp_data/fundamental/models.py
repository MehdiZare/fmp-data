# fmp_data/fundamental/models.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FinancialStatementBase(BaseModel):
    """Base model for financial statements"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Statement date")
    symbol: str = Field(description="Company symbol")
    reported_currency: str = Field(
        alias="reportedCurrency", description="Currency used"
    )
    period: str = Field(description="Reporting period (annual/quarter)")
    filling_date: datetime = Field(alias="fillingDate", description="SEC filing date")
    accepted_date: datetime = Field(
        alias="acceptedDate", description="SEC acceptance date"
    )
    calendar_year: int = Field(alias="calendarYear", description="Calendar year")
    period_length: str = Field(alias="periodLength", description="Period length")


class IncomeStatement(FinancialStatementBase):
    """Income statement data"""

    revenue: float = Field(description="Total revenue")
    cost_of_revenue: float = Field(alias="costOfRevenue", description="Cost of revenue")
    gross_profit: float = Field(alias="grossProfit", description="Gross profit")
    operating_expenses: float = Field(
        alias="operatingExpenses", description="Operating expenses"
    )
    operating_income: float = Field(
        alias="operatingIncome", description="Operating income"
    )
    net_income: float = Field(alias="netIncome", description="Net income")
    eps: float = Field(description="Earnings per share")
    ebitda: float = Field(description="EBITDA")
    # Add more fields as needed


class BalanceSheet(FinancialStatementBase):
    """Balance sheet data"""

    total_assets: float = Field(alias="totalAssets", description="Total assets")
    total_liabilities: float = Field(
        alias="totalLiabilities", description="Total liabilities"
    )
    total_equity: float = Field(alias="totalEquity", description="Total equity")
    cash_and_equivalents: float = Field(
        alias="cashAndEquivalents", description="Cash and equivalents"
    )
    short_term_debt: float = Field(alias="shortTermDebt", description="Short term debt")
    long_term_debt: float = Field(alias="longTermDebt", description="Long term debt")
    # Add more fields as needed


class CashFlowStatement(FinancialStatementBase):
    """Cash flow statement data"""

    operating_cash_flow: float = Field(
        alias="operatingCashFlow", description="Operating cash flow"
    )
    investing_cash_flow: float = Field(
        alias="investingCashFlow", description="Investing cash flow"
    )
    financing_cash_flow: float = Field(
        alias="financingCashFlow", description="Financing cash flow"
    )
    net_cash_flow: float = Field(alias="netCashFlow", description="Net cash flow")
    # Add more fields as needed


class KeyMetrics(BaseModel):
    """Key financial metrics"""

    model_config = ConfigDict(populate_by_name=True)

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
    # Add more fields as needed


class KeyMetricsTTM(KeyMetrics):
    """Trailing twelve months key metrics"""

    pass


class FinancialRatios(BaseModel):
    """Financial ratios"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Growth metrics date")
    revenue_growth: float = Field(alias="revenueGrowth", description="Revenue growth")
    gross_profit_growth: float = Field(
        alias="grossProfitGrowth", description="Gross profit growth"
    )
    eps_growth: float = Field(alias="epsGrowth", description="EPS growth")
    # Add more fields as needed


class FinancialScore(BaseModel):
    """Company financial score"""

    model_config = ConfigDict(populate_by_name=True)

    altman_z_score: float = Field(alias="altmanZScore", description="Altman Z-Score")
    piotroski_score: float = Field(
        alias="piotroskiScore", description="Piotroski Score"
    )
    # Add more fields as needed


class DCF(BaseModel):
    """Discounted cash flow valuation"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Rating date")
    rating: str = Field(description="Overall rating")
    recommendation: str = Field(description="Investment recommendation")
    # Add more fields as needed


class EnterpriseValue(BaseModel):
    """Enterprise value metrics"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Valuation date")
    enterprise_value: float = Field(
        alias="enterpriseValue", description="Enterprise value"
    )
    market_cap: float = Field(
        alias="marketCapitalization", description="Market capitalization"
    )


class FinancialStatementFull(BaseModel):
    """Full financial statement data including all statements"""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Statement date")
    symbol: str = Field(description="Company symbol")
    income_statement: dict = Field(
        alias="incomeStatement", description="Income statement data"
    )
    balance_sheet: dict = Field(alias="balanceSheet", description="Balance sheet data")
    cash_flow_statement: dict = Field(
        alias="cashFlowStatement", description="Cash flow statement data"
    )


class FinancialReport(BaseModel):
    """Financial report data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Report year")
    period: str = Field(description="Report period")
    url: str = Field(description="Report URL")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")


class OwnerEarnings(BaseModel):
    """Owner earnings data"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    report_date: datetime = Field(alias="date", description="Report date")
