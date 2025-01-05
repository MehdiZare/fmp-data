# fmp_data/institutional/validation.py

from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class InstitutionalRule(CommonValidationRule):
    """Validation rules for institutional endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Base": (
            "get_",
            [
                "asset_allocation",
                "institutional_holdings",
                "institutional_holders",  # Added
                "transaction_types",
                "insider_statistics",
                "price_target",  # Added
            ],
        ),
        "13F": (
            "get_form_13f",
            [
                "",  # For base get_form_13f
                "_dates",
                "_list",
                "_metadata",
                "_holding_summary",
                "_securities_list",
            ],
        ),
        "Insider": (
            "get_insider_",
            ["trading", "trades", "roster", "ownership", "transactions", "statistics"],
        ),
        "CIK": (
            "get_cik_",
            [
                "mapper",
                "mapper_by_name",
                "mapper_by_symbol",
                "search",
                "list",
                "lookup",
                "map",
            ],
        ),
        "Beneficial": ("get_beneficial_", ["ownership", "summary", "holders"]),
        "FTD": ("get_fail_to_", ["deliver", "receive", "summary"]),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD format
        "limit": [r"^\d+$"],  # Numeric only
        "symbol": [r"^[A-Z]{1,5}$"],  # Standard stock symbols
        "cik": [r"^\d{10}$"],  # 10-digit CIK numbers
        # 13F specific patterns
        "13f_specific": {
            "form_type": [r"^(13F-HR|13F-NT)$"],  # 13F form types
            "quarter": [r"^[1-4]$"],  # Quarters 1-4
            "year": [r"^\d{4}$"],  # 4-digit year
        },
        # Holdings specific patterns
        "holdings_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],
        },
        # Insider specific patterns
        "insider_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        # CIK specific patterns
        "cik_specific": {"cik": [r"^\d{10}$"]},
        # Beneficial ownership specific patterns
        "beneficial_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],
        },
        # Failures to deliver specific patterns
        "ftd_specific": {"symbol": [r"^[A-Z]{1,5}$"], "date": [r"^\d{4}-\d{2}-\d{2}$"]},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for institutional endpoints"""
        return SemanticCategory.INSTITUTIONAL

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with institutional-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, _ = endpoint_info

        # Define base requirements for each subcategory
        match subcategory:
            case "13F Filings":
                patterns = {
                    "cik": self.PARAMETER_PATTERNS["cik"],
                    "date": self.PARAMETER_PATTERNS["date"],
                }
                patterns.update(self.PARAMETER_PATTERNS["13f_specific"])
                return patterns

            case "Institutional Holdings":
                return self.PARAMETER_PATTERNS["holdings_specific"]

            case "Insider Trading":
                return self.PARAMETER_PATTERNS["insider_specific"]

            case "CIK Data":
                return self.PARAMETER_PATTERNS["cik_specific"]

            case "Beneficial Ownership":
                return self.PARAMETER_PATTERNS["beneficial_specific"]

            case "Failures to Deliver":
                return self.PARAMETER_PATTERNS["ftd_specific"]

        return None
