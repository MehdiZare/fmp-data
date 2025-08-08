from fmp_data.institutional.models import (
    AssetAllocation,
    BeneficialOwnership,
    CIKMapping,
    FailToDeliver,
    Form13F,
    Form13FDate,
    HolderIndustryBreakdown,
    HolderPerformanceSummary,
    IndustryPerformanceSummary,
    InsiderRoster,
    InsiderStatistic,
    InsiderTrade,
    InsiderTradingByName,
    InsiderTradingLatest,
    InsiderTradingSearch,
    InsiderTradingStatistics,
    InsiderTransactionType,
    InstitutionalHolder,
    InstitutionalHolding,
    InstitutionalOwnershipAnalytics,
    InstitutionalOwnershipDates,
    InstitutionalOwnershipExtract,
    InstitutionalOwnershipLatest,
    SymbolPositionsSummary,
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

FORM_13F: Endpoint = Endpoint(
    name="form_13f",
    path="form-thirteen/{cik}",
    version=APIVersion.STABLE,
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

FORM_13F_DATES: Endpoint = Endpoint(
    name="form_13f_dates",
    path="form-thirteen-date/{cik}",
    version=APIVersion.STABLE,
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

ASSET_ALLOCATION: Endpoint = Endpoint(
    name="asset_allocation",
    path="13f-asset-allocation",
    version=APIVersion.STABLE,
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

INSTITUTIONAL_HOLDERS: Endpoint = Endpoint(
    name="institutional_holders",
    path="institutional-ownership/list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of institutional holders",
    mandatory_params=[],
    optional_params=[],
    response_model=InstitutionalHolder,
)

INSTITUTIONAL_HOLDINGS: Endpoint = Endpoint(
    name="institutional_holdings",
    path="institutional-ownership/symbol-ownership",
    version=APIVersion.STABLE,
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

INSIDER_TRADES: Endpoint = Endpoint(
    name="insider_trades",
    path="insider-trading",
    version=APIVersion.STABLE,
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

TRANSACTION_TYPES: Endpoint = Endpoint(
    name="transaction_types",
    path="insider-trading-transaction-type",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider transaction types",
    mandatory_params=[],
    optional_params=[],
    response_model=InsiderTransactionType,
)

INSIDER_ROSTER: Endpoint = Endpoint(
    name="insider_roster",
    path="insider-roaster",
    version=APIVersion.STABLE,
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

INSIDER_STATISTICS: Endpoint = Endpoint(
    name="insider_statistics",
    path="insider-roaster-statistic",
    version=APIVersion.STABLE,
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

CIK_MAPPER: Endpoint = Endpoint(
    name="cik_mapper",
    path="mapper-cik-name",
    version=APIVersion.STABLE,
    description="Get CIK to name mappings",
    mandatory_params=[],
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
    response_model=CIKMapping,
)

CIK_MAPPER_BY_NAME: Endpoint = Endpoint(
    name="cik_mapper_by_name",
    path="mapper-cik-name",
    version=APIVersion.STABLE,
    description="Search CIK mappings by name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Name to search",
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
    response_model=CIKMapping,
)

BENEFICIAL_OWNERSHIP: Endpoint = Endpoint(
    name="beneficial_ownership",
    path="insider/ownership/acquisition_of_beneficial_ownership",
    version=APIVersion.STABLE,
    description="Get beneficial ownership data",
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
    response_model=BeneficialOwnership,
)

FAIL_TO_DELIVER: Endpoint = Endpoint(
    name="fail_to_deliver",
    path="fail_to_deliver",
    version=APIVersion.STABLE,
    description="Get fail to deliver data",
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
    response_model=FailToDeliver,
)

# Insider Trading Endpoints
INSIDER_TRADING_LATEST: Endpoint = Endpoint(
    name="insider_trading_latest",
    path="insider-trading/latest",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get latest insider trading activity",
    mandatory_params=[],
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
    response_model=InsiderTradingLatest,
)

INSIDER_TRADING_SEARCH: Endpoint = Endpoint(
    name="insider_trading_search",
    path="insider-trading/search",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search insider trades with filters",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Stock symbol filter",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results per page",
            default=100,
        ),
    ],
    response_model=InsiderTradingSearch,
)

INSIDER_TRADING_BY_NAME: Endpoint = Endpoint(
    name="insider_trading_by_name",
    path="insider-trading/reporting-name",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search insider trades by reporting name",
    mandatory_params=[
        EndpointParam(
            name="reportingName",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Name of the reporting person",
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
    response_model=InsiderTradingByName,
)

INSIDER_TRADING_STATISTICS_ENHANCED: Endpoint = Endpoint(
    name="insider_trading_statistics_enhanced",
    path="insider-trading/statistics",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get enhanced insider trading statistics",
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
    response_model=InsiderTradingStatistics,
)

# Form 13F Endpoints
INSTITUTIONAL_OWNERSHIP_LATEST: Endpoint = Endpoint(
    name="institutional_ownership_latest",
    path="institutional-ownership/latest",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get latest institutional ownership filings",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Institution CIK filter",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number",
            default=0,
        ),
    ],
    response_model=InstitutionalOwnershipLatest,
)

INSTITUTIONAL_OWNERSHIP_EXTRACT: Endpoint = Endpoint(
    name="institutional_ownership_extract",
    path="institutional-ownership/extract",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get filings extract data",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK",
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
    response_model=InstitutionalOwnershipExtract,
)

INSTITUTIONAL_OWNERSHIP_DATES: Endpoint = Endpoint(
    name="institutional_ownership_dates",
    path="institutional-ownership/dates",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Form 13F filing dates",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK",
        )
    ],
    optional_params=[],
    response_model=InstitutionalOwnershipDates,
)

INSTITUTIONAL_OWNERSHIP_ANALYTICS: Endpoint = Endpoint(
    name="institutional_ownership_analytics",
    path="institutional-ownership/extract-analytics/holder",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get filings extract with analytics by holder",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK",
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
    response_model=InstitutionalOwnershipAnalytics,
)

HOLDER_PERFORMANCE_SUMMARY: Endpoint = Endpoint(
    name="holder_performance_summary",
    path="institutional-ownership/holder-performance-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get holder performance summary",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK",
        )
    ],
    optional_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Filing date",
        )
    ],
    response_model=HolderPerformanceSummary,
)

HOLDER_INDUSTRY_BREAKDOWN: Endpoint = Endpoint(
    name="holder_industry_breakdown",
    path="institutional-ownership/holder-industry-breakdown",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get holders industry breakdown",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Institution CIK",
        )
    ],
    optional_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Filing date",
        )
    ],
    response_model=HolderIndustryBreakdown,
)

SYMBOL_POSITIONS_SUMMARY: Endpoint = Endpoint(
    name="symbol_positions_summary",
    path="institutional-ownership/symbol-positions-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get positions summary by symbol",
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
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Filing date",
        )
    ],
    response_model=SymbolPositionsSummary,
)

INDUSTRY_PERFORMANCE_SUMMARY: Endpoint = Endpoint(
    name="industry_performance_summary",
    path="institutional-ownership/industry-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get industry performance summary",
    mandatory_params=[
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Industry sector",
        )
    ],
    optional_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Filing date",
        )
    ],
    response_model=IndustryPerformanceSummary,
)
