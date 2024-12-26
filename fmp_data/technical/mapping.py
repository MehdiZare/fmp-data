# fmp_data/technical/mapping.py

from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)
from fmp_data.technical.endpoints import TECHNICAL_INDICATOR

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

# Common parameter hints for reuse
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

DATE_HINT = ParameterHint(
    natural_names=["date", "start date", "end date"],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(?:from|since|after)\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-01-15", "2023-12-31"],
    context_clues=["date", "from", "since", "starting", "until"],
)

# Common response field hints
BASIC_PRICE_HINTS = {
    "date": ResponseFieldInfo(
        description="Date of the price data point",
        examples=["2024-01-15", "2023-12-31"],
        related_terms=["date", "timestamp", "time"],
    ),
    "open": ResponseFieldInfo(
        description="Opening price",
        examples=["150.25", "3500.75"],
        related_terms=["open price", "opening", "start price"],
    ),
    "high": ResponseFieldInfo(
        description="Highest price",
        examples=["152.50", "3525.00"],
        related_terms=["high price", "peak", "maximum"],
    ),
    "low": ResponseFieldInfo(
        description="Lowest price",
        examples=["148.75", "3475.50"],
        related_terms=["low price", "bottom", "minimum"],
    ),
    "close": ResponseFieldInfo(
        description="Closing price",
        examples=["151.00", "3510.25"],
        related_terms=["close price", "closing", "end price"],
    ),
    "volume": ResponseFieldInfo(
        description="Trading volume",
        examples=["1000000", "500000"],
        related_terms=["volume", "shares traded", "trading volume"],
    ),
}

TECHNICAL_ENDPOINTS_SEMANTICS = {
    "sma": EndpointSemantics(
        client_name="technical",
        method_name="get_sma",
        natural_description=(
            "Calculate Simple Moving Average (SMA) for a given security. SMA is the "
            "arithmetic mean price over a specified period, useful for identifying "
            "trends and support/resistance levels."
        ),
        example_queries=[
            "Calculate 50-day SMA for AAPL",
            "Get daily SMA(20) for MSFT",
            "Show 200-day moving average for GOOGL",
            "What's the 10-day SMA for TSLA?",
            "Plot 100-day simple moving average for AMZN",
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
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "interval": INTERVAL_HINT,
            "from": DATE_HINT,
            "to": DATE_HINT,
        },
        response_hints={
            **BASIC_PRICE_HINTS,
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
            "Technical analysis",
        ],
    ),
    "ema": EndpointSemantics(
        client_name="technical",
        method_name="get_ema",
        natural_description=(
            "Calculate Exponential Moving Average (EMA) for a security. EMA gives "
            "more weight to recent prices, making it more responsive to new "
            "information than SMA."
        ),
        example_queries=[
            "Calculate 20-day EMA for AAPL",
            "Get exponential moving average(50) for MSFT",
            "Show 12-day EMA for GOOGL",
            "What's the 26-day EMA for TSLA?",
            "Plot exponential average for AMZN",
        ],
        related_terms=[
            "exponential average",
            "weighted moving average",
            "trend indicator",
            "price average",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Moving Averages",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "interval": INTERVAL_HINT,
            "from": DATE_HINT,
            "to": DATE_HINT,
        },
        response_hints={
            **BASIC_PRICE_HINTS,
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
            "Technical analysis",
            "Market timing",
        ],
    ),
    "rsi": EndpointSemantics(
        client_name="technical",
        method_name="get_rsi",
        natural_description=(
            "Calculate Relative Strength Index (RSI) for a security. RSI measures "
            "the speed and magnitude of price movements to evaluate overbought or "
            "oversold conditions."
        ),
        example_queries=[
            "Get 14-day RSI for AAPL",
            "Calculate relative strength index for MSFT",
            "Show RSI levels for GOOGL",
            "What's the current RSI for TSLA?",
            "Plot RSI indicator for AMZN",
        ],
        related_terms=[
            "relative strength",
            "momentum indicator",
            "overbought",
            "oversold",
            "momentum oscillator",
        ],
        category=SemanticCategory.TECHNICAL_ANALYSIS,
        sub_category="Momentum Indicators",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "interval": INTERVAL_HINT,
            "from": DATE_HINT,
            "to": DATE_HINT,
        },
        response_hints={
            **BASIC_PRICE_HINTS,
            "rsi": ResponseFieldInfo(
                description="Relative Strength Index value",
                examples=["70.5", "30.2"],
                related_terms=["RSI", "momentum", "overbought", "oversold"],
            ),
        },
        use_cases=[
            "Overbought/oversold detection",
            "Momentum analysis",
            "Trend reversal signals",
            "Technical analysis",
            "Trading signal generation",
        ],
    ),
    # Add similar semantic definitions for other indicators...
}

# Aggregate all technical endpoints for global mapping
ALL_TECHNICAL_ENDPOINTS = {
    name: TECHNICAL_INDICATOR
    for name in [
        "get_sma",
        "get_ema",
        "get_wma",
        "get_dema",
        "get_tema",
        "get_williams",
        "get_rsi",
        "get_adx",
        "get_standard_deviation",
    ]
}

# Additional mappings for common terms
TECHNICAL_COMMON_TERMS = {
    "moving_average": [
        "average price",
        "price mean",
        "smoothed price",
        "trend line",
        "MA",
    ],
    "momentum": [
        "price momentum",
        "trend strength",
        "price strength",
        "movement speed",
        "price velocity",
    ],
    "volatility": [
        "price volatility",
        "market volatility",
        "price variation",
        "price fluctuation",
        "market movement",
    ],
}

# Time interval mappings
TECHNICAL_INTERVALS = {
    "intraday": {
        "1min": ["1-minute", "one minute", "1 min", "1m"],
        "5min": ["5-minute", "five minute", "5 min", "5m"],
        "15min": ["15-minute", "fifteen minute", "15 min", "15m"],
        "30min": ["30-minute", "thirty minute", "30 min", "30m"],
        "1hour": ["1-hour", "one hour", "1 hr", "1h"],
        "4hour": ["4-hour", "four hour", "4 hr", "4h"],
    },
    "daily": ["daily", "day", "1 day", "1d"],
}

# Common calculation patterns
TECHNICAL_CALCULATIONS = {
    "moving_average": {
        "simple": "sum(prices) / period",
        "exponential": "(price * k) + (previous_ema * (1-k)) where k = 2/(period+1)",
        "weighted": "sum(price * weight) / sum(weights)",
    },
    "momentum": {
        "rsi": "(100 - 100/(1 + RS)) where RS = avg_gain/avg_loss",
        "williams": "((highest_high - close)/(highest_high - lowest_low)) * -100",
        "adx": "(+DI - -DI)/(+DI + -DI) * 100",
    },
}
