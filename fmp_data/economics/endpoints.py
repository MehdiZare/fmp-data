# fmp_data/economics/endpoints.py

from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

TREASURY_RATES = Endpoint(
    name="treasury_rates",
    path="treasury",
    version=APIVersion.V4,
    description="Get treasury rates",
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date",
        ),
    ],
    response_model=TreasuryRate,
)

ECONOMIC_INDICATORS = Endpoint(
    name="economic_indicators",
    path="economic",
    version=APIVersion.V4,
    description="Get economic indicators",
    mandatory_params=[
        EndpointParam(
            name="name",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Indicator name",
        )
    ],
    response_model=EconomicIndicator,
)

ECONOMIC_CALENDAR = Endpoint(
    name="economic_calendar",
    path="economic_calendar",
    version=APIVersion.V3,
    description="Get economic calendar events",
    optional_params=[
        EndpointParam(
            name="from",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="End date",
        ),
    ],
    response_model=EconomicEvent,
)

MARKET_RISK_PREMIUM = Endpoint(
    name="market_risk_premium",
    path="market_risk_premium",
    version=APIVersion.V4,
    description="Get market risk premium data",
    response_model=MarketRiskPremium,
)
