# fmp_data/institutional/endpoints.py
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

from . import models

# Form 13F endpoints
FORM_13F = Endpoint(
    name="form_13f",
    path="form-thirteen/{cik}",
    version=APIVersion.V3,
    description="Get Form 13F filing data",
    mandatory_params=[
        EndpointParam(
            name="cik",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Institution CIK number",
        ),
        EndpointParam(
            name="date",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing date",
        ),
    ],
    response_model=models.Form13F,
)

ASSET_ALLOCATION = Endpoint(
    name="asset_allocation",
    path="13f-asset-allocation",
    version=APIVersion.V4,
    description="Get 13F asset allocation data",
    mandatory_params=[
        EndpointParam(
            name="date",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Filing date",
        )
    ],
    response_model=models.AssetAllocation,
)

INSTITUTIONAL_HOLDERS = Endpoint(
    name="institutional_holders",
    path="institutional-ownership/list",
    version=APIVersion.V4,
    description="Get list of institutional holders",
    response_model=models.InstitutionalHolder,
)

INSTITUTIONAL_HOLDINGS = Endpoint(
    name="institutional_holdings",
    path="institutional-ownership/symbol-ownership",
    version=APIVersion.V4,
    description="Get institutional holdings by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        ),
        EndpointParam(
            name="includeCurrentQuarter",
            param_type=ParamType.QUERY,
            required=False,
            type=bool,
            description="Include current quarter",
            default=False,
        ),
    ],
    response_model=models.InstitutionalHolding,
)

# Insider Trading endpoints
INSIDER_TRADES = Endpoint(
    name="insider_trades",
    path="insider-trading",
    version=APIVersion.V4,
    description="Get insider trades",
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
            name="page",
            param_type=ParamType.QUERY,
            required=False,
            type=int,
            description="Page number",
            default=0,
        )
    ],
    response_model=models.InsiderTrade,
)

TRANSACTION_TYPES = Endpoint(
    name="transaction_types",
    path="insider-trading-transaction-type",
    version=APIVersion.V4,
    description="Get insider transaction types",
    response_model=models.InsiderTransactionType,
)

INSIDER_ROSTER = Endpoint(
    name="insider_roster",
    path="insider-roaster",
    version=APIVersion.V4,
    description="Get insider roster",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.InsiderRoster,
)

INSIDER_STATISTICS = Endpoint(
    name="insider_statistics",
    path="insider-roaster-statistic",
    version=APIVersion.V4,
    description="Get insider trading statistics",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol",
        )
    ],
    response_model=models.InsiderStatistic,
)
