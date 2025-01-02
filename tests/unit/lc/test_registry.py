# tests/lc/test_registry.py
from unittest.mock import Mock

import pytest

from fmp_data.lc.models import EndpointInfo, EndpointSemantics, SemanticCategory
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.models import Endpoint, EndpointParam, ParamLocation, ParamType


@pytest.fixture
def valid_endpoint_info():
    """Create valid endpoint info for tests"""
    from fmp_data.lc.models import EndpointSemantics, ParameterHint, SemanticCategory
    from fmp_data.models import Endpoint, EndpointParam, ParamLocation, ParamType

    endpoint = Endpoint(
        name="get_stock_price",
        path="/price/{symbol}",
        description="Get stock price",
        mandatory_params=[
            EndpointParam(
                name="symbol",
                location=ParamLocation.PATH,
                param_type=ParamType.STRING,
                required=True,
                description="Stock symbol",
            )
        ],
        optional_params=[],
        response_model=dict,
    )

    # Create proper ParameterHint instance
    symbol_hint = ParameterHint(
        natural_names=["symbol", "ticker"],
        extraction_patterns=[r"\b[A-Z]{1,5}\b"],
        examples=["AAPL"],
        context_clues=["stock symbol"],
    )

    semantics = EndpointSemantics(
        client_name="market",
        method_name="get_stock_price",
        category=SemanticCategory.MARKET_DATA,
        natural_description="Get stock price",
        example_queries=["Get price for AAPL"],
        parameter_hints={"symbol": symbol_hint},  # Use the ParameterHint instance
        response_hints={},
        related_terms=["price", "quote"],
        use_cases=["Price checking"],
    )

    return endpoint, semantics


@pytest.fixture
def mock_endpoint():
    """Create a mock endpoint"""
    return Endpoint(
        name="get_stock_price",
        path="price/{symbol}",
        description="Get stock price",
        mandatory_params=[
            EndpointParam(
                name="symbol",
                location=ParamLocation.PATH,
                param_type=ParamType.STRING,
                required=True,
                description="Stock symbol",
            )
        ],
        optional_params=[],
        response_model=dict,
    )


@pytest.fixture
def mock_validation_rule():
    """Mock validation rule"""
    rule = Mock()
    rule.validate.return_value = (True, "")
    rule.endpoint_prefixes = {"get_stock_price"}
    rule.expected_category = "MARKET_DATA"
    return rule


@pytest.fixture
def mock_semantics():
    """Create mock endpoint semantics"""
    return EndpointSemantics(
        client_name="market",
        method_name="get_stock_price",
        natural_description="Get current stock price",
        example_queries=["What's the price of AAPL?"],
        related_terms=["stock price", "quote"],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={
            "symbol": {
                "natural_names": ["symbol"],
                "extraction_patterns": [r"\b[A-Z]{1,5}\b"],
                "examples": ["AAPL"],
                "context_clues": ["stock symbol"],
            }
        },
        response_hints={
            "price": {
                "description": "Current stock price",
                "examples": ["100.50"],
                "related_terms": ["value"],
            }
        },
        use_cases=["Price checking"],
    )


def test_endpoint_registry_initialization():
    """Test registry initialization"""
    registry = EndpointRegistry()
    assert len(registry.list_endpoints()) == 0


def test_endpoint_validation(mock_endpoint, mock_semantics, mock_validation_rule):
    """Test endpoint validation"""
    registry = EndpointRegistry()
    # Add mock validation rule
    registry._validation._rules = [mock_validation_rule]

    info = EndpointInfo(endpoint=mock_endpoint, semantics=mock_semantics)
    valid, error = registry.validate_endpoint(name="get_stock_price", info=info)
    assert valid is True
    assert error == ""


def test_endpoint_registration(valid_endpoint_info, mock_validation_rule):
    """Test endpoint registration"""
    registry = EndpointRegistry()
    # Add mock validation rule
    registry._validation._rules = [mock_validation_rule]

    endpoint, semantics = valid_endpoint_info
    registry.register("get_stock_price", endpoint, semantics)
    assert registry.get_endpoint("get_stock_price") is not None
