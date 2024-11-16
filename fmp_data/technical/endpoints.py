# fmp_data/technical/endpoints.py
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    ParamLocation,
    ParamType,
)

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
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    response_model=models.TechnicalIndicator,
)
