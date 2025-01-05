from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class InvestmentProductsRule(CommonValidationRule):
    """Validation rules for investment products endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "ETF": (
            "get_etf_",
            [
                "holdings",
                "holding_dates",
                "info",
                "sector_weightings",
                "country_weightings",
                "exposure",
                "holder",
                # Legacy for backward compatibility
                "profile",
                "sector_weights",
                "country_weights",
                "historical",
                "holders",
                "constituents",
                "stats",
            ],
        ),
        "Mutual Fund": (
            "get_mutual_fund_",
            [
                "holdings",
                "dates",
                "by_name",
                "holder",
                # Legacy
                "profile",
                "historical",
                "search",
                "holders",
                "performance",
                "stats",
            ],
        ),
    }

    # Must match the parent's exact annotation:
    # dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Common keys that are lists of patterns
        "limit": [r"^\d+$"],  # numeric only
        "order": [r"^(asc|desc)$"],  # sort order
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        # ETF-specific sub-dictionary
        "etf_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],  # ticker symbols
            "exchange": [r"^[A-Z]{2,6}$"],  # exchange codes
        },
        # Mutual-fund-specific sub-dictionary
        "mutual_fund_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "name": [r".{2,}"],  # at least 2 chars
            "type": [r"^(equity|fixed_income|commodity|mixed|specialty|money_market)$"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for investment products endpoints"""
        return SemanticCategory.INVESTMENT_PRODUCTS

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Return parameter validation patterns for recognized investment endpoints.

        Ensures we return a dict[str, list[str]] with only list-of-string patterns,
        or None if we fail to match an endpoint.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Start with a blank dict and selectively add patterns
        base_patterns: dict[str, list[str]] = {}

        # Add common patterns: limit, order
        self._add_top_level_pattern("limit", base_patterns)
        self._add_top_level_pattern("order", base_patterns)

        # Add "date" if "historical" in operation
        if "historical" in operation:
            self._add_top_level_pattern("date", base_patterns)

        # Subcategory-specific patterns
        if subcategory == "ETF":
            self._add_subdict_patterns("etf_specific", base_patterns)
        elif subcategory == "Mutual Fund":
            self._add_subdict_patterns("mutual_fund_specific", base_patterns)

        return base_patterns if base_patterns else None

    def _add_top_level_pattern(
        self, key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[key] is a list of patterns, copy it into base_patterns.
        """
        val = self.PARAMETER_PATTERNS.get(key)
        if isinstance(val, list):
            base_patterns[key] = val

    def _add_subdict_patterns(
        self, dict_key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[dict_key] is a dict, copy only its list[str] entries
        into base_patterns. This avoids passing str/int where list[str] is expected.
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            for param_name, param_val in sub_dict.items():
                if isinstance(param_val, list):
                    base_patterns[param_name] = param_val
