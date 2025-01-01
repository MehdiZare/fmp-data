from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class InvestmentProductsRule(CommonValidationRule):
    """Validation rules for investment products endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "ETF": (
            "get_etf_",
            [
                "holdings",  # Actual endpoint name
                "holding_dates",  # Actual endpoint name
                "info",  # Actual endpoint name
                "sector_weightings",  # Actual endpoint name
                "country_weightings",  # Actual endpoint name
                "exposure",  # Actual endpoint name
                "holder",  # Actual endpoint name
                # Legacy patterns kept for backwards compatibility
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
                "holdings",  # Actual endpoint name
                "dates",  # Actual endpoint name
                "by_name",  # Actual endpoint name
                "holder",  # Actual endpoint name
                # Legacy patterns kept for backwards compatibility
                "profile",
                "historical",
                "search",
                "holders",
                "performance",
                "stats",
            ],
        ),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "limit": [r"^\d+$"],  # Numeric only
        "order": [r"^(asc|desc)$"],  # Sort order
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        # ETF specific patterns
        "etf_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],  # Standard ticker symbols
            "exchange": [r"^[A-Z]{2,6}$"],  # Exchange codes
        },
        # Mutual fund specific patterns
        "mutual_fund_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "name": [r".{2,}"],  # At least 2 characters for fund names
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
        """Get parameter validation patterns with investment-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Base requirements common to all investment endpoints
        base_patterns = {
            "limit": self.PARAMETER_PATTERNS["limit"],
            "order": self.PARAMETER_PATTERNS["order"],
        }

        # Add date requirement for historical operations
        if "historical" in operation:
            base_patterns["date"] = self.PARAMETER_PATTERNS["date"]

        # Add subcategory-specific patterns
        if subcategory == "ETF":
            base_patterns.update(self.PARAMETER_PATTERNS["etf_specific"])
        elif subcategory == "Mutual Fund":
            base_patterns.update(self.PARAMETER_PATTERNS["mutual_fund_specific"])

        return base_patterns
