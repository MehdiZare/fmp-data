from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import json
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from pydantic import (
    AliasChoices,
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    TypeAdapter,
    ValidationError,
    field_validator,
)
from pydantic.alias_generators import to_camel

from fmp_data.models import ShareFloat

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)

UTC = ZoneInfo("UTC")


class CompanyProfile(BaseModel):
    """Company profile information."""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol (ticker)")
    price: float | None = Field(None, description="Current stock price")
    beta: float | None = Field(None, description="Beta value")
    vol_avg: int | None = Field(None, description="Average volume")
    mkt_cap: float | None = Field(None, description="Market capitalization")
    last_div: float | None = Field(None, description="Last dividend payment")
    range: str | None = Field(None, description="52-week price range")
    changes: float | None = Field(None, description="Price change")
    company_name: str | None = Field(None, description="Company name")
    currency: str | None = Field(None, description="Trading currency")
    cik: str | None = Field(None, description="CIK number")
    isin: str | None = Field(None, description="ISIN number")
    cusip: str | None = Field(None, description="CUSIP number")
    exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(None, description="Exchange short name")
    industry: str | None = Field(None, description="Industry classification")
    website: AnyHttpUrl | None = Field(None, description="Company website")
    description: str | None = Field(None, description="Company description")
    ceo: str | None = Field(None, description="CEO name")
    sector: str | None = Field(None, description="Sector classification")
    country: str | None = Field(None, description="Country of incorporation")
    full_time_employees: str | None = Field(
        None, description="Number of full-time employees"
    )
    phone: str | None = Field(None, description="Contact phone number")
    address: str | None = Field(None, description="Company address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    zip: str | None = Field(None, description="ZIP/Postal code")
    dcf_diff: float | None = Field(None, description="DCF difference")
    dcf: float | None = Field(None, description="Discounted Cash Flow value")
    image: AnyHttpUrl | None = Field(None, description="Company logo URL")
    ipo_date: datetime | None = Field(None, description="IPO date")
    default_image: bool | None = Field(None, description="Whether using default image")
    is_etf: bool | None = Field(None, description="Whether the symbol is an ETF")
    is_actively_trading: bool | None = Field(
        None, description="Whether actively trading"
    )
    is_adr: bool | None = Field(None, description="Whether is ADR")
    is_fund: bool | None = Field(None, description="Whether is a fund")

    @field_validator("website", mode="before")
    @classmethod
    def normalize_website(cls, value: Any) -> Any:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return None
            if " " in cleaned:
                cleaned = cleaned.split()[0]
            cleaned = cleaned.replace("http://www:", "http://www.").replace(
                "https://www:", "https://www."
            )
            if "://" not in cleaned:
                return f"https://{cleaned}"
            try:
                parsed = urlparse(cleaned)
            except ValueError:
                return None
            if not parsed.scheme or not parsed.netloc:
                return None
            if not parsed.hostname or "." not in parsed.hostname:
                return None
            adapter = TypeAdapter(AnyHttpUrl)
            try:
                adapter.validate_python(cleaned)
            except ValidationError:
                return None
            return cleaned
        return value


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
    """
    Real-time stock quote data

    Relative path: models/quote.py
    """

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current price")
    change_percentage: float = Field(
        alias="changePercentage", description="Price change percentage"
    )
    change: float = Field(description="Price change")
    day_low: float = Field(alias="dayLow", description="Day low price")
    day_high: float = Field(alias="dayHigh", description="Day high price")
    year_high: float = Field(alias="yearHigh", description="52-week high")
    year_low: float = Field(alias="yearLow", description="52-week low")
    market_cap: float = Field(alias="marketCap", description="Market capitalization")
    price_avg_50: float = Field(alias="priceAvg50", description="50-day average price")
    price_avg_200: float = Field(
        alias="priceAvg200", description="200-day average price"
    )
    volume: int = Field(description="Trading volume")
    exchange: str = Field(description="Stock exchange")
    open_price: float = Field(alias="open", description="Opening price")
    previous_close: float = Field(
        alias="previousClose", description="Previous close price"
    )
    timestamp: datetime = Field(description="Quote timestamp")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> datetime:
        """Parse Unix timestamp to datetime with UTC timezone"""
        if isinstance(value, datetime):
            return value
        return datetime.fromtimestamp(float(value), tz=UTC)

    @property
    def quote_datetime(self) -> datetime:
        """Convert Unix timestamp to datetime object"""
        return self.timestamp


class SimpleQuote(BaseModel):
    """Simple stock quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    price: float = Field(description="Current price")
    volume: int = Field(description="Trading volume")


class AftermarketTrade(BaseModel):
    """Aftermarket trade data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    price: float | None = Field(None, description="Trade price")
    trade_size: int | None = Field(None, alias="tradeSize", description="Trade size")
    timestamp: int | None = Field(None, description="Trade timestamp")


class AftermarketQuote(BaseModel):
    """Aftermarket quote data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    bid_size: int | None = Field(None, alias="bidSize", description="Bid size")
    bid_price: float | None = Field(None, alias="bidPrice", description="Bid price")
    ask_size: int | None = Field(None, alias="askSize", description="Ask size")
    ask_price: float | None = Field(None, alias="askPrice", description="Ask price")
    volume: int | None = Field(None, description="Trading volume")
    timestamp: int | None = Field(None, description="Quote timestamp")


class StockPriceChange(BaseModel):
    """Stock price change percentages over multiple time horizons"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    one_day: float | None = Field(
        None, alias="1D", description="1-day price change percentage"
    )
    five_day: float | None = Field(
        None, alias="5D", description="5-day price change percentage"
    )
    one_month: float | None = Field(
        None, alias="1M", description="1-month price change percentage"
    )
    three_month: float | None = Field(
        None, alias="3M", description="3-month price change percentage"
    )
    six_month: float | None = Field(
        None, alias="6M", description="6-month price change percentage"
    )
    ytd: float | None = Field(
        None, alias="ytd", description="Year-to-date price change percentage"
    )
    one_year: float | None = Field(
        None, alias="1Y", description="1-year price change percentage"
    )
    three_year: float | None = Field(
        None, alias="3Y", description="3-year price change percentage"
    )
    five_year: float | None = Field(
        None, alias="5Y", description="5-year price change percentage"
    )
    ten_year: float | None = Field(
        None, alias="10Y", description="10-year price change percentage"
    )
    max_change: float | None = Field(
        None, alias="max", description="Max price change percentage"
    )


class HistoricalPrice(BaseModel):
    """Historical price data point"""

    model_config = default_model_config

    date: datetime = Field(description="Date of the price data")
    open: float | None = Field(None, description="Opening price")
    high: float | None = Field(None, description="High price")
    low: float | None = Field(None, description="Low price")
    close: float | None = Field(None, description="Closing price")
    price: float | None = Field(None, description="Lightweight closing price")
    adj_close: float | None = Field(
        None, alias="adjClose", description="Adjusted closing price"
    )
    volume: int | None = Field(None, description="Trading volume")
    change: float | None = Field(None, description="Price change")
    change_percent: float | None = Field(
        None, alias="changePercent", description="Price change percentage"
    )
    vwap: float | None = Field(None, description="Volume weighted average price")


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
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    industry_title: str | None = Field(
        None, alias="industryTitle", description="Industry classification"
    )
    filing_date: date = Field(alias="filingDate", description="SEC filing date")
    accepted_date: datetime = Field(
        alias="acceptedDate", description="SEC acceptance date"
    )
    name_and_position: str = Field(
        alias="nameAndPosition", description="Executive name and title"
    )
    year: int = Field(description="Compensation year")
    salary: float = Field(description="Base salary")
    bonus: float = Field(description="Annual bonus")
    stock_award: float = Field(alias="stockAward", description="Stock awards value")
    option_award: float | None = Field(
        None, alias="optionAward", description="Option awards value"
    )
    incentive_plan_compensation: float = Field(
        alias="incentivePlanCompensation",
        description="Incentive plan compensation",
    )
    all_other_compensation: float = Field(
        alias="allOtherCompensation", description="All other compensation"
    )
    total: float = Field(description="Total compensation")
    url: HttpUrl | None = Field(None, alias="link", description="SEC filing URL")


class HistoricalShareFloat(ShareFloat):
    """Historical share float data with the same structure as current share float"""

    pass


class RevenueSegmentItem(BaseModel):
    """Single year revenue segment data"""

    model_config = default_model_config

    date: str = Field(description="Fiscal year end date")
    segments: dict[str, float] = Field(
        alias="data", description="Segment name to revenue mapping"
    )

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
    name: str = Field(alias="companyName", description="Company or security name")
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
        alias="lastMonthCount", description="Number of analysts in the last month"
    )
    last_month_avg_price_target: float = Field(
        alias="lastMonthAvgPriceTarget",
        description="Average price target from the last month",
    )
    last_quarter: int = Field(
        alias="lastQuarterCount", description="Number of analysts in the last quarter"
    )
    last_quarter_avg_price_target: float = Field(
        alias="lastQuarterAvgPriceTarget",
        description="Average price target from the last quarter",
    )
    last_year: int = Field(
        alias="lastYearCount", description="Number of analysts in the last year"
    )
    last_year_avg_price_target: float = Field(
        alias="lastYearAvgPriceTarget",
        description="Average price target from the last year",
    )
    all_time: int = Field(alias="allTimeCount", description="Total number of analysts")
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
    date: datetime | None = Field(None, description="Estimate date")
    estimated_revenue_low: float | None = Field(
        None,
        alias="estimatedRevenueLow",
        validation_alias=AliasChoices("estimatedRevenueLow", "revenueLow"),
        description="Lowest estimated revenue",
    )
    estimated_revenue_high: float | None = Field(
        None,
        alias="estimatedRevenueHigh",
        validation_alias=AliasChoices("estimatedRevenueHigh", "revenueHigh"),
        description="Highest estimated revenue",
    )
    estimated_revenue_avg: float | None = Field(
        None,
        alias="estimatedRevenueAvg",
        validation_alias=AliasChoices("estimatedRevenueAvg", "revenueAvg"),
        description="Average estimated revenue",
    )
    estimated_ebitda_low: float | None = Field(
        None,
        alias="estimatedEbitdaLow",
        validation_alias=AliasChoices("estimatedEbitdaLow", "ebitdaLow"),
        description="Lowest estimated EBITDA",
    )
    estimated_ebitda_high: float | None = Field(
        None,
        alias="estimatedEbitdaHigh",
        validation_alias=AliasChoices("estimatedEbitdaHigh", "ebitdaHigh"),
        description="Highest estimated EBITDA",
    )
    estimated_ebitda_avg: float | None = Field(
        None,
        alias="estimatedEbitdaAvg",
        validation_alias=AliasChoices("estimatedEbitdaAvg", "ebitdaAvg"),
        description="Average estimated EBITDA",
    )
    estimated_ebit_low: float | None = Field(
        None,
        alias="estimatedEbitLow",
        validation_alias=AliasChoices("estimatedEbitLow", "ebitLow"),
        description="Lowest estimated EBIT",
    )
    estimated_ebit_high: float | None = Field(
        None,
        alias="estimatedEbitHigh",
        validation_alias=AliasChoices("estimatedEbitHigh", "ebitHigh"),
        description="Highest estimated EBIT",
    )
    estimated_ebit_avg: float | None = Field(
        None,
        alias="estimatedEbitAvg",
        validation_alias=AliasChoices("estimatedEbitAvg", "ebitAvg"),
        description="Average estimated EBIT",
    )
    estimated_net_income_low: float | None = Field(
        None,
        alias="estimatedNetIncomeLow",
        validation_alias=AliasChoices("estimatedNetIncomeLow", "netIncomeLow"),
        description="Lowest estimated net income",
    )
    estimated_net_income_high: float | None = Field(
        None,
        alias="estimatedNetIncomeHigh",
        validation_alias=AliasChoices("estimatedNetIncomeHigh", "netIncomeHigh"),
        description="Highest estimated net income",
    )
    estimated_net_income_avg: float | None = Field(
        None,
        alias="estimatedNetIncomeAvg",
        validation_alias=AliasChoices("estimatedNetIncomeAvg", "netIncomeAvg"),
        description="Average estimated net income",
    )
    estimated_sga_expense_low: float | None = Field(
        None,
        alias="estimatedSgaExpenseLow",
        validation_alias=AliasChoices("estimatedSgaExpenseLow", "sgaExpenseLow"),
        description="Lowest estimated SG&A expense",
    )
    estimated_sga_expense_high: float | None = Field(
        None,
        alias="estimatedSgaExpenseHigh",
        validation_alias=AliasChoices("estimatedSgaExpenseHigh", "sgaExpenseHigh"),
        description="Highest estimated SG&A expense",
    )
    estimated_sga_expense_avg: float | None = Field(
        None,
        alias="estimatedSgaExpenseAvg",
        validation_alias=AliasChoices("estimatedSgaExpenseAvg", "sgaExpenseAvg"),
        description="Average estimated SG&A expense",
    )
    estimated_eps_low: float | None = Field(
        None,
        alias="estimatedEpsLow",
        validation_alias=AliasChoices("estimatedEpsLow", "epsLow"),
        description="Lowest estimated EPS",
    )
    estimated_eps_high: float | None = Field(
        None,
        alias="estimatedEpsHigh",
        validation_alias=AliasChoices("estimatedEpsHigh", "epsHigh"),
        description="Highest estimated EPS",
    )
    estimated_eps_avg: float | None = Field(
        None,
        alias="estimatedEpsAvg",
        validation_alias=AliasChoices("estimatedEpsAvg", "epsAvg"),
        description="Average estimated EPS",
    )
    number_analyst_estimated_revenue: int | None = Field(
        None,
        alias="numberAnalystEstimatedRevenue",
        validation_alias=AliasChoices(
            "numberAnalystEstimatedRevenue", "numAnalystsRevenue"
        ),
        description="Number of analysts estimating revenue",
    )
    number_analysts_estimated_eps: int | None = Field(
        None,
        alias="numberAnalystsEstimatedEps",
        validation_alias=AliasChoices("numberAnalystsEstimatedEps", "numAnalystsEps"),
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


class CompanyPeer(BaseModel):
    """Company peer information."""

    model_config = default_model_config

    symbol: str = Field(alias="symbol", description="Peer company symbol")
    name: str = Field(alias="companyName", description="Peer company name")
    price: float | None = Field(None, alias="price", description="Current stock price")
    market_cap: int | None = Field(
        None, alias="mktCap", description="Market capitalization"
    )


class CompanyPeers(BaseModel):
    """Container for company peer information."""

    model_config = default_model_config

    peers: list[CompanyPeer] = Field(
        alias="peersList", description="List of company peers"
    )


class MergerAcquisition(BaseModel):
    """Merger and acquisition transaction data"""

    model_config = default_model_config

    companyName: str | None = Field(None, description="Company name")
    targetedCompanyName: str | None = Field(None, description="Targeted company name")
    dealDate: str | None = Field(None, description="Deal date")
    acceptanceTime: str | None = Field(None, description="Acceptance time")
    url: str | None = Field(None, description="URL to filing")


class ExecutiveCompensationBenchmark(BaseModel):
    """Executive compensation benchmark data by industry"""

    model_config = default_model_config

    year: int = Field(description="Year of compensation data")
    industryTitle: str = Field(description="Industry title")
    marketCapitalization: str | None = Field(
        None, description="Market capitalization range"
    )
    averageCompensation: float | None = Field(
        None, description="Average compensation for the industry"
    )
    averageTotalCompensation: float | None = Field(
        None, description="Average total compensation"
    )
    averageCashCompensation: float | None = Field(
        None, description="Average cash compensation"
    )
    averageEquityCompensation: float | None = Field(
        None, description="Average equity compensation"
    )
    averageOtherCompensation: float | None = Field(
        None, description="Average other compensation"
    )
