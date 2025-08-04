# fmp_data/institutional/models.py
from datetime import date, datetime
from typing import Any
import warnings

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class Form13F(BaseModel):
    """Individual holding in a 13F report"""

    model_config = default_model_config

    form_date: date = Field(description="Date of form", alias="date")
    filing_date: date = Field(alias="fillingDate", description="Filing date")
    accepted_date: date = Field(alias="acceptedDate", description="Accepted date")
    cik: str = Field(description="CIK number")
    cusip: str = Field(description="CUSIP number")
    ticker: str | None = Field(None, description="CUSIP of ticker", alias="tickercusip")
    company_name: str = Field(alias="nameOfIssuer", description="Name of issuer")
    shares: int = Field(description="Number of shares held")
    class_title: str = Field(alias="titleOfClass", description="Share class")
    value: float = Field(description="Market value of holding")
    link: str = Field(description="link to SEC report")
    link_final: str | None = Field(
        None, alias="linkFinal", description="Link to final SEC report"
    )


class Form13FDate(BaseModel):
    """Form 13F filing dates"""

    model_config = default_model_config

    form_date: date = Field(description="Date of form 13F filing", alias="date")

    @field_validator("form_date", mode="before")
    def validate_date(cls, value: Any) -> date | None:
        """
        Validate the date field. If validation fails, log a warning and return None.

        Args:
            value: The value to validate, can be date, string, or any other type

        Returns:
            date | None: Validated date object or None if validation fails

        Example:
            >>> "2023-01-01" -> date(2023, 1, 1)
            >>> "invalid" -> None  # with warning
            >>> None -> None
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                warnings.warn(
                    f"Invalid date format: {value}. "
                    f"Expected format: YYYY-MM-DD. Skipping this value.",
                    stacklevel=2,
                )
                return None
        warnings.warn(
            f"Unexpected type for date: {type(value)}. Skipping this value.",
            stacklevel=2,
        )
        return None


class AssetAllocation(BaseModel):
    """13F asset allocation data"""

    model_config = default_model_config

    allocation_date: date = Field(description="Allocation date", alias="date")
    cik: str = Field(description="Institution CIK")
    company_name: str = Field(alias="companyName", description="Institution name")
    asset_type: str = Field(alias="assetType", description="Type of asset")
    percentage: float = Field(description="Allocation percentage")
    current_quarter: bool = Field(
        alias="currentQuarter", description="Is current quarter"
    )


class InstitutionalHolder(BaseModel):
    """Institutional holder information"""

    model_config = default_model_config

    cik: str = Field(description="CIK number")
    name: str = Field(description="Institution name")


class InstitutionalHolding(BaseModel):
    """Institutional holding information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    report_date: date = Field(description="Report date", alias="date")
    investors_holding: int = Field(
        alias="investorsHolding", description="Number of investors holding"
    )
    last_investors_holding: int = Field(
        alias="lastInvestorsHolding", description="Previous number of investors"
    )
    investors_holding_change: int = Field(
        alias="investorsHoldingChange", description="Change in investor count"
    )
    number_of_13f_shares: int = Field(
        alias="numberOf13Fshares", description="Number of 13F shares"
    )
    last_number_of_13f_shares: int = Field(
        alias="lastNumberOf13Fshares", description="Previous number of 13F shares"
    )
    number_of_13f_shares_change: int = Field(
        alias="numberOf13FsharesChange", description="Change in 13F shares"
    )
    total_invested: float = Field(
        alias="totalInvested", description="Total invested amount"
    )
    last_total_invested: float = Field(
        alias="lastTotalInvested", description="Previous total invested"
    )
    total_invested_change: float = Field(
        alias="totalInvestedChange", description="Change in total invested"
    )
    ownership_percent: float = Field(
        alias="ownershipPercent", description="Ownership percentage"
    )
    last_ownership_percent: float = Field(
        alias="lastOwnershipPercent", description="Previous ownership percentage"
    )
    ownership_percent_change: float = Field(
        alias="ownershipPercentChange", description="Change in ownership percentage"
    )


class InsiderTransactionType(BaseModel):
    """Insider transaction type"""

    model_config = default_model_config

    code: str = Field(description="Transaction code")
    description: str = Field(description="Transaction description")
    is_acquisition: bool = Field(
        alias="isAcquisition", description="Whether transaction is an acquisition"
    )


class InsiderRoster(BaseModel):
    """Insider roster information"""

    model_config = default_model_config

    owner: str = Field(description="Insider name")
    transaction_date: date = Field(
        alias="transactionDate", description="Transaction date"
    )
    type_of_owner: str | None = Field(
        None, alias="typeOfOwner", description="Type of owner/position"
    )


class InsiderStatistic(BaseModel):
    """Insider trading statistics"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Year")
    quarter: int = Field(description="Quarter")
    purchases: int = Field(description="Number of purchases")
    sales: int = Field(description="Number of sales")
    buy_sell_ratio: float = Field(alias="buySellRatio", description="Buy/sell ratio")
    total_bought: int = Field(alias="totalBought", description="Total shares bought")
    total_sold: int = Field(alias="totalSold", description="Total shares sold")
    average_bought: float = Field(
        alias="averageBought", description="Average shares bought"
    )
    average_sold: float = Field(alias="averageSold", description="Average shares sold")
    p_purchases: int = Field(alias="pPurchases", description="P purchases")
    s_sales: int = Field(alias="sSales", description="S sales")


class InsiderTrade(BaseModel):
    """Insider trade information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    transaction_date: date = Field(alias="transactionDate", description="Trade date")
    reporting_cik: str = Field(alias="reportingCik", description="Reporting CIK")
    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    securities_owned: float | None = Field(
        None, alias="securitiesOwned", description="Securities owned"
    )
    company_cik: str = Field(alias="companyCik", description="Company CIK")
    reporting_name: str = Field(
        alias="reportingName", description="Reporting person name"
    )
    type_of_owner: str = Field(alias="typeOfOwner", description="Type of owner")
    acquisition_or_disposition: str = Field(
        alias="acquistionOrDisposition", description="A/D indicator"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(description="SEC filing link")


class CIKMapping(BaseModel):
    """CIK to name mapping information"""

    model_config = default_model_config

    reporting_cik: str = Field(alias="reportingCik", description="CIK number")
    reporting_name: str = Field(
        alias="reportingName", description="Individual or company name"
    )


class CIKCompanyMap(BaseModel):
    """CIK to company mapping information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number", alias="companyCik")


class BeneficialOwnership(BaseModel):
    """Beneficial ownership information"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    filing_date: datetime = Field(alias="filingDate", description="Filing date")
    accepted_ate: datetime = Field(alias="acceptedDate", description="Acceptance date")
    cusip: str = Field(description="CUSIP number")
    citizenship_place_org: str | None | None = Field(
        None,
        alias="citizenshipOrPlaceOfOrganization",
        description="Citizenship or place of organization",
    )
    sole_voting_power: float | None | None = Field(
        None, alias="soleVotingPower", description="Sole voting power"
    )
    shared_voting_power: float | None | None = Field(
        None, alias="sharedVotingPower", description="Shared voting power"
    )
    sole_dispositive_power: float | None | None = Field(
        None, alias="soleDispositivePower", description="Sole dispositive power"
    )
    shared_dispositive_power: float | None | None = Field(
        None, alias="sharedDispositivePower", description="Shared dispositive power"
    )
    amount_beneficially_owned: float = Field(
        alias="amountBeneficiallyOwned", description="Amount beneficially owned"
    )
    percent_of_class: float = Field(
        alias="percentOfClass", description="Percent of class"
    )
    type_of_reporting_person: str = Field(
        alias="typeOfReportingPerson", description="Type of reporting person"
    )
    url: str = Field(description="Name of reporting person")


class FailToDeliver(BaseModel):
    """Fail to deliver information"""

    model_config = default_model_config

    symbol: str = Field(description="Company symbol")
    fail_date: date = Field(description="Date of fail to deliver", alias="date")
    price: float = Field(description="Price per share")
    quantity: int = Field(description="Number of shares failed to deliver")
    cusip: str = Field(description="CUSIP identifier")
    name: str = Field(description="Company name")


class InsiderTradingLatest(BaseModel):
    """Latest insider trading information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    transaction_date: date = Field(alias="transactionDate", description="Trade date")
    reporting_cik: str = Field(alias="reportingCik", description="Reporting CIK")
    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    securities_owned: float | None = Field(
        None, alias="securitiesOwned", description="Securities owned"
    )
    company_cik: str = Field(alias="companyCik", description="Company CIK")
    reporting_name: str = Field(
        alias="reportingName", description="Reporting person name"
    )
    type_of_owner: str = Field(alias="typeOfOwner", description="Type of owner")
    acquisition_or_disposition: str = Field(
        alias="acquistionOrDisposition", description="A/D indicator"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(description="SEC filing link")


class InsiderTradingSearch(BaseModel):
    """Search results for insider trading"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    transaction_date: date = Field(alias="transactionDate", description="Trade date")
    reporting_cik: str = Field(alias="reportingCik", description="Reporting CIK")
    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    securities_owned: float | None = Field(
        None, alias="securitiesOwned", description="Securities owned"
    )
    company_cik: str = Field(alias="companyCik", description="Company CIK")
    reporting_name: str = Field(
        alias="reportingName", description="Reporting person name"
    )
    type_of_owner: str = Field(alias="typeOfOwner", description="Type of owner")
    acquisition_or_disposition: str = Field(
        alias="acquistionOrDisposition", description="A/D indicator"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(description="SEC filing link")


class InsiderTradingByName(BaseModel):
    """Insider trading by reporting name"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    filing_date: datetime = Field(alias="filingDate", description="SEC filing date")
    transaction_date: date = Field(alias="transactionDate", description="Trade date")
    reporting_cik: str = Field(alias="reportingCik", description="Reporting CIK")
    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    securities_owned: float | None = Field(
        None, alias="securitiesOwned", description="Securities owned"
    )
    company_cik: str = Field(alias="companyCik", description="Company CIK")
    reporting_name: str = Field(
        alias="reportingName", description="Reporting person name"
    )
    type_of_owner: str = Field(alias="typeOfOwner", description="Type of owner")
    acquisition_or_disposition: str = Field(
        alias="acquistionOrDisposition", description="A/D indicator"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(description="SEC filing link")


class InsiderTradingStatistics(BaseModel):
    """Enhanced insider trading statistics"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Year")
    quarter: int = Field(description="Quarter")
    purchases: int = Field(description="Number of purchases")
    sales: int = Field(description="Number of sales")
    buy_sell_ratio: float = Field(alias="buySellRatio", description="Buy/sell ratio")
    total_bought: int = Field(alias="totalBought", description="Total shares bought")
    total_sold: int = Field(alias="totalSold", description="Total shares sold")
    average_bought: float = Field(
        alias="averageBought", description="Average shares bought"
    )
    average_sold: float = Field(alias="averageSold", description="Average shares sold")
    p_purchases: int = Field(alias="pPurchases", description="P purchases")
    s_sales: int = Field(alias="sSales", description="S sales")


class InstitutionalOwnershipLatest(BaseModel):
    """Latest institutional ownership filings"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    filing_date: date = Field(description="Filing date", alias="date")
    symbol: str = Field(description="Stock symbol")
    company_name: str = Field(alias="companyName", description="Company name")
    shares: int = Field(description="Number of shares")
    value: float = Field(description="Market value")
    weight: float = Field(description="Portfolio weight")
    change: int = Field(description="Change in shares")
    change_percent: float = Field(
        alias="changePercent", description="Percentage change"
    )


class InstitutionalOwnershipExtract(BaseModel):
    """Filings extract information"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    filing_date: date = Field(description="Filing date", alias="date")
    name_of_issuer: str = Field(alias="nameOfIssuer", description="Issuer name")
    title_of_class: str = Field(alias="titleOfClass", description="Class title")
    cusip: str = Field(description="CUSIP number")
    value: float = Field(description="Market value")
    shares_prn_amt: int = Field(
        alias="sharesPrnAmt", description="Shares/principal amount"
    )
    shares_prn_type: str = Field(
        alias="sharesPrnType", description="Shares/principal type"
    )
    put_call: str | None = Field(
        None, alias="putCall", description="Put/call indicator"
    )
    investment_discretion: str = Field(
        alias="investmentDiscretion", description="Investment discretion"
    )
    other_manager: str | None = Field(
        None, alias="otherManager", description="Other manager"
    )
    voting_authority_sole: int | None = Field(
        None, alias="votingAuthoritySole", description="Sole voting authority"
    )
    voting_authority_shared: int | None = Field(
        None, alias="votingAuthorityShared", description="Shared voting authority"
    )
    voting_authority_none: int | None = Field(
        None, alias="votingAuthorityNone", description="No voting authority"
    )


class InstitutionalOwnershipDates(BaseModel):
    """Form 13F filing dates"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    filing_date: date = Field(description="Filing date", alias="date")


class InstitutionalOwnershipAnalytics(BaseModel):
    """Filings extract with analytics by holder"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    filing_date: date = Field(description="Filing date", alias="date")
    symbol: str = Field(description="Stock symbol")
    company_name: str = Field(alias="companyName", description="Company name")
    shares: int = Field(description="Number of shares")
    value: float = Field(description="Market value")
    weight: float = Field(description="Portfolio weight")
    change: int = Field(description="Change in shares")
    change_percent: float = Field(
        alias="changePercent", description="Percentage change"
    )
    market_value: float = Field(alias="marketValue", description="Total market value")
    avg_price_paid: float = Field(
        alias="avgPricePaid", description="Average price paid"
    )
    is_new: bool = Field(alias="isNew", description="Is new position")
    is_sold_out: bool = Field(alias="isSoldOut", description="Is sold out")


class HolderPerformanceSummary(BaseModel):
    """Holder performance summary"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    name: str = Field(description="Institution name")
    total_value: float = Field(alias="totalValue", description="Total portfolio value")
    entries: int = Field(description="Number of entries")
    change: float = Field(description="Total change")
    change_percent: float = Field(
        alias="changePercent", description="Percentage change"
    )


class HolderIndustryBreakdown(BaseModel):
    """Holders industry breakdown"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    industry: str = Field(description="Industry sector")
    value: float = Field(description="Total value in industry")
    weight: float = Field(description="Industry weight in portfolio")
    entries: int = Field(description="Number of positions")


class SymbolPositionsSummary(BaseModel):
    """Positions summary by symbol"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    total_positions: int = Field(
        alias="totalPositions", description="Total institutional positions"
    )
    total_shares: int = Field(alias="totalShares", description="Total shares held")
    total_value: float = Field(alias="totalValue", description="Total market value")
    avg_weight: float = Field(alias="avgWeight", description="Average portfolio weight")
    change: int = Field(description="Change in total shares")
    change_percent: float = Field(
        alias="changePercent", description="Percentage change"
    )


class IndustryPerformanceSummary(BaseModel):
    """Industry performance summary"""

    model_config = default_model_config

    industry: str = Field(description="Industry sector")
    total_value: float = Field(alias="totalValue", description="Total industry value")
    total_positions: int = Field(
        alias="totalPositions", description="Total positions in industry"
    )
    avg_weight: float = Field(alias="avgWeight", description="Average industry weight")
    change: float = Field(description="Total change")
    change_percent: float = Field(
        alias="changePercent", description="Percentage change"
    )
