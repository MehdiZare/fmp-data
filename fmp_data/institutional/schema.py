from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Form13FArgs(BaseModel):
    """Arguments for getting Form 13F data"""

    cik: str = Field(description="Institution CIK number")
    filing_date: date = Field(description="Filing date")


class Form13FDatesArgs(BaseModel):
    """Arguments for getting Form 13F filing dates"""

    cik: str = Field(description="Institution CIK number")


class AssetAllocationArgs(BaseModel):
    """Arguments for getting 13F asset allocation data"""

    filing_date: date = Field(description="Filing date")


class InstitutionalHoldingsArgs(BaseModel):
    """Arguments for getting institutional holdings"""

    symbol: str = Field(description="Stock symbol")
    include_current_quarter: bool = Field(
        default=False, description="Include current quarter data"
    )


class InsiderTradesArgs(BaseModel):
    """Arguments for getting insider trades"""

    symbol: str = Field(description="Stock symbol")
    page: int = Field(default=0, description="Page number")


class InsiderRosterArgs(BaseModel):
    """Arguments for getting insider roster"""

    symbol: str = Field(description="Stock symbol")


class InsiderStatisticsArgs(BaseModel):
    """Arguments for getting insider statistics"""

    symbol: str = Field(description="Stock symbol")


class CIKMapperArgs(BaseModel):
    """Arguments for getting CIK mappings"""

    page: int = Field(default=0, description="Page number")


class CIKMapperByNameArgs(BaseModel):
    """Arguments for searching CIK mappings by name"""

    name: str = Field(description="Name to search")
    page: int = Field(default=0, description="Page number")


class CIKMapperBySymbolArgs(BaseModel):
    """Arguments for getting CIK mapping by symbol"""

    symbol: str = Field(description="Stock symbol")


class BeneficialOwnershipArgs(BaseModel):
    """Arguments for getting beneficial ownership data"""

    symbol: str = Field(description="Stock symbol")


class FailToDeliverArgs(BaseModel):
    """Arguments for getting fail to deliver data"""

    symbol: str = Field(description="Stock symbol")
    page: int = Field(default=0, description="Page number")


class InsiderTransactionType(str, Enum):
    """Types of insider transactions"""

    PURCHASE = "P"
    SALE = "S"
    GRANT = "A"
    CONVERSION = "C"
    EXERCISE = "E"
    OTHER = "O"
