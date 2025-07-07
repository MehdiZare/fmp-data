from fmp_data.company.schema import IntradayTimeInterval
from fmp_data.lc.models import ParameterHint, ResponseFieldInfo

STRUCTURE_HINT = ParameterHint(
    natural_names=["structure", "format", "data format"],
    extraction_patterns=[r"\b(flat|nested)\b"],
    examples=["flat", "nested"],
    context_clues=["structure", "format", "organize", "arrangement"],
)

# Common response field hints
PROFILE_RESPONSE_HINTS = {
    "price": ResponseFieldInfo(
        description="Current stock price",
        examples=["150.25", "3500.00"],
        related_terms=["stock price", "trading price", "share price", "current price"],
    ),
    "market_cap": ResponseFieldInfo(
        description="Company's market capitalization",
        examples=["2.5T", "800B"],
        related_terms=["market value", "company worth", "capitalization", "market cap"],
    ),
    "beta": ResponseFieldInfo(
        description="Stock's beta value (market correlation)",
        examples=["1.2", "0.8"],
        related_terms=["volatility", "market correlation", "risk measure"],
    ),
}

FINANCIAL_RESPONSE_HINTS = {
    "revenue": ResponseFieldInfo(
        description="Company's revenue/sales",
        examples=["$365.8B", "$115.5M"],
        related_terms=["sales", "income", "earnings", "top line"],
    ),
    "employees": ResponseFieldInfo(
        description="Number of employees",
        examples=["164,000", "25,000"],
        related_terms=["workforce", "staff", "personnel", "headcount"],
    ),
}

EXECUTIVE_RESPONSE_HINTS = {
    "name": ResponseFieldInfo(
        description="Executive's name",
        examples=["Tim Cook", "Satya Nadella"],
        related_terms=["CEO", "executive", "officer", "management"],
    ),
    "compensation": ResponseFieldInfo(
        description="Executive compensation",
        examples=["$15.7M", "$40.2M"],
        related_terms=["salary", "pay", "remuneration", "earnings"],
    ),
}

FLOAT_RESPONSE_HINTS = {
    "float_shares": ResponseFieldInfo(
        description="Number of shares available for trading",
        examples=["5.2B", "750M"],
        related_terms=["floating shares", "tradable shares", "public float"],
    ),
    "float_percentage": ResponseFieldInfo(
        description="Percentage of shares available for trading",
        examples=["85.5%", "45.2%"],
        related_terms=["float ratio", "public float percentage", "tradable ratio"],
    ),
}

INTERVAL_HINT = ParameterHint(
    natural_names=["interval", "timeframe", "period"],
    extraction_patterns=[
        r"(?i)(\d+)\s*(?:min|minute|hour|hr)",
        r"(?i)(one|five|fifteen|thirty)\s*(?:min|minute|hour|hr)",
    ],
    examples=list(IntradayTimeInterval),
    context_clues=["interval", "timeframe", "period", "frequency"],
)
