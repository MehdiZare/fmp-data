# fmp_data/technical/endpoints.py

from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)
from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    EMAIndicator,
    RSIIndicator,
    SMAIndicator,
    StandardDeviationIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)
from fmp_data.technical.schema import TechnicalIndicatorArgs

# Valid timeframes for all technical indicators
VALID_TIMEFRAMES = ["1min", "5min", "15min", "30min", "1hour", "4hour", "1day"]

# Simple Moving Average
SMA: Endpoint = Endpoint(
    name="sma",
    path="technical-indicators/sma",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Simple Moving Average (SMA) for a given symbol. "
        "SMA is the average price over a specified number of periods."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=SMAIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get 50-day SMA for Apple",
        "Calculate simple moving average for TSLA",
        "Show 200-day moving average",
    ],
)

# Exponential Moving Average
EMA: Endpoint = Endpoint(
    name="ema",
    path="technical-indicators/ema",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Exponential Moving Average (EMA) for a given symbol. "
        "EMA gives more weight to recent prices."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=EMAIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get 12-day EMA for AAPL",
        "Calculate exponential moving average",
        "Show EMA indicator values",
    ],
)

# Weighted Moving Average
WMA: Endpoint = Endpoint(
    name="wma",
    path="technical-indicators/wma",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Weighted Moving Average (WMA) for a given symbol. "
        "WMA assigns linearly decreasing weights to past prices."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=WMAIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get weighted moving average for MSFT",
        "Calculate WMA indicator",
        "Show 20-day WMA",
    ],
)

# Double Exponential Moving Average
DEMA: Endpoint = Endpoint(
    name="dema",
    path="technical-indicators/dema",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Double Exponential Moving Average (DEMA) for a given symbol. "
        "DEMA is more responsive to price changes than regular EMA."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=DEMAIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get DEMA for stock analysis",
        "Calculate double exponential moving average",
        "Show DEMA indicator",
    ],
)

# Triple Exponential Moving Average
TEMA: Endpoint = Endpoint(
    name="tema",
    path="technical-indicators/tema",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Triple Exponential Moving Average (TEMA) for a given symbol. "
        "TEMA further reduces lag compared to DEMA."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=TEMAIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get TEMA for trend analysis",
        "Calculate triple exponential moving average",
        "Show TEMA values",
    ],
)

# Relative Strength Index
RSI: Endpoint = Endpoint(
    name="rsi",
    path="technical-indicators/rsi",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Relative Strength Index (RSI) for a given symbol. "
        "RSI measures momentum and identifies overbought/oversold conditions."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation (typically 14)",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=RSIIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get RSI for overbought/oversold signals",
        "Calculate 14-day RSI",
        "Show RSI momentum indicator",
    ],
)

# Standard Deviation
STANDARD_DEVIATION: Endpoint = Endpoint(
    name="standard_deviation",
    path="technical-indicators/standarddeviation",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Standard Deviation for a given symbol. "
        "Measures the volatility of price movements."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=StandardDeviationIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get volatility using standard deviation",
        "Calculate price volatility",
        "Show standard deviation values",
    ],
)

# Williams %R
WILLIAMS: Endpoint = Endpoint(
    name="williams",
    path="technical-indicators/williams",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Williams %R indicator for a given symbol. "
        "Williams %R identifies overbought and oversold levels."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation (typically 14)",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=WilliamsIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get Williams %R indicator",
        "Calculate Williams percentage range",
        "Show overbought/oversold signals",
    ],
)

# Average Directional Index
ADX: Endpoint = Endpoint(
    name="adx",
    path="technical-indicators/adx",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Calculate Average Directional Index (ADX) for a given symbol. "
        "ADX measures the strength of a trend."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="periodLength",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Number of periods for calculation (typically 14)",
        ),
        EndpointParam(
            name="timeframe",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=VALID_TIMEFRAMES,
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=ADXIndicator,
    arg_model=TechnicalIndicatorArgs,
    example_queries=[
        "Get ADX trend strength indicator",
        "Calculate average directional index",
        "Show trend strength values",
    ],
)
