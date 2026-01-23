# fmp_data/index/models.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class IndexConstituent(BaseModel):
    """Index constituent information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    name: str | None = Field(None, description="Company name")
    sector: str | None = Field(None, description="Company sector")
    sub_sector: str | None = Field(None, alias="subSector", description="Sub-sector")
    headquarter: str | None = Field(None, description="Company headquarters")
    date_first_added: datetime | None = Field(
        None, alias="dateFirstAdded", description="Date added to index"
    )
    cik: str | None = Field(None, description="CIK number")
    founded: str | None = Field(None, description="Year founded")


class HistoricalIndexConstituent(BaseModel):
    """Historical index constituent change information"""

    model_config = default_model_config

    date: datetime = Field(description="Date of change")
    symbol: str | None = Field(None, description="Stock symbol")
    added_security: str | None = Field(
        None, alias="addedSecurity", description="Added security symbol"
    )
    removed_security: str | None = Field(
        None, alias="removedSecurity", description="Removed security symbol"
    )
    removed_ticker: str | None = Field(
        None, alias="removedTicker", description="Removed ticker symbol"
    )
    added_ticker: str | None = Field(
        None, alias="addedTicker", description="Added ticker symbol"
    )
    reason: str | None = Field(None, description="Reason for the change")
