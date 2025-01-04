# fmp_data/company/mapping.py

from fmp_data.company.endpoints import (
    ALL_SHARES_FLOAT,
    AVAILABLE_INDEXES,
    CIK_SEARCH,
    COMPANY_LOGO,
    COMPANY_NOTES,
    CORE_INFORMATION,
    CUSIP_SEARCH,
    EMPLOYEE_COUNT,
    ETF_LIST,
    EXCHANGE_SYMBOLS,
    EXECUTIVE_COMPENSATION,
    GEOGRAPHIC_REVENUE_SEGMENTATION,
    HISTORICAL_SHARE_FLOAT,
    ISIN_SEARCH,
    KEY_EXECUTIVES,
    PRODUCT_REVENUE_SEGMENTATION,
    PROFILE,
    SEARCH,
    SHARE_FLOAT,
    STOCK_LIST,
    SYMBOL_CHANGES,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

IDENTIFIER_HINT = ParameterHint(
    natural_names=["identifier", "ID", "number"],
    extraction_patterns=[
        r"\b\d{6,10}\b",  # CIK numbers
        r"\b[0-9A-Z]{9}\b",  # CUSIP
        r"\b[A-Z]{2}[A-Z0-9]{9}\d\b",  # ISIN
    ],
    examples=["320193", "037833100", "US0378331005"],
    context_clues=["number", "identifier", "ID", "code"],
)

LIMIT_HINT = ParameterHint(
    natural_names=["limit", "max results", "number of results"],
    extraction_patterns=[
        r"(?:limit|show|get|return)\s+(\d+)",
        r"top\s+(\d+)",
        r"first\s+(\d+)",
    ],
    examples=["10", "25", "50"],
    context_clues=["limit", "maximum", "top", "first", "up to"],
)

STRUCTURE_HINT = ParameterHint(
    natural_names=["structure", "format", "data format"],
    extraction_patterns=[r"\b(flat|nested)\b"],
    examples=["flat", "nested"],
    context_clues=["structure", "format", "organize", "arrangement"],
)

PERIOD_HINT = ParameterHint(
    natural_names=["period", "frequency", "timeframe"],
    extraction_patterns=[r"\b(annual|quarter|quarterly)\b"],
    examples=["annual", "quarter"],
    context_clues=["period", "frequency", "annually", "quarterly"],
)

# Symbol related hints
SYMBOL_HINT = ParameterHint(
    natural_names=["ticker", "symbol", "stock", "company"],
    extraction_patterns=[
        r"\b[A-Z]{1,5}\b",
        r"(?:for|of)\s+([A-Z]{1,5})",
        r"([A-Z]{1,5})(?:'s|')",
    ],
    examples=["AAPL", "MSFT", "GOOG", "TSLA", "AMZN"],
    context_clues=["for", "about", "'s", "of", "company", "stock"],
)

EXCHANGE_HINT = ParameterHint(
    natural_names=["exchange", "market", "trading venue"],
    extraction_patterns=[
        r"\b(NYSE|NASDAQ|LSE|TSX|ASX)\b",
        r"(?:on|at)\s+(the\s+)?([A-Z]{2,6})",
    ],
    examples=["NYSE", "NASDAQ", "LSE", "TSX"],
    context_clues=["on", "listed on", "trading on", "exchange", "market"],
)

SEARCH_HINT = ParameterHint(
    natural_names=["search term", "query", "keyword"],
    extraction_patterns=[
        r"(?:search|find|look up)\s+(.+?)(?:\s+in|\s+on|\s*$)",
        r"(?:about|related to)\s+(.+?)(?:\s+in|\s+on|\s*$)",
    ],
    examples=["tech companies", "renewable energy", "artificial intelligence"],
    context_clues=["search", "find", "look up", "about", "related to"],
)

PERIOD_HINT = ParameterHint(
    natural_names=["period", "timeframe", "frequency"],
    extraction_patterns=[
        r"\b(annual|quarterly)\b",
        r"(?:by|per)\s+(year|quarter)",
    ],
    examples=["annual", "quarter"],
    context_clues=["annual", "quarterly", "year", "quarter"],
)

# Common response field hints
PROFILE_RESPONSE_HINTS = {
    "price": ResponseFieldInfo(
        description="Current stock price",
        examples=["150.25", "3500.00"],
        related_terms=["stock price", "trading price", "share price", "current price"],
    ),
    "market_cap": ResponseFieldInfo(
        description="Company's market capitalization",
        examples=["2.5T", "800B"],
        related_terms=["market value", "company worth", "capitalization", "market cap"],
    ),
    "beta": ResponseFieldInfo(
        description="Stock's beta value (market correlation)",
        examples=["1.2", "0.8"],
        related_terms=["volatility", "market correlation", "risk measure"],
    ),
}

FINANCIAL_RESPONSE_HINTS = {
    "revenue": ResponseFieldInfo(
        description="Company's revenue/sales",
        examples=["$365.8B", "$115.5M"],
        related_terms=["sales", "income", "earnings", "top line"],
    ),
    "employees": ResponseFieldInfo(
        description="Number of employees",
        examples=["164,000", "25,000"],
        related_terms=["workforce", "staff", "personnel", "headcount"],
    ),
}

EXECUTIVE_RESPONSE_HINTS = {
    "name": ResponseFieldInfo(
        description="Executive's name",
        examples=["Tim Cook", "Satya Nadella"],
        related_terms=["CEO", "executive", "officer", "management"],
    ),
    "compensation": ResponseFieldInfo(
        description="Executive compensation",
        examples=["$15.7M", "$40.2M"],
        related_terms=["salary", "pay", "remuneration", "earnings"],
    ),
}

FLOAT_RESPONSE_HINTS = {
    "float_shares": ResponseFieldInfo(
        description="Number of shares available for trading",
        examples=["5.2B", "750M"],
        related_terms=["floating shares", "tradable shares", "public float"],
    ),
    "float_percentage": ResponseFieldInfo(
        description="Percentage of shares available for trading",
        examples=["85.5%", "45.2%"],
        related_terms=["float ratio", "public float percentage", "tradable ratio"],
    ),
}

# Company endpoints mapping
COMPANY_ENDPOINT_MAP = {
    "get_profile": PROFILE,
    "get_core_information": CORE_INFORMATION,
    "search": SEARCH,
    "get_executives": KEY_EXECUTIVES,
    "get_company_notes": COMPANY_NOTES,
    "get_employee_count": EMPLOYEE_COUNT,
    "get_stock_list": STOCK_LIST,
    "get_etf_list": ETF_LIST,
    "get_available_indexes": AVAILABLE_INDEXES,
    "get_exchange_symbols": EXCHANGE_SYMBOLS,
    "search_by_cik": CIK_SEARCH,
    "search_by_cusip": CUSIP_SEARCH,
    "search_by_isin": ISIN_SEARCH,
    "get_company_logo_url": COMPANY_LOGO,
    "get_executive_compensation": EXECUTIVE_COMPENSATION,
    "get_share_float": SHARE_FLOAT,
    "get_historical_share_float": HISTORICAL_SHARE_FLOAT,
    "get_all_shares_float": ALL_SHARES_FLOAT,
    "get_product_revenue_segmentation": PRODUCT_REVENUE_SEGMENTATION,
    "get_geographic_revenue_segmentation": GEOGRAPHIC_REVENUE_SEGMENTATION,
    "get_symbol_changes": SYMBOL_CHANGES,
}

# Complete semantic definitions for all endpoints
COMPANY_ENDPOINTS_SEMANTICS = {
    "profile": EndpointSemantics(
        client_name="company",
        method_name="get_profile",
        natural_description=(
            "Get detailed company profile information including financial metrics, "
            "company description, sector, industry, and contact information"
        ),
        example_queries=[
            "Get Apple's company profile",
            "Show me Microsoft's company information",
            "What is Tesla's market cap and industry?",
            "Tell me about NVDA's business profile",
            "Get company details for Amazon",
        ],
        related_terms=[
            "company profile",
            "business overview",
            "company information",
            "corporate details",
            "company facts",
            "business description",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints=PROFILE_RESPONSE_HINTS,
        use_cases=[
            "Understanding company basics",
            "Investment research",
            "Company valuation",
            "Industry analysis",
            "Competitor comparison",
        ],
    ),
    "core_information": EndpointSemantics(
        client_name="company",
        method_name="get_core_information",
        natural_description=(
            "Get essential company information including CIK number, exchange listing, "
            "SIC code, state of incorporation, and fiscal year details"
        ),
        example_queries=[
            "Get core information for Apple",
            "Show me Tesla's basic company details",
            "What is Microsoft's CIK number?",
            "Find Amazon's incorporation details",
            "Get regulatory information for Google",
        ],
        related_terms=[
            "basic information",
            "company details",
            "regulatory info",
            "incorporation details",
            "company registration",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "cik": ResponseFieldInfo(
                description="SEC Central Index Key",
                examples=["0000320193", "0001318605"],
                related_terms=["SEC identifier", "registration number"],
            ),
            "sic_code": ResponseFieldInfo(
                description="Standard Industrial Classification code",
                examples=["7370", "3711"],
                related_terms=["industry code", "sector classification"],
            ),
        },
        use_cases=[
            "Regulatory compliance",
            "SEC filing research",
            "Industry classification",
            "Company registration lookup",
        ],
    ),
    "stock_list": EndpointSemantics(
        client_name="company",
        method_name="get_stock_list",
        natural_description=(
            "Get a comprehensive list of all available stocks with their basic "
            "information including symbol, name, and exchange details"
        ),
        example_queries=[
            "Get a list of all available stocks",
            "Show me all tradable company symbols",
            "What stocks are available for trading?",
            "List all company tickers",
            "Get the complete list of stocks",
        ],
        related_terms=[
            "stocks",
            "securities",
            "tradable companies",
            "listed companies",
            "stock symbols",
            "tickers",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock trading symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "stock symbol", "trading symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Company name",
                examples=["Apple Inc", "Microsoft Corporation"],
                related_terms=["company name", "business name", "corporation name"],
            ),
        },
        use_cases=[
            "Finding available stocks to trade",
            "Market analysis",
            "Building stock screeners",
            "Portfolio management",
        ],
    ),
    "search": EndpointSemantics(
        client_name="company",
        method_name="search",
        natural_description=(
            "Search for companies by name, ticker, " "or other identifiers."
        ),
        example_queries=[
            "Search for companies with 'tech' in their name",
            "Find companies related to artificial intelligence",
            "Look up companies in the healthcare sector",
            "Search for banks listed on NYSE",
            "Find companies matching 'renewable energy'",
        ],
        related_terms=[
            "company search",
            "find companies",
            "lookup businesses",
            "search stocks",
            "find tickers",
            "company lookup",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={
            "query": SEARCH_HINT,
            "limit": LIMIT_HINT,
            "exchange": EXCHANGE_HINT,
        },
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Company stock symbol",
                examples=["AAPL", "MSFT", "GOOGL"],
                related_terms=["ticker", "stock symbol", "company symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Full company name",
                examples=["Apple Inc.", "Microsoft Corporation"],
                related_terms=["company name", "business name", "organization"],
            ),
            "exchange": ResponseFieldInfo(
                description="Stock exchange where company is listed",
                examples=["NASDAQ", "NYSE"],
                related_terms=["listing exchange", "market", "trading venue"],
            ),
        },
        use_cases=[
            "Finding companies by keyword",
            "Sector research",
            "Competitor analysis",
            "Investment screening",
            "Market research",
        ],
    ),
    "share_float": EndpointSemantics(
        client_name="company",
        method_name="get_share_float",
        natural_description=(
            "Get current share float data showing the number and percentage of "
            "shares available for public trading"
        ),
        example_queries=[
            "What is Apple's share float?",
            "Get Microsoft's floating shares",
            "Show Tesla's share float percentage",
            "How many Amazon shares are floating?",
            "Get Google's share float information",
        ],
        related_terms=[
            "floating shares",
            "public float",
            "tradable shares",
            "share availability",
            "stock float",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Float",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints=FLOAT_RESPONSE_HINTS,
        use_cases=[
            "Liquidity analysis",
            "Trading volume research",
            "Short interest analysis",
            "Institutional ownership tracking",
        ],
    ),
    "product_revenue_segmentation": EndpointSemantics(
        client_name="company",
        method_name="get_product_revenue_segmentation",
        natural_description=(
            "Get detailed revenue breakdown by product lines or services, showing "
            "how company revenue is distributed across different offerings"
        ),
        example_queries=[
            "Show Apple's revenue by product",
            "How is Microsoft's revenue split between products?",
            "Get Tesla's product revenue breakdown",
            "What are Amazon's main revenue sources?",
            "Show Google's revenue by service line",
        ],
        related_terms=[
            "revenue breakdown",
            "product mix",
            "service revenue",
            "revenue sources",
            "product sales",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Revenue",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "structure": STRUCTURE_HINT,
            "period": PERIOD_HINT,
        },
        response_hints={
            "segments": ResponseFieldInfo(
                description="Revenue by product/service",
                examples=["iPhone: $191.2B", "AWS: $80.1B"],
                related_terms=["product revenue", "segment sales", "line items"],
            )
        },
        use_cases=[
            "Product performance analysis",
            "Revenue diversification study",
            "Business segment analysis",
            "Growth trend identification",
        ],
    ),
    "geographic_revenue_segmentation": EndpointSemantics(
        client_name="company",
        method_name="get_geographic_revenue_segmentation",
        natural_description=(
            "Get revenue breakdown by geographic regions, showing how company "
            "revenue is distributed across different countries and regions"
        ),
        example_queries=[
            "Show Apple's revenue by region",
            "How is Microsoft's revenue split geographically?",
            "Get Tesla's revenue by country",
            "What are Amazon's revenue sources by region?",
            "Show Google's geographic revenue distribution",
        ],
        related_terms=[
            "regional revenue",
            "geographic breakdown",
            "country revenue",
            "international sales",
            "regional sales",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Revenue",
        parameter_hints={"symbol": SYMBOL_HINT, "structure": STRUCTURE_HINT},
        response_hints={
            "segments": ResponseFieldInfo(
                description="Revenue by region",
                examples=["Americas: $169.6B", "Europe: $95.1B"],
                related_terms=[
                    "regional revenue",
                    "geographic sales",
                    "country revenue",
                ],
            )
        },
        use_cases=[
            "Geographic exposure analysis",
            "International market research",
            "Regional performance tracking",
            "Market penetration study",
        ],
    ),
    "etf_list": EndpointSemantics(
        client_name="company",
        method_name="get_etf_list",
        natural_description=(
            "Get a complete list of all available "
            "ETFs (Exchange Traded Funds) with their "
            "basic information including symbol, "
            "name, and trading details"
        ),
        example_queries=[
            "List all available ETFs",
            "Show me tradable ETF symbols",
            "What ETFs can I invest in?",
            "Get a complete list of ETFs",
            "Show all exchange traded funds",
        ],
        related_terms=[
            "exchange traded funds",
            "ETFs",
            "index funds",
            "traded funds",
            "fund listings",
            "investment vehicles",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Lists",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="ETF trading symbol",
                examples=["SPY", "QQQ", "VTI"],
                related_terms=["ETF symbol", "fund ticker", "trading symbol"],
            ),
            "name": ResponseFieldInfo(
                description="ETF name",
                examples=["SPDR S&P 500 ETF", "Invesco QQQ Trust"],
                related_terms=["fund name", "ETF name", "product name"],
            ),
        },
        use_cases=[
            "ETF research",
            "Fund selection",
            "Portfolio diversification",
            "Investment screening",
        ],
    ),
    "available_indexes": EndpointSemantics(
        client_name="company",
        method_name="get_available_indexes",
        natural_description=(
            "Get a list of all available market indexes including major stock market "
            "indices, sector indexes, and other benchmark indicators"
        ),
        example_queries=[
            "List all available market indexes",
            "Show me tradable market indices",
            "What stock market indexes are available?",
            "Get information about market indices",
            "Show all benchmark indexes",
        ],
        related_terms=[
            "market indices",
            "stock indexes",
            "benchmarks",
            "market indicators",
            "sector indices",
            "composite indexes",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Lists",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Index symbol",
                examples=["^GSPC", "^DJI", "^IXIC"],
                related_terms=["index symbol", "benchmark code", "indicator symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Index name",
                examples=["S&P 500", "Dow Jones Industrial Average"],
                related_terms=["index name", "benchmark name", "indicator name"],
            ),
        },
        use_cases=[
            "Market analysis",
            "Benchmark selection",
            "Index tracking",
            "Performance comparison",
        ],
    ),
    "key_executives": EndpointSemantics(
        client_name="company",
        method_name="get_executives",
        natural_description=(
            "Get detailed information about company's key executives including their "
            "names, titles, tenure, and basic compensation data"
        ),
        example_queries=[
            "Who are Apple's key executives?",
            "Get Microsoft's management team",
            "Show me Tesla's executive leadership",
            "List Amazon's top executives",
            "Get information about Google's CEO",
        ],
        related_terms=[
            "executives",
            "management team",
            "leadership",
            "officers",
            "C-suite",
            "senior management",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Executive",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "name": ResponseFieldInfo(
                description="Executive name",
                examples=["Tim Cook", "Satya Nadella"],
                related_terms=["executive name", "officer name", "leader name"],
            ),
            "title": ResponseFieldInfo(
                description="Executive position",
                examples=["Chief Executive Officer", "Chief Financial Officer"],
                related_terms=["position", "role", "job title"],
            ),
        },
        use_cases=[
            "Management analysis",
            "Corporate governance research",
            "Leadership assessment",
            "Executive background check",
        ],
    ),
    "company_notes": EndpointSemantics(
        client_name="company",
        method_name="get_company_notes",
        natural_description=(
            "Retrieve company financial notes and "
            "disclosures from SEC filings, providing "
            "additional context and explanations "
            "about financial statements"
        ),
        example_queries=[
            "Get financial notes for Apple",
            "Show me Microsoft's company disclosures",
            "What are Tesla's financial statement notes?",
            "Find important disclosures for Amazon",
            "Get company notes for Google",
        ],
        related_terms=[
            "financial notes",
            "disclosures",
            "SEC notes",
            "financial statements",
            "accounting notes",
            "regulatory filings",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "title": ResponseFieldInfo(
                description="Note title or subject",
                examples=["Revenue Recognition", "Segment Information"],
                related_terms=["note title", "disclosure topic", "subject"],
            ),
            "content": ResponseFieldInfo(
                description="Note content",
                examples=["The Company recognizes revenue...", "Segment data..."],
                related_terms=["description", "explanation", "details"],
            ),
        },
        use_cases=[
            "Financial analysis",
            "Regulatory compliance check",
            "Accounting research",
            "Risk assessment",
        ],
    ),
    "employee_count": EndpointSemantics(
        client_name="company",
        method_name="get_employee_count",
        natural_description=(
            "Get historical employee count data showing how company workforce has "
            "changed over time"
        ),
        example_queries=[
            "How many employees does Apple have?",
            "Show Microsoft's employee count history",
            "Get Tesla's workforce numbers",
            "Track Amazon's employee growth",
            "What is Google's historical employee count?",
        ],
        related_terms=[
            "workforce size",
            "employee numbers",
            "staff count",
            "headcount",
            "personnel count",
            "employment figures",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "count": ResponseFieldInfo(
                description="Number of employees",
                examples=["164,000", "100,000"],
                related_terms=["headcount", "workforce size", "staff number"],
            ),
            "date": ResponseFieldInfo(
                description="Report date",
                examples=["2023-12-31", "2022-09-30"],
                related_terms=["filing date", "report period", "as of date"],
            ),
        },
        use_cases=[
            "Company growth analysis",
            "Workforce trend tracking",
            "Operational scale assessment",
            "Industry comparison",
        ],
    ),
    "historical_share_float": EndpointSemantics(
        client_name="company",
        method_name="get_historical_share_float",
        natural_description=(
            "Get historical share float data showing how the number of tradable shares "
            "has changed over time"
        ),
        example_queries=[
            "Show historical share float for Tesla",
            "How has Apple's share float changed over time?",
            "Get Microsoft's historical floating shares",
            "Track Amazon's share float history",
            "Show changes in Google's share float",
        ],
        related_terms=[
            "historical float",
            "float history",
            "share availability",
            "trading volume history",
            "liquidity history",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Float",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints=FLOAT_RESPONSE_HINTS,
        use_cases=[
            "Liquidity trend analysis",
            "Ownership pattern research",
            "Trading volume analysis",
            "Market dynamics study",
        ],
    ),
    "symbol_changes": EndpointSemantics(
        client_name="company",
        method_name="get_symbol_changes",
        natural_description=(
            "Get historical record of company ticker symbol changes, tracking when and "
            "why companies changed their trading symbols"
        ),
        example_queries=[
            "Show recent stock symbol changes",
            "List companies that changed their tickers",
            "Get history of symbol changes",
            "What companies changed their symbols?",
            "Track stock symbol modifications",
        ],
        related_terms=[
            "ticker changes",
            "symbol modifications",
            "name changes",
            "trading symbol updates",
            "stock symbol history",
        ],
        category=SemanticCategory.COMPANY_INFO,
        parameter_hints={},  # No parameters needed
        response_hints={
            "old_symbol": ResponseFieldInfo(
                description="Previous trading symbol",
                examples=["FB", "TWTR"],
                related_terms=["old ticker", "previous symbol", "former symbol"],
            ),
            "new_symbol": ResponseFieldInfo(
                description="New trading symbol",
                examples=["META", "X"],
                related_terms=["new ticker", "current symbol", "updated symbol"],
            ),
        },
        use_cases=[
            "Corporate action tracking",
            "Historical data analysis",
            "Market research",
            "Database maintenance",
        ],
    ),
    "executives": EndpointSemantics(
        client_name="company",
        method_name="get_executives",
        natural_description=(
            "Get detailed information about company's key executives including their "
            "names, titles, compensation, and tenure."
        ),
        example_queries=[
            "Who are Apple's key executives?",
            "Get Microsoft's management team",
            "Show me Tesla's executive leadership",
            "List Amazon's top executives",
            "Get information about Google's CEO",
        ],
        related_terms=[
            "executives",
            "management team",
            "leadership",
            "officers",
            "C-suite",
            "senior management",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Executive",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "name": ResponseFieldInfo(
                description="Executive name",
                examples=["Tim Cook", "Satya Nadella"],
                related_terms=["name", "executive name", "officer name"],
            ),
            "title": ResponseFieldInfo(
                description="Executive position",
                examples=["Chief Executive Officer", "Chief Financial Officer"],
                related_terms=["position", "role", "title", "job"],
            ),
        },
        use_cases=[
            "Management analysis",
            "Corporate governance research",
            "Leadership assessment",
            "Executive background check",
        ],
    ),
    "exchange_symbols": EndpointSemantics(
        client_name="company",
        method_name="get_exchange_symbols",
        natural_description=(
            "Get all symbols listed on a specific exchange including stocks, ETFs, "
            "and other traded instruments."
        ),
        example_queries=[
            "List all symbols on NYSE",
            "Show me NASDAQ listed companies",
            "What securities trade on LSE?",
            "Get all stocks listed on TSX",
            "Show symbols available on ASX",
        ],
        related_terms=[
            "exchange listings",
            "listed securities",
            "traded symbols",
            "exchange symbols",
            "market listings",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Lists",
        parameter_hints={
            "exchange": EXCHANGE_HINT,
        },
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Trading symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "stock symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Company name",
                examples=["Apple Inc", "Microsoft Corporation"],
                related_terms=["company name", "listing name"],
            ),
        },
        use_cases=[
            "Exchange analysis",
            "Market coverage",
            "Trading universe definition",
            "Market research",
        ],
    ),
    # Search variant semantics
    "search_by_cik": EndpointSemantics(
        client_name="company",
        method_name="search_by_cik",  # Match exact method name
        natural_description=(
            "Search for companies by their SEC " "Central Index Key (CIK) number"
        ),
        example_queries=[
            "Find company with CIK number 320193",
            "Search for company by CIK",
            "Look up SEC CIK information",
            "Get company details by CIK",
            "Find ticker symbol for CIK",
        ],
        related_terms=[
            "CIK search",
            "SEC identifier",
            "Central Index Key",
            "regulatory ID",
            "SEC lookup",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Search",
        parameter_hints={"query": IDENTIFIER_HINT},
        response_hints={
            "cik": ResponseFieldInfo(
                description="SEC Central Index Key",
                examples=["0000320193"],
                related_terms=["CIK", "SEC ID"],
            )
        },
        use_cases=[
            "Regulatory research",
            "SEC filing lookup",
            "Company identification",
            "Regulatory compliance",
        ],
    ),
    "search_by_cusip": EndpointSemantics(
        client_name="company",
        method_name="search_by_cusip",
        natural_description="Search for companies by their CUSIP identifier",
        example_queries=[
            "Find company by CUSIP number",
            "Search securities using CUSIP",
            "Look up stock with CUSIP",
            "Get company information by CUSIP",
        ],
        related_terms=[
            "CUSIP search",
            "security identifier",
            "CUSIP lookup",
            "security ID",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Search",
        parameter_hints={"query": IDENTIFIER_HINT},
        response_hints={
            "cusip": ResponseFieldInfo(
                description="CUSIP identifier",
                examples=["037833100"],
                related_terms=["CUSIP", "security ID"],
            )
        },
        use_cases=[
            "Security identification",
            "Trade processing",
            "Portfolio management",
            "Security lookup",
        ],
    ),
    "search_by_isin": EndpointSemantics(
        client_name="company",
        method_name="search_by_isin",
        natural_description=(
            "Search for companies by their International "
            "Securities Identification Number (ISIN)"
        ),
        example_queries=[
            "Find company by ISIN",
            "Search using ISIN number",
            "Look up stock with ISIN",
            "Get security details by ISIN",
        ],
        related_terms=[
            "ISIN search",
            "international identifier",
            "ISIN lookup",
            "global ID",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Search",
        parameter_hints={"query": IDENTIFIER_HINT},
        response_hints={
            "isin": ResponseFieldInfo(
                description="International Securities Identification Number",
                examples=["US0378331005"],
                related_terms=["ISIN", "international ID"],
            )
        },
        use_cases=[
            "Global security identification",
            "International trading",
            "Cross-border transactions",
            "Global portfolio management",
        ],
    ),
    "company_logo_url": EndpointSemantics(
        client_name="company",
        method_name="get_company_logo_url",
        natural_description=(
            "Get the URL of the company's official logo image for use in "
            "applications, websites, or documentation"
        ),
        example_queries=[
            "Get Apple's company logo",
            "Find Microsoft's logo URL",
            "Show me Tesla's logo",
            "Get logo image for Amazon",
            "Find company logo for Google",
        ],
        related_terms=[
            "company logo",
            "brand image",
            "corporate logo",
            "logo URL",
            "company icon",
            "brand symbol",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Media",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "url": ResponseFieldInfo(
                description="URL to company logo image",
                examples=[
                    "https://example.com/logos/AAPL.png",
                    "https://example.com/logos/MSFT.png",
                ],
                related_terms=["logo link", "image URL", "logo source", "image link"],
            ),
        },
        use_cases=[
            "Brand asset retrieval",
            "Website development",
            "Application UI development",
            "Marketing materials",
            "Company presentations",
        ],
    ),
    "executive_compensation": EndpointSemantics(
        client_name="company",
        method_name="get_executive_compensation",
        natural_description=(
            "Get detailed executive compensation information including salary, "
            "bonuses, stock awards, and total compensation packages for company leaders"
        ),
        example_queries=[
            "How much does Apple's CEO make?",
            "Get Microsoft executive compensation",
            "Show me Tesla executive salaries",
            "What's the compensation for Amazon's executives?",
            "Get Google executive pay information",
        ],
        related_terms=[
            "executive pay",
            "compensation package",
            "salary",
            "executive benefits",
            "remuneration",
            "executive rewards",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Executive",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "salary": ResponseFieldInfo(
                description="Base salary amount",
                examples=["1500000", "1000000"],
                related_terms=["base pay", "annual salary", "base compensation"],
            ),
            "bonus": ResponseFieldInfo(
                description="Annual bonus payment",
                examples=["3000000", "2500000"],
                related_terms=["annual bonus", "cash bonus", "performance bonus"],
            ),
            "stock_awards": ResponseFieldInfo(
                description="Value of stock awards",
                examples=["12000000", "15000000"],
                related_terms=["equity awards", "stock grants", "RSUs"],
            ),
            "total_compensation": ResponseFieldInfo(
                description="Total annual compensation",
                examples=["25000000", "30000000"],
                related_terms=["total pay", "total package", "annual compensation"],
            ),
        },
        use_cases=[
            "Executive compensation analysis",
            "Corporate governance research",
            "Compensation benchmarking",
            "SEC compliance reporting",
            "Management expense analysis",
        ],
    ),
    "all_shares_float": EndpointSemantics(
        client_name="company",
        method_name="get_all_shares_float",
        natural_description=(
            "Get comprehensive share float data for all companies, showing the "
            "number and percentage of shares available for public trading"
        ),
        example_queries=[
            "Get all companies' share float data",
            "Show float information for all stocks",
            "List share float for all companies",
            "Get complete float data",
            "Show all public float information",
        ],
        related_terms=[
            "market float",
            "public float",
            "tradable shares",
            "floating stock",
            "share availability",
            "trading float",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Float",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Company stock symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "trading symbol", "stock symbol"],
            ),
            "float_shares": ResponseFieldInfo(
                description="Number of shares in public float",
                examples=["5.2B", "750M"],
                related_terms=["floating shares", "tradable shares", "public shares"],
            ),
            "percentage_float": ResponseFieldInfo(
                description="Percentage of shares in public float",
                examples=["85.5%", "45.2%"],
                related_terms=["float percentage", "public float ratio", "float ratio"],
            ),
        },
        use_cases=[
            "Market liquidity analysis",
            "Float comparison across companies",
            "Trading volume analysis",
            "Institutional ownership research",
            "Market availability assessment",
        ],
    ),
}
