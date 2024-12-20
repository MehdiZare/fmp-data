# fmp_langchain/utils.py
import importlib.util

from fmp_data.exceptions import ConfigError


def is_langchain_available() -> bool:
    """
    Check if LangChain integration is available.

    Returns:
        bool: True if LangChain dependencies are installed
        and available, False otherwise
    """
    has_langchain = importlib.util.find_spec("langchain") is not None

    return has_langchain


def check_langchain_dependency() -> None:
    """Check if langchain is installed when embedding config is used"""
    if not is_langchain_available:
        raise ConfigError(
            "Langchain is required for using embeddings functionality. "
            "Please install with: pip install langchain"
        )


def check_dependency(package: str, provider: str) -> None:
    """
    Check if a required package is installed.

    Args:
        package: Name of the package to check
        provider: Name of the provider requiring this package

    Raises:
        ConfigError: If the package is not installed, with installation instructions
    """
    if importlib.util.find_spec(package) is None:
        provider_packages = {
            "openai": ["openai", "tiktoken"],
            "huggingface": ["sentence_transformers", "torch"],
            "cohere": ["cohere"],
        }

        packages = provider_packages.get(provider.lower(), [package])
        install_cmd = " ".join(packages)

        raise ConfigError(
            f"Required package(s) for {provider} embeddings not found. "
            f"Please install with: pip install {install_cmd}"
        )
