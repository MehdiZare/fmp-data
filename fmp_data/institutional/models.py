# fmp_data/institutional/models.py
import warnings
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Form13F(BaseModel):
    """Individual holding in a 13F report"""

    model_config = ConfigDict(populate_by_name=True)

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

    form_date: date = Field(description="Date of form 13F filing", alias="date")

    @field_validator("form_date", mode="before")
    def validate_date(cls, value):
        """
        Validate the date field. If validation fails, log a warning and return None.
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

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    cik: str = Field(description="CIK number")
    name: str = Field(description="Institution name")


class InstitutionalHolding(BaseModel):
    """Institutional holding information"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(description="Transaction code")
    description: str = Field(description="Transaction description")
    is_acquisition: bool = Field(
        alias="isAcquisition", description="Whether transaction is an acquisition"
    )


class InsiderRoster(BaseModel):
    """Insider roster information"""

    model_config = ConfigDict(populate_by_name=True)

    owner: str = Field(description="Insider name")
    transaction_date: date = Field(
        alias="transactionDate", description="Transaction date"
    )
    type_of_owner: str | None = Field(
        None, alias="typeOfOwner", description="Type of owner/position"
    )


class InsiderStatistic(BaseModel):
    """Insider trading statistics"""

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(populate_by_name=True)

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
