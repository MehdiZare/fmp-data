from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class EconomicsRule(CommonValidationRule):
    """Validation rules for economics endpoints"""

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

    # Must match parent's type exactly:
    # dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Top-level keys => list[str]
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD
        "limit": [r"^\d+$"],  # numeric
        "frequency": [r"^(daily|monthly|quarterly|annual)$"],
        # treasury_specific => a dict
        "treasury_specific": {
            "maturity": [r"^(\d+[MY]|3M|6M|1Y|2Y|5Y|10Y|30Y)$"]  # e.g. 3M, 5Y, 10Y
        },
        # economic_indicators_specific => a dict
        "economic_indicators_specific": {
            "country": [r"^[A-Z]{2}$"],  # e.g. US
            "indicator": [r"^(GDP|CPI|PMI|NFP|RETAIL|TRADE|HOUSING|SENTIMENT)$"],
        },
        # market_risk_specific => a dict
        "market_risk_specific": {"country": [r"^[A-Z]{2}$"]},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.ECONOMIC

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Get parameter validation patterns for economics endpoints.
        Returns dict[str, list[str]] if recognized, else None.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, _ = endpoint_info

        # Build a dict[str, list[str]] by selectively copying patterns.
        base_patterns: dict[str, list[str]] = {}

        # Always add these top-level patterns
        self._copy_top_level(["date", "limit", "frequency"], base_patterns)

        # Subcategory-specific
        if subcategory == "Treasury":
            self._copy_subdict("treasury_specific", base_patterns)
        elif subcategory == "Economic Indicators":
            self._copy_subdict("economic_indicators_specific", base_patterns)
        elif subcategory == "Market Risk":
            self._copy_subdict("market_risk_specific", base_patterns)
        else:
            return None

        return base_patterns if base_patterns else None

    def _copy_top_level(self, keys: list[str], target: dict[str, list[str]]) -> None:
        """
        Copies only top-level list[str] from PARAMETER_PATTERNS.
        """
        for k in keys:
            val = self.PARAMETER_PATTERNS.get(k)
            if isinstance(val, list):
                target[k] = val

    def _copy_subdict(self, dict_key: str, target: dict[str, list[str]]) -> None:
        """
        Copies only the list[str] items from
        a nested dict at PARAMETER_PATTERNS[dict_key].
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            for param, patterns in sub_dict.items():
                if isinstance(patterns, list):
                    target[param] = patterns
