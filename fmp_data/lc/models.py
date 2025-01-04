# fmp_langchain/models.py
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from fmp_data.models import Endpoint


class ToolType(str, Enum):
    """Type of tool/function"""

    FUNCTION = "function"
    RETRIEVAL = "retrieval"  # For future use
    ACTION = "action"  # For future use


class SemanticCategory(str, Enum):
    """Categories for semantic classification"""

    ALTERNATIVE_DATA = "Alternative Data"
    COMPANY_INFO = "Company Information"
    ECONOMIC = "Economic Data"
    FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
    INSTITUTIONAL = "Institutional Data"
    INTELLIGENCE = "Intelligence"
    INVESTMENT_PRODUCTS = "Investment Products"
    MARKET_DATA = "Market Data"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    UNKNOWN_CATEGORY = "Unknown Category"


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
    required: bool = Field(
        default=True, description="Whether this parameter is required"
    )
    schema_properties: dict | None = Field(
        default=None, description="Additional schema properties for specific providers"
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
    tool_type: ToolType = Field(
        default=ToolType.FUNCTION, description="Type of tool this endpoint represents"
    )
    natural_description: str = Field(
        description="Natural language description of what this endpoint does",
        max_length=150,  # To ensure descriptions work well with LLMs
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
    schema_format: Literal["openai", "anthropic", "standard"] = Field(
        default="standard", description="Format specification for parameter schema"
    )


class EndpointInfo(BaseModel):
    """Combined endpoint information"""

    endpoint: Endpoint
    semantics: EndpointSemantics
