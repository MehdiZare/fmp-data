# fmp_data/fundamental/validation.py

from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CategoryValidationRule


class FundamentalAnalysisRule(CategoryValidationRule):
    """Validation rules for fundamental analysis endpoints"""

    # Method prefix to subcategory mapping
    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Financial Statements": (
            "get_",
            [
                "income_statement",
                "balance_sheet",
                "cash_flow",
                "full_financial_statement",
                "financial_report_dates",
            ],
        ),
        "Financial Metrics": (
            "get_",
            ["key_metrics", "financial_ratios", "owner_earnings", "levered_dcf"],
        ),
        "Ratings": ("get_", ["historical_rating"]),
    }

    # Parameter patterns for validation
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, str | list[str] | int]]] = {
        "symbol": {"pattern": r"^[A-Z]{1,5}$", "examples": ["AAPL", "MSFT", "GOOGL"]},
        "period": {
            "pattern": r"^(annual|quarter)$",
            "examples": ["annual", "quarter"],
            "valid_values": ["annual", "quarter"],
        },
        "limit": {"pattern": r"^\d+$", "min": 1, "max": 100},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.FUNDAMENTAL_ANALYSIS

    def validate(self, method_name: str, category: SemanticCategory) -> bool:
        """
        Validate if method name matches expected category

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
            for operation in operations:
                if method_name == f"{prefix}{operation}":
                    return True

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

        # Validate symbol parameter if present
        if "symbol" in parameters:
            symbol_pattern = self.PARAMETER_PATTERNS["symbol"]["pattern"]
            if not re.match(symbol_pattern, str(parameters["symbol"])):
                return False

        # Validate period parameter if present
        if "period" in parameters:
            period = str(parameters["period"])
            valid_periods = self.PARAMETER_PATTERNS["period"]["valid_values"]
            if period not in valid_periods:
                return False

        # Validate limit parameter if present
        if "limit" in parameters:
            try:
                limit = int(parameters["limit"])
                min_limit = self.PARAMETER_PATTERNS["limit"]["min"]
                max_limit = self.PARAMETER_PATTERNS["limit"]["max"]
                if limit < min_limit or limit > max_limit:
                    return False
            except (ValueError, TypeError):
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
            for operation in operations:
                if method_name == f"{prefix}{operation}":
                    return subcategory, operation
        return None

    def get_parameter_requirements(self, method_name: str) -> dict[str, dict] | None:
        """
        Get parameter validation requirements for a method

        Args:
            method_name: Name of the method

        Returns:
            Dictionary of parameter requirements or None if not found
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        # Return relevant parameter patterns based on method type
        patterns = {}

        # All methods require symbol
        patterns["symbol"] = self.PARAMETER_PATTERNS["symbol"]

        # Statement methods require period and limit
        if endpoint_info[0] == "Financial Statements":
            patterns["period"] = self.PARAMETER_PATTERNS["period"]
            patterns["limit"] = self.PARAMETER_PATTERNS["limit"]

        return patterns
