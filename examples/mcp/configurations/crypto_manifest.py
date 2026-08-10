"""
Cryptocurrency-Focused MCP Tools Manifest

This configuration specializes in cryptocurrency and digital asset data.
"""

TOOLS = [
    # Crypto market data
    "crypto_list",
    "crypto_quote",
    # `crypto_quotes` and `forex_quotes` are each claimed by two clients
    # (`alternative` and `batch`), so the bare key cannot resolve (#126).
    "alternative.crypto_quotes",
    "crypto_historical",
    "crypto_intraday",
    # Related market data
    "forex_quote",  # For fiat pairs
    "alternative.forex_quotes",
    "commodities_quotes",  # For gold/silver comparison
    # Market sentiment
    "crypto_news",
    # Technical indicators for crypto
    "sma",
    "rsi",
    "ema",
    "adx",
    "williams",
]
