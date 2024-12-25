# fmp_data/investment/validation.py

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class InvestmentProductsRule(CategoryValidationRule):
    """Validation rules for investment products endpoints"""

    PREFIXES = (
        "get_etf_",
        "get_mutual_fund_",
    )

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.INVESTMENT_PRODUCTS

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

    def validate_semantic_hints(self, method_name: str, hints: dict) -> bool:
        """
        Additional validation for semantic hints

        Args:
            method_name: Method name being validated
            hints: Dictionary of parameter hints

        Returns:
            bool: True if valid, False otherwise
        """
        # ETF endpoints should have symbol parameter hint
        if method_name.startswith("get_etf_"):
            if "symbol" not in hints:
                return False

        # Mutual fund endpoints should have either symbol or name
        elif method_name.startswith("get_mutual_fund_"):
            if not any(param in hints for param in ["symbol", "name"]):
                return False

        return True
