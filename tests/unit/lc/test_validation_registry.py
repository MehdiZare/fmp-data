from enum import Enum, IntEnum
import re
from typing import Any

import pytest

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.registry import (
    EndpointBasedRule,
    ValidationRuleRegistry,
    get_endpoint_groups,
)
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

    def test_validate_category_prefers_longest_prefix(
        self,
        market_endpoints: dict[str, Endpoint[Any]],
        alternative_endpoints: dict[str, Endpoint[Any]],
    ) -> None:
        """A more specific prefix wins over a shorter one registered earlier.

        Endpoint-map keys are method names, so the owning group always supplies
        an exact match. Scanning for the *first* prefix hit instead lets an
        unrelated group with a shorter prefix claim the endpoint — the defect
        behind issue #122, where company's ``get_price_target`` swallowed
        intelligence's ``get_price_target_news``.
        """
        registry = ValidationRuleRegistry()
        # Shorter, unrelated prefix registered first.
        registry.register_rule(
            EndpointBasedRule(
                {"get_market": market_endpoints["get_market_data"]},
                SemanticCategory.MARKET_DATA,
            )
        )
        registry.register_rule(
            EndpointBasedRule(
                {"get_market_data_feed": market_endpoints["get_market_data"]},
                SemanticCategory.ALTERNATIVE_DATA,
            )
        )

        is_valid, message = registry.validate_category(
            "get_market_data_feed", SemanticCategory.ALTERNATIVE_DATA
        )
        assert is_valid, message

        is_valid, message = registry.validate_category(
            "get_market_data_feed", SemanticCategory.MARKET_DATA
        )
        assert not is_valid
        assert "Category mismatch" in message

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

    def test_get_expected_category_prefers_longest_prefix(
        self,
        market_endpoints: dict[str, Endpoint[Any]],
        alternative_endpoints: dict[str, Endpoint[Any]],
    ) -> None:
        """Ownership must not depend on which public method you ask.

        ``validate_category`` picks the most specific prefix; this method has to
        agree, or the same endpoint belongs to two different categories
        depending on the entry point.
        """
        registry = ValidationRuleRegistry()
        # Shorter, unrelated prefix registered first.
        registry.register_rule(
            EndpointBasedRule(
                {"get_market": market_endpoints["get_market_data"]},
                SemanticCategory.MARKET_DATA,
            )
        )
        registry.register_rule(
            EndpointBasedRule(
                {"get_market_data_feed": market_endpoints["get_market_data"]},
                SemanticCategory.ALTERNATIVE_DATA,
            )
        )

        assert (
            registry.get_expected_category("get_market_data_feed")
            == SemanticCategory.ALTERNATIVE_DATA
        )


def test_every_emitted_pattern_compiles() -> None:
    """Every regex the registry can emit must compile.

    Patterns from this family are consumed by an uncaught ``re.match`` in
    ``fmp_data/lc/validation.py``, so an uncompilable pattern is a crash
    waiting for the first caller that reaches it.
    """
    uncompilable: list[tuple[str, str, str]] = []
    checked = 0
    for group_name, config in get_endpoint_groups().items():
        rule = EndpointBasedRule(config["endpoint_map"], config["category"])
        for method_name in config["endpoint_map"]:
            requirements = rule.get_parameter_requirements(method_name) or {}
            for param_name, patterns in requirements.items():
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                        checked += 1
                    except re.error as exc:
                        uncompilable.append(
                            (f"{group_name}.{method_name}", param_name, str(exc))
                        )
    assert not uncompilable, f"uncompilable patterns: {uncompilable}"
    assert checked > 100, (
        f"guard checked only {checked} patterns — is it still reaching the registry?"
    )


def test_enum_valid_values_use_wire_value_not_repr() -> None:
    """Enum members must contribute their .value, not their repr.

    ``economics.get_economic_indicators`` declares valid_values as
    EconomicIndicatorType members. ``str(member)`` yields
    'EconomicIndicatorType.GDP', so the pattern would compile and then
    reject the very values it is supposed to accept.
    """
    from fmp_data.economics.endpoints import ECONOMIC_INDICATORS
    from fmp_data.economics.schema import EconomicIndicatorType

    rule = EndpointBasedRule(
        {"get_economic_indicators": ECONOMIC_INDICATORS},
        SemanticCategory.ECONOMIC,
    )
    requirements = rule.get_parameter_requirements("get_economic_indicators")
    assert requirements is not None
    patterns = requirements["name"]

    assert "EconomicIndicatorType." not in patterns[0]
    for member in EconomicIndicatorType:
        assert any(re.match(pattern, member.value) for pattern in patterns), (
            f"{member.value!r} rejected by {patterns}"
        )


class TestValidValuesNormalisation:
    """EndpointParam unwraps Enum members in valid_values at construction."""

    def test_enum_members_are_unwrapped_to_wire_values(self) -> None:
        from fmp_data.economics.schema import EconomicIndicatorType

        param = EndpointParam(
            name="name",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Indicator",
            valid_values=list(EconomicIndicatorType),
        )

        assert param.valid_values == [m.value for m in EconomicIndicatorType]
        assert not any(isinstance(v, Enum) for v in param.valid_values or [])

    def test_non_enum_values_keep_their_native_type(self) -> None:
        """Integer valid_values must stay ints.

        ``validate_value`` compares the *converted* request value against
        this list, and an INTEGER param converts to ``int``. Stringifying
        the list here would make every such comparison fail.
        """
        param = EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            description="Fiscal quarter",
            valid_values=[1, 2, 3, 4],
        )

        assert param.valid_values == [1, 2, 3, 4]
        assert param.validate_value("2") == 2

    def test_none_valid_values_stays_none(self) -> None:
        param = EndpointParam(
            name="symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Symbol",
        )

        assert param.valid_values is None

    def test_non_str_enum_yields_a_compilable_pattern(self) -> None:
        """A non-str Enum must not reach re.escape as an int.

        ``re.escape`` raises TypeError on a non-str, so an IntEnum in
        valid_values used to crash pattern generation outright.
        """

        class Quarter(IntEnum):
            Q1 = 1
            Q2 = 2

        param = EndpointParam(
            name="quarter",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            description="Fiscal quarter",
            valid_values=list(Quarter),
        )
        patterns = EndpointBasedRule._get_type_pattern(
            param.param_type.value, param.valid_values
        )

        for pattern in patterns:
            re.compile(pattern)
        assert any(re.match(p, "1") for p in patterns)
        assert not any(re.match(p, "Quarter.Q1") for p in patterns)

    def test_get_type_pattern_tolerates_raw_enum_from_direct_callers(self) -> None:
        """The staticmethod is public enough to be called with raw members."""

        class Quarter(IntEnum):
            Q1 = 1

        patterns = EndpointBasedRule._get_type_pattern("string", list(Quarter))

        for pattern in patterns:
            re.compile(pattern)
        assert any(re.match(p, "1") for p in patterns)
