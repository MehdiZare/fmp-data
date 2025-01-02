# fmp_data/lc/utils.py
import importlib.util


class DependencyError(Exception):
    """Raised when a required dependency is missing"""

    pass


def is_langchain_available() -> bool:
    """Check if LangChain is available."""
    return importlib.util.find_spec("langchain") is not None


def check_package_dependency(package: str, provider: str) -> None:
    """Check if a package is installed."""
    if importlib.util.find_spec(package) is None:
        raise DependencyError(
            f"Required package '{package}' for {provider} not found. "
            f"Please install with: pip install {package}"
        )


def check_embedding_requirements(provider: str) -> None:
    """Check embedding-specific dependencies."""
    provider_packages = {
        "openai": ["openai", "tiktoken"],
        "huggingface": ["sentence_transformers", "torch"],
        "cohere": ["cohere"],
    }

    packages = provider_packages.get(provider.lower(), [provider])
    for package in packages:
        check_package_dependency(package, provider)
