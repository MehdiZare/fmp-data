# fmp_data/transcripts/models.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

default_model_config = ConfigDict(
    populate_by_name=True,
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="allow",
    alias_generator=to_camel,
)


class EarningsTranscript(BaseModel):
    """Earnings call transcript data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    quarter: int = Field(alias="period", description="Fiscal quarter (1-4)")
    year: int = Field(alias="fiscalYear", description="Fiscal year")
    date: datetime | None = Field(None, description="Earnings call date")
    content: str | None = Field(None, description="Full transcript content")

    @field_validator("quarter", mode="before")
    @classmethod
    def normalize_quarter(cls, value: int | str) -> int:
        if isinstance(value, str) and value.upper().startswith("Q"):
            return int(value[1:])
        return int(value)


class TranscriptDate(BaseModel):
    """Available transcript date information"""

    model_config = default_model_config

    symbol: str | None = Field(None, description="Stock symbol")
    quarter: int = Field(alias="period", description="Fiscal quarter (1-4)")
    year: int = Field(alias="fiscalYear", description="Fiscal year")
    date: datetime | None = Field(None, description="Earnings call date")

    @field_validator("quarter", mode="before")
    @classmethod
    def normalize_quarter(cls, value: int | str) -> int:
        if isinstance(value, str) and value.upper().startswith("Q"):
            return int(value[1:])
        return int(value)


class TranscriptSymbol(BaseModel):
    """Symbol with available transcripts"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    company_name: str | None = Field(
        None, alias="companyName", description="Company name"
    )
    no_of_transcripts: int | None = Field(
        None, alias="noOfTranscripts", description="Number of transcripts"
    )
