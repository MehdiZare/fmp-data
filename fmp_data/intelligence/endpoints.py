from fmp_data.intelligence.models import (
    AnalystEstimate,
    AnalystRecommendation,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    IPOEvent,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    StockSplitEvent,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
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

PRICE_TARGET = Endpoint(
    name="price_target",
    path="price-target",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price targets",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTarget,
)

PRICE_TARGET_SUMMARY = Endpoint(
    name="price_target_summary",
    path="price-target-summary",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price target summary",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTargetSummary,
)

PRICE_TARGET_CONSENSUS = Endpoint(
    name="price_target_consensus",
    path="price-target-consensus",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price target consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTargetConsensus,
)

ANALYST_ESTIMATES = Endpoint(
    name="analyst_estimates",
    path="analyst-estimates/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst estimates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=AnalystEstimate,
)

ANALYST_RECOMMENDATIONS = Endpoint(
    name="analyst_recommendations",
    path="analyst-stock-recommendations/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst recommendations",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=AnalystRecommendation,
)

UPGRADES_DOWNGRADES = Endpoint(
    name="upgrades_downgrades",
    path="upgrades-downgrades",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get upgrades and downgrades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=UpgradeDowngrade,
)

UPGRADES_DOWNGRADES_CONSENSUS = Endpoint(
    name="upgrades_downgrades_consensus",
    path="upgrades-downgrades-consensus",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get upgrades and downgrades consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=UpgradeDowngradeConsensus,
)

EARNINGS_CALENDAR = Endpoint(
    name="earnings_calendar",
    path="earning_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings calendar",
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
    response_model=EarningEvent,
)

EARNINGS_CONFIRMED = Endpoint(
    name="earnings_confirmed",
    path="earning-calendar-confirmed",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get confirmed earnings dates",
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
    response_model=EarningConfirmed,
)

EARNINGS_SURPRISES = Endpoint(
    name="earnings_surprises",
    path="earnings-surprises/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get earnings surprises",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=EarningSurprise,
)

HISTORICAL_EARNINGS = Endpoint(
    name="historical_earnings",
    path="historical/earning_calendar/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get historical earnings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=EarningEvent,
)

DIVIDENDS_CALENDAR = Endpoint(
    name="dividends_calendar",
    path="stock_dividend_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get dividends calendar",
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
    response_model=DividendEvent,
)

STOCK_SPLITS_CALENDAR = Endpoint(
    name="stock_splits_calendar",
    path="stock_split_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get stock splits calendar",
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
    response_model=StockSplitEvent,
)

IPO_CALENDAR = Endpoint(
    name="ipo_calendar",
    path="ipo_calendar",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get IPO calendar",
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
    response_model=IPOEvent,
)
