# tests/lc/test_validation.py
from typing import ClassVar

import pytest

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import (
    CommonValidationRule,
    ValidationRule,
    ValidationRuleRegistry,
)


class TestValidationRule(CommonValidationRule):
    """
    Test implementation of CommonValidationRule for Market Data.

    Fixes:
      - endpoint_prefixes now returns all 'prefix + operation' combos
      - get_endpoint_info properly parses subcategory, prefix, operation
      - get_parameter_requirements returns parameter patterns for recognized endpoints
    """

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Market": ("get_market_", ["data", "summary", "stats"]),
        "Price": ("get_price_", ["history", "current", "forecast"]),
        "News": ("get_", ["news", "articles", "press_releases"]),
    }

    # Must exactly match CommonValidationRule's signature:
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str]] | dict[str, dict[str, list[str] | str | int]]
    ] = {
        # top-level "date" -> list of regex
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        # top-level "symbol" -> list of regex
        "symbol": [r"^[A-Z]{1,5}$"],
        # sub-dict "market_specific"
        "market_specific": {
            "exchange": [r"^(NYSE|NASDAQ)$"],
            "sector": [r"^[A-Za-z\s]+$"],
        },
        # sub-dict "price_specific"
        "price_specific": {
            "interval": [r"^(1min|5min|15min|30min|1hour|daily)$"],
        },
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.MARKET_DATA

    @property
    def endpoint_prefixes(self) -> set[str]:
        """
        Build a set of valid full method names like:
          get_market_data, get_market_summary, get_price_history, etc.
        """
        prefixes: set[str] = set()
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            for op in operations:
                prefixes.add(f"{prefix}{op}")
        return prefixes

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        """
        Return (subcategory, operation), e.g. ("Market", "data") for "get_market_data".
        """
        for subcat, (prefix, operations) in cls.METHOD_GROUPS.items():
            # exact match if method_name is just one of the operations
            if method_name in operations:
                return subcat, method_name
            # else check if method_name is prefix + operation
            if prefix and method_name.startswith(prefix):
                possible_op = method_name[len(prefix) :]
                if possible_op in operations:
                    return subcat, possible_op
        return None

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """
        Override validate method to ensure strict category matching and
        check METHOD_GROUPS for recognized endpoints.
        """
        if category != self.expected_category:
            return (
                False,
                f"Category mismatch: expected {self.expected_category}, got {category}",
            )

        # Check method_name against METHOD_GROUPS
        info = self.get_endpoint_info(method_name)
        if not info:
            return False, f"Method {method_name} does not match any expected patterns"
        return True, ""

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Return a dictionary of parameter regex lists for recognized endpoints.
        E.g. "get_market_data" -> includes top-level "date"/"symbol" +
        subcategory-specific entries.

        Args:
            method_name: The method name for which we want parameter requirements.

        Returns:
            dict[str, list[str]] | None: A dict of parameters (keys) and
            regex patterns (list[str]) if recognized; otherwise None.
        """
        info = self.get_endpoint_info(method_name)
        if not info:
            return None

        subcat, _ = info
        base_patterns: dict[str, list[str]] = {}

        self._add_top_level_patterns(base_patterns)
        self._add_subcategory_patterns(base_patterns, subcat)

        return base_patterns if base_patterns else None

    def _add_top_level_patterns(self, base_patterns: dict[str, list[str]]) -> None:
        """Add global top-level patterns like 'date', 'symbol' if they exist."""
        for key in ("date", "symbol"):
            pattern_value = self.PARAMETER_PATTERNS.get(key)
            if isinstance(pattern_value, list):
                base_patterns[key] = pattern_value

    def _add_subcategory_patterns(
        self, base_patterns: dict[str, list[str]], subcat: str
    ) -> None:
        """
        For subcategories like 'market', 'price', 'news', add
        respective patterns from PARAMETER_PATTERNS.
        """
        subcat_map = {
            "market": "market_specific",
            "price": "price_specific",
            "news": "news_specific",  # add if you have news-specific patterns
        }
        subcat_key = subcat_map.get(subcat.lower())
        if not subcat_key:
            return

        subdict = self.PARAMETER_PATTERNS.get(subcat_key)
        if isinstance(subdict, dict):
            for param_name, patterns in subdict.items():
                if isinstance(patterns, list):
                    base_patterns[param_name] = patterns


class TestInstitutionalRule(CommonValidationRule):
    """
    Test implementation of CommonValidationRule for Institutional Data.
    """

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Institutional": ("get_institutional_", ["data", "holdings"]),
    }

    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str]] | dict[str, dict[str, list[str] | str | int]]
    ] = {
        # Potential future patterns:
        # "date": [r"^\d{4}-\d{2}-\d{2}$"],
        # "institution_specific": { "fund": [...], ... }
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.INSTITUTIONAL

    @property
    def endpoint_prefixes(self) -> set[str]:
        """
        Build a set of valid full method names like:
          get_institutional_data, get_institutional_holdings
        """
        prefixes: set[str] = set()
        for _, (prefix, operations) in self.METHOD_GROUPS.items():
            for op in operations:
                prefixes.add(f"{prefix}{op}")
        return prefixes

    @classmethod
    def get_endpoint_info(cls, method_name: str) -> tuple[str, str] | None:
        for subcat, (prefix, ops) in cls.METHOD_GROUPS.items():
            if method_name in ops:
                return subcat, method_name
            if prefix and method_name.startswith(prefix):
                possible_op = method_name[len(prefix) :]
                if possible_op in ops:
                    return subcat, possible_op
        return None


#
# Below: existing tests reorganized for clarity or left as-is
#


@pytest.fixture
def market_rule() -> TestValidationRule:
    """Pytest fixture that returns an instance of TestValidationRule (Market Data)."""
    return TestValidationRule()


@pytest.fixture
def institutional_rule() -> TestInstitutionalRule:
    """Pytest fixture that returns an instance of
    TestInstitutionalRule (Institutional Data)."""
    return TestInstitutionalRule()


class TestMarketValidationRule:
    """Tests specifically for the Market-based ValidationRule (TestValidationRule)."""

    def test_initialization(self, market_rule: TestValidationRule) -> None:
        assert isinstance(market_rule, ValidationRule)
        assert market_rule.expected_category == SemanticCategory.MARKET_DATA

    def test_endpoint_prefixes(self, market_rule: TestValidationRule) -> None:
        prefixes = market_rule.endpoint_prefixes
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

    @pytest.mark.parametrize(
        "method_name,category",
        [
            ("get_market_data", SemanticCategory.MARKET_DATA),
            ("get_price_history", SemanticCategory.MARKET_DATA),
            ("get_news", SemanticCategory.MARKET_DATA),
        ],
    )
    def test_validate_method_valid(
        self,
        market_rule: TestValidationRule,
        method_name: str,
        category: SemanticCategory,
    ) -> None:
        is_valid, message = market_rule.validate(method_name, category)
        assert is_valid is True
        assert message == ""

    @pytest.mark.parametrize(
        "method_name,category",
        [
            ("invalid_method", SemanticCategory.MARKET_DATA),
            ("get_market_invalid", SemanticCategory.MARKET_DATA),
            ("get_market_data", SemanticCategory.INSTITUTIONAL),
        ],
    )
    def test_validate_method_invalid(
        self,
        market_rule: TestValidationRule,
        method_name: str,
        category: SemanticCategory,
    ) -> None:
        is_valid, message = market_rule.validate(method_name, category)
        assert not is_valid
        assert message != ""

    @pytest.mark.parametrize(
        "method_name,expected_info",
        [
            ("get_market_data", ("Market", "data")),
            ("get_price_history", ("Price", "history")),
            ("get_news", ("News", "news")),
        ],
    )
    def test_get_endpoint_info_valid(
        self,
        market_rule: TestValidationRule,
        method_name: str,
        expected_info: tuple[str, str],
    ) -> None:
        info = market_rule.get_endpoint_info(method_name)
        assert info == expected_info

    @pytest.mark.parametrize(
        "method_name",
        ["invalid_method", "get_invalid", "unknown_endpoint"],
    )
    def test_get_endpoint_info_invalid(
        self, market_rule: TestValidationRule, method_name: str
    ) -> None:
        info = market_rule.get_endpoint_info(method_name)
        assert info is None

    def test_validate_parameters_valid(self, market_rule: TestValidationRule) -> None:
        valid_params = {
            "date": "2024-01-01",
            "symbol": "AAPL",
            "exchange": "NYSE",
            "interval": "1min",
        }
        is_valid, message = market_rule.validate_parameters(
            "get_market_data", valid_params
        )
        assert is_valid
        assert message == ""

    def test_validate_parameters_invalid(self, market_rule: TestValidationRule) -> None:
        invalid_params = {
            "date": "invalid-date",
            "symbol": "invalid-symbol",
            "exchange": "invalid-exchange",
            "interval": "invalid-interval",
        }
        is_valid, message = market_rule.validate_parameters(
            "get_market_data", invalid_params
        )
        assert not is_valid
        assert "Invalid value for parameter" in message

    def test_get_parameter_requirements(self, market_rule: TestValidationRule) -> None:
        # 'get_market_data' -> expect 'exchange' and 'sector' from market_specific
        market_reqs = market_rule.get_parameter_requirements("get_market_data")
        assert market_reqs is not None
        assert "exchange" in market_reqs
        assert "sector" in market_reqs

        # 'get_price_history' -> expect 'interval' from price_specific
        price_reqs = market_rule.get_parameter_requirements("get_price_history")
        assert price_reqs is not None
        assert "interval" in price_reqs

        invalid_reqs = market_rule.get_parameter_requirements("invalid_endpoint")
        assert invalid_reqs is None


class TestInstitutionalValidationRule:
    """Tests for the Institutional-based ValidationRule (TestInstitutionalRule)."""

    def test_institutional_rule_initialization(
        self, institutional_rule: TestInstitutionalRule
    ) -> None:
        assert isinstance(institutional_rule, ValidationRule)
        assert institutional_rule.expected_category == SemanticCategory.INSTITUTIONAL


class TestValidationRuleRegistrySuite:
    """Tests for ValidationRuleRegistry, ensuring it coordinates multiple rules."""

    def test_registry_with_multiple_rules(
        self, market_rule: TestValidationRule, institutional_rule: TestInstitutionalRule
    ) -> None:
        registry = ValidationRuleRegistry()
        registry.register_rule(market_rule)
        registry.register_rule(institutional_rule)

        # Market Data
        valid, message = registry.validate_category(
            "get_market_data", SemanticCategory.MARKET_DATA
        )
        assert valid and message == ""

        # Institutional
        valid, message = registry.validate_category(
            "get_institutional_data", SemanticCategory.INSTITUTIONAL
        )
        assert valid and message == ""

        # Category mismatch
        valid, message = registry.validate_category(
            "get_market_data", SemanticCategory.INSTITUTIONAL
        )
        assert not valid
        assert "Category mismatch" in message

        # Unknown method
        valid, message = registry.validate_category(
            "unknown_method", SemanticCategory.MARKET_DATA
        )
        assert not valid
        assert "No matching rule found" in message

        # Unknown category
        valid, message = registry.validate_category(
            "get_market_data", SemanticCategory.UNKNOWN_CATEGORY
        )
        assert not valid
        assert "No rules found for category" in message

    def test_get_expected_category(
        self, market_rule: TestValidationRule, institutional_rule: TestInstitutionalRule
    ) -> None:
        registry = ValidationRuleRegistry()
        registry.register_rule(market_rule)
        registry.register_rule(institutional_rule)

        assert (
            registry.get_expected_category("get_market_data")
            == SemanticCategory.MARKET_DATA
        )
        assert (
            registry.get_expected_category("get_institutional_data")
            == SemanticCategory.INSTITUTIONAL
        )
        assert registry.get_expected_category("invalid_endpoint") is None
