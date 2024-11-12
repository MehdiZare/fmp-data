# fmp_data/technical/endpoints.py
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

from . import models

# Map of indicator types to their corresponding models
INDICATOR_MODEL_MAP = {
    "sma": models.SMAIndicator,
    "ema": models.EMAIndicator,
    "wma": models.WMAIndicator,
    "dema": models.DEMAIndicator,
    "tema": models.TEMAIndicator,
    "williams": models.WilliamsIndicator,
    "rsi": models.RSIIndicator,
    "adx": models.ADXIndicator,
    "standardDeviation": models.StandardDeviationIndicator,
}

TECHNICAL_INDICATOR = Endpoint(
    name="technical_indicator",
    path="technical_indicator/{interval}/{symbol}",
    version=APIVersion.V3,
    description="Get technical indicator values",
    mandatory_params=[
        EndpointParam(
            name="interval",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Time interval",
            valid_values=["1min", "5min", "15min", "30min", "1hour", "4hour", "daily"],
        ),
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="type",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
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
            param_type=ParamType.QUERY,
            required=True,
            type=int,
            description="Period for indicator calculation",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=models.TechnicalIndicator,
)
