# fmp_data/alternative/__init__.py
from __future__ import annotations

from fmp_data.alternative.async_client import AsyncAlternativeMarketsClient
from fmp_data.alternative.client import AlternativeMarketsClient
from fmp_data.alternative.models import (
    Commodity,
    CommodityHistoricalPrice,
    CommodityIntradayPrice,
    CommodityQuote,
    CryptoHistoricalPrice,
    CryptoIntradayPrice,
    CryptoPair,
    CryptoQuote,
    ForexHistoricalPrice,
    ForexIntradayPrice,
    ForexPair,
    ForexQuote,
)

__all__ = [
    "AlternativeMarketsClient",
    "AsyncAlternativeMarketsClient",
    "Commodity",
    "CommodityHistoricalPrice",
    "CommodityIntradayPrice",
    "CommodityQuote",
    "CryptoHistoricalPrice",
    "CryptoIntradayPrice",
    "CryptoPair",
    "CryptoQuote",
    "ForexHistoricalPrice",
    "ForexIntradayPrice",
    "ForexPair",
    "ForexQuote",
]
