# fmp_data/investment/mapping.py

from fmp_data.investment.endpoints import (
    ETF_COUNTRY_WEIGHTINGS,
    ETF_EXPOSURE,
    ETF_HOLDER,
    ETF_HOLDING_DATES,
    ETF_HOLDINGS,
    ETF_INFO,
    ETF_SECTOR_WEIGHTINGS,
    MUTUAL_FUND_BY_NAME,
    MUTUAL_FUND_DATES,
    MUTUAL_FUND_HOLDER,
    MUTUAL_FUND_HOLDINGS,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

# Common parameter hints
SYMBOL_HINT = ParameterHint(
    natural_names=["symbol", "ticker", "code"],
    extraction_patterns=[
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"\b[A-Z]{1,5}\b",
    ],
    examples=["SPY", "QQQ", "VTI", "VFIAX"],
    context_clues=["etf", "fund", "symbol", "ticker"],
)

DATE_HINT = ParameterHint(
    natural_names=["date", "as of", "portfolio date"],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(?:on|at|for)\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-01-15", "2023-12-31"],
    context_clues=["date", "as of", "holdings", "portfolio"],
)

CIK_HINT = ParameterHint(
    natural_names=["cik", "company id", "sec id"],
    extraction_patterns=[
        r"(?i)cik[:\s]+(\d{10})",
        r"(?i)cik[:\s]+(\d{1,10})",
    ],
    examples=["0000102909", "0000884560"],
    context_clues=["cik", "sec identifier", "company id"],
)

FUND_NAME_HINT = ParameterHint(
    natural_names=["fund name", "mutual fund name", "fund"],
    extraction_patterns=[
        r'(?i)"([^"]+)"',
        r"(?i)named? +(.+?)(?:\s+fund|\s*$)",
    ],
    examples=["Vanguard 500 Index Fund", "Fidelity Magellan Fund"],
    context_clues=["named", "fund", "called", "mutual fund"],
)

# Additional semantic mappings
INVESTMENT_COMMON_TERMS = {
    "etf": [
        "exchange traded fund",
        "index fund",
        "traded fund",
        "ETF fund",
        "passive fund",
    ],
    "mutual_fund": [
        "mutual fund",
        "active fund",
        "managed fund",
        "open-end fund",
        "unit trust",
    ],
    "holdings": [
        "portfolio",
        "positions",
        "investments",
        "securities",
        "assets",
        "constituents",
    ],
    "weightings": [
        "allocation",
        "exposure",
        "breakdown",
        "distribution",
        "composition",
        "diversification",
    ],
}

# Additional helper mappings
INVESTMENT_CALCULATIONS = {
    "portfolio_weight": {
        "description": "Calculate position weight in portfolio",
        "formula": "(position_value / total_portfolio_value) * 100",
        "parameters": ["position_value", "total_portfolio_value"],
        "return_type": "percentage",
    },
    "position_return": {
        "description": "Calculate return on position",
        "formula": "((current_value - cost_basis) / cost_basis) * 100",
        "parameters": ["current_value", "cost_basis"],
        "return_type": "percentage",
    },
    "sector_concentration": {
        "description": "Calculate sector concentration ratio",
        "formula": "sum((sector_weight / 100) ** 2) * 100",
        "parameters": ["sector_weights"],
        "return_type": "ratio",
    },
}

# Endpoint mappings
INVESTMENT_ENDPOINT_MAP = {
    "get_etf_holdings": ETF_HOLDINGS,
    "get_etf_holding_dates": ETF_HOLDING_DATES,
    "get_etf_info": ETF_INFO,
    "get_etf_sector_weightings": ETF_SECTOR_WEIGHTINGS,
    "get_etf_country_weightings": ETF_COUNTRY_WEIGHTINGS,
    "get_etf_exposure": ETF_EXPOSURE,
    "get_etf_holder": ETF_HOLDER,
    "get_mutual_fund_dates": MUTUAL_FUND_DATES,
    "get_mutual_fund_holdings": MUTUAL_FUND_HOLDINGS,
    "get_mutual_fund_by_name": MUTUAL_FUND_BY_NAME,
    "get_mutual_fund_holder": MUTUAL_FUND_HOLDER,
}

# Complete semantic definitions
INVESTMENT_ENDPOINTS_SEMANTICS = {
    "etf_holdings": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_holdings",  # Keep full method name here
        natural_description=(
            "Retrieve detailed holdings information for an ETF including assets, "
            "weights, and market values as of a specific date"
        ),
        example_queries=[
            "What are the holdings of SPY?",
            "Show me QQQ's portfolio composition",
            "Get VTI holdings as of 2024-01-15",
            "What stocks does IWM hold?",
        ],
        related_terms=[
            "portfolio holdings",
            "constituents",
            "components",
            "assets",
            "positions",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Holdings",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "date": DATE_HINT,
        },
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Symbol of the held security",
                examples=["AAPL", "MSFT", "GOOGL"],
                related_terms=["ticker", "stock symbol"],
            ),
            "value_usd": ResponseFieldInfo(
                description="Market value in USD",
                examples=["1250000", "750000"],
                related_terms=["market value", "position value"],
            ),
            "percentage_value": ResponseFieldInfo(
                description="Percentage of portfolio",
                examples=["2.5", "1.8"],
                related_terms=["weight", "allocation"],
            ),
        },
        use_cases=[
            "Portfolio analysis",
            "Investment research",
            "Risk assessment",
            "Asset allocation analysis",
        ],
    ),
    "etf_holding_dates": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_holding_dates",
        natural_description=(
            "Get a list of available portfolio dates for which ETF holdings data "
            "is available"
        ),
        example_queries=[
            "When was SPY's portfolio last updated?",
            "Get available holding dates for QQQ",
            "Show me VTI's portfolio dates",
        ],
        related_terms=[
            "portfolio dates",
            "holding dates",
            "reporting dates",
            "disclosure dates",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Holdings",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "portfolio_date": ResponseFieldInfo(
                description="Date of portfolio holdings",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["date", "as of date", "holding date"],
            ),
        },
        use_cases=[
            "Portfolio tracking",
            "Historical analysis",
            "Portfolio changes monitoring",
        ],
    ),
    "etf_info": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_info",  # Keep full method name
        natural_description=(
            "Get comprehensive information about an ETF including expense ratio, "
            "assets under management, and fund characteristics"
        ),
        example_queries=[
            "Get ETF details for SPY",
            "Show me information about QQQ",
            "What are VTI's fund characteristics?",
        ],
        related_terms=[
            "fund information",
            "ETF details",
            "fund characteristics",
            "fund overview",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Information",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "expense_ratio": ResponseFieldInfo(
                description="Fund expense ratio",
                examples=["0.09", "0.15"],
                related_terms=["fees", "costs"],
            ),
            "aum": ResponseFieldInfo(
                description="Assets under management",
                examples=["350000000000", "25000000000"],
                related_terms=["assets", "fund size"],
            ),
        },
        use_cases=[
            "Fund selection",
            "Investment research",
            "Cost analysis",
        ],
    ),
    "etf_sector_weightings": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_sector_weightings",
        natural_description=(
            "Retrieve detailed sector allocation data for an ETF, showing the "
            "percentage of the portfolio invested in different market sectors"
        ),
        example_queries=[
            "What are SPY's sector weights?",
            "Show sector allocation for QQQ",
            "Get VTI sector breakdown",
            "How is IWM distributed across sectors?",
            "What sectors does VOO invest in?",
        ],
        related_terms=[
            "sector allocation",
            "industry weights",
            "sector exposure",
            "sector distribution",
            "industry breakdown",
            "sector diversification",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Analysis",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "sector": ResponseFieldInfo(
                description="Market sector name",
                examples=["Technology", "Healthcare", "Financials"],
                related_terms=["industry", "sector name", "market sector"],
            ),
            "weight_percentage": ResponseFieldInfo(
                description="Sector weight in portfolio",
                examples=["25.5", "18.3", "12.7"],
                related_terms=["allocation", "exposure", "percentage"],
            ),
        },
        use_cases=[
            "Sector analysis",
            "Portfolio diversification assessment",
            "Risk analysis",
            "Investment strategy alignment",
            "Sector exposure monitoring",
        ],
    ),
    "etf_country_weightings": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_country_weightings",
        natural_description=(
            "Get detailed geographic allocation data for an ETF, showing the "
            "percentage of the portfolio invested in different countries"
        ),
        example_queries=[
            "What are the country weights in VEA?",
            "Show country allocation for EFA",
            "Get VXUS country breakdown",
            "How is VWO distributed across countries?",
            "What countries does IEFA invest in?",
        ],
        related_terms=[
            "country allocation",
            "geographic exposure",
            "country distribution",
            "international exposure",
            "regional weights",
            "country diversification",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Analysis",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "country": ResponseFieldInfo(
                description="Country name",
                examples=["United States", "Japan", "United Kingdom"],
                related_terms=["nation", "market", "geography", "region"],
            ),
            "weight_percentage": ResponseFieldInfo(
                description="Country weight in portfolio",
                examples=["45.5", "15.3", "8.7"],
                related_terms=["allocation", "exposure", "percentage"],
            ),
        },
        use_cases=[
            "Geographic diversification analysis",
            "Country risk assessment",
            "International exposure monitoring",
            "Regional allocation strategy",
            "Country concentration analysis",
        ],
    ),
    "etf_exposure": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_exposure",
        natural_description=(
            "Retrieve detailed stock exposure data for an ETF, showing specific "
            "securities held and their weights in the portfolio"
        ),
        example_queries=[
            "What stocks does SPY hold?",
            "Show QQQ's stock exposures",
            "Get VTI stock breakdown",
            "List IWM's stock holdings",
            "What companies are in VOO?",
        ],
        related_terms=[
            "stock holdings",
            "security exposure",
            "portfolio holdings",
            "stock weights",
            "equity exposure",
            "constituent weights",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Holdings",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "asset_exposure": ResponseFieldInfo(
                description="Stock symbol held in portfolio",
                examples=["AAPL", "MSFT", "GOOGL"],
                related_terms=["stock", "security", "holding", "position"],
            ),
            "shares_number": ResponseFieldInfo(
                description="Number of shares held",
                examples=["150000", "75000", "25000"],
                related_terms=["quantity", "position size", "shares"],
            ),
            "weight_percentage": ResponseFieldInfo(
                description="Portfolio weight percentage",
                examples=["7.5", "5.3", "3.2"],
                related_terms=["allocation", "weight", "exposure"],
            ),
        },
        use_cases=[
            "Portfolio composition analysis",
            "Stock exposure monitoring",
            "Concentration risk assessment",
            "Position size analysis",
            "Portfolio replication",
        ],
    ),
    "etf_holder": EndpointSemantics(
        client_name="investment",
        method_name="get_etf_holder",
        natural_description=(
            "Get information about institutional holders of an ETF, including "
            "their holdings and position sizes"
        ),
        example_queries=[
            "Who owns SPY?",
            "Show QQQ's institutional holders",
            "Get VTI ownership information",
            "List IWM's major holders",
            "Who are VOO's largest investors?",
        ],
        related_terms=[
            "institutional holders",
            "ownership",
            "investors",
            "stakeholders",
            "fund holders",
            "institutional ownership",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="ETF Ownership",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "holder": ResponseFieldInfo(
                description="Name of institutional holder",
                examples=["BlackRock", "Vanguard", "State Street"],
                related_terms=["institution", "investor", "owner"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["15000000", "7500000", "2500000"],
                related_terms=["position size", "holding size", "quantity"],
            ),
            "value": ResponseFieldInfo(
                description="Value of position",
                examples=["750000000", "375000000"],
                related_terms=["position value", "holding value", "worth"],
            ),
        },
        use_cases=[
            "Ownership analysis",
            "Institutional interest tracking",
            "Liquidity assessment",
            "Investment sentiment analysis",
            "Stakeholder analysis",
        ],
    ),
    "mutual_fund_dates": EndpointSemantics(
        client_name="investment",
        method_name="get_mutual_fund_dates",
        natural_description=(
            "Retrieve available portfolio dates for mutual fund holdings data, "
            "helping track portfolio composition changes over time"
        ),
        example_queries=[
            "When was VFIAX's portfolio last updated?",
            "Get available holding dates for PRNHX",
            "Show me FCNTX's portfolio dates",
            "What dates are available for VTSMX holdings?",
            "List portfolio dates for VTSAX",
        ],
        related_terms=[
            "portfolio dates",
            "disclosure dates",
            "reporting dates",
            "filing dates",
            "update dates",
            "holdings dates",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="Mutual Fund Holdings",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "cik": CIK_HINT,
        },
        response_hints={
            "portfolio_date": ResponseFieldInfo(
                description="Date of portfolio holdings",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["date", "as of date", "holding date"],
            ),
        },
        use_cases=[
            "Portfolio tracking",
            "Historical analysis",
            "Portfolio changes monitoring",
            "Data availability checking",
            "Reporting timeline analysis",
        ],
    ),
    "mutual_fund_by_name": EndpointSemantics(
        client_name="investment",
        method_name="get_mutual_fund_by_name",
        natural_description=(
            "Search for mutual funds by name to get their holdings and basic "
            "information"
        ),
        example_queries=[
            'Find funds named "Vanguard 500"',
            'Search for "Fidelity Magellan"',
            'Look up "T. Rowe Price Growth"',
            'Find mutual funds with "Index" in the name',
            'Search for "Growth Fund" mutual funds',
        ],
        related_terms=[
            "fund search",
            "fund lookup",
            "fund finder",
            "mutual fund search",
            "fund discovery",
            "fund identification",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="Mutual Fund Search",
        parameter_hints={
            "name": FUND_NAME_HINT,
        },
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Fund symbol",
                examples=["VFIAX", "FMAGX"],
                related_terms=["ticker", "symbol", "code"],
            ),
            "name": ResponseFieldInfo(
                description="Fund name",
                examples=["Vanguard 500 Index Fund", "Fidelity Magellan Fund"],
                related_terms=["fund name", "product name"],
            ),
        },
        use_cases=[
            "Fund discovery",
            "Investment research",
            "Fund comparison",
            "Product lookup",
            "Fund identification",
        ],
    ),
    "mutual_fund_holder": EndpointSemantics(
        client_name="investment",
        method_name="get_mutual_fund_holder",
        natural_description=(
            "Get information about institutional holders of a mutual fund, "
            "including their holdings and position sizes"
        ),
        example_queries=[
            "Who owns VFIAX?",
            "Show PRNHX institutional holders",
            "Get FCNTX ownership information",
            "List VTSMX major holders",
            "Who are VTSAX's largest investors?",
        ],
        related_terms=[
            "fund holders",
            "institutional owners",
            "fund ownership",
            "stakeholders",
            "institutional investors",
            "major holders",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="Mutual Fund Ownership",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "holder": ResponseFieldInfo(
                description="Name of institutional holder",
                examples=["BlackRock", "Vanguard", "Fidelity"],
                related_terms=["institution", "investor", "owner"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["1500000", "750000"],
                related_terms=["position size", "holding size", "quantity"],
            ),
            "date_reported": ResponseFieldInfo(
                description="Date of reported holding",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["report date", "date", "as of date", "holding date"],
            ),
        },
        use_cases=[
            "Fund ownership analysis",
            "Institutional interest tracking",
            "Liquidity assessment",
            "Investment sentiment analysis",
            "Stakeholder analysis",
        ],
    ),
    "mutual_fund_holdings": EndpointSemantics(
        client_name="investment",
        method_name="get_mutual_fund_holdings",
        natural_description=(
            "Get detailed holdings information for a mutual fund, including "
            "securities held, weights, and market values as of a specific date"
        ),
        example_queries=[
            "What does VFIAX hold?",
            "Show PRNHX holdings",
            "Get FCNTX portfolio composition",
            "List VTSMX holdings",
            "What stocks are in VTSAX?",
        ],
        related_terms=[
            "portfolio holdings",
            "fund composition",
            "positions",
            "investments",
            "securities held",
            "portfolio constituents",
        ],
        category=SemanticCategory.INVESTMENT_PRODUCTS,
        sub_category="Mutual Fund Holdings",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "date": DATE_HINT,
        },
        response_hints={
            "asset": ResponseFieldInfo(
                description="Security name or symbol",
                examples=["AAPL", "MSFT", "Apple Inc"],
                related_terms=["security", "holding", "position", "investment"],
            ),
            "shares": ResponseFieldInfo(
                description="Number of shares held",
                examples=["150000", "75000"],
                related_terms=["quantity", "position size"],
            ),
            "market_value": ResponseFieldInfo(
                description="Value of position",
                examples=["25000000", "12500000"],
                related_terms=["position value", "worth", "value"],
            ),
        },
        use_cases=[
            "Portfolio analysis",
            "Investment strategy analysis",
            "Risk assessment",
            "Position monitoring",
            "Fund comparison",
        ],
    ),
}
