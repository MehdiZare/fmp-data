from __future__ import annotations

from fmp_data.economics.endpoints import (
    ECONOMIC_CALENDAR,
    ECONOMIC_INDICATORS,
    MARKET_RISK_PREMIUM,
    TREASURY_RATES,
)
from fmp_data.economics.schema import EconomicIndicatorType
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

ECONOMICS_ENDPOINT_MAP = {
    "get_treasury_rates": TREASURY_RATES,
    "get_economic_indicators": ECONOMIC_INDICATORS,
    "get_economic_calendar": ECONOMIC_CALENDAR,
    "get_market_risk_premium": MARKET_RISK_PREMIUM,
}
# Additional semantic mappings for common terms and concepts
ECONOMICS_COMMON_TERMS = {
    "gdp": [
        "gross domestic product",
        "economic output",
        "national output",
        "economic production",
        "national production",
    ],
    "inflation": [
        "price increases",
        "cost increases",
        "price changes",
        "purchasing power",
        "price levels",
    ],
    "interest_rates": [
        "yields",
        "rates",
        "borrowing costs",
        "lending rates",
        "financing costs",
    ],
    "employment": [
        "jobs",
        "labor market",
        "workforce",
        "employment situation",
        "labor statistics",
    ],
}

DATE_HINTS = {
    "start_date": ParameterHint(
        natural_names=["start date", "from date", "beginning", "since"],
        extraction_patterns=[
            r"(\d{4}-\d{2}-\d{2})",
            r"(?:from|since|after)\s+(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2023-01-01", "2022-12-31"],
        context_clues=["from", "since", "starting", "beginning", "after"],
    ),
    "end_date": ParameterHint(  # Changed from "to_date"
        natural_names=["end date", "to date", "until", "through"],
        extraction_patterns=[
            r"(?:to|until|through)\s+(\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})",
        ],
        examples=["2024-01-01", "2023-12-31"],
        context_clues=["to", "until", "through", "ending"],
    ),
}
# Time period mapping for natural language processing
ECONOMICS_TIME_PERIODS = {
    "daily": {
        "patterns": [
            r"(?i)daily",
            r"(?i)day by day",
            r"(?i)each day",
            r"(?i)per day",
        ],
        "terms": ["daily", "day", "24-hour", "intraday"],
    },
    "weekly": {
        "patterns": [
            r"(?i)weekly",
            r"(?i)week by week",
            r"(?i)each week",
            r"(?i)per week",
        ],
        "terms": ["weekly", "week", "7-day", "per week"],
    },
    "monthly": {
        "patterns": [
            r"(?i)monthly",
            r"(?i)month by month",
            r"(?i)each month",
            r"(?i)per month",
        ],
        "terms": ["monthly", "month", "30-day", "per month"],
    },
    "quarterly": {
        "patterns": [
            r"(?i)quarterly",
            r"(?i)quarter by quarter",
            r"(?i)each quarter",
            r"(?i)per quarter",
        ],
        "terms": ["quarterly", "quarter", "3-month", "Q1", "Q2", "Q3", "Q4"],
    },
    "annual": {
        "patterns": [
            r"(?i)annual",
            r"(?i)yearly",
            r"(?i)per year",
            r"(?i)each year",
        ],
        "terms": ["annual", "yearly", "year", "12-month", "per year"],
    },
}

# Economic indicator categories for organization
ECONOMIC_INDICATOR_CATEGORIES = {
    "output": [
        "gdp",
        "gdp_growth",
        "industrial_production",
        "capacity_utilization",
    ],
    "prices": [
        "inflation",
        "cpi",
        "ppi",
        "import_prices",
        "export_prices",
    ],
    "employment": [
        "unemployment",
        "nonfarm_payroll",
        "jobless_claims",
        "employment_cost",
    ],
    "consumption": [
        "retail_sales",
        "personal_spending",
        "consumer_confidence",
        "consumer_sentiment",
    ],
    "housing": [
        "housing_starts",
        "building_permits",
        "home_sales",
        "construction_spending",
    ],
    "trade": [
        "balance_of_trade",
        "current_account",
        "import_export",
        "trade_balance",
    ],
    "business": [
        "durable_goods",
        "factory_orders",
        "business_inventories",
        "business_confidence",
    ],
    "government": [
        "government_budget",
        "government_debt",
        "government_spending",
        "tax_revenue",
    ],
}

# Function mappings for common calculations
ECONOMICS_CALCULATIONS = {
    "growth_rate": {
        "description": "Calculate period-over-period growth rate",
        "formula": "((current_value - previous_value) / previous_value) * 100",
        "parameters": ["current_value", "previous_value"],
        "return_type": "percentage",
    },
    "inflation_rate": {
        "description": "Calculate inflation rate from price indices",
        "formula": "((current_cpi - previous_cpi) / previous_cpi) * 100",
        "parameters": ["current_cpi", "previous_cpi"],
        "return_type": "percentage",
    },
    "real_rate": {
        "description": "Calculate real interest rate",
        "formula": "nominal_rate - inflation_rate",
        "parameters": ["nominal_rate", "inflation_rate"],
        "return_type": "percentage",
    },
}

# Complete Semantic Definitions
ECONOMICS_ENDPOINTS_SEMANTICS = {
    "treasury_rates": EndpointSemantics(
        client_name="economics",
        method_name="get_treasury_rates",
        natural_description=(
            "Retrieve U.S. Treasury rates across multiple maturities including bills, "
            "notes, and bonds. "
        ),
        example_queries=[
            "What are the current Treasury rates?",
            "Get historical treasury yields for last month",
            "Show me the yield curve data",
            "What's the 10-year Treasury rate?",
            "Compare 2-year and 10-year yields",
            "Get Treasury rates between January and March",
            "Show me the full yield curve",
            "What's the 30-year bond rate?",
        ],
        related_terms=[
            "treasury yields",
            "government bonds",
            "interest rates",
            "yield curve",
            "T-bills",
            "T-notes",
            "T-bonds",
            "federal debt",
            "bond market",
            "fixed income",
        ],
        category=SemanticCategory.ECONOMIC,
        sub_category="Interest Rates",
        parameter_hints={
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "rate_date": ResponseFieldInfo(
                description="Date of the Treasury rate measurements",
                examples=["2024-01-20", "2023-12-31"],
                related_terms=["date", "trading date", "market date", "quote date"],
            ),
            "month_1": ResponseFieldInfo(
                description="1-month Treasury bill rate",
                examples=["4.25", "3.95"],
                related_terms=["1-month rate", "short-term rate", "T-bill rate"],
            ),
            "month_3": ResponseFieldInfo(
                description="3-month Treasury bill rate",
                examples=["4.35", "4.05"],
                related_terms=["3-month rate", "quarterly rate", "T-bill rate"],
            ),
            "month_6": ResponseFieldInfo(
                description="6-month Treasury bill rate",
                examples=["4.45", "4.15"],
                related_terms=["6-month rate", "semi-annual rate"],
            ),
            "year_1": ResponseFieldInfo(
                description="1-year Treasury note rate",
                examples=["4.55", "4.25"],
                related_terms=["1-year yield", "annual rate"],
            ),
            "year_2": ResponseFieldInfo(
                description="2-year Treasury note rate",
                examples=["4.65", "4.35"],
                related_terms=["2-year yield", "short-term note"],
            ),
            "year_5": ResponseFieldInfo(
                description="5-year Treasury note rate",
                examples=["4.75", "4.45"],
                related_terms=["5-year yield", "medium-term note"],
            ),
            "year_10": ResponseFieldInfo(
                description="10-year Treasury note rate (benchmark)",
                examples=["4.85", "4.55"],
                related_terms=["10-year yield", "benchmark rate"],
            ),
            "year_30": ResponseFieldInfo(
                description="30-year Treasury bond rate",
                examples=["4.95", "4.65"],
                related_terms=["30-year yield", "long bond", "long-term rate"],
            ),
        },
        use_cases=[
            "Analyzing interest rate trends",
            "Monitoring yield curve changes",
            "Fixed income market analysis",
            "Economic policy research",
            "Bond market analysis",
            "Investment strategy development",
            "Risk-free rate determination",
            "Portfolio management",
            "Economic forecasting",
            "Monetary policy analysis",
        ],
    ),
    "economic_indicators": EndpointSemantics(
        client_name="economics",
        method_name="get_economic_indicators",
        natural_description=(
            "Access comprehensive economic indicator data including GDP, inflation, "
            "employment statistics, trade balances, and more."
        ),
        example_queries=[
            "Get GDP growth rate",
            "Show inflation data",
            "What's the unemployment rate?",
            "Get CPI numbers",
            "Show industrial production",
            "Get retail sales data",
            "What's the current account balance?",
            "Show consumer confidence index",
        ],
        related_terms=[
            "economic data",
            "macroeconomic indicators",
            "economic metrics",
            "economic statistics",
            "macro data",
            "economic measures",
            "economic health",
            "macro indicators",
            "economic activity",
            "statistical data",
        ],
        category=SemanticCategory.ECONOMIC,
        sub_category="Economic Indicators",
        parameter_hints={
            "name": ParameterHint(
                natural_names=[
                    "indicator",
                    "metric",
                    "measure",
                    "statistic",
                    "economic measure",
                    "data point",
                ],
                extraction_patterns=[
                    r"(?i)(GDP|CPI|PMI|unemployment|inflation)",
                    r"(?i)(consumer.*index|producer.*index)",
                    r"(?i)(retail.*sales|industrial.*production)",
                    r"(?i)(trade.*balance|current.*account)",
                ],
                examples=list(EconomicIndicatorType),
                context_clues=[
                    "rate",
                    "index",
                    "indicator",
                    "measurement",
                    "metric",
                    "statistic",
                    "data",
                ],
            ),
        },
        response_hints={
            "indicator_date": ResponseFieldInfo(
                description="Date of the indicator measurement",
                examples=["2024-01-15", "2023-Q4"],
                related_terms=[
                    "release date",
                    "report date",
                    "period",
                    "measurement date",
                ],
            ),
            "value": ResponseFieldInfo(
                description="Value of the economic indicator",
                examples=["3.2", "245000", "7.1"],
                related_terms=["reading", "level", "measurement", "rate", "figure"],
            ),
            "name": ResponseFieldInfo(
                description="Name of the economic indicator",
                examples=list(EconomicIndicatorType),
                related_terms=["metric", "measure", "indicator", "statistic"],
            ),
        },
        use_cases=[
            "Economic analysis and research",
            "Policy research and development",
            "Market research and analysis",
            "Economic forecasting",
            "Investment planning",
            "Business strategy",
            "Risk assessment",
            "Country analysis",
            "Sector analysis",
            "Macroeconomic modeling",
        ],
    ),
    "economic_calendar": EndpointSemantics(
        client_name="economics",
        method_name="get_economic_calendar",
        natural_description=(
            "Access a comprehensive calendar of economic events, data releases, "
            "and policy announcements."
        ),
        example_queries=[
            "Show economic calendar",
            "What economic releases are coming up?",
            "Get economic events for next week",
            "Show me important economic announcements",
            "When is the next GDP release?",
            "Get calendar of economic events",
            "Show upcoming data releases",
        ],
        related_terms=[
            "economic events",
            "data releases",
            "economic announcements",
            "economic schedule",
            "market events",
            "financial calendar",
        ],
        category=SemanticCategory.ECONOMIC,
        sub_category="Economic Events",
        parameter_hints={
            "start_date": ParameterHint(
                natural_names=["start date", "from", "beginning"],
                extraction_patterns=[
                    r"(\d{4}-\d{2}-\d{2})",
                    r"(?:from|after)\s+(\d{4}-\d{2}-\d{2})",
                    r"(?:starting|beginning)\s+(\d{2}/\d{2}/\d{4})",
                ],
                examples=["2024-01-01", "2024-02-01", "01/15/2024"],
                context_clues=[
                    "from",
                    "starting",
                    "after",
                    "beginning",
                    "upcoming",
                    "future",
                    "next",
                ],
            ),
            "end_date": ParameterHint(
                natural_names=["end date", "until", "through"],
                extraction_patterns=[
                    r"(?:to|until)\s+(\d{4}-\d{2}-\d{2})",
                    r"(\d{4}-\d{2}-\d{2})",
                    r"(\d{2}/\d{2}/\d{4})",
                ],
                examples=["2024-01-31", "2024-02-28", "03/31/2024"],
                context_clues=[
                    "to",
                    "until",
                    "through",
                    "ending",
                    "by",
                    "up to",
                    "no later than",
                ],
            ),
        },
        response_hints={
            "event": ResponseFieldInfo(
                description="Name of the economic event or release",
                examples=[
                    "GDP Release",
                    "FOMC Meeting",
                    "CPI Data",
                    "Nonfarm Payrolls",
                    "Retail Sales",
                ],
                related_terms=[
                    "announcement",
                    "release",
                    "report",
                    "meeting",
                    "data",
                    "publication",
                    "statement",
                ],
            ),
            "date": ResponseFieldInfo(
                description="Date and time of the event",
                examples=["2024-01-20 14:30:00", "2024-02-15 10:00:00"],
                related_terms=[
                    "release time",
                    "announcement date",
                    "schedule",
                    "publication time",
                    "release date",
                ],
            ),
            "country": ResponseFieldInfo(
                description="Country code for the event",
                examples=["US", "UK", "EU", "JP"],
                related_terms=["region", "market", "economy"],
            ),
            "actual": ResponseFieldInfo(
                description="Actual released value",
                examples=["3.2%", "245K", "58.6"],
                related_terms=[
                    "result",
                    "released value",
                    "actual number",
                    "reported value",
                    "final number",
                ],
            ),
            "previous": ResponseFieldInfo(
                description="Previous period's value",
                examples=["3.1%", "240K", "57.9"],
                related_terms=[
                    "prior value",
                    "last reading",
                    "previous number",
                    "last period",
                    "prior reading",
                ],
            ),
            "estimate": ResponseFieldInfo(
                description="Expected/forecast value",
                examples=["3.3%", "250K", "58.0"],
                related_terms=[
                    "forecast",
                    "expected",
                    "consensus",
                    "projected",
                    "estimated",
                ],
            ),
            "impact": ResponseFieldInfo(
                description="Expected market impact level",
                examples=["High", "Medium", "Low"],
                related_terms=[
                    "significance",
                    "importance",
                    "market effect",
                    "volatility impact",
                    "market reaction",
                ],
            ),
        },
        use_cases=[
            "Event planning and scheduling",
            "Market timing strategies",
            "Economic monitoring and tracking",
            "Trading strategy development",
            "Risk management",
            "Market analysis",
            "Research planning",
            "Portfolio management",
            "Economic research",
            "Policy analysis",
        ],
    ),
    "market_risk_premium": EndpointSemantics(
        client_name="economics",
        method_name="get_market_risk_premium",
        natural_description=(
            "Retrieve comprehensive market risk premium data by country, including "
            "equity risk premiums, country-specific risk factors, and total risk "
            "premiums"
        ),
        example_queries=[
            "Get market risk premium data",
            "Show country risk premiums",
            "What's the equity risk premium?",
            "Get risk premium by country",
            "Show market risk by region",
            "Compare country risk premiums",
            "What's the US market premium?",
            "Get global risk premiums",
        ],
        related_terms=[
            "risk premium",
            "market premium",
            "equity premium",
            "country risk",
            "risk factors",
            "market risk",
            "sovereign risk",
            "systematic risk",
            "country premium",
            "risk assessment",
            "market assessment",
            "investment risk",
            "risk metrics",
            "risk factors",
            "cost of equity",
            "required return",
        ],
        category=SemanticCategory.ECONOMIC,
        sub_category="Risk Metrics",
        parameter_hints={},  # No parameters needed
        response_hints={
            "country": ResponseFieldInfo(
                description="Country name for risk premium data",
                examples=["United States", "United Kingdom", "Japan", "Germany"],
                related_terms=[
                    "nation",
                    "market",
                    "region",
                    "economy",
                    "jurisdiction",
                    "territory",
                ],
            ),
            "continent": ResponseFieldInfo(
                description="Continental region of the country",
                examples=["North America", "Europe", "Asia", "South America"],
                related_terms=["region", "geographic area", "economic zone"],
            ),
            "total_equity_risk_premium": ResponseFieldInfo(
                description="Total equity risk premium including country risk",
                examples=["5.20", "6.75", "4.90", "7.25"],
                related_terms=[
                    "equity premium",
                    "market premium",
                    "risk premium",
                    "total premium",
                    "required premium",
                ],
            ),
            "country_risk_premium": ResponseFieldInfo(
                description="Country-specific risk premium component",
                examples=["1.20", "2.50", "0.75", "3.15"],
                related_terms=[
                    "sovereign risk",
                    "country premium",
                    "market risk",
                    "country-specific risk",
                    "sovereign premium",
                ],
            ),
        },
        use_cases=[
            "Investment analysis and valuation",
            "Country risk assessment",
            "Portfolio management and allocation",
            "Risk modeling and quantification",
            "Asset pricing and valuation",
            "International investment strategy",
            "Market entry analysis",
            "Capital budgeting",
            "Cost of capital estimation",
            "Risk-adjusted return analysis",
        ],
    ),
}
