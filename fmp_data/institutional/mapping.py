from fmp_data.institutional.endpoints import (
    ASSET_ALLOCATION,
    BENEFICIAL_OWNERSHIP,
    CIK_MAPPER,
    CIK_MAPPER_BY_NAME,
    CIK_MAPPER_BY_SYMBOL,
    FAIL_TO_DELIVER,
    FORM_13F,
    FORM_13F_DATES,
    INSIDER_ROSTER,
    INSIDER_STATISTICS,
    INSIDER_TRADES,
    INSTITUTIONAL_HOLDERS,
    INSTITUTIONAL_HOLDINGS,
    TRANSACTION_TYPES,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

# Common parameter hints for reuse
SYMBOL_HINT = ParameterHint(
    natural_names=["ticker", "stock symbol", "company symbol"],
    extraction_patterns=[
        r"[A-Z]{1,5}",
        r"symbol[:\s]+([A-Z]{1,5})",
        r"(?i)for\s+([A-Z]{1,5})",
    ],
    examples=["AAPL", "MSFT", "TSLA"],
    context_clues=["stock", "ticker", "symbol", "shares", "company"],
)

CIK_HINT = ParameterHint(
    natural_names=["CIK", "SEC ID", "filing ID"],
    extraction_patterns=[
        r"CIK[:\s]+(\d+)",
        r"(\d{10})",
    ],
    examples=["0000320193", "0000789019", "0001652044"],
    context_clues=["CIK", "SEC identifier", "filing ID", "regulatory ID"],
)

DATE_HINT = ParameterHint(
    natural_names=["date", "filing date", "report date"],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
    ],
    examples=["2024-03-31", "2023-12-31", "2024-06-30"],
    context_clues=["date", "as of", "filed on", "reported", "for period"],
)

PAGE_HINT = ParameterHint(
    natural_names=["page number", "page", "result page"],
    extraction_patterns=[
        r"page[:\s]+(\d+)",
        r"p(\d+)",
    ],
    examples=["0", "1", "2"],
    context_clues=["page", "next", "previous", "results"],
)

NAME_HINT = ParameterHint(
    natural_names=["company name", "entity name", "institution name"],
    extraction_patterns=[
        r"name[:\s]+(.+)",
        r"company[:\s]+(.+)",
    ],
    examples=["Apple Inc", "Microsoft Corporation", "BlackRock"],
    context_clues=["name", "company", "corporation", "entity"],
)

INSTITUTIONAL_TIME_PERIODS = {
    "quarterly": {
        "patterns": [
            r"(?i)quarterly",
            r"(?i)quarter",
            r"(?i)Q[1-4]",
            r"(?i)13F",
        ],
        "terms": ["quarterly", "13F filing", "quarter", "three months"],
    },
    "annual": {
        "patterns": [
            r"(?i)annual",
            r"(?i)yearly",
            r"(?i)year",
        ],
        "terms": ["annual", "yearly", "fiscal year", "calendar year"],
    },
}

# Filing type categories
INSTITUTIONAL_FILING_TYPES = {
    "ownership": [
        "13F",
        "13D",
        "13G",
        "Form 3",
        "Form 4",
        "Form 5",
    ],
    "insider": [
        "Form 3",
        "Form 4",
        "Form 5",
        "Initial filing",
        "Changes in ownership",
    ],
    "institutional": [
        "13F",
        "13F-HR",
        "13F-NT",
        "Quarterly report",
        "Holdings report",
    ],
}
INSTITUTIONAL_ENDPOINT_MAP = {
    "get_form_13f": FORM_13F,
    "get_form_13f_dates": FORM_13F_DATES,
    "get_asset_allocation": ASSET_ALLOCATION,
    "get_institutional_holders": INSTITUTIONAL_HOLDERS,
    "get_institutional_holdings": INSTITUTIONAL_HOLDINGS,
    "get_insider_trades": INSIDER_TRADES,
    "get_transaction_types": TRANSACTION_TYPES,
    "get_insider_roster": INSIDER_ROSTER,
    "get_insider_statistics": INSIDER_STATISTICS,
    "get_cik_mapper": CIK_MAPPER,
    "get_cik_mapper_by_name": CIK_MAPPER_BY_NAME,
    "get_cik_mapper_by_symbol": CIK_MAPPER_BY_SYMBOL,
    "get_beneficial_ownership": BENEFICIAL_OWNERSHIP,
    "get_fail_to_deliver": FAIL_TO_DELIVER,
}

INSTITUTIONAL_ENDPOINTS_SEMANTICS = {
    "form_13f": EndpointSemantics(
        client_name="institutional",
        method_name="get_form_13f",
        natural_description=(
            "Retrieve Form 13F filings data "
            "for institutional investment managers, "
            "including detailed holdings information, "
            "share quantities, and market values."
        ),
        example_queries=[
            "Get 13F filing data for BlackRock",
            "Show me Vanguard's latest 13F holdings",
            "What stocks does Renaissance hold?",
            "Get institutional holdings for CIK 1234567",
            "Show me Warren Buffett's portfolio",
        ],
        related_terms=[
            "13F filings",
            "institutional holdings",
            "portfolio holdings",
            "investment managers",
            "fund holdings",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="13F Filings",
        parameter_hints={
            "cik": CIK_HINT,
            "date": DATE_HINT,
        },
        response_hints={
            "cusip": ResponseFieldInfo(
                description="CUSIP identifier for the security",
                examples=["037833100", "594918104"],
                related_terms=["security identifier", "CUSIP number"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["1000000", "500000"],
                related_terms=["position size", "quantity", "holding size"],
            ),
            "value": ResponseFieldInfo(
                description="Market value of holding in dollars",
                examples=["1000000", "500000"],
                related_terms=["position value", "market value", "dollar value"],
            ),
        },
        use_cases=[
            "Portfolio analysis",
            "Investment research",
            "Competitive analysis",
            "Market sentiment analysis",
        ],
    ),
    "form_13f_dates": EndpointSemantics(
        client_name="institutional",
        method_name="get_form_13f_dates",
        natural_description=(
            "Get a list of available Form 13F "
            "filing dates for a specific institutional "
            "investment manager, helping track "
            "their reporting history and timeline."
        ),
        example_queries=[
            "When did BlackRock file their 13Fs?",
            "Show me filing dates for CIK 1234567",
            "Get reporting timeline for Vanguard",
            "List all 13F dates for Renaissance",
        ],
        related_terms=[
            "filing dates",
            "reporting timeline",
            "submission dates",
            "13F schedule",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="13F Filings",
        parameter_hints={"cik": CIK_HINT},
        response_hints={
            "form_date": ResponseFieldInfo(
                description="Date of the Form 13F filing",
                examples=["2024-03-31", "2023-12-31"],
                related_terms=["filing date", "report date", "submission date"],
            ),
        },
        use_cases=[
            "Filing timeline analysis",
            "Reporting compliance tracking",
            "Historical filing research",
        ],
    ),
    "asset_allocation": EndpointSemantics(
        client_name="institutional",
        method_name="get_asset_allocation",
        natural_description=("Analyze asset allocation data from 13F filings"),
        example_queries=[
            "Show asset allocation for major institutions",
            "Get portfolio distribution by asset type",
            "How are institutions allocating their assets?",
        ],
        related_terms=[
            "portfolio allocation",
            "asset distribution",
            "investment mix",
            "sector weights",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Portfolio Analysis",
        parameter_hints={"date": DATE_HINT},
        response_hints={
            "asset_type": ResponseFieldInfo(
                description="Type of asset or investment category",
                examples=["Equities", "Fixed Income", "Cash"],
                related_terms=["investment type", "security type", "asset class"],
            ),
            "percentage": ResponseFieldInfo(
                description="Allocation percentage for the asset type",
                examples=["45.2", "23.8", "12.5"],
                related_terms=["weight", "allocation", "exposure"],
            ),
        },
        use_cases=[
            "Portfolio strategy analysis",
            "Asset allocation trends",
            "Risk distribution analysis",
        ],
    ),
    "institutional_holdings": EndpointSemantics(
        client_name="institutional",
        method_name="get_institutional_holdings",
        natural_description=(
            "Analyze institutional ownership for a specific security."
        ),
        example_queries=[
            "Show institutional ownership for AAPL",
            "Who owns Tesla stock?",
            "Get institutional holdings for MSFT",
            "How many institutions hold Amazon?",
        ],
        related_terms=[
            "institutional ownership",
            "fund holdings",
            "institutional stakes",
            "ownership structure",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Ownership Analysis",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "includeCurrentQuarter": ParameterHint(
                natural_names=[
                    "include current quarter",
                    "show latest quarter",
                    "include current period",
                ],
                extraction_patterns=[
                    r"(?i)include.*current.*quarter",
                    r"(?i)show.*latest.*quarter",
                    r"(?i)include.*current.*period",
                ],
                examples=["true", "false"],
                context_clues=[
                    "current quarter",
                    "latest period",
                    "most recent quarter",
                    "preliminary data",
                ],
            ),
        },
        response_hints={
            "investors_holding": ResponseFieldInfo(
                description="Number of institutional investors holding the stock",
                examples=["1250", "876", "2341"],
                related_terms=["holder count", "institutional count"],
            ),
            "ownership_percent": ResponseFieldInfo(
                description="Percentage of shares owned by institutions",
                examples=["72.5", "45.8", "88.3"],
                related_terms=["institutional ownership", "ownership percentage"],
            ),
        },
        use_cases=[
            "Ownership structure analysis",
            "Institutional interest tracking",
            "Investment thesis research",
        ],
    ),
    "insider_trades": EndpointSemantics(
        client_name="institutional",
        method_name="get_insider_trades",
        natural_description=("Track insider trading activity for a specific security."),
        example_queries=[
            "Show insider trades for AAPL",
            "Get recent insider activity for Tesla",
            "Who's buying or selling Microsoft stock?",
            "Show executive trades for NVDA",
        ],
        related_terms=[
            "insider activity",
            "executive trades",
            "insider buying",
            "insider selling",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Insider Activity",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "page": PAGE_HINT,
        },
        response_hints={
            "transaction_type": ResponseFieldInfo(
                description="Type of insider transaction",
                examples=["P", "S", "A", "D"],
                related_terms=["trade type", "transaction code"],
            ),
            "securities_transacted": ResponseFieldInfo(
                description="Number of shares involved in the transaction",
                examples=["10000", "5000", "25000"],
                related_terms=["shares traded", "quantity"],
            ),
        },
        use_cases=[
            "Insider sentiment analysis",
            "Corporate governance research",
            "Investment signal generation",
        ],
    ),
    "transaction_types": EndpointSemantics(
        client_name="institutional",
        method_name="get_transaction_types",
        natural_description=(
            "Get a reference list of insider transaction types and their descriptions."
        ),
        example_queries=[
            "List all insider transaction types",
            "What do insider trade codes mean?",
            "Show transaction type definitions",
            "Explain insider trading codes",
        ],
        related_terms=[
            "transaction codes",
            "trade types",
            "Form 4 codes",
            "insider codes",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Insider Activity",
        parameter_hints={},  # No parameters needed
        response_hints={
            "code": ResponseFieldInfo(
                description="Transaction type code",
                examples=["P", "S", "A", "D"],
                related_terms=["type code", "transaction code"],
            ),
            "description": ResponseFieldInfo(
                description="Description of the transaction type",
                examples=["Open market purchase", "Open market sale"],
                related_terms=["code meaning", "type description"],
            ),
        },
        use_cases=[
            "Transaction analysis",
            "Regulatory compliance",
            "Data interpretation",
        ],
    ),
    "insider_roster": EndpointSemantics(
        client_name="institutional",
        method_name="get_insider_roster",
        natural_description=(
            "Get a list of company insiders including executives, directors, and major "
            "shareholders, along with their positions and latest transaction dates."
        ),
        example_queries=[
            "Show insiders for AAPL",
            "Who are Tesla's executives?",
            "Get Microsoft insider list",
            "List company officers for NVDA",
        ],
        related_terms=[
            "company insiders",
            "executives",
            "officers",
            "directors",
            "key personnel",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Insider Information",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "owner": ResponseFieldInfo(
                description="Name of the insider",
                examples=["John Smith", "Jane Doe"],
                related_terms=["insider name", "officer name"],
            ),
            "type_of_owner": ResponseFieldInfo(
                description="Position or role of the insider",
                examples=["CEO", "CFO", "Director"],
                related_terms=["position", "role", "title"],
            ),
        },
        use_cases=[
            "Corporate governance analysis",
            "Management research",
            "Insider tracking",
        ],
    ),
    "insider_statistics": EndpointSemantics(
        client_name="institutional",
        method_name="get_insider_statistics",
        natural_description=(
            "Get aggregated statistics about insider trading activity."
        ),
        example_queries=[
            "Get insider trading stats for AAPL",
            "Show insider metrics for Tesla",
            "What's the buy/sell ratio for MSFT?",
            "Get insider trading summary for NVDA",
        ],
        related_terms=[
            "insider metrics",
            "trading statistics",
            "insider analysis",
            "trading patterns",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Insider Activity",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "buy_sell_ratio": ResponseFieldInfo(
                description="Ratio of buy to sell transactions",
                examples=["1.5", "0.8", "2.3"],
                related_terms=["trading ratio", "buy/sell ratio"],
            ),
            "total_bought": ResponseFieldInfo(
                description="Total shares purchased by insiders",
                examples=["100000", "50000", "250000"],
                related_terms=["buy volume", "purchase quantity"],
            ),
            "total_sold": ResponseFieldInfo(
                description="Total shares sold by insiders",
                examples=["75000", "40000", "200000"],
                related_terms=["sell volume", "sale quantity"],
            ),
        },
        use_cases=[
            "Insider sentiment analysis",
            "Trading pattern analysis",
            "Signal generation",
            "Risk assessment",
        ],
    ),
    "cik_mapper": EndpointSemantics(
        client_name="institutional",
        method_name="get_cik_mapper",
        natural_description=(
            "Get a comprehensive mapping between "
            "CIK numbers and company/institution names."
        ),
        example_queries=[
            "Get CIK mappings",
            "Show CIK to name mapping",
            "List company CIK numbers",
            "Get SEC filer identifiers",
        ],
        related_terms=[
            "CIK numbers",
            "SEC identifiers",
            "company IDs",
            "filing codes",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Reference Data",
        parameter_hints={"page": PAGE_HINT},
        response_hints={
            "reporting_cik": ResponseFieldInfo(
                description="CIK number of the entity",
                examples=["0001166559", "0000102909"],
                related_terms=["CIK", "SEC ID", "identifier"],
            ),
            "reporting_name": ResponseFieldInfo(
                description="Name of the entity",
                examples=["APPLE INC", "MICROSOFT CORP"],
                related_terms=["company name", "entity name", "legal name"],
            ),
        },
        use_cases=[
            "Entity identification",
            "Filing research",
            "Data integration",
            "Compliance verification",
        ],
    ),
    "cik_mapper_by_name": EndpointSemantics(
        client_name="institutional",
        method_name="get_cik_mapper_by_name",
        natural_description=("Search for CIK numbers by company or institution name."),
        example_queries=[
            "Find CIK for Apple",
            "Search CIK by company name",
            "What's Microsoft's CIK?",
            "Look up Tesla's CIK number",
        ],
        related_terms=[
            "company search",
            "entity lookup",
            "name search",
            "CIK lookup",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Reference Data",
        parameter_hints={
            "name": NAME_HINT,
            "page": PAGE_HINT,
        },
        response_hints={
            "reporting_cik": ResponseFieldInfo(
                description="CIK number of the entity",
                examples=["0001166559", "0000102909"],
                related_terms=["CIK", "SEC ID", "identifier"],
            ),
            "reporting_name": ResponseFieldInfo(
                description="Name of the entity",
                examples=["APPLE INC", "MICROSOFT CORP"],
                related_terms=["company name", "entity name", "legal name"],
            ),
        },
        use_cases=[
            "Entity identification",
            "Filing research",
            "Company lookup",
            "Data verification",
        ],
    ),
    "cik_mapper_by_symbol": EndpointSemantics(
        client_name="institutional",
        method_name="get_cik_mapper_by_symbol",
        natural_description=("Look up CIK numbers using stock symbols."),
        example_queries=[
            "Get CIK for AAPL",
            "Find Tesla's CIK by symbol",
            "Look up MSFT CIK number",
            "What's NVDA's SEC ID?",
        ],
        related_terms=[
            "ticker lookup",
            "symbol search",
            "company identifier",
            "stock lookup",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Reference Data",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock symbol",
                examples=["AAPL", "MSFT", "TSLA"],
                related_terms=["ticker", "trading symbol"],
            ),
            "cik": ResponseFieldInfo(
                description="CIK number",
                examples=["0001166559", "0000102909"],
                related_terms=["SEC ID", "identifier"],
            ),
        },
        use_cases=[
            "Quick company lookup",
            "Filing research",
            "Data integration",
            "Entity verification",
        ],
    ),
    "beneficial_ownership": EndpointSemantics(
        client_name="institutional",
        method_name="get_beneficial_ownership",
        natural_description=(
            "Retrieve beneficial ownership information including voting rights and "
            "dispositive power for major shareholders of a company."
        ),
        example_queries=[
            "Show beneficial owners for AAPL",
            "Get major shareholders for Tesla",
            "Who are the beneficial owners of MSFT?",
            "Show significant holders for NVDA",
        ],
        related_terms=[
            "major shareholders",
            "significant owners",
            "beneficial holders",
            "voting rights",
            "ownership stakes",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Ownership Analysis",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "amount_beneficially_owned": ResponseFieldInfo(
                description="Number of shares beneficially owned",
                examples=["1000000", "500000", "2500000"],
                related_terms=["shares owned", "beneficial holdings"],
            ),
            "percent_of_class": ResponseFieldInfo(
                description="Percentage of share class owned",
                examples=["5.2", "7.8", "12.5"],
                related_terms=["ownership percentage", "stake percentage"],
            ),
            "voting_power": ResponseFieldInfo(
                description="Voting power percentage",
                examples=["4.8", "6.5", "10.2"],
                related_terms=["voting rights", "voting control"],
            ),
        },
        use_cases=[
            "Ownership analysis",
            "Control analysis",
            "Corporate governance",
            "Risk assessment",
        ],
    ),
    "fail_to_deliver": EndpointSemantics(
        client_name="institutional",
        method_name="get_fail_to_deliver",
        natural_description=(
            "Get data on failed trade settlements (FTDs) for a security."
        ),
        example_queries=[
            "Show FTDs for AAPL",
            "Get fail to deliver data for Tesla",
            "What are the FTDs for MSFT?",
            "Show settlement failures for NVDA",
        ],
        related_terms=[
            "FTD",
            "settlement failures",
            "failed deliveries",
            "trade settlement",
            "delivery failures",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Settlement Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "page": PAGE_HINT,
        },
        response_hints={
            "quantity": ResponseFieldInfo(
                description="Number of shares that failed to deliver",
                examples=["50000", "25000", "100000"],
                related_terms=[
                    "failed shares",
                    "FTD quantity",
                    "settlement failure size",
                ],
            ),
            "price": ResponseFieldInfo(
                description="Price per share for the failed delivery",
                examples=["156.78", "245.90", "89.32"],
                related_terms=["share price", "settlement price", "FTD price"],
            ),
        },
        use_cases=[
            "Settlement risk analysis",
            "Market efficiency monitoring",
            "Short interest analysis",
            "Trading strategy development",
            "Risk management",
        ],
    ),
    "institutional_holders": EndpointSemantics(
        client_name="institutional",
        method_name="get_institutional_holders",
        natural_description=(
            "Get detailed information about institutional holders of securities."
        ),
        example_queries=[
            "Who are the institutional holders of AAPL?",
            "Show me institutional ownership for MSFT",
            "Get major holders for GOOGL",
            "List institutional investors in TSLA",
        ],
        related_terms=[
            "institutional investors",
            "major holders",
            "institutional ownership",
            "fund holdings",
            "stakeholders",
        ],
        category=SemanticCategory.INSTITUTIONAL,
        sub_category="Ownership",
        parameter_hints={},
        response_hints={
            "holder": ResponseFieldInfo(
                description="Name of institutional holder",
                examples=["BlackRock", "Vanguard", "State Street"],
                related_terms=["institution", "investor", "owner"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["1000000", "500000"],
                related_terms=["position size", "holding"],
            ),
        },
        use_cases=[
            "Ownership analysis",
            "Institutional interest tracking",
            "Stakeholder analysis",
        ],
    ),
}
