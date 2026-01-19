# fmp_data/transcripts/models.py
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


class EarningsTranscript(BaseModel):
    """Earnings call transcript data"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    quarter: int = Field(description="Fiscal quarter (1-4)")
    year: int = Field(description="Fiscal year")
    date: datetime | None = Field(None, description="Earnings call date")
    content: str | None = Field(None, description="Full transcript content")


class TranscriptDate(BaseModel):
    """Available transcript date information"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
    quarter: int = Field(description="Fiscal quarter (1-4)")
    year: int = Field(description="Fiscal year")
    date: datetime | None = Field(None, description="Earnings call date")


class TranscriptSymbol(BaseModel):
    """Symbol with available transcripts"""

    model_config = default_model_config

    symbol: str = Field(description="Stock symbol")
