from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

from fmp_data.schema import BaseArgModel, DateRangeArg


# Available Economic Indicators
class EconomicIndicatorType(str, Enum):
    """Types of economic indicators available"""

    GDP = "GDP"
    REAL_GDP = "realGDP"
    NOMINAL_POTENTIAL_GDP = "nominalPotentialGDP"
    REAL_GDP_PER_CAPITA = "realGDPPerCapita"
    FEDERAL_FUNDS = "federalFunds"
    CPI = "CPI"
    INFLATION_RATE = "inflationRate"
    INFLATION = "inflation"
    RETAIL_SALES = "retailSales"
    CONSUMER_SENTIMENT = "consumerSentiment"
    DURABLE_GOODS = "durableGoods"
    UNEMPLOYMENT_RATE = "unemploymentRate"
    NONFARM_PAYROLL = "totalNonfarmPayroll"
    INITIAL_CLAIMS = "initialClaims"
    INDUSTRIAL_PRODUCTION = "industrialProductionTotalIndex"
    HOUSING_STARTS = "newPrivatelyOwnedHousingUnitsStartedTotalUnits"
    VEHICLE_SALES = "totalVehicleSales"
    RETAIL_MONEY_FUNDS = "retailMoneyFunds"
    RECESSION_PROBABILITIES = "smoothedUSRecessionProbabilities"
    CD_RATES = "3MonthOr90DayRatesAndYieldsCertificatesOfDeposit"
    CREDIT_CARD_INTEREST_RATE = "commercialBankInterestRateOnCreditCardPlansAllAccounts"
    MORTGAGE_RATE_30 = "30YearFixedRateMortgageAverage"
    MORTGAGE_RATE_15 = "15YearFixedRateMortgageAverage"


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


# Response schemas for economics endpoints
class TreasuryRateData(BaseModel):
    """Daily treasury rate data"""

    rate_date: date = Field(..., description="Date of the rates")
    month_1: float | None = Field(None, description="1-month Treasury rate")
    month_2: float | None = Field(None, description="2-month Treasury rate")
    month_3: float | None = Field(None, description="3-month Treasury rate")
    month_6: float | None = Field(None, description="6-month Treasury rate")
    year_1: float | None = Field(None, description="1-year Treasury rate")
    year_2: float | None = Field(None, description="2-year Treasury rate")
    year_5: float | None = Field(None, description="5-year Treasury rate")
    year_10: float | None = Field(None, description="10-year Treasury rate")
    year_30: float | None = Field(None, description="30-year Treasury rate")


class EconomicIndicatorData(BaseModel):
    """Economic indicator value"""

    indicator_date: date = Field(..., description="Date of the indicator value")
    value: float = Field(..., description="Value of the indicator")
    name: str = Field(..., description="Name of the indicator")


class EconomicEventData(BaseModel):
    """Economic calendar event"""

    event: str = Field(..., description="Name of the economic event")
    event_date: datetime = Field(..., description="Date and time of the event")
    country: str = Field(..., description="Country code")
    actual: float | None = Field(None, description="Actual value if released")
    estimate: float | None = Field(None, description="Estimated value")
    impact: str | None = Field(None, description="Expected market impact")
