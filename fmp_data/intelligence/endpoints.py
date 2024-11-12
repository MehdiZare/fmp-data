# fmp_data/intelligence/endpoints.py
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

from . import models

# Price Targets endpoints
PRICE_TARGET = Endpoint(
    name="price_target",
    path="price-target",
    version=APIVersion.V4,
    description="Get price targets",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.PriceTarget,
)

PRICE_TARGET_SUMMARY = Endpoint(
    name="price_target_summary",
    path="price-target-summary",
    version=APIVersion.V4,
    description="Get price target summary",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.PriceTargetSummary,
)

PRICE_TARGET_CONSENSUS = Endpoint(
    name="price_target_consensus",
    path="price-target-consensus",
    version=APIVersion.V4,
    description="Get price target consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.PriceTargetConsensus,
)

# Analyst Coverage endpoints
ANALYST_ESTIMATES = Endpoint(
    name="analyst_estimates",
    path="analyst-estimates/{symbol}",
    version=APIVersion.V3,
    description="Get analyst estimates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.AnalystEstimate,
)

ANALYST_RECOMMENDATIONS = Endpoint(
    name="analyst_recommendations",
    path="analyst-stock-recommendations/{symbol}",
    version=APIVersion.V3,
    description="Get analyst recommendations",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.AnalystRecommendation,
)

# Upgrades & Downgrades endpoints
UPGRADES_DOWNGRADES = Endpoint(
    name="upgrades_downgrades",
    path="upgrades-downgrades",
    version=APIVersion.V4,
    description="Get upgrades and downgrades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.UpgradeDowngrade,
)

UPGRADES_DOWNGRADES_CONSENSUS = Endpoint(
    name="upgrades_downgrades_consensus",
    path="upgrades-downgrades-consensus",
    version=APIVersion.V4,
    description="Get upgrades and downgrades consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.UpgradeDowngradeConsensus,
)

# Corporate Events endpoints
EARNINGS_CALENDAR = Endpoint(
    name="earnings_calendar",
    path="earning_calendar",
    version=APIVersion.V3,
    description="Get earnings calendar",
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
    response_model=models.EarningEvent,
)

EARNINGS_CONFIRMED = Endpoint(
    name="earnings_confirmed",
    path="earning-calendar-confirmed",
    version=APIVersion.V4,
    description="Get confirmed earnings dates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
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
    response_model=models.EarningConfirmed,
)

EARNINGS_SURPRISES = Endpoint(
    name="earnings_surprises",
    path="earnings-surprises/{symbol}",
    version=APIVersion.V3,
    description="Get earnings surprises",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.EarningSurprise,
)

HISTORICAL_EARNINGS = Endpoint(
    name="historical_earnings",
    path="historical/earning_calendar/{symbol}",
    version=APIVersion.V3,
    description="Get historical earnings",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.EarningEvent,
)

DIVIDENDS_CALENDAR = Endpoint(
    name="dividends_calendar",
    path="stock_dividend_calendar",
    version=APIVersion.V3,
    description="Get dividends calendar",
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
    response_model=models.DividendEvent,
)

STOCK_SPLITS_CALENDAR = Endpoint(
    name="stock_splits_calendar",
    path="stock_split_calendar",
    version=APIVersion.V3,
    description="Get stock splits calendar",
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
    response_model=models.StockSplitEvent,
)

IPO_CALENDAR = Endpoint(
    name="ipo_calendar",
    path="ipo_calendar",
    version=APIVersion.V3,
    description="Get IPO calendar",
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
    response_model=models.IPOEvent,
)
