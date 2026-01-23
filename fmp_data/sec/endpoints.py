# fmp_data/sec/endpoints.py
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)
from fmp_data.sec.models import (
    IndustryClassification,
    SECCompanySearchResult,
    SECFiling8K,
    SECFilingSearchResult,
    SECFinancialFiling,
    SECProfile,
    SICCode,
)

SEC_FILINGS_8K: Endpoint = Endpoint(
    name="sec_filings_8k",
    path="sec-filings-8k",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get the latest SEC 8-K filings",
    mandatory_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECFiling8K,
    example_queries=[
        "Get latest 8-K filings",
        "Recent SEC 8-K forms",
        "Latest material event disclosures",
    ],
)

SEC_FILINGS_FINANCIALS: Endpoint = Endpoint(
    name="sec_filings_financials",
    path="sec-filings-financials",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get the latest SEC financial filings (10-K, 10-Q)",
    mandatory_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date (YYYY-MM-DD)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECFinancialFiling,
    example_queries=[
        "Get latest financial filings",
        "Recent 10-K and 10-Q forms",
        "Latest SEC financial reports",
    ],
)

SEC_FILINGS_SEARCH_FORM_TYPE: Endpoint = Endpoint(
    name="sec_filings_search_form_type",
    path="sec-filings-search/form-type",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC filings by form type",
    mandatory_params=[
        EndpointParam(
            name="formType",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="SEC form type (e.g., 10-K, 10-Q, 8-K)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECFilingSearchResult,
    example_queries=[
        "Search for all 10-K filings",
        "Find SEC forms by type",
        "Get filings of specific form type",
    ],
)

SEC_FILINGS_SEARCH_SYMBOL: Endpoint = Endpoint(
    name="sec_filings_search_symbol",
    path="sec-filings-search/symbol",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC filings by stock symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECFilingSearchResult,
    example_queries=[
        "Search SEC filings for AAPL",
        "Get all filings for a company",
        "Find SEC forms by symbol",
    ],
)

SEC_FILINGS_SEARCH_CIK: Endpoint = Endpoint(
    name="sec_filings_search_cik",
    path="sec-filings-search/cik",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC filings by CIK number",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="SEC CIK number",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECFilingSearchResult,
    example_queries=[
        "Search SEC filings by CIK",
        "Get filings using CIK number",
        "Find SEC forms by CIK",
    ],
)

SEC_COMPANY_SEARCH_NAME: Endpoint = Endpoint(
    name="sec_company_search_name",
    path="sec-filings-company-search/name",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC companies by name",
    mandatory_params=[
        EndpointParam(
            name="company",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company name or partial name",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=SECCompanySearchResult,
    example_queries=[
        "Search SEC companies by name",
        "Find companies named Apple",
        "Search for company in SEC database",
    ],
)

SEC_COMPANY_SEARCH_SYMBOL: Endpoint = Endpoint(
    name="sec_company_search_symbol",
    path="sec-filings-company-search/symbol",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC companies by stock symbol",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
    ],
    optional_params=[],
    response_model=SECCompanySearchResult,
    example_queries=[
        "Get SEC company info for AAPL",
        "Find company by symbol in SEC",
        "SEC company lookup by ticker",
    ],
)

SEC_COMPANY_SEARCH_CIK: Endpoint = Endpoint(
    name="sec_company_search_cik",
    path="sec-filings-company-search/cik",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search SEC companies by CIK number",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="SEC CIK number",
        ),
    ],
    optional_params=[],
    response_model=SECCompanySearchResult,
    example_queries=[
        "Get SEC company info by CIK",
        "Find company by CIK number",
        "SEC company lookup by CIK",
    ],
)

SEC_PROFILE: Endpoint[SECProfile] = Endpoint(
    name="sec_profile",
    path="sec-profile",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get SEC profile for a company",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
    ],
    optional_params=[],
    response_model=SECProfile,
    example_queries=[
        "Get SEC profile for AAPL",
        "Company SEC registration info",
        "SEC company profile",
    ],
)

SIC_LIST: Endpoint = Endpoint(
    name="sic_list",
    path="standard-industrial-classification-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get list of all Standard Industrial Classification (SIC) codes",
    mandatory_params=[],
    optional_params=[],
    response_model=SICCode,
    example_queries=[
        "Get all SIC codes",
        "List industrial classification codes",
        "SIC code directory",
    ],
)

INDUSTRY_CLASSIFICATION_SEARCH: Endpoint = Endpoint(
    name="industry_classification_search",
    path="industry-classification-search",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Search industry classification data",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Stock symbol",
        ),
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="SEC CIK number",
        ),
        EndpointParam(
            name="sicCode",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="SIC code",
        ),
    ],
    response_model=IndustryClassification,
    example_queries=[
        "Search industry classification for AAPL",
        "Find industry data by CIK",
        "Lookup classification by SIC code",
    ],
)

ALL_INDUSTRY_CLASSIFICATION: Endpoint = Endpoint(
    name="all_industry_classification",
    path="all-industry-classification",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get all industry classification data",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
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
    response_model=IndustryClassification,
    example_queries=[
        "Get all industry classification records",
        "List industry classifications",
        "Browse industry classification data",
    ],
)
