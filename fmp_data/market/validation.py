from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class MarketDataRule(CommonValidationRule):
    """Validation rules for market data endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Market Data": (
            "get_",
            [
                "market_hours",
                "market_indices",
                "market_gainers",
                "market_losers",
                "market_sectors",
                "market_most_active",
                "all_shares_float",
            ],
        ),
        "Quote Data": (
            "get_",
            [
                "pre_post_market",
            ],
        ),
        "Stock Lists": (
            "get_",
            [
                "stock_list",
                "available_stocks",
                "tradable_symbols",
                "exchange_symbols",
                "etf_list",
                "available_indexes",
                "exchange_symbols",
                "company_list",
            ],
        ),
        "Search": (
            "",
            ["search", "search_by_cik", "search_by_cusip", "search_by_isin", "notes"],
        ),
        "Market Movers": ("get_", ["gainers", "losers", "most_active"]),
        "Market Analysis": ("get_", ["sector_performance"]),
    }

    # Must exactly match the parent signature:
    # dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        "limit": [r"^\d+$"],
        "order": [r"^(asc|desc)$"],
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "price_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        },
        "quote_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        "list_specific": {"exchange": [r"^[A-Z]{2,6}$"]},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for market data endpoints"""
        return SemanticCategory.MARKET_DATA

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Get parameter validation patterns with market-specific logic.

        Returns:
            A dict mapping parameter name to a list of regex patterns.
            Returns None if the endpoint does not match any subcategory/operation.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns: dict[str, list[str]] = {}

        # Always add limit/order if present
        self._add_top_level_pattern("limit", base_patterns)
        self._add_top_level_pattern("order", base_patterns)

        # Add subcategory-specific patterns
        match subcategory:
            case "Price Data":
                self._add_subdict_patterns("price_specific", base_patterns)
                if "historical" in operation or "intraday" in operation:
                    self._add_top_level_pattern("date", base_patterns)

            case "Quote Data":
                self._add_subdict_patterns("quote_specific", base_patterns)
                # Some operations might need "date"
                if "trade" in operation or "tick" in operation:
                    self._add_top_level_pattern("date", base_patterns)

            case "Stock Lists":
                self._add_subdict_patterns("list_specific", base_patterns)

        # If we have patterns, return them; else None
        return base_patterns if base_patterns else None

    def _add_top_level_pattern(
        self, key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[key] is a list, add it to base_patterns.
        """
        val = self.PARAMETER_PATTERNS.get(key)
        if isinstance(val, list):
            base_patterns[key] = val

    def _add_subdict_patterns(
        self, dict_key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[dict_key] is a dict, copy only the entries
        whose value is a list[str].
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            for param, value in sub_dict.items():
                if isinstance(value, list):
                    base_patterns[param] = value
