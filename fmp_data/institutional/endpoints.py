from fmp_data.institutional.models import (
    AssetAllocation,
    Form13F,
    Form13FDate,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InsiderTransactionType,
    InstitutionalHolder,
    InstitutionalHolding,
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

FORM_13F = Endpoint(
    name="form_13f",
    path="form-thirteen/{cik}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Form 13F filing data",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK number",
        ),
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Filing date",
        ),
    ],
    optional_params=[],
    response_model=Form13F,
)

FORM_13F_DATES = Endpoint(
    name="form_13f_dates",
    path="form-thirteen-date/{cik}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Form 13F filing dates",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK number",
        ),
    ],
    optional_params=[],
    response_model=Form13FDate,
)

ASSET_ALLOCATION = Endpoint(
    name="asset_allocation",
    path="13f-asset-allocation",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get 13F asset allocation data",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Filing date",
        )
    ],
    optional_params=[],
    response_model=AssetAllocation,
)

INSTITUTIONAL_HOLDERS = Endpoint(
    name="institutional_holders",
    path="institutional-ownership/list",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of institutional holders",
    mandatory_params=[],
    optional_params=[],
    response_model=InstitutionalHolder,
)

INSTITUTIONAL_HOLDINGS = Endpoint(
    name="institutional_holdings",
    path="institutional-ownership/symbol-ownership",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get institutional holdings by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
        EndpointParam(
            name="includeCurrentQuarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Include current quarter",
            default=False,
        ),
    ],
    optional_params=[],
    response_model=InstitutionalHolding,
)

INSIDER_TRADES = Endpoint(
    name="insider_trades",
    path="insider-trading",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider trades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        )
    ],
    response_model=InsiderTrade,
)

TRANSACTION_TYPES = Endpoint(
    name="transaction_types",
    path="insider-trading-transaction-type",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider transaction types",
    mandatory_params=[],
    optional_params=[],
    response_model=InsiderTransactionType,
)

INSIDER_ROSTER = Endpoint(
    name="insider_roster",
    path="insider-roaster",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider roster",
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
    response_model=InsiderRoster,
)

INSIDER_STATISTICS = Endpoint(
    name="insider_statistics",
    path="insider-roaster-statistic",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider trading statistics",
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
    response_model=InsiderStatistic,
)
