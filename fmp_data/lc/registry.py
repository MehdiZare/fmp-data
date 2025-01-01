# fmp_data/lc/registry.py
from __future__ import annotations

import re

from fmp_data.alternative.validation import AlternativeMarketsRule
from fmp_data.company.validation import CompanyInfoRule
from fmp_data.economics.validation import EconomicsRule
from fmp_data.fundamental.validation import FundamentalAnalysisRule
from fmp_data.institutional.validation import InstitutionalRule
from fmp_data.intelligence.validation import IntelligenceRule
from fmp_data.investment.validation import InvestmentProductsRule
from fmp_data.lc.models import EndpointInfo, EndpointSemantics
from fmp_data.lc.validation import ValidationRuleRegistry
from fmp_data.logger import FMPLogger
from fmp_data.market.validation import MarketDataRule
from fmp_data.models import Endpoint
from fmp_data.technical.validation import TechnicalAnalysisRule

logger = FMPLogger().get_logger(__name__)


class EndpointRegistry:
    def __init__(self):
        self._endpoints: dict[str, EndpointInfo] = {}
        self._validation = ValidationRuleRegistry()
        self.logger = logger.getChild(self.__class__.__name__)

        # Register validation rules
        self._register_validation_rules()

    def _register_validation_rules(self) -> None:
        """Register all validation rules in order of precedence"""
        rules = [
            FundamentalAnalysisRule(),
            MarketDataRule(),
            TechnicalAnalysisRule(),
            CompanyInfoRule(),
            InstitutionalRule(),
            IntelligenceRule(),
            AlternativeMarketsRule(),
            EconomicsRule(),
            InvestmentProductsRule(),
        ]

        for rule in rules:
            self._validation.register_rule(rule)
            self.logger.debug(f"Registered validation rule: {rule.__class__.__name__}")

    @staticmethod
    def _validate_method_name(name: str, info: EndpointInfo) -> tuple[bool, str | None]:
        """Validate method name consistency"""
        if info.semantics.method_name != name:
            return False, (
                f"Method name mismatch: endpoint uses '{name}' but semantics uses "
                f"'{info.semantics.method_name}'"
            )
        return True, None

    @staticmethod
    def _validate_parameters(name: str, info: EndpointInfo) -> tuple[bool, str | None]:
        """Validate parameter consistency"""
        # Get all endpoint parameters (mandatory + optional)
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
        # Method name validation
        valid, error = self._validate_method_name(name, info)
        if not valid:
            return False, f"Method name validation failed: {error}"

        # Category validation
        valid, error = self._validation.validate_category(name, info.semantics.category)
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
        Register an endpoint with validation

        Args:
            name: Method name for the endpoint
            endpoint: Endpoint configuration
            semantics: Semantic information for the endpoint

        Raises:
            ValueError: If endpoint information is invalid or inconsistent
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
                        "validation_error": error_details,  # Add detailed error message
                    },
                )
                error_msg = f"Invalid endpoint information for {name}: {error_details}"
                raise ValueError(error_msg)

            self._endpoints[name] = info
            self.logger.debug(f"Successfully registered endpoint: {name}")
        except Exception as e:
            self.logger.error(
                f"Failed to register endpoint {name}: {str(e)}", exc_info=True
            )
            raise

    def register_batch(
        self, endpoints: dict[str, tuple[Endpoint, EndpointSemantics]]
    ) -> None:
        """Register multiple endpoints at once"""
        for name, (endpoint, semantics) in endpoints.items():
            try:
                self.register(name, endpoint, semantics)
            except ValueError as e:
                self.logger.error(f"Failed to register endpoint {name}: {str(e)}")
                raise

    def get_endpoint(self, name: str) -> EndpointInfo | None:
        """Get endpoint information by name"""
        return self._endpoints.get(name)

    def get_endpoints_by_names(self, names: list[str]) -> dict[str, EndpointInfo]:
        """Get multiple endpoints by their names"""
        return {name: info for name, info in self._endpoints.items() if name in names}

    def list_endpoints(self) -> dict[str, EndpointInfo]:
        """Get all registered endpoints"""
        return self._endpoints

    def filter_endpoints(self, category: str | None = None) -> dict[str, EndpointInfo]:
        """Filter endpoints by category"""
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
        """Filter endpoints by multiple categories"""
        if not categories:
            return self._endpoints
        return {
            name: info
            for name, info in self._endpoints.items()
            if info.semantics.category in categories
        }

    def get_embedding_text(self, name: str) -> str | None:
        """Get text for embedding generation"""
        info = self.get_endpoint(name)
        if not info:
            return None

        def normalize_text(text: str) -> str:
            """Normalize text for consistent embeddings"""
            text = re.sub(r"\s+", " ", text).strip().lower()
            text = re.sub(r"[^\w\s\-/]", "", text)
            return text

        def format_list(items: list[str], prefix: str = "") -> list[str]:
            """Format a list of items with optional prefix"""
            return [f"{prefix}{normalize_text(str(item))}" for item in items if item]

        text_parts = [
            normalize_text(info.semantics.natural_description),
            *format_list(info.semantics.example_queries, "example: "),
            *format_list(info.semantics.related_terms, "related: "),
            *format_list(info.semantics.use_cases, "use case: "),
            f"category: {info.semantics.category.lower()}",
        ]

        if info.semantics.sub_category:
            text_parts.append(f"subcategory: {info.semantics.sub_category.lower()}")

        for param_name, hint in info.semantics.parameter_hints.items():
            param_parts = [
                f"parameter {param_name}:",
                *format_list(hint.natural_names, "name: "),
                *format_list(hint.context_clues, "context: "),
                *format_list(hint.examples, "example: "),
            ]
            text_parts.extend(param_parts)

        for field_name, hint in info.semantics.response_hints.items():
            response_parts = [
                f"response {field_name}:",
                normalize_text(hint.description),
                *format_list(hint.related_terms, "related: "),
                *format_list([str(ex) for ex in hint.examples], "example: "),
            ]
            text_parts.extend(response_parts)

        return " ".join(filter(None, text_parts))

    def get_search_metadata(self, name: str) -> dict[str, str] | None:
        """Get metadata for vector store search"""
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
