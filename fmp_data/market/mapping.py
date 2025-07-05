# fmp_data/market/mapping.py

from fmp_data.lc.hints import EXCHANGE_HINT, LIMIT_HINT
from fmp_data.lc.models import EndpointSemantics, ResponseFieldInfo, SemanticCategory
from fmp_data.market.endpoints import (
    ALL_SHARES_FLOAT,
    AVAILABLE_INDEXES,
    CIK_SEARCH,
    CUSIP_SEARCH,
    ETF_LIST,
    EXCHANGE_SYMBOLS,
    GAINERS,
    ISIN_SEARCH,
    LOSERS,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    SEARCH,
    SECTOR_PERFORMANCE,
    STOCK_LIST,
)

from .hints import COMPANY_SEARCH_HINT, IDENTIFIER_HINT

MARKET_ENDPOINT_MAP = {
    "search": SEARCH,
    "get_all_shares_float": ALL_SHARES_FLOAT,
    "get_market_hours": MARKET_HOURS,
    "get_gainers": GAINERS,
    "get_losers": LOSERS,
    "get_most_active": MOST_ACTIVE,
    "get_sector_performance": SECTOR_PERFORMANCE,
    "get_pre_post_market": PRE_POST_MARKET,
    "get_stock_list": STOCK_LIST,
    "get_etf_list": ETF_LIST,
    "get_available_indexes": AVAILABLE_INDEXES,
    "get_exchange_symbols": EXCHANGE_SYMBOLS,
    "search_by_cik": CIK_SEARCH,
    "search_by_cusip": CUSIP_SEARCH,
    "search_by_isin": ISIN_SEARCH,
}
# Common parameter hints


MARKET_SESSIONS = {
    "regular": {
        "patterns": [
            r"(?i)regular\s+(?:session|hours|trading)",
            r"(?i)normal\s+(?:session|hours|trading)",
            r"(?i)market\s+hours",
        ],
        "terms": ["regular session", "market hours", "normal trading"],
    },
    "pre_market": {
        "patterns": [
            r"(?i)pre[-\s]market",
            r"(?i)before\s+(?:market|trading)",
            r"(?i)early\s+trading",
        ],
        "terms": ["pre-market", "before hours", "early trading"],
    },
    "post_market": {
        "patterns": [
            r"(?i)(?:post|after)[-\s](?:market|hours)",
            r"(?i)extended\s+(?:trading|hours)",
            r"(?i)late\s+trading",
        ],
        "terms": ["after-hours", "post-market", "extended hours"],
    },
}

PRICE_MOVEMENTS = {
    "up": {
        "patterns": [
            r"(?i)up|higher|gaining|advancing|rising",
            r"(?i)positive|increased|grew",
        ],
        "terms": ["gainers", "advancing", "up", "higher", "positive"],
    },
    "down": {
        "patterns": [
            r"(?i)down|lower|losing|declining|falling",
            r"(?i)negative|decreased|dropped",
        ],
        "terms": ["losers", "declining", "down", "lower", "negative"],
    },
    "unchanged": {
        "patterns": [
            r"(?i)unchanged|flat|steady|stable",
            r"(?i)no\s+change",
        ],
        "terms": ["unchanged", "flat", "steady", "stable"],
    },
}

SIGNIFICANCE_LEVELS = {
    "high_activity": {
        "patterns": [
            r"(?i)most\s+active|highest\s+volume",
            r"(?i)heavily\s+traded|busy",
        ],
        "terms": ["most active", "high volume", "heavy trading"],
    },
    "unusual_activity": {
        "patterns": [
            r"(?i)unusual|abnormal|exceptional",
            r"(?i)irregular|unexpected",
        ],
        "terms": ["unusual", "abnormal", "irregular"],
    },
}

PRICE_METRICS = {
    "ohlc": ["open", "high", "low", "close"],
    "derived": ["vwap", "twap", "moving_average"],
    "adjusted": ["split_adjusted", "dividend_adjusted"],
}

VOLUME_METRICS = {
    "basic": ["volume", "trades", "turnover"],
    "advanced": ["vwap_volume", "block_trades", "dark_pool"],
}

TECHNICAL_INDICATORS = {
    "momentum": ["rsi", "macd", "momentum"],
    "trend": ["moving_average", "trend_line"],
    "volatility": ["atr", "bollinger_bands"],
}
MARKET_COMMON_TERMS = {
    "price": [
        "quote",
        "value",
        "trading price",
        "market price",
        "stock price",
    ],
    "volume": [
        "shares traded",
        "trading volume",
        "market volume",
        "activity",
    ],
    "market_cap": [
        "market capitalization",
        "company value",
        "market value",
        "size",
    ],
}
MARKET_TIME_PERIODS = {
    "intraday": {
        "patterns": [
            r"(?i)intraday",
            r"(?i)during the day",
            r"(?i)today's trading",
        ],
        "terms": ["intraday", "today", "current session"],
    },
    "daily": {
        "patterns": [
            r"(?i)daily",
            r"(?i)day by day",
            r"(?i)each day",
        ],
        "terms": ["daily", "per day", "day"],
    },
}

# Complete semantic definitions
MARKET_ENDPOINTS_SEMANTICS = {
    "search": EndpointSemantics(
        client_name="market",
        method_name="search",
        natural_description=(
            "Search for companies by name, ticker, or other identifiers."
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
        category=SemanticCategory.MARKET_DATA,
        sub_category="Search",
        parameter_hints={
            "query": COMPANY_SEARCH_HINT,
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
    "exchange_symbols": EndpointSemantics(
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
        client_name="market",
        method_name="search_by_cik",  # Match exact method name
        natural_description=(
            "Search for companies by their SEC Central Index Key (CIK) number"
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
        category=SemanticCategory.MARKET_DATA,
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
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
    "all_shares_float": EndpointSemantics(
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
    "etf_list": EndpointSemantics(
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
        client_name="market",
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
        category=SemanticCategory.MARKET_DATA,
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
    "market_hours": EndpointSemantics(
        client_name="market",
        method_name="get_market_hours",
        natural_description=(
            "Check current market status and trading hours including regular session "
            "times and holiday schedules for major markets"
        ),
        example_queries=[
            "Is the market open?",
            "Show trading hours",
            "When does the market close?",
            "Get market schedule",
            "Check holiday schedule",
        ],
        related_terms=[
            "trading hours",
            "market schedule",
            "trading schedule",
            "market status",
            "exchange hours",
            "holiday calendar",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Market Status",
        parameter_hints={},  # No parameters needed
        response_hints={
            "isTheStockMarketOpen": ResponseFieldInfo(
                description="Whether the stock market is currently open",
                examples=["true", "false"],
                related_terms=["market status", "trading status"],
            ),
            "stockMarketHours": ResponseFieldInfo(
                description="Regular trading hours",
                examples=["9:30-16:00", "8:00-17:00"],
                related_terms=["trading hours", "session hours"],
            ),
        },
        use_cases=[
            "Trading schedule planning",
            "Market status monitoring",
            "Holiday planning",
            "Trading automation",
            "Order timing",
        ],
    ),
    "gainers": EndpointSemantics(
        client_name="market",
        method_name="get_gainers",
        natural_description=(
            "Get list of top gaining stocks by percentage change, showing the best "
            "performing stocks in the current trading session"
        ),
        example_queries=[
            "Show top gainers",
            "What stocks are up the most?",
            "Best performing stocks today",
            "Show biggest stock gains",
            "Top market movers up",
        ],
        related_terms=[
            "top gainers",
            "best performers",
            "biggest gains",
            "market movers",
            "upward movers",
            "winning stocks",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Market Movers",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "company symbol"],
            ),
            "change_percentage": ResponseFieldInfo(
                description="Percentage gain",
                examples=["5.25", "10.50"],
                related_terms=["percent gain", "increase percentage"],
            ),
        },
        use_cases=[
            "Momentum trading",
            "Market sentiment analysis",
            "Opportunity identification",
            "Sector strength analysis",
            "News impact tracking",
        ],
    ),
    "losers": EndpointSemantics(
        client_name="market",
        method_name="get_losers",
        natural_description=(
            "Get list of top losing stocks by percentage change, showing the worst "
            "performing stocks in the current trading session"
        ),
        example_queries=[
            "Show top losers",
            "What stocks are down the most?",
            "Worst performing stocks today",
            "Show biggest stock losses",
            "Top market movers down",
        ],
        related_terms=[
            "top losers",
            "worst performers",
            "biggest losses",
            "declining stocks",
            "downward movers",
            "falling stocks",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Market Movers",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "company symbol"],
            ),
            "change_percentage": ResponseFieldInfo(
                description="Percentage loss",
                examples=["-5.25", "-10.50"],
                related_terms=["percent loss", "decrease percentage"],
            ),
        },
        use_cases=[
            "Risk assessment",
            "Market sentiment analysis",
            "Short selling opportunities",
            "Sector weakness analysis",
            "News impact tracking",
        ],
    ),
    "most_active": EndpointSemantics(
        client_name="market",
        method_name="get_most_active",
        natural_description=(
            "Get list of most actively traded stocks by volume, showing stocks "
            "with the highest trading activity in the current session"
        ),
        example_queries=[
            "Show most active stocks",
            "What's trading the most today?",
            "Highest volume stocks",
            "Most traded securities",
            "Show busiest stocks",
        ],
        related_terms=[
            "active stocks",
            "high volume",
            "most traded",
            "busy stocks",
            "trading activity",
            "volume leaders",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Market Activity",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "company symbol"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["10000000", "5000000"],
                related_terms=["shares traded", "activity"],
            ),
        },
        use_cases=[
            "Liquidity analysis",
            "Volume analysis",
            "Market interest tracking",
            "Trading opportunity identification",
            "Market sentiment analysis",
        ],
    ),
    "sector_performance": EndpointSemantics(
        client_name="market",
        method_name="get_sector_performance",
        natural_description=(
            "Get performance data for major market sectors, showing relative "
            "strength and weakness across different areas of the market"
        ),
        example_queries=[
            "How are sectors performing?",
            "Show sector performance",
            "Which sectors are up today?",
            "Best performing sectors",
            "Sector movement summary",
        ],
        related_terms=[
            "sector returns",
            "industry performance",
            "sector movement",
            "market sectors",
            "sector gains",
            "industry returns",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Sector Analysis",
        parameter_hints={},  # No parameters needed
        response_hints={
            "sector": ResponseFieldInfo(
                description="Sector name",
                examples=["Technology", "Healthcare"],
                related_terms=["industry", "market sector"],
            ),
            "change_percentage": ResponseFieldInfo(
                description="Sector performance",
                examples=["2.5", "-1.8"],
                related_terms=["sector return", "performance"],
            ),
        },
        use_cases=[
            "Sector rotation analysis",
            "Market trend analysis",
            "Portfolio sector allocation",
            "Relative strength analysis",
            "Market breadth analysis",
        ],
    ),
    "pre_post_market": EndpointSemantics(
        client_name="market",
        method_name="get_pre_post_market",
        natural_description=(
            "Retrieve pre-market and post-market trading data including prices, "
            "volume, and trading session information outside regular market hours"
        ),
        example_queries=[
            "Show pre-market trading",
            "Get after-hours prices",
            "What's trading pre-market?",
            "Post-market activity",
            "Extended hours trading data",
            "Show early trading activity",
        ],
        related_terms=[
            "pre-market",
            "after-hours",
            "extended hours",
            "early trading",
            "late trading",
            "off-hours trading",
            "extended session",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Extended Hours Trading",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock symbol",
                examples=["AAPL", "MSFT"],
                related_terms=["ticker", "company symbol"],
            ),
            "timestamp": ResponseFieldInfo(
                description="Time of the quote",
                examples=["2024-01-15 08:00:00", "2024-01-15 16:30:00"],
                related_terms=["time", "quote time", "trading time"],
            ),
            "price": ResponseFieldInfo(
                description="Trading price",
                examples=["150.25", "151.50"],
                related_terms=["quote", "trading price", "current price"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["50000", "25000"],
                related_terms=["shares traded", "activity"],
            ),
            "session": ResponseFieldInfo(
                description="Trading session identifier",
                examples=["pre", "post"],
                related_terms=["market session", "trading period"],
            ),
        },
        use_cases=[
            "Extended hours trading",
            "News impact analysis",
            "Global market impact monitoring",
            "Early market direction indicators",
            "After-hours movement tracking",
            "Pre-market momentum analysis",
        ],
    ),
    "stock_list": EndpointSemantics(
        client_name="market",
        method_name="get_stock_list",
        natural_description=(
            "Get a complete list of all available stocks in the market including their "
            "basic information such as symbol, name, and exchange listing"
        ),
        example_queries=[
            "List all available stocks",
            "Show me all tradable stocks",
            "Get complete stock list",
            "What stocks can I trade?",
            "Show all listed companies",
        ],
        related_terms=[
            "stock listings",
            "tradable securities",
            "listed stocks",
            "equity securities",
            "stock universe",
            "market listings",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Lists",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Stock trading symbol",
                examples=["AAPL", "MSFT", "GOOGL"],
                related_terms=["ticker", "trading symbol", "stock symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Company name",
                examples=["Apple Inc.", "Microsoft Corporation"],
                related_terms=["company name", "business name", "listing name"],
            ),
            "exchange": ResponseFieldInfo(
                description="Stock exchange where the stock is listed",
                examples=["NASDAQ", "NYSE"],
                related_terms=["listing exchange", "trading venue", "market"],
            ),
        },
        use_cases=[
            "Market coverage analysis",
            "Trading universe definition",
            "Portfolio screening",
            "Market research",
            "Company discovery",
        ],
    ),
}
