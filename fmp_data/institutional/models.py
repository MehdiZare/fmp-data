# fmp_data/institutional/models.py
from datetime import date, datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
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
    filing_date: date = Field(alias="filingDate", description="Filing date")
    accepted_date: date = Field(alias="acceptedDate", description="Accepted date")
    cik: str = Field(description="CIK number")
    cusip: str = Field(alias="securityCusip", description="CUSIP number")
    symbol: str | None = Field(default=None, description="Ticker symbol")
    company_name: str = Field(alias="nameOfIssuer", description="Name of issuer")
    shares: int = Field(description="Number of shares held")
    class_title: str = Field(alias="titleOfClass", description="Share class")
    shares_type: str | None = Field(
        default=None, alias="sharesType", description="Shares type"
    )
    put_call_share: str | None = Field(
        default=None, alias="putCallShare", description="Put/call indicator"
    )
    value: float = Field(description="Market value of holding")
    link: str = Field(description="Link to SEC report")
    link_final: str | None = Field(
        default=None, alias="finalLink", description="Link to final SEC report"
    )


class Form13FDate(BaseModel):
    """Form 13F filing dates"""

    model_config = default_model_config

    form_date: date | None = Field(
        default=None, description="Date of form 13F filing", alias="date"
    )
    year: int | None = Field(default=None, description="Filing year")
    quarter: int | None = Field(default=None, description="Filing quarter")

    @field_validator("form_date", mode="before")
    def validate_date(cls, value: Any) -> date | None:
        """
        Validate the date field. Raises exceptions for invalid data to fail fast.

        Args:
            value: The value to validate, can be date, string, or any other type

        Returns:
            date | None: Validated date object or None for None input

        Raises:
            ValueError: If the date string format is invalid
            TypeError: If the value type is unexpected

        Example:
            >>> "2023-01-01" -> date(2023, 1, 1)
            >>> "invalid" -> raises ValueError
            >>> None -> None
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(
                    f"Invalid date format: {value}. Expected format: YYYY-MM-DD"
                ) from e
        raise TypeError(
            f"Unexpected type for date: {type(value).__name__}. "
            f"Expected str, date, or None"
        )


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

    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    code: str | None = Field(default=None, description="Transaction code")
    description: str | None = Field(default=None, description="Transaction description")
    is_acquisition: bool | None = Field(
        default=None,
        alias="isAcquisition",
        description="Whether transaction is an acquisition",
    )


class InsiderRoster(BaseModel):
    """Insider roster information"""

    model_config = default_model_config

    owner: str = Field(alias="reportingName", description="Insider name")
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
    acquired_transactions: int = Field(
        alias="acquiredTransactions", description="Number of acquired transactions"
    )
    disposed_transactions: int = Field(
        alias="disposedTransactions", description="Number of disposed transactions"
    )
    acquired_disposed_ratio: float = Field(
        alias="acquiredDisposedRatio", description="Acquired/disposed ratio"
    )
    total_acquired: int = Field(alias="totalAcquired", description="Total acquired")
    total_disposed: int = Field(alias="totalDisposed", description="Total disposed")
    average_acquired: float = Field(
        alias="averageAcquired", description="Average acquired"
    )
    average_disposed: float = Field(
        alias="averageDisposed", description="Average disposed"
    )
    total_purchases: int = Field(alias="totalPurchases", description="Total purchases")
    total_sales: int = Field(alias="totalSales", description="Total sales")


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
        validation_alias=AliasChoices(
            "acquisitionOrDisposition", "acquistionOrDisposition"
        ),
        description="A/D indicator",
    )
    direct_or_indirect: str | None = Field(
        default=None, alias="directOrIndirect", description="Direct/indirect"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(
        validation_alias=AliasChoices("url", "link"), description="SEC filing link"
    )


class CIKMapping(BaseModel):
    """CIK to name mapping information"""

    model_config = default_model_config

    reporting_cik: str = Field(
        validation_alias=AliasChoices("reportingCik", "cik"),
        description="CIK number",
    )
    reporting_name: str = Field(
        validation_alias=AliasChoices("reportingName", "companyName"),
        description="Individual or company name",
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
    accepted_date: datetime = Field(alias="acceptedDate", description="Acceptance date")
    cusip: str = Field(description="CUSIP number")
    citizenship_place_org: str | None = Field(
        None,
        alias="citizenshipOrPlaceOfOrganization",
        description="Citizenship or place of organization",
    )
    sole_voting_power: float | None = Field(
        None, alias="soleVotingPower", description="Sole voting power"
    )
    shared_voting_power: float | None = Field(
        None, alias="sharedVotingPower", description="Shared voting power"
    )
    sole_dispositive_power: float | None = Field(
        None, alias="soleDispositivePower", description="Sole dispositive power"
    )
    shared_dispositive_power: float | None = Field(
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
        validation_alias=AliasChoices(
            "acquisitionOrDisposition", "acquistionOrDisposition"
        ),
        description="A/D indicator",
    )
    direct_or_indirect: str | None = Field(
        default=None, alias="directOrIndirect", description="Direct/indirect"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(
        validation_alias=AliasChoices("url", "link"), description="SEC filing link"
    )


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
        validation_alias=AliasChoices(
            "acquisitionOrDisposition", "acquistionOrDisposition"
        ),
        description="A/D indicator",
    )
    direct_or_indirect: str | None = Field(
        default=None, alias="directOrIndirect", description="Direct/indirect"
    )
    form_type: str = Field(alias="formType", description="SEC form type")
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float = Field(description="Transaction price")
    security_name: str = Field(alias="securityName", description="Security name")
    link: str = Field(
        validation_alias=AliasChoices("url", "link"), description="SEC filing link"
    )


class InsiderTradingByName(BaseModel):
    """Insider trading by reporting name"""

    model_config = default_model_config

    reporting_cik: str = Field(alias="reportingCik", description="Reporting CIK")
    reporting_name: str = Field(
        alias="reportingName", description="Reporting person name"
    )
    symbol: str | None = Field(default=None, description="Stock symbol")
    filing_date: datetime | None = Field(
        default=None, alias="filingDate", description="SEC filing date"
    )
    transaction_date: date | None = Field(
        default=None, alias="transactionDate", description="Trade date"
    )
    transaction_type: str | None = Field(
        default=None, alias="transactionType", description="Transaction type"
    )
    securities_owned: float | None = Field(
        default=None, alias="securitiesOwned", description="Securities owned"
    )
    company_cik: str | None = Field(
        default=None, alias="companyCik", description="Company CIK"
    )
    type_of_owner: str | None = Field(
        default=None, alias="typeOfOwner", description="Type of owner"
    )
    acquisition_or_disposition: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "acquisitionOrDisposition", "acquistionOrDisposition"
        ),
        description="A/D indicator",
    )
    direct_or_indirect: str | None = Field(
        default=None, alias="directOrIndirect", description="Direct/indirect"
    )
    form_type: str | None = Field(
        default=None, alias="formType", description="SEC form type"
    )
    securities_transacted: float | None = Field(
        None, alias="securitiesTransacted", description="Securities transacted"
    )
    price: float | None = Field(default=None, description="Transaction price")
    security_name: str | None = Field(
        default=None, alias="securityName", description="Security name"
    )
    link: str | None = Field(
        default=None,
        validation_alias=AliasChoices("url", "link"),
        description="SEC filing link",
    )


class InsiderTradingStatistics(BaseModel):
    """Enhanced insider trading statistics"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str = Field(description="CIK number")
    year: int = Field(description="Year")
    quarter: int = Field(description="Quarter")
    acquired_transactions: int = Field(
        alias="acquiredTransactions", description="Number of acquired transactions"
    )
    disposed_transactions: int = Field(
        alias="disposedTransactions", description="Number of disposed transactions"
    )
    acquired_disposed_ratio: float = Field(
        alias="acquiredDisposedRatio", description="Acquired/disposed ratio"
    )
    total_acquired: int = Field(alias="totalAcquired", description="Total acquired")
    total_disposed: int = Field(alias="totalDisposed", description="Total disposed")
    average_acquired: float = Field(
        alias="averageAcquired", description="Average acquired"
    )
    average_disposed: float = Field(
        alias="averageDisposed", description="Average disposed"
    )
    total_purchases: int = Field(alias="totalPurchases", description="Total purchases")
    total_sales: int = Field(alias="totalSales", description="Total sales")


class InstitutionalOwnershipLatest(BaseModel):
    """Latest institutional ownership filings"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    name: str = Field(description="Institution name")
    report_date: date = Field(description="Portfolio date", alias="date")
    filing_date: datetime | None = Field(
        default=None, alias="filingDate", description="Filing date"
    )
    accepted_date: datetime | None = Field(
        default=None, alias="acceptedDate", description="Accepted date"
    )
    form_type: str | None = Field(
        default=None, alias="formType", description="Form type"
    )
    link: str | None = Field(default=None, description="SEC filing link")
    final_link: str | None = Field(
        default=None, alias="finalLink", description="Final SEC filing link"
    )


class InstitutionalOwnershipExtract(BaseModel):
    """Filings extract information"""

    model_config = default_model_config

    cik: str = Field(description="Institution CIK")
    report_date: date = Field(description="Report date", alias="date")
    filing_date: date | None = Field(
        default=None, alias="filingDate", description="Filing date"
    )
    accepted_date: date | None = Field(
        default=None, alias="acceptedDate", description="Accepted date"
    )
    security_cusip: str = Field(alias="securityCusip", description="Security CUSIP")
    symbol: str | None = Field(default=None, description="Symbol")
    name_of_issuer: str = Field(alias="nameOfIssuer", description="Issuer name")
    title_of_class: str = Field(alias="titleOfClass", description="Class title")
    shares: int = Field(description="Shares held")
    shares_type: str | None = Field(
        default=None, alias="sharesType", description="Shares type"
    )
    put_call_share: str | None = Field(
        default=None, alias="putCallShare", description="Put/call indicator"
    )
    value: float = Field(description="Market value")
    link: str = Field(description="SEC filing link")
    final_link: str | None = Field(
        default=None, alias="finalLink", description="Final SEC filing link"
    )


class InstitutionalOwnershipDates(BaseModel):
    """Form 13F filing dates"""

    model_config = default_model_config

    report_date: date = Field(description="Filing date", alias="date")
    year: int | None = Field(default=None, description="Filing year")
    quarter: int | None = Field(default=None, description="Filing quarter")


class InstitutionalOwnershipAnalytics(BaseModel):
    """Filings extract with analytics by holder"""

    model_config = default_model_config

    report_date: date = Field(description="Filing date", alias="date")
    cik: str = Field(description="Institution CIK")
    filing_date: date | None = Field(
        default=None, alias="filingDate", description="Filing date"
    )
    investor_name: str | None = Field(
        default=None, alias="investorName", description="Investor name"
    )
    symbol: str = Field(description="Stock symbol")
    security_name: str | None = Field(
        default=None, alias="securityName", description="Security name"
    )
    type_of_security: str | None = Field(
        default=None, alias="typeOfSecurity", description="Security type"
    )
    security_cusip: str | None = Field(
        default=None, alias="securityCusip", description="Security CUSIP"
    )
    shares_type: str | None = Field(
        default=None, alias="sharesType", description="Shares type"
    )
    put_call_share: str | None = Field(
        default=None, alias="putCallShare", description="Put/call indicator"
    )
    investment_discretion: str | None = Field(
        default=None,
        alias="investmentDiscretion",
        description="Investment discretion",
    )
    industry_title: str | None = Field(
        default=None, alias="industryTitle", description="Industry title"
    )
    weight: float | None = Field(default=None, description="Portfolio weight")
    last_weight: float | None = Field(
        default=None, alias="lastWeight", description="Previous weight"
    )
    change_in_weight: float | None = Field(
        default=None, alias="changeInWeight", description="Change in weight"
    )
    change_in_weight_percentage: float | None = Field(
        default=None,
        alias="changeInWeightPercentage",
        description="Change in weight percentage",
    )
    market_value: float | None = Field(
        default=None, alias="marketValue", description="Market value"
    )
    last_market_value: float | None = Field(
        default=None, alias="lastMarketValue", description="Previous market value"
    )
    change_in_market_value: float | None = Field(
        default=None,
        alias="changeInMarketValue",
        description="Change in market value",
    )
    change_in_market_value_percentage: float | None = Field(
        default=None,
        alias="changeInMarketValuePercentage",
        description="Change in market value percentage",
    )
    shares_number: int | None = Field(
        default=None, alias="sharesNumber", description="Shares number"
    )
    last_shares_number: int | None = Field(
        default=None, alias="lastSharesNumber", description="Previous shares number"
    )
    change_in_shares_number: int | None = Field(
        default=None,
        alias="changeInSharesNumber",
        description="Change in shares number",
    )
    change_in_shares_number_percentage: float | None = Field(
        default=None,
        alias="changeInSharesNumberPercentage",
        description="Change in shares number percentage",
    )
    quarter_end_price: float | None = Field(
        default=None, alias="quarterEndPrice", description="Quarter end price"
    )
    avg_price_paid: float | None = Field(
        default=None, alias="avgPricePaid", description="Average price paid"
    )
    is_new: bool | None = Field(default=None, alias="isNew", description="Is new")
    is_sold_out: bool | None = Field(
        default=None, alias="isSoldOut", description="Is sold out"
    )
    ownership: float | None = Field(default=None, description="Ownership")
    last_ownership: float | None = Field(
        default=None, alias="lastOwnership", description="Previous ownership"
    )
    change_in_ownership: float | None = Field(
        default=None, alias="changeInOwnership", description="Change in ownership"
    )
    change_in_ownership_percentage: float | None = Field(
        default=None,
        alias="changeInOwnershipPercentage",
        description="Change in ownership percentage",
    )
    holding_period: int | None = Field(
        default=None, alias="holdingPeriod", description="Holding period"
    )
    first_added: date | None = Field(
        default=None, alias="firstAdded", description="First added date"
    )
    performance: float | None = Field(default=None, description="Performance")
    performance_percentage: float | None = Field(
        default=None,
        alias="performancePercentage",
        description="Performance percentage",
    )
    last_performance: float | None = Field(
        default=None, alias="lastPerformance", description="Last performance"
    )
    change_in_performance: float | None = Field(
        default=None, alias="changeInPerformance", description="Change in performance"
    )
    is_counted_for_performance: bool | None = Field(
        default=None,
        alias="isCountedForPerformance",
        description="Counted for performance",
    )


class HolderPerformanceSummary(BaseModel):
    """Holder performance summary"""

    model_config = default_model_config

    report_date: date = Field(description="Filing date", alias="date")
    cik: str = Field(description="Institution CIK")
    investor_name: str = Field(alias="investorName", description="Institution name")
    portfolio_size: int = Field(alias="portfolioSize", description="Portfolio size")
    securities_added: int = Field(
        alias="securitiesAdded", description="Securities added"
    )
    securities_removed: int = Field(
        alias="securitiesRemoved", description="Securities removed"
    )
    market_value: float = Field(alias="marketValue", description="Market value")
    previous_market_value: float = Field(
        alias="previousMarketValue", description="Previous market value"
    )
    change_in_market_value: float = Field(
        alias="changeInMarketValue", description="Change in market value"
    )
    change_in_market_value_percentage: float = Field(
        alias="changeInMarketValuePercentage",
        description="Change in market value percentage",
    )
    average_holding_period: int = Field(
        alias="averageHoldingPeriod", description="Average holding period"
    )
    average_holding_period_top10: int = Field(
        alias="averageHoldingPeriodTop10",
        description="Average holding period top 10",
    )
    average_holding_period_top20: int = Field(
        alias="averageHoldingPeriodTop20",
        description="Average holding period top 20",
    )
    turnover: float = Field(description="Turnover")
    turnover_alternate_sell: float = Field(
        alias="turnoverAlternateSell", description="Turnover alternate sell"
    )
    turnover_alternate_buy: float = Field(
        alias="turnoverAlternateBuy", description="Turnover alternate buy"
    )
    performance: float = Field(description="Performance")
    performance_percentage: float = Field(
        alias="performancePercentage", description="Performance percentage"
    )
    last_performance: float = Field(
        alias="lastPerformance", description="Last performance"
    )
    change_in_performance: float = Field(
        alias="changeInPerformance", description="Change in performance"
    )
    performance_1year: float = Field(
        alias="performance1year", description="Performance 1 year"
    )
    performance_percentage_1year: float = Field(
        alias="performancePercentage1year",
        description="Performance percentage 1 year",
    )
    performance_3year: float = Field(
        alias="performance3year", description="Performance 3 year"
    )
    performance_percentage_3year: float = Field(
        alias="performancePercentage3year",
        description="Performance percentage 3 year",
    )
    performance_5year: float = Field(
        alias="performance5year", description="Performance 5 year"
    )
    performance_percentage_5year: float = Field(
        alias="performancePercentage5year",
        description="Performance percentage 5 year",
    )
    performance_since_inception: float = Field(
        alias="performanceSinceInception", description="Performance since inception"
    )
    performance_since_inception_percentage: float = Field(
        alias="performanceSinceInceptionPercentage",
        description="Performance since inception percentage",
    )
    performance_relative_to_sp500_percentage: float = Field(
        alias="performanceRelativeToSP500Percentage",
        description="Performance relative to S&P 500 percentage",
    )
    performance_1year_relative_to_sp500_percentage: float = Field(
        alias="performance1yearRelativeToSP500Percentage",
        description="Performance 1 year relative to S&P 500 percentage",
    )
    performance_3year_relative_to_sp500_percentage: float = Field(
        alias="performance3yearRelativeToSP500Percentage",
        description="Performance 3 year relative to S&P 500 percentage",
    )
    performance_5year_relative_to_sp500_percentage: float = Field(
        alias="performance5yearRelativeToSP500Percentage",
        description="Performance 5 year relative to S&P 500 percentage",
    )
    performance_since_inception_relative_to_sp500_percentage: float = Field(
        alias="performanceSinceInceptionRelativeToSP500Percentage",
        description="Performance since inception relative to S&P 500 percentage",
    )


class HolderIndustryBreakdown(BaseModel):
    """Holders industry breakdown"""

    model_config = default_model_config

    report_date: date = Field(description="Filing date", alias="date")
    cik: str = Field(description="Institution CIK")
    investor_name: str = Field(alias="investorName", description="Investor name")
    industry_title: str = Field(alias="industryTitle", description="Industry title")
    weight: float = Field(description="Industry weight in portfolio")
    last_weight: float | None = Field(
        default=None, alias="lastWeight", description="Previous weight"
    )
    change_in_weight: float | None = Field(
        default=None, alias="changeInWeight", description="Change in weight"
    )
    change_in_weight_percentage: float | None = Field(
        default=None,
        alias="changeInWeightPercentage",
        description="Change in weight percentage",
    )
    performance: float | None = Field(default=None, description="Performance")
    performance_percentage: float | None = Field(
        default=None,
        alias="performancePercentage",
        description="Performance percentage",
    )
    last_performance: float | None = Field(
        default=None, alias="lastPerformance", description="Last performance"
    )
    change_in_performance: float | None = Field(
        default=None, alias="changeInPerformance", description="Change in performance"
    )


class SymbolPositionsSummary(BaseModel):
    """Positions summary by symbol"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    cik: str | None = Field(default=None, description="Company CIK")
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
    new_positions: int | None = Field(
        default=None, alias="newPositions", description="New positions"
    )
    last_new_positions: int | None = Field(
        default=None, alias="lastNewPositions", description="Previous new positions"
    )
    new_positions_change: int | None = Field(
        default=None, alias="newPositionsChange", description="Change in new positions"
    )
    increased_positions: int | None = Field(
        default=None, alias="increasedPositions", description="Increased positions"
    )
    last_increased_positions: int | None = Field(
        default=None,
        alias="lastIncreasedPositions",
        description="Previous increased positions",
    )
    increased_positions_change: int | None = Field(
        default=None,
        alias="increasedPositionsChange",
        description="Change in increased positions",
    )
    closed_positions: int | None = Field(
        default=None, alias="closedPositions", description="Closed positions"
    )
    last_closed_positions: int | None = Field(
        default=None,
        alias="lastClosedPositions",
        description="Previous closed positions",
    )
    closed_positions_change: int | None = Field(
        default=None,
        alias="closedPositionsChange",
        description="Change in closed positions",
    )
    reduced_positions: int | None = Field(
        default=None, alias="reducedPositions", description="Reduced positions"
    )
    last_reduced_positions: int | None = Field(
        default=None,
        alias="lastReducedPositions",
        description="Previous reduced positions",
    )
    reduced_positions_change: int | None = Field(
        default=None,
        alias="reducedPositionsChange",
        description="Change in reduced positions",
    )
    total_calls: int | None = Field(
        default=None, alias="totalCalls", description="Total calls"
    )
    last_total_calls: int | None = Field(
        default=None, alias="lastTotalCalls", description="Previous total calls"
    )
    total_calls_change: int | None = Field(
        default=None, alias="totalCallsChange", description="Change in calls"
    )
    total_puts: int | None = Field(
        default=None, alias="totalPuts", description="Total puts"
    )
    last_total_puts: int | None = Field(
        default=None, alias="lastTotalPuts", description="Previous total puts"
    )
    total_puts_change: int | None = Field(
        default=None, alias="totalPutsChange", description="Change in puts"
    )
    put_call_ratio: float | None = Field(
        default=None, alias="putCallRatio", description="Put/call ratio"
    )
    last_put_call_ratio: float | None = Field(
        default=None,
        alias="lastPutCallRatio",
        description="Previous put/call ratio",
    )
    put_call_ratio_change: float | None = Field(
        default=None,
        alias="putCallRatioChange",
        description="Change in put/call ratio",
    )


class IndustryPerformanceSummary(BaseModel):
    """Industry performance summary"""

    model_config = default_model_config

    industry_title: str = Field(alias="industryTitle", description="Industry sector")
    industry_value: float = Field(
        alias="industryValue", description="Total industry value"
    )
    report_date: date = Field(description="Report date", alias="date")
