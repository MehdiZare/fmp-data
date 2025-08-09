from typing import Any

import pytest

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.registry import EndpointBasedRule, ValidationRuleRegistry
from fmp_data.models import APIVersion, Endpoint, HTTPMethod, URLType


@pytest.fixture
def market_endpoints() -> dict[str, Endpoint[Any]]:
    """Fixture providing market data endpoints."""
    return {
        "get_market_data": Endpoint(
            name="get_market_data",
            path="market/data",
            version=APIVersion.STABLE,
            url_type=URLType.API,
            method=HTTPMethod.GET,
            description="Get market data",
            mandatory_params=[],
            optional_params=None,
            response_model=dict,
            arg_model=None,
        )
    }


@pytest.fixture
def alternative_endpoints() -> dict[str, Endpoint[Any]]:
    """Fixture providing alternative data endpoints."""
    return {
        "get_crypto_price": Endpoint(
            name="get_crypto_price",
            path="crypto/price",
            version=APIVersion.STABLE,
            url_type=URLType.API,
            method=HTTPMethod.GET,
            description="Get crypto price",
            mandatory_params=[],
            optional_params=None,
            response_model=dict,
            arg_model=None,
        )
    }


@pytest.fixture
def registry(market_endpoints, alternative_endpoints) -> ValidationRuleRegistry:
    """Fixture providing populated ValidationRuleRegistry."""
    registry = ValidationRuleRegistry()

    market_rule = EndpointBasedRule(market_endpoints, SemanticCategory.MARKET_DATA)
    alt_rule = EndpointBasedRule(
        alternative_endpoints, SemanticCategory.ALTERNATIVE_DATA
    )

    registry.register_rule(market_rule)
    registry.register_rule(alt_rule)

    return registry


class TestValidationRuleRegistry:
    """Tests for ValidationRuleRegistry."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        registry = ValidationRuleRegistry()
        assert registry._rules == []

    def test_register_rule(self, market_endpoints) -> None:
        """Test rule registration."""
        registry = ValidationRuleRegistry()
        rule = EndpointBasedRule(market_endpoints, SemanticCategory.MARKET_DATA)
        registry.register_rule(rule)
        assert len(registry._rules) == 1

    def test_validate_category_valid(self, registry: ValidationRuleRegistry) -> None:
        """Test category validation with valid input."""
        is_valid, message = registry.validate_category(
            "get_market_data", SemanticCategory.MARKET_DATA
        )
        assert is_valid
        assert message == ""

    def test_validate_category_invalid(self, registry: ValidationRuleRegistry) -> None:
        """Test category validation with invalid input."""
        # Wrong category
        is_valid, message = registry.validate_category(
            "get_market_data", SemanticCategory.ALTERNATIVE_DATA
        )
        assert not is_valid
        assert "Category mismatch" in message

        # Unknown method
        is_valid, message = registry.validate_category(
            "unknown_method", SemanticCategory.MARKET_DATA
        )
        assert not is_valid
        assert "No matching rule found" in message

    def test_get_parameter_requirements(self, registry: ValidationRuleRegistry) -> None:
        """Test getting parameter requirements."""
        # Test endpoint with no parameters - should return None
        requirements, message = registry.get_parameter_requirements(
            "get_market_data", SemanticCategory.MARKET_DATA
        )
        assert requirements is None
        assert message == "No parameter requirements found for get_market_data"

        # Test invalid endpoint
        requirements, message = registry.get_parameter_requirements(
            "invalid_endpoint", SemanticCategory.MARKET_DATA
        )
        assert requirements is None
        assert "No parameter requirements found" in message

    def test_validate_parameters(self, registry: ValidationRuleRegistry) -> None:
        """Test parameter validation."""
        is_valid, message = registry.validate_parameters(
            "get_market_data",
            SemanticCategory.MARKET_DATA,
            {},  # Empty params since our test endpoint has none
        )
        assert is_valid
        assert message == ""

    def test_get_expected_category(self, registry: ValidationRuleRegistry) -> None:
        """Test getting expected category."""
        assert (
            registry.get_expected_category("get_market_data")
            == SemanticCategory.MARKET_DATA
        )
        assert (
            registry.get_expected_category("get_crypto_price")
            == SemanticCategory.ALTERNATIVE_DATA
        )
        assert registry.get_expected_category("invalid_method") is None
