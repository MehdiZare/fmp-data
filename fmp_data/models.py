# fmp_data/models.py
"""Data models for FMP client."""
from datetime import datetime

from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    """Company profile model."""

    symbol: str
    company_name: str = Field(alias="companyName")
    currency: str
    exchange: str
    industry: str | None = None
    website: str | None = None
    description: str | None = None
    ceo: str | None = None
    sector: str | None = None
    country: str | None = None
    employees: int | None = Field(None, alias="fullTimeEmployees")
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = Field(None, alias="zip")
    price: float | None = None
    beta: float | None = None
    volume_avg: int | None = Field(None, alias="volAvg")
    market_cap: float | None = Field(None, alias="mktCap")
    last_dividend: float | None = Field(None, alias="lastDiv")
    range: str | None = None
    changes: float | None = None
    dcf_diff: float | None = Field(None, alias="dcfDiff")
    dcf: float | None = None
    ipo_date: datetime | None = Field(None, alias="ipoDate")


class IncomeStatement(BaseModel):
    """Income statement model."""

    date: str
    symbol: str
    revenue: float
    gross_profit: float = Field(alias="grossProfit")
    operating_income: float = Field(alias="operatingIncome")
    net_income: float = Field(alias="netIncome")
    eps: float = Field(alias="eps")
