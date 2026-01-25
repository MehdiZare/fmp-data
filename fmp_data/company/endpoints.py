# company/endpoints.py
from __future__ import annotations

from fmp_data.company.models import (
    AftermarketQuote,
    AftermarketTrade,
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyPeer,
    CompanyProfile,
    EmployeeCount,
    ExecutiveCompensation,
    ExecutiveCompensationBenchmark,
    GeographicRevenueSegment,
    HistoricalPrice,
    HistoricalShareFloat,
    IntradayPrice,
    MergerAcquisition,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    ProductRevenueSegment,
    Quote,
    ShareFloat,
    SimpleQuote,
    StockPriceChange,
    SymbolChange,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)
from fmp_data.company.schema import (
    BaseSymbolArg,
    GeographicRevenueArgs,
    ProductRevenueArgs,
    SymbolChangesArgs,
)
from fmp_data.fundamental.models import (
    AsReportedBalanceSheet,
    AsReportedCashFlowStatement,
    AsReportedIncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    EnterpriseValue,
    FinancialGrowth,
    FinancialRatiosTTM,
    FinancialScore,
    IncomeStatement,
    KeyMetricsTTM,
)
from fmp_data.intelligence.models import DividendEvent, EarningEvent, StockSplitEvent
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    MarketCapitalization,
    ParamLocation,
    ParamType,
    URLType,
)

QUOTE: Endpoint[Quote] = Endpoint(
    name="quote",
    path="quote",
    version=APIVersion.STABLE,
    description="Get real-time stock quote",
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
    response_model=Quote,
)

SIMPLE_QUOTE: Endpoint[SimpleQuote] = Endpoint(
    name="simple_quote",
    path="quote-short",
    version=APIVersion.STABLE,
    description="Get simple stock quote",
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
    response_model=SimpleQuote,
)

AFTERMARKET_TRADE: Endpoint[AftermarketTrade] = Endpoint(
    name="aftermarket_trade",
    path="aftermarket-trade",
    version=APIVersion.STABLE,
    description="Get aftermarket (post-market) trade data for a symbol",
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
    response_model=AftermarketTrade,
    arg_model=BaseSymbolArg,
)

AFTERMARKET_QUOTE: Endpoint[AftermarketQuote] = Endpoint(
    name="aftermarket_quote",
    path="aftermarket-quote",
    version=APIVersion.STABLE,
    description="Get aftermarket (post-market) quote data for a symbol",
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
    response_model=AftermarketQuote,
    arg_model=BaseSymbolArg,
)

STOCK_PRICE_CHANGE: Endpoint[StockPriceChange] = Endpoint(
    name="stock_price_change",
    path="stock-price-change",
    version=APIVersion.STABLE,
    description="Get price change percentages across multiple time horizons",
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
    response_model=StockPriceChange,
    arg_model=BaseSymbolArg,
)

HISTORICAL_PRICE: Endpoint = Endpoint(
    name="historical_price",
    path="historical-price-eod/full",
    version=APIVersion.STABLE,
    description="Get historical daily price data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
    ],
    response_model=HistoricalPrice,
)

HISTORICAL_PRICE_LIGHT: Endpoint = Endpoint(
    name="historical_price_light",
    path="historical-price-eod/light",
    version=APIVersion.STABLE,
    description="Get lightweight historical daily price data (OHLC only)",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
    ],
    response_model=HistoricalPrice,
)

HISTORICAL_PRICE_NON_SPLIT_ADJUSTED: Endpoint = Endpoint(
    name="historical_price_non_split_adjusted",
    path="historical-price-eod/non-split-adjusted",
    version=APIVersion.STABLE,
    description="Get historical daily price data without split adjustments",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
    ],
    response_model=HistoricalPrice,
)

HISTORICAL_PRICE_DIVIDEND_ADJUSTED: Endpoint = Endpoint(
    name="historical_price_dividend_adjusted",
    path="historical-price-eod/dividend-adjusted",
    version=APIVersion.STABLE,
    description="Get historical daily price data adjusted for dividends",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        )
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
    ],
    response_model=HistoricalPrice,
)

INTRADAY_PRICE: Endpoint = Endpoint(
    name="intraday_price",
    path="historical-chart/{interval}",
    version=APIVersion.STABLE,
    description="Get intraday price data",
    mandatory_params=[
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval (1min, 5min, 15min, 30min, 1hour, 4hour)",
        ),
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="start_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date",
            alias="to",
        ),
        EndpointParam(
            name="nonadjusted",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Use non-adjusted data",
        ),
    ],
    response_model=IntradayPrice,
)
# Profile Endpoints
PROFILE: Endpoint[CompanyProfile] = Endpoint(
    name="profile",
    path="profile",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
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

CORE_INFORMATION: Endpoint[CompanyCoreInformation] = Endpoint(
    name="core_information",
    path="company-core-information",
    version=APIVersion.STABLE,
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

# Executive Information Endpoints
KEY_EXECUTIVES: Endpoint = Endpoint(
    name="key_executives",
    path="key-executives",
    version=APIVersion.STABLE,
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
            location=ParamLocation.QUERY,
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

EXECUTIVE_COMPENSATION: Endpoint = Endpoint(
    name="executive_compensation",
    path="governance-executive-compensation",
    version=APIVersion.STABLE,
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

EMPLOYEE_COUNT: Endpoint = Endpoint(
    name="employee_count",
    path="employee-count",
    version=APIVersion.STABLE,
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Maximum number of employee count records to return",
        ),
    ],
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

# Symbol Related Endpoints
# Company Operational Data
COMPANY_NOTES: Endpoint = Endpoint(
    name="company_notes",
    path="company-notes",
    version=APIVersion.STABLE,
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

HISTORICAL_SHARE_FLOAT: Endpoint = Endpoint(
    name="historical_share_float",
    path="historical/shares-float",
    version=APIVersion.STABLE,
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

# Revenue Analysis Endpoints
PRODUCT_REVENUE_SEGMENTATION: Endpoint = Endpoint(
    name="product_revenue_segmentation",
    path="revenue-product-segmentation",
    version=APIVersion.STABLE,
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

GEOGRAPHIC_REVENUE_SEGMENTATION: Endpoint = Endpoint(
    name="geographic_revenue_segmentation",
    path="revenue-geographic-segmentation",
    version=APIVersion.STABLE,
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

SYMBOL_CHANGES: Endpoint = Endpoint(
    name="symbol_changes",
    path="symbol-change",
    version=APIVersion.STABLE,
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

SHARE_FLOAT: Endpoint[ShareFloat] = Endpoint(
    name="share_float",
    path="shares-float",
    version=APIVersion.STABLE,
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

MARKET_CAP: Endpoint[MarketCapitalization] = Endpoint(
    name="market_cap",
    path="market-capitalization",
    version=APIVersion.STABLE,
    description="Get market capitalization data",
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
    response_model=MarketCapitalization,
)

HISTORICAL_MARKET_CAP: Endpoint = Endpoint(
    name="historical_market_cap",
    path="historical-market-capitalization",
    version=APIVersion.STABLE,
    description="Get historical market capitalization data",
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
    response_model=MarketCapitalization,
)
PRICE_TARGET: Endpoint = Endpoint(
    name="price_target",
    path="price-target",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price targets",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTarget,
)

PRICE_TARGET_SUMMARY: Endpoint[PriceTargetSummary] = Endpoint(
    name="price_target_summary",
    path="price-target-summary",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price target summary",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTargetSummary,
)

PRICE_TARGET_CONSENSUS: Endpoint[PriceTargetConsensus] = Endpoint(
    name="price_target_consensus",
    path="price-target-consensus",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get price target consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=PriceTargetConsensus,
)

ANALYST_ESTIMATES: Endpoint = Endpoint(
    name="analyst_estimates",
    path="analyst-estimates",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst estimates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Estimate period (annual or quarter)",
            valid_values=["annual", "quarter"],
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
            default=10,
        ),
    ],
    response_model=AnalystEstimate,
)

ANALYST_RECOMMENDATIONS: Endpoint = Endpoint(
    name="analyst_recommendations",
    path="analyst-stock-recommendations",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst recommendations",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=AnalystRecommendation,
)

UPGRADES_DOWNGRADES: Endpoint = Endpoint(
    name="upgrades_downgrades",
    path="upgrades-downgrades",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get upgrades and downgrades",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=UpgradeDowngrade,
)

UPGRADES_DOWNGRADES_CONSENSUS: Endpoint[UpgradeDowngradeConsensus] = Endpoint(
    name="upgrades_downgrades_consensus",
    path="upgrades-downgrades-consensus",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get upgrades and downgrades consensus",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=UpgradeDowngradeConsensus,
)

COMPANY_PEERS: Endpoint = Endpoint(
    name="stock_peers",
    path="stock-peers",
    version=APIVersion.STABLE,
    method=HTTPMethod.GET,
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=CompanyPeer,
    description="Retrieves a list of peers of a company.",
)

PROFILE_CIK: Endpoint[CompanyProfile] = Endpoint(
    name="profile_cik",
    path="profile-cik",
    version=APIVersion.STABLE,
    description="Get company profile using CIK number",
    mandatory_params=[
        EndpointParam(
            name="cik",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company CIK number",
        )
    ],
    optional_params=[],
    response_model=CompanyProfile,
)

DELISTED_COMPANIES: Endpoint = Endpoint(
    name="delisted_companies",
    path="delisted-companies",
    version=APIVersion.STABLE,
    description="Get list of delisted companies",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="page",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Page number for pagination",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results per page",
        ),
    ],
    response_model=CompanyProfile,
)

HISTORICAL_EMPLOYEE_COUNT: Endpoint = Endpoint(
    name="historical_employee_count",
    path="historical/employee-count",
    version=APIVersion.STABLE,
    description="Get historical employee count data",
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
    response_model=EmployeeCount,
)

COMPANY_OUTLOOK: Endpoint = Endpoint(
    name="company_outlook",
    path="company-outlook",
    version=APIVersion.STABLE,
    description="Get comprehensive company outlook data",
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
    response_model=CompanyProfile,  # This would need a more comprehensive model
)

STOCK_SCREENER: Endpoint = Endpoint(
    name="stock_screener",
    path="stock-screener",
    version=APIVersion.STABLE,
    description="Screen stocks based on various criteria",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="market_cap_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Market cap greater than",
        ),
        EndpointParam(
            name="market_cap_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Market cap less than",
        ),
        EndpointParam(
            name="price_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Price greater than",
        ),
        EndpointParam(
            name="price_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Price less than",
        ),
        EndpointParam(
            name="beta_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Beta greater than",
        ),
        EndpointParam(
            name="beta_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Beta less than",
        ),
        EndpointParam(
            name="volume_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Volume greater than",
        ),
        EndpointParam(
            name="volume_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Volume less than",
        ),
        EndpointParam(
            name="dividend_more_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Dividend yield greater than",
        ),
        EndpointParam(
            name="dividend_less_than",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="Dividend yield less than",
        ),
        EndpointParam(
            name="is_etf",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Filter for ETFs",
        ),
        EndpointParam(
            name="is_fund",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Filter for funds",
        ),
        EndpointParam(
            name="is_actively_trading",
            location=ParamLocation.QUERY,
            param_type=ParamType.BOOLEAN,
            required=False,
            description="Filter for actively trading stocks",
        ),
        EndpointParam(
            name="sector",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Filter by sector",
        ),
        EndpointParam(
            name="industry",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Filter by industry",
        ),
        EndpointParam(
            name="country",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Filter by country",
        ),
        EndpointParam(
            name="exchange",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Filter by exchange",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of results to return",
        ),
    ],
    response_model=CompanyProfile,
)

MERGERS_ACQUISITIONS_LATEST: Endpoint = Endpoint(
    name="mergers_acquisitions_latest",
    path="mergers-acquisitions-latest",
    version=APIVersion.STABLE,
    description="Get latest mergers and acquisitions transactions",
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
    response_model=MergerAcquisition,
)

MERGERS_ACQUISITIONS_SEARCH: Endpoint = Endpoint(
    name="mergers_acquisitions_search",
    path="mergers-acquisitions-search",
    version=APIVersion.STABLE,
    description="Search mergers and acquisitions transactions by company name",
    mandatory_params=[
        EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Company name to search for",
        )
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
    response_model=MergerAcquisition,
)

EXECUTIVE_COMPENSATION_BENCHMARK: Endpoint = Endpoint(
    name="executive_compensation_benchmark",
    path="executive-compensation-benchmark",
    version=APIVersion.STABLE,
    description="Get executive compensation benchmark data by industry and year",
    mandatory_params=[
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Year for compensation data",
        )
    ],
    optional_params=[],
    response_model=ExecutiveCompensationBenchmark,
)

COMPANY_DIVIDENDS: Endpoint = Endpoint(
    name="company_dividends",
    path="dividends",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get historical dividend payments for a specific company. "
        "Includes ex-dividend dates, payment dates, and dividend amounts."
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
    optional_params=[
        EndpointParam(
            name="from_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date for dividend history (YYYY-MM-DD)",
            alias="from",
        ),
        EndpointParam(
            name="to_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date for dividend history (YYYY-MM-DD)",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of dividend records to return",
        ),
    ],
    response_model=DividendEvent,
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get Apple's dividend history",
        "Show Microsoft's dividend payments",
        "What dividends has Coca-Cola paid?",
        "Get Johnson & Johnson dividend history",
        "Show dividend payments for Procter & Gamble",
    ],
)

COMPANY_EARNINGS: Endpoint = Endpoint(
    name="company_earnings",
    path="earnings",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get historical earnings reports for a specific company. "
        "Includes actual EPS, estimated EPS, revenue, and earnings dates."
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of earnings reports to return",
            default=20,
        ),
    ],
    response_model=EarningEvent,
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get Apple's earnings history",
        "Show Tesla's earnings reports",
        "What were Amazon's past earnings?",
        "Get Microsoft's earnings results",
        "Show earnings history for Google",
    ],
)

COMPANY_SPLITS: Endpoint = Endpoint(
    name="company_splits",
    path="splits",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get historical stock split information for a specific company. "
        "Includes split dates, ratios (numerator/denominator), and split details."
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
    optional_params=[
        EndpointParam(
            name="from_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="Start date for split history (YYYY-MM-DD)",
            alias="from",
        ),
        EndpointParam(
            name="to_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=False,
            description="End date for split history (YYYY-MM-DD)",
            alias="to",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of split records to return",
        ),
    ],
    response_model=StockSplitEvent,
    arg_model=BaseSymbolArg,
    example_queries=[
        "Get Apple's stock split history",
        "Show Tesla's stock splits",
        "What stock splits has Amazon done?",
        "Get NVIDIA's split history",
        "Show historical splits for Google",
    ],
)

INCOME_STATEMENT_TTM: Endpoint = Endpoint(
    name="income_statement_ttm",
    path="income-statement-ttm",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get trailing twelve months (TTM) income statement data. "
        "Provides the most recent 12-month financial performance metrics."
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
        )
    ],
    response_model=IncomeStatement,
)

BALANCE_SHEET_TTM: Endpoint = Endpoint(
    name="balance_sheet_ttm",
    path="balance-sheet-statement-ttm",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get trailing twelve months (TTM) balance sheet data. "
        "Shows the company's current financial position."
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
        )
    ],
    response_model=BalanceSheet,
)

CASH_FLOW_TTM: Endpoint = Endpoint(
    name="cash_flow_ttm",
    path="cash-flow-statement-ttm",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get trailing twelve months (TTM) cash flow statement data. "
        "Shows how cash moves through the company over the past 12 months."
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
    optional_params=[
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
        )
    ],
    response_model=CashFlowStatement,
)

KEY_METRICS_TTM: Endpoint = Endpoint(
    name="key_metrics_ttm",
    path="key-metrics-ttm",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get trailing twelve months (TTM) key financial metrics. "
        "Includes important ratios and performance indicators."
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
    response_model=KeyMetricsTTM,
)

FINANCIAL_RATIOS_TTM: Endpoint = Endpoint(
    name="financial_ratios_ttm",
    path="ratios-ttm",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get trailing twelve months (TTM) financial ratios. "
        "Includes profitability, liquidity, leverage, and efficiency ratios."
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
    response_model=FinancialRatiosTTM,
)

FINANCIAL_SCORES: Endpoint = Endpoint(
    name="financial_scores",
    path="financial-scores",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get comprehensive financial health scores including Altman Z-Score, "
        "Piotroski Score, and other financial strength indicators."
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
    response_model=FinancialScore,
)

ENTERPRISE_VALUES: Endpoint = Endpoint(
    name="enterprise_values",
    path="enterprise-values",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get historical enterprise value data including market cap, debt, "
        "cash positions, and calculated enterprise value."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=20,
        ),
    ],
    response_model=EnterpriseValue,
)

INCOME_STATEMENT_GROWTH: Endpoint = Endpoint(
    name="income_statement_growth",
    path="income-statement-growth",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get year-over-year growth rates for income statement line items. "
        "Shows how revenue, expenses, and profits are growing."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=20,
        ),
    ],
    response_model=FinancialGrowth,
)

BALANCE_SHEET_GROWTH: Endpoint = Endpoint(
    name="balance_sheet_growth",
    path="balance-sheet-statement-growth",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get year-over-year growth rates for balance sheet line items. "
        "Shows how assets, liabilities, and equity are changing."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=20,
        ),
    ],
    response_model=FinancialGrowth,
)

CASH_FLOW_GROWTH: Endpoint = Endpoint(
    name="cash_flow_growth",
    path="cash-flow-statement-growth",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get year-over-year growth rates for cash flow statement line items. "
        "Shows trends in operating, investing, and financing cash flows."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=20,
        ),
    ],
    response_model=FinancialGrowth,
)

FINANCIAL_GROWTH: Endpoint = Endpoint(
    name="financial_growth",
    path="financial-growth",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get comprehensive financial growth metrics across all statements. "
        "Combines income, balance sheet, and cash flow growth rates."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual, quarter, FY, Q1-Q4)",
            default="annual",
            valid_values=["annual", "quarter", "FY", "Q1", "Q2", "Q3", "Q4"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=20,
        ),
    ],
    response_model=FinancialGrowth,
)

FINANCIAL_REPORTS_JSON: Endpoint = Endpoint(
    name="financial_reports_json",
    path="financial-reports-json",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get Form 10-K financial reports in JSON format. "
        "Provides structured access to annual report data."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Report year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Report period (FY or Q1-Q4)",
            default="FY",
            valid_values=["FY", "Q1", "Q2", "Q3", "Q4"],
        ),
    ],
    optional_params=[],
    response_model=dict,  # This would need a proper model
)

FINANCIAL_REPORTS_XLSX: Endpoint = Endpoint(
    name="financial_reports_xlsx",
    path="financial-reports-xlsx",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get Form 10-K financial reports in Excel format. "
        "Returns a downloadable XLSX file with financial data."
    ),
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
        EndpointParam(
            name="year",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=True,
            description="Report year",
        ),
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="Report period (FY or Q1-Q4)",
            default="FY",
            valid_values=["FY", "Q1", "Q2", "Q3", "Q4"],
        ),
    ],
    optional_params=[],
    response_model=bytes,  # Binary data
)

INCOME_STATEMENT_AS_REPORTED: Endpoint = Endpoint(
    name="income_statement_as_reported",
    path="income-statement-as-reported",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get income statement as originally reported without adjustments. "
        "Shows exact figures from company filings."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual or quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=10,
        ),
    ],
    response_model=AsReportedIncomeStatement,
)

BALANCE_SHEET_AS_REPORTED: Endpoint = Endpoint(
    name="balance_sheet_as_reported",
    path="balance-sheet-statement-as-reported",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get balance sheet as originally reported without adjustments. "
        "Shows exact figures from company filings."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual or quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=10,
        ),
    ],
    response_model=AsReportedBalanceSheet,
)

CASH_FLOW_AS_REPORTED: Endpoint = Endpoint(
    name="cash_flow_as_reported",
    path="cash-flow-statement-as-reported",
    version=APIVersion.STABLE,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description=(
        "Get cash flow statement as originally reported without adjustments. "
        "Shows exact figures from company filings."
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
    optional_params=[
        EndpointParam(
            name="period",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Period type (annual or quarter)",
            default="annual",
            valid_values=["annual", "quarter"],
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            required=False,
            description="Number of periods to return",
            default=10,
        ),
    ],
    response_model=AsReportedCashFlowStatement,
)
