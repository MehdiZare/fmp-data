# fmp_client/lc/registry.py
from __future__ import annotations

import re

from pydantic import BaseModel

from fmp_data.alternative.validation import AlternativeMarketsRule
from fmp_data.company.validation import CompanyInfoRule
from fmp_data.economics.validation import EconomicsRule
from fmp_data.fundamental.validation import FundamentalAnalysisRule
from fmp_data.institutional.validation import InstitutionalRule
from fmp_data.intelligence.validation import MarketIntelligenceRule
from fmp_data.investment.validation import InvestmentProductsRule
from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.validation import ValidationRuleRegistry
from fmp_data.logger import FMPLogger
from fmp_data.market.validation import MarketDataRule
from fmp_data.models import Endpoint
from fmp_data.technical.validation import TechnicalAnalysisRule

logger = FMPLogger().get_logger(__name__)


class EndpointInfo(BaseModel):
    """Combined endpoint information"""

    endpoint: Endpoint
    semantics: EndpointSemantics


class EndpointRegistry:
    def __init__(self):
        self._endpoints: dict[str, EndpointInfo] = {}
        self._validation = ValidationRuleRegistry()
        self.logger = logger.getChild(self.__class__.__name__)

        # Register validation rules
        self._validation.register_rule(AlternativeMarketsRule())
        self._validation.register_rule(CompanyInfoRule())
        self._validation.register_rule(EconomicsRule())
        self._validation.register_rule(FundamentalAnalysisRule())
        self._validation.register_rule(InstitutionalRule())
        self._validation.register_rule(MarketIntelligenceRule())
        self._validation.register_rule(InvestmentProductsRule())
        self._validation.register_rule(MarketDataRule())
        self._validation.register_rule(TechnicalAnalysisRule())

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
        info = EndpointInfo(endpoint=endpoint, semantics=semantics)
        if not self.validate_endpoint(name, info):
            error_msg = f"Invalid endpoint information for {name}"
            raise ValueError(error_msg)

        self._endpoints[name] = info
        self.logger.debug(f"Registered endpoint: {name}")

    def register_batch(
        self, endpoints: dict[str, tuple[Endpoint, EndpointSemantics]]
    ) -> None:
        """
        Register multiple endpoints at once

        Args:
            endpoints: Dictionary mapping names to (endpoint, semantics) tuples
        """
        for name, (endpoint, semantics) in endpoints.items():
            try:
                self.register(name, endpoint, semantics)
            except ValueError as e:
                self.logger.error(f"Failed to register endpoint {name}: {str(e)}")
                raise

    def get_endpoint(self, name: str) -> EndpointInfo | None:
        """
        Get endpoint information by name

        Args:
            name: Method name of the endpoint

        Returns:
            EndpointInfo if found, None otherwise
        """
        return self._endpoints.get(name)

    def get_endpoints_by_names(self, names: list[str]) -> dict[str, EndpointInfo]:
        """
        Get multiple endpoints by their names

        Args:
            names: List of endpoint names to retrieve

        Returns:
            Dictionary of found endpoints
        """
        return {name: info for name, info in self._endpoints.items() if name in names}

    def list_endpoints(self) -> dict[str, EndpointInfo]:
        """
        Get all registered endpoints

        Returns:
            Dictionary of all endpoints
        """
        return self._endpoints

    def filter_endpoints(self, category: str | None = None) -> dict[str, EndpointInfo]:
        """
        Filter endpoints by category

        Args:
            category: Category to filter by, returns all if None

        Returns:
            Dictionary of matching endpoints
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
        Filter endpoints by multiple categories

        Args:
            categories: List of categories to include

        Returns:
            Dictionary of matching endpoints
        """
        if not categories:
            return self._endpoints

        return {
            name: info
            for name, info in self._endpoints.items()
            if info.semantics.category in categories
        }

    def validate_endpoint(self, name: str, info: EndpointInfo) -> bool:
        """Validate endpoint information consistency"""
        # Method name check
        if info.semantics.method_name != name:
            self.logger.warning(
                f"Method name mismatch for {name}: "
                f"semantics has {info.semantics.method_name}"
            )
            return False

        # Category validation using rules
        if not self._validation.validate_category(name, info.semantics.category):
            self.logger.warning(
                f"Invalid category for endpoint {name}: "
                f"got {info.semantics.category}"
            )
            return False

        # Get all endpoint parameters (mandatory + optional)
        endpoint_params = {p.name for p in info.endpoint.mandatory_params}
        if info.endpoint.optional_params:
            endpoint_params.update(p.name for p in info.endpoint.optional_params)

        semantic_params = set(info.semantics.parameter_hints.keys())

        missing_hints = endpoint_params - semantic_params
        if missing_hints:
            self.logger.warning(
                f"Missing semantic hints for parameters in {name}: {missing_hints}"
            )
            return False

        extra_hints = semantic_params - endpoint_params
        if extra_hints:
            self.logger.warning(
                f"Extra semantic hints for non-existent "
                f"parameters in {name}: {extra_hints}"
            )
            return False

        return True

    def get_embedding_text(self, name: str) -> str | None:
        """
        Get text for embedding generation

        Args:
            name: Endpoint name to generate text for

        Returns:
            Normalized text for embedding or None if endpoint not found
        """
        info = self.get_endpoint(name)
        if not info:
            return None

        def normalize_text(text: str) -> str:
            """Normalize text for consistent embeddings"""
            # Remove extra whitespace and lowercase
            text = re.sub(r"\s+", " ", text).strip().lower()
            # Remove special characters but keep structure (escaping hyphen)
            text = re.sub(r"[^\w\s\-/]", "", text)  # Escape hyphen with backslash
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

        # Add subcategory if present
        if info.semantics.sub_category:
            text_parts.append(f"subcategory: {info.semantics.sub_category.lower()}")

        # Add organized parameter information
        for param_name, hint in info.semantics.parameter_hints.items():
            param_parts = [
                f"parameter {param_name}:",
                *format_list(hint.natural_names, "name: "),
                *format_list(hint.context_clues, "context: "),
                *format_list(hint.examples, "example: "),
            ]
            text_parts.extend(param_parts)

        # Add organized response field information
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
        """
        Get metadata for vector store search

        Args:
            name: Endpoint name to get metadata for

        Returns:
            Dictionary of metadata or None if endpoint not found
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
