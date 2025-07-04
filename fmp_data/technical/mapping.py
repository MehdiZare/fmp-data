from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)
from fmp_data.technical.endpoints import TECHNICAL_INDICATOR

# Common parameter hints
SYMBOL_HINT = ParameterHint(
    natural_names=["symbol", "ticker", "stock"],
    extraction_patterns=[
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"\b[A-Z]{1,5}\b",
    ],
    examples=["AAPL", "MSFT", "GOOGL"],
    context_clues=["stock", "symbol", "ticker", "company"],
)

TYPE_HINT = ParameterHint(
    natural_names=["type", "indicator", "calculation"],
    extraction_patterns=[
        r"(sma|ema|wma|dema|tema|williams|rsi|adx|standardDeviation)",
    ],
    examples=["sma", "ema", "rsi"],
    context_clues=["type", "indicator", "method"],
)

PERIOD_HINT = ParameterHint(
    natural_names=["period", "timeframe", "lookback"],
    extraction_patterns=[
        r"(\d+)[-\s]?(?:day|period)",
        r"(?:period|timeframe)\s+of\s+(\d+)",
    ],
    examples=["14", "20", "50", "200"],
    context_clues=["period", "days", "lookback", "window"],
)

INTERVAL_HINT = ParameterHint(
    natural_names=["interval", "timeframe", "frequency"],
    extraction_patterns=[
        r"(1min|5min|15min|30min|1hour|4hour|daily)",
        r"(\d+)[\s-]?(?:minute|min|hour|day)",
    ],
    examples=["1min", "5min", "15min", "30min", "1hour", "4hour", "daily"],
    context_clues=["interval", "frequency", "period", "timeframe"],
)

FROM_DATE_HINT = ParameterHint(
    natural_names=["from date", "start date", "beginning"],
    extraction_patterns=[
        r"from\s+(\d{4}-\d{2}-\d{2})",
        r"starting\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-01-01", "2023-12-01"],
    context_clues=["from", "start", "beginning", "since"],
)

TO_DATE_HINT = ParameterHint(
    natural_names=["to date", "end date", "until"],
    extraction_patterns=[
        r"to\s+(\d{4}-\d{2}-\d{2})",
        r"until\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-12-31", "2023-12-31"],
    context_clues=["to", "end", "until", "through"],
)

# Common parameter hints dictionary
COMMON_PARAMS = {
    "symbol": SYMBOL_HINT,
    "type": TYPE_HINT,
    "period": PERIOD_HINT,
    "interval": INTERVAL_HINT,
    "start_date": FROM_DATE_HINT,
    "end_date": TO_DATE_HINT,
}

# Define each technical indicator explicitly
TECHNICAL_ENDPOINTS_SEMANTICS = {
    "sma": EndpointSemantics(
        client_name="technical",
        method_name="get_sma",
        natural_description=(
            "Calculate Simple Moving Average (SMA) for a given security."
        ),
        example_queries=[
            "Calculate 50-day SMA for AAPL",
            "Get daily SMA(20) for MSFT from 2024-01-01 to 2024-12-31",
            "Show 200-day moving average for GOOGL",
            "What's the 10-day SMA for TSLA?",
        ],
        related_terms=[
            "moving average",
            "trend indicator",
            "price average",
            "smoothing",
            "trend analysis",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "sma": ResponseFieldInfo(
                description="Simple Moving Average value",
                examples=["150.75", "3505.50"],
                related_terms=["moving average", "average price", "MA"],
            ),
        },
        use_cases=[
            "Trend identification",
            "Support/resistance levels",
            "Price smoothing",
            "Trading signals generation",
        ],
    ),
    "ema": EndpointSemantics(
        client_name="technical",
        method_name="get_ema",
        natural_description=(
            "Calculate Exponential Moving Average (EMA) for a security."
        ),
        example_queries=[
            "Calculate 20-day EMA for AAPL",
            "Get exponential moving average(50) for MSFT",
            "Show 12-day EMA for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the 26-day EMA for TSLA?",
        ],
        related_terms=[
            "exponential average",
            "weighted moving average",
            "trend indicator",
            "price average",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "ema": ResponseFieldInfo(
                description="Exponential Moving Average value",
                examples=["151.25", "3508.75"],
                related_terms=["exponential average", "weighted average", "EMA"],
            ),
        },
        use_cases=[
            "Trend following",
            "Price momentum analysis",
            "Trading signal generation",
            "Market timing",
        ],
    ),
    "wma": EndpointSemantics(
        client_name="technical",
        method_name="get_wma",
        natural_description=("Calculate Weighted Moving Average (WMA)."),
        example_queries=[
            "Calculate WMA for AAPL",
            "Get weighted moving average for MSFT",
            "Show 10-day WMA for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the 20-day WMA for TSLA?",
        ],
        related_terms=[
            "weighted average",
            "moving average",
            "trend indicator",
            "price weighting",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "wma": ResponseFieldInfo(
                description="Weighted Moving Average value",
                examples=["152.50", "3515.25"],
                related_terms=["weighted average", "moving average", "WMA"],
            ),
        },
        use_cases=[
            "Trend analysis",
            "Price momentum tracking",
            "Technical trading",
            "Market analysis",
        ],
    ),
    "dema": EndpointSemantics(
        client_name="technical",
        method_name="get_dema",
        natural_description=("Calculate Double Exponential Moving Average (DEMA)."),
        example_queries=[
            "Calculate DEMA for AAPL",
            "Get double exponential average for MSFT",
            "Show 10-day DEMA for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the 20-day DEMA for TSLA?",
        ],
        related_terms=[
            "double exponential",
            "moving average",
            "trend indicator",
            "lag reduction",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "dema": ResponseFieldInfo(
                description="Double Exponential Moving Average value",
                examples=["153.75", "3520.50"],
                related_terms=["double exponential", "moving average", "DEMA"],
            ),
        },
        use_cases=[
            "Trend analysis",
            "Reduced lag indicators",
            "Technical trading",
            "Quick trend detection",
        ],
    ),
    "tema": EndpointSemantics(
        client_name="technical",
        method_name="get_tema",
        natural_description=("Calculate Triple Exponential Moving Average (TEMA)."),
        example_queries=[
            "Calculate TEMA for AAPL",
            "Get triple exponential average for MSFT",
            "Show 10-day TEMA for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the 20-day TEMA for TSLA?",
        ],
        related_terms=[
            "triple exponential",
            "moving average",
            "trend indicator",
            "lag reduction",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "tema": ResponseFieldInfo(
                description="Triple Exponential Moving Average value",
                examples=["154.25", "3525.75"],
                related_terms=["triple exponential", "moving average", "TEMA"],
            ),
        },
        use_cases=[
            "Trend analysis",
            "Minimal lag indicators",
            "Technical trading",
            "Rapid trend detection",
        ],
    ),
    "williams": EndpointSemantics(
        client_name="technical",
        method_name="get_williams",
        natural_description=(
            "Calculate Williams %R indicator. This momentum indicator measures "
            "overbought and oversold levels."
        ),
        example_queries=[
            "Calculate Williams %R for AAPL",
            "Get Williams indicator for MSFT",
            "Show 14-day Williams %R for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the overbought/oversold level for TSLA?",
        ],
        related_terms=[
            "williams percent r",
            "momentum indicator",
            "overbought/oversold",
            "price momentum",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Momentum Indicators",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "williams": ResponseFieldInfo(
                description="Williams %R value",
                examples=["-20.5", "-80.3"],
                related_terms=["percent r", "momentum", "overbought", "oversold"],
            ),
        },
        use_cases=[
            "Overbought/oversold detection",
            "Momentum analysis",
            "Market timing",
            "Reversal signals",
        ],
    ),
    "rsi": EndpointSemantics(
        client_name="technical",
        method_name="get_rsi",
        natural_description=("Calculate Relative Strength Index (RSI)."),
        example_queries=[
            "Calculate 14-day RSI for AAPL",
            "Get RSI indicator for MSFT",
            "Show relative strength for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the RSI level for TSLA?",
        ],
        related_terms=[
            "relative strength",
            "momentum indicator",
            "overbought/oversold",
            "price momentum",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Momentum Indicators",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "rsi": ResponseFieldInfo(
                description="RSI value",
                examples=["70.5", "30.2"],
                related_terms=[
                    "relative strength",
                    "momentum",
                    "overbought",
                    "oversold",
                ],
            ),
        },
        use_cases=[
            "Momentum analysis",
            "Trend reversal signals",
            "Market timing",
            "Overbought/oversold detection",
        ],
    ),
    "adx": EndpointSemantics(
        client_name="technical",
        method_name="get_adx",
        natural_description=("Calculate Average Directional Index (ADX)."),
        example_queries=[
            "Calculate ADX for AAPL",
            "Get directional movement for MSFT",
            "Show trend strength for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the ADX value for TSLA?",
        ],
        related_terms=[
            "directional movement",
            "trend strength",
            "trend indicator",
            "directional index",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Trend Indicators",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "adx": ResponseFieldInfo(
                description="ADX value",
                examples=["25.5", "45.8"],
                related_terms=["directional movement", "trend strength", "ADX"],
            ),
        },
        use_cases=[
            "Trend strength analysis",
            "Trend following",
            "Trade filtering",
            "Market direction",
        ],
    ),
    "standard_deviation": EndpointSemantics(
        client_name="technical",
        method_name="get_standard_deviation",
        natural_description=(
            "Calculate price Standard Deviation to measure volatility and dispersion."
        ),
        example_queries=[
            "Calculate price volatility for AAPL",
            "Get standard deviation for MSFT",
            "Show price dispersion for GOOGL from 2024-01-01 to 2024-12-31",
            "What's the volatility level for TSLA?",
        ],
        related_terms=[
            "volatility",
            "price dispersion",
            "statistical indicator",
            "risk measure",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Volatility Indicators",
        parameter_hints=COMMON_PARAMS,
        response_hints={
            "standard_deviation": ResponseFieldInfo(
                description="Standard Deviation value",
                examples=["2.5", "5.8"],
                related_terms=["volatility", "dispersion", "variance", "risk"],
            ),
        },
        use_cases=[
            "Volatility analysis",
            "Risk assessment",
            "Option pricing",
            "Market stability",
        ],
    ),
}

# Endpoint mappings
TECHNICAL_ENDPOINT_MAP = {
    "get_sma": TECHNICAL_INDICATOR,
    "get_ema": TECHNICAL_INDICATOR,
    "get_wma": TECHNICAL_INDICATOR,
    "get_dema": TECHNICAL_INDICATOR,
    "get_tema": TECHNICAL_INDICATOR,
    "get_williams": TECHNICAL_INDICATOR,
    "get_rsi": TECHNICAL_INDICATOR,
    "get_adx": TECHNICAL_INDICATOR,
    "get_standard_deviation": TECHNICAL_INDICATOR,
}

# Aggregate technical endpoints for global mapping
# Replace lines around 411-424:
ALL_TECHNICAL_ENDPOINTS = dict.fromkeys(
    [
        "get_sma",
        "get_ema",
        "get_wma",
        "get_dema",
        "get_tema",
        "get_williams",
        "get_rsi",
        "get_adx",
        "get_standard_deviation",
    ],
    TECHNICAL_INDICATOR,
)

# Common subcategories for technical analysis
TECHNICAL_CATEGORIES = {
    "Moving Averages": ["sma", "ema", "wma", "dema", "tema"],
    "Momentum Indicators": ["williams", "rsi"],
    "Trend Indicators": ["adx"],
    "Volatility Indicators": ["standard_deviation"],
}

# Default periods for different technical indicators
DEFAULT_PERIODS = {
    "sma": 20,
    "ema": 20,
    "wma": 20,
    "dema": 20,
    "tema": 20,
    "williams": 14,
    "rsi": 14,
    "adx": 14,
    "standard_deviation": 20,
}

# Indicator thresholds for interpretation
INDICATOR_THRESHOLDS = {
    "rsi": {"overbought": 70, "oversold": 30},
    "williams": {"overbought": -20, "oversold": -80},
    "adx": {"weak_trend": 25, "strong_trend": 50, "very_strong_trend": 75},
}
