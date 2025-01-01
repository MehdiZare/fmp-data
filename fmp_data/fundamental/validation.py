from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class FundamentalAnalysisRule(CommonValidationRule):
    """Validation rules for fundamental analysis endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Financial Statements": (
            "get_",
            [
                "income_statement",
                "balance_sheet",
                "cash_flow",
                "full_financial_statement",
                "financial_reports_dates",
            ],
        ),
        "Financial Metrics": (
            "get_",
            [
                "key_metrics",
                "financial_ratios",
                "owner_earnings",
            ],
        ),
        "Valuation": (
            "get_",
            ["levered_dcf"],
        ),
        "Ratings": (
            "get_",
            ["historical_rating"],
        ),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns used across all fundamental endpoints
        "symbol": [r"^[A-Z]{1,5}$"],  # Stock symbols
        "limit": [r"^\d+$"],  # Numeric only
        "order": [r"^(asc|desc)$"],  # Sort order
        # Financial statements specific patterns
        "statement_specific": {
            "period": [r"^(annual|quarter)$"],  # Reporting period
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # Financial metrics specific patterns
        "metrics_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # Valuation specific patterns
        "valuation_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # Ratings specific patterns
        "ratings_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for fundamental analysis endpoints"""
        return SemanticCategory.FUNDAMENTAL_ANALYSIS

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with fundamental analysis specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Base requirements common to all fundamental endpoints
        base_patterns = {
            "limit": self.PARAMETER_PATTERNS["limit"],
            "order": self.PARAMETER_PATTERNS["order"],
        }

        # Add subcategory-specific requirements
        if subcategory == "Financial Statements":
            base_patterns.update(
                {
                    "symbol": self.PARAMETER_PATTERNS["symbol"],
                    "period": self.PARAMETER_PATTERNS.get("statement_specific", {}).get(
                        "period", []
                    ),
                }
            )
        elif subcategory == "Financial Metrics":
            base_patterns.update(
                symbol=self.PARAMETER_PATTERNS.get("metrics_specific", {}).get(
                    "symbol", []
                )
            )
        elif subcategory == "Valuation":
            base_patterns.update(
                symbol=self.PARAMETER_PATTERNS.get("valuation_specific", {}).get(
                    "symbol", []
                )
            )
        elif subcategory == "Ratings":
            base_patterns.update(
                {
                    "symbol": self.PARAMETER_PATTERNS.get("ratings_specific", {}).get(
                        "symbol", []
                    ),
                    "date": self.PARAMETER_PATTERNS.get("ratings_specific", {}).get(
                        "date", []
                    ),
                }
            )

        return base_patterns
