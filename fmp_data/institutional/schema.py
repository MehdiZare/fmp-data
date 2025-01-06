# fmp_data/institutional/schema.py

from datetime import date

from pydantic import Field

from fmp_data.schema import BaseArgModel, BaseEnum, PaginationArg, SymbolArg


class InsiderTransactionType(BaseEnum):
    """Types of insider transactions"""

    PURCHASE = "P"
    SALE = "S"
    GRANT = "A"
    CONVERSION = "C"
    EXERCISE = "E"
    OTHER = "O"


class Form13FArgs(BaseArgModel):
    """Arguments for getting Form 13F data"""

    cik: str = Field(
        description="Institution CIK number",
        pattern=r"^\d{10}$",
        json_schema_extra={"examples": ["0001234567"]},
    )
    filing_date: date = Field(
        description="Filing date", json_schema_extra={"examples": ["2024-01-15"]}
    )


class Form13FDatesArgs(BaseArgModel):
    """Arguments for getting Form 13F filing dates"""

    cik: str = Field(description="Institution CIK number", pattern=r"^\d{10}$")


class AssetAllocationArgs(BaseArgModel):
    """Arguments for getting 13F asset allocation data"""

    filing_date: date = Field(description="Filing date")


class InstitutionalHoldingsArgs(SymbolArg):
    """Arguments for getting institutional holdings"""

    include_current_quarter: bool = Field(
        default=False, description="Include current quarter data"
    )


class InsiderTradesArgs(SymbolArg, PaginationArg):
    """Arguments for getting insider trades"""

    pass


class InsiderRosterArgs(SymbolArg):
    """Arguments for getting insider roster"""

    pass


class InsiderStatisticsArgs(SymbolArg):
    """Arguments for getting insider statistics"""

    pass


class CIKMapperArgs(PaginationArg):
    """Arguments for getting CIK mappings"""

    pass


class CIKMapperByNameArgs(PaginationArg):
    """Arguments for searching CIK mappings by name"""

    name: str = Field(description="Name to search", min_length=2)


class CIKMapperBySymbolArgs(SymbolArg):
    """Arguments for getting CIK mapping by symbol"""

    pass


class BeneficialOwnershipArgs(SymbolArg):
    """Arguments for getting beneficial ownership data"""

    pass


class FailToDeliverArgs(SymbolArg, PaginationArg):
    """Arguments for getting fail to deliver data"""

    pass
