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
                "get_price_target_consensus",
                "get_price_target_summary",
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
            "get_company_",
            ["profile", "core_information", "notes", "employee_count"],
        ),
        "Search": (
            "",
            ["notes"],
        ),
        "Float": (
            "get_",
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
            "get_company_",
            ["logo_url", "symbol_changes"],
        ),
        "Screening": (
            "get_",
            ["stock_screener", "company_rating", "company_score", "company_outlook"],
        ),
    }

    # Must match parent type: dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str]] | dict[str, dict[str, list[str] | str | int]]
    ] = {
        # Top-level keys => list[str] only
        "symbol": [
            r"^[A-Z]{1,5}$",
            r"^[A-Z]{1,5}\.[A-Z]{1,3}$",  # e.g. "TSLA.B"
        ],
        "exchange": [r"^[A-Z]{2,6}$"],
        "date": [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{4}-\d{2}$",  # Monthly
        ],
        "period": ["annual", "quarter"],
        "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        "limit": [r"^\d+$"],
        # search_specific => a dict
        "search_specific": {
            "query": [r".{2,}"],
            "cik": [r"^\d{10}$"],
            "cusip": [r"^[A-Z0-9]{9}$"],
            "isin": [r"^[A-Z]{2}[A-Z0-9]{9}\d$"],
        },
        # technical_specific => a dict
        "technical_specific": {
            "type": [
                r"^(sma|ema|wma|dema|tema)$",
                r"^(williams|rsi|adx)$",
                r"^(standardDeviation)$",
            ],
            "time_period": [r"^\d+$"],
        },
        # screening_specific => a dict
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
        return SemanticCategory.COMPANY_INFO

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Return a dict[str, list[str]] if recognized, else None.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns: dict[str, list[str]] = {}

        # If not a search-related or list method, add "symbol"
        if not any(x in method_name for x in ["search", "list", "indexes"]):
            self._copy_top_level_list("symbol", base_patterns)

        # Subcategory-specific
        if subcategory == "Technical":
            # e.g. add "period", "interval" from top-level plus "type" from sub-dict
            self._copy_top_level_list("period", base_patterns)
            self._copy_top_level_list("interval", base_patterns)
            # Now copy "type" from technical_specific
            self._copy_subdict_keys("technical_specific", ["type"], base_patterns)

        if subcategory == "Search":
            # Pull everything from search_specific
            self._copy_subdict("search_specific", base_patterns)

        if subcategory == "Float" and "historical" in operation:
            # e.g. need "date" for historical share float
            self._copy_top_level_list("date", base_patterns)

        if subcategory == "Screening":
            # copy entire screening_specific sub-dict
            self._copy_subdict("screening_specific", base_patterns)

        return base_patterns if base_patterns else None

    def validate_response_type(self, method_name: str, response_type: str) -> bool:
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
        if category != self.expected_category:
            return False, f"Expected category {self.expected_category}, got {category}"

        # Check if method matches any group patterns
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                operation_part = method_name[len(prefix) :]

                # Direct or partial matches
                if operation_part in operations or any(
                    op in method_name for op in operations
                ):
                    return True, ""

        return False, f"Method {method_name} does not match any expected patterns"

    def _copy_top_level_list(self, key: str, target: dict[str, list[str]]) -> None:
        """
        Copies a top-level list[str] from PARAMETER_PATTERNS if it exists.
        """
        val = self.PARAMETER_PATTERNS.get(key)
        if isinstance(val, list):
            target[key] = val

    def _copy_subdict(self, dict_key: str, target: dict[str, list[str]]) -> None:
        """
        Copies every list[str] from PARAMETER_PATTERNS[dict_key].
        """
        maybe_sub = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(maybe_sub, dict):
            for sub_k, sub_v in maybe_sub.items():
                if isinstance(sub_v, list):
                    target[sub_k] = sub_v

    def _copy_subdict_keys(
        self, dict_key: str, keys: list[str], target: dict[str, list[str]]
    ) -> None:
        """
        Copies only certain keys from PARAMETER_PATTERNS[dict_key] if they're list[str].
        """
        maybe_sub = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(maybe_sub, dict):
            for k in keys:
                v = maybe_sub.get(k)
                if isinstance(v, list):
                    target[k] = v
