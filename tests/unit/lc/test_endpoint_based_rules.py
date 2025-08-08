from datetime import date
from typing import Any

import pytest

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.registry import EndpointBasedRule
from fmp_data.models import (
    APIVersion,
    Endpoint,
    EndpointParam,
    HTTPMethod,
    ParamLocation,
    ParamType,
    URLType,
)


@pytest.fixture
def sample_endpoints() -> dict[str, Endpoint[Any]]:
    """Fixture providing sample endpoints for testing."""
    return {
        "get_market_price": Endpoint(
            name="get_market_price",
            path="market/price/{symbol}",
            version=APIVersion.STABLE,
            url_type=URLType.API,
            method=HTTPMethod.GET,
            description="Get market price for a symbol",
            mandatory_params=[
                EndpointParam(
                    name="symbol",
                    location=ParamLocation.PATH,
                    param_type=ParamType.STRING,
                    required=True,
                    description="Stock symbol",
                )
            ],
            optional_params=[
                EndpointParam(
                    name="date",
                    location=ParamLocation.QUERY,
                    param_type=ParamType.DATE,
                    required=False,
                    description="Historical date",
                )
            ],
            response_model=dict,  # Simplified for testing
            arg_model=None,
        ),
        "get_market_summary": Endpoint(
            name="get_market_summary",
            path="market/summary",
            version=APIVersion.STABLE,
            url_type=URLType.API,
            method=HTTPMethod.GET,
            description="Get market summary",
            mandatory_params=[],
            optional_params=None,
            response_model=dict,
            arg_model=None,
        ),
    }


@pytest.fixture
def rule(sample_endpoints) -> EndpointBasedRule:
    """Fixture providing EndpointBasedRule instance."""
    return EndpointBasedRule(sample_endpoints, SemanticCategory.MARKET_DATA)


class TestEndpointBasedRule:
    """Tests for EndpointBasedRule validation."""

    def test_initialization(self, rule: EndpointBasedRule) -> None:
        """Test basic initialization."""
        assert rule.expected_category == SemanticCategory.MARKET_DATA
        assert isinstance(rule.endpoint_prefixes, set)

    def test_endpoint_prefixes(self, rule: EndpointBasedRule) -> None:
        """Test endpoint prefix generation."""
        prefixes = rule.endpoint_prefixes
        assert "get_market_price" in prefixes
        assert "get_market_summary" in prefixes
        assert "market_price" in prefixes
        assert "market" in prefixes

    @pytest.mark.parametrize(
        "method_name,category,expected_valid",
        [
            ("get_market_price", SemanticCategory.MARKET_DATA, True),
            ("get_market_summary", SemanticCategory.MARKET_DATA, True),
            ("get_invalid_method", SemanticCategory.MARKET_DATA, False),
            ("get_market_price", SemanticCategory.ALTERNATIVE_DATA, False),
        ],
    )
    def test_validate(
        self,
        rule: EndpointBasedRule,
        method_name: str,
        category: SemanticCategory,
        expected_valid: bool,
    ) -> None:
        """Test method validation."""
        is_valid, message = rule.validate(method_name, category)
        assert is_valid == expected_valid
        if not expected_valid:
            assert message != ""

    def test_validate_parameters_valid(self, rule: EndpointBasedRule) -> None:
        """Test parameter validation with valid parameters."""
        params = {
            "symbol": "AAPL",
            "date": date(2024, 1, 1),
        }
        is_valid, message = rule.validate_parameters("get_market_price", params)
        assert is_valid
        assert message == ""

    def test_validate_parameters_invalid_param(self, rule: EndpointBasedRule) -> None:
        """Test parameter validation with invalid parameter."""
        params = {
            "symbol": "AAPL",
            "invalid_param": "value",
        }
        is_valid, message = rule.validate_parameters("get_market_price", params)
        assert not is_valid
        assert "Invalid parameters" in message

    def test_validate_parameters_missing_mandatory(
        self, rule: EndpointBasedRule
    ) -> None:
        """Test parameter validation with missing mandatory parameter."""
        params = {
            "date": date(2024, 1, 1),  # Missing required 'symbol'
        }
        is_valid, message = rule.validate_parameters("get_market_price", params)
        assert not is_valid
        assert "Missing mandatory parameters" in message

    def test_get_parameter_requirements(self, rule: EndpointBasedRule) -> None:
        """Test getting parameter requirements."""
        # Test for market price endpoint which has parameters
        market_price_reqs = rule.get_parameter_requirements("get_market_price")

        if market_price_reqs is not None:
            assert isinstance(market_price_reqs, dict)
            # Should have patterns for symbol and date parameters
            assert "symbol" in market_price_reqs
            assert "date" in market_price_reqs
            # Verify pattern structure
            for _, patterns in market_price_reqs.items():
                assert isinstance(patterns, list)
                assert all(isinstance(pattern, str) for pattern in patterns)

        # Test for market summary endpoint which has no parameters
        summary_reqs = rule.get_parameter_requirements("get_market_summary")
        assert summary_reqs is None  # Should be None as there are no parameters

        # Test for non-existent endpoint
        invalid_reqs = rule.get_parameter_requirements("non_existent_endpoint")
        assert invalid_reqs is None

    def test_validate_parameters_invalid_endpoint(
        self, rule: EndpointBasedRule
    ) -> None:
        """Test parameter validation for non-existent endpoint."""
        is_valid, message = rule.validate_parameters("non_existent", {})
        assert not is_valid
        assert "No endpoint found" in message
