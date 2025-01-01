# fmp_data/lc/validation.py

import logging
import re
from abc import ABC, abstractmethod
from typing import ClassVar

from fmp_data.lc.models import SemanticCategory

logger = logging.getLogger(__name__)


class ValidationRule(ABC):
    """
    Abstract base class that defines the validation interface.
    All market-specific validation rules must inherit from this.
    """

    # Required class variables that must be defined by subclasses
    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]]
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]]

    @property
    @abstractmethod
    def endpoint_prefixes(self) -> set[str]:
        """Get all valid endpoint prefixes for this rule"""
        pass

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        """The category this rule validates"""
        pass

    @abstractmethod
    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """
        Validate if method name matches expected category

        Args:
            method_name: Name of the method to validate
            category: Category to validate against

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """
        Validate parameters for a method

        Args:
            method_name: Name of the method
            parameters: Dictionary of parameter names and values

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @classmethod
    @abstractmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """
        Get subcategory and operation for a method name

        Args:
            method_name: Name of the method

        Returns:
            Tuple of (subcategory, operation) or None if not found
        """
        pass

    @abstractmethod
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
        pass


class ValidationRuleRegistry:
    """Registry that manages and coordinates all validation rules"""

    def __init__(self):
        self._rules: list[ValidationRule] = []
        self.logger = logger.getChild(self.__class__.__name__)

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule"""
        self._rules.append(rule)
        self.logger.debug(f"Registered validation rule: {rule.__class__.__name__}")

    def validate_category(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """
        Validate category using registered rules

        Args:
            method_name: Method name to validate
            category: Category to validate against

        Returns:
            Tuple of (is_valid, error_message)
        """
        # First find the rule that matches this category
        matching_rules = [
            rule for rule in self._rules if rule.expected_category == category
        ]
        message = ""
        if not matching_rules:
            # No rules for this category - consider it valid
            return True, ""

        # Try each matching rule
        for rule in matching_rules:
            valid, message = rule.validate(method_name, category)
            if valid:
                return True, ""

        # If we have rules but none validated, use the last error message
        return False, message

    def get_parameter_requirements(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[dict[str, list[str]] | None, str]:
        """
        Get parameter requirements for a method

        Args:
            method_name: Method name
            category: Expected category

        Returns:
            Tuple of (requirements dict or None, error message)
        """
        for rule in self._rules:
            if rule.expected_category == category:
                requirements = rule.get_parameter_requirements(method_name)
                if requirements is not None:
                    return requirements, ""
                return None, f"No parameter requirements found for {method_name}"

        return None, f"No validation rule found for category {category}"

    def validate_parameters(
        self, method_name: str, category: SemanticCategory, parameters: dict
    ) -> tuple[bool, str]:
        """
        Validate parameters using registered rules

        Args:
            method_name: Method name
            category: Expected category
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        for rule in self._rules:
            if rule.expected_category == category:
                return rule.validate_parameters(method_name, parameters)

        return True, ""  # No rules found for this category

    def get_expected_category(self, method_name: str) -> SemanticCategory | None:
        """
        Determine expected category for a method name

        Args:
            method_name: Method name to check

        Returns:
            Expected category or None if no matching rule found
        """
        for rule in self._rules:
            if any(method_name.startswith(prefix) for prefix in rule.endpoint_prefixes):
                return rule.expected_category
        return None


class CommonValidationRule(ValidationRule):
    """
    Common implementation of validation logic.
    Market-specific rules should inherit from this.
    """

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {}
    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {}

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        """Must be implemented by market-specific rules"""
        raise NotImplementedError

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate method name and category"""
        # First check category
        if category != self.expected_category:
            return False, f"Expected category {self.expected_category}, got {category}"

        # Check if method matches any group patterns
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            # Handle exact matches first
            if method_name in operations:
                return True, ""

            # Then check prefix + operation combinations
            if prefix:  # Only if prefix is not empty
                for operation in operations:
                    full_method = f"{prefix}{operation}"
                    if method_name == full_method:
                        return True, ""

        return False, f"Method {method_name} does not match any expected patterns"

    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """Common parameter validation implementation"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return False, f"Invalid method name: {method_name}"

        requirements = self.get_parameter_requirements(method_name)
        if not requirements:
            return True, ""  # No requirements defined

        for param_name, param_value in parameters.items():
            if param_name in requirements:
                patterns = requirements[param_name]
                if not any(re.match(pattern, str(param_value)) for pattern in patterns):
                    return (
                        False,
                        f"Invalid value for parameter {param_name}: {param_value}",
                    )

        return True, ""

    @property
    def endpoint_prefixes(self) -> set[str]:
        """Get all valid endpoint prefixes"""
        prefixes = set()
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            for operation in operations:
                prefixes.add(f"{prefix}{operation}")
        return prefixes

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """Get endpoint subcategory and operation"""
        for subcategory, (prefix, operations) in cls.METHOD_GROUPS.items():
            if method_name.startswith(prefix):
                operation = method_name[len(prefix) :]
                if operation in operations:
                    return subcategory, operation
        return None

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns = {}

        # Add common patterns based on operation type
        if operation == "historical":
            base_patterns.update(
                {
                    "start_date": self.PARAMETER_PATTERNS.get("date", []),
                    "end_date": self.PARAMETER_PATTERNS.get("date", []),
                }
            )
        elif operation == "intraday":
            base_patterns["interval"] = self.PARAMETER_PATTERNS.get("interval", [])

        # Add subcategory-specific patterns
        subcategory_patterns = self.PARAMETER_PATTERNS.get(
            f"{subcategory.lower()}_specific", {}
        )
        base_patterns.update(subcategory_patterns)

        return base_patterns
