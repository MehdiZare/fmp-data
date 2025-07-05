# fmp_data/company/mapping.py
from __future__ import annotations

from fmp_data.company.endpoints import (
    ANALYST_ESTIMATES,
    ANALYST_RECOMMENDATIONS,
    COMPANY_LOGO,
    COMPANY_NOTES,
    CORE_INFORMATION,
    EMPLOYEE_COUNT,
    EXECUTIVE_COMPENSATION,
    GEOGRAPHIC_REVENUE_SEGMENTATION,
    HISTORICAL_MARKET_CAP,
    HISTORICAL_PRICE,
    HISTORICAL_SHARE_FLOAT,
    INTRADAY_PRICE,
    KEY_EXECUTIVES,
    MARKET_CAP,
    PRICE_TARGET,
    PRICE_TARGET_CONSENSUS,
    PRICE_TARGET_SUMMARY,
    PRODUCT_REVENUE_SEGMENTATION,
    PROFILE,
    QUOTE,
    SHARE_FLOAT,
    SIMPLE_QUOTE,
    SYMBOL_CHANGES,
    UPGRADES_DOWNGRADES,
    UPGRADES_DOWNGRADES_CONSENSUS,
)
from fmp_data.company.hints import (
    FLOAT_RESPONSE_HINTS,
    INTERVAL_HINT,
    PROFILE_RESPONSE_HINTS,
    STRUCTURE_HINT,
)
from fmp_data.lc.hints import DATE_HINTS, PERIOD_HINT, SYMBOL_HINT
from fmp_data.lc.models import EndpointSemantics, ResponseFieldInfo, SemanticCategory

# Company endpoints mapping
COMPANY_ENDPOINT_MAP = {
    # Price Target endpoints
    "get_price_target": PRICE_TARGET,
    "get_price_target_summary": PRICE_TARGET_SUMMARY,
    "get_price_target_consensus": PRICE_TARGET_CONSENSUS,
    # Analyst endpoints
    "get_analyst_estimates": ANALYST_ESTIMATES,
    "get_analyst_recommendations": ANALYST_RECOMMENDATIONS,
    "get_upgrades_downgrades": UPGRADES_DOWNGRADES,
    "get_upgrades_downgrades_consensus": UPGRADES_DOWNGRADES_CONSENSUS,
    "get_quote": QUOTE,
    "get_simple_quote": SIMPLE_QUOTE,
    "get_historical_prices": HISTORICAL_PRICE,
    "get_intraday_prices": INTRADAY_PRICE,
    "get_market_cap": MARKET_CAP,
    "get_historical_market_cap": HISTORICAL_MARKET_CAP,
    "get_share_float": SHARE_FLOAT,
    "get_profile": PROFILE,
    "get_core_information": CORE_INFORMATION,
    "get_executives": KEY_EXECUTIVES,
    "get_company_notes": COMPANY_NOTES,
    "get_employee_count": EMPLOYEE_COUNT,
    "get_company_logo_url": COMPANY_LOGO,
    "get_executive_compensation": EXECUTIVE_COMPENSATION,
    "get_historical_share_float": HISTORICAL_SHARE_FLOAT,
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
    "quote": EndpointSemantics(
        client_name="market",
        method_name="get_quote",
        natural_description=(
            "Get real-time stock quote data including current price, "
            "volume, day range, and other key market metrics"
        ),
        example_queries=[
            "What's the current price of AAPL?",
            "Get me a quote for MSFT",
            "Show GOOGL's market data",
            "What's TSLA trading at?",
            "Get current market data for AMZN",
        ],
        related_terms=[
            "stock price",
            "market price",
            "trading price",
            "quote",
            "market data",
            "stock quote",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Real-time Quotes",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current stock price",
                examples=["150.25", "3500.95"],
                related_terms=["price", "current price", "trading price"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["1000000", "500000"],
                related_terms=["volume", "shares traded", "trading volume"],
            ),
            "change_percentage": ResponseFieldInfo(
                description="Price change percentage",
                examples=["2.5", "-1.8"],
                related_terms=["change", "percent change", "movement"],
            ),
        },
        use_cases=[
            "Real-time price monitoring",
            "Trading decisions",
            "Portfolio tracking",
            "Market analysis",
            "Price change monitoring",
        ],
    ),
    "simple_quote": EndpointSemantics(
        client_name="market",
        method_name="get_simple_quote",
        natural_description=(
            "Get real-time basic stock quote "
            "including price, volume, and change information"
        ),
        example_queries=[
            "Get current price for AAPL",
            "Show Microsoft stock quote",
            "What's Tesla trading at?",
            "Get Google stock price",
            "Show Amazon quote",
        ],
        related_terms=[
            "stock quote",
            "current price",
            "trading price",
            "market price",
            "live quote",
            "real-time price",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Real-time Quotes",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current stock price",
                examples=["150.25", "3200.50"],
                related_terms=["current price", "trading price", "market price"],
            ),
            "change": ResponseFieldInfo(
                description="Price change",
                examples=["+2.50", "-1.75"],
                related_terms=["price change", "change amount", "price movement"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["1.2M", "500K"],
                related_terms=["volume", "shares traded", "trading volume"],
            ),
        },
        use_cases=[
            "Real-time price monitoring",
            "Basic stock tracking",
            "Quick price checks",
            "Portfolio monitoring",
        ],
    ),
    "intraday_prices": EndpointSemantics(
        client_name="market",
        method_name="get_intraday_prices",
        natural_description=(
            "Get intraday price data with minute-by-minute or hourly intervals"
        ),
        example_queries=[
            "Get AAPL intraday prices",
            "Show Microsoft today's price movement",
            "Tesla intraday data",
            "Get Google price by minute",
            "Show Amazon today's trading",
        ],
        related_terms=[
            "intraday",
            "minute data",
            "day trading",
            "price movement",
            "daily chart",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Intraday Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "interval": INTERVAL_HINT,
        },
        response_hints={
            "datetime": ResponseFieldInfo(
                description="Exact time of the price",
                examples=["2024-01-15 10:30:00", "2024-01-15 15:45:00"],
                related_terms=["timestamp", "time", "minute"],
            ),
            "price": ResponseFieldInfo(
                description="Price at that time",
                examples=["150.25", "3200.50"],
                related_terms=["price", "trade price", "current"],
            ),
        },
        use_cases=[
            "Day trading",
            "Intraday analysis",
            "Price monitoring",
            "Short-term trading",
        ],
    ),
    "historical_price": EndpointSemantics(
        client_name="market",
        method_name="get_historical_prices",
        natural_description=(
            "Retrieve historical daily price data including open, high, low, close, "
            "and adjusted prices with volume information ."
        ),
        example_queries=[
            "Get AAPL's historical prices",
            "Show price history for MSFT",
            "Get GOOGL prices from last month",
            "Historical data for TSLA",
            "Show AMZN's past performance",
            "Get price history between dates",
        ],
        related_terms=[
            "price history",
            "historical data",
            "past prices",
            "historical performance",
            "price chart data",
            "ohlc data",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Historical Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["date", "trading day", "session date"],
            ),
            "open": ResponseFieldInfo(
                description="Opening price",
                examples=["150.25", "3500.95"],
                related_terms=["open price", "opening", "open"],
            ),
            "high": ResponseFieldInfo(
                description="High price",
                examples=["152.50", "3550.00"],
                related_terms=["high", "day high", "session high"],
            ),
            "low": ResponseFieldInfo(
                description="Low price",
                examples=["148.75", "3475.50"],
                related_terms=["low", "day low", "session low"],
            ),
            "close": ResponseFieldInfo(
                description="Closing price",
                examples=["151.00", "3525.75"],
                related_terms=["close", "closing price", "final price"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["1000000", "500000"],
                related_terms=["volume", "shares traded", "daily volume"],
            ),
        },
        use_cases=[
            "Technical analysis",
            "Historical performance analysis",
            "Backtesting trading strategies",
            "Price trend analysis",
            "Volatility analysis",
            "Volume analysis",
        ],
    ),
    "intraday_price": EndpointSemantics(
        client_name="market",
        method_name="get_intraday_prices",
        natural_description=(
            "Get intraday price data at various intervals (1min to 4hour) "
            "for detailed analysis of price movements within the trading day"
        ),
        example_queries=[
            "Get 1-minute data for AAPL",
            "Show MSFT's intraday prices",
            "Get 5-minute bars for GOOGL",
            "Intraday chart data for TSLA",
            "Get hourly prices for AMZN",
        ],
        related_terms=[
            "intraday data",
            "minute bars",
            "tick data",
            "time and sales",
            "price ticks",
            "intraday chart",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Intraday Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "interval": INTERVAL_HINT,
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Timestamp of the price data",
                examples=["2024-01-15 14:30:00", "2024-01-15 14:31:00"],
                related_terms=["time", "timestamp", "datetime"],
            ),
            "price": ResponseFieldInfo(
                description="Price at the given time",
                examples=["150.25", "150.30"],
                related_terms=["price", "tick price", "trade price"],
            ),
            "volume": ResponseFieldInfo(
                description="Volume for the interval",
                examples=["1000", "500"],
                related_terms=["interval volume", "tick volume"],
            ),
        },
        use_cases=[
            "Day trading analysis",
            "High-frequency trading",
            "Price momentum analysis",
            "Real-time market monitoring",
            "Short-term trading strategies",
            "Volume profile analysis",
        ],
    ),
    "market_cap": EndpointSemantics(
        client_name="market",
        method_name="get_market_cap",
        natural_description=(
            "Get current market capitalization data for a company, including "
            "total market value and related metrics"
        ),
        example_queries=[
            "What's AAPL's market cap?",
            "Get market value for MSFT",
            "Show GOOGL market capitalization",
            "How much is TSLA worth?",
            "Get AMZN's market value",
        ],
        related_terms=[
            "market capitalization",
            "company value",
            "market value",
            "company size",
            "equity value",
            "company worth",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Company Valuation",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "market_cap": ResponseFieldInfo(
                description="Total market capitalization",
                examples=["2000000000000", "1500000000000"],
                related_terms=["market value", "capitalization", "company value"],
            ),
        },
        use_cases=[
            "Company valuation analysis",
            "Market size comparison",
            "Index inclusion analysis",
            "Investment screening",
            "Portfolio weighting",
        ],
    ),
    "historical_market_cap": EndpointSemantics(
        client_name="market",
        method_name="get_historical_market_cap",
        natural_description=(
            "Retrieve historical market capitalization data to track changes in "
            "company value over time"
        ),
        example_queries=[
            "Show AAPL's historical market cap",
            "Get MSFT's past market value",
            "Historical size of GOOGL",
            "Track TSLA's market cap",
            "AMZN market cap history",
        ],
        related_terms=[
            "historical capitalization",
            "market value history",
            "size history",
            "historical worth",
            "past market cap",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Historical Valuation",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "date": ResponseFieldInfo(
                description="Date of the market cap value",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["valuation date", "as of date"],
            ),
            "market_cap": ResponseFieldInfo(
                description="Market capitalization value",
                examples=["2000000000000", "1500000000000"],
                related_terms=["market value", "company value", "worth"],
            ),
        },
        use_cases=[
            "Growth analysis",
            "Valuation trends",
            "Size evolution tracking",
            "Historical comparison",
            "Market impact analysis",
        ],
    ),
    "historical_prices": EndpointSemantics(
        client_name="market",
        method_name="get_historical_prices",
        natural_description=(
            "Retrieve historical price data including OHLCV (Open, High, Low, Close, "
            "Volume) information for detailed technical and performance analysis."
        ),
        example_queries=[
            "Get AAPL historical prices",
            "Show MSFT price history from 2023-01-01 to 2023-12-31",
            "Get GOOGL historical data between dates",
            "TSLA price history last year",
            "Show AMZN trading history",
        ],
        related_terms=[
            "price history",
            "historical data",
            "past prices",
            "trading history",
            "historical performance",
            "price chart data",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Historical Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["date", "trading day", "session date"],
            ),
            "open": ResponseFieldInfo(
                description="Opening price",
                examples=["150.25", "3500.95"],
                related_terms=["open price", "opening", "open"],
            ),
            "close": ResponseFieldInfo(
                description="Closing price",
                examples=["151.00", "3525.75"],
                related_terms=["close price", "closing", "final price"],
            ),
        },
        use_cases=[
            "Technical analysis",
            "Performance tracking",
            "Backtesting",
            "Trend analysis",
            "Historical research",
        ],
    ),
    "price_target": EndpointSemantics(
        client_name="company",
        method_name="get_price_target",
        natural_description=(
            "Retrieve analyst price targets "
            "for a specific stock, including target prices, "
            "analyst details, and publication dates"
        ),
        example_queries=[
            "Get AAPL price targets",
            "Show analyst targets for TSLA",
            "What's the price target for MSFT?",
            "Latest analyst price predictions",
        ],
        related_terms=[
            "analyst target",
            "price prediction",
            "stock valuation",
            "analyst forecast",
            "price estimate",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Research",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "price_target": ResponseFieldInfo(
                description="Target price set by analyst",
                examples=["150.00", "3500.00"],
                related_terms=["target", "prediction", "forecast"],
            ),
            "analyst_name": ResponseFieldInfo(
                description="Name of the analyst",
                examples=["John Smith", "Jane Doe"],
                related_terms=["analyst", "researcher"],
            ),
        },
        use_cases=[
            "Investment research",
            "Stock analysis",
            "Valuation comparison",
            "Market sentiment analysis",
        ],
    ),
    "analyst_estimates": EndpointSemantics(
        client_name="company",
        method_name="get_analyst_estimates",
        natural_description=(
            "Retrieve detailed analyst "
            "estimates including revenue, earnings, EBITDA, "
            "and other financial metrics "
            "forecasts with high/low/average ranges"
        ),
        example_queries=[
            "Get analyst estimates for AAPL",
            "Show revenue estimates for MSFT",
            "What are the earnings forecasts for GOOGL?",
            "Get quarterly estimates for TSLA",
        ],
        related_terms=[
            "earnings estimates",
            "revenue forecasts",
            "financial projections",
            "analyst forecasts",
            "EBITDA estimates",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Research",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "estimated_revenue_avg": ResponseFieldInfo(
                description="Average estimated revenue",
                examples=["350.5B", "42.1B"],
                related_terms=["revenue forecast", "sales estimate"],
            ),
            "estimated_eps_avg": ResponseFieldInfo(
                description="Average estimated earnings per share",
                examples=["3.45", "1.82"],
                related_terms=["EPS estimate", "earnings forecast"],
            ),
        },
        use_cases=[
            "Financial forecasting",
            "Investment research",
            "Earnings analysis",
            "Revenue projections",
        ],
    ),
    "upgrades_downgrades": EndpointSemantics(
        client_name="company",
        method_name="get_upgrades_downgrades",
        natural_description=(
            "Access stock rating changes including upgrades, downgrades, and "
            "rating adjustments with analyst and firm information"
        ),
        example_queries=[
            "Show recent upgrades for AAPL",
            "Get analyst rating changes for MSFT",
            "Display GOOGL rating changes",
            "Recent stock downgrades",
        ],
        related_terms=[
            "rating changes",
            "analyst ratings",
            "stock upgrades",
            "stock downgrades",
            "recommendation changes",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Research",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "new_grade": ResponseFieldInfo(
                description="New rating assigned by analyst",
                examples=["Buy", "Hold", "Sell"],
                related_terms=["rating", "recommendation", "grade"],
            ),
            "previous_grade": ResponseFieldInfo(
                description="Previous rating before change",
                examples=["Hold", "Buy", "Neutral"],
                related_terms=["old rating", "prior grade"],
            ),
        },
        use_cases=[
            "Rating change tracking",
            "Sentiment analysis",
            "Investment decisions",
            "Market monitoring",
        ],
    ),
    "upgrades_downgrades_consensus": EndpointSemantics(
        client_name="company",
        method_name="get_upgrades_downgrades_consensus",
        natural_description=(
            "Get aggregated rating consensus data including buy/sell/hold counts "
            "and overall recommendation trends"
        ),
        example_queries=[
            "Get rating consensus for AAPL",
            "Show analyst consensus for MSFT",
            "What's the rating breakdown for GOOGL?",
            "Display recommendation summary",
        ],
        related_terms=[
            "rating consensus",
            "analyst agreement",
            "recommendation summary",
            "rating breakdown",
            "consensus view",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Research",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "consensus": ResponseFieldInfo(
                description="Overall consensus rating",
                examples=["Buy", "Overweight", "Hold"],
                related_terms=["overall rating", "consensus grade"],
            ),
            "strong_buy": ResponseFieldInfo(
                description="Number of strong buy ratings",
                examples=["12", "8"],
                related_terms=["buy count", "positive ratings"],
            ),
        },
        use_cases=[
            "Consensus analysis",
            "Rating trends",
            "Market sentiment",
            "Investment research",
        ],
    ),
    "price_target_consensus": EndpointSemantics(
        client_name="company",
        method_name="get_price_target_consensus",
        natural_description=(
            "Get detailed consensus information about analyst price targets, "
            "including target distribution, recent changes, and analyst "
            "recommendations."
        ),
        example_queries=[
            "What's the analyst consensus on AAPL?",
            "Show MSFT target price consensus",
            "Get analyst agreement on GOOGL price",
            "Consensus target for TSLA",
            "What's the market expecting for AMZN?",
            "Show analyst consensus for Netflix",
        ],
        related_terms=[
            "price consensus",
            "analyst agreement",
            "target consensus",
            "market expectation",
            "price agreement",
            "collective forecast",
            "analyst consensus",
            "price outlook",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Coverage",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "consensus_price": ResponseFieldInfo(
                description="Consensus price target",
                examples=["185.50", "3750.00"],
                related_terms=["consensus target", "agreed target", "mean target"],
            ),
            "consensus_growth": ResponseFieldInfo(
                description="Expected price growth percentage",
                examples=["15.5%", "22.3%"],
                related_terms=["target growth", "expected return", "price potential"],
            ),
            "analyst_count": ResponseFieldInfo(
                description="Number of analysts in consensus",
                examples=["25", "32"],
                related_terms=["analyst coverage", "following analysts", "coverage"],
            ),
            "recommendation": ResponseFieldInfo(
                description="Overall analyst recommendation",
                examples=["Buy", "Hold", "Sell"],
                related_terms=["rating", "analyst rating", "recommendation"],
            ),
        },
        use_cases=[
            "Investment research",
            "Market sentiment analysis",
            "Price target tracking",
            "Analyst coverage monitoring",
            "Investment decision support",
            "Portfolio strategy planning",
            "Risk assessment",
        ],
    ),
    "price_target_summary": EndpointSemantics(
        client_name="company",
        method_name="get_price_target_summary",
        natural_description=(
            "Get a summary of analyst price targets for a stock, including average, "
            "highest, and lowest targets along with number of analysts."
        ),
        example_queries=[
            "What's the average price target for AAPL?",
            "Show analyst price targets for MSFT",
            "Get price target range for GOOGL",
            "What do analysts expect for TSLA stock?",
            "Show target price summary for AMZN",
            "Analyst predictions for Netflix stock",
        ],
        related_terms=[
            "analyst target",
            "price forecast",
            "stock target",
            "price prediction",
            "analyst estimate",
            "price expectation",
            "stock valuation",
            "price consensus",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Coverage",
        parameter_hints={
            "symbol": SYMBOL_HINT,
        },
        response_hints={
            "target_consensus": ResponseFieldInfo(
                description="Average analyst price target",
                examples=["185.50", "3750.00"],
                related_terms=["consensus target", "average target", "mean target"],
            ),
            "target_high": ResponseFieldInfo(
                description="Highest analyst price target",
                examples=["200.00", "4000.00"],
                related_terms=["highest target", "maximum target", "bull case"],
            ),
            "target_low": ResponseFieldInfo(
                description="Lowest analyst price target",
                examples=["160.00", "3200.00"],
                related_terms=["lowest target", "minimum target", "bear case"],
            ),
            "number_of_analysts": ResponseFieldInfo(
                description="Number of analysts providing targets",
                examples=["25", "32"],
                related_terms=["analyst count", "coverage", "analysts following"],
            ),
        },
        use_cases=[
            "Investment research",
            "Price potential analysis",
            "Market sentiment assessment",
            "Target price monitoring",
            "Analyst coverage tracking",
            "Investment decision making",
            "Portfolio management",
        ],
    ),
    "analyst_recommendations": EndpointSemantics(
        client_name="company",
        method_name="get_analyst_recommendations",
        natural_description=(
            "Retrieve analyst buy/sell/hold recommendations and consensus ratings "
            "for stocks including detailed rating breakdowns"
        ),
        example_queries=[
            "Get analyst recommendations for AAPL",
            "Show buy/sell ratings for TSLA",
            "What do analysts recommend for MSFT?",
            "Get stock recommendations",
        ],
        related_terms=[
            "buy rating",
            "sell rating",
            "hold rating",
            "analyst consensus",
            "stock recommendation",
        ],
        category=SemanticCategory.COMPANY_INFO,
        sub_category="Analyst Research",
        parameter_hints={"symbol": SYMBOL_HINT},
        response_hints={
            "analyst_ratings_buy": ResponseFieldInfo(
                description="Number of buy ratings",
                examples=["25", "12"],
                related_terms=["buy ratings", "positive ratings"],
            ),
            "analyst_ratings_sell": ResponseFieldInfo(
                description="Number of sell ratings",
                examples=["5", "2"],
                related_terms=["sell ratings", "negative ratings"],
            ),
        },
        use_cases=[
            "Investment decisions",
            "Consensus analysis",
            "Rating tracking",
            "Market sentiment",
        ],
    ),
}
