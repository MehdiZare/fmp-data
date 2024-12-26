# fmp_data/technical/validation.py

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class TechnicalAnalysisRule(CategoryValidationRule):
    """Validation rules for technical analysis endpoints"""

    PREFIXES = (
        "get_sma",
        "get_ema",
        "get_wma",
        "get_dema",
        "get_tema",
        "get_williams",
        "get_rsi",
        "get_adx",
        "get_standard_deviation",
    )

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.TECHNICAL_ANALYSIS

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
