"""
Trading-Focused MCP Tools Manifest

This configuration includes tools optimized for trading and market analysis.
Includes real-time quotes, technical indicators, and market movers.
"""

TOOLS = [
    # Real-time market data
    "quote",
    "simple_quote",
    "gainers",
    "losers",
    "most_active",
    "pre_post_market",
    # Price history for charting
    "historical_price",
    "historical_prices",
    "intraday_price",
    "intraday_prices",
    # Technical analysis
    "sma",
    "ema",
    "rsi",
    "adx",
    "williams",
    "dema",
    "tema",
    "wma",
    "standard_deviation",
    # Market intelligence
    "stock_news",
    "price_target",
    "price_target_consensus",
    "price_target_summary",
    # Alternative markets
    "crypto_quote",
    "forex_quote",
]
