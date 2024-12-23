from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.economics.schema import (
    EconomicCalendarArgs,
    EconomicIndicatorsArgs,
    EconomicIndicatorType,
    TreasuryRatesArgs,
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
    description=(
        "Get U.S. Treasury rates across different maturities "
        "including daily rates and yield curve data"
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date for treasury rates data",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date for treasury rates data",
        ),
    ],
    response_model=TreasuryRate,
    arg_model=TreasuryRatesArgs,
    example_queries=[
        "What are the current Treasury rates?",
        "Get historical treasury yields",
        "Show me the yield curve data",
        "What's the 10-year Treasury rate?",
        "Get Treasury rates for last month",
        "Show me all Treasury maturities",
        "Compare short-term and long-term rates",
    ],
)

ECONOMIC_INDICATORS = Endpoint(
    name="economic_indicators",
    path="economic",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve economic indicator data including GDP, "
        "inflation rates, employment statistics, and other key metrics"
    ),
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Name of the economic indicator to retrieve",
            valid_values=list(EconomicIndicatorType),
        )
    ],
    optional_params=[],
    response_model=EconomicIndicator,
    arg_model=EconomicIndicatorsArgs,
    example_queries=[
        "Get GDP growth rate",
        "Show inflation data",
        "What's the unemployment rate?",
        "Get CPI numbers",
        "Show industrial production stats",
        "What's the current account balance?",
        "Show me consumer confidence data",
    ],
)

ECONOMIC_CALENDAR = Endpoint(
    name="economic_calendar",
    path="economic_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Access a calendar of economic events, releases, "
        "and announcements with their expected and actual values"
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date for economic events",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date for economic events",
        ),
    ],
    response_model=EconomicEvent,
    arg_model=EconomicCalendarArgs,
    example_queries=[
        "Show economic calendar",
        "What economic releases are coming up?",
        "Get economic events for next week",
        "Show me important economic announcements",
        "When is the next GDP release?",
        "Show upcoming data releases",
        "What economic reports are due?",
    ],
)

MARKET_RISK_PREMIUM = Endpoint(
    name="market_risk_premium",
    path="market_risk_premium",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve market risk premium data by country, "
        "including equity risk premiums and country-specific risk factors"
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=MarketRiskPremium,
    arg_model=None,  # No parameters needed
    example_queries=[
        "Get market risk premium data",
        "Show country risk premiums",
        "What's the equity risk premium?",
        "Get risk premium by country",
        "Show market risk by region",
        "Compare country risk premiums",
        "What's the US market premium?",
    ],
)
