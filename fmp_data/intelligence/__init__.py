# fmp_data/intelligence/__init__.py
from fmp_data.intelligence.client import MarketIntelligenceClient
from fmp_data.intelligence.models import (
    AnalystEstimate,
    AnalystRecommendation,
    DividendEvent,
    EarningConfirmed,
    EarningEvent,
    EarningSurprise,
    IPOEvent,
    PriceTarget,
    PriceTargetConsensus,
    PriceTargetSummary,
    StockSplitEvent,
    UpgradeDowngrade,
    UpgradeDowngradeConsensus,
)

__all__ = [
    "MarketIntelligenceClient",
    "PriceTarget",
    "PriceTargetSummary",
    "PriceTargetConsensus",
    "AnalystEstimate",
    "AnalystRecommendation",
    "UpgradeDowngrade",
    "UpgradeDowngradeConsensus",
    "EarningEvent",
    "EarningConfirmed",
    "EarningSurprise",
    "DividendEvent",
    "StockSplitEvent",
    "IPOEvent",
]
