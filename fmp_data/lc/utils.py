# fmp_data/lc/utils.py
import importlib.util

from fmp_data.exceptions import DependencyError

__all__ = [
    "DependencyError",
    "check_embedding_requirements",
    "check_package_dependency",
    "is_langchain_available",
]


def is_langchain_available() -> bool:
    """Check if LangChain is available."""
    return (
        importlib.util.find_spec("langchain_core") is not None
        and importlib.util.find_spec("langchain_community") is not None
    )


def check_package_dependency(package: str, provider: str) -> None:
    """Check if a package is installed."""
    if importlib.util.find_spec(package) is None:
        raise DependencyError(
            feature=f"{provider} ({package})", install_command=f"pip install {package}"
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
