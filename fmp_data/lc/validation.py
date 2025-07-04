# fmp_data/lc/validation.py
from abc import ABC, abstractmethod
import re
from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.logger import FMPLogger


class ValidationRule(ABC):
    """
    Abstract base class for validation rules.
    Subclasses must implement the abstract properties and methods below.
    """

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        """
        The category this rule is responsible for validating.
        """
        ...

    @property
    @abstractmethod
    def endpoint_prefixes(self) -> set[str]:
        """
        A set of prefixes that identify which methods belong to this rule.
        Example: {"getPrice", "fetchData"}.
        """
        ...

    @abstractmethod
    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """
        Validate that the `method_name` belongs to `category`.

        Returns:
            A tuple of (is_valid, error_message).
        """
        ...

    @abstractmethod
    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """
        Validate parameters for the specified method_name.

        Returns:
            A tuple of (is_valid, error_message).
        """
        ...

    @classmethod
    @abstractmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """
        Return metadata about the method (e.g., subcategory, operation),
        or None if not recognized.
        """
        ...

    @abstractmethod
    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Return a dict of parameter requirements (param_name -> list of regex patterns),
        or None if no pattern is enforced.
        """
        ...


class CommonValidationRule(ValidationRule):
    """
    Common base class for validation. Subclasses define the actual
    expected_category, endpoint_prefixes, etc.
    """

    # Each key can map to either a list of regex patterns or a nested dict.
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {}

    def __init__(self) -> None:
        super().__init__()
        self.logger = FMPLogger().get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        raise NotImplementedError

    @property
    def endpoint_prefixes(self) -> set[str]:
        """
        By default, return an empty set. Subclasses can override.
        """
        return set()

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """
        Default 'validate' just checks if categories match.
        Subclasses can override for additional logic.
        """
        if category != self.expected_category:
            return False, f"Expected {self.expected_category}, got {category}"
        return True, ""

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """
        Subclasses can override to return (subcategory, operation) if relevant.
        """
        return None

    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """
        Default implementation checks any known parameter requirements.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return False, f"Invalid method name: {method_name}"

        requirements = self.get_parameter_requirements(method_name)
        if not requirements:
            return True, ""  # No specific patterns

        for param_name, param_value in parameters.items():
            if param_name in requirements:
                patterns = requirements[param_name]
                # Ensure at least one pattern matches
                if not any(re.match(p, str(param_value)) for p in patterns):
                    return (
                        False,
                        f"Invalid value for parameter '{param_name}': {param_value}",
                    )

        return True, ""

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        if method_name == "historical":
            return self._build_historical_patterns()
        return None

    def _build_historical_patterns(self) -> dict[str, list[str]]:
        """
        Example of building patterns for a 'historical' method.
        """
        base_patterns: dict[str, list[str]] = {}

        date_patterns = self.PARAMETER_PATTERNS.get("date")
        if isinstance(date_patterns, list):
            # It's already a list[str]
            base_patterns["start_date"] = date_patterns
            base_patterns["end_date"] = date_patterns
        elif isinstance(date_patterns, dict):
            # A nested dict, e.g. {"common": [...], ...}
            sub_list = date_patterns.get("common")
            if isinstance(sub_list, list):
                base_patterns["start_date"] = sub_list
                base_patterns["end_date"] = sub_list
            else:
                base_patterns["start_date"] = []
                base_patterns["end_date"] = []
        else:
            base_patterns["start_date"] = []
            base_patterns["end_date"] = []

        return base_patterns


class ValidationRuleRegistry:
    """Registry that manages and coordinates all validation rules"""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._rules: list[ValidationRule] = []
        self.logger = FMPLogger().get_logger(self.__class__.__name__)

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
        # First check if we have any rules for this category
        category_rules = [
            rule for rule in self._rules if rule.expected_category == category
        ]
        if not category_rules:
            return False, f"No rules found for category {category.value}"

        # Then find the correct rule for this method based on its prefix patterns
        matching_rule: ValidationRule | None = None
        for rule in self._rules:
            # Here we rely on rule.endpoint_prefixes existing
            if any(method_name.startswith(prefix) for prefix in rule.endpoint_prefixes):
                matching_rule = rule
                break

        if matching_rule:
            # If we found a matching rule but category doesn't match
            if matching_rule.expected_category != category:
                return (
                    False,
                    f"Category mismatch: endpoint {method_name} "
                    f"belongs to {matching_rule.expected_category.value}, "
                    f"not {category.value}",
                )

            # If categories match, validate the method pattern
            return matching_rule.validate(method_name, category)

        # If no rule has a matching prefix
        return (
            False,
            f"No matching rule found for {method_name} in category {category.value}",
        )

    def get_parameter_requirements(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[dict[str, list[str]] | None, str]:
        """Get parameter requirements for a method"""
        for rule in self._rules:
            if rule.expected_category == category:
                requirements = rule.get_parameter_requirements(method_name)
                if requirements is not None:
                    return requirements, ""
        return None, f"No parameter requirements found for {method_name}"

    def validate_parameters(
        self, method_name: str, category: SemanticCategory, parameters: dict
    ) -> tuple[bool, str]:
        """Validate parameters using registered rules"""
        for rule in self._rules:
            if rule.expected_category == category:
                return rule.validate_parameters(method_name, parameters)
        return True, ""  # No rules for this category

    def get_expected_category(self, method_name: str) -> SemanticCategory | None:
        """Determine the expected category for a method name"""
        for rule in self._rules:
            if any(method_name.startswith(prefix) for prefix in rule.endpoint_prefixes):
                return rule.expected_category
        return None
