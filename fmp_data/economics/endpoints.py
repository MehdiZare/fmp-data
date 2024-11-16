from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)

TREASURY_RATES = Endpoint(
    name="treasury_rates",
    path="treasury",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get treasury rates",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=TreasuryRate,
)

ECONOMIC_INDICATORS = Endpoint(
    name="economic_indicators",
    path="economic",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get economic indicators",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Indicator name",
        )
    ],
    optional_params=[],
    response_model=EconomicIndicator,
)

ECONOMIC_CALENDAR = Endpoint(
    name="economic_calendar",
    path="economic_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get economic calendar events",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
        ),
    ],
    response_model=EconomicEvent,
)

MARKET_RISK_PREMIUM = Endpoint(
    name="market_risk_premium",
    path="market_risk_premium",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get market risk premium data",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketRiskPremium,
)
