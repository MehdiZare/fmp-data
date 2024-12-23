# fmp_data/alternative/validation.py
from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class AlternativeMarketsRule(CategoryValidationRule):
    """Validation rules for alternative markets endpoints"""

    # Method prefix to subcategory mapping
    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Cryptocurrency": (
            "get_crypto_",
            ["list", "quotes", "quote", "historical", "intraday"],
        ),
        "Forex": ("get_forex_", ["list", "quotes", "quote", "historical", "intraday"]),
        "Commodities": (
            "get_commodit",  # Handles both commodities_ and commodity_
            ["list", "quotes", "quote", "historical", "intraday"],
        ),
    }

    # Parameter patterns for validation
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str]]]] = {
        "Cryptocurrency": {
            "symbol": ["^[A-Z]{3,4}USD$"],
            "interval": ["1min", "5min", "15min", "30min", "1hour", "4hour"],
        },
        "Forex": {
            "symbol": ["^[A-Z]{6}$"],
            "interval": ["1min", "5min", "15min", "30min", "1hour", "4hour"],
        },
        "Commodities": {
            "symbol": ["^[A-Z]{2,3}$"],
            "interval": ["1min", "5min", "15min", "30min", "1hour", "4hour"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.ALTERNATIVE_DATA

    def validate(self, method_name: str, category: SemanticCategory) -> bool:
        """
        Validate method name and category

        Args:
            method_name: Name of the method to validate
            category: Category to validate against

        Returns:
            bool: True if valid, False otherwise
        """
        # First check category
        if category != self.expected_category:
            return False

        # Validate method name format and allowed operations
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                # Extract operation name after prefix
                operation = method_name[len(prefix) :]
                return operation in operations

        return False

    def validate_parameters(self, method_name: str, parameters: dict) -> bool:
        """
        Validate parameters for a method

        Args:
            method_name: Name of the method
            parameters: Dictionary of parameter names and values

        Returns:
            bool: True if valid, False otherwise
        """
        # Determine which subcategory this method belongs to
        subcategory = None
        for subcat, (prefix, _) in self.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                subcategory = subcat
                break

        if not subcategory:
            return False

        # Get parameter patterns for this subcategory
        patterns = self.PARAMETER_PATTERNS[subcategory]

        # Validate each parameter
        for param_name, param_value in parameters.items():
            if param_name in patterns:
                if param_name == "interval":
                    if param_value not in patterns["interval"]:
                        return False
                elif param_name == "symbol":
                    import re

                    if not any(
                        re.match(pattern, param_value) for pattern in patterns["symbol"]
                    ):
                        return False

        return True

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """
        Get subcategory and operation for a method name

        Args:
            method_name: Name of the method

        Returns:
            Tuple of (subcategory, operation) or None if not found
        """
        for subcategory, (prefix, operations) in cls.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                operation = method_name[len(prefix) :]
                if operation in operations:
                    return subcategory, operation
        return None

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Get required parameter patterns for a method

        Args:
            method_name: Name of the method

        Returns:
            Dict of parameter patterns or None if not found
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if endpoint_info:
            subcategory, operation = endpoint_info
            return self.PARAMETER_PATTERNS[subcategory]
        return None
