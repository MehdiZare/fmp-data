from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class EconomicsRule(CommonValidationRule):
    """Validation rules for economics endpoints"""

    # Method prefix to subcategory mapping
    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Treasury": (
            "get_treasury_",
            [
                "rate",
                "rates",
                "yield_curve",
                "inflation_expectation",
            ],
        ),
        "Economic Indicators": (
            "get_economic_",
            [
                "calendar",
                "indicators",
                "inflation_rate",
                "gdp_growth_rate",
                "unemployment_rate",
                "consumer_sentiment",
                "retail_sales",
                "industrial_production",
                "housing_starts",
            ],
        ),
        "Market Risk": (
            "get_market_risk_",
            [
                "premium",
                "free_rate",
                "indicators",
                "index",
            ],
        ),
    }

    # Parameter patterns for validation with better organization
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns used across all economics endpoints
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        "limit": [r"^\d+$"],  # Numeric only
        "frequency": [r"^(daily|monthly|quarterly|annual)$"],
        # Treasury specific patterns
        "treasury_specific": {
            "maturity": [r"^(\d+[MY]|3M|6M|1Y|2Y|5Y|10Y|30Y)$"]  # Treasury maturities
        },
        # Economic indicators specific patterns
        "economic_indicators_specific": {
            "country": [r"^[A-Z]{2}$"],  # Two-letter country codes
            "indicator": [r"^(GDP|CPI|PMI|NFP|RETAIL|TRADE|HOUSING|SENTIMENT)$"],
        },
        # Market risk specific patterns
        "market_risk_specific": {
            "country": [r"^[A-Z]{2}$"]  # Two-letter country codes
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for economics endpoints"""
        return SemanticCategory.ECONOMIC

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with economics-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Base requirements common to all economic endpoints
        base_patterns = {
            "date": self.PARAMETER_PATTERNS["date"],
            "limit": self.PARAMETER_PATTERNS["limit"],
            "frequency": self.PARAMETER_PATTERNS["frequency"],
        }

        # Add subcategory-specific patterns
        if subcategory == "Treasury":
            base_patterns.update(self.PARAMETER_PATTERNS["treasury_specific"])
        elif subcategory == "Economic Indicators":
            base_patterns.update(
                self.PARAMETER_PATTERNS["economic_indicators_specific"]
            )
        elif subcategory == "Market Risk":
            base_patterns.update(self.PARAMETER_PATTERNS["market_risk_specific"])

        return base_patterns
