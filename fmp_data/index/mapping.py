# fmp_data/index/mapping.py
from __future__ import annotations

from fmp_data.index.endpoints import (
    DOWJONES_CONSTITUENTS,
    HISTORICAL_DOWJONES,
    HISTORICAL_NASDAQ,
    HISTORICAL_SP500,
    NASDAQ_CONSTITUENTS,
    SP500_CONSTITUENTS,
)
from fmp_data.lc.models import EndpointSemantics, SemanticCategory

# Index endpoints mapping
INDEX_ENDPOINT_MAP = {
    "get_sp500_constituents": SP500_CONSTITUENTS,
    "get_nasdaq_constituents": NASDAQ_CONSTITUENTS,
    "get_dowjones_constituents": DOWJONES_CONSTITUENTS,
    "get_historical_sp500": HISTORICAL_SP500,
    "get_historical_nasdaq": HISTORICAL_NASDAQ,
    "get_historical_dowjones": HISTORICAL_DOWJONES,
}

# Complete semantic definitions for all endpoints
INDEX_ENDPOINTS_SEMANTICS = {
    "sp500_constituents": EndpointSemantics(
        client_name="index",
        method_name="get_sp500_constituents",
        natural_description=(
            "Get current S&P 500 index constituents. "
            "Returns list of companies currently included in the S&P 500 index."
        ),
        example_queries=[
            "Get S&P 500 constituents",
            "List companies in the S&P 500",
            "What stocks are in the S&P 500?",
            "Show me S&P 500 members",
            "S&P 500 component companies",
        ],
        related_terms=[
            "S&P 500",
            "SPX",
            "index constituents",
            "index members",
            "S&P components",
            "large cap index",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "nasdaq_constituents": EndpointSemantics(
        client_name="index",
        method_name="get_nasdaq_constituents",
        natural_description=(
            "Get current NASDAQ index constituents. "
            "Returns companies currently in the NASDAQ composite index."
        ),
        example_queries=[
            "Get NASDAQ constituents",
            "List companies in NASDAQ",
            "What stocks are in the NASDAQ index?",
            "Show me NASDAQ members",
            "NASDAQ component companies",
        ],
        related_terms=[
            "NASDAQ",
            "NASDAQ composite",
            "tech index",
            "index constituents",
            "index members",
            "NASDAQ components",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "dowjones_constituents": EndpointSemantics(
        client_name="index",
        method_name="get_dowjones_constituents",
        natural_description=(
            "Get current Dow Jones Industrial Average constituents. "
            "Returns list of 30 companies currently included in the DJIA."
        ),
        example_queries=[
            "Get Dow Jones constituents",
            "List Dow 30 companies",
            "What stocks are in the Dow Jones?",
            "Show me DJIA members",
            "Dow Jones Industrial Average components",
        ],
        related_terms=[
            "Dow Jones",
            "DJIA",
            "Dow 30",
            "blue chip stocks",
            "index constituents",
            "Dow components",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "historical_sp500": EndpointSemantics(
        client_name="index",
        method_name="get_historical_sp500",
        natural_description=(
            "Get historical S&P 500 constituent changes. "
            "Returns list of additions and removals from the S&P 500 over time."
        ),
        example_queries=[
            "Get S&P 500 historical changes",
            "Show me S&P 500 additions and removals",
            "Historical S&P 500 constituent changes",
            "When was Tesla added to S&P 500?",
            "S&P 500 index rebalancing history",
        ],
        related_terms=[
            "index changes",
            "index rebalancing",
            "constituent additions",
            "constituent removals",
            "S&P 500 history",
            "index composition changes",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "historical_nasdaq": EndpointSemantics(
        client_name="index",
        method_name="get_historical_nasdaq",
        natural_description=(
            "Get historical NASDAQ constituent changes. "
            "Returns list of additions and removals from the NASDAQ index over time."
        ),
        example_queries=[
            "Get NASDAQ historical changes",
            "Show me NASDAQ additions and removals",
            "Historical NASDAQ constituent changes",
            "NASDAQ index rebalancing history",
            "Track NASDAQ composition changes",
        ],
        related_terms=[
            "index changes",
            "index rebalancing",
            "constituent additions",
            "constituent removals",
            "NASDAQ history",
            "index composition changes",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
    "historical_dowjones": EndpointSemantics(
        client_name="index",
        method_name="get_historical_dowjones",
        natural_description=(
            "Get historical Dow Jones constituent changes. "
            "Returns list of additions and removals from the DJIA over time."
        ),
        example_queries=[
            "Get Dow Jones historical changes",
            "Show me Dow 30 additions and removals",
            "Historical DJIA constituent changes",
            "Dow Jones index rebalancing history",
            "Track Dow component changes",
        ],
        related_terms=[
            "index changes",
            "index rebalancing",
            "constituent additions",
            "constituent removals",
            "Dow Jones history",
            "DJIA composition changes",
        ],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={},
        response_hints={},
        use_cases=["Financial analysis", "Investment research"],
    ),
}
