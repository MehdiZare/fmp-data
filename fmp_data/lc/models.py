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


# fmp_langchain/endpoints/alternative.py

ALTERNATIVE_ENDPOINTS = {
    "crypto_list": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_list",
        natural_description=(
            "Get a list of all available cryptocurrencies " "that can be queried"
        ),
        example_queries=[
            "What cryptocurrencies are available?",
            "Show me the list of supported crypto pairs",
            "What crypto symbols can I look up?",
        ],
        related_terms=[
            "cryptocurrency",
            "crypto",
            "digital assets",
            "tokens",
            "available pairs",
            "trading pairs",
            "crypto symbols",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={},  # No parameters for this endpoint
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Trading symbol for the cryptocurrency pair",
                examples=["BTCUSD", "ETHUSD"],
                related_terms=["trading pair", "crypto symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Full name of the cryptocurrency",
                examples=["Bitcoin", "Ethereum"],
                related_terms=["crypto name", "currency name"],
            ),
        },
        use_cases=[
            "Finding available cryptocurrencies to analyze",
            "Looking up crypto trading pairs",
            "Discovering supported digital assets",
        ],
    ),
    "crypto_quotes": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_quotes",
        natural_description="Get current price quotes for cryptocurrencies",
        example_queries=[
            "What's the current Bitcoin price?",
            "Show me crypto prices",
            "Get cryptocurrency quotes",
            "What's the price of ETH?",
        ],
        related_terms=[
            "crypto price",
            "cryptocurrency value",
            "token price",
            "digital asset price",
            "crypto quotes",
            "current price",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={
            "symbol": ParameterHint(
                natural_names=["cryptocurrency", "crypto", "token"],
                extraction_patterns=[r"\b[A-Z]{3,4}USD\b", r"\b(BTC|ETH|XRP)\b"],
                examples=["BTCUSD", "ETHUSD"],
                context_clues=["price of", "value of", "quote for"],
            )
        },
        response_hints={
            "price": ResponseFieldInfo(
                description="Current trading price of the cryptocurrency",
                examples=["45000.50", "1800.75"],
                related_terms=["current price", "trading price", "value"],
            ),
            "change": ResponseFieldInfo(
                description="Price change from previous close",
                examples=["+1500", "-200"],
                related_terms=["price change", "movement", "difference"],
            ),
        },
        use_cases=[
            "Checking current crypto prices",
            "Monitoring cryptocurrency markets",
            "Tracking digital asset values",
        ],
    ),
}
