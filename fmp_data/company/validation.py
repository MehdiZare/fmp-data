from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class CompanyInfoRule(CommonValidationRule):
    """Validation rules for company information endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Analyst Research": (
            "",
            [
                "get_analyst_estimates",
                "get_analyst_recommendations",
                "get_price_target",
                "get_price_target_consensus",  # Only list once
                "get_price_target_summary",  # Only list once
                "get_upgrades_downgrades",
                "get_upgrades_downgrades_consensus",
            ],
        ),
        "Price Data": (
            "get_",
            [
                "price",
                "historical_price",
                "daily_price",
                "intraday_price",
                "real_time_price",
                "simple_quote",
                "quote",
            ],
        ),
        "Historical Data": (
            "get_",
            [
                "historical_prices",
                "intraday_prices",
                "market_cap",
                "historical_market_cap",
            ],
        ),
        "Basic": (
            "get_",
            [
                "executives",
                "executive_compensation",
                "employee_count",
                "symbol_changes",
                "profile",
                "core_information",
                "tradable_symbols",
                "delisted_companies",
            ],
        ),
        "Profile": (
            "get_company_",  # Changed prefix to be more specific
            ["profile", "core_information", "notes", "employee_count"],
        ),
        "Search": (
            "",  # Added underscore for consistency
            ["notes"],
        ),
        "Float": (
            "get_",  # Changed prefix
            [
                "share_float",
                "historical_share_float",
            ],
        ),
        "Revenue": (
            "get_",
            ["product_revenue_segmentation", "geographic_revenue_segmentation"],
        ),
        "Symbol": (
            "get_company_",  # Made prefix more specific
            ["logo_url", "symbol_changes"],
        ),
        "Screening": (
            "get_",
            ["stock_screener", "company_rating", "company_score", "company_outlook"],
        ),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "symbol": [
            r"^[A-Z]{1,5}$",  # Standard stock symbols
            r"^[A-Z]{1,5}\.[A-Z]{1,3}$",  # Symbols with exchange suffix
        ],
        "exchange": [r"^[A-Z]{2,6}$"],
        "date": [
            r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
            r"^\d{4}-\d{2}$",  # YYYY-MM for monthly data
        ],
        "period": ["annual", "quarter"],
        "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        "limit": [r"^\d+$"],
        # Search patterns
        "search_specific": {
            "query": [r".{2,}"],  # At least 2 characters
            "cik": [r"^\d{10}$"],
            "cusip": [r"^[A-Z0-9]{9}$"],
            "isin": [r"^[A-Z]{2}[A-Z0-9]{9}\d$"],
        },
        # Technical patterns
        "technical_specific": {
            "type": [
                r"^(sma|ema|wma|dema|tema)$",  # Moving averages
                r"^(williams|rsi|adx)$",  # Momentum
                r"^(standardDeviation)$",  # Volatility
            ],
            "time_period": [r"^\d+$"],
        },
        # Screening patterns
        "screening_specific": {
            "market_cap_min": [r"^\d+$"],
            "market_cap_max": [r"^\d+$"],
            "beta_min": [r"^-?\d*\.?\d+$"],
            "beta_max": [r"^-?\d*\.?\d+$"],
            "volume_min": [r"^\d+$"],
            "volume_max": [r"^\d+$"],
            "dividend_min": [r"^\d*\.?\d+$"],
            "dividend_max": [r"^\d*\.?\d+$"],
            "sector": [r"^[A-Za-z\s]+$"],
            "industry": [r"^[A-Za-z\s]+$"],
            "country": [r"^[A-Za-z\s]+$"],
        },
    }

    RESPONSE_TYPES: ClassVar[dict[str, set[str]]] = {
        "Basic": {"json"},
        "Profile": {"json"},
        "Search": {"json"},
        "Float": {"json"},
        "Revenue": {"json"},
        "Symbol": {"json", "image"},
        "Technical": {"json"},
        "Screening": {"json"},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for company information endpoints"""
        return SemanticCategory.COMPANY_INFO

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get required parameter patterns for method"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns = {}

        # Add symbol requirement for most endpoints
        if not any(x in method_name for x in ["search", "list", "indexes"]):
            base_patterns["symbol"] = self.PARAMETER_PATTERNS["symbol"]

        # Add subcategory-specific patterns
        if subcategory == "Technical":
            base_patterns.update(
                {
                    "period": self.PARAMETER_PATTERNS["period"],
                    "interval": self.PARAMETER_PATTERNS["interval"],
                    "type": self.PARAMETER_PATTERNS["technical_specific"]["type"],
                }
            )

        if subcategory == "Search":
            base_patterns.update(self.PARAMETER_PATTERNS["search_specific"])

        if subcategory == "Float" and "historical" in operation:
            base_patterns.update({"date": self.PARAMETER_PATTERNS["date"]})

        if subcategory == "Screening":
            base_patterns.update(self.PARAMETER_PATTERNS["screening_specific"])

        return base_patterns

    def validate_response_type(self, method_name: str, response_type: str) -> bool:
        """Validate if response type is supported for method"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return False

        subcategory, _ = endpoint_info
        valid_types = self.RESPONSE_TYPES.get(subcategory, {"json"})
        return response_type in valid_types

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate method name and category"""
        # First check category
        if category != self.expected_category:
            return False, f"Expected category {self.expected_category}, got {category}"

        # Check if method matches any group patterns
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                # Get the operation part by removing prefix
                operation = method_name[len(prefix) :]

                # Handle both direct matches and compound operations
                if operation in operations or any(
                    op in method_name for op in operations
                ):
                    return True, ""

        return False, f"Method {method_name} does not match any expected patterns"
