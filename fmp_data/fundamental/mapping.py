# fmp_data/fundamental/mapping.py

from fmp_data.fundamental.endpoints import (
    BALANCE_SHEET,
    CASH_FLOW,
    FINANCIAL_RATIOS,
    FINANCIAL_REPORTS_DATES,
    FULL_FINANCIAL_STATEMENT,
    HISTORICAL_RATING,
    INCOME_STATEMENT,
    KEY_METRICS,
    LEVERED_DCF,
    OWNER_EARNINGS,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

# Endpoint mappings
FUNDAMENTAL_ENDPOINT_MAP = {
    "get_income_statement": INCOME_STATEMENT,
    "get_balance_sheet": BALANCE_SHEET,
    "get_cash_flow": CASH_FLOW,
    "get_key_metrics": KEY_METRICS,
    "get_financial_ratios": FINANCIAL_RATIOS,
    "get_owner_earnings": OWNER_EARNINGS,
    "get_levered_dcf": LEVERED_DCF,
    "get_historical_rating": HISTORICAL_RATING,
    "get_full_financial_statement": FULL_FINANCIAL_STATEMENT,
    "get_financial_reports_dates": FINANCIAL_REPORTS_DATES,
}
# Common parameter hints
SYMBOL_HINT = ParameterHint(
    natural_names=["company", "ticker", "stock", "symbol"],
    extraction_patterns=[
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"\b[A-Z]{1,5}\b",
    ],
    examples=["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
    context_clues=[
        "company",
        "stock",
        "ticker",
        "shares",
        "corporation",
        "business",
        "enterprise",
        "firm",
    ],
)

PERIOD_HINT = ParameterHint(
    natural_names=["period", "frequency", "interval"],
    extraction_patterns=[
        r"(?i)(annual|yearly|quarterly|quarter)",
        r"(?i)every\s+(year|quarter)",
    ],
    examples=["annual", "quarter"],
    context_clues=[
        "annual",
        "yearly",
        "quarterly",
        "fiscal",
        "period",
        "reporting",
        "financial",
    ],
)

LIMIT_HINT = ParameterHint(
    natural_names=["limit", "count", "number"],
    extraction_patterns=[
        r"(?i)last\s+(\d+)",
        r"(?i)(\d+)\s+periods",
        r"(?i)recent\s+(\d+)",
    ],
    examples=["10", "20", "40"],
    context_clues=[
        "last",
        "recent",
        "previous",
        "historical",
        "periods",
        "statements",
        "reports",
    ],
)
FUNDAMENTAL_CONCEPTS = {
    "profitability": [
        "margins",
        "returns",
        "earnings",
        "profits",
        "income",
    ],
    "liquidity": [
        "cash",
        "working capital",
        "current ratio",
        "quick ratio",
    ],
    "solvency": [
        "debt",
        "leverage",
        "coverage",
        "capital structure",
    ],
    "efficiency": [
        "turnover",
        "utilization",
        "productivity",
        "asset management",
        "inventory management",
    ],
    "growth": [
        "expansion",
        "increase",
        "development",
        "scaling",
        "momentum",
    ],
    "reporting": [
        "filings",
        "reports",
        "statements",
        "disclosures",
        "documentation",
    ],
    "timing": [
        "schedule",
        "calendar",
        "dates",
        "timeline",
        "availability",
    ],
}
FUNDAMENTAL_ENDPOINTS_SEMANTICS = {
    "income_statement": EndpointSemantics(
        client_name="fundamental",
        method_name="get_income_statement",
        natural_description=(
            "Retrieve detailed income statements showing revenue, costs, expenses and "
            "profitability metrics for a company over multiple periods."
        ),
        example_queries=[
            "Get AAPL income statement",
            "Show quarterly income statements for MSFT",
            "What is Tesla's revenue?",
            "Show me Google's profit margins",
            "Get Amazon's operating expenses",
            "Last 5 years income statements for Netflix",
        ],
        related_terms=[
            "profit and loss",
            "P&L statement",
            "earnings report",
            "revenue",
            "expenses",
            "net income",
            "operating income",
            "gross profit",
            "margins",
            "earnings",
            "costs",
            "profitability",
            "financial performance",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Statements",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "revenue": ResponseFieldInfo(
                description="Total revenue/sales for the period",
                examples=["365.7B", "42.1B"],
                related_terms=["sales", "income", "turnover"],
            ),
            "gross_profit": ResponseFieldInfo(
                description="Revenue minus cost of goods sold",
                examples=["124.8B", "15.3B"],
                related_terms=["gross margin", "gross income"],
            ),
            "operating_income": ResponseFieldInfo(
                description="Profit from operations before interest and taxes",
                examples=["85.2B", "10.4B"],
                related_terms=["EBIT", "operating profit"],
            ),
            "net_income": ResponseFieldInfo(
                description="Bottom line profit after all expenses",
                examples=["59.6B", "7.8B"],
                related_terms=["net profit", "earnings", "bottom line"],
            ),
            "eps": ResponseFieldInfo(
                description="Earnings per share",
                examples=["4.82", "2.15"],
                related_terms=["earnings per share", "EPS"],
            ),
        },
        use_cases=[
            "Financial performance analysis",
            "Profitability assessment",
            "Trend analysis",
            "Competitive comparison",
            "Investment research",
            "Earnings analysis",
            "Cost structure evaluation",
        ],
    ),
    "balance_sheet": EndpointSemantics(
        client_name="fundamental",
        method_name="get_balance_sheet",
        natural_description=(
            "Access detailed balance sheet statements showing a company's assets, "
            "liabilities, and shareholders' equity."
        ),
        example_queries=[
            "Get AAPL balance sheet",
            "Show Microsoft's assets and liabilities",
            "What's Tesla's cash position?",
            "Get Google's debt levels",
            "Show Amazon's equity structure",
            "Latest balance sheet for Netflix",
        ],
        related_terms=[
            "assets",
            "liabilities",
            "equity",
            "financial position",
            "book value",
            "net worth",
            "financial condition",
            "liquidity",
            "solvency",
            "capital structure",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Statements",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "total_assets": ResponseFieldInfo(
                description="Total assets of the company",
                examples=["365.7B", "42.1B"],
                related_terms=["assets", "resources", "property"],
            ),
            "total_liabilities": ResponseFieldInfo(
                description="Total liabilities/obligations",
                examples=["180.3B", "25.7B"],
                related_terms=["debts", "obligations", "commitments"],
            ),
            "total_equity": ResponseFieldInfo(
                description="Total shareholders' equity",
                examples=["185.4B", "16.4B"],
                related_terms=["net worth", "book value", "stockholders' equity"],
            ),
            "cash_and_equivalents": ResponseFieldInfo(
                description="Cash and cash equivalents",
                examples=["48.3B", "12.5B"],
                related_terms=["cash", "liquid assets", "cash position"],
            ),
        },
        use_cases=[
            "Financial position analysis",
            "Liquidity assessment",
            "Solvency analysis",
            "Capital structure analysis",
            "Investment due diligence",
            "Credit analysis",
            "Asset quality evaluation",
        ],
    ),
    "cash_flow": EndpointSemantics(
        client_name="fundamental",
        method_name="get_cash_flow",
        natural_description=(
            "Retrieve detailed cash flow statements showing operating, investing, and "
            "financing activities."
        ),
        example_queries=[
            "Get AAPL cash flow statement",
            "Show Microsoft's operating cash flow",
            "What's Tesla's free cash flow?",
            "Get Google's capital expenditures",
            "Show Amazon's financing cash flows",
            "Netflix operating cash flow history",
        ],
        related_terms=[
            "cash flow statement",
            "operating activities",
            "investing activities",
            "financing activities",
            "cash generation",
            "cash usage",
            "capital expenditure",
            "free cash flow",
            "cash operations",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Statements",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "operating_cash_flow": ResponseFieldInfo(
                description="Net cash from operating activities",
                examples=["95.2B", "12.4B"],
                related_terms=["operating cash", "cash from operations"],
            ),
            "investing_cash_flow": ResponseFieldInfo(
                description="Net cash from investing activities",
                examples=["-12.8B", "-5.4B"],
                related_terms=["investing cash", "investment cash flow"],
            ),
            "financing_cash_flow": ResponseFieldInfo(
                description="Net cash from financing activities",
                examples=["-85.5B", "10.2B"],
                related_terms=["financing cash", "financial cash flow"],
            ),
            "free_cash_flow": ResponseFieldInfo(
                description="Operating cash flow minus capital expenditures",
                examples=["75.8B", "8.9B"],
                related_terms=["FCF", "available cash flow", "discretionary cash"],
            ),
        },
        use_cases=[
            "Cash flow analysis",
            "Liquidity assessment",
            "Capital allocation review",
            "Investment capacity evaluation",
            "Cash management analysis",
            "Financial planning",
            "Dividend sustainability analysis",
        ],
    ),
    "financial_ratios": EndpointSemantics(
        client_name="fundamental",
        method_name="get_financial_ratios",
        natural_description=(
            "Access comprehensive financial ratios for analyzing company performance, "
            "efficiency, and financial health."
        ),
        example_queries=[
            "Get AAPL financial ratios",
            "Show Microsoft's liquidity ratios",
            "What's Tesla's debt ratio?",
            "Get Google's profitability metrics",
            "Show Amazon's efficiency ratios",
            "Calculate Netflix financial ratios",
        ],
        related_terms=[
            "financial metrics",
            "performance ratios",
            "efficiency ratios",
            "liquidity ratios",
            "solvency ratios",
            "profitability metrics",
            "operating metrics",
            "financial indicators",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Metrics",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "current_ratio": ResponseFieldInfo(
                description="Current assets divided by current liabilities",
                examples=["2.5", "1.8"],
                related_terms=["liquidity ratio", "working capital ratio"],
            ),
            "quick_ratio": ResponseFieldInfo(
                description="Quick assets divided by current liabilities",
                examples=["1.8", "1.2"],
                related_terms=["acid test", "quick assets ratio"],
            ),
            "debt_equity_ratio": ResponseFieldInfo(
                description="Total debt divided by shareholders' equity",
                examples=["1.5", "0.8"],
                related_terms=["leverage ratio", "gearing"],
            ),
            "return_on_equity": ResponseFieldInfo(
                description="Net income divided by shareholders' equity",
                examples=["25.4%", "18.2%"],
                related_terms=["ROE", "equity returns", "profitability"],
            ),
        },
        use_cases=[
            "Financial analysis",
            "Performance comparison",
            "Risk assessment",
            "Investment screening",
            "Credit analysis",
            "Trend analysis",
            "Peer comparison",
        ],
    ),
    "key_metrics": EndpointSemantics(
        client_name="fundamental",
        method_name="get_key_metrics",
        natural_description=(
            "Access essential financial metrics and KPIs including profitability, "
            "efficiency, and valuation measures."
        ),
        example_queries=[
            "Show AAPL key metrics",
            "Get Microsoft's financial KPIs",
            "What are Tesla's key ratios?",
            "Show performance metrics for Amazon",
            "Get Google's fundamental metrics",
            "Key indicators for Netflix",
        ],
        related_terms=[
            "KPIs",
            "metrics",
            "key indicators",
            "performance measures",
            "financial metrics",
            "key figures",
            "benchmarks",
            "performance indicators",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Metrics",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "revenue_per_share": ResponseFieldInfo(
                description="Revenue divided by shares outstanding",
                examples=["85.20", "12.45"],
                related_terms=["sales per share", "revenue/share"],
            ),
            "net_income_per_share": ResponseFieldInfo(
                description="Net income divided by shares outstanding",
                examples=["6.15", "2.30"],
                related_terms=["earnings per share", "profit per share"],
            ),
            "operating_cash_flow_per_share": ResponseFieldInfo(
                description="Operating cash flow divided by shares outstanding",
                examples=["8.75", "3.45"],
                related_terms=["cash flow per share", "CFPS"],
            ),
            "free_cash_flow_per_share": ResponseFieldInfo(
                description="Free cash flow divided by shares outstanding",
                examples=["7.25", "2.95"],
                related_terms=["FCF per share", "FCFPS"],
            ),
        },
        use_cases=[
            "Performance evaluation",
            "Company comparison",
            "Investment screening",
            "Valuation analysis",
            "Trend monitoring",
            "Strategic planning",
            "Operational assessment",
        ],
    ),
    "owner_earnings": EndpointSemantics(
        client_name="fundamental",
        method_name="get_owner_earnings",
        natural_description=(
            "Calculate owner earnings using Warren "
            "Buffett's methodology to evaluate "
            "true business profitability and "
            "cash generation capability."
        ),
        example_queries=[
            "Calculate AAPL owner earnings",
            "Get Microsoft's owner earnings",
            "What's Tesla's true earnings power?",
            "Show Google's owner earnings metrics",
            "Calculate Apple's real earnings power",
            "What's Amazon's true profitability?",
        ],
        related_terms=[
            "owner earnings",
            "buffett earnings",
            "true earnings",
            "cash earnings",
            "real earnings power",
            "economic earnings",
            "cash generation",
            "earning power",
            "sustainable earnings",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Metrics",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "reported_owner_earnings": ResponseFieldInfo(
                description="Reported owner earnings value",
                examples=["8.5B", "12.3B"],
                related_terms=["earnings", "cash earnings", "true earnings"],
            ),
            "owner_earnings_per_share": ResponseFieldInfo(
                description="Owner earnings per share",
                examples=["4.25", "6.15"],
                related_terms=["per share earnings", "earnings power", "eps"],
            ),
        },
        use_cases=[
            "True earnings power analysis",
            "Long-term investment analysis",
            "Business value assessment",
            "Cash generation evaluation",
            "Quality of earnings analysis",
            "Value investing research",
            "Fundamental analysis",
        ],
    ),
    "levered_dcf": EndpointSemantics(
        client_name="fundamental",
        method_name="get_levered_dcf",
        natural_description=(
            "Perform levered discounted cash flow "
            "valuation with detailed assumptions "
            "about growth, cost of capital, and "
            "future cash flows."
        ),
        example_queries=[
            "Calculate AAPL DCF value",
            "Get Microsoft's intrinsic value",
            "What's Tesla worth using DCF?",
            "Show Google's DCF valuation",
            "Get Amazon's fair value estimate",
            "Calculate Facebook's intrinsic value",
        ],
        related_terms=[
            "dcf valuation",
            "intrinsic value",
            "present value",
            "fair value",
            "discounted cash flow",
            "valuation",
            "enterprise value",
            "equity value",
            "company value",
            "levered value",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Valuation",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "levered_dcf": ResponseFieldInfo(
                description="Calculated DCF value per share",
                examples=["180.50", "2450.75"],
                related_terms=["fair value", "intrinsic value", "dcf price"],
            ),
            "growth_rate": ResponseFieldInfo(
                description="Growth rate used in calculation",
                examples=["12.5%", "8.3%"],
                related_terms=["growth assumption", "projected growth"],
            ),
            "cost_of_equity": ResponseFieldInfo(
                description="Cost of equity used in calculation",
                examples=["9.5%", "11.2%"],
                related_terms=["required return", "discount rate", "cost of capital"],
            ),
            "stock_price": ResponseFieldInfo(
                description="Current stock price for comparison",
                examples=["150.25", "2800.50"],
                related_terms=["market price", "current price", "trading price"],
            ),
        },
        use_cases=[
            "Intrinsic value calculation",
            "Investment valuation",
            "Fair value estimation",
            "Value investing analysis",
            "Acquisition analysis",
            "Investment decision making",
            "Price target setting",
        ],
    ),
    "historical_rating": EndpointSemantics(
        client_name="fundamental",
        method_name="get_historical_rating",
        natural_description=(
            "Retrieve historical company ratings and "
            "scoring metrics over time based on "
            "fundamental analysis."
        ),
        example_queries=[
            "Get AAPL historical ratings",
            "Show Microsoft's rating history",
            "What are Tesla's past ratings?",
            "Get Google's historical scores",
            "Show Amazon's rating changes",
            "Rating history for Netflix",
        ],
        related_terms=[
            "company rating",
            "credit rating",
            "investment grade",
            "score history",
            "historical grades",
            "rating changes",
            "company score",
            "financial rating",
            "analyst rating",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Ratings",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "rating": ResponseFieldInfo(
                description="Overall rating grade",
                examples=["A+", "B", "C-"],
                related_terms=["grade", "score", "rating level"],
            ),
            "rating_score": ResponseFieldInfo(
                description="Numerical rating score",
                examples=["85", "72", "63"],
                related_terms=["score", "numerical rating", "rating value"],
            ),
            "rating_recommendation": ResponseFieldInfo(
                description="Investment recommendation",
                examples=["Strong Buy", "Hold", "Sell"],
                related_terms=["recommendation", "investment advice", "rating action"],
            ),
            "rating_details": ResponseFieldInfo(
                description="Detailed rating breakdown",
                examples=["Profitability: A, Growth: B+, Stability: A-"],
                related_terms=[
                    "rating components",
                    "score breakdown",
                    "rating factors",
                ],
            ),
        },
        use_cases=[
            "Rating trend analysis",
            "Investment screening",
            "Risk assessment",
            "Credit analysis",
            "Performance tracking",
            "Investment research",
            "Historical analysis",
        ],
    ),
    "full_financial_statement": EndpointSemantics(
        client_name="fundamental",
        method_name="get_full_financial_statement",
        natural_description=(
            "Access complete financial statements as reported "
            "to regulatory authorities, "
            "including detailed line items, notes, and supplementary information."
        ),
        example_queries=[
            "Get AAPL full financial statements",
            "Show complete Microsoft financials",
            "Get Tesla's detailed statements",
            "Full financial report for Google",
            "Show Amazon's complete financials",
            "Detailed statements for Netflix",
        ],
        related_terms=[
            "complete financials",
            "detailed statements",
            "full report",
            "comprehensive financials",
            "as reported",
            "regulatory filing",
            "financial filing",
            "complete statements",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Statements",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "period": PERIOD_HINT,
            "limit": LIMIT_HINT,
        },
        response_hints={
            "revenue": ResponseFieldInfo(
                description="Total reported revenue",
                examples=["365.7B", "42.1B"],
                related_terms=["total sales", "reported revenue", "gross revenue"],
            ),
            "operating_income": ResponseFieldInfo(
                description="Operating income as reported",
                examples=["108.95B", "15.23B"],
                related_terms=["operating profit", "reported income"],
            ),
            "net_income": ResponseFieldInfo(
                description="Reported net income",
                examples=["94.68B", "12.9B"],
                related_terms=["net profit", "reported earnings", "bottom line"],
            ),
        },
        use_cases=[
            "Detailed financial analysis",
            "Regulatory compliance review",
            "Audit preparation",
            "Investment research",
            "Financial modeling",
            "Due diligence",
        ],
    ),
    "financial_reports_dates": EndpointSemantics(
        client_name="fundamental",
        method_name="get_financial_reports_dates",
        natural_description=(
            "Retrieve available financial report dates and access links for a company, "
            "including quarterly and annual filings."
        ),
        example_queries=[
            "When are AAPL's financial reports available?",
            "Get MSFT financial filing dates",
            "Show report dates for GOOGL",
            "List available financial statements for TSLA",
            "Find Amazon's report timeline",
            "Get financial report schedule for Netflix",
        ],
        related_terms=[
            "filing dates",
            "report schedule",
            "financial calendar",
            "earnings dates",
            "statement availability",
            "financial filings",
            "quarterly reports",
            "annual reports",
        ],
        category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
        sub_category="Financial Reports",
        parameter_hints={
            "symbol": ParameterHint(
                natural_names=["symbol", "ticker", "company", "stock"],
                extraction_patterns=[
                    r"(?i)for\s+([A-Z]{1,5})",
                    r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
                    r"\b[A-Z]{1,5}\b",
                ],
                examples=["AAPL", "MSFT", "GOOGL"],
                context_clues=["company", "stock", "ticker", "corporation", "business"],
            )
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Date of the financial report",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["report date", "filing date", "statement date"],
            ),
            "period": ResponseFieldInfo(
                description="Reporting period covered",
                examples=["Q1 2024", "FY 2023"],
                related_terms=["fiscal period", "quarter", "annual period"],
            ),
            "link_xlsx": ResponseFieldInfo(
                description="Link to Excel format report",
                examples=["https://api.example.com/reports/AAPL_2024Q1.xlsx"],
                related_terms=["excel link", "spreadsheet link", "xlsx download"],
            ),
            "link_json": ResponseFieldInfo(
                description="Link to JSON format report",
                examples=["https://api.example.com/reports/AAPL_2024Q1.json"],
                related_terms=["json link", "data link", "api link"],
            ),
        },
        use_cases=[
            "Report scheduling",
            "Filing date tracking",
            "Research planning",
            "Due diligence timeline",
            "Analysis scheduling",
            "Report access planning",
            "Historical statement retrieval",
        ],
    ),
}

FULL_STATEMENT_SEMANTICS = EndpointSemantics(
    client_name="fundamental",
    method_name="full_financial_statement",
    natural_description=(
        "Access complete financial statements as reported to regulatory authorities, "
        "including detailed line items, notes, and supplementary information."
    ),
    example_queries=[
        "Get AAPL's full financial statements",
        "Show complete Microsoft financial reports",
        "Get Tesla's detailed financial statements",
        "Full financial report for Google",
        "Show Amazon's complete financial data",
        "Access Netflix's detailed financial reports",
    ],
    related_terms=[
        "complete financials",
        "detailed statements",
        "full report",
        "comprehensive financials",
        "as reported",
        "regulatory filing",
        "financial filing",
        "complete statements",
        "detailed financials",
        "SEC filing",
        "financial report",
    ],
    category=SemanticCategory.FUNDAMENTAL_ANALYSIS,
    sub_category="Financial Statements",
    parameter_hints={
        "symbol": SYMBOL_HINT,
        "period": PERIOD_HINT,
        "limit": LIMIT_HINT,
    },
    response_hints={
        "revenue": ResponseFieldInfo(
            description="Total reported revenue",
            examples=["365.7B", "42.1B"],
            related_terms=["total sales", "reported revenue", "gross revenue"],
        ),
        "operating_income": ResponseFieldInfo(
            description="Operating income as reported",
            examples=["108.95B", "15.23B"],
            related_terms=["operating profit", "reported income", "EBIT"],
        ),
        "net_income": ResponseFieldInfo(
            description="Reported net income",
            examples=["94.68B", "12.9B"],
            related_terms=["net profit", "reported earnings", "bottom line"],
        ),
        "total_assets": ResponseFieldInfo(
            description="Total reported assets",
            examples=["352.8B", "128.3B"],
            related_terms=["assets", "total resources", "reported assets"],
        ),
        "total_liabilities": ResponseFieldInfo(
            description="Total reported liabilities",
            examples=["258.5B", "89.7B"],
            related_terms=["liabilities", "obligations", "debts"],
        ),
        "stockholders_equity": ResponseFieldInfo(
            description="Total stockholders' equity",
            examples=["94.3B", "38.6B"],
            related_terms=["equity", "net worth", "shareholder equity"],
        ),
    },
    use_cases=[
        "Detailed financial analysis",
        "Regulatory compliance review",
        "Audit preparation",
        "Investment research",
        "Financial modeling",
        "Due diligence",
        "Comprehensive analysis",
        "SEC filing analysis",
    ],
)
