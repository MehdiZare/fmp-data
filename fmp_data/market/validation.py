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
            "",  # Added underscore for consistency
            ["search", "search_by_cik", "search_by_cusip", "search_by_isin", "notes"],
        ),
        "Market Movers": ("get_", ["gainers", "losers", "most_active"]),
        "Market Analysis": ("get_", ["sector_performance"]),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "limit": [r"^\d+$"],  # Numeric only
        "order": [r"^(asc|desc)$"],  # Sort order
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        # Price data specific
        "price_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        },
        # Quote data specific
        "quote_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        # Stock lists specific
        "list_specific": {"exchange": [r"^[A-Z]{2,6}$"]},  # Exchange codes
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for market data endpoints"""
        return SemanticCategory.MARKET_DATA

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with market-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Base requirements
        base_patterns = {
            "limit": self.PARAMETER_PATTERNS["limit"],
            "order": self.PARAMETER_PATTERNS["order"],
        }

        # Add subcategory-specific patterns
        match subcategory:
            case "Price Data":
                base_patterns.update(self.PARAMETER_PATTERNS["price_specific"])
                if "historical" in operation or "intraday" in operation:
                    base_patterns["date"] = self.PARAMETER_PATTERNS["date"]

            case "Quote Data":
                base_patterns.update(self.PARAMETER_PATTERNS["quote_specific"])
                if "trade" in operation or "tick" in operation:
                    base_patterns["date"] = self.PARAMETER_PATTERNS["date"]

            case "Stock Lists":
                base_patterns.update(self.PARAMETER_PATTERNS["list_specific"])

        return base_patterns
