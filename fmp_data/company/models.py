from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class CompanyProfile(BaseModel):
    """Company profile information."""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol (ticker)")
    price: float = Field(description="Current stock price")
    beta: float = Field(description="Beta value")
    vol_avg: int = Field(alias="volAvg", description="Average volume")
    mkt_cap: float = Field(alias="mktCap", description="Market capitalization")
    last_div: float = Field(alias="lastDiv", description="Last dividend payment")
    range: str = Field(description="52-week price range")
    changes: float = Field(description="Price change")
    company_name: str = Field(alias="companyName", description="Company name")
    currency: str = Field(description="Trading currency")
    cik: str = Field(description="CIK number")
    isin: str = Field(description="ISIN number")
    cusip: str = Field(description="CUSIP number")
    exchange: str = Field(description="Stock exchange")
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )
    industry: str = Field(description="Industry classification")
    website: AnyHttpUrl = Field(description="Company website")
    description: str = Field(description="Company description")
    ceo: str = Field(description="CEO name")
    sector: str = Field(description="Sector classification")
    country: str = Field(description="Country of incorporation")
    full_time_employees: str = Field(
        alias="fullTimeEmployees", description="Number of full-time employees"
    )
    phone: str = Field(description="Contact phone number")
    address: str = Field(description="Company address")
    city: str = Field(description="City")
    state: str = Field(description="State")
    zip: str = Field(description="ZIP/Postal code")
    dcf_diff: float = Field(alias="dcfDiff", description="DCF difference")
    dcf: float = Field(description="Discounted Cash Flow value")
    image: AnyHttpUrl = Field(description="Company logo URL")
    ipo_date: datetime = Field(alias="ipoDate", description="IPO date")
    default_image: bool = Field(
        alias="defaultImage", description="Whether using default image"
    )
    is_etf: bool = Field(alias="isEtf", description="Whether the symbol is an ETF")
    is_actively_trading: bool = Field(
        alias="isActivelyTrading", description="Whether actively trading"
    )
    is_adr: bool = Field(alias="isAdr", description="Whether is ADR")
    is_fund: bool = Field(alias="isFund", description="Whether is a fund")


class CompanyCoreInformation(BaseModel):
    """Core company information."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="allow",
    )

    # Required fields
    symbol: str = Field(description="Stock symbol (ticker)")
    cik: str = Field(description="CIK number")

    # Optional fields with defaults
    date: datetime | None = Field(None, description="Information date")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Stock exchange"
    )
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    registrant_name: str | None = Field(
        None, alias="registrantName", description="Registrant name"
    )
    industry: str | None = Field(None, description="Industry classification")
    sector: str | None = Field(None, description="Sector classification")
    zip: str | None = Field(None, description="ZIP/Postal code")
    state: str | None = Field(None, description="State")
    city: str | None = Field(None, description="City")
    address: str | None = Field(None, description="Address")
    website: AnyHttpUrl | None = Field(None, description="Company website")
    country: str | None = Field(None, description="Country")
    phone: str | None = Field(None, description="Phone number")
    sic: str | None = Field(None, description="SIC code")
    ticker_cusip: str | None = Field(
        None, alias="tickerCusip", description="CUSIP number"
    )
    business_address: str | None = Field(
        None, alias="businessAddress", description="Business address"
    )
    mail_address: str | None = Field(
        None, alias="mailAddress", description="Mailing address"
    )


class CompanyExecutive(BaseModel):
    """Company executive information."""

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(description="Executive title")
    name: str = Field(description="Executive name")
    pay: int = Field(description="Annual compensation")
    currency_pay: str = Field(alias="currencyPay", description="Compensation currency")
    gender: str = Field(description="Gender")
    year_born: int = Field(alias="yearBorn", description="Birth year")
    title_since: datetime = Field(alias="titleSince", description="Position start date")


class CompanyNote(BaseModel):
    """Company financial note."""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Note date")
    note: str = Field(description="Note content")
    filing_type: str = Field(alias="filingType", description="SEC filing type")
    section: str = Field(description="Section of the filing")


class CompanySearchResult(BaseModel):
    """Company search result."""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol (ticker)")
    name: str = Field(description="Company name")
    currency: str = Field(description="Trading currency")
    stock_exchange: str = Field(alias="stockExchange", description="Stock exchange")
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )


class EmployeeCount(BaseModel):
    """Company employee count history."""

    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(description="Report date")
    count: int = Field(description="Number of employees")
    reported_currency: str = Field(
        alias="reportedCurrency", description="Reporting currency"
    )
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")


class CompanySymbol(BaseModel):
    """Company symbol information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current stock price")
    exchange: str = Field(description="Stock exchange")


class ExchangeSymbol(BaseModel):
    """Exchange symbol information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
    price: float = Field(description="Current stock price")
    type: str = Field(description="Security type")


class CIKResult(BaseModel):
    """CIK search result"""

    model_config = ConfigDict(populate_by_name=True)

    cik: str = Field(description="CIK number")
    name: str = Field(description="Company name")
    symbol: str = Field(description="Stock symbol")


class CUSIPResult(BaseModel):
    """CUSIP search result"""

    model_config = ConfigDict(populate_by_name=True)

    cusip: str = Field(description="CUSIP number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")


class ISINResult(BaseModel):
    """ISIN search result"""

    model_config = ConfigDict(populate_by_name=True)

    isin: str = Field(description="ISIN number")
    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Company name")
