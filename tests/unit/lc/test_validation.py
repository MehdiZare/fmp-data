# tests/unit/lc/test_validation.py
"""Behavioural tests for ``fmp_data.lc.validation``.

``fmp_data.lc.registry`` ships its own, unrelated ``ValidationRuleRegistry``
(covered by ``test_validation_registry.py``). Everything here exercises the
standalone rule framework in ``fmp_data/lc/validation.py``: the
``CommonValidationRule`` template methods and the registry that dispatches to
them.

Note for future readers: nothing inside ``fmp_data`` imports this module — it
is importable public API that only third-party subclasses reach. The tests
below therefore pin the *published* contract, not any internal call path.
"""

from datetime import date
import logging
import re
from typing import ClassVar

import pytest

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import (
    CommonValidationRule,
    ValidationRule,
    ValidationRuleRegistry,
)

# Mirrors the ClassVar declared on CommonValidationRule.
PatternMap = dict[str, list[str] | dict[str, list[str] | str | int]]

ISO_DATE = r"^\d{4}-\d{2}-\d{2}$"
US_DATE = r"^\d{2}/\d{2}/\d{4}$"


class MarketRule(CommonValidationRule):
    """Market rule with flat (list-shaped) date patterns."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": [ISO_DATE]}

    ENDPOINTS: ClassVar[dict[str, tuple[str, str]]] = {
        "get_quote": ("quote", "read"),
        "historical": ("price", "read"),
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.MARKET_DATA

    @property
    def endpoint_prefixes(self) -> set[str]:
        return {"get_quote", "historical"}

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        return cls.ENDPOINTS.get(method_name)


class NestedCommonRule(MarketRule):
    """Date patterns nested under the ``common`` key."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": {"common": [ISO_DATE]}}


class NestedWithoutCommonRule(MarketRule):
    """Nested date patterns that never declare a ``common`` bucket."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": {"quarterly": [ISO_DATE]}}


class NestedBadCommonRule(MarketRule):
    """``common`` holds a bare pattern instead of a list of patterns."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": {"common": ISO_DATE}}


class NoPatternsRule(MarketRule):
    """Endpoint table but no parameter patterns at all."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {}


class UnanchoredDateRule(MarketRule):
    """Date pattern without a trailing anchor."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": [r"\d{4}-\d{2}-\d{2}"]}


class MultiFormatDateRule(MarketRule):
    """Two alternative date formats; a value need only satisfy one."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": [ISO_DATE, US_DATE]}


class UncompilableDateRule(MarketRule):
    """A pattern that ``re`` cannot compile at all."""

    PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": ["(unclosed"]}


class MinimalRule(CommonValidationRule):
    """Only implements the one abstract member; everything else is inherited."""

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.ECONOMIC


class EconomicRule(MinimalRule):
    """Economic rule owning a single, specific prefix."""

    @property
    def endpoint_prefixes(self) -> set[str]:
        return {"get_gdp"}


class BroadRule(MinimalRule):
    """Economic rule with a prefix broad enough to swallow other groups."""

    @property
    def endpoint_prefixes(self) -> set[str]:
        return {"get_"}


class SnakeCaseRule(CommonValidationRule):
    """Adds a method-name check on top of the inherited category check."""

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.MARKET_DATA

    @property
    def endpoint_prefixes(self) -> set[str]:
        return {"get_"}

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        is_valid, message = super().validate(method_name, category)
        if not is_valid:
            return False, message
        if not method_name.islower():
            return False, f"{method_name} is not snake_case"
        return True, ""


class NoRequirementsRule(MarketRule):
    """Market rule that never publishes parameter requirements."""

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        return None


@pytest.fixture
def market_rule() -> MarketRule:
    return MarketRule()


@pytest.fixture
def registry() -> ValidationRuleRegistry:
    return ValidationRuleRegistry()


class TestAbstractContract:
    """The ABC layer must refuse incomplete implementations."""

    def test_validation_rule_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError, match="abstract"):
            ValidationRule()  # type: ignore[abstract]

    def test_subclass_without_expected_category_is_abstract(self) -> None:
        class HalfBakedRule(CommonValidationRule):
            pass

        with pytest.raises(TypeError) as exc_info:
            HalfBakedRule()  # type: ignore[abstract]

        assert "expected_category" in str(exc_info.value)


class TestCommonValidationRuleDefaults:
    """Inherited defaults of CommonValidationRule."""

    def test_endpoint_prefixes_default_to_empty(self) -> None:
        assert MinimalRule().endpoint_prefixes == set()

    def test_get_endpoint_info_defaults_to_none(self) -> None:
        assert MinimalRule.get_endpoint_info("get_gdp") is None

    def test_only_historical_has_parameter_requirements(self) -> None:
        rule = MinimalRule()

        assert rule.get_parameter_requirements("get_gdp") is None
        assert rule.get_parameter_requirements("historical") == {
            "start_date": [],
            "end_date": [],
        }


class TestValidateCategory:
    """CommonValidationRule.validate compares categories only."""

    def test_matching_category_is_accepted(self, market_rule: MarketRule) -> None:
        assert market_rule.validate("get_quote", SemanticCategory.MARKET_DATA) == (
            True,
            "",
        )

    def test_unknown_method_still_passes_the_default_check(
        self, market_rule: MarketRule
    ) -> None:
        """The default rule never looks at the method name."""
        assert market_rule.validate(
            "method_that_does_not_exist", SemanticCategory.MARKET_DATA
        ) == (True, "")

    def test_mismatched_category_is_rejected(self, market_rule: MarketRule) -> None:
        is_valid, message = market_rule.validate("get_quote", SemanticCategory.ECONOMIC)

        assert not is_valid
        # The message interpolates the enum *member*, not ``.value`` — on
        # Python >= 3.11 that renders as ``SemanticCategory.MARKET_DATA``.
        assert message in (
            "Expected SemanticCategory.MARKET_DATA, got SemanticCategory.ECONOMIC",
            "Expected Market Data, got Economic Data",
        )

    def test_subclass_can_extend_validate(self) -> None:
        rule = SnakeCaseRule()

        assert rule.validate("get_quote", SemanticCategory.MARKET_DATA) == (True, "")
        assert rule.validate("get_Quote", SemanticCategory.MARKET_DATA) == (
            False,
            "get_Quote is not snake_case",
        )


class TestValidateParameters:
    """CommonValidationRule.validate_parameters."""

    def test_unknown_method_is_rejected(self, market_rule: MarketRule) -> None:
        assert market_rule.validate_parameters("get_nope", {}) == (
            False,
            "Invalid method name: get_nope",
        )

    def test_method_without_requirements_accepts_anything(
        self, market_rule: MarketRule
    ) -> None:
        assert market_rule.validate_parameters(
            "get_quote", {"symbol": "AAPL", "limit": 5}
        ) == (True, "")

    def test_valid_dates_are_accepted(self, market_rule: MarketRule) -> None:
        assert market_rule.validate_parameters(
            "historical", {"start_date": "2024-01-01", "end_date": "2024-03-31"}
        ) == (True, "")

    def test_requirements_do_not_make_parameters_mandatory(
        self, market_rule: MarketRule
    ) -> None:
        """Requirements constrain format, never presence.

        ``get_parameter_requirements`` names ``start_date``/``end_date``, but
        the check iterates the *supplied* parameters, so omitting them entirely
        is accepted.
        """
        assert market_rule.get_parameter_requirements("historical") == {
            "start_date": [ISO_DATE],
            "end_date": [ISO_DATE],
        }
        assert market_rule.validate_parameters("historical", {}) == (True, "")

    def test_any_declared_pattern_may_match(self) -> None:
        """Patterns are alternatives: matching the second one is enough."""
        rule = MultiFormatDateRule()

        assert rule.validate_parameters("historical", {"start_date": "2024-01-01"}) == (
            True,
            "",
        )
        assert rule.validate_parameters("historical", {"start_date": "01/31/2024"}) == (
            True,
            "",
        )
        assert rule.validate_parameters(
            "historical", {"start_date": "31 Jan 2024"}
        ) == (False, "Invalid value for parameter 'start_date': 31 Jan 2024")

    def test_uncompilable_pattern_escapes_as_re_error(self) -> None:
        """A malformed pattern crashes the caller instead of failing validation.

        ``re.match`` is called without a guard, so a bad pattern surfaces as
        ``re.error`` rather than the ``(False, "Invalid value ...")`` tuple the
        signature promises. Callers cannot distinguish "rejected" from
        "misconfigured" without catching this.
        """
        rule = UncompilableDateRule()

        with pytest.raises(re.error):
            rule.validate_parameters("historical", {"start_date": "2024-01-01"})

    def test_invalid_date_is_rejected_by_name(self, market_rule: MarketRule) -> None:
        assert market_rule.validate_parameters(
            "historical", {"start_date": "2024/01/01"}
        ) == (False, "Invalid value for parameter 'start_date': 2024/01/01")

    def test_first_invalid_parameter_short_circuits(
        self, market_rule: MarketRule
    ) -> None:
        is_valid, message = market_rule.validate_parameters(
            "historical", {"start_date": "yesterday", "end_date": "tomorrow"}
        )

        assert not is_valid
        assert message == "Invalid value for parameter 'start_date': yesterday"

    def test_unconstrained_parameters_are_ignored(
        self, market_rule: MarketRule
    ) -> None:
        assert market_rule.validate_parameters(
            "historical", {"symbol": "AAPL", "limit": "not-a-date"}
        ) == (True, "")

    def test_values_are_stringified_before_matching(
        self, market_rule: MarketRule
    ) -> None:
        assert market_rule.validate_parameters(
            "historical", {"start_date": date(2024, 1, 1)}
        ) == (True, "")
        assert market_rule.validate_parameters(
            "historical", {"start_date": 20240101}
        ) == (False, "Invalid value for parameter 'start_date': 20240101")

    def test_empty_pattern_list_rejects_every_value(self) -> None:
        """A rule whose date patterns cannot be resolved rejects all dates."""
        rule = NestedWithoutCommonRule()

        assert rule.get_parameter_requirements("historical") == {
            "start_date": [],
            "end_date": [],
        }
        assert rule.validate_parameters("historical", {"start_date": "2024-01-01"}) == (
            False,
            "Invalid value for parameter 'start_date': 2024-01-01",
        )

    def test_matching_is_prefix_only(self) -> None:
        """``re.match`` is not ``fullmatch``: trailing junk survives."""
        rule = UnanchoredDateRule()

        assert rule.validate_parameters(
            "historical", {"start_date": "2024-01-01' OR 1=1"}
        ) == (True, "")


class TestHistoricalPatternShapes:
    """_build_historical_patterns handles each PARAMETER_PATTERNS shape."""

    @pytest.mark.parametrize(
        ("rule", "expected"),
        [
            pytest.param(MarketRule(), [ISO_DATE], id="flat-list"),
            pytest.param(NestedCommonRule(), [ISO_DATE], id="nested-common-list"),
            pytest.param(NestedWithoutCommonRule(), [], id="nested-without-common"),
            pytest.param(NestedBadCommonRule(), [], id="nested-common-not-a-list"),
            pytest.param(NoPatternsRule(), [], id="no-date-key"),
        ],
    )
    def test_start_and_end_date_patterns(
        self, rule: CommonValidationRule, expected: list[str]
    ) -> None:
        assert rule.get_parameter_requirements("historical") == {
            "start_date": expected,
            "end_date": expected,
        }

    def test_non_historical_methods_have_no_requirements(
        self, market_rule: MarketRule
    ) -> None:
        assert market_rule.get_parameter_requirements("get_quote") is None

    def test_the_historical_hook_is_an_exact_name_match(
        self, market_rule: MarketRule
    ) -> None:
        """Only the literal name ``historical`` gets date requirements."""
        assert market_rule.get_parameter_requirements("historical_chart") is None
        assert market_rule.get_parameter_requirements("Historical") is None

    def test_returned_patterns_alias_the_class_level_config(self) -> None:
        """The result is live class state, so mutating it rewrites the rule.

        Both date keys hand back the *same* list object that lives on the
        class, rather than a copy. A caller that edits the requirements it was
        handed silently reconfigures every later validation, which is why the
        result has to be treated as read-only.
        """

        class ScratchRule(MarketRule):
            PARAMETER_PATTERNS: ClassVar[PatternMap] = {"date": [ISO_DATE]}

        rule = ScratchRule()
        requirements = rule.get_parameter_requirements("historical")

        assert requirements is not None
        assert requirements["start_date"] is ScratchRule.PARAMETER_PATTERNS["date"]
        assert requirements["end_date"] is requirements["start_date"]

        requirements["start_date"].clear()

        assert ScratchRule.PARAMETER_PATTERNS["date"] == []
        assert rule.get_parameter_requirements("historical") == {
            "start_date": [],
            "end_date": [],
        }
        assert rule.validate_parameters("historical", {"start_date": "2024-01-01"}) == (
            False,
            "Invalid value for parameter 'start_date': 2024-01-01",
        )
        # The damage is confined to the subclass that owns the list.
        assert MarketRule.PARAMETER_PATTERNS["date"] == [ISO_DATE]


class TestRegistryValidateCategory:
    """ValidationRuleRegistry.validate_category dispatch."""

    def test_register_rule_logs_the_class_name(
        self, registry: ValidationRuleRegistry, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.DEBUG, logger="fmp_data.lc.validation"):
            registry.register_rule(MarketRule())

        # Registration is a debug-level event: it must be traceable without
        # being promoted into the noise every consumer sees by default.
        assert ("DEBUG", "Registered validation rule: MarketRule") in [
            (record.levelname, record.getMessage()) for record in caplog.records
        ]
        # ...and the registration actually took effect.
        assert (
            registry.get_expected_category("get_quote") == SemanticCategory.MARKET_DATA
        )

    def test_category_with_no_rules_is_rejected(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(EconomicRule())

        assert registry.validate_category(
            "get_quote", SemanticCategory.MARKET_DATA
        ) == (False, "No rules found for category Market Data")

    def test_unmatched_method_is_rejected(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.validate_category(
            "mystery_method", SemanticCategory.MARKET_DATA
        ) == (
            False,
            "No matching rule found for mystery_method in category Market Data",
        )

    def test_matching_rule_is_accepted(self, registry: ValidationRuleRegistry) -> None:
        registry.register_rule(MarketRule())

        assert registry.validate_category(
            "get_quote", SemanticCategory.MARKET_DATA
        ) == (True, "")

    def test_registry_returns_the_rules_own_verdict(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(SnakeCaseRule())

        assert registry.validate_category(
            "get_Quote", SemanticCategory.MARKET_DATA
        ) == (False, "get_Quote is not snake_case")

    def test_mismatch_names_the_owning_category(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())
        registry.register_rule(EconomicRule())

        assert registry.validate_category("get_gdp", SemanticCategory.MARKET_DATA) == (
            False,
            "Category mismatch: endpoint get_gdp belongs to Economic Data, "
            "not Market Data",
        )

    def test_first_registered_prefix_wins(
        self, registry: ValidationRuleRegistry
    ) -> None:
        """A broad prefix registered first claims another group's endpoint.

        Current behaviour: ``get_quote`` is owned by ``MarketRule`` (exact
        prefix) but ``BroadRule``'s ``get_`` is scanned first, so the market
        endpoint is reported as belonging to Economic Data.

        This is the #122 defect that ``fmp_data.lc.registry`` fixed by picking
        the longest matching prefix; this module still scans first-match. If
        it is ever fixed here too, invert this assertion rather than deleting
        it — the point is that ownership must not depend on registration order.
        """
        registry.register_rule(BroadRule())
        registry.register_rule(MarketRule())

        assert registry.validate_category(
            "get_quote", SemanticCategory.MARKET_DATA
        ) == (
            False,
            "Category mismatch: endpoint get_quote belongs to Economic Data, "
            "not Market Data",
        )


class TestRegistryParameterRequirements:
    """ValidationRuleRegistry parameter lookups."""

    def test_requirements_are_returned_for_the_category(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.get_parameter_requirements(
            "historical", SemanticCategory.MARKET_DATA
        ) == ({"start_date": [ISO_DATE], "end_date": [ISO_DATE]}, "")

    def test_rules_returning_none_are_skipped(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(NoRequirementsRule())
        registry.register_rule(MarketRule())

        assert registry.get_parameter_requirements(
            "historical", SemanticCategory.MARKET_DATA
        ) == ({"start_date": [ISO_DATE], "end_date": [ISO_DATE]}, "")

    def test_missing_requirements_are_reported(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.get_parameter_requirements(
            "get_quote", SemanticCategory.MARKET_DATA
        ) == (None, "No parameter requirements found for get_quote")

    def test_other_categories_are_not_consulted(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.get_parameter_requirements(
            "historical", SemanticCategory.ECONOMIC
        ) == (None, "No parameter requirements found for historical")


class TestRegistryValidateParameters:
    """ValidationRuleRegistry.validate_parameters delegation."""

    def test_delegates_to_the_category_rule(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.validate_parameters(
            "historical", SemanticCategory.MARKET_DATA, {"start_date": "2024-13-99x"}
        ) == (False, "Invalid value for parameter 'start_date': 2024-13-99x")

    def test_only_the_first_rule_of_a_category_is_used(
        self, registry: ValidationRuleRegistry
    ) -> None:
        """Registration order decides the verdict, not endpoint ownership."""
        registry.register_rule(SnakeCaseRule())  # no endpoint table
        registry.register_rule(MarketRule())  # owns "historical"

        assert registry.validate_parameters(
            "historical", SemanticCategory.MARKET_DATA, {"start_date": "2024-01-01"}
        ) == (False, "Invalid method name: historical")

    def test_unregistered_category_passes_silently(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(EconomicRule())

        assert registry.validate_parameters(
            "historical", SemanticCategory.MARKET_DATA, {"start_date": "nonsense"}
        ) == (True, "")


class TestRegistryExpectedCategory:
    """ValidationRuleRegistry.get_expected_category."""

    def test_known_prefixes_resolve(self, registry: ValidationRuleRegistry) -> None:
        registry.register_rule(MarketRule())
        registry.register_rule(EconomicRule())

        assert (
            registry.get_expected_category("historical") == SemanticCategory.MARKET_DATA
        )
        assert registry.get_expected_category("get_gdp") == SemanticCategory.ECONOMIC

    def test_unknown_method_has_no_category(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MarketRule())

        assert registry.get_expected_category("get_dividends") is None

    def test_rule_without_prefixes_never_matches(
        self, registry: ValidationRuleRegistry
    ) -> None:
        registry.register_rule(MinimalRule())

        assert registry.get_expected_category("get_gdp") is None

    def test_broad_prefix_shadows_specific_rule(
        self, registry: ValidationRuleRegistry
    ) -> None:
        """Same first-match defect as ``validate_category``.

        Both entry points agree today only because both are wrong in the same
        way; see ``test_first_registered_prefix_wins``.
        """
        registry.register_rule(BroadRule())
        registry.register_rule(MarketRule())

        assert registry.get_expected_category("get_quote") == SemanticCategory.ECONOMIC
