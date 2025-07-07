# tests/lc/test_models.py
from pydantic import ValidationError
import pytest

from fmp_data.lc.models import (
    EndpointSemantics,
    ParameterHint,
    ResponseFieldInfo,
    SemanticCategory,
)


def test_parameter_hint_validation():
    """Test ParameterHint model validation"""
    from pydantic import ValidationError

    from fmp_data.lc.models import ParameterHint

    # Valid parameter hint
    hint = ParameterHint(
        natural_names=["symbol", "ticker"],
        extraction_patterns=[r"\b[A-Z]{1,5}\b"],
        examples=["AAPL", "GOOGL"],
        context_clues=["stock symbol", "company ticker"],
    )
    assert hint.natural_names == ["symbol", "ticker"]
    assert len(hint.extraction_patterns) == 1

    # Test invalid case with None values
    with pytest.raises(ValidationError):
        ParameterHint(
            natural_names=None,  # type error - must be list
            extraction_patterns=None,
            examples=None,
            context_clues=None,
        )


def test_response_field_info():
    """Test ResponseFieldInfo model validation"""
    # Valid response field info
    info = ResponseFieldInfo(
        description="Stock price",
        examples=["100.50", "202.75"],
        related_terms=["value", "cost"],
    )
    assert info.description == "Stock price"
    assert len(info.examples) == 2

    # Invalid - missing required fields
    with pytest.raises(ValidationError):
        ResponseFieldInfo()


def test_endpoint_semantics():
    """Test EndpointSemantics model validation"""
    # Valid endpoint semantics
    semantics = EndpointSemantics(
        client_name="market",
        method_name="get_price",
        natural_description="Get current stock price",
        example_queries=["What's the price of AAPL?"],
        related_terms=["stock price", "quote"],
        category=SemanticCategory.MARKET_DATA,
        parameter_hints={
            "symbol": ParameterHint(
                natural_names=["symbol"],
                extraction_patterns=[r"\b[A-Z]{1,5}\b"],
                examples=["AAPL"],
                context_clues=["stock symbol"],
            )
        },
        response_hints={
            "price": ResponseFieldInfo(
                description="Current stock price",
                examples=["100.50"],
                related_terms=["value"],
            )
        },
        use_cases=["Price checking"],
    )

    assert semantics.client_name == "market"
    assert semantics.category == SemanticCategory.MARKET_DATA

    # Invalid - missing required fields
    with pytest.raises(ValidationError):
        EndpointSemantics()
