# fmp_data/company/validation.py
from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class CompanyInfoRule(CategoryValidationRule):
    """Validation rules for company information endpoints"""

    # Method prefix to subcategory mapping
    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Profile": (
            "get_",
            ["profile", "core_information", "company_notes", "employee_count"],
        ),
        "Search": ("search", ["", "by_cik", "by_cusip", "by_isin"]),
        "Lists": (
            "get_",
            ["stock_list", "etf_list", "available_indexes", "exchange_symbols"],
        ),
        "Executive": ("get_", ["executives", "executive_compensation"]),
        "Float": (
            "get_",
            ["share_float", "historical_share_float", "all_shares_float"],
        ),
        "Revenue": (
            "get_",
            ["product_revenue_segmentation", "geographic_revenue_segmentation"],
        ),
        "Symbol": ("get_", ["company_logo_url", "symbol_changes"]),
    }

    # Parameter patterns for validation
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str]]]] = {
        "symbol": [r"^[A-Z]{1,5}$"],  # Standard stock symbols
        "exchange": [r"^[A-Z]{2,6}$"],  # Exchange codes like NYSE, NASDAQ
        "period": ["annual", "quarter"],
        "query": [r".{2,}"],  # At least 2 characters for search
        "limit": [r"^\d+$"],  # Numeric only
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.COMPANY_INFO

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
        import re

        # Validate each parameter
        for param_name, param_value in parameters.items():
            if param_name in self.PARAMETER_PATTERNS:
                patterns = self.PARAMETER_PATTERNS[param_name]

                # Check if value matches any of the valid patterns
                if not any(re.match(pattern, str(param_value)) for pattern in patterns):
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
            subcategory, _ = endpoint_info
            # Return relevant patterns based on subcategory and method
            if "profile" in method_name or "float" in method_name:
                return {"symbol": self.PARAMETER_PATTERNS["symbol"]}
            elif "search" in method_name:
                return {"query": self.PARAMETER_PATTERNS["query"]}
            elif "exchange" in method_name:
                return {"exchange": self.PARAMETER_PATTERNS["exchange"]}
        return None
