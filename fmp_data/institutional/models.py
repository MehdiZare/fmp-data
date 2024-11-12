# fmp_data/institutional/models.py
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Form13FHolding(BaseModel):
    """Individual holding in a 13F report"""

    model_config = ConfigDict(populate_by_name=True)

    cusip: str = Field(description="CUSIP of security")
    ticker: str | None = Field(description="Ticker symbol if available")
    company_name: str = Field(alias="nameOfIssuer", description="Name of issuer")
    shares: int = Field(description="Number of shares held")
    value: Decimal = Field(description="Market value of holding")
    class_title: str = Field(alias="classTitle", description="Share class")
    investment_discretion: str = Field(
        alias="investmentDiscretion", description="Type of investment discretion"
    )
    sole_voting_authority: int | None = Field(
        alias="soleVotingAuthority", description="Sole voting authority shares"
    )
    shared_voting_authority: int | None = Field(
        alias="sharedVotingAuthority", description="Shared voting authority shares"
    )
    no_voting_authority: int | None = Field(
        alias="noVotingAuthority", description="No voting authority shares"
    )


class Form13F(BaseModel):
    """Form 13F filing data"""

    model_config = ConfigDict(populate_by_name=True)

    cik: str = Field(description="CIK number")
    filing_date: date = Field(alias="filingDate", description="Filing date")
    period_date: date = Field(alias="periodOfReport", description="Period end date")
    filing_type: str = Field(alias="form13FFileNumber", description="Filing type")
    holdings: list[Form13FHolding] = Field(description="List of holdings")
    total_value: Decimal = Field(
        alias="totalValue", description="Total portfolio value"
    )


class AssetAllocation(BaseModel):
    """13F asset allocation data"""

    model_config = ConfigDict(populate_by_name=True)

    allocation_date: date = Field(description="Allocation date", alias="date")
    cik: str = Field(description="Institution CIK")
    company_name: str = Field(alias="companyName", description="Institution name")
    asset_type: str = Field(alias="assetType", description="Type of asset")
    percentage: Decimal = Field(description="Allocation percentage")
    value: Decimal = Field(description="Asset value")
    current_quarter: bool = Field(
        alias="currentQuarter", description="Is current quarter"
    )


class InstitutionalHolder(BaseModel):
    """Institutional holder information"""

    model_config = ConfigDict(populate_by_name=True)

    cik: str = Field(description="CIK number")
    name: str = Field(description="Institution name")
    description: str | None = Field(description="Institution description")
    website: str | None = Field(description="Institution website")
    address: str | None = Field(description="Institution address")
    city: str | None = Field(description="Institution city")
    state: str | None = Field(description="Institution state")
    country: str | None = Field(description="Institution country")


class InstitutionalHolding(BaseModel):
    """Institutional holding information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    holder: str = Field(description="Institution name")
    shares: int = Field(description="Number of shares held")
    value: Decimal = Field(description="Holding value")
    weight_percentage: Decimal = Field(
        alias="weightPercentage", description="Portfolio weight percentage"
    )
    change: int = Field(description="Change in shares")
    change_percentage: Decimal = Field(
        alias="changePercentage", description="Change percentage"
    )
    date_reported: date = Field(alias="dateReported", description="Report date")


class InsiderTransactionType(BaseModel):
    """Insider transaction type"""

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(description="Transaction code")
    description: str = Field(description="Transaction description")
    is_acquisition: bool = Field(
        alias="isAcquisition", description="Whether transaction is an acquisition"
    )


class InsiderTrade(BaseModel):
    """Insider trade information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    insider_name: str = Field(alias="insiderName", description="Insider name")
    insider_title: str = Field(alias="insiderTitle", description="Insider title")
    transaction_date: date = Field(alias="transactionDate", description="Trade date")
    transaction_type: str = Field(
        alias="transactionType", description="Transaction type"
    )
    transaction_code: str = Field(
        alias="transactionCode", description="Transaction code"
    )
    shares: int = Field(description="Number of shares")
    share_price: Decimal = Field(alias="sharePrice", description="Price per share")
    value: Decimal = Field(description="Total transaction value")
    filing_date: date = Field(alias="filingDate", description="SEC filing date")


class InsiderRoster(BaseModel):
    """Insider roster information"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    name: str = Field(description="Insider name")
    title: str = Field(description="Insider title")
    total_holdings: int = Field(alias="totalHoldings", description="Total shares held")
    last_transaction_date: date = Field(
        alias="lastTransactionDate", description="Last transaction date"
    )
    last_transaction_filing_date: date = Field(
        alias="lastTransactionFilingDate", description="Last transaction filing date"
    )


class InsiderStatistic(BaseModel):
    """Insider trading statistics"""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(description="Stock symbol")
    total_transactions: int = Field(
        alias="totalTransactions", description="Total number of transactions"
    )
    total_bought: int = Field(alias="totalBought", description="Total shares bought")
    total_sold: int = Field(alias="totalSold", description="Total shares sold")
    net_transactions: int = Field(
        alias="netTransactions", description="Net transaction count"
    )
    last_transaction_date: date = Field(
        alias="lastTransactionDate", description="Last transaction date"
    )
