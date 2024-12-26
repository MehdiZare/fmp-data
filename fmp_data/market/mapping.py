# fmp_data/market/mapping.py

from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)
from fmp_data.market.endpoints import (
    GAINERS,
    HISTORICAL_MARKET_CAP,
    HISTORICAL_PRICE,
    INTRADAY_PRICE,
    LOSERS,
    MARKET_CAP,
    MARKET_HOURS,
    MOST_ACTIVE,
    PRE_POST_MARKET,
    QUOTE,
    SECTOR_PERFORMANCE,
    SIMPLE_QUOTE,
)
from fmp_data.market.schema import TimeInterval

MARKET_ENDPOINT_MAP = {
    "get_quote": QUOTE,
    "get_simple_quote": SIMPLE_QUOTE,
    "get_historical_prices": HISTORICAL_PRICE,
    "get_intraday_prices": INTRADAY_PRICE,
    "get_market_hours": MARKET_HOURS,
    "get_market_cap": MARKET_CAP,
    "get_historical_market_cap": HISTORICAL_MARKET_CAP,
    "get_gainers": GAINERS,
    "get_losers": LOSERS,
    "get_most_active": MOST_ACTIVE,
    "get_sector_performance": SECTOR_PERFORMANCE,
    "get_pre_post_market": PRE_POST_MARKET,
}
# Common parameter hints
SYMBOL_HINT = ParameterHint(
    natural_names=["symbol", "ticker", "stock", "security"],
    extraction_patterns=[
        r"(?i)for\s+([A-Z]{1,5})",
        r"(?i)([A-Z]{1,5})(?:'s|'|\s+)",
        r"\b[A-Z]{1,5}\b",
    ],
    examples=["AAPL", "MSFT", "GOOGL"],
    context_clues=["stock", "symbol", "ticker", "company"],
)

DATE_HINT = ParameterHint(
    natural_names=["date", "as of", "trading date"],
    extraction_patterns=[
        r"(\d{4}-\d{2}-\d{2})",
        r"(?:on|at|for)\s+(\d{4}-\d{2}-\d{2})",
    ],
    examples=["2024-01-15", "2023-12-31"],
    context_clues=["date", "as of", "trading day", "on"],
)

INTERVAL_HINT = ParameterHint(
    natural_names=["interval", "timeframe", "period"],
    extraction_patterns=[
        r"(?i)(\d+)\s*(?:min|minute|hour|hr)",
        r"(?i)(one|five|fifteen|thirty)\s*(?:min|minute|hour|hr)",
    ],
    examples=list(TimeInterval),
    context_clues=["interval", "timeframe", "period", "frequency"],
)

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
        category=SemanticCategory.MARKET_DATA,
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
        category=SemanticCategory.MARKET_DATA,
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
    "historical_prices": EndpointSemantics(
        client_name="market",
        method_name="get_historical_prices",
        natural_description=(
            "Retrieve historical price data "
            "including OHLCV (Open, High, Low, Close, Volume) information"
        ),
        example_queries=[
            "Get AAPL historical prices",
            "Show Microsoft price history",
            "Tesla stock price history",
            "Get Google historical data",
            "Show Amazon price chart data",
        ],
        related_terms=[
            "price history",
            "historical data",
            "OHLCV",
            "price chart",
            "historical quotes",
            "past prices",
        ],
        category=SemanticCategory.MARKET_DATA,
        sub_category="Historical Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "from_date": DATE_HINT,
            "to_date": DATE_HINT,
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2024-01-15", "2023-12-31"],
                related_terms=["date", "trading day", "session date"],
            ),
            "open": ResponseFieldInfo(
                description="Opening price",
                examples=["150.25", "3200.50"],
                related_terms=["open price", "opening", "open"],
            ),
            "close": ResponseFieldInfo(
                description="Closing price",
                examples=["151.75", "3225.25"],
                related_terms=["close price", "closing", "close"],
            ),
        },
        use_cases=[
            "Technical analysis",
            "Historical analysis",
            "Price trend analysis",
            "Chart creation",
        ],
    ),
    "intraday_prices": EndpointSemantics(
        client_name="market",
        method_name="get_intraday_prices",
        natural_description=(
            "Get intraday price data with " "minute-by-minute or hourly intervals"
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
        category=SemanticCategory.MARKET_DATA,
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
            "and adjusted prices with volume information for technical analysis "
            "and historical performance tracking"
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
        category=SemanticCategory.MARKET_DATA,
        sub_category="Historical Data",
        parameter_hints={
            "symbol": SYMBOL_HINT,
            "from": DATE_HINT,
            "to": DATE_HINT,
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
        category=SemanticCategory.MARKET_DATA,
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
        category=SemanticCategory.MARKET_DATA,
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
        category=SemanticCategory.MARKET_DATA,
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
}
