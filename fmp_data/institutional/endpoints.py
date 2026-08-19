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

FORM_13F: Endpoint[Form13F] = Endpoint(
    name="form_13f",
    path="institutional-ownership/extract",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Form 13F filing data",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            description="Institution CIK number",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=Form13F,
)

FORM_13F_DATES: Endpoint[Form13FDate] = Endpoint(
    name="form_13f_dates",
    path="institutional-ownership/dates",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get Form 13F filing dates",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.CIK,
            description="Institution CIK number",
        ),
    ],
    optional_params=[],
    response_model=Form13FDate,
)

ASSET_ALLOCATION: Endpoint[AssetAllocation] = Endpoint(
    name="asset_allocation",
    path="13f-asset-allocation",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "DEPRECATED and non-functional: FMP no longer serves 13F asset "
        "allocation, so this path 404s, and no stable endpoint replaces it. "
        "Do not select it. The nearest live data is per-filer 13F holdings, "
        "which must be aggregated by hand."
    ),
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Filing date",
        )
    ],
    optional_params=[],
    response_model=AssetAllocation,
)

INSTITUTIONAL_HOLDERS: Endpoint[InstitutionalHolder] = Endpoint(
    name="institutional_holders",
    path="institutional-ownership/latest",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of institutional holders",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    response_model=InstitutionalHolder,
)

INSTITUTIONAL_HOLDINGS: Endpoint[InstitutionalHolding] = Endpoint(
    name="institutional_holdings",
    path="institutional-ownership/symbol-positions-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get institutional holdings by symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=InstitutionalHolding,
)

INSIDER_TRADES: Endpoint[InsiderTrade] = Endpoint(
    name="insider_trades",
    path="insider-trading/search",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider trades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results per page",
            default=100,
        ),
    ],
    response_model=InsiderTrade,
)

TRANSACTION_TYPES: Endpoint[InsiderTransactionType] = Endpoint(
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

INSIDER_ROSTER: Endpoint[InsiderRoster] = Endpoint(
    name="insider_roster",
    path="insider-trading/search",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider roster",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=InsiderRoster,
)

INSIDER_STATISTICS: Endpoint[InsiderStatistic] = Endpoint(
    name="insider_statistics",
    path="insider-trading/statistics",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get insider trading statistics",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=InsiderStatistic,
)

CIK_MAPPER: Endpoint[CIKMapping] = Endpoint(
    name="cik_mapper",
    path="cik-list",
    version=APIVersion.STABLE,
    description="Get CIK to name mappings",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=1000,
        ),
    ],
    response_model=CIKMapping,
)

# ``CIK_MAPPER_BY_NAME`` was removed in 2.6 (#130). It declared the same path
# and the same ``page``/``limit`` parameters as ``CIK_MAPPER`` -- ``cik-list``
# has no server-side name filter -- so it was a byte-for-byte duplicate that
# could not express the search it claimed. ``InstitutionalClient
# .search_cik_by_name`` remains the interface: it calls ``CIK_MAPPER`` with
# ``limit=10000`` and filters locally.

BENEFICIAL_OWNERSHIP: Endpoint[BeneficialOwnership] = Endpoint(
    name="beneficial_ownership",
    path="acquisition-of-beneficial-ownership",
    version=APIVersion.STABLE,
    description="Get beneficial ownership data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=BeneficialOwnership,
)

FAIL_TO_DELIVER: Endpoint[FailToDeliver] = Endpoint(
    # The second naming oddity #166 raised: underscores in a ``path`` where
    # every other path in the catalogue uses hyphens, and ``name == path``.
    # Left alone deliberately, and not for lack of checking -- probed against
    # the live API while closing #166, ``fail_to_deliver``, ``fail-to-deliver``
    # and ``fails-to-deliver`` all return 404 (a known-good control on the same
    # key returned 200 in the same run). There is no live variant to rename
    # *to*; the endpoint is withdrawn upstream, the client method is
    # ``@deprecated`` and the tool is in ``WITHDRAWN_TOOLS`` with no successor.
    # Changing the path here would swap one 404 for another. Goes away with the
    # endpoint in 3.0.
    name="fail_to_deliver",
    path="fail_to_deliver",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: FMP no longer serves fail-to-deliver "
        "data, so this path 404s, and no stable endpoint replaces it. Do not "
        "select it. The SEC publishes the same fails-to-deliver files itself."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    response_model=FailToDeliver,
)

# Insider Trading Endpoints
INSIDER_TRADING_LATEST: Endpoint[InsiderTradingLatest] = Endpoint(
    name="insider_trading_latest",
    path="insider-trading/latest",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get latest insider trading activity",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Filter by transaction date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results per page",
            default=100,
        ),
    ],
    response_model=InsiderTradingLatest,
)

INSIDER_TRADING_SEARCH: Endpoint[InsiderTradingSearch] = Endpoint(
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
            description="Stock symbol filter",
        ),
        EndpointParam(
            name="reportingCik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Reporting CIK filter",
        ),
        EndpointParam(
            name="companyCik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Company CIK filter",
        ),
        EndpointParam(
            name="transactionType",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Transaction type filter",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results per page",
            default=100,
        ),
    ],
    response_model=InsiderTradingSearch,
)

INSIDER_TRADING_BY_NAME: Endpoint[InsiderTradingByName] = Endpoint(
    name="insider_trading_by_name",
    path="insider-trading/reporting-name",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search insider trades by reporting name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Name of the reporting person",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        )
    ],
    response_model=InsiderTradingByName,
)

INSIDER_TRADING_STATISTICS_ENHANCED: Endpoint[InsiderTradingStatistics] = Endpoint(
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
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=InsiderTradingStatistics,
)

# Form 13F Endpoints
INSTITUTIONAL_OWNERSHIP_LATEST: Endpoint[InstitutionalOwnershipLatest] = Endpoint(
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
            param_type=ParamType.CIK,
            description="Institution CIK filter",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    response_model=InstitutionalOwnershipLatest,
)

INSTITUTIONAL_OWNERSHIP_EXTRACT: Endpoint[InstitutionalOwnershipExtract] = Endpoint(
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
            param_type=ParamType.CIK,
            description="Institution CIK",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=InstitutionalOwnershipExtract,
)

INSTITUTIONAL_OWNERSHIP_DATES: Endpoint[InstitutionalOwnershipDates] = Endpoint(
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
            param_type=ParamType.CIK,
            description="Institution CIK",
        )
    ],
    optional_params=[],
    response_model=InstitutionalOwnershipDates,
)

INSTITUTIONAL_OWNERSHIP_ANALYTICS: Endpoint[InstitutionalOwnershipAnalytics] = Endpoint(
    name="institutional_ownership_analytics",
    path="institutional-ownership/extract-analytics/holder",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get filings extract with analytics by holder",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Stock symbol",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results",
            default=100,
        ),
    ],
    response_model=InstitutionalOwnershipAnalytics,
)

HOLDER_PERFORMANCE_SUMMARY: Endpoint[HolderPerformanceSummary] = Endpoint(
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
            param_type=ParamType.CIK,
            description="Institution CIK",
        )
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
            default=0,
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    response_model=HolderPerformanceSummary,
)

HOLDER_INDUSTRY_BREAKDOWN: Endpoint[HolderIndustryBreakdown] = Endpoint(
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
            param_type=ParamType.CIK,
            description="Institution CIK",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=HolderIndustryBreakdown,
)

SYMBOL_POSITIONS_SUMMARY: Endpoint[SymbolPositionsSummary] = Endpoint(
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
            description="Stock symbol",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=SymbolPositionsSummary,
)

INDUSTRY_PERFORMANCE_SUMMARY: Endpoint[IndustryPerformanceSummary] = Endpoint(
    name="industry_performance_summary",
    path="institutional-ownership/industry-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get industry performance summary",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing year",
        ),
        EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Filing quarter (1-4)",
        ),
    ],
    optional_params=[],
    response_model=IndustryPerformanceSummary,
)
