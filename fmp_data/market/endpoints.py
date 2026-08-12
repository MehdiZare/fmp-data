# fmp_data/market/endpoints.py
from fmp_data.market.models import (
    AvailableIndex,
    CIKListEntry,
    CIKResult,
    CompanySearchResult,
    CUSIPResult,
    ExchangeSymbol,
    IndustryPerformance,
    IndustryPESnapshot,
    IPODisclosure,
    IPOProspectus,
    ISINResult,
    MarketHoliday,
    MarketHours,
    MarketMover,
    PrePostMarketQuote,
    SectorPerformance,
    SectorPESnapshot,
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
    path="stock-list",
    version=APIVersion.STABLE,
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
    path="etf-list",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get a complete list of all available ETFs (Exchange Traded Funds) with their "
        "basic information. Provides a comprehensive view of tradable ETF products."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
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
    path="index-list",
    version=APIVersion.STABLE,
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
    example_queries=[
        "List all available market indexes",
        "Show me tradable market indices",
        "What stock market indexes are available?",
        "Get information about market indices",
        "Show all benchmark indexes",
    ],
)
SEARCH_COMPANY: Endpoint = Endpoint(
    # ``name`` is snake_case like every other endpoint in the catalogue;
    # ``path`` keeps the hyphen because that is the real API path (#166).
    # Renaming ``name`` moved this endpoint's cache-key prefix and its
    # ``ttl_overrides`` key -- see the 2.6.0 CHANGELOG for the migration note.
    name="search_name",
    path="search-name",
    version=APIVersion.STABLE,
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
            description="Search query string",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of results",
            default=10,
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by exchange",
        ),
    ],
    response_model=CompanySearchResult,
    example_queries=[
        "Search for companies with 'tech' in their name",
        "Find companies related to artificial intelligence",
        "Look up companies in the healthcare sector",
        "Search for banks listed on NYSE",
        "Find companies matching 'renewable energy'",
    ],
)
CIK_SEARCH: Endpoint = Endpoint(
    name="cik_search",
    path="search-cik",
    version=APIVersion.STABLE,
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
            param_type=ParamType.CIK,
            description=(
                "CIK number to look up, e.g. 320193 or '0000320193'. This is "
                "not a free-text search: the API matches a CIK only, and "
                "rejects a company name with 400 'Invalid or missing query "
                "parameter - cik'. Sent on the wire as 'cik' via the alias."
            ),
            alias="cik",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Maximum number of results to return",
            default=50,
        ),
    ],
    response_model=CIKResult,
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
    path="search-cusip",
    version=APIVersion.STABLE,
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
            description="Search query",
            alias="cusip",
        )
    ],
    optional_params=[],
    response_model=CUSIPResult,
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
    path="search-isin",
    version=APIVersion.STABLE,
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
            description="Search query",
            alias="isin",
        )
    ],
    optional_params=[],
    response_model=ISINResult,
    example_queries=[
        "Find company by ISIN",
        "Search using ISIN number",
        "Look up stock with ISIN",
        "Get security details by ISIN",
        "Find ticker for ISIN",
    ],
)

MARKET_HOURS: Endpoint[MarketHours] = Endpoint(
    name="market_hours",
    path="exchange-market-hours",
    version=APIVersion.STABLE,
    description="Get market trading hours information",
    mandatory_params=[
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
            valid_values=None,
        )
    ],
    optional_params=[],
    response_model=MarketHours,
)

ALL_EXCHANGE_MARKET_HOURS: Endpoint[MarketHours] = Endpoint(
    name="all_exchange_market_hours",
    path="all-exchange-market-hours",
    version=APIVersion.STABLE,
    description="Get market trading hours for all exchanges",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketHours,
)

HOLIDAYS_BY_EXCHANGE: Endpoint = Endpoint(
    name="holidays_by_exchange",
    path="holidays-by-exchange",
    version=APIVersion.STABLE,
    description="Get market holidays for a specific exchange",
    mandatory_params=[
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
            valid_values=None,
        )
    ],
    optional_params=[],
    response_model=MarketHoliday,
)

GAINERS: Endpoint = Endpoint(
    name="gainers",
    path="biggest-gainers",
    version=APIVersion.STABLE,
    description="Get market gainers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

LOSERS: Endpoint = Endpoint(
    name="losers",
    path="biggest-losers",
    version=APIVersion.STABLE,
    description="Get market losers",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

MOST_ACTIVE: Endpoint = Endpoint(
    name="most_active",
    path="most-actives",
    version=APIVersion.STABLE,
    description="Get most active stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=MarketMover,
)

SECTOR_PERFORMANCE: Endpoint = Endpoint(
    name="sector_performance",
    path="sector-performance-snapshot",
    version=APIVersion.STABLE,
    description="Get sector performance data",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Snapshot date (YYYY-MM-DD)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sector code (e.g., 'Technology')",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=SectorPerformance,
)

INDUSTRY_PERFORMANCE_SNAPSHOT: Endpoint = Endpoint(
    name="industry_performance_snapshot",
    path="industry-performance-snapshot",
    version=APIVersion.STABLE,
    description="Get industry performance data",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Snapshot date (YYYY-MM-DD)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Industry name (e.g., 'Biotechnology')",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=IndustryPerformance,
)

HISTORICAL_SECTOR_PERFORMANCE: Endpoint = Endpoint(
    name="historical_sector_performance",
    path="historical-sector-performance",
    version=APIVersion.STABLE,
    description="Get historical sector performance data",
    mandatory_params=[
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sector name (e.g., 'Energy')",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=SectorPerformance,
)

HISTORICAL_INDUSTRY_PERFORMANCE: Endpoint = Endpoint(
    name="historical_industry_performance",
    path="historical-industry-performance",
    version=APIVersion.STABLE,
    description="Get historical industry performance data",
    mandatory_params=[
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Industry name (e.g., 'Biotechnology')",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=IndustryPerformance,
)

SECTOR_PE_SNAPSHOT: Endpoint = Endpoint(
    name="sector_pe_snapshot",
    path="sector-pe-snapshot",
    version=APIVersion.STABLE,
    description="Get sector PE snapshot data",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Snapshot date (YYYY-MM-DD)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sector name (e.g., 'Energy')",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=SectorPESnapshot,
)

INDUSTRY_PE_SNAPSHOT: Endpoint = Endpoint(
    name="industry_pe_snapshot",
    path="industry-pe-snapshot",
    version=APIVersion.STABLE,
    description="Get industry PE snapshot data",
    mandatory_params=[
        EndpointParam(
            name="date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Snapshot date (YYYY-MM-DD)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Industry name (e.g., 'Biotechnology')",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=IndustryPESnapshot,
)

HISTORICAL_SECTOR_PE: Endpoint = Endpoint(
    name="historical_sector_pe",
    path="historical-sector-pe",
    version=APIVersion.STABLE,
    description="Get historical sector PE data",
    mandatory_params=[
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Sector name (e.g., 'Energy')",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=SectorPESnapshot,
)

HISTORICAL_INDUSTRY_PE: Endpoint = Endpoint(
    name="historical_industry_pe",
    path="historical-industry-pe",
    version=APIVersion.STABLE,
    description="Get historical industry PE data",
    mandatory_params=[
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Industry name (e.g., 'Biotechnology')",
        )
    ],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Exchange code (e.g., NYSE, NASDAQ)",
        ),
    ],
    response_model=IndustryPESnapshot,
)

PRE_POST_MARKET: Endpoint = Endpoint(
    name="pre_post_market",
    path="pre-post-market",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: pre-post-market 404s, and the "
        "market-wide shape no longer exists. Do not select it. Live "
        "extended-hours data is per symbol via aftermarket-quote, or "
        "batch-aftermarket-quote with a mandatory symbols parameter."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=PrePostMarketQuote,
)

ALL_SHARES_FLOAT: Endpoint = Endpoint(
    name="all_shares_float",
    path="shares-float-all",
    version=APIVersion.STABLE,
    description=(
        "Get share float data for all companies at once. Provides a comprehensive "
        "view of market-wide float data, useful for screening and comparing "
        "companies based on their float characteristics."
    ),
    mandatory_params=[],
    optional_params=[],
    response_model=ShareFloat,
    example_queries=[
        "Get share float data for all companies",
        "Show market-wide float information",
        "List float data across all stocks",
        "Compare share floats across companies",
        "Get complete market float data",
    ],
)

FINANCIAL_STATEMENT_SYMBOL_LIST: Endpoint = Endpoint(
    name="financial_statement_symbol_list",
    path="financial-statement-symbol-list",
    version=APIVersion.STABLE,
    description="Get list of symbols with financial statements available",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

CIK_LIST: Endpoint = Endpoint(
    name="cik_list",
    path="cik-list",
    version=APIVersion.STABLE,
    description="Get complete list of all CIK numbers",
    mandatory_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Page number",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results per page",
        ),
    ],
    optional_params=[],
    response_model=CIKListEntry,
)

ACTIVELY_TRADING_LIST: Endpoint = Endpoint(
    name="actively_trading_list",
    path="actively-trading-list",
    version=APIVersion.STABLE,
    description="Get list of actively trading stocks",
    mandatory_params=[],
    optional_params=[],
    response_model=CompanySymbol,
)

TRADABLE_SEARCH: Endpoint = Endpoint(
    name="tradable_search",
    path="tradable-list",
    version=APIVersion.STABLE,
    description=(
        "DEPRECATED and non-functional: tradable-list 404s and has no "
        "drop-in replacement -- available-traded/list, symbol-list, "
        "tradable-symbol-list and symbol/all all 404 too. Do not select it. "
        "stock-list, etf-list and actively-trading-list are partial "
        "substitutes covering different universes."
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results to return",
        ),
        EndpointParam(
            name="offset",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Offset for pagination",
        ),
    ],
    response_model=CompanySymbol,
)

SEARCH_SYMBOL: Endpoint = Endpoint(
    name="search_symbol",
    path="search-symbol",
    version=APIVersion.STABLE,
    description="Search for security symbols across all asset types",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Search query",
        )
    ],
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results to return",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter results by exchange (e.g., NASDAQ)",
        ),
    ],
    response_model=CompanySearchResult,
)

COMPANY_SCREENER: Endpoint = Endpoint(
    name="company_screener",
    path="company-screener",
    version=APIVersion.STABLE,
    description="Screen companies based on various criteria",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="market_cap_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Market cap greater than",
            alias="marketCapMoreThan",
        ),
        EndpointParam(
            name="market_cap_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Market cap less than",
            alias="marketCapLowerThan",
        ),
        EndpointParam(
            name="price_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Price greater than",
            alias="priceMoreThan",
        ),
        EndpointParam(
            name="price_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Price less than",
            alias="priceLowerThan",
        ),
        EndpointParam(
            name="beta_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Beta greater than",
            alias="betaMoreThan",
        ),
        EndpointParam(
            name="beta_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Beta less than",
            alias="betaLowerThan",
        ),
        EndpointParam(
            name="volume_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Volume greater than",
            alias="volumeMoreThan",
        ),
        EndpointParam(
            name="volume_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Volume less than",
            alias="volumeLowerThan",
        ),
        EndpointParam(
            name="dividend_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Dividend yield greater than",
            alias="dividendMoreThan",
        ),
        EndpointParam(
            name="dividend_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            description="Dividend yield less than",
            alias="dividendLowerThan",
        ),
        EndpointParam(
            name="is_etf",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description="Filter for ETFs",
            alias="isEtf",
        ),
        EndpointParam(
            name="is_fund",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description="Filter for funds",
            alias="isFund",
        ),
        EndpointParam(
            name="is_actively_trading",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description="Filter for actively trading symbols",
            alias="isActivelyTrading",
        ),
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by sector",
        ),
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by industry",
        ),
        EndpointParam(
            name="country",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by country",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Filter by exchange",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results to return",
        ),
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description=(
                "Zero-based page of screener results. Omitted from the "
                "request when unset so existing callers keep their wire shape."
            ),
        ),
        EndpointParam(
            name="include_all_share_classes",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            description="Include all share classes in results",
            alias="includeAllShareClasses",
        ),
    ],
    response_model=CompanySearchResult,
)

SEARCH_EXCHANGE_VARIANTS: Endpoint = Endpoint(
    name="search_exchange_variants",
    path="search-exchange-variants",
    version=APIVersion.STABLE,
    description="Search for exchange trading variants of a company",
    mandatory_params=[
        EndpointParam(
            name="query",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Company name or symbol to search",
        )
    ],
    optional_params=[],
    response_model=CompanySearchResult,
)

AVAILABLE_EXCHANGES: Endpoint = Endpoint(
    name="available_exchanges",
    path="available-exchanges",
    version=APIVersion.STABLE,
    description="Get a complete list of supported stock exchanges",
    mandatory_params=[],
    optional_params=[],
    response_model=ExchangeSymbol,
)

AVAILABLE_SECTORS: Endpoint = Endpoint(
    name="available_sectors",
    path="available-sectors",
    version=APIVersion.STABLE,
    description="Get a complete list of industry sectors",
    mandatory_params=[],
    optional_params=[],
    response_model=str,  # Returns list of strings
)

AVAILABLE_INDUSTRIES: Endpoint = Endpoint(
    name="available_industries",
    path="available-industries",
    version=APIVersion.STABLE,
    description="Get a comprehensive list of available industries",
    mandatory_params=[],
    optional_params=[],
    response_model=str,  # Returns list of strings
)

AVAILABLE_COUNTRIES: Endpoint = Endpoint(
    name="available_countries",
    path="available-countries",
    version=APIVersion.STABLE,
    description="Get a comprehensive list of available countries",
    mandatory_params=[],
    optional_params=[],
    response_model=str,  # Returns list of strings
)

IPO_DISCLOSURE: Endpoint = Endpoint(
    name="ipo_disclosure",
    path="ipos-disclosure",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get IPO disclosure documents and filing information for companies "
        "going public. Includes disclosure URLs, filing dates, and IPO details."
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date for IPO search (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date for IPO search (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results to return",
            default=100,
        ),
    ],
    response_model=IPODisclosure,
    example_queries=[
        "Get recent IPO disclosure documents",
        "Show IPO filings from last month",
        "Find disclosure documents for upcoming IPOs",
        "Get IPO disclosure URLs",
    ],
)

IPO_PROSPECTUS: Endpoint = Endpoint(
    name="ipo_prospectus",
    path="ipos-prospectus",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get IPO prospectus documents and detailed offering information for companies "
        "going public. Includes prospectus URLs, offer prices, and proceeds data."
    ),
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="Start date for IPO search (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="to",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            description="End date for IPO search (YYYY-MM-DD)",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Number of results to return",
            default=100,
        ),
    ],
    response_model=IPOProspectus,
    example_queries=[
        "Get IPO prospectus documents",
        "Show prospectus for recent IPOs",
        "Find offering details for upcoming IPOs",
        "Get IPO pricing and proceeds information",
    ],
)
