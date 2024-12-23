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
from fmp_data.company.schema import (
    AvailableIndexesArgs,
    BaseExchangeArg,
    BaseSearchArg,
    BaseSymbolArg,
    ETFListArgs,
    GeographicRevenueArgs,
    LogoArgs,
    ProductRevenueArgs,
    SearchArgs,
    StockListArgs,
    SymbolChangesArgs,
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

# Profile Endpoints
PROFILE = Endpoint(
    name="profile",
    path="profile/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get comprehensive company profile including financial metrics, description, "
        "sector, industry, contact information, and basic market data. Provides a "
        "complete overview of a company's business and current market status."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get Apple's company profile",
        "Show me Microsoft's company information",
        "What is Tesla's market cap and industry?",
        "Tell me about NVDA's business profile",
        "Get detailed information about Amazon",
    ],
)

CORE_INFORMATION = Endpoint(
    name="core_information",
    path="company-core-information",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve essential company information including CIK, exchange, SIC code, "
        "state of incorporation, and fiscal year details. Provides core regulatory "
        "and administrative information about a company."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get core information for Apple",
        "Show me Tesla's basic company details",
        "What is Microsoft's CIK number?",
        "Find Amazon's incorporation details",
        "Get regulatory information for Google",
    ],
)

# Search Endpoints
SEARCH = Endpoint(
    name="search",
    path="search",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Search for companies by name, ticker, or other identifiers. Returns matching "
        "companies with their basic information including symbol, name, and exchange. "
        "Useful for finding companies based on keywords or partial matches."
    ),
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
    arg_model=SearchArgs,
    example_queries=[
        "Search for companies with 'tech' in their name",
        "Find companies related to artificial intelligence",
        "Look up companies in the healthcare sector",
        "Search for banks listed on NYSE",
        "Find companies matching 'renewable energy'",
    ],
)
# Executive Information Endpoints
KEY_EXECUTIVES = Endpoint(
    name="key_executives",
    path="key-executives/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get detailed information about a company's key executives including their "
        "names, titles, compensation, and tenure. Provides insights into company "
        "leadership, management structure, and executive compensation."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "Who are Apple's key executives?",
        "Get Microsoft's management team",
        "Show me Tesla's executive leadership",
        "List Amazon's top executives and their compensation",
        "Get information about Google's CEO and management",
    ],
)

EXECUTIVE_COMPENSATION = Endpoint(
    name="executive_compensation",
    path="governance/executive_compensation",
    version=APIVersion.V4,
    description=(
        "Get detailed executive compensation data including salary, bonuses, stock "
        "awards, and total compensation. Provides insights into how company "
        "executives are compensated."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "What is Apple CEO's compensation?",
        "Show Microsoft executive pay",
        "Get Tesla executive compensation details",
        "How much are Amazon executives paid?",
        "Find Google executive salary information",
    ],
)

EMPLOYEE_COUNT = Endpoint(
    name="employee_count",
    path="historical/employee_count",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get historical employee count data for a company. Tracks how the company's "
        "workforce has changed over time, providing insights into company growth "
        "and operational scale."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "How many employees does Apple have?",
        "Show Microsoft's employee count history",
        "Get Tesla's workforce numbers over time",
        "Track Amazon's employee growth",
        "What is Google's historical employee count?",
    ],
)

STOCK_LIST = Endpoint(
    name="stock_list",
    path="stock/list",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available stocks with their basic information "
        "including symbol, name, price, and exchange details. Returns the complete "
        "universe of tradable stocks."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
    arg_model=StockListArgs,
    example_queries=[
        "Get a list of all available stocks",
        "Show me all tradable company symbols",
        "What stocks are available for trading?",
        "List all company tickers",
        "Get the complete list of stocks",
    ],
)

ETF_LIST = Endpoint(
    name="etf_list",
    path="etf/list",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a complete list of all available ETFs (Exchange Traded Funds) with their "
        "basic information. Provides a comprehensive view of tradable ETF products."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
    arg_model=ETFListArgs,
    example_queries=[
        "List all available ETFs",
        "Show me tradable ETF symbols",
        "What ETFs can I invest in?",
        "Get a complete list of ETFs",
        "Show all exchange traded funds",
    ],
)
AVAILABLE_INDEXES = Endpoint(
    name="available_indexes",
    path="symbol/available-indexes",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a comprehensive list of all available market indexes including major "
        "stock market indices, sector indexes, and other benchmark indicators. "
        "Provides information about tradable and trackable market indexes along "
        "with their basic details such as name, currency, and exchange."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=AvailableIndex,
    arg_model=AvailableIndexesArgs,
    example_queries=[
        "List all available market indexes",
        "Show me tradable market indices",
        "What stock market indexes are available?",
        "Get information about market indices",
        "Show all benchmark indexes",
    ],
)

EXCHANGE_SYMBOLS = Endpoint(
    name="exchange_symbols",
    path="symbol/{exchange}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get all symbols listed on a specific exchange. Returns detailed information "
        "about all securities trading on the specified exchange including stocks, "
        "ETFs, and other instruments."
    ),
    mandatory_params=[
        EndpointParam(
            name="exchange",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Exchange code (e.g., NYSE, NASDAQ)",
            valid_values=None,  # Will be validated by schema pattern
        )
    ],
    optional_params=[],
    response_model=ExchangeSymbol,
    arg_model=BaseExchangeArg,  # Updated to use the base class
    example_queries=[
        "List all symbols on NYSE",
        "Show me NASDAQ listed companies",
        "What securities trade on LSE?",
        "Get all stocks listed on TSX",
        "Show symbols available on ASX",
    ],
)

CIK_SEARCH = Endpoint(
    name="cik_search",
    path="cik-search",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Search for companies by their CIK (Central Index Key) number. Useful for "
        "finding companies using their SEC identifier and accessing regulatory filings."
    ),
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
    arg_model=BaseSearchArg,
    example_queries=[
        "Find company with CIK number 320193",
        "Search for company by CIK",
        "Look up SEC CIK information",
        "Get company details by CIK",
        "Find ticker symbol for CIK",
    ],
)

CUSIP_SEARCH = Endpoint(
    name="cusip_search",
    path="cusip",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Search for companies by their CUSIP (Committee on Uniform Securities "
        "Identification Procedures) number. Helps identify securities using their "
        "unique identifier."
    ),
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
    arg_model=BaseSearchArg,
    example_queries=[
        "Find company by CUSIP number",
        "Search securities using CUSIP",
        "Look up stock with CUSIP",
        "Get company information by CUSIP",
        "Find ticker for CUSIP",
    ],
)

ISIN_SEARCH = Endpoint(
    name="isin_search",
    path="search/isin",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Search for companies by their ISIN (International Securities Identification "
        "Number). Used to find securities using their globally unique identifier."
    ),
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
    arg_model=BaseSearchArg,
    example_queries=[
        "Find company by ISIN",
        "Search using ISIN number",
        "Look up stock with ISIN",
        "Get security details by ISIN",
        "Find ticker for ISIN",
    ],
)
# Symbol Related Endpoints
COMPANY_LOGO = Endpoint(
    name="company_logo",
    path="{symbol}.png",
    version=None,
    url_type=URLType.IMAGE,
    method=HTTPMethod.GET,
    description=(
        "Get the company's official logo image. Returns the URL to the company's "
        "logo in PNG format. Useful for displaying company branding, creating "
        "visual company profiles, or enhancing financial dashboards with "
        "company identification."
    ),
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
    arg_model=LogoArgs,
    example_queries=[
        "Get Apple's company logo",
        "Show me the logo for Microsoft",
        "Download Tesla's logo",
        "Fetch the company logo for Amazon",
        "Get Google's brand image",
    ],
)


# Company Operational Data
COMPANY_NOTES = Endpoint(
    name="company_notes",
    path="company-notes",
    version=APIVersion.V4,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Retrieve company financial notes and disclosures. These notes provide "
        "additional context and detailed explanations about company financial "
        "statements and important events."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get financial notes for Apple",
        "Show me Microsoft's company disclosures",
        "What are Tesla's financial statement notes?",
        "Find important disclosures for Amazon",
        "Get company notes for Google",
    ],
)

SHARE_FLOAT = Endpoint(
    name="share_float",
    path="shares_float",
    version=APIVersion.V4,
    description=(
        "Get current share float data including number of shares available for "
        "trading and percentage of total shares outstanding. Important for "
        "understanding stock liquidity and institutional ownership."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "What is Apple's share float?",
        "Get Microsoft's floating shares",
        "Show Tesla's share float percentage",
        "How many Amazon shares are floating?",
        "Get Google's share float information",
    ],
)

HISTORICAL_SHARE_FLOAT = Endpoint(
    name="historical_share_float",
    path="historical/shares_float",
    version=APIVersion.V4,
    description=(
        "Get historical share float data showing how the number of tradable shares "
        "has changed over time. Useful for analyzing changes in stock liquidity and "
        "institutional ownership patterns over time."
    ),
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
    arg_model=BaseSymbolArg,
    example_queries=[
        "Show historical share float for Tesla",
        "How has Apple's share float changed over time?",
        "Get Microsoft's historical floating shares",
        "Track Amazon's share float history",
        "Show changes in Google's share float",
    ],
)

ALL_SHARES_FLOAT = Endpoint(
    name="all_shares_float",
    path="shares_float/all",
    version=APIVersion.V4,
    description=(
        "Get share float data for all companies at once. Provides a comprehensive "
        "view of market-wide float data, useful for screening and comparing "
        "companies based on their float characteristics."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ShareFloat,
    arg_model=StockListArgs,  # Using StockListArgs since it's a no-parameter endpoint
    example_queries=[
        "Get share float data for all companies",
        "Show market-wide float information",
        "List float data across all stocks",
        "Compare share floats across companies",
        "Get complete market float data",
    ],
)

# Revenue Analysis Endpoints
PRODUCT_REVENUE_SEGMENTATION = Endpoint(
    name="product_revenue_segmentation",
    path="revenue-product-segmentation",
    version=APIVersion.V4,
    description=(
        "Get detailed revenue segmentation by product or service line. Shows how "
        "company revenue is distributed across different products and services, "
        "helping understand revenue diversification and key product contributions."
    ),
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
    response_model=ProductRevenueSegment,
    arg_model=ProductRevenueArgs,
    example_queries=[
        "Show Apple's revenue by product",
        "How is Microsoft's revenue split between products?",
        "Get Tesla's product revenue breakdown",
        "What are Amazon's main revenue sources?",
        "Show Google's revenue by service line",
    ],
)

GEOGRAPHIC_REVENUE_SEGMENTATION = Endpoint(
    name="geographic_revenue_segmentation",
    path="revenue-geographic-segmentation",
    version=APIVersion.V4,
    description=(
        "Get revenue segmentation by geographic region. Shows how company revenue "
        "is distributed across different countries and regions, providing insights "
        "into geographical diversification and market exposure."
    ),
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
    response_model=GeographicRevenueSegment,
    arg_model=GeographicRevenueArgs,
    example_queries=[
        "Show Apple's revenue by region",
        "How is Microsoft's revenue split geographically?",
        "Get Tesla's revenue by country",
        "What are Amazon's revenue sources by region?",
        "Show Google's geographic revenue distribution",
    ],
)


SYMBOL_CHANGES = Endpoint(
    name="symbol_changes",
    path="symbol_change",
    version=APIVersion.V4,
    description=(
        "Get historical record of company symbol changes. Tracks when and why "
        "companies changed their ticker symbols, useful for maintaining accurate "
        "historical data and understanding corporate actions."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=SymbolChange,
    arg_model=SymbolChangesArgs,
    example_queries=[
        "Show recent stock symbol changes",
        "List companies that changed their tickers",
        "Get history of symbol changes",
        "What companies changed their symbols?",
        "Track stock symbol modifications",
    ],
)
