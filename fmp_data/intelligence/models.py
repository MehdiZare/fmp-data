# fmp_data/intelligence/models.py
import json
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PriceTarget(BaseModel):
    """Price target data based on FMP API response"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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
    publishers: list[str] | None = Field(
        None,
        description=(
            "List of publishers. Must be a valid JSON array string and"
            " will be parsed into a Python list."
        ),
    )

    @field_validator("publishers", mode="before")
    def validate_publishers(cls, value):
        """Validate and parse publishers field if it is a JSON string."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None  # Return None if parsing fails
        return value


class PriceTargetConsensus(BaseModel):
    """Price target consensus data"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    consensus: str = Field(description="Overall consensus")
    strong_buy: int = Field(alias="strongBuy", description="Strong buy ratings")
    buy: int = Field(description="Buy ratings")
    hold: int = Field(description="Hold ratings")
    sell: int = Field(description="Sell ratings")
    strong_sell: int = Field(alias="strongSell", description="Strong sell ratings")


class EarningEvent(BaseModel):
    """Earnings calendar event based on FMP API response"""

    model_config = ConfigDict(populate_by_name=True)

    event_date: date = Field(description="Earnings date", alias="date")
    symbol: str = Field(description="Company symbol")
    eps: float | None = Field(default=None, description="Actual earnings per share")
    eps_estimated: float | None = Field(
        alias="epsEstimated", default=None, description="Estimated earnings per share"
    )
    time: str | None = Field(default=None, description="Time of day (amc/bmo)")
    revenue: float | None = Field(default=None, description="Actual revenue")
    revenue_estimated: float | None = Field(
        alias="revenueEstimated", default=None, description="Estimated revenue"
    )
    fiscal_date_ending: date = Field(
        alias="fiscalDateEnding", description="Fiscal period end date"
    )
    updated_from_date: date = Field(
        alias="updatedFromDate", description="Last update date"
    )


class EarningConfirmed(BaseModel):
    """Confirmed earnings event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    exchange: str = Field(description="Stock exchange")
    time: str = Field(description="Earnings announcement time (HH:MM)")
    when: str = Field(description="Time of day (pre market/post market)")
    event_date: datetime = Field(description="Earnings announcement date", alias="date")
    publication_date: datetime = Field(
        alias="publicationDate", description="Publication date of the announcement"
    )
    title: str = Field(description="Title of the earnings announcement")
    url: str = Field(description="URL to the earnings announcement")


class EarningSurprise(BaseModel):
    """Earnings surprise data based on FMP API response"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    surprise_date: date = Field(description="Earnings date", alias="date")
    actual_earning_result: float = Field(
        alias="actualEarningResult", description="Actual earnings per share"
    )
    estimated_earning: float = Field(
        alias="estimatedEarning", description="Estimated earnings per share"
    )


class DividendEvent(BaseModel):
    """Dividend calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    ex_dividend_date: date = Field(description="Ex-dividend date", alias="date")
    label: str = Field(description="Human-readable date label")
    adj_dividend: float = Field(
        alias="adjDividend", description="Adjusted dividend amount"
    )
    dividend: float = Field(description="Declared dividend amount")
    record_date: date | None = Field(
        None, alias="recordDate", description="Record date"
    )
    payment_date: date | None = Field(
        None, alias="paymentDate", description="Payment date"
    )
    declaration_date: date | None = Field(
        None, alias="declarationDate", description="Declaration date"
    )


class StockSplitEvent(BaseModel):
    """Stock split calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    split_event_date: date = Field(description="Split date", alias="date")
    label: str = Field(description="Human-readable date label")
    numerator: int = Field(description="Numerator of the split ratio")
    denominator: int = Field(description="Denominator of the split ratio")


class IPOEvent(BaseModel):
    """IPO calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    company: str = Field(description="Company name")
    ipo_event_date: date = Field(description="IPO date", alias="date")
    exchange: str = Field(description="Exchange")
    actions: str = Field(description="IPO status")
    shares: int | None = Field(description="Number of shares")
    price_range: str | None = Field(
        alias="priceRange", description="Expected price range"
    )
    market_cap: Decimal | None = Field(
        alias="marketCap", description="Expected market cap"
    )


class FMPArticle(BaseModel):
    """Individual FMP article data"""

    title: str | None = Field(description="Article title")
    date: datetime = Field(description="Publication date and time")
    content: str | None = Field(description="Article content in HTML format")
    tickers: str | None = Field(None, description="Related stock tickers")
    image: HttpUrl | None = Field(None, description="Article image URL")
    link: HttpUrl | None = Field(None, description="Article URL")
    author: str | None = Field(None, description="Article author")
    site: str | None = Field(None, description="Publishing site name")


class FMPArticlesResponse(BaseModel):
    """Root response containing array of articles"""

    content: list[FMPArticle] = Field(description="List of articles")

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class GeneralNewsArticle(BaseModel):
    """General news article data"""

    publishedDate: datetime
    title: str
    image: HttpUrl
    site: str
    text: str
    url: HttpUrl


class StockNewsArticle(BaseModel):
    """Stock news article data"""

    symbol: str
    publishedDate: datetime
    title: str
    image: HttpUrl
    site: str
    text: str
    url: HttpUrl


class StockNewsSentiment(BaseModel):
    """Stock news article with sentiment data"""

    symbol: str
    publishedDate: datetime
    title: str
    image: HttpUrl
    site: str
    text: str
    url: HttpUrl
    sentiment: str
    sentimentScore: float


class ForexNewsArticle(BaseModel):
    """Forex news article data"""

    publishedDate: datetime = Field(description="Article publication date and time")
    title: str = Field(description="Article title")
    image: HttpUrl = Field(description="URL of the article image")
    site: str = Field(description="Source website")
    text: str = Field(description="Article preview text/summary")
    url: HttpUrl = Field(description="Full article URL")
    symbol: str = Field(description="Forex pair symbol")

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class CryptoNewsArticle(BaseModel):
    """Crypto news article data"""

    publishedDate: datetime = Field(description="Article publication date and time")
    title: str = Field(description="Article title")
    image: HttpUrl = Field(description="URL of the article image")
    site: str = Field(description="Source website")
    text: str = Field(description="Article preview text/summary")
    url: HttpUrl = Field(description="Full article URL")
    symbol: str = Field(description="Cryptocurrency trading pair symbol")

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class PressRelease(BaseModel):
    """Press release data"""

    symbol: str
    date: datetime
    title: str
    text: str


class PressReleaseBySymbol(BaseModel):
    """Press release data by company symbol"""

    symbol: str
    date: datetime
    title: str
    text: str


class HistoricalSocialSentiment(BaseModel):
    """Historical social sentiment data"""

    date: datetime
    symbol: str
    stocktwitsPosts: int
    twitterPosts: int
    stocktwitsComments: int
    twitterComments: int
    stocktwitsLikes: int
    twitterLikes: int
    stocktwitsImpressions: int
    twitterImpressions: int
    stocktwitsSentiment: float
    twitterSentiment: float


class TrendingSocialSentiment(BaseModel):
    """Trending social sentiment data"""

    symbol: str
    name: str
    rank: int
    sentiment: float
    lastSentiment: float


class SocialSentimentChanges(BaseModel):
    """Changes in social sentiment data"""

    symbol: str
    name: str
    rank: int
    sentiment: float
    sentimentChange: float
