import warnings
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator


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

    symbol: str = Field(description="Stock symbol (ticker)")
    cik: str = Field(description="CIK number")
    exchange: str = Field(description="Exchange name")
    sic_code: str | None = Field(None, alias="sicCode", description="SIC code")
    sic_group: str | None = Field(None, alias="sicGroup", description="SIC group")
    sic_description: str | None = Field(
        None, alias="sicDescription", description="SIC description"
    )
    state_location: str | None = Field(
        None, alias="stateLocation", description="Company state location"
    )
    state_of_incorporation: str | None = Field(
        None, alias="stateOfIncorporation", description="State of incorporation"
    )
    fiscal_year_end: str | None = Field(
        None, alias="fiscalYearEnd", description="Fiscal year end date"
    )
    business_address: str | None = Field(
        None, alias="businessAddress", description="Business address"
    )
    mailing_address: str | None = Field(
        None, alias="mailingAddress", description="Mailing address"
    )
    tax_identification_number: str | None = Field(
        None, alias="taxIdentificationNumber", description="Tax ID"
    )
    registrant_name: str | None = Field(
        None, alias="registrantName", description="Registrant name"
    )


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

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(description="Note title")
    cik: str = Field(description="CIK number")
    symbol: str = Field(description="Stock symbol")
    exchange: str = Field(description="Exchange name")


class CompanySearchResult(BaseModel):
    """Company search result"""

    symbol: str = Field(description="Stock symbol (ticker)")
    name: str = Field(description="Company name")
    currency: str | None = Field(None, description="Trading currency")
    stock_exchange: str | None = Field(
        None, alias="stockExchange", description="Stock exchange"
    )
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Exchange short name"
    )


class EmployeeCount(BaseModel):
    """Company employee count history."""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Company symbol")
    cik: str = Field(description="CIK number")
    acceptance_time: datetime = Field(
        alias="acceptanceTime", description="Filing acceptance time"
    )
    period_of_report: str = Field(alias="periodOfReport", description="Report period")
    company_name: str = Field(alias="companyName", description="Company name")
    form_type: str = Field(alias="formType", description="SEC form type")
    filing_date: str = Field(alias="filingDate", description="Filing date")
    employee_count: int = Field(
        alias="employeeCount", description="Number of employees"
    )
    source: str | None = Field(None, description="SEC filing source URL")


class CompanySymbol(BaseModel):
    """Company symbol information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current stock price")
    exchange: str | None = Field(None, description="Stock exchange")
    exchange_short_name: str | None = Field(
        None, alias="exchangeShortName", description="Exchange short name"
    )
    type: str | None = Field(None, description="Security type")


class ExchangeSymbol(BaseModel):
    """Exchange symbol information matching actual API response"""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        validate_assignment=True,
        validate_default=True,
    )

    # Fields with union types (|) instead of Optional
    symbol: str | None = Field(None, description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    price: float | None = Field(None, description="Current price")
    change_percentage: float | None = Field(
        None, alias="changesPercentage", description="Price change percentage"
    )
    change: float | None = Field(None, description="Price change")
    day_low: float | None = Field(None, alias="dayLow", description="Day low price")
    day_high: float | None = Field(None, alias="dayHigh", description="Day high price")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low")
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization"
    )
    price_avg_50: float | None = Field(
        None, alias="priceAvg50", description="50-day moving average"
    )
    price_avg_200: float | None = Field(
        None, alias="priceAvg200", description="200-day moving average"
    )
    exchange: str | None = Field(None, description="Stock exchange")
    volume: float | None = Field(None, description="Trading volume")
    avg_volume: float | None = Field(
        None, alias="avgVolume", description="Average volume"
    )
    open: float | None = Field(None, description="Opening price")
    previous_close: float | None = Field(
        None, alias="previousClose", description="Previous closing price"
    )
    eps: float | None = Field(None, description="Earnings per share")
    pe: float | None = Field(None, description="Price to earnings ratio")
    earnings_announcement: datetime | None = Field(None, alias="earningsAnnouncement")
    shares_outstanding: float | None = Field(
        None, alias="sharesOutstanding", description="Shares outstanding"
    )
    timestamp: int | None = Field(None, description="Quote timestamp")

    @classmethod
    @model_validator(mode="before")
    def validate_data(cls, data):
        """Validate data and convert invalid values to None with warnings"""
        if not isinstance(data, dict):
            return data

        cleaned_data = {}
        for field_name, field_value in data.items():
            try:
                # Check if field exists and is a float type
                field_info = cls.model_fields.get(field_name)
                if field_info and field_info.annotation in (float, float | None):
                    try:
                        if field_value is not None:
                            cleaned_data[field_name] = float(field_value)
                        else:
                            cleaned_data[field_name] = None
                    except (ValueError, TypeError):
                        warnings.warn(
                            f"Invalid value for {field_name}: "
                            f"{field_value}. Setting to None",
                            stacklevel=2,
                        )
                        cleaned_data[field_name] = None
                else:
                    cleaned_data[field_name] = field_value
            except Exception as e:
                warnings.warn(
                    f"Error processing field {field_name}: {str(e)}. "
                    f"Setting to None",
                    stacklevel=2,
                )
                cleaned_data[field_name] = None

        return cleaned_data


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


class AvailableIndex(BaseModel):
    """Market index information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Index symbol")
    name: str = Field(description="Index name")
    currency: str = Field(description="Trading currency")
    stock_exchange: str = Field(alias="stockExchange", description="Stock exchange")
    exchange_short_name: str = Field(
        alias="exchangeShortName", description="Exchange short name"
    )
