# fmp_data/sec/models.py
from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class SECFiling8K(BaseModel):
    """SEC 8-K filing data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str | None = Field(None, description="SEC CIK number")
    form_type: str | None = Field(None, alias="formType", description="SEC form type")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Filing acceptance date"
    )
    filed_date: datetime | None = Field(
        None,
        alias="filedDate",
        validation_alias=AliasChoices("filedDate", "filingDate"),
        description="Filing date",
    )
    has_financials: bool | None = Field(
        None, alias="hasFinancials", description="Whether filing has financials"
    )
    link: str | None = Field(None, description="Link to SEC filing index")
    final_link: str | None = Field(
        None, alias="finalLink", description="Link to the filing"
    )
    link_to_txt: str | None = Field(
        None, alias="linkToTxt", description="Link to text version"
    )
    link_to_html: str | None = Field(
        None, alias="linkToHtml", description="Link to HTML version"
    )
    link_to_filing_details: str | None = Field(
        None, alias="linkToFilingDetails", description="Link to filing details"
    )


class SECFinancialFiling(BaseModel):
    """SEC financial filing data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str | None = Field(None, description="SEC CIK number")
    form_type: str | None = Field(None, alias="formType", description="SEC form type")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Filing acceptance date"
    )
    filed_date: datetime | None = Field(
        None,
        alias="filedDate",
        validation_alias=AliasChoices("filedDate", "filingDate"),
        description="Filing date",
    )
    final_link: str | None = Field(
        None, alias="finalLink", description="Link to the filing"
    )
    link_to_txt: str | None = Field(
        None, alias="linkToTxt", description="Link to text version"
    )
    link_to_html: str | None = Field(
        None, alias="linkToHtml", description="Link to HTML version"
    )
    link_to_xbrl: str | None = Field(
        None, alias="linkToXbrl", description="Link to XBRL version"
    )
    has_financials: bool | None = Field(default=None)
    link: str | None = Field(default=None)


class SECFilingSearchResult(BaseModel):
    """SEC filing search result"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    cik: str | None = Field(None, description="SEC CIK number")
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    form_type: str | None = Field(None, alias="formType", description="SEC form type")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="Filing acceptance date"
    )
    filed_date: datetime | None = Field(
        None,
        alias="filedDate",
        validation_alias=AliasChoices("filedDate", "filingDate"),
        description="Filing date",
    )
    final_link: str | None = Field(
        None, alias="finalLink", description="Link to the filing"
    )
    link: str | None = Field(default=None)


class SECCompanySearchResult(BaseModel):
    """SEC company search result"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    cik: str | None = Field(None, description="SEC CIK number")
    company_name: str | None = Field(
        None,
        alias="companyName",
        validation_alias=AliasChoices("companyName", "name"),
        description="Company name",
    )
    exchange: str | None = Field(None, description="Stock exchange")
    sic_code: str | None = Field(None, alias="sicCode", description="SIC code")
    sic_description: str | None = Field(
        None, alias="sicDescription", description="SIC description"
    )
    industry_title: str | None = Field(
        None, alias="industryTitle", description="Industry title"
    )
    business_address: str | None = Field(
        None, alias="businessAddress", description="Business address"
    )
    phone_number: str | None = Field(
        None, alias="phoneNumber", description="Business phone number"
    )
    state: str | None = Field(None, description="State of incorporation")
    fiscal_year_end: str | None = Field(
        None, alias="fiscalYearEnd", description="Fiscal year end month"
    )


class SECProfile(BaseModel):
    """SEC company profile"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str | None = Field(None, description="SEC CIK number")
    company_name: str | None = Field(
        None,
        alias="companyName",
        validation_alias=AliasChoices("companyName", "registrantName"),
        description="Company name",
    )
    exchange: str | None = Field(None, description="Stock exchange")
    sic_code: str | None = Field(None, alias="sicCode", description="SIC code")
    sic_description: str | None = Field(
        None, alias="sicDescription", description="SIC description"
    )
    sic_group: str | None = Field(
        None, alias="sicGroup", description="SIC group category"
    )
    isin: str | None = Field(None, description="ISIN identifier")
    state_location: str | None = Field(
        None, alias="stateLocation", description="State of headquarters"
    )
    state_of_incorporation: str | None = Field(
        None, alias="stateOfIncorporation", description="State of incorporation"
    )
    fiscal_year_end: str | None = Field(
        None, alias="fiscalYearEnd", description="Fiscal year end month"
    )
    business_address: str | None = Field(
        None, alias="businessAddress", description="Business address"
    )
    mailing_address: str | None = Field(
        None, alias="mailingAddress", description="Mailing address"
    )
    business_phone: str | None = Field(
        None,
        alias="businessPhone",
        validation_alias=AliasChoices("businessPhone", "phoneNumber"),
        description="Business phone",
    )
    postal_code: str | None = Field(None, alias="postalCode", description="Postal code")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    country: str | None = Field(None, description="Country")
    description: str | None = Field(None, description="Company description")
    ceo: str | None = Field(None, description="CEO name")
    website: str | None = Field(None, description="Company website")
    ipo_date: str | None = Field(None, alias="ipoDate", description="IPO date")
    employees: str | None = Field(None, description="Number of employees")
    sec_filings_url: str | None = Field(
        None, alias="secFilingsUrl", description="SEC filings URL"
    )
    tax_identification_number: str | None = Field(
        None, alias="taxIdentificationNumber", description="Tax ID number"
    )
    fifty_two_week_range: str | None = Field(
        None, alias="fiftyTwoWeekRange", description="52-week price range"
    )
    is_active: bool | None = Field(
        None, alias="isActive", description="Whether company is active"
    )
    asset_type: str | None = Field(None, alias="assetType", description="Asset type")
    open_figi_composite: str | None = Field(
        None, alias="openFigiComposite", description="OpenFIGI composite ID"
    )
    price_currency: str | None = Field(
        None, alias="priceCurrency", description="Price currency"
    )
    market_sector: str | None = Field(
        None, alias="marketSector", description="Market sector"
    )
    security_type: str | None = Field(
        None, alias="securityType", description="Security type"
    )
    is_etf: bool | None = Field(None, alias="isEtf", description="Whether it's an ETF")
    is_adr: bool | None = Field(None, alias="isAdr", description="Whether it's an ADR")
    is_fund: bool | None = Field(
        None, alias="isFund", description="Whether it's a fund"
    )


class SICCode(BaseModel):
    """Standard Industrial Classification code"""

    model_config = default_model_config

    sic_code: str = Field(alias="sicCode", description="SIC code")
    industry: str | None = Field(
        None,
        alias="industryTitle",
        validation_alias=AliasChoices("industryTitle", "industry"),
        description="Industry name",
    )
    office: str | None = Field(None, description="SEC office")


class IndustryClassification(BaseModel):
    """Industry classification data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    cik: str | None = Field(None, description="SEC CIK number")
    sic_code: str | None = Field(None, alias="sicCode", description="SIC code")
    industry_title: str | None = Field(
        None, alias="industryTitle", description="Industry title"
    )
    business_address: str | None = Field(
        None, alias="businessAddress", description="Business address"
    )
    phone_number: str | None = Field(
        None, alias="phoneNumber", description="Business phone number"
    )
