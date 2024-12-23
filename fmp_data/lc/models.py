# fmp_langchain/models.py
from enum import Enum

from pydantic import BaseModel, Field


class SemanticCategory(str, Enum):
    """Categories for semantic classification"""

    COMPANY_INFO = "Company Information"
    MARKET_DATA = "Market Data"
    ALTERNATIVE_DATA = "Alternative Data"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
    INSTITUTIONAL = "Institutional Data"
    ECONOMIC = "Economic Data"
    INVESTMENT_PRODUCTS = "Investment Products"


class ParameterHint(BaseModel):
    """Hints for parameter interpretation"""

    natural_names: list[str] = Field(
        description="Natural language names for this parameter"
    )
    extraction_patterns: list[str] = Field(
        description="Regex patterns to extract parameter values"
    )
    examples: list[str] = Field(description="Example values")
    context_clues: list[str] = Field(
        description="Words that indicate this parameter is being referenced"
    )


class ResponseFieldInfo(BaseModel):
    """Information about response fields"""

    description: str = Field(description="Human-readable description of the field")
    examples: list[str] = Field(description="Example values")
    related_terms: list[str] = Field(description="Related terms for this field")


class EndpointSemantics(BaseModel):
    """Semantic information for an endpoint"""

    client_name: str = Field(
        description="Name of the FMP client containing this endpoint"
    )
    method_name: str = Field(description="Method name in the client")
    natural_description: str = Field(
        description="Natural language description of what this endpoint does"
    )
    example_queries: list[str] = Field(
        description="Example natural language queries this endpoint can handle"
    )
    related_terms: list[str] = Field(description="Related terms for semantic matching")
    category: SemanticCategory = Field(description="Primary category of this endpoint")
    sub_category: str | None = Field(None, description="Optional sub-category")
    parameter_hints: dict[str, ParameterHint] = Field(
        description="Hints for parameter extraction"
    )
    response_hints: dict[str, ResponseFieldInfo] = Field(
        description="Information about response fields"
    )
    use_cases: list[str] = Field(description="Common use cases for this endpoint")
