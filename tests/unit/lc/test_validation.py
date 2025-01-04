# tests/lc/test_validation.py
from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import (
    CommonValidationRule,
    ValidationRule,
    ValidationRuleRegistry,
)


class TestValidationRule(CommonValidationRule):
    """Test implementation of CommonValidationRule"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Market": ("get_market_", ["data", "summary", "stats"]),
        "Price": ("get_price_", ["history", "current", "forecast"]),
        "News": ("get_", ["news", "articles", "press_releases"]),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "symbol": [r"^[A-Z]{1,5}$"],
        "market_specific": {
            "exchange": [r"^(NYSE|NASDAQ)$"],
            "sector": [r"^[A-Za-z\s]+$"],
        },
        "price_specific": {
            "interval": [r"^(1min|5min|15min|30min|1hour|daily)$"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.MARKET_DATA

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Override validate method to ensure strict category matching"""
        if category != self.expected_category:
            return (
                False,
                f"Category mismatch: expected {self.expected_category}, got {category}",
            )

        # Check if method matches any group patterns
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            # Handle exact matches first
            if method_name in operations:
                return True, ""

            # Then check prefix + operation combinations
            if prefix:
                for operation in operations:
                    full_method = f"{prefix}{operation}"
                    if method_name == full_method:
                        return True, ""

        return False, f"Method {method_name} does not match any expected patterns"


def test_validation_rule_initialization():
    """Test validation rule initialization"""
    rule = TestValidationRule()
    assert isinstance(rule, ValidationRule)
    assert rule.expected_category == SemanticCategory.MARKET_DATA


def test_endpoint_prefixes():
    """Test getting endpoint prefixes"""
    rule = TestValidationRule()
    prefixes = rule.endpoint_prefixes

    expected_prefixes = {
        "get_market_data",
        "get_market_summary",
        "get_market_stats",
        "get_price_history",
        "get_price_current",
        "get_price_forecast",
        "get_news",
        "get_articles",
        "get_press_releases",
    }
    assert prefixes == expected_prefixes


def test_validate_method():
    """Test method validation"""
    rule = TestValidationRule()

    # Test valid methods
    valid_methods = [
        ("get_market_data", SemanticCategory.MARKET_DATA),
        ("get_price_history", SemanticCategory.MARKET_DATA),
        ("get_news", SemanticCategory.MARKET_DATA),
    ]
    for method, category in valid_methods:
        is_valid, message = rule.validate(method, category)
        assert is_valid
        assert message == ""

    # Test invalid methods
    invalid_methods = [
        ("invalid_method", SemanticCategory.MARKET_DATA),
        ("get_market_invalid", SemanticCategory.MARKET_DATA),
        ("get_market_data", SemanticCategory.INSTITUTIONAL),  # Wrong category
    ]
    for method, category in invalid_methods:
        is_valid, message = rule.validate(method, category)
        assert not is_valid
        assert message != ""


def test_get_endpoint_info():
    """Test getting endpoint info"""
    rule = TestValidationRule()

    valid_cases = [
        ("get_market_data", ("Market", "data")),
        ("get_price_history", ("Price", "history")),
        ("get_news", ("News", "news")),
    ]
    for method, expected in valid_cases:
        info = rule.get_endpoint_info(method)
        assert info == expected

    invalid_cases = ["invalid_method", "get_invalid", "unknown_endpoint"]
    for method in invalid_cases:
        info = rule.get_endpoint_info(method)
        assert info is None


def test_validate_parameters():
    """Test parameter validation"""
    rule = TestValidationRule()

    valid_params = {
        "date": "2024-01-01",
        "symbol": "AAPL",
        "exchange": "NYSE",
        "interval": "1min",
    }
    is_valid, message = rule.validate_parameters("get_market_data", valid_params)
    assert is_valid
    assert message == ""

    invalid_params = {
        "date": "invalid-date",
        "symbol": "invalid-symbol",
        "exchange": "invalid-exchange",
        "interval": "invalid-interval",
    }
    is_valid, message = rule.validate_parameters("get_market_data", invalid_params)
    assert not is_valid
    assert "Invalid value for parameter" in message


def test_get_parameter_requirements():
    """Test getting parameter requirements"""
    rule = TestValidationRule()

    market_reqs = rule.get_parameter_requirements("get_market_data")
    assert market_reqs is not None
    assert "exchange" in market_reqs
    assert "sector" in market_reqs

    price_reqs = rule.get_parameter_requirements("get_price_history")
    assert price_reqs is not None
    assert "interval" in price_reqs

    invalid_reqs = rule.get_parameter_requirements("invalid_endpoint")
    assert invalid_reqs is None


class TestInstitutionalRule(CommonValidationRule):
    """Test implementation for institutional category"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Institutional": ("get_institutional_", ["data", "holdings"]),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {}

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.INSTITUTIONAL


def test_validation_rule_registry():
    """Test ValidationRuleRegistry with multiple rules"""
    registry = ValidationRuleRegistry()
    market_rule = TestValidationRule()
    institutional_rule = TestInstitutionalRule()

    # Register both rules
    registry.register_rule(market_rule)
    registry.register_rule(institutional_rule)

    # Test valid market data category validation
    valid, message = registry.validate_category(
        "get_market_data", SemanticCategory.MARKET_DATA
    )
    assert valid
    assert message == ""

    # Test valid institutional category validation
    valid, message = registry.validate_category(
        "get_institutional_data", SemanticCategory.INSTITUTIONAL
    )
    assert valid
    assert message == ""

    # Test category mismatch for market data endpoint
    valid, message = registry.validate_category(
        "get_market_data", SemanticCategory.INSTITUTIONAL
    )
    assert not valid
    assert "Category mismatch" in message
    assert "belongs to Market Data" in message  # Updated to match enum value
    assert "not Institutional Data" in message  # Updated to match enum value

    # Test unknown method
    valid, message = registry.validate_category(
        "unknown_method", SemanticCategory.MARKET_DATA
    )
    assert not valid
    assert "No matching rule found" in message

    # Test unknown category
    valid, message = registry.validate_category(
        "get_market_data", SemanticCategory.UNKNOWN_CATEGORY
    )
    assert not valid
    assert "No rules found for category" in message


def test_get_expected_category():
    """Test getting expected category"""
    registry = ValidationRuleRegistry()
    market_rule = TestValidationRule()
    institutional_rule = TestInstitutionalRule()

    registry.register_rule(market_rule)
    registry.register_rule(institutional_rule)

    # Test valid endpoints
    assert (
        registry.get_expected_category("get_market_data")
        == SemanticCategory.MARKET_DATA
    )
    assert (
        registry.get_expected_category("get_institutional_data")
        == SemanticCategory.INSTITUTIONAL
    )

    # Test invalid endpoint
    assert registry.get_expected_category("invalid_endpoint") is None
