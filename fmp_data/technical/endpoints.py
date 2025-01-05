# fmp_data/technical/endpoints.py

from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)
from fmp_data.technical.models import (
    ADXIndicator,
    DEMAIndicator,
    EMAIndicator,
    RSIIndicator,
    SMAIndicator,
    StandardDeviationIndicator,
    TechnicalIndicator,
    TEMAIndicator,
    WilliamsIndicator,
    WMAIndicator,
)

# Map of indicator types to their corresponding models
INDICATOR_MODEL_MAP: dict[str, type[TechnicalIndicator]] = {
    "sma": SMAIndicator,
    "ema": EMAIndicator,
    "wma": WMAIndicator,
    "dema": DEMAIndicator,
    "tema": TEMAIndicator,
    "williams": WilliamsIndicator,
    "rsi": RSIIndicator,
    "adx": ADXIndicator,
    "standardDeviation": StandardDeviationIndicator,
}

TECHNICAL_INDICATOR: Endpoint = Endpoint(
    name="technical_indicator",
    path="technical_indicator/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get technical indicator values",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour", "daily"],
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Indicator type",
            valid_values=[
                "sma",
                "ema",
                "wma",
                "dema",
                "tema",
                "williams",
                "rsi",
                "adx",
                "standardDeviation",
            ],
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Period for indicator calculation",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=TechnicalIndicator,
)
