from fmp_data.economics.models import (
    CommitmentOfTradersAnalysis,
    CommitmentOfTradersListItem,
    CommitmentOfTradersReport,
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)
from fmp_data.economics.schema import (
    CommitmentOfTradersArgs,
    CommitmentOfTradersListArgs,
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

TREASURY_RATES: Endpoint = Endpoint(
    name="treasury_rates",
    path="treasury-rates",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get U.S. Treasury rates across different maturities "
        "including daily rates and yield curve data"
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
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

ECONOMIC_INDICATORS: Endpoint = Endpoint(
    name="economic_indicators",
    path="economic-indicators",
    version=APIVersion.STABLE,
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

ECONOMIC_CALENDAR: Endpoint = Endpoint(
    name="economic_calendar",
    path="economic-calendar",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Access a calendar of economic events, releases, "
        "and announcements with their expected and actual values"
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
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

MARKET_RISK_PREMIUM: Endpoint = Endpoint(
    name="market_risk_premium",
    path="market-risk-premium",
    version=APIVersion.STABLE,
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

COMMITMENT_OF_TRADERS_REPORT: Endpoint = Endpoint(
    name="commitment_of_traders_report",
    path="commitment-of-traders-report",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Commitment of Traders (COT) report data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="COT report symbol",
        ),
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
    optional_params=[],
    response_model=CommitmentOfTradersReport,
    arg_model=CommitmentOfTradersArgs,
    example_queries=[
        "Get COT report for KC",
        "Show commitment of traders report for NG",
        "COT report for B6 between dates",
    ],
)

COMMITMENT_OF_TRADERS_ANALYSIS: Endpoint = Endpoint(
    name="commitment_of_traders_analysis",
    path="commitment-of-traders-analysis",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Commitment of Traders (COT) analysis data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="COT report symbol",
        ),
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
    optional_params=[],
    response_model=CommitmentOfTradersAnalysis,
    arg_model=CommitmentOfTradersArgs,
    example_queries=[
        "Get COT analysis for KC",
        "Show COT analysis for NG between dates",
        "Commitment of traders analysis for B6",
    ],
)

COMMITMENT_OF_TRADERS_LIST: Endpoint = Endpoint(
    name="commitment_of_traders_list",
    path="commitment-of-traders-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of available Commitment of Traders (COT) symbols",
    mandatory_params=[],
    optional_params=[],
    response_model=CommitmentOfTradersListItem,
    arg_model=CommitmentOfTradersListArgs,
    example_queries=[
        "List COT report symbols",
        "Show all commitment of traders contracts",
        "Available COT symbols",
    ],
)
