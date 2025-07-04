from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import json
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, HttpUrl
from pydantic.alias_generators import to_camel

from fmp_data.models import ShareFloat

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class CompanyProfile(BaseModel):
    """Company profile information."""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    price: float = Field(description="Current stock price")
    beta: float = Field(description="Beta value")
    vol_avg: int | None = Field(None, description="Average volume")
    mkt_cap: float | None = Field(None, description="Market capitalization")
    last_div: float | None = Field(None, description="Last dividend payment")
    range: str | None = Field(None, description="52-week price range")
    changes: float | None = Field(None, description="Price change")
    company_name: str | None = Field(None, description="Company name")
    currency: str | None = Field(None, description="Trading currency")
    cik: str = Field(description="CIK number")
    isin: str = Field(description="ISIN number")
    cusip: str = Field(description="CUSIP number")
    exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(None, description="Exchange short name")
    industry: str | None = Field(None, description="Industry classification")
    website: AnyHttpUrl | None = Field(None, description="Company website")
    description: str = Field(description="Company description")
    ceo: str = Field(description="CEO name")
    sector: str = Field(description="Sector classification")
    country: str = Field(description="Country of incorporation")
    full_time_employees: str | None = Field(
        None, description="Number of full-time employees"
    )
    phone: str = Field(description="Contact phone number")
    address: str = Field(description="Company address")
    city: str = Field(description="City")
    state: str = Field(description="State")
    zip: str = Field(description="ZIP/Postal code")
    dcf_diff: float | None = Field(None, description="DCF difference")
    dcf: float = Field(description="Discounted Cash Flow value")
    image: AnyHttpUrl = Field(description="Company logo URL")
    ipo_date: datetime | None = Field(None, description="IPO date")
    default_image: bool | None = Field(None, description="Whether using default image")
    is_etf: bool | None = Field(None, description="Whether the symbol is an ETF")
    is_actively_trading: bool | None = Field(
        None, description="Whether actively trading"
    )
    is_adr: bool | None = Field(None, description="Whether is ADR")
    is_fund: bool | None = Field(None, description="Whether is a fund")


class CompanyCoreInformation(BaseModel):
    """Core company information."""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    cik: str = Field(description="CIK number")
    exchange: str | None = Field(None, description="Exchange name")
    sic_code: str | None = Field(None, description="SIC code")
    sic_group: str | None = Field(None, description="SIC group")
    sic_description: str | None = Field(None, description="SIC description")
    state_location: str | None = Field(None, description="Company state location")
    state_of_incorporation: str | None = Field(
        None, description="State of incorporation"
    )
    fiscal_year_end: str | None = Field(None, description="Fiscal year end date")
    business_address: str | None = Field(None, description="Business address")
    mailing_address: str | None = Field(None, description="Mailing address")
    tax_identification_number: str | None = Field(None, description="Tax ID")
    registrant_name: str | None = Field(None, description="Registrant name")


class CompanyExecutive(BaseModel):
    """Company executive information"""

    title: str = Field(description="Executive title")
    name: str = Field(description="Executive name")
    pay: int | None = Field(None, description="Annual compensation")
    currency_pay: str | None = Field(
        None, alias="currencyPay", description="Compensation currency"
    )
    gender: str | None = Field(None, description="Gender")
    year_born: int | None = Field(None, alias="yearBorn", description="Birth year")
    title_since: datetime | None = Field(
        None, alias="titleSince", description="Position start date"
    )


class CompanyNote(BaseModel):
    """Company financial note."""

    model_config = default_model_config

    title: str = Field(description="Note title")
    cik: str = Field(description="CIK number")
    symbol: str = Field(description="Stock symbol")
    exchange: str = Field(description="Exchange name")


class EmployeeCount(BaseModel):
    """Company employee count history."""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    cik: str = Field(description="CIK number")
    acceptance_time: datetime = Field(description="Filing acceptance time")
    period_of_report: str = Field(description="Report period")
    company_name: str | None = Field(None, description="Company name")
    form_type: str = Field(description="SEC form type")
    filing_date: str = Field(description="Filing date")
    employee_count: int = Field(description="Number of employees")
    source: str | None = Field(None, description="SEC filing source URL")


class Quote(BaseModel):
    """Real-time stock quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changesPercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")
    day_low: float = Field(description="Day low price")
    day_high: float = Field(description="Day high price")
    year_high: float = Field(description="52-week high")
    year_low: float = Field(description="52-week low")
    market_cap: float | None = Field(None, description="Market capitalization")
    price_avg_50: float | None = Field(None, description="50-day average price")
    price_avg_200: float | None = Field(None, description="200-day average price")
    volume: int = Field(description="Trading volume")
    avg_volume: int | None = Field(None, description="Average volume")
    open: float = Field(description="Opening price")
    previous_close: float | None = Field(None, description="Previous close price")
    eps: float = Field(description="Earnings per share")
    pe: float = Field(description="Price to earnings ratio")
    timestamp: datetime = Field(description="Quote timestamp")


class SimpleQuote(BaseModel):
    """Simple stock quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")


class HistoricalPrice(BaseModel):
    """Historical price data point"""

    model_config = default_model_config

    date: datetime = Field(description="Date of the price data")
    open: float = Field(description="Opening price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Closing price")
    adj_close: float = Field(alias="adjClose", description="Adjusted closing price")
    volume: int = Field(description="Trading volume")
    unadjusted_volume: int = Field(description="Unadjusted volume")
    change: float = Field(description="Price change")
    change_percent: float = Field(description="Price change percentage")
    vwap: float = Field(description="Volume weighted average price")
    label: str = Field(description="Date label")
    change_over_time: float = Field(description="Change over time")


class HistoricalData(BaseModel):
    """Model to parse the full historical data response"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    historical: list[HistoricalPrice] = Field(
        description="List of historical price data"
    )

    @classmethod
    def parse_api_response(cls, data: dict[str, Any]) -> HistoricalData:
        """Parse raw API response into validated HistoricalData model."""
        # Ensure historical data is validated
        historical_prices = [
            HistoricalPrice(**item) for item in data.get("historical", [])
        ]
        return cls(symbol=data["symbol"], historical=historical_prices)


class IntradayPrice(BaseModel):
    """Intraday price data point"""

    model_config = default_model_config

    date: datetime = Field(description="Date and time")
    open: float = Field(description="Opening price")
    low: float = Field(description="Low price")
    high: float = Field(description="High price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Trading volume")


class ExecutiveCompensation(BaseModel):
    """Executive compensation information based on SEC filings"""

    model_config = default_model_config

    cik: str = Field(description="SEC CIK number")
    symbol: str = Field(description="Company symbol")
    company_name: str = Field(description="Company name")
    industry_title: str = Field(description="Industry classification")
    filing_date: date = Field(description="SEC filing date")
    accepted_date: datetime = Field(description="SEC acceptance date")
    name_and_position: str = Field(description="Executive name and title")
    year: int = Field(description="Compensation year")
    salary: float = Field(description="Base salary")
    bonus: float = Field(description="Annual bonus")
    stock_award: float = Field(description="Stock awards value")
    option_award: float | None = Field(None, description="Option awards value")
    incentive_plan_compensation: float = Field(
        description="Incentive plan compensation"
    )
    all_other_compensation: float = Field(description="All other compensation")
    total: float = Field(description="Total compensation")
    url: HttpUrl = Field(description="SEC filing URL")


class HistoricalShareFloat(ShareFloat):
    """Historical share float data with the same structure as current share float"""

    pass


class RevenueSegmentItem(BaseModel):
    """Single year revenue segment data"""

    model_config = default_model_config

    date: str = Field(description="Fiscal year end date")
    segments: dict[str, float] = Field(description="Segment name to revenue mapping")

    def __init__(self, **data: Any) -> None:
        """Custom init to handle the single-key dictionary structure.

        Args:
            **data: Dictionary of initialization parameters where either:
                   - It contains a single key (date) mapping to a dict of segments
                   - It contains 'date' and 'segments' keys directly
        """
        if len(data) == 1:
            date_key = next(iter(data))
            segments = data[date_key]
            super().__init__(date=date_key, segments=segments)
        else:
            super().__init__(**data)


class ProductRevenueSegment(RevenueSegmentItem):
    """Product revenue segmentation with product segments"""

    pass


class GeographicRevenueSegment(RevenueSegmentItem):
    """Geographic revenue segmentation with region segments"""

    pass


class SymbolChange(BaseModel):
    """Symbol change information from the FMP API"""

    model_config = default_model_config

    change_date: date = Field(
        description="Date when the symbol change occurred", alias="date"
    )
    name: str = Field(description="Company or security name")
    old_symbol: str = Field(alias="oldSymbol", description="Previous trading symbol")
    new_symbol: str = Field(alias="newSymbol", description="New trading symbol")


class PriceTarget(BaseModel):
    """Price target data based on FMP API response"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime = Field(
        alias="publishedDate", description="Publication date and time"
    )
    news_url: str = Field(alias="newsURL", description="URL to the news article")
    news_title: str | None = Field(
        None, alias="newsTitle", description="Title of the news article"
    )
    analyst_name: str | None = Field(
        alias="analystName", description="Name of the analyst"
    )
    price_target: float = Field(alias="priceTarget", description="Price target")
    adj_price_target: float = Field(
        alias="adjPriceTarget", description="Adjusted price target"
    )
    price_when_posted: float = Field(
        alias="priceWhenPosted", description="Stock price at publication"
    )
    news_publisher: str = Field(
        alias="newsPublisher", description="Publisher of the news"
    )
    news_base_url: str = Field(
        alias="newsBaseURL", description="Base URL of the news source"
    )
    analyst_company: str = Field(
        alias="analystCompany", description="Analyst's company"
    )


class PriceTargetSummary(BaseModel):
    """Price target summary statistics"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    last_month: int = Field(
        alias="lastMonth", description="Number of analysts in the last month"
    )
    last_month_avg_price_target: float = Field(
        alias="lastMonthAvgPriceTarget",
        description="Average price target from the last month",
    )
    last_quarter: int = Field(
        alias="lastQuarter", description="Number of analysts in the last quarter"
    )
    last_quarter_avg_price_target: float = Field(
        alias="lastQuarterAvgPriceTarget",
        description="Average price target from the last quarter",
    )
    last_year: int = Field(
        alias="lastYear", description="Number of analysts in the last year"
    )
    last_year_avg_price_target: float = Field(
        alias="lastYearAvgPriceTarget",
        description="Average price target from the last year",
    )
    all_time: int = Field(alias="allTime", description="Total number of analysts")
    all_time_avg_price_target: float = Field(
        alias="allTimeAvgPriceTarget", description="Average price target of all time"
    )
    publishers: str = Field(
        description=(
            "JSON string containing list of publishers providing the price targets"
        )
    )

    @property
    def publishers_list(self) -> list[str] | None:
        """Get publishers as a parsed list."""
        if not self.publishers:
            return None
        try:
            parsed = json.loads(self.publishers)
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return parsed
        except json.JSONDecodeError:
            pass
        return None


class PriceTargetConsensus(BaseModel):
    """Price target consensus data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    target_high: float = Field(alias="targetHigh", description="Highest price target")
    target_low: float = Field(alias="targetLow", description="Lowest price target")
    target_consensus: float = Field(
        alias="targetConsensus", description="Consensus price target"
    )
    target_median: float = Field(
        alias="targetMedian", description="Median price target"
    )


class AnalystEstimate(BaseModel):
    """Analyst earnings and revenue estimates"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Estimate date")
    estimated_revenue_low: float = Field(
        alias="estimatedRevenueLow", description="Lowest estimated revenue"
    )
    estimated_revenue_high: float = Field(
        alias="estimatedRevenueHigh", description="Highest estimated revenue"
    )
    estimated_revenue_avg: float = Field(
        alias="estimatedRevenueAvg", description="Average estimated revenue"
    )
    estimated_ebitda_low: float = Field(
        alias="estimatedEbitdaLow", description="Lowest estimated EBITDA"
    )
    estimated_ebitda_high: float = Field(
        alias="estimatedEbitdaHigh", description="Highest estimated EBITDA"
    )
    estimated_ebitda_avg: float = Field(
        alias="estimatedEbitdaAvg", description="Average estimated EBITDA"
    )
    estimated_ebit_low: float = Field(
        alias="estimatedEbitLow", description="Lowest estimated EBIT"
    )
    estimated_ebit_high: float = Field(
        alias="estimatedEbitHigh", description="Highest estimated EBIT"
    )
    estimated_ebit_avg: float = Field(
        alias="estimatedEbitAvg", description="Average estimated EBIT"
    )
    estimated_net_income_low: float = Field(
        alias="estimatedNetIncomeLow", description="Lowest estimated net income"
    )
    estimated_net_income_high: float = Field(
        alias="estimatedNetIncomeHigh", description="Highest estimated net income"
    )
    estimated_net_income_avg: float = Field(
        alias="estimatedNetIncomeAvg", description="Average estimated net income"
    )
    estimated_sga_expense_low: float = Field(
        alias="estimatedSgaExpenseLow", description="Lowest estimated SG&A expense"
    )
    estimated_sga_expense_high: float = Field(
        alias="estimatedSgaExpenseHigh", description="Highest estimated SG&A expense"
    )
    estimated_sga_expense_avg: float = Field(
        alias="estimatedSgaExpenseAvg", description="Average estimated SG&A expense"
    )
    estimated_eps_low: float = Field(
        alias="estimatedEpsLow", description="Lowest estimated EPS"
    )
    estimated_eps_high: float = Field(
        alias="estimatedEpsHigh", description="Highest estimated EPS"
    )
    estimated_eps_avg: float = Field(
        alias="estimatedEpsAvg", description="Average estimated EPS"
    )
    number_analyst_estimated_revenue: int = Field(
        alias="numberAnalystEstimatedRevenue",
        description="Number of analysts estimating revenue",
    )
    number_analysts_estimated_eps: int = Field(
        alias="numberAnalystsEstimatedEps",
        description="Number of analysts estimating EPS",
    )


class AnalystRecommendation(BaseModel):
    """Analyst stock recommendation"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Recommendation date")
    analyst_ratings_buy: int = Field(
        alias="analystRatingsbuy", description="Number of buy ratings"
    )
    analyst_ratings_hold: int = Field(
        alias="analystRatingsHold", description="Number of hold ratings"
    )
    analyst_ratings_sell: int = Field(
        alias="analystRatingsSell", description="Number of sell ratings"
    )
    analyst_ratings_strong_sell: int = Field(
        alias="analystRatingsStrongSell", description="Number of strong sell ratings"
    )
    analyst_ratings_strong_buy: int = Field(
        alias="analystRatingsStrongBuy", description="Number of strong buy ratings"
    )


class UpgradeDowngrade(BaseModel):
    """Stock upgrade/downgrade data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime = Field(
        alias="publishedDate", description="Publication date of the news"
    )
    news_url: str = Field(alias="newsURL", description="URL of the news article")
    news_title: str = Field(alias="newsTitle", description="Title of the news article")
    news_base_url: str = Field(
        alias="newsBaseURL", description="Base URL of the news source"
    )
    news_publisher: str = Field(
        alias="newsPublisher", description="Publisher of the news article"
    )
    new_grade: str = Field(alias="newGrade", description="New rating grade")
    previous_grade: str | None = Field(
        None, alias="previousGrade", description="Previous rating grade"
    )
    grading_company: str = Field(
        alias="gradingCompany", description="Company providing the grade"
    )
    action: str = Field(description="Action taken (e.g., hold, buy, sell)")
    price_when_posted: Decimal = Field(
        alias="priceWhenPosted",
        description="Price of the stock when the article was posted",
    )


class UpgradeDowngradeConsensus(BaseModel):
    """Upgrade/downgrade consensus data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    consensus: str = Field(description="Overall consensus")
    strong_buy: int = Field(alias="strongBuy", description="Strong buy ratings")
    buy: int = Field(description="Buy ratings")
    hold: int = Field(description="Hold ratings")
    sell: int = Field(description="Sell ratings")
    strong_sell: int = Field(alias="strongSell", description="Strong sell ratings")
