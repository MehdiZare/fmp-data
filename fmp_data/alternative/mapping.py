# fmp_data/alternative/mapping.py
from __future__ import annotations

from fmp_data.alternative.endpoints import (
    COMMODITIES_LIST,
    COMMODITIES_QUOTES,
    COMMODITY_HISTORICAL,
    COMMODITY_INTRADAY,
    COMMODITY_QUOTE,
    CRYPTO_HISTORICAL,
    CRYPTO_INTRADAY,
    CRYPTO_LIST,
    CRYPTO_QUOTE,
    CRYPTO_QUOTES,
    FOREX_HISTORICAL,
    FOREX_INTRADAY,
    FOREX_LIST,
    FOREX_QUOTE,
    FOREX_QUOTES,
)
from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)

# Create method name mapping
ALTERNATIVE_ENDPOINT_MAP = {
    f"get_{name}": endpoint
    for name, endpoint in {
        "crypto_list": CRYPTO_LIST,
        "crypto_quotes": CRYPTO_QUOTES,
        "crypto_quote": CRYPTO_QUOTE,
        "crypto_historical": CRYPTO_HISTORICAL,
        "crypto_intraday": CRYPTO_INTRADAY,
        "forex_list": FOREX_LIST,
        "forex_quotes": FOREX_QUOTES,
        "forex_quote": FOREX_QUOTE,
        "forex_historical": FOREX_HISTORICAL,
        "forex_intraday": FOREX_INTRADAY,
        "commodities_list": COMMODITIES_LIST,
        "commodities_quotes": COMMODITIES_QUOTES,
        "commodity_quote": COMMODITY_QUOTE,
        "commodity_historical": COMMODITY_HISTORICAL,
        "commodity_intraday": COMMODITY_INTRADAY,
    }.items()
}

# Common parameter hints
SYMBOL_HINTS = {
    "crypto": ParameterHint(
        natural_names=["cryptocurrency", "crypto", "token"],
        extraction_patterns=[
            r"\b[A-Z]{3,4}USD\b",
            r"\b(BTC|ETH|XRP|USDT)[A-Z]*",
            r"(?i)(?:for|of)\s+([A-Z]{3,})",
        ],
        examples=["BTCUSD", "ETHUSD", "XRPUSD"],
        context_clues=["bitcoin", "ethereum", "crypto", "token", "coin"],
    ),
    "forex": ParameterHint(
        natural_names=["currency pair", "forex pair", "exchange rate"],
        extraction_patterns=[
            r"([A-Z]{6})",
            r"([A-Z]{3}/[A-Z]{3})",
            r"(?i)(EUR|USD|GBP|JPY|AUD|CAD|CHF|NZD)[A-Z]{3}",
        ],
        examples=["EURUSD", "GBPJPY", "USDCAD"],
        context_clues=["currency", "forex", "fx", "exchange rate"],
    ),
    "commodity": ParameterHint(
        natural_names=["commodity", "symbol", "product"],
        extraction_patterns=[
            r"(?i)(gold|oil|silver|GC|CL|SI)",
            r"([A-Z]{2})",
        ],
        examples=["GC", "CL", "SI"],
        context_clues=["gold", "oil", "silver", "commodity", "metal", "energy"],
    ),
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

INTERVAL_HINT = ParameterHint(
    natural_names=["timeframe", "interval", "period"],
    extraction_patterns=[
        r"(\d+)\s*(?:minute|min|hour|hr)",
        r"(?:1min|5min|15min|30min|1hour|4hour)",
    ],
    examples=["1min", "5min", "1hour"],
    context_clues=["minute", "hour", "interval", "timeframe"],
)

ALTERNATIVE_ENDPOINTS_SEMANTICS = {
    # Crypto endpoints
    "crypto_list": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_list",
        natural_description=(
            "Get a list of all available cryptocurrencies and their basic information"
        ),
        example_queries=[
            "What cryptocurrencies are available?",
            "Show me the list of supported crypto pairs",
            "What crypto symbols can I look up?",
            "List available digital assets",
        ],
        related_terms=[
            "cryptocurrency",
            "crypto",
            "digital assets",
            "tokens",
            "available pairs",
            "trading pairs",
            "crypto symbols",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={},  # No parameters needed
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Trading symbol for the cryptocurrency pair",
                examples=["BTCUSD", "ETHUSD"],
                related_terms=["trading pair", "crypto symbol"],
            ),
            "name": ResponseFieldInfo(
                description="Full name of the cryptocurrency",
                examples=["Bitcoin", "Ethereum"],
                related_terms=["crypto name", "currency name"],
            ),
        },
        use_cases=[
            "Finding available cryptocurrencies to analyze",
            "Looking up crypto trading pairs",
            "Discovering supported digital assets",
        ],
    ),
    "crypto_historical": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_historical",
        natural_description="Retrieve historical price data for a cryptocurrency",
        example_queries=[
            "Get Bitcoin price history",
            "Show ETH price history for last month",
            "Historical crypto data between dates",
            "Get historical OHLCV data for cryptocurrency",
        ],
        related_terms=[
            "historical prices",
            "price history",
            "past data",
            "historical trading",
            "crypto history",
            "price trends",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={
            "symbol": SYMBOL_HINTS["crypto"],
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2023-12-20", "2024-01-15"],
                related_terms=["date", "trading date", "timestamp"],
            ),
            "price": ResponseFieldInfo(
                description="Closing price",
                examples=["45000.50", "1800.75"],
                related_terms=["close", "closing price", "settlement"],
            ),
        },
        use_cases=[
            "Historical price analysis",
            "Technical analysis",
            "Trend identification",
            "Backtesting trading strategies",
        ],
    ),
    "crypto_quotes": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_quotes",
        natural_description=(
            "Get current price quotes for all available cryptocurrencies"
        ),
        example_queries=[
            "What's the current Bitcoin price?",
            "Show me crypto prices",
            "Get cryptocurrency quotes",
            "What's the price of ETH?",
        ],
        related_terms=[
            "crypto price",
            "cryptocurrency value",
            "token price",
            "digital asset price",
            "crypto quotes",
            "current price",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={},  # No parameters needed
        response_hints={
            "price": ResponseFieldInfo(
                description="Current trading price",
                examples=["45000.50", "1800.75"],
                related_terms=["current price", "trading price", "value"],
            ),
            "change": ResponseFieldInfo(
                description="Price change from previous close",
                examples=["+1500", "-200"],
                related_terms=["price change", "movement", "difference"],
            ),
        },
        use_cases=[
            "Checking current crypto prices",
            "Monitoring cryptocurrency markets",
            "Tracking digital asset values",
        ],
    ),
    "crypto_quote": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_quote",
        natural_description=(
            "Get detailed real-time quote for a specific cryptocurrency"
        ),
        example_queries=[
            "Get current Bitcoin price",
            "Show ETHUSD quote",
            "What's the latest price for BTC?",
            "Get detailed crypto quote",
        ],
        related_terms=[
            "crypto price",
            "quote",
            "current price",
            "real-time",
            "live price",
            "market data",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={"symbol": SYMBOL_HINTS["crypto"]},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current trading price",
                examples=["45000.50", "1800.75"],
                related_terms=["price", "current price", "trading price"],
            ),
        },
        use_cases=[
            "Real-time crypto price monitoring",
            "Trading decisions",
            "Market analysis",
        ],
    ),
    "crypto_intraday": EndpointSemantics(
        client_name="alternative",
        method_name="get_crypto_intraday",
        natural_description="Get detailed intraday price data for a cryptocurrency",
        example_queries=[
            "Get minute-by-minute Bitcoin prices",
            "Show hourly ETH data",
            "Get intraday crypto prices",
            "5-minute interval BTCUSD data",
        ],
        related_terms=[
            "intraday",
            "minute data",
            "hourly data",
            "high-frequency",
            "short-term",
            "detailed prices",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Cryptocurrency",
        parameter_hints={
            "symbol": SYMBOL_HINTS["crypto"],
            "interval": INTERVAL_HINT,
        },
        response_hints={
            "datetime": ResponseFieldInfo(
                description="Price timestamp",
                examples=["2024-01-20 14:30:00"],
                related_terms=["time", "timestamp", "date"],
            ),
            "price": ResponseFieldInfo(
                description="Price at the interval",
                examples=["45000.50", "1800.75"],
                related_terms=["price", "rate", "value"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["1250", "3500"],
                related_terms=["volume", "trades", "activity"],
            ),
        },
        use_cases=[
            "Day trading analysis",
            "High-frequency trading",
            "Real-time monitoring",
            "Technical analysis",
        ],
    ),
    # Forex endpoints
    "forex_list": EndpointSemantics(
        client_name="alternative",
        method_name="get_forex_list",
        natural_description="Get a complete list of available forex currency pairs",
        example_queries=[
            "What forex pairs are available?",
            "Show available currency pairs",
            "List forex trading pairs",
            "What currencies can I trade?",
        ],
        related_terms=[
            "forex pairs",
            "currency pairs",
            "exchange rates",
            "available currencies",
            "trading pairs",
            "fx pairs",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Forex",
        parameter_hints={},
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Currency pair symbol",
                examples=["EURUSD", "GBPJPY"],
                related_terms=["pair", "forex symbol", "currency code"],
            ),
            "name": ResponseFieldInfo(
                description="Full name of the currency pair",
                examples=["Euro/US Dollar", "British Pound/Japanese Yen"],
                related_terms=["pair name", "currency name"],
            ),
        },
        use_cases=[
            "Finding available currency pairs",
            "Forex market exploration",
            "Currency trading setup",
        ],
    ),
    "forex_quotes": EndpointSemantics(
        client_name="alternative",
        method_name="get_forex_quotes",
        natural_description=(
            "Get real-time quotes for all available forex currency pairs"
        ),
        example_queries=[
            "Get all forex rates",
            "Show current exchange rates",
            "What are the current forex prices?",
            "Get all currency quotes",
        ],
        related_terms=[
            "exchange rates",
            "forex rates",
            "currency quotes",
            "fx prices",
            "current rates",
            "live quotes",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Forex",
        parameter_hints={},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current exchange rate",
                examples=["1.2150", "110.75"],
                related_terms=["rate", "exchange rate", "forex rate"],
            ),
        },
        use_cases=[
            "Currency market monitoring",
            "Exchange rate tracking",
            "Global market analysis",
        ],
    ),
    "forex_quote": EndpointSemantics(
        client_name="alternative",
        method_name="get_forex_quote",
        natural_description="Get detailed real-time quote for a specific currency pair",
        example_queries=[
            "What's the current EUR/USD rate?",
            "Get GBP/JPY quote",
            "Show me the USD/CAD exchange rate",
            "Current forex price",
        ],
        related_terms=[
            "exchange rate",
            "forex rate",
            "currency price",
            "fx quote",
            "currency pair",
            "forex market",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Forex",
        parameter_hints={"symbol": SYMBOL_HINTS["forex"]},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current exchange rate",
                examples=["1.2150", "110.75"],
                related_terms=["rate", "exchange rate", "forex rate"],
            ),
            "bid": ResponseFieldInfo(
                description="Current bid price",
                examples=["1.2148", "110.73"],
                related_terms=["bid price", "buying price"],
            ),
            "ask": ResponseFieldInfo(
                description="Current ask price",
                examples=["1.2152", "110.77"],
                related_terms=["ask price", "selling price"],
            ),
        },
        use_cases=[
            "Currency trading",
            "Exchange rate monitoring",
            "Forex market analysis",
            "Currency conversion",
        ],
    ),
    "forex_historical": EndpointSemantics(
        client_name="alternative",
        method_name="get_forex_historical",
        natural_description="Get historical exchange rate data for a currency pair",
        example_queries=[
            "Get EUR/USD price history",
            "Show historical forex rates",
            "Past exchange rates for GBP/JPY",
            "Historical currency data",
        ],
        related_terms=[
            "historical rates",
            "past prices",
            "exchange rate history",
            "forex history",
            "currency trends",
            "historical data",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Forex",
        parameter_hints={
            "symbol": SYMBOL_HINTS["forex"],
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2023-12-20"],
                related_terms=["date", "trading day"],
            ),
            "rate": ResponseFieldInfo(
                description="Exchange rate",
                examples=["1.2150", "110.75"],
                related_terms=["price", "exchange rate", "rate"],
            ),
        },
        use_cases=[
            "Currency trend analysis",
            "Historical rate analysis",
            "Forex backtesting",
            "Market research",
        ],
    ),
    "forex_intraday": EndpointSemantics(
        client_name="alternative",
        method_name="get_forex_intraday",
        natural_description="Get intraday exchange rate data at specified intervals",
        example_queries=[
            "Get minute-by-minute EUR/USD rates",
            "Show hourly forex prices",
            "5-minute GBP/JPY data",
            "Intraday currency rates",
        ],
        related_terms=[
            "intraday rates",
            "minute data",
            "hourly rates",
            "high-frequency",
            "detailed rates",
            "short-term",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Forex",
        parameter_hints={
            "symbol": SYMBOL_HINTS["forex"],
            "interval": INTERVAL_HINT,
        },
        response_hints={
            "datetime": ResponseFieldInfo(
                description="Rate timestamp",
                examples=["2024-01-20 14:30:00"],
                related_terms=["time", "timestamp"],
            ),
            "rate": ResponseFieldInfo(
                description="Exchange rate",
                examples=["1.2150", "110.75"],
                related_terms=["price", "rate", "exchange rate"],
            ),
        },
        use_cases=[
            "Intraday trading",
            "High-frequency analysis",
            "Real-time monitoring",
            "Short-term trading",
        ],
    ),
    # Commodities endpoints
    "commodities_list": EndpointSemantics(
        client_name="alternative",
        method_name="get_commodities_list",
        natural_description="Get a list of all available commodities",
        example_queries=[
            "What commodities are available?",
            "Show commodity symbols",
            "List tradable commodities",
            "Available commodity markets",
        ],
        related_terms=[
            "commodities",
            "raw materials",
            "futures",
            "commodity markets",
            "trading symbols",
            "available products",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Commodities",
        parameter_hints={},
        response_hints={
            "symbol": ResponseFieldInfo(
                description="Commodity symbol",
                examples=["GC", "CL", "SI"],
                related_terms=["trading symbol", "commodity code"],
            ),
            "name": ResponseFieldInfo(
                description="Commodity name",
                examples=["Gold", "Crude Oil", "Silver"],
                related_terms=["product name", "commodity name"],
            ),
        },
        use_cases=[
            "Commodity market exploration",
            "Trading setup",
            "Market research",
        ],
    ),
    "commodities_quotes": EndpointSemantics(
        client_name="alternative",
        method_name="get_commodities_quotes",
        natural_description="Get current quotes for all available commodities",
        example_queries=[
            "Get all commodity prices",
            "Show current commodity quotes",
            "What are commodity prices now?",
            "Current commodity market rates",
        ],
        related_terms=[
            "commodity prices",
            "current quotes",
            "market prices",
            "spot prices",
            "futures prices",
            "live quotes",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Commodities",
        parameter_hints={},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current price",
                examples=["1875.50", "75.30"],
                related_terms=["current price", "spot price", "market price"],
            ),
        },
        use_cases=[
            "Market monitoring",
            "Price tracking",
            "Trading decisions",
        ],
    ),
    "commodity_quote": EndpointSemantics(
        client_name="alternative",
        method_name="get_commodity_quote",
        natural_description="Get detailed quote for a specific commodity",
        example_queries=[
            "What's the current gold price?",
            "Get oil quote",
            "Show silver market price",
            "Current commodity rate",
        ],
        related_terms=[
            "commodity price",
            "spot price",
            "futures price",
            "market quote",
            "current price",
            "trading price",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Commodities",
        parameter_hints={"symbol": SYMBOL_HINTS["commodity"]},
        response_hints={
            "price": ResponseFieldInfo(
                description="Current price",
                examples=["1875.50", "75.30"],
                related_terms=["spot price", "market price", "current price"],
            ),
        },
        use_cases=[
            "Price monitoring",
            "Trading decisions",
            "Market analysis",
        ],
    ),
    "commodity_historical": EndpointSemantics(
        client_name="alternative",
        method_name="get_commodity_historical",
        natural_description="Get historical price data for a commodity",
        example_queries=[
            "Get gold price history",
            "Historical oil prices",
            "Show past silver prices",
            "Commodity price trends",
        ],
        related_terms=[
            "historical prices",
            "price history",
            "past data",
            "historical trading",
            "commodity trends",
            "price data",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Commodities",
        parameter_hints={
            "symbol": SYMBOL_HINTS["commodity"],
            "start_date": DATE_HINTS["start_date"],
            "end_date": DATE_HINTS["end_date"],
        },
        response_hints={
            "date": ResponseFieldInfo(
                description="Trading date",
                examples=["2023-12-20"],
                related_terms=["date", "trading day"],
            ),
            "price": ResponseFieldInfo(
                description="Closing price",
                examples=["1875.50", "75.30"],
                related_terms=["close", "settlement price", "closing price"],
            ),
        },
        use_cases=[
            "Historical analysis",
            "Trend research",
            "Price forecasting",
            "Market studies",
        ],
    ),
    "commodity_intraday": EndpointSemantics(
        client_name="alternative",
        method_name="get_commodity_intraday",
        natural_description="Get intraday price data for commodities",
        example_queries=[
            "Get minute-by-minute gold prices",
            "Show hourly oil data",
            "Get silver intraday prices",
            "5-minute commodity data",
        ],
        related_terms=[
            "intraday prices",
            "minute data",
            "hourly prices",
            "high frequency",
            "real-time data",
            "price updates",
        ],
        category=SemanticCategory.ALTERNATIVE_DATA,
        sub_category="Commodities",
        parameter_hints={
            "symbol": SYMBOL_HINTS["commodity"],
            "interval": INTERVAL_HINT,
        },
        response_hints={
            "datetime": ResponseFieldInfo(
                description="Price timestamp",
                examples=["2024-01-20 14:30:00"],
                related_terms=["timestamp", "time", "date"],
            ),
            "price": ResponseFieldInfo(
                description="Price at interval",
                examples=["1875.50", "75.30"],
                related_terms=["price", "rate", "value"],
            ),
            "volume": ResponseFieldInfo(
                description="Trading volume",
                examples=["1250", "3500"],
                related_terms=["volume", "trades", "activity"],
            ),
        },
        use_cases=[
            "Day trading",
            "High-frequency trading",
            "Market monitoring",
            "Technical analysis",
            "Price tracking",
        ],
    ),
}
