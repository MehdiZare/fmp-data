from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class IntelligenceRule(CommonValidationRule):
    """Validation rules for market intelligence endpoints"""

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

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "limit": [r"^\d+$"],  # Numeric only
        "order": [r"^(asc|desc)$"],  # Sort order
        "symbol": [r"^[A-Z]{1,5}$"],  # Stock symbols
        "cik": [r"^\d{10}$"],  # CIK numbers
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        # Analyst research specific
        "analyst_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        # Calendar events specific
        "calendar_specific": {
            "quarter": [r"^[1-4]$"],  # Quarters 1-4
            "year": [r"^\d{4}$"],  # 4-digit year
        },
        # ESG specific
        "esg_specific": {
            "category": [r"^(E|S|G|ESG)$"],  # ESG categories
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # News & media specific
        "news_specific": {
            "source": [r"^[a-zA-Z_]+$"],  # News sources
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # Government & fundraising specific
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
                f"Category mismatch: expected "
                f"{SemanticCategory.INTELLIGENCE}, got {category}"
            )
            return (
                False,
                f"Expected category {SemanticCategory.INTELLIGENCE}, got {category}",
            )

        # Check if method exists in any group
        all_methods = set()
        for subcategory, (_, operations) in self.METHOD_GROUPS.items():
            self.logger.debug(
                f"Checking group {subcategory} with {len(operations)} operations"
            )
            all_methods.update(operations)
            if method_name in operations:
                self.logger.debug(f"Found {method_name} in {subcategory}")
                return True, ""

        self.logger.debug(f"Method {method_name} not found in any group")
        return (
            False,
            f"Method {method_name} not found. Valid methods: {sorted(all_methods)}",
        )

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with intelligence-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns = {}

        # Add common patterns based on operation type
        if any(x in operation for x in ["calendar", "historical", "dates"]):
            base_patterns.update(
                {
                    "from": self.PARAMETER_PATTERNS.get("date", []),
                    "to": self.PARAMETER_PATTERNS.get("date", []),
                }
            )

        # Add subcategory-specific patterns
        if subcategory in ["Analyst Research", "News & Media"]:
            base_patterns["symbol"] = self.PARAMETER_PATTERNS["symbol"]
        elif subcategory == "ESG":
            base_patterns.update(
                {
                    "symbol": self.PARAMETER_PATTERNS["symbol"],
                    "year": self.PARAMETER_PATTERNS.get("year", []),
                }
            )
        elif subcategory in ["Government Trading", "Fundraising"]:
            base_patterns["cik"] = self.PARAMETER_PATTERNS["cik"]

        return base_patterns
