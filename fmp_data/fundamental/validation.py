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

    # EXACTLY match the parent type signature:
    # dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Top-level keys => list[str]
        "symbol": [r"^[A-Z]{1,5}$"],  # Stock symbols
        "limit": [r"^\d+$"],  # Numeric only
        "order": [r"^(asc|desc)$"],  # Sort order
        # statement_specific => a dict with string keys → list[str]|str|int
        "statement_specific": {
            "period": [r"^(annual|quarter)$"],  # Reporting period
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # metrics_specific => dict
        "metrics_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # valuation_specific => dict
        "valuation_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
        },
        # ratings_specific => dict
        "ratings_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],  # YYYY-MM-DD
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for fundamental analysis endpoints."""
        return SemanticCategory.FUNDAMENTAL_ANALYSIS

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Get parameter validation patterns for fundamental analysis endpoints.
        Returns a dict[str, list[str]] if recognized, else None.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, _ = endpoint_info

        # Build up a final dict[str, list[str]] using only list-of-string values.
        base_patterns: dict[str, list[str]] = {}

        # Common to all fundamental endpoints
        self._copy_top_level_patterns(["limit", "order"], base_patterns)

        # Add subcategory-specific patterns
        match subcategory:
            case "Financial Statements":
                # Add 'symbol' top-level
                self._copy_top_level_patterns(["symbol"], base_patterns)
                # Copy 'period' from statement_specific
                self._copy_subdict_patterns(
                    "statement_specific", ["period"], base_patterns
                )

            case "Financial Metrics":
                # Copy 'symbol' from metrics_specific
                self._copy_subdict_patterns(
                    "metrics_specific", ["symbol"], base_patterns
                )

            case "Valuation":
                # Copy 'symbol' from valuation_specific
                self._copy_subdict_patterns(
                    "valuation_specific", ["symbol"], base_patterns
                )

            case "Ratings":
                # Copy 'symbol' and 'date' from ratings_specific
                self._copy_subdict_patterns(
                    "ratings_specific", ["symbol", "date"], base_patterns
                )

            case _:
                return None

        return base_patterns if base_patterns else None

    def _copy_top_level_patterns(
        self, keys: list[str], target: dict[str, list[str]]
    ) -> None:
        """
        Copy each key from top-level if it is a list[str].
        """
        for k in keys:
            maybe_val = self.PARAMETER_PATTERNS.get(k)
            if isinstance(maybe_val, list):
                target[k] = maybe_val

    def _copy_subdict_patterns(
        self, dict_key: str, sub_keys: list[str], target: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[dict_key] is a dict, copy only the 'list[str]' entries
        for the specified sub_keys into 'target'.
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            for sk in sub_keys:
                maybe_val = sub_dict.get(sk)
                if isinstance(maybe_val, list):
                    target[sk] = maybe_val
