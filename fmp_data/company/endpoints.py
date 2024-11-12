# endpoints.py
from fmp_data.company.models import (
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
    ISINResult,
)
from fmp_data.models import APIVersion, Endpoint, EndpointParam, ParamType

# Company Endpoints
PROFILE = Endpoint(
    name="profile",
    path="profile/{symbol}",
    version=APIVersion.V3,
    description="Get company profile information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
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
    description="Get core company information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
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
    description="Search for companies",
    mandatory_params=[
        EndpointParam(
            name="query",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Search query string",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            param_type=ParamType.QUERY,
            required=False,
            type=int,
            description="Maximum number of results",
            default=10,
        ),
        EndpointParam(
            name="exchange",
            param_type=ParamType.QUERY,
            required=False,
            type=str,
            description="Filter by exchange",
        ),
    ],
    response_model=CompanySearchResult,
)

KEY_EXECUTIVES = Endpoint(
    name="key_executives",
    path="key-executives/{symbol}",
    version=APIVersion.V3,
    description="Get company executives information",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
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
    description="Get company financial notes",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
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
    description="Get company employee count history",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=EmployeeCount,
)
# In endpoints.py, add:

STOCK_LIST = Endpoint(
    name="stock_list",
    path="stock/list",
    version=APIVersion.V3,
    description="Get list of all available stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

ETF_LIST = Endpoint(
    name="etf_list",
    path="etf/list",
    version=APIVersion.V3,
    description="Get list of all available ETFs",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

AVAILABLE_INDEXES = Endpoint(
    name="available_indexes",
    path="symbol/available-indexes",
    version=APIVersion.V3,
    description="Get list of all available indexes",
    mandatory_params=[],
    optional_params=[],
    response_model=str,
)

EXCHANGE_SYMBOLS = Endpoint(
    name="exchange_symbols",
    path="symbol/{exchange}",
    version=APIVersion.V3,
    description="Get all symbols for a specific exchange",
    mandatory_params=[
        EndpointParam(
            name="exchange",
            param_type=ParamType.PATH,
            required=True,
            type=str,
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
    description="Search companies by CIK number",
    mandatory_params=[
        EndpointParam(
            name="query",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
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
    description="Search companies by CUSIP",
    mandatory_params=[
        EndpointParam(
            name="query",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
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
    description="Search companies by ISIN",
    mandatory_params=[
        EndpointParam(
            name="query",
            param_type=ParamType.QUERY,
            required=True,
            type=str,
            description="Search query",
        )
    ],
    optional_params=[],
    response_model=ISINResult,
)

COMPANY_LOGO = Endpoint(
    name="company_logo",
    path="image-stock/{symbol}.png",
    version=APIVersion.V3,
    description="Get company logo URL",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            param_type=ParamType.PATH,
            required=True,
            type=str,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[],
    response_model=str,
)
