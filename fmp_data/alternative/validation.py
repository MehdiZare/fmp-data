from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class AlternativeMarketsRule(CommonValidationRule):
    """Validation rules for alternative markets endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Cryptocurrency": (
            "get_crypto_",
            ["list", "quotes", "quote", "historical", "intraday"],
        ),
        "Forex": (
            "get_forex_",
            ["list", "quotes", "quote", "historical", "intraday"],
        ),
        "CommoditiesSingular": (
            "get_commodity_",  # For singular form
            ["quote", "historical", "intraday"],
        ),
        "CommoditiesPlural": (
            "get_commodities_",  # For plural form
            ["list", "quotes"],
        ),
    }

    # Parameter patterns remain the same
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "interval": [r"^(1min|5min|15min|30min|1hour|4hour)$"],
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "limit": [r"^\d+$"],
        # Subcategory-specific patterns
        "cryptocurrency_specific": {"symbol": [r"^[A-Z]{3,4}USD$"]},
        "forex_specific": {"symbol": [r"^[A-Z]{6}$"]},
        "commodities_specific": {"symbol": [r"^[A-Z]{2,3}$"]},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for alternative market endpoints"""
        return SemanticCategory.ALTERNATIVE_DATA
