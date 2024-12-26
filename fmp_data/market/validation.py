# fmp_data/market/validation.py

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class MarketDataRule(CategoryValidationRule):
    """Validation rules for market data endpoints"""

    PREFIXES = (
        "get_quote",
        "get_historical_",
        "get_intraday_",
        "get_market_",
        "get_gainers",
        "get_losers",
        "get_most_active",
        "get_sector_",
        "get_pre_post_",
    )

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.MARKET_DATA

    def validate(self, method_name: str, category: SemanticCategory) -> bool:
        """
        Validate if method name matches expected category

        Args:
            method_name: Name of the method to validate
            category: Category to validate against

        Returns:
            bool: True if valid, False otherwise
        """
        if category != self.expected_category:
            return False

        return any(method_name.startswith(prefix) for prefix in self.PREFIXES)
