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
                "institutional_holders",
                "transaction_types",
                "insider_statistics",
                "price_target",
            ],
        ),
        "13F": (
            "get_form_13f",
            [
                "",
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

    # EXACTLY match the parent's type:
    # dict[str, list[str] | dict[str, list[str] | str | int]]
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Top-level keys => list[str]
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "limit": [r"^\d+$"],
        "symbol": [r"^[A-Z]{1,5}$"],
        "cik": [r"^\d{10}$"],
        # Nested keys => dict[str, list[str]|str|int]
        "13f_specific": {
            "form_type": [r"^(13F-HR|13F-NT)$"],
            "quarter": [r"^[1-4]$"],
            "year": [r"^\d{4}$"],
        },
        "holdings_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],
        },
        "insider_specific": {"symbol": [r"^[A-Z]{1,5}$"]},
        "cik_specific": {"cik": [r"^\d{10}$"]},
        "beneficial_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],
        },
        "ftd_specific": {
            "symbol": [r"^[A-Z]{1,5}$"],
            "date": [r"^\d{4}-\d{2}-\d{2}$"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.INSTITUTIONAL

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcat, _ = endpoint_info

        # Build a dict[str, list[str]] from the relevant sub-dict
        match subcat:
            case "13F Filings":
                return self._build_13f_requirements()
            case "Institutional Holdings":
                return self._copy_subdict_patterns("holdings_specific")
            case "Insider Trading":
                return self._copy_subdict_patterns("insider_specific")
            case "CIK Data":
                return self._copy_subdict_patterns("cik_specific")
            case "Beneficial Ownership":
                return self._copy_subdict_patterns("beneficial_specific")
            case "Failures to Deliver":
                return self._copy_subdict_patterns("ftd_specific")
            case _:
                return None

    def _build_13f_requirements(self) -> dict[str, list[str]]:
        """
        Example: combine a few top-level keys plus the 13f_specific sub-dict.
        """
        base: dict[str, list[str]] = {}
        # Add top-level keys if they exist
        self._safe_add_top_level("cik", base)
        self._safe_add_top_level("date", base)
        # Merge '13f_specific' patterns
        sub = self._copy_subdict_patterns("13f_specific")
        base.update(sub)
        return base

    def _safe_add_top_level(self, key: str, target: dict[str, list[str]]) -> None:
        """
        Safely copies a top-level list[str], if present, into the target dict.
        """
        value = self.PARAMETER_PATTERNS.get(key)
        if isinstance(value, list):
            target[key] = value

    def _copy_subdict_patterns(self, dict_key: str) -> dict[str, list[str]]:
        """
        Copies only the entries whose value is list[str] from a nested dict key.
        Returns an empty dict if not found or if sub-dict is invalid.
        """
        results: dict[str, list[str]] = {}
        maybe_sub = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(maybe_sub, dict):
            for k, v in maybe_sub.items():
                if isinstance(v, list):
                    results[k] = v
        return results
