# fmp_data/intelligence/validation.py

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class MarketIntelligenceRule(CategoryValidationRule):
    """Validation rules for market intelligence endpoints"""

    METHOD_GROUPS: dict[str, tuple[str, list[str]]] = {
        "Analyst Research": (
            "get_",
            [
                "price_target",
                "analyst_estimates",
                "analyst_recommendations",
                "upgrades_downgrades",
            ],
        ),
        "Calendar Events": (
            "get_",
            [
                "earnings_calendar",
                "earnings_confirmed",
                "dividends_calendar",
                "stock_splits_calendar",
                "ipo_calendar",
            ],
        ),
        "ESG": (
            "get_esg_",
            ["data", "ratings", "benchmark"],
        ),
        "News": (
            "get_",
            [
                "fmp_articles",
                "general_news",
                "stock_news",
                "forex_news",
                "crypto_news",
                "press_releases",
            ],
        ),
        "Government Trading": (
            "get_",
            ["senate_trading", "house_disclosure"],
        ),
    }

    PARAMETER_PATTERNS: dict[str, dict[str, list[str]]] = {
        "symbol": {
            "stock": [r"^[A-Z]{1,5}$"],
            "crypto": [r"^[A-Z]{3,4}$"],
            "forex": [r"^[A-Z]{6}$"],
        },
        "date": {
            "format": [r"^\d{4}-\d{2}-\d{2}$"],
        },
        "page": {
            "range": [r"^\d+$"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.INSTITUTIONAL

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

        # Validate method name format and allowed operations
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                operation = method_name[len(prefix) :]
                return operation in operations

        return False

    def validate_parameters(self, method_name: str, parameters: dict) -> bool:
        """
        Validate parameters for the endpoint

        Args:
            method_name: Name of the method
            parameters: Dictionary of parameters

        Returns:
            bool: True if valid, False otherwise
        """
        for param_name, param_value in parameters.items():
            patterns = self.PARAMETER_PATTERNS.get(param_name, {})
            for pattern_list in patterns.values():
                import re

                if not any(
                    re.match(pattern, str(param_value)) for pattern in pattern_list
                ):
                    return False
        return True
