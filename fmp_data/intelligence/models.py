# fmp_data/intelligence/models.py
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceTarget(BaseModel):
    """Price target data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Publication date")
    analyst_name: str = Field(alias="analystName", description="Analyst name")
    analyst_company: str = Field(alias="analystCompany", description="Analyst company")
    target_price: Decimal = Field(alias="targetPrice", description="Price target")
    price_when_posted: Decimal = Field(
        alias="priceWhenPosted", description="Stock price at publication"
    )
    rating: str = Field(description="Analyst rating")
    exchange: str = Field(description="Stock exchange")


class PriceTargetSummary(BaseModel):
    """Price target summary statistics"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    target_consensus: Decimal = Field(
        alias="targetConsensus", description="Consensus price target"
    )
    target_high: Decimal = Field(alias="targetHigh", description="Highest price target")
    target_low: Decimal = Field(alias="targetLow", description="Lowest price target")
    target_average: Decimal = Field(
        alias="targetAverage", description="Average price target"
    )
    target_median: Decimal = Field(
        alias="targetMedian", description="Median price target"
    )
    last_update: datetime = Field(alias="lastUpdate", description="Last update date")
    number_of_analysts: int = Field(
        alias="numberOfAnalysts", description="Number of analysts"
    )


class PriceTargetConsensus(BaseModel):
    """Price target consensus data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    consensus_type: str = Field(alias="consensusType", description="Type of consensus")
    consensus: str = Field(description="Consensus rating")
    total_analysts: int = Field(
        alias="totalAnalysts", description="Total number of analysts"
    )
    buy_analysts: int = Field(alias="buyAnalysts", description="Number of buy ratings")
    hold_analysts: int = Field(
        alias="holdAnalysts", description="Number of hold ratings"
    )
    sell_analysts: int = Field(
        alias="sellAnalysts", description="Number of sell ratings"
    )
    consensus_date: datetime = Field(
        alias="consensusDate", description="Consensus date"
    )


class AnalystEstimate(BaseModel):
    """Analyst earnings estimate"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Estimate date")
    estimate_type: str = Field(alias="estimateType", description="Type of estimate")
    estimate: Decimal = Field(description="Earnings estimate")
    currency: str = Field(description="Currency")
    period: str = Field(description="Fiscal period")
    year: int = Field(description="Fiscal year")
    analysts_count: int = Field(alias="analystsCount", description="Number of analysts")


class AnalystRecommendation(BaseModel):
    """Analyst stock recommendation"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Recommendation date")
    analyst_company: str = Field(alias="analystCompany", description="Analyst company")
    recommendation: str = Field(description="Stock recommendation")
    previous_recommendation: str | None = Field(
        alias="previousRecommendation", description="Previous recommendation"
    )
    ratings_count: int = Field(alias="ratingsCount", description="Number of ratings")


class UpgradeDowngrade(BaseModel):
    """Stock upgrade/downgrade data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Publication date")
    action: str = Field(description="Upgrade/downgrade action")
    company: str = Field(description="Analysis company")
    from_grade: str = Field(alias="fromGrade", description="Previous rating")
    to_grade: str = Field(alias="toGrade", description="New rating")
    price_target: Decimal | None = Field(
        alias="priceTarget", description="New price target"
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
    """Earnings calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Earnings date")
    eps_estimate: Decimal | None = Field(
        alias="epsEstimate", description="EPS estimate"
    )
    eps_actual: Decimal | None = Field(alias="epsActual", description="Actual EPS")
    revenue_estimate: Decimal | None = Field(
        alias="revenueEstimate", description="Revenue estimate"
    )
    revenue_actual: Decimal | None = Field(
        alias="revenueActual", description="Actual revenue"
    )
    fiscal_quarter: int = Field(alias="fiscalQuarter", description="Fiscal quarter")
    fiscal_year: int = Field(alias="fiscalYear", description="Fiscal year")
    time: str | None = Field(description="Time of day (BMO/AMC)")


class EarningConfirmed(EarningEvent):
    """Confirmed earnings event"""

    confirmed_date: datetime = Field(
        alias="confirmedDate", description="Date earnings confirmed"
    )
    conference_call_time: datetime | None = Field(
        alias="conferenceCallTime", description="Conference call time"
    )


class EarningSurprise(BaseModel):
    """Earnings surprise data"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Earnings date")
    actual_eps: Decimal = Field(alias="actualEps", description="Actual EPS")
    estimated_eps: Decimal = Field(alias="estimatedEps", description="Estimated EPS")
    surprise: Decimal = Field(description="EPS surprise amount")
    surprise_percentage: Decimal = Field(
        alias="surprisePercentage", description="Surprise percentage"
    )
    change_percent: Decimal = Field(
        alias="changePercent", description="Stock price change %"
    )
    change_value: Decimal = Field(
        alias="changeValue", description="Stock price change value"
    )


class DividendEvent(BaseModel):
    """Dividend calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    dividend: Decimal = Field(description="Dividend amount")
    record_date: date = Field(alias="recordDate", description="Record date")
    payment_date: date = Field(alias="paymentDate", description="Payment date")
    declaration_date: date = Field(
        alias="declarationDate", description="Declaration date"
    )
    ex_date: date = Field(alias="exDate", description="Ex-dividend date")
    frequency: str = Field(description="Payment frequency")


class StockSplitEvent(BaseModel):
    """Stock split calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    date: date = Field(description="Split date")
    ratio: str = Field(description="Split ratio")
    to_factor: int = Field(alias="toFactor", description="New shares factor")
    from_factor: int = Field(alias="fromFactor", description="Old shares factor")
    declaration_date: date | None = Field(
        alias="declarationDate", description="Declaration date"
    )


class IPOEvent(BaseModel):
    """IPO calendar event"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    company: str = Field(description="Company name")
    date: date = Field(description="IPO date")
    exchange: str = Field(description="Exchange")
    actions: str = Field(description="IPO status")
    shares: int | None = Field(description="Number of shares")
    price_range: str | None = Field(
        alias="priceRange", description="Expected price range"
    )
    market_cap: Decimal | None = Field(
        alias="marketCap", description="Expected market cap"
    )
