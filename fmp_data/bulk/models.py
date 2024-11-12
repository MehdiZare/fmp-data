# fmp_data/bulk/models.py
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BulkQuote(BaseModel):
    """Bulk company quote data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changesPercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")
    day_low: float = Field(alias="dayLow", description="Day low price")
    day_high: float = Field(alias="dayHigh", description="Day high price")
    year_high: float = Field(alias="yearHigh", description="52-week high")
    year_low: float = Field(alias="yearLow", description="52-week low")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")
    volume: int = Field(description="Trading volume")
    avg_volume: int = Field(alias="avgVolume", description="Average volume")
    exchange: str = Field(description="Stock exchange")
    open: float = Field(description="Opening price")
    previous_close: float = Field(
        alias="previousClose", description="Previous close price"
    )
    timestamp: datetime = Field(description="Quote timestamp")


class BulkEODPrice(BaseModel):
    """Bulk end-of-day price data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Trading date")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    adj_close: float = Field(alias="adjClose", description="Adjusted closing price")
    volume: int = Field(description="Trading volume")


class BulkFinancialStatement(BaseModel):
    """Base model for bulk financial statements"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Statement date")
    period: str = Field(description="Reporting period")
    currency: str = Field(description="Currency")
    filing_date: date = Field(alias="filingDate", description="SEC filing date")


class BulkIncomeStatement(BulkFinancialStatement):
    """Bulk income statement data"""

    revenue: float = Field(description="Total revenue")
    gross_profit: float = Field(alias="grossProfit", description="Gross profit")
    operating_income: float = Field(
        alias="operatingIncome", description="Operating income"
    )
    net_income: float = Field(alias="netIncome", description="Net income")
    eps: float = Field(description="Earnings per share")
    eps_diluted: float = Field(
        alias="epsDiluted", description="Diluted earnings per share"
    )


class BulkBalanceSheet(BulkFinancialStatement):
    """Bulk balance sheet data"""

    total_assets: float = Field(alias="totalAssets", description="Total assets")
    total_liabilities: float = Field(
        alias="totalLiabilities", description="Total liabilities"
    )
    total_equity: float = Field(alias="totalEquity", description="Total equity")
    cash_and_equivalents: float = Field(
        alias="cashAndEquivalents", description="Cash and equivalents"
    )
    total_debt: float = Field(alias="totalDebt", description="Total debt")


class BulkCashFlowStatement(BulkFinancialStatement):
    """Bulk cash flow statement data"""

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


class BulkRatio(BaseModel):
    """Bulk financial ratio data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Date")
    period: str = Field(description="Reporting period")
    current_ratio: float = Field(alias="currentRatio", description="Current ratio")
    quick_ratio: float = Field(alias="quickRatio", description="Quick ratio")
    debt_ratio: float = Field(alias="debtRatio", description="Debt ratio")
    debt_equity_ratio: float = Field(
        alias="debtEquityRatio", description="Debt to equity ratio"
    )
    return_on_assets: float = Field(
        alias="returnOnAssets", description="Return on assets"
    )
    return_on_equity: float = Field(
        alias="returnOnEquity", description="Return on equity"
    )


class BulkKeyMetric(BaseModel):
    """Bulk key metric data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Date")
    period: str = Field(description="Reporting period")
    revenue_per_share: float = Field(
        alias="revenuePerShare", description="Revenue per share"
    )
    net_income_per_share: float = Field(
        alias="netIncomePerShare", description="Net income per share"
    )
    operating_cash_flow_per_share: float = Field(
        alias="operatingCashFlowPerShare", description="Operating cash flow per share"
    )
    book_value_per_share: float = Field(
        alias="bookValuePerShare", description="Book value per share"
    )
    market_cap: float = Field(alias="marketCap", description="Market capitalization")
    enterprise_value: float = Field(
        alias="enterpriseValue", description="Enterprise value"
    )


class BulkEarningSurprise(BaseModel):
    """Bulk earnings surprise data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Earnings date")
    actual_eps: float = Field(alias="actualEPS", description="Actual EPS")
    estimated_eps: float = Field(alias="estimatedEPS", description="Estimated EPS")
    surprise: float = Field(description="EPS surprise")
    surprise_percentage: float = Field(
        alias="surprisePercentage", description="Surprise percentage"
    )


class BulkCompanyProfile(BaseModel):
    """Bulk company profile data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    exchange: str = Field(description="Stock exchange")
    industry: str = Field(description="Industry")
    sector: str = Field(description="Sector")
    country: str = Field(description="Country")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")
    employees: int | None = Field(description="Number of employees")


class BulkStockPeer(BaseModel):
    """Bulk stock peer data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    peers: list[str] = Field(description="List of peer symbols")
    industry: str = Field(description="Industry")
    sector: str = Field(description="Sector")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")


class BulkFinancialGrowth(BaseModel):
    """Bulk financial growth data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    date: date = Field(description="Date")
    period: str = Field(description="Reporting period")
    revenue_growth: float = Field(
        alias="revenueGrowth", description="Revenue growth rate"
    )
    gross_profit_growth: float = Field(
        alias="grossProfitGrowth", description="Gross profit growth rate"
    )
    ebit_growth: float = Field(alias="ebitGrowth", description="EBIT growth rate")
    net_income_growth: float = Field(
        alias="netIncomeGrowth", description="Net income growth rate"
    )
    eps_growth: float = Field(alias="epsGrowth", description="EPS growth rate")
