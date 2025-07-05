# company/endpoints.py
from __future__ import annotations

from fmp_data.company.models import (
    AnalystEstimate,
    AnalystRecommendation,
    CompanyCoreInformation,
    CompanyExecutive,
    CompanyNote,
    CompanyProfile,
    EmployeeCount,
    ExecutiveCompensation,
    GeographicRevenueSegment,
    HistoricalData,
    HistoricalShareFloat,
    IntradayPrice,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    ProductRevenueSegment,
    Quote,
    ShareFloat,
    SimpleQuote,
    SymbolChange,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)
from fmp_data.company.schema import (
    BaseSymbolArg,
    GeographicRevenueArgs,
    LogoArgs,
    ProductRevenueArgs,
    SymbolChangesArgs,
)
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

QUOTE: Endpoint = Endpoint(
    name="quote",
    path="quote/{symbol}",
    version=APIVersion.V3,
    description="Get real-time stock quote",
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
    response_model=Quote,
)

SIMPLE_QUOTE: Endpoint = Endpoint(
    name="simple_quote",
    path="quote-short/{symbol}",
    version=APIVersion.V3,
    description="Get simple stock quote",
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
    response_model=SimpleQuote,
)

HISTORICAL_PRICE: Endpoint = Endpoint(
    name="historical_price",
    path="historical-price-full/{symbol}",
    version=APIVersion.V3,
    description="Get historical daily price data",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
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
            required=True,
            description="Start date",
            alias="from",
        ),
        EndpointParam(
            name="end_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATE,
            required=True,
            description="End date",
            alias="to",
        ),
    ],
    response_model=HistoricalData,
)

INTRADAY_PRICE: Endpoint = Endpoint(
    name="intraday_price",
    path="historical-chart/{interval}/{symbol}",
    version=APIVersion.V3,
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
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol (ticker)",
        ),
    ],
    optional_params=[],
    response_model=IntradayPrice,
)
# Profile Endpoints
PROFILE: Endpoint = Endpoint(
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

CORE_INFORMATION: Endpoint = Endpoint(
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

# Executive Information Endpoints
KEY_EXECUTIVES: Endpoint = Endpoint(
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

EXECUTIVE_COMPENSATION: Endpoint = Endpoint(
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

EMPLOYEE_COUNT: Endpoint = Endpoint(
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

# Symbol Related Endpoints
COMPANY_LOGO: Endpoint = Endpoint(
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
COMPANY_NOTES: Endpoint = Endpoint(
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

HISTORICAL_SHARE_FLOAT: Endpoint = Endpoint(
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

# Revenue Analysis Endpoints
PRODUCT_REVENUE_SEGMENTATION: Endpoint = Endpoint(
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

GEOGRAPHIC_REVENUE_SEGMENTATION: Endpoint = Endpoint(
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

SYMBOL_CHANGES: Endpoint = Endpoint(
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

SHARE_FLOAT: Endpoint = Endpoint(
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

MARKET_CAP: Endpoint = Endpoint(
    name="market_cap",
    path="market-capitalization/{symbol}",
    version=APIVersion.V3,
    description="Get market capitalization data",
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
    response_model=MarketCapitalization,
)

HISTORICAL_MARKET_CAP: Endpoint = Endpoint(
    name="historical_market_cap",
    path="historical-market-capitalization/{symbol}",
    version=APIVersion.V3,
    description="Get historical market capitalization data",
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
    response_model=MarketCapitalization,
)
PRICE_TARGET: Endpoint = Endpoint(
    name="price_target",
    path="price-target",
    version=APIVersion.V4,
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

PRICE_TARGET_SUMMARY: Endpoint = Endpoint(
    name="price_target_summary",
    path="price-target-summary",
    version=APIVersion.V4,
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

PRICE_TARGET_CONSENSUS: Endpoint = Endpoint(
    name="price_target_consensus",
    path="price-target-consensus",
    version=APIVersion.V4,
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
    path="analyst-estimates/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst estimates",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Stock symbol",
        )
    ],
    optional_params=[],
    response_model=AnalystEstimate,
)

ANALYST_RECOMMENDATIONS: Endpoint = Endpoint(
    name="analyst_recommendations",
    path="analyst-stock-recommendations/{symbol}",
    version=APIVersion.V3,
    url_type=URLType.API,
    method=HTTPMethod.GET,
    description="Get analyst recommendations",
    mandatory_params=[
        EndpointParam(
            name="symbol",
            location=ParamLocation.PATH,
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
    version=APIVersion.V4,
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

UPGRADES_DOWNGRADES_CONSENSUS: Endpoint = Endpoint(
    name="upgrades_downgrades_consensus",
    path="upgrades-downgrades-consensus",
    version=APIVersion.V4,
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
