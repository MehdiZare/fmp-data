# fmp_data/lc/validation.py
from abc import ABC, abstractmethod

from fmp_data.lc.models import SemanticCategory


class CategoryValidationRule(ABC):
    """Base class for endpoint category validation rules"""

    @abstractmethod
    def validate(self, method_name: str, category: SemanticCategory) -> bool:
        """Validate if method name matches expected category"""
        pass

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        """Expected category for this rule"""
        pass


# fmp_data/lc/validation.py
class ValidationRuleRegistry:
    """Registry for endpoint validation rules"""

    def __init__(self):
        self._rules: list[CategoryValidationRule] = []

    def register_rule(self, rule: CategoryValidationRule) -> None:
        """Register a new validation rule"""
        self._rules.append(rule)

    def validate_category(self, method_name: str, category: SemanticCategory) -> bool:
        """
        Validate endpoint category using registered rules

        Returns True if method_name matches any rule for its category
        """
        matching_rules = [
            rule for rule in self._rules if rule.validate(method_name, category)
        ]

        if not matching_rules:
            return True  # No rules found for this method name

        return any(rule.expected_category == category for rule in matching_rules)
