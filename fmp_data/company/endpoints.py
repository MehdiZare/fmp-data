# company/endpoints.py
from fmp_data.company.models import (
    AvailableIndex,
    CIKResult,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    CompanySearchResult,
    CompanySymbol,
    CUSIPResult,
    EmployeeCount,
    ExchangeSymbol,
    ExecutiveCompensation,
    GeographicRevenueSegment,
    HistoricalShareFloat,
    ISINResult,
    ProductRevenueSegment,
    ShareFloat,
    SymbolChange,
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

PROFILE = Endpoint(
    name="profile",
    path="profile/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get company profile information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=CompanyProfile,
)

CORE_INFORMATION = Endpoint(
    name="core_information",
    path="company-core-information",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get core company information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=CompanyCoreInformation,
)

SEARCH = Endpoint(
    name="search",
    path="search",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search for companies",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Search query string",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of results",
            default=10,
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Filter by exchange",
        ),
    ],
    response_model=CompanySearchResult,
)

KEY_EXECUTIVES = Endpoint(
    name="key_executives",
    path="key-executives/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get company executives information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=CompanyExecutive,
)

COMPANY_NOTES = Endpoint(
    name="company_notes",
    path="company-notes",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get company financial notes",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=CompanyNote,
)

EMPLOYEE_COUNT = Endpoint(
    name="employee_count",
    path="historical/employee_count",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get company employee count history",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=EmployeeCount,
)

STOCK_LIST = Endpoint(
    name="stock_list",
    path="stock/list",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of all available stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

ETF_LIST = Endpoint(
    name="etf_list",
    path="etf/list",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of all available ETFs",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

AVAILABLE_INDEXES = Endpoint(
    name="available_indexes",
    path="symbol/available-indexes",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of all available indexes",
    mandatory_params=[],
    optional_params=[],
    response_model=AvailableIndex,
)

EXCHANGE_SYMBOLS = Endpoint(
    name="exchange_symbols",
    path="symbol/{exchange}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get all symbols for a specific exchange",
    mandatory_params=[
        EndpointParam(
            name="exchange",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Exchange code",
        )
    ],
    optional_params=[],
    response_model=ExchangeSymbol,
)

CIK_SEARCH = Endpoint(
    name="cik_search",
    path="cik-search",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search companies by CIK number",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Search query",
        )
    ],
    optional_params=[],
    response_model=CIKResult,
)

CUSIP_SEARCH = Endpoint(
    name="cusip_search",
    path="cusip",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search companies by CUSIP",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Search query",
        )
    ],
    optional_params=[],
    response_model=CUSIPResult,
)

ISIN_SEARCH = Endpoint(
    name="isin_search",
    path="search/isin",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search companies by ISIN",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Search query",
        )
    ],
    optional_params=[],
    response_model=ISINResult,
)

COMPANY_LOGO = Endpoint(
    name="company_logo",
    path="{symbol}.png",
    version=None,
    url_type=URLType.IMAGE,
    method=HTTPMethod.GET,
    description="Get company logo URL",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=str,
)

EXECUTIVE_COMPENSATION = Endpoint(
    name="executive_compensation",
    path="governance/executive_compensation",
    version=APIVersion.V4,
    description="Get executive compensation data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=ExecutiveCompensation,
)

SHARE_FLOAT = Endpoint(
    name="share_float",
    path="shares_float",
    version=APIVersion.V4,
    description="Get current share float data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=ShareFloat,
)

HISTORICAL_SHARE_FLOAT = Endpoint(
    name="historical_share_float",
    path="historical/shares_float",
    version=APIVersion.V4,
    description="Get historical share float data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        )
    ],
    optional_params=[],
    response_model=HistoricalShareFloat,
)

ALL_SHARES_FLOAT = Endpoint(
    name="all_shares_float",
    path="shares_float/all",
    version=APIVersion.V4,
    description="Get share float data for all companies",
    mandatory_params=[],
    optional_params=[],
    response_model=ShareFloat,
)

# endpoints.py
PRODUCT_REVENUE_SEGMENTATION = Endpoint(
    name="product_revenue_segmentation",
    path="revenue-product-segmentation",
    version=APIVersion.V4,
    description="Get revenue segmentation by product",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        ),
        EndpointParam(
            name="structure",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Data structure format",
            default="flat",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Annual or quarterly data",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
    ],
    optional_params=[],
    response_model=ProductRevenueSegment,  # Updated to new model
)

GEOGRAPHIC_REVENUE_SEGMENTATION = Endpoint(
    name="geographic_revenue_segmentation",
    path="revenue-geographic-segmentation",
    version=APIVersion.V4,
    description="Get revenue segmentation by geography",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company symbol",
        ),
        EndpointParam(
            name="structure",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Data structure format",
            default="flat",
        ),
    ],
    optional_params=[],
    response_model=GeographicRevenueSegment,  # Updated to new model
)

SYMBOL_CHANGES = Endpoint(
    name="symbol_changes",
    path="symbol_change",
    version=APIVersion.V4,
    description="Get symbol change history",
    mandatory_params=[],
    optional_params=[],
    response_model=SymbolChange,
)
