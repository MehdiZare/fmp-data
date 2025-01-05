from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class IntelligenceRule(CommonValidationRule):
    """
    Validation rules for market intelligence endpoints
    """

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Calendar Events": (
            "",
            [
                "get_dividends_calendar",
                "get_earnings_calendar",
                "get_earnings_confirmed",
                "get_earnings_surprises",
                "get_equity_offering_by_cik",
                "get_equity_offering_rss",
                "get_historical_earnings",
                "get_ipo_calendar",
                "get_stock_splits_calendar",
                "get_financial_reports_dates",
            ],
        ),
        "ESG": (
            "",
            [
                "get_esg_benchmark",
                "get_esg_data",
                "get_esg_ratings",
            ],
        ),
        "News & Media": (
            "",
            [
                "get_crypto_news",
                "get_fmp_articles",
                "get_forex_news",
                "get_general_news",
                "get_press_releases",
                "get_press_releases_by_symbol",
                "get_stock_news",
                "get_stock_news_sentiments",
            ],
        ),
        "Sentiment": (
            "",
            [
                "get_historical_social_sentiment",
                "get_social_sentiment_changes",
                "get_trending_social_sentiment",
            ],
        ),
        "Government Trading": (
            "",
            [
                "get_house_disclosure",
                "get_house_disclosure_rss",
                "get_senate_trading",
                "get_senate_trading_rss",
            ],
        ),
        "Fundraising": (
            "",
            [
                "get_crowdfunding_by_cik",
                "get_crowdfunding_rss",
                "get_crowdfunding_search",
                "get_equity_offering_by_cik",
                "get_equity_offering_rss",
                "get_equity_offering_search",
            ],
        ),
    }

    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Top-level keys that map to list[str]
        "limit": [r"^\d+$"],  # numeric-only
        "order": [r"^(asc|desc)$"],  # sort order
        "symbol": [r"^[A-Z]{1,5}$"],  # stock symbols
        "cik": [r"^\d{10}$"],  # CIK numbers (10-digit)
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        # Keys that map to dict[str, list[str] | str | int]
        "analyst_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        "calendar_specific": {
            "quarter": [r"^[1-4]$"],  # Quarters 1-4
            "year": [r"^\d{4}$"],  # 4-digit year
        },
        "esg_specific": {"category": [r"^(E|S|G|ESG)$"], "symbol": [r"^[A-Z]{1,5}$"]},
        "news_specific": {"source": [r"^[a-zA-Z_]+$"], "symbol": [r"^[A-Z]{1,5}$"]},
        "gov_fundraising_specific": {"cik": [r"^\d{10}$"]},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for market intelligence endpoints"""
        return SemanticCategory.INTELLIGENCE

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate method name and category"""
        self.logger.debug(f"Validating method: {method_name} with category: {category}")

        if category != SemanticCategory.INTELLIGENCE:
            self.logger.debug(
                f"Category mismatch: "
                f"expected {SemanticCategory.INTELLIGENCE}, "
                f"got {category}"
            )
            return (
                False,
                f"Expected category {SemanticCategory.INTELLIGENCE}, got {category}",
            )

        # Check if method exists in any group
        all_methods = set()
        for subcat, (_, operations) in self.METHOD_GROUPS.items():
            self.logger.debug(
                f"Checking group {subcat} with {len(operations)} operations"
            )
            all_methods.update(operations)
            if method_name in operations:
                self.logger.debug(f"Found {method_name} in {subcat}")
                return True, ""

        self.logger.debug(f"Method {method_name} not found in any group")
        return (
            False,
            f"Method {method_name} not found. Valid methods: {sorted(all_methods)}",
        )

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Get parameter validation patterns with intelligence-specific logic.
        Returns a dict[str, list[str]] or None if no match.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Always annotate your dict
        base_patterns: dict[str, list[str]] = {}

        if any(x in operation for x in ("calendar", "historical", "dates")):
            base_patterns["from"] = self._fetch_list_patterns("date")
            base_patterns["to"] = self._fetch_list_patterns("date")

        # Possibly add 'limit'/'order'
        base_patterns["limit"] = self._fetch_list_patterns("limit")
        base_patterns["order"] = self._fetch_list_patterns("order")

        # Add subcategory-specific:
        match subcategory:
            case "Analyst Research" | "News & Media":
                # symbol is top-level => a list[str]
                base_patterns["symbol"] = self._fetch_list_patterns("symbol")
            case "ESG":
                base_patterns["symbol"] = self._fetch_list_patterns("symbol")
                base_patterns["year"] = self._fetch_list_patterns_in_subdict(
                    "calendar_specific", "year"
                )
            case "Government Trading" | "Fundraising":
                base_patterns["cik"] = self._fetch_list_patterns("cik")

        return base_patterns if base_patterns else None

    def _fetch_list_patterns(self, key: str) -> list[str]:
        """
        Safely retrieve a list of patterns from PARAMETER_PATTERNS[key].
        Returns [] if not found or if it's not a list[str].
        """
        val = self.PARAMETER_PATTERNS.get(key)
        return val if isinstance(val, list) else []

    def _fetch_list_patterns_in_subdict(self, dict_key: str, param: str) -> list[str]:
        """
        If PARAMETER_PATTERNS[dict_key] is a dict, try to fetch a list[str]
        under 'param'. Return [] if not found or mismatched type.
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            val = sub_dict.get(param)
            if isinstance(val, list):
                return val
        return []
