# fmp_data/intelligence/models.py
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import (
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
)
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


def _empty_str_to_none(value: object) -> object:
    if value == "":
        return None
    return value


class EarningEvent(BaseModel):
    """Earnings calendar event based on FMP API response"""

    model_config = default_model_config

    event_date: date = Field(description="Earnings date", alias="date")
    symbol: str = Field(description="Company symbol")
    eps: float | None = Field(
        default=None, alias="epsActual", description="Actual earnings per share"
    )
    eps_estimated: float | None = Field(
        alias="epsEstimated", default=None, description="Estimated earnings per share"
    )
    time: str | None = Field(default=None, description="Time of day (amc/bmo)")
    revenue: float | None = Field(
        default=None, alias="revenueActual", description="Actual revenue"
    )
    revenue_estimated: float | None = Field(
        alias="revenueEstimated", default=None, description="Estimated revenue"
    )
    fiscal_date_ending: date | None = Field(
        None, alias="fiscalDateEnding", description="Fiscal period end date"
    )
    updated_from_date: date | None = Field(
        None, alias="updatedFromDate", description="Last update date"
    )
    last_updated: date | None = Field(
        None, alias="lastUpdated", description="Last update date"
    )


class EarningConfirmed(BaseModel):
    """Confirmed earnings event"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    exchange: str = Field(description="Stock exchange")
    time: str | None = Field(None, description="Earnings announcement time (HH:MM)")
    when: str | None = Field(None, description="Time of day (pre market/post market)")
    event_date: datetime = Field(description="Earnings announcement date", alias="date")
    publication_date: datetime = Field(
        alias="publicationDate", description="Publication date of the announcement"
    )
    title: str = Field(description="Title of the earnings announcement")
    url: str = Field(description="URL to the earnings announcement")


class EarningSurprise(BaseModel):
    """Earnings surprise data based on FMP API response"""

    model_config = default_model_config

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

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    ex_dividend_date: date = Field(description="Ex-dividend date", alias="date")
    label: str | None = Field(None, description="Human-readable date label")
    adj_dividend: float | None = Field(
        None, alias="adjDividend", description="Adjusted dividend amount"
    )
    dividend: float | None = Field(None, description="Declared dividend amount")
    dividend_yield: float | None = Field(
        None, alias="yield", description="Dividend yield"
    )
    frequency: str | None = Field(None, description="Dividend frequency")
    record_date: Annotated[date | None, BeforeValidator(_empty_str_to_none)] = Field(
        None, alias="recordDate", description="Record date"
    )
    payment_date: Annotated[date | None, BeforeValidator(_empty_str_to_none)] = Field(
        None, alias="paymentDate", description="Payment date"
    )
    declaration_date: Annotated[
        date | None,
        BeforeValidator(_empty_str_to_none),
    ] = Field(None, alias="declarationDate", description="Declaration date")


class StockSplitEvent(BaseModel):
    """Stock split calendar event"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    split_event_date: date = Field(description="Split date", alias="date")
    label: str | None = Field(None, description="Human-readable date label")
    numerator: float = Field(description="Numerator of the split ratio")
    denominator: float = Field(description="Denominator of the split ratio")
    split_type: str | None = Field(None, alias="splitType", description="Split type")


class IPOEvent(BaseModel):
    """IPO calendar event"""

    model_config = default_model_config

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

    model_config = default_model_config

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

    model_config = default_model_config

    content: list[FMPArticle] = Field(description="List of articles")


class GeneralNewsArticle(BaseModel):
    """General news article data"""

    model_config = default_model_config

    publishedDate: datetime
    title: str
    image: HttpUrl
    site: str
    text: str
    url: HttpUrl


class StockNewsArticle(BaseModel):
    """Stock news article data"""

    model_config = default_model_config

    symbol: str | None = None
    publishedDate: datetime
    title: str
    image: HttpUrl | None = None
    site: str
    text: str
    url: HttpUrl


class StockNewsSentiment(BaseModel):
    """Stock news article with sentiment data"""

    model_config = default_model_config

    symbol: str | None = None
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

    model_config = default_model_config

    publishedDate: datetime = Field(description="Article publication date and time")
    title: str = Field(description="Article title")
    image: HttpUrl = Field(description="URL of the article image")
    site: str = Field(description="Source website")
    text: str = Field(description="Article preview text/summary")
    url: HttpUrl = Field(description="Full article URL")
    symbol: str | None = Field(default=None, description="Forex pair symbol")


class CryptoNewsArticle(BaseModel):
    """Crypto news article data"""

    model_config = default_model_config

    publishedDate: datetime = Field(description="Article publication date and time")
    title: str = Field(description="Article title")
    image: HttpUrl | None = Field(default=None, description="URL of the article image")
    site: str = Field(description="Source website")
    text: str = Field(description="Article preview text/summary")
    url: HttpUrl = Field(description="Full article URL")
    symbol: str = Field(description="Cryptocurrency trading pair symbol")
    publisher: str | None = Field(default=None, description="News publisher")


class PressRelease(BaseModel):
    """Press release data"""

    model_config = default_model_config

    symbol: str | None = None
    date: datetime | None = None
    title: str
    text: str


class PressReleaseBySymbol(BaseModel):
    """Press release data by company symbol"""

    model_config = default_model_config

    symbol: str
    date: datetime | None = None
    title: str
    text: str


class HistoricalSocialSentiment(BaseModel):
    """Historical social sentiment data"""

    model_config = default_model_config

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

    model_config = default_model_config

    symbol: str
    name: str
    rank: int
    sentiment: float
    lastSentiment: float


class SocialSentimentChanges(BaseModel):
    """Changes in social sentiment data"""

    model_config = default_model_config

    symbol: str
    name: str
    rank: int
    sentiment: float
    sentimentChange: float


class ESGData(BaseModel):
    """ESG environmental, social and governance data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Company symbol")
    cik: str | None = Field(None, description="CIK number")
    date: datetime | None = Field(None, description="ESG data date")
    environmental_score: float | None = Field(
        None, alias="environmentalScore", description="Environmental score"
    )
    social_score: float | None = Field(
        None, alias="socialScore", description="Social score"
    )
    governance_score: float | None = Field(
        None, alias="governanceScore", description="Governance score"
    )
    esg_score: float | None = Field(
        None, alias="ESGScore", description="Total ESG score"
    )
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    industry: str | None = Field(None, description="Industry classification")
    form_type: str | None = Field(None, alias="formType", description="SEC form type")
    accepted_date: datetime | None = Field(
        None, alias="acceptedDate", description="SEC acceptance date"
    )
    url: HttpUrl | None = Field(None, description="SEC filing URL")


class ESGRating(BaseModel):
    """ESG rating data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Company symbol")
    cik: str | None = Field(None, description="CIK number")
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    industry: str | None = Field(None, description="Industry classification")
    year: int | None = Field(None, description="Rating year")
    esg_risk_rating: str | None = Field(
        None, alias="ESGRiskRating", description="ESG risk rating grade"
    )
    industry_rank: str | None = Field(
        None, alias="industryRank", description="Industry rank (e.g. '4 out of 5')"
    )


class ESGBenchmark(BaseModel):
    model_config = default_model_config

    year: int | None = None
    sector: str | None = None

    # raw scores (always present in “sector benchmark” endpoint)
    environmental_score: float | None = Field(None, alias="environmentalScore")
    social_score: float | None = Field(None, alias="socialScore")
    governance_score: float | None = Field(None, alias="governanceScore")
    esg_score: float | None = Field(None, alias="ESGScore")

    # averages (present in “global benchmark” endpoint)
    average_environmental_score: float | None = Field(
        None, alias="averageEnvironmentalScore"
    )
    average_social_score: float | None = Field(None, alias="averageSocialScore")
    average_governance_score: float | None = Field(None, alias="averageGovernanceScore")
    average_esg_score: float | None = Field(None, alias="averageESGScore")


# Government Trading Models
class SenateTrade(BaseModel):
    """Senate trading data"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    disclosure_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("disclosureDate", "dateRecieved"),
        description="Date disclosure received",
    )
    transaction_date: datetime | None = Field(
        None, alias="transactionDate", description="Date of transaction"
    )
    first_name: str | None = Field(
        None, alias="firstName", description="Senator's first name"
    )
    last_name: str | None = Field(
        None, alias="lastName", description="Senator's last name"
    )
    office: str | None = Field(None, description="Senate office")
    district: str | None = Field(None, description="Senate district")
    owner: str | None = Field(None, description="Owner of the asset")
    asset_description: str | None = Field(
        None, alias="assetDescription", description="Description of the asset"
    )
    asset_type: str | None = Field(None, alias="assetType", description="Type of asset")
    type: str | None = Field(None, description="Transaction type")
    amount: str | None = Field(None, description="Transaction amount range")
    capital_gains_over_200usd: bool | None = Field(
        None,
        alias="capitalGainsOver200USD",
        description="Whether capital gains exceeded $200",
    )
    comment: str | None = Field(default=None, description="Additional comments")
    link: HttpUrl | None = Field(None, description="Link to filing")

    @property
    def date_received(self) -> datetime | None:
        """Backward-compatible alias for disclosure_date."""
        return self.disclosure_date


class HouseDisclosure(BaseModel):
    """House disclosure data"""

    model_config = default_model_config

    symbol: str | None = Field(
        None,
        validation_alias=AliasChoices("symbol", "ticker"),
        description="Stock symbol",
    )
    disclosure_date: datetime | None = Field(
        None, alias="disclosureDate", description="Date of disclosure"
    )
    transaction_date: datetime | None = Field(
        None, alias="transactionDate", description="Date of transaction"
    )
    first_name: str | None = Field(
        None, alias="firstName", description="Representative's first name"
    )
    last_name: str | None = Field(
        None, alias="lastName", description="Representative's last name"
    )
    office: str | None = Field(None, description="Representative office")
    district: str | None = Field(None, description="Congressional district")
    owner: str | None = Field(default=None, description="Owner of the asset")
    asset_description: str | None = Field(
        None, alias="assetDescription", description="Description of the asset"
    )
    asset_type: str | None = Field(None, alias="assetType", description="Type of asset")
    type: str | None = Field(None, description="Transaction type")
    amount: str | None = Field(None, description="Transaction amount range")
    comment: str | None = Field(default=None, description="Additional comments")
    link: HttpUrl | None = Field(None, description="Link to filing")
    capital_gains_over_200usd: bool | None = Field(
        None,
        alias="capitalGainsOver200USD",
        description="Whether capital gains exceeded $200",
    )

    @property
    def representative(self) -> str | None:
        """Backward-compatible representative name."""
        if self.office:
            return self.office
        name = " ".join(filter(None, [self.first_name, self.last_name])).strip()
        return name or None

    @property
    def ticker(self) -> str | None:
        """Backward-compatible ticker symbol."""
        return self.symbol

    @property
    def disclosure_year(self) -> str | None:
        """Backward-compatible disclosure year."""
        return str(self.disclosure_date.year) if self.disclosure_date else None


class CrowdfundingOffering(BaseModel):
    """Crowdfunding offering data"""

    model_config = default_model_config

    cik: str = Field(description="Company CIK number")
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    acceptance_time: datetime | None = Field(
        None,
        validation_alias=AliasChoices("acceptedDate", "acceptanceTime"),
        description="Filing acceptance time",
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    form_signification: str = Field(
        alias="formSignification", description="Form signification"
    )
    filing_date: datetime | None = Field(
        None,
        validation_alias=AliasChoices("filingDate", "fillingDate"),
        description="Filing date",
    )
    date: str | None = Field(None, description="Date in MM-DD-YYYY format")
    name_of_issuer: str | None = Field(
        None, alias="nameOfIssuer", description="Name of issuer"
    )
    legal_status_form: str | None = Field(
        None, alias="legalStatusForm", description="Legal status form"
    )
    jurisdiction_organization: str | None = Field(
        None, alias="jurisdictionOrganization", description="Jurisdiction"
    )

    # Issuer information
    issuer_street: str | None = Field(
        None, alias="issuerStreet", description="Issuer street address"
    )
    issuer_city: str | None = Field(None, alias="issuerCity", description="Issuer city")
    issuer_state_or_country: str | None = Field(
        None, alias="issuerStateOrCountry", description="Issuer state/country"
    )
    issuer_zip_code: str | None = Field(
        None, alias="issuerZipCode", description="Issuer ZIP code"
    )
    issuer_website: str | None = Field(
        None, alias="issuerWebsite", description="Issuer website"
    )

    # Intermediary information
    intermediary_company_name: str | None = Field(
        None, alias="intermediaryCompanyName", description="Intermediary company name"
    )
    intermediary_commission_cik: str | None = Field(
        None, alias="intermediaryCommissionCik", description="Intermediary CIK"
    )
    intermediary_commission_file_number: str | None = Field(
        None,
        alias="intermediaryCommissionFileNumber",
        description="Intermediary file number",
    )
    compensation_amount: str | None = Field(
        None, alias="compensationAmount", description="Compensation amount"
    )
    financial_interest: str | None = Field(
        None, alias="financialInterest", description="Financial interest"
    )

    # Offering details
    security_offered_type: str | None = Field(
        None, alias="securityOfferedType", description="Type of security offered"
    )
    security_offered_other_description: str | None = Field(
        default=None,
        alias="securityOfferedOtherDescription",
        description="Other security description",
    )
    number_of_security_offered: int = Field(
        alias="numberOfSecurityOffered", description="Number of securities offered"
    )
    offering_price: Decimal = Field(
        alias="offeringPrice", description="Price per security"
    )
    offering_amount: Decimal = Field(
        alias="offeringAmount", description="Total offering amount"
    )
    over_subscription_accepted: str = Field(
        alias="overSubscriptionAccepted", description="Over-subscription accepted"
    )
    over_subscription_allocation_type: str | None = Field(
        None,
        alias="overSubscriptionAllocationType",
        description="Over-subscription allocation type",
    )
    maximum_offering_amount: Decimal = Field(
        alias="maximumOfferingAmount", description="Maximum offering amount"
    )
    offering_deadline_date: str | None = Field(
        None, alias="offeringDeadlineDate", description="Offering deadline"
    )

    # Company metrics
    current_number_of_employees: int = Field(
        alias="currentNumberOfEmployees", description="Current employee count"
    )

    # Financial data - Most recent fiscal year
    total_asset_most_recent_fiscal_year: Decimal = Field(
        alias="totalAssetMostRecentFiscalYear", description="Total assets - most recent"
    )
    cash_and_cash_equivalent_most_recent_fiscal_year: Decimal = Field(
        alias="cashAndCashEquiValentMostRecentFiscalYear",
        description="Cash - most recent",
    )
    accounts_receivable_most_recent_fiscal_year: Decimal = Field(
        alias="accountsReceivableMostRecentFiscalYear", description="AR - most recent"
    )
    short_term_debt_most_recent_fiscal_year: Decimal = Field(
        alias="shortTermDebtMostRecentFiscalYear",
        description="Short term debt - most recent",
    )
    long_term_debt_most_recent_fiscal_year: Decimal = Field(
        alias="longTermDebtMostRecentFiscalYear",
        description="Long term debt - most recent",
    )
    revenue_most_recent_fiscal_year: Decimal = Field(
        alias="revenueMostRecentFiscalYear", description="Revenue - most recent"
    )
    cost_goods_sold_most_recent_fiscal_year: Decimal = Field(
        alias="costGoodsSoldMostRecentFiscalYear", description="COGS - most recent"
    )
    taxes_paid_most_recent_fiscal_year: Decimal = Field(
        alias="taxesPaidMostRecentFiscalYear", description="Taxes - most recent"
    )
    net_income_most_recent_fiscal_year: Decimal = Field(
        alias="netIncomeMostRecentFiscalYear", description="Net income - most recent"
    )

    # Financial data - Prior fiscal year
    total_asset_prior_fiscal_year: Decimal = Field(
        alias="totalAssetPriorFiscalYear", description="Total assets - prior"
    )
    cash_and_cash_equivalent_prior_fiscal_year: Decimal = Field(
        alias="cashAndCashEquiValentPriorFiscalYear", description="Cash - prior"
    )
    accounts_receivable_prior_fiscal_year: Decimal = Field(
        alias="accountsReceivablePriorFiscalYear", description="AR - prior"
    )
    short_term_debt_prior_fiscal_year: Decimal = Field(
        alias="shortTermDebtPriorFiscalYear", description="Short term debt - prior"
    )
    long_term_debt_prior_fiscal_year: Decimal = Field(
        alias="longTermDebtPriorFiscalYear", description="Long term debt - prior"
    )
    revenue_prior_fiscal_year: Decimal = Field(
        alias="revenuePriorFiscalYear", description="Revenue - prior"
    )
    cost_goods_sold_prior_fiscal_year: Decimal = Field(
        alias="costGoodsSoldPriorFiscalYear", description="COGS - prior"
    )
    taxes_paid_prior_fiscal_year: Decimal = Field(
        alias="taxesPaidPriorFiscalYear", description="Taxes - prior"
    )
    net_income_prior_fiscal_year: Decimal = Field(
        alias="netIncomePriorFiscalYear", description="Net income - prior"
    )


class CrowdfundingOfferingSearchItem(BaseModel):
    """Crowdfunding offering search item"""

    model_config = default_model_config

    cik: str = Field(description="Company CIK number")
    name: str | None = Field(None, description="Company or issuer name")
    date: str | None = Field(None, description="Offering date")


class EquityOffering(BaseModel):
    """Equity offering data"""

    model_config = default_model_config

    # Filing information
    date: str | None = Field(None, description="Offering date")
    filing_date: datetime | None = Field(
        None, alias="filingDate", description="Filing date"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    form_signification: str = Field(
        alias="formSignification", description="Form signification"
    )
    acceptance_time: datetime | None = Field(
        None,
        validation_alias=AliasChoices("acceptedDate", "acceptanceTime"),
        description="Filing acceptance time",
    )
    is_amendment: bool | None = Field(
        None, alias="isAmendment", description="Whether this is an amendment"
    )

    # Issuer information
    cik: str = Field(description="Company CIK number")
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    entity_name: str = Field(alias="entityName", description="Entity name")
    entity_type: str = Field(alias="entityType", description="Type of entity")
    jurisdiction_of_incorporation: str = Field(
        alias="jurisdictionOfIncorporation", description="Jurisdiction"
    )
    incorporated_within_five_years: bool | None = Field(
        alias="incorporatedWithinFiveYears",
        default=None,
        description="Whether incorporated within 5 years",
    )
    year_of_incorporation: str = Field(
        alias="yearOfIncorporation", description="Year of incorporation"
    )
    industry_group_type: str = Field(
        alias="industryGroupType", description="Industry group"
    )
    revenue_range: str | None = Field(
        default=None, alias="revenueRange", description="Revenue range"
    )

    # Issuer address
    issuer_street: str = Field(
        alias="issuerStreet", description="Issuer street address"
    )
    issuer_city: str = Field(alias="issuerCity", description="Issuer city")
    issuer_state_or_country: str = Field(
        alias="issuerStateOrCountry", description="Issuer state/country code"
    )
    issuer_state_or_country_description: str = Field(
        alias="issuerStateOrCountryDescription", description="Issuer state/country name"
    )
    issuer_zip_code: str = Field(alias="issuerZipCode", description="Issuer ZIP code")
    issuer_phone_number: str = Field(
        alias="issuerPhoneNumber", description="Issuer phone number"
    )

    # Related person information
    related_person_first_name: str = Field(
        alias="relatedPersonFirstName", description="Related person first name"
    )
    related_person_last_name: str = Field(
        alias="relatedPersonLastName", description="Related person last name"
    )
    related_person_street: str = Field(
        alias="relatedPersonStreet", description="Related person street"
    )
    related_person_city: str = Field(
        alias="relatedPersonCity", description="Related person city"
    )
    related_person_state_or_country: str = Field(
        alias="relatedPersonStateOrCountry",
        description="Related person state/country code",
    )
    related_person_state_or_country_description: str = Field(
        alias="relatedPersonStateOrCountryDescription",
        description="Related person state/country name",
    )
    related_person_zip_code: str = Field(
        alias="relatedPersonZipCode", description="Related person ZIP code"
    )
    related_person_relationship: str = Field(
        alias="relatedPersonRelationship", description="Related person relationship"
    )

    # Offering details
    federal_exemptions_exclusions: str = Field(
        alias="federalExemptionsExclusions", description="Federal exemptions"
    )
    date_of_first_sale: str = Field(
        alias="dateOfFirstSale", description="Date of first sale"
    )
    duration_of_offering_is_more_than_year: bool | None = Field(
        None,
        alias="durationOfOfferingIsMoreThanYear",
        description="Whether offering duration exceeds one year",
    )
    securities_offered_are_of_equity_type: bool | None = Field(
        None,
        alias="securitiesOfferedAreOfEquityType",
        description="Whether securities are equity type",
    )
    is_business_combination_transaction: bool | None = Field(
        None,
        alias="isBusinessCombinationTransaction",
        description="Whether this is a business combination",
    )

    # Financial details
    minimum_investment_accepted: Decimal = Field(
        alias="minimumInvestmentAccepted", description="Minimum investment"
    )
    total_offering_amount: Decimal = Field(
        alias="totalOfferingAmount", description="Total offering amount"
    )
    total_amount_sold: Decimal = Field(
        alias="totalAmountSold", description="Total amount sold"
    )
    total_amount_remaining: Decimal = Field(
        alias="totalAmountRemaining", description="Amount remaining"
    )
    has_non_accredited_investors: bool | None = Field(
        None,
        alias="hasNonAccreditedInvestors",
        description="Has non-accredited investors",
    )
    total_number_already_invested: int = Field(
        alias="totalNumberAlreadyInvested", description="Number of investors"
    )
    sales_commissions: Decimal = Field(
        alias="salesCommissions", description="Sales commissions"
    )
    finders_fees: Decimal = Field(alias="findersFees", description="Finders fees")
    gross_proceeds_used: Decimal = Field(
        alias="grossProceedsUsed", description="Gross proceeds used"
    )


class EquityOfferingSearchItem(BaseModel):
    """Equity offering search item"""

    model_config = default_model_config

    cik: str = Field(description="Company CIK number")
    name: str = Field(description="Company name")
    date: datetime = Field(description="Date of filing")


# Analyst Ratings and Grades Models
class RatingsSnapshot(BaseModel):
    """Current analyst ratings snapshot"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime | None = Field(default=None, description="Rating date")
    rating: str = Field(description="Overall rating (Buy, Hold, Sell)")
    rating_score: int | None = Field(
        default=None,
        alias="ratingScore",
        description="Numeric rating score",
    )
    rating_recommendation: str | None = Field(
        default=None, alias="ratingRecommendation", description="Rating recommendation"
    )
    rating_details_dcf_score: int | None = Field(
        default=None, alias="ratingDetailsDCFScore", description="DCF model score"
    )
    rating_details_dcf_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsDCFRecommendation",
        description="DCF recommendation",
    )
    rating_details_roe_score: int | None = Field(
        default=None,
        alias="ratingDetailsROEScore",
        description="Return on Equity score",
    )
    rating_details_roe_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsROERecommendation",
        description="ROE recommendation",
    )
    rating_details_roa_score: int | None = Field(
        default=None,
        alias="ratingDetailsROAScore",
        description="Return on Assets score",
    )
    rating_details_roa_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsROARecommendation",
        description="ROA recommendation",
    )
    rating_details_de_score: int | None = Field(
        default=None, alias="ratingDetailsDEScore", description="Debt to Equity score"
    )
    rating_details_de_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsDERecommendation",
        description="D/E recommendation",
    )
    rating_details_pe_score: int | None = Field(
        default=None,
        alias="ratingDetailsPEScore",
        description="Price to Earnings score",
    )
    rating_details_pe_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsPERecommendation",
        description="P/E recommendation",
    )
    rating_details_pb_score: int | None = Field(
        default=None, alias="ratingDetailsPBScore", description="Price to Book score"
    )
    rating_details_pb_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsPBRecommendation",
        description="P/B recommendation",
    )


class HistoricalRating(BaseModel):
    """Historical analyst rating data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    date: datetime = Field(description="Rating date")
    rating: str = Field(description="Overall rating")
    rating_score: int | None = Field(
        default=None,
        alias="ratingScore",
        description="Numeric rating score",
    )
    rating_recommendation: str | None = Field(
        default=None, alias="ratingRecommendation", description="Rating recommendation"
    )
    rating_details_dcf_score: int | None = Field(
        default=None, alias="ratingDetailsDCFScore", description="DCF model score"
    )
    rating_details_dcf_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsDCFRecommendation",
        description="DCF recommendation",
    )
    rating_details_roe_score: int | None = Field(
        default=None,
        alias="ratingDetailsROEScore",
        description="Return on Equity score",
    )
    rating_details_roe_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsROERecommendation",
        description="ROE recommendation",
    )
    rating_details_roa_score: int | None = Field(
        default=None,
        alias="ratingDetailsROAScore",
        description="Return on Assets score",
    )
    rating_details_roa_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsROARecommendation",
        description="ROA recommendation",
    )
    rating_details_de_score: int | None = Field(
        default=None, alias="ratingDetailsDEScore", description="Debt to Equity score"
    )
    rating_details_de_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsDERecommendation",
        description="D/E recommendation",
    )
    rating_details_pe_score: int | None = Field(
        default=None,
        alias="ratingDetailsPEScore",
        description="Price to Earnings score",
    )
    rating_details_pe_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsPERecommendation",
        description="P/E recommendation",
    )
    rating_details_pb_score: int | None = Field(
        default=None, alias="ratingDetailsPBScore", description="Price to Book score"
    )
    rating_details_pb_recommendation: str | None = Field(
        default=None,
        alias="ratingDetailsPBRecommendation",
        description="P/B recommendation",
    )


class PriceTargetNews(BaseModel):
    """Price target news article"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime = Field(
        alias="publishedDate", description="Publication date"
    )
    news_url: HttpUrl = Field(alias="newsURL", description="News article URL")
    news_title: str = Field(alias="newsTitle", description="News article title")
    analyst_name: str | None = Field(
        None, alias="analystName", description="Analyst name"
    )
    price_target: float = Field(alias="priceTarget", description="Price target")
    adj_price_target: float = Field(
        alias="adjPriceTarget", description="Adjusted price target"
    )
    price_when_posted: float = Field(
        alias="priceWhenPosted", description="Stock price when posted"
    )
    news_publisher: str = Field(alias="newsPublisher", description="News publisher")
    news_base_url: str = Field(alias="newsBaseURL", description="Publisher base URL")
    analyst_company: str = Field(alias="analystCompany", description="Analyst company")


class StockGrade(BaseModel):
    """Stock grade from analyst"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime | None = Field(
        default=None, alias="publishedDate", description="Publication date"
    )
    news_url: HttpUrl | None = Field(
        default=None, alias="newsURL", description="News article URL"
    )
    news_title: str | None = Field(
        default=None, alias="newsTitle", description="News article title"
    )
    news_base_url: str | None = Field(
        default=None, alias="newsBaseURL", description="Publisher base URL"
    )
    news_publisher: str | None = Field(
        default=None, alias="newsPublisher", description="News publisher"
    )
    new_grade: str = Field(alias="newGrade", description="New grade assigned")
    previous_grade: str | None = Field(
        None, alias="previousGrade", description="Previous grade"
    )
    grading_company: str = Field(
        alias="gradingCompany", description="Company issuing the grade"
    )
    action: str = Field(description="Action taken (upgrade, downgrade, etc.)")
    price_when_posted: Decimal | None = Field(
        default=None,
        alias="priceWhenPosted",
        description="Stock price when grade was posted",
    )


class HistoricalStockGrade(BaseModel):
    """Historical stock grade data"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime | None = Field(
        default=None, alias="publishedDate", description="Publication date"
    )
    news_url: HttpUrl | None = Field(
        default=None, alias="newsURL", description="News article URL"
    )
    news_title: str | None = Field(
        default=None, alias="newsTitle", description="News article title"
    )
    news_base_url: str | None = Field(
        default=None, alias="newsBaseURL", description="Publisher base URL"
    )
    news_publisher: str | None = Field(
        default=None, alias="newsPublisher", description="News publisher"
    )
    new_grade: str | None = Field(
        default=None, alias="newGrade", description="New grade assigned"
    )
    previous_grade: str | None = Field(
        None, alias="previousGrade", description="Previous grade"
    )
    grading_company: str | None = Field(
        default=None, alias="gradingCompany", description="Company issuing the grade"
    )
    action: str | None = Field(default=None, description="Action taken")
    price_when_posted: Decimal | None = Field(
        default=None,
        alias="priceWhenPosted",
        description="Stock price when grade was posted",
    )


class StockGradesConsensus(BaseModel):
    """Stock grades consensus summary"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    consensus: str = Field(description="Overall consensus rating")
    strong_buy: int = Field(
        alias="strongBuy", description="Number of strong buy ratings"
    )
    buy: int = Field(description="Number of buy ratings")
    hold: int = Field(description="Number of hold ratings")
    sell: int = Field(description="Number of sell ratings")
    strong_sell: int = Field(
        alias="strongSell", description="Number of strong sell ratings"
    )


class StockGradeNews(BaseModel):
    """Stock grade news article"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    published_date: datetime = Field(
        alias="publishedDate", description="Publication date"
    )
    news_url: HttpUrl = Field(alias="newsURL", description="News article URL")
    news_title: str = Field(alias="newsTitle", description="News article title")
    news_base_url: str = Field(alias="newsBaseURL", description="Publisher base URL")
    news_publisher: str = Field(alias="newsPublisher", description="News publisher")
    new_grade: str = Field(alias="newGrade", description="New grade assigned")
    previous_grade: str | None = Field(
        None, alias="previousGrade", description="Previous grade"
    )
    grading_company: str = Field(
        alias="gradingCompany", description="Company issuing the grade"
    )
    action: str = Field(description="Action taken")
    price_when_posted: Decimal = Field(
        alias="priceWhenPosted", description="Stock price when grade was posted"
    )
