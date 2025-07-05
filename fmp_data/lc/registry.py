# fmp_data/lc/registry.py
"""
Endpoint registry for LangChain integration with
lazy imports to avoid circular dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import Logger
import re
from typing import TYPE_CHECKING, Any, TypedDict

from fmp_data.lc.models import EndpointInfo, EndpointSemantics, SemanticCategory
from fmp_data.logger import FMPLogger

if TYPE_CHECKING:
    from fmp_data.models import Endpoint

logger = FMPLogger().get_logger(__name__)


class GroupConfig(TypedDict):
    """Configuration for an endpoint group."""

    endpoint_map: dict[str, Endpoint[Any]]
    semantics_map: dict[str, EndpointSemantics]
    category: SemanticCategory


def _get_endpoint_groups() -> dict[str, GroupConfig]:
    """
    Lazily load endpoint groups to avoid circular imports.

    Returns:
        Dictionary of endpoint groups with their mappings
    """
    # Import mappings only when needed to avoid circular imports
    from fmp_data.alternative.mapping import (
        ALTERNATIVE_ENDPOINT_MAP,
        ALTERNATIVE_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.company.mapping import (
        COMPANY_ENDPOINT_MAP,
        COMPANY_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.economics.mapping import (
        ECONOMICS_ENDPOINT_MAP,
        ECONOMICS_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.fundamental.mapping import (
        FUNDAMENTAL_ENDPOINT_MAP,
        FUNDAMENTAL_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.institutional.mapping import (
        INSTITUTIONAL_ENDPOINT_MAP,
        INSTITUTIONAL_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.intelligence.mapping import (
        INTELLIGENCE_ENDPOINT_MAP,
        INTELLIGENCE_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.investment.mapping import (
        INVESTMENT_ENDPOINT_MAP,
        INVESTMENT_ENDPOINTS_SEMANTICS,
    )
    from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS
    from fmp_data.technical.mapping import (
        TECHNICAL_ENDPOINT_MAP,
        TECHNICAL_ENDPOINTS_SEMANTICS,
    )

    return {
        "alternative": {
            "endpoint_map": ALTERNATIVE_ENDPOINT_MAP,
            "semantics_map": ALTERNATIVE_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.ALTERNATIVE_DATA,
        },
        "company": {
            "endpoint_map": COMPANY_ENDPOINT_MAP,
            "semantics_map": COMPANY_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.COMPANY_INFO,
        },
        "economics": {
            "endpoint_map": ECONOMICS_ENDPOINT_MAP,
            "semantics_map": ECONOMICS_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.ECONOMIC,
        },
        "fundamental": {
            "endpoint_map": FUNDAMENTAL_ENDPOINT_MAP,
            "semantics_map": FUNDAMENTAL_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.FUNDAMENTAL_ANALYSIS,
        },
        "market": {
            "endpoint_map": MARKET_ENDPOINT_MAP,
            "semantics_map": MARKET_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.MARKET_DATA,
        },
        "technical": {
            "endpoint_map": TECHNICAL_ENDPOINT_MAP,
            "semantics_map": TECHNICAL_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.TECHNICAL_ANALYSIS,
        },
        "institutional": {
            "endpoint_map": INSTITUTIONAL_ENDPOINT_MAP,
            "semantics_map": INSTITUTIONAL_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.INSTITUTIONAL,
        },
        "intelligence": {
            "endpoint_map": INTELLIGENCE_ENDPOINT_MAP,
            "semantics_map": INTELLIGENCE_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.INTELLIGENCE,
        },
        "investment": {
            "endpoint_map": INVESTMENT_ENDPOINT_MAP,
            "semantics_map": INVESTMENT_ENDPOINTS_SEMANTICS,
            "category": SemanticCategory.INVESTMENT_PRODUCTS,
        },
    }


# Lazy property to get ENDPOINT_GROUPS only when needed
def get_endpoint_groups() -> dict[str, GroupConfig]:
    """Get endpoint groups with lazy loading."""
    return _get_endpoint_groups()


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self) -> None:
        self.logger = FMPLogger().get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def expected_category(self) -> SemanticCategory:
        """The category this rule is responsible for validating."""
        ...

    @property
    @abstractmethod
    def endpoint_prefixes(self) -> set[str]:
        """Set of prefixes that identify which methods belong to this rule."""
        ...

    @abstractmethod
    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate that the method_name belongs to category."""
        ...

    @abstractmethod
    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """Validate parameters for the specified method_name."""
        ...

    @abstractmethod
    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Return parameter validation requirements."""
        ...


class EndpointBasedRule(ValidationRule):
    """Validation rule that derives its rules from endpoint definitions."""

    def __init__(self, endpoints: dict[str, Endpoint], category: SemanticCategory):
        super().__init__()
        self._endpoints = endpoints
        self._category = category

    @property
    def expected_category(self) -> SemanticCategory:
        """Return the category this rule validates."""
        return self._category

    @property
    def endpoint_prefixes(self) -> set[str]:
        """Get prefixes directly from endpoint names."""
        prefixes = set()
        for name in self._endpoints.keys():
            # Add the method name as a prefix
            prefixes.add(name)
            # If it starts with get_, also add the base part
            if name.startswith("get_"):
                base = name[4:]
                prefixes.add(base)
                # Add component parts for nested prefixes
                parts = base.split("_")
                for i in range(len(parts)):
                    prefix = "_".join(parts[: i + 1])
                    prefixes.add(prefix)
        return prefixes

    def validate(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate method name and category."""
        if category != self.expected_category:
            return False, f"Expected {self.expected_category}, got {category}"

        # Check if this method exists in our endpoints
        if method_name in self._endpoints:
            return True, ""

        # If it doesn't match directly, see if it matches any of our prefixes
        operation = method_name[4:] if method_name.startswith("get_") else method_name
        for endpoint_name in self._endpoints.keys():
            endpoint_base = (
                endpoint_name[4:] if endpoint_name.startswith("get_") else endpoint_name
            )
            if operation == endpoint_base or operation.startswith(f"{endpoint_base}_"):
                return True, ""

        return False, f"Method {method_name} not found in registered endpoints"

    def validate_parameters(
        self, method_name: str, parameters: dict
    ) -> tuple[bool, str]:
        """Validate parameters against endpoint definition."""
        endpoint = self._endpoints.get(method_name)
        if not endpoint:
            return False, f"No endpoint found for {method_name}"

        # Get all valid parameter names
        valid_params = {p.name for p in endpoint.mandatory_params}
        if endpoint.optional_params:
            valid_params.update(p.name for p in endpoint.optional_params)

        # Check for invalid parameters
        invalid_params = set(parameters.keys()) - valid_params
        if invalid_params:
            return False, f"Invalid parameters: {', '.join(invalid_params)}"

        # Check for missing mandatory parameters
        mandatory_params = {p.name for p in endpoint.mandatory_params}
        missing_params = mandatory_params - set(parameters.keys())
        if missing_params:
            return False, f"Missing mandatory parameters: {', '.join(missing_params)}"

        # Validate parameter values
        for param_name, value in parameters.items():
            param_def = next(
                (
                    p
                    for p in endpoint.mandatory_params
                    + (endpoint.optional_params or [])
                    if p.name == param_name
                ),
                None,
            )
            if param_def:
                try:
                    param_def.validate_value(value)
                except ValueError as e:
                    return False, str(e)

        return True, ""

    @staticmethod
    def _get_type_pattern(
        param_type: str, valid_values: list[Any] | None = None
    ) -> list[str]:
        """Get regex patterns for a given parameter type."""
        match param_type:
            case "string":
                if valid_values:
                    return [f"^({'|'.join(map(str, valid_values))}))$"]
                return [r"^.+$"]
            case "integer":
                return [r"^\d+$"]
            case "float":
                return [r"^\d*\.?\d+$"]
            case "boolean":
                return [r"^(true|false|0|1)$"]
            case "date":
                return [r"^\d{4}-\d{2}-\d{2}$"]
            case "datetime":
                return [r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"]
            case _:
                return []

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter requirements from endpoint definition."""
        endpoint = self._endpoints.get(method_name)
        if not endpoint:
            return None

        patterns: dict[str, list[str]] = {}

        # Add patterns for all parameters
        for param in endpoint.mandatory_params + (endpoint.optional_params or []):
            param_patterns = self._get_type_pattern(
                param.param_type.value, param.valid_values
            )
            if param_patterns:
                patterns[param.name] = param_patterns

        return patterns if patterns else None


class ValidationRuleRegistry:
    """Registry that manages and coordinates validation rules."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._rules: list[ValidationRule] = []
        self.logger = FMPLogger().get_logger(self.__class__.__name__)

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule."""
        self._rules.append(rule)
        self.logger.debug(f"Registered validation rule: {rule.__class__.__name__}")

    def validate_category(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[bool, str]:
        """Validate category using registered rules."""
        # First check if we have any rules for this category
        category_rules = [
            rule for rule in self._rules if rule.expected_category == category
        ]
        if not category_rules:
            return False, f"No rules found for category {category.value}"

        # Find matching rule based on prefix patterns
        matching_rule: ValidationRule | None = None
        for rule in self._rules:
            if any(method_name.startswith(prefix) for prefix in rule.endpoint_prefixes):
                matching_rule = rule
                break

        if matching_rule:
            if matching_rule.expected_category != category:
                return (
                    False,
                    f"Category mismatch: endpoint {method_name} "
                    f"belongs to {matching_rule.expected_category.value}, "
                    f"not {category.value}",
                )
            return matching_rule.validate(method_name, category)

        return (
            False,
            f"No matching rule found for {method_name} in category {category.value}",
        )

    def get_parameter_requirements(
        self, method_name: str, category: SemanticCategory
    ) -> tuple[dict[str, list[str]] | None, str]:
        """Get parameter requirements for a method."""
        for rule in self._rules:
            if rule.expected_category == category:
                requirements = rule.get_parameter_requirements(method_name)
                if requirements is not None:
                    return requirements, ""
        return None, f"No parameter requirements found for {method_name}"

    def validate_parameters(
        self, method_name: str, category: SemanticCategory, parameters: dict
    ) -> tuple[bool, str]:
        """Validate parameters using registered rules."""
        for rule in self._rules:
            if rule.expected_category == category:
                return rule.validate_parameters(method_name, parameters)
        return True, ""

    def get_expected_category(self, method_name: str) -> SemanticCategory | None:
        """Determine the expected category for a method name."""
        for rule in self._rules:
            if any(method_name.startswith(prefix) for prefix in rule.endpoint_prefixes):
                return rule.expected_category
        return None


class EndpointRegistry:
    """Registry for managing FMP API endpoints and their semantic information."""

    def __init__(self) -> None:
        self._endpoints: dict[str, EndpointInfo] = {}
        self._validation: ValidationRuleRegistry | None = None  # Lazy initialization
        self.logger: Logger = (
            FMPLogger().get_logger(__name__).getChild(self.__class__.__name__)
        )
        # Don't register validation rules immediately - do it lazily

    def _ensure_validation_initialized(self) -> None:
        """Ensure validation registry is initialized (lazy initialization)."""
        if self._validation is None:
            self._validation = ValidationRuleRegistry()
            self._register_validation_rules()

    def _register_validation_rules(self) -> None:
        """Register validation rules for each endpoint group."""
        if self._validation is None:
            return

        endpoint_groups = get_endpoint_groups()  # Use lazy loading
        for group_name, config in endpoint_groups.items():
            # Explicitly create the rule with properly typed arguments
            rule = EndpointBasedRule(
                endpoints=config["endpoint_map"],
                category=config["category"],
            )
            self._validation.register_rule(rule)
            self.logger.debug(f"Registered validation rule for {group_name}")

    @property
    def validation(self) -> ValidationRuleRegistry:
        """Return the lazily-initialised validation registry.

        Example:
            >>> registry = EndpointRegistry()
            >>> validation = registry.validation
        """
        self._ensure_validation_initialized()
        if self._validation is None:  # should never happen
            raise RuntimeError("Validation registry failed to initialise")
        return self._validation

    @staticmethod
    def _validate_method_name(name: str, info: EndpointInfo) -> tuple[bool, str | None]:
        """Validate method name consistency."""
        if info.semantics.method_name != name:
            return False, (
                f"Method name mismatch: endpoint uses '{name}' but semantics uses "
                f"'{info.semantics.method_name}'"
            )
        return True, None

    @staticmethod
    def _validate_parameters(name: str, info: EndpointInfo) -> tuple[bool, str | None]:
        """Validate parameter consistency."""
        endpoint_params = {p.name for p in info.endpoint.mandatory_params}
        if info.endpoint.optional_params:
            endpoint_params.update(p.name for p in info.endpoint.optional_params)

        semantic_params = set(info.semantics.parameter_hints.keys())

        # Check for missing parameter hints
        missing_hints = endpoint_params - semantic_params
        if missing_hints:
            return False, f"Missing semantic hints for parameters: {missing_hints}"

        # Check for extra parameter hints
        extra_hints = semantic_params - endpoint_params
        if extra_hints:
            return (
                False,
                f"Extra semantic hints for non-existent parameters: {extra_hints}",
            )

        return True, None

    def validate_endpoint(self, name: str, info: EndpointInfo) -> tuple[bool, str]:
        """Validate complete endpoint information."""
        # Method name validation
        valid, error = self._validate_method_name(name, info)
        if not valid:
            return False, f"Method name validation failed: {error}"

        # Category validation - use property to trigger lazy init
        valid, error = self.validation.validate_category(name, info.semantics.category)
        if not valid:
            return False, f"Category validation failed: {error}"

        # Parameter validation
        valid, error = self._validate_parameters(name, info)
        if not valid:
            return False, f"Parameter validation failed: {error}"

        return True, ""

    def register(
        self, name: str, endpoint: Endpoint, semantics: EndpointSemantics
    ) -> None:
        """
        Register an endpoint with validation.

        Args:
            name: Name of the endpoint
            endpoint: Endpoint definition
            semantics: Semantic information for the endpoint

        Raises:
            ValueError: If endpoint info is invalid or inconsistent
        """
        try:
            info = EndpointInfo(endpoint=endpoint, semantics=semantics)
            valid, error_details = self.validate_endpoint(name, info)
            if not valid:
                self.logger.error(
                    f"Validation failed for endpoint {name}",
                    extra={
                        "endpoint_name": name,
                        "semantic_method_name": semantics.method_name,
                        "semantic_category": semantics.category,
                        "validation_error": error_details,
                    },
                )
                raise ValueError(
                    f"Invalid endpoint information for {name}: {error_details}"
                )

            self._endpoints[name] = info
            self.logger.debug(f"Successfully registered endpoint: {name}")
        except Exception as e:
            self.logger.error(
                f"Failed to register endpoint {name}: {e!s}", exc_info=True
            )
            raise

    def register_batch(
        self, endpoints: dict[str, tuple[Endpoint, EndpointSemantics]]
    ) -> None:
        """
        Register multiple endpoints at once.

        Args:
            endpoints: Dictionary mapping
            endpoint names to (Endpoint, EndpointSemantics) pairs

        Raises:
            ValueError: If any endpoint fails validation
        """
        for name, (endpoint, semantics) in endpoints.items():
            try:
                self.register(name, endpoint, semantics)
            except ValueError as e:
                self.logger.error(f"Failed to register endpoint {name}: {e!s}")
                raise

    def get_endpoint(self, name: str) -> EndpointInfo | None:
        """
        Get endpoint information by name.

        Args:
            name: Name of the endpoint

        Returns:
            EndpointInfo if found, None otherwise
        """
        return self._endpoints.get(name)

    def get_endpoints_by_names(self, names: list[str]) -> dict[str, EndpointInfo]:
        """
        Get multiple endpoints by their names.

        Args:
            names: List of endpoint names to retrieve

        Returns:
            Dictionary mapping names to endpoint info for found endpoints
        """
        return {name: info for name, info in self._endpoints.items() if name in names}

    def list_endpoints(self) -> dict[str, EndpointInfo]:
        """
        Get all registered endpoints.

        Returns:
            Dictionary mapping endpoint names to their info
        """
        return self._endpoints

    def filter_endpoints(self, category: str | None = None) -> dict[str, EndpointInfo]:
        """
        Filter endpoints by category.

        Args:
            category: Category to filter by, or None for all endpoints

        Returns:
            Dictionary of endpoints matching the category
        """
        if not category:
            return self._endpoints
        return {
            name: info
            for name, info in self._endpoints.items()
            if info.semantics.category == category
        }

    def filter_endpoints_by_categories(
        self, categories: list[str]
    ) -> dict[str, EndpointInfo]:
        """
        Filter endpoints by multiple categories.

        Args:
            categories: List of categories to filter by

        Returns:
            Dictionary of endpoints matching any of the categories
        """
        if not categories:
            return self._endpoints
        return {
            name: info
            for name, info in self._endpoints.items()
            if info.semantics.category in categories
        }

    def get_embedding_text(self, name: str) -> str | None:
        """
        Get text for embedding generation.

        Args:
            name: Name of the endpoint

        Returns:
            Normalized text suitable for
            embedding generation, or None if endpoint not found
        """
        info = self.get_endpoint(name)
        if not info:
            return None

        def normalize_text(text: str) -> str:
            """Normalize text for consistent embeddings."""

            text = re.sub(r"\s+", " ", text).strip().lower()
            text = re.sub(r"[^\w\s\-/]", "", text)
            return text

        def format_list(items: list[str], prefix: str = "") -> list[str]:
            """Format a list of items with optional prefix."""
            return [f"{prefix}{normalize_text(str(item))}" for item in items if item]

        # Build text parts from endpoint semantics
        text_parts: list[str] = [
            normalize_text(info.semantics.natural_description),
            *format_list(info.semantics.example_queries, "example: "),
            *format_list(info.semantics.related_terms, "related: "),
            *format_list(info.semantics.use_cases, "use case: "),
            f"category: {info.semantics.category.lower()}",
        ]

        if info.semantics.sub_category:
            text_parts.append(f"subcategory: {info.semantics.sub_category.lower()}")

        # Parameter hints
        for param_name, hint in info.semantics.parameter_hints.items():
            param_parts = [
                f"parameter {param_name}:",
                *format_list(hint.natural_names, "name: "),
                *format_list(hint.context_clues, "context: "),
                *format_list(hint.examples, "example: "),
            ]
            text_parts.extend(param_parts)

        # Response hints
        for field_name, resp_hint in info.semantics.response_hints.items():
            response_parts = [
                f"response {field_name}:",
                normalize_text(resp_hint.description),
                *format_list(resp_hint.related_terms, "related: "),
                *format_list([str(ex) for ex in resp_hint.examples], "example: "),
            ]
            text_parts.extend(response_parts)

        return " ".join(filter(None, text_parts))

    def get_search_metadata(self, name: str) -> dict[str, str] | None:
        """
        Get metadata for vector store search.

        Args:
            name: Name of the endpoint

        Returns:
            Dictionary of metadata suitable for
            search indexing, or None if endpoint not found
        """
        info = self.get_endpoint(name)
        if not info:
            return None

        return {
            "method_name": info.semantics.method_name,
            "category": info.semantics.category,
            "sub_category": info.semantics.sub_category or "",
            "parameter_count": str(len(info.endpoint.mandatory_params)),
            "has_optional_params": str(bool(info.endpoint.optional_params)),
            "response_model": info.endpoint.response_model.__name__,
        }


# Convenience access function for external use
def get_all_endpoint_groups() -> dict[str, GroupConfig]:
    """Get all endpoint groups (for external use)."""
    return get_endpoint_groups()
