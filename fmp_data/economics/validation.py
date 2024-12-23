from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class EconomicsRule(CategoryValidationRule):
    """Validation rules for economics endpoints"""

    PREFIXES = (
        "get_treasury_",
        "get_economic_",
        "get_market_risk_",
    )

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.ECONOMIC

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
