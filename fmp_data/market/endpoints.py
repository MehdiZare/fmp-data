# fmp_data/market/endpoints.py
from fmp_data.market.models import (
    AvailableIndex,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    ISINResult,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
)
from fmp_data.market.schema import (
    AvailableIndexesArgs,
    BaseExchangeArg,
    BaseSearchArg,
    ETFListArgs,
    SearchArgs,
    StockListArgs,
)
from fmp_data.models import (
    APIVersion,
    CompanySymbol,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    ShareFloat,
    URLType,
)

STOCK_LIST: Endpoint = Endpoint(
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

ETF_LIST: Endpoint = Endpoint(
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
AVAILABLE_INDEXES: Endpoint = Endpoint(
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
SEARCH: Endpoint = Endpoint(
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
EXCHANGE_SYMBOLS: Endpoint = Endpoint(
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

CIK_SEARCH: Endpoint = Endpoint(
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

CUSIP_SEARCH: Endpoint = Endpoint(
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

ISIN_SEARCH: Endpoint = Endpoint(
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

MARKET_HOURS: Endpoint = Endpoint(
    name="market_hours",
    path="is-the-market-open",
    version=APIVersion.V3,
    description="Get market trading hours information",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketHours,
)

GAINERS: Endpoint = Endpoint(
    name="gainers",
    path="stock_market/gainers",
    version=APIVersion.V3,
    description="Get market gainers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

LOSERS: Endpoint = Endpoint(
    name="losers",
    path="stock_market/losers",
    version=APIVersion.V3,
    description="Get market losers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

MOST_ACTIVE: Endpoint = Endpoint(
    name="most_active",
    path="stock_market/actives",
    version=APIVersion.V3,
    description="Get most active stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

SECTOR_PERFORMANCE: Endpoint = Endpoint(
    name="sector_performance",
    path="sectors-performance",
    version=APIVersion.V3,
    description="Get sector performance data",
    mandatory_params=[],
    optional_params=[],
    response_model=SectorPerformance,
)

PRE_POST_MARKET: Endpoint = Endpoint(
    name="pre_post_market",
    path="pre-post-market",
    version=APIVersion.V4,
    description="Get pre/post market data",
    mandatory_params=[],
    optional_params=[],
    response_model=PrePostMarketQuote,
)

ALL_SHARES_FLOAT: Endpoint = Endpoint(
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
