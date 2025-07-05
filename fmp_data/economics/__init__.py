# fmp_data/economics/__init__.py
from fmp_data.economics.client import EconomicsClient
from fmp_data.economics.models import (
    EconomicEvent,
    EconomicIndicator,
    MarketRiskPremium,
    TreasuryRate,
)

__all__ = [
    "EconomicEvent",
    "EconomicIndicator",
    "EconomicsClient",
    "MarketRiskPremium",
    "TreasuryRate",
]
