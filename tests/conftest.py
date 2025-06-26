# conftest.py (root level)
"""
Root conftest.py for managing optional dependencies and test configuration.

This file handles:
- Detection of available optional dependencies
- Automatic test skipping based on markers and dependencies
- Global fixtures for dependency management
- Safe imports that don't fail when dependencies are missing
"""
import importlib.util
import os
import warnings
from typing import Any

import pytest


def _is_package_available(package_name: str) -> bool:
    """Check if a package is available for import."""
    return importlib.util.find_spec(package_name) is not None


def _safe_import(module_name: str, attr_name: str | None = None) -> Any | None:
    """Safely import a module/attribute, returning None if not available."""
    try:
        module = importlib.import_module(module_name)
        if attr_name:
            return getattr(module, attr_name, None)
        return module
    except ImportError:
        return None


# Check available dependencies at import time
LANGCHAIN_AVAILABLE = _is_package_available("langchain")
OPENAI_AVAILABLE = _is_package_available("openai")
FAISS_AVAILABLE = _is_package_available("faiss")


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with dependency information."""
    # Add dependency info to config
    config._langchain_available = LANGCHAIN_AVAILABLE  # type: ignore
    config._openai_available = OPENAI_AVAILABLE  # type: ignore
    config._fmp_api_key = os.getenv("FMP_TEST_API_KEY")  # type: ignore
    config._openai_api_key = os.getenv("OPENAI_API_KEY")  # type: ignore

    # Print dependency status
    if config.option.verbose >= 1:
        print(f"\n🔍 Dependency Check:")
        print(f"   LangChain: {'✅' if LANGCHAIN_AVAILABLE else '❌'}")
        print(f"   OpenAI: {'✅' if OPENAI_AVAILABLE else '❌'}")
        print(f"   FAISS: {'✅' if FAISS_AVAILABLE else '❌'}")
        print(f"   FMP API Key: {'✅' if config._fmp_api_key else '❌'}")  # type: ignore
        print(f"   OpenAI API Key: {'✅' if config._openai_api_key else '❌'}")  # type: ignore


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to skip tests based on available dependencies."""

    for item in items:
        # Skip LangChain tests if LangChain not available
        if item.get_closest_marker("langchain") and not LANGCHAIN_AVAILABLE:
            item.add_marker(
                pytest.mark.skip(
                    reason="LangChain dependencies not installed. "
                    "Install with: pip install 'fmp-data[langchain]'"
                )
            )

        # Skip integration tests if no API key
        if item.get_closest_marker("integration") and not config._fmp_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="FMP_TEST_API_KEY not set"))

        # Skip tests requiring API keys
        if item.get_closest_marker("requires_api_key") and not config._fmp_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="FMP_TEST_API_KEY not set"))

        if item.get_closest_marker("requires_openai_key") and not config._openai_api_key:  # type: ignore
            item.add_marker(pytest.mark.skip(reason="OPENAI_API_KEY not set"))


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Setup for individual test runs with dependency checks."""

    # Additional runtime checks for edge cases
    if item.get_closest_marker("langchain"):
        # Double check that LangChain is really available
        if not LANGCHAIN_AVAILABLE:
            pytest.skip("LangChain not available at runtime")

        # For LangChain tests, try importing key modules
        langchain_core = _safe_import("langchain_core.embeddings")
        if not langchain_core:
            pytest.skip("langchain_core not available")


@pytest.fixture(scope="session")
def langchain_available() -> bool:
    """Fixture indicating if LangChain is available."""
    return LANGCHAIN_AVAILABLE


@pytest.fixture(scope="session")
def openai_available() -> bool:
    """Fixture indicating if OpenAI is available."""
    return OPENAI_AVAILABLE


@pytest.fixture(scope="session")
def has_fmp_api_key() -> bool:
    """Fixture indicating if FMP API key is available."""
    return bool(os.getenv("FMP_TEST_API_KEY"))


@pytest.fixture(scope="session")
def has_openai_api_key() -> bool:
    """Fixture indicating if OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY"))


@pytest.fixture(autouse=True)
def suppress_dependency_warnings() -> None:
    """Automatically suppress dependency-related warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ImportWarning)
        warnings.filterwarnings("ignore", message=".*langchain.*")
        warnings.filterwarnings("ignore", message=".*faiss.*")
        warnings.filterwarnings("ignore", message=".*openai.*")
        yield


# Safe imports for tests - these won't fail if dependencies are missing
@pytest.fixture(scope="session")
def safe_fmp_imports() -> dict[str, Any]:
    """Safely import core FMP modules."""
    imports = {}

    # Core imports that should always work
    try:
        fmp_data = importlib.import_module("fmp_data")
        imports["fmp_data"] = fmp_data

        # Import specific classes
        from fmp_data import FMPDataClient, FMPError, ClientConfig

        imports["FMPDataClient"] = FMPDataClient
        imports["FMPError"] = FMPError
        imports["ClientConfig"] = ClientConfig

    except ImportError as e:
        pytest.fail(f"Core fmp_data imports failed: {e}")

    return imports


@pytest.fixture(scope="session")
def safe_langchain_imports() -> dict[str, Any]:
    """Safely import LangChain modules if available."""
    imports = {}

    if not LANGCHAIN_AVAILABLE:
        return imports

    # Try importing LangChain modules
    imports["create_vector_store"] = _safe_import("fmp_data", "create_vector_store")
    imports["LangChainConfig"] = _safe_import("fmp_data.lc.config", "LangChainConfig")
    imports["EndpointSemantics"] = _safe_import(
        "fmp_data.lc.models", "EndpointSemantics"
    )

    return imports


# Skip entire test files based on path and dependencies
def pytest_ignore_collect(collection_path: str, config: pytest.Config) -> bool | None:
    """Skip collecting certain test files based on dependencies."""

    # Convert to string for path checking
    path_str = str(collection_path)

    # Skip LangChain test files if LangChain not available
    if "/lc/" in path_str or "langchain" in path_str.lower():
        if not LANGCHAIN_AVAILABLE:
            return True

    # Skip integration tests if no API key (optional - can be handled by markers instead)
    if "/integration/" in path_str:
        if not config._fmp_api_key and not config.getoption("--collect-only"):  # type: ignore
            return True

    return None
