# fmp_data/utils/check_install.py
"""
Installation verification script for fmp-data package.

This script checks that the package is properly installed and that
optional dependencies are correctly handled.
"""
import sys


def check_core_installation() -> bool:
    """Check that core fmp-data functionality is available."""
    try:
        import fmp_data
        from fmp_data import FMPDataClient, FMPError
        from fmp_data.config import ClientConfig
        from fmp_data.lc.utils import is_langchain_available

        print("✅ Core fmp-data imports successful")
        print(f"   Package version: {getattr(fmp_data, '__version__', 'unknown')}")
        print(f"   LangChain available: {is_langchain_available()}")
        return True

    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False


def check_langchain_installation() -> bool:
    """Check that LangChain integration is available."""
    try:
        from fmp_data.lc.utils import is_langchain_available

        if not is_langchain_available():
            print("ℹ️  LangChain dependencies not installed")
            print("   Install with: pip install 'fmp-data[langchain]'")
            return False

        # Test lazy imports
        import fmp_data

        create_vector_store = fmp_data.create_vector_store
        EndpointSemantics = fmp_data.EndpointSemantics
        SemanticCategory = fmp_data.SemanticCategory

        from fmp_data.lc.config import LangChainConfig
        from fmp_data.lc.embedding import EmbeddingProvider

        print("✅ LangChain integration available")
        print("   All LangChain imports successful")
        return True

    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        print("   Install with: pip install 'fmp-data[langchain]'")
        return False


def check_api_keys() -> dict[str, bool]:
    """Check if API keys are configured."""
    import os

    results = {}

    # Check FMP API key
    fmp_key = os.getenv("FMP_API_KEY")
    if fmp_key:
        print("✅ FMP_API_KEY environment variable set")
        results["fmp"] = True
    else:
        print("⚠️  FMP_API_KEY environment variable not set")
        print("   Set with: export FMP_API_KEY=your_api_key")
        results["fmp"] = False

    # Check OpenAI API key (for LangChain)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY environment variable set")
        results["openai"] = True
    else:
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("   Set with: export OPENAI_API_KEY=your_api_key")
        print("   (Required for LangChain integration)")
        results["openai"] = False

    return results


def test_basic_functionality() -> bool:
    """Test basic client functionality."""
    import os

    try:
        from fmp_data import FMPDataClient

        # Check if API key is available for testing
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            print("ℹ️  Skipping API test - no FMP_API_KEY set")
            return True

        # Test client creation (don't make actual API calls)
        client = FMPDataClient(api_key=api_key)
        print("✅ FMP client creation successful")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_langchain_functionality() -> bool:
    """Test LangChain integration functionality."""
    import os

    try:
        from fmp_data.lc.utils import is_langchain_available

        if not is_langchain_available():
            print("ℹ️  Skipping LangChain test - dependencies not installed")
            return True

        # Check if both API keys are available
        fmp_key = os.getenv("FMP_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not fmp_key or not openai_key:
            print("ℹ️  Skipping LangChain test - API keys not set")
            return True

        # Test configuration creation (don't create actual vector store)
        from fmp_data.lc.config import LangChainConfig
        from fmp_data.lc.embedding import EmbeddingProvider

        config = LangChainConfig(
            api_key=fmp_key,
            embedding_provider=EmbeddingProvider.OPENAI,
            embedding_api_key=openai_key,
        )

        print("✅ LangChain configuration successful")
        return True

    except Exception as e:
        print(f"❌ LangChain functionality test failed: {e}")
        return False


def main() -> None:
    """Run all installation checks."""
    print("🔍 Checking fmp-data installation...\n")

    # Check core installation
    print("1. Core Installation Check:")
    core_ok = check_core_installation()
    print()

    # Check LangChain installation
    print("2. LangChain Integration Check:")
    langchain_ok = check_langchain_installation()
    print()

    # Check API keys
    print("3. API Key Configuration:")
    api_keys = check_api_keys()
    print()

    # Test basic functionality
    print("4. Basic Functionality Test:")
    basic_ok = test_basic_functionality()
    print()

    # Test LangChain functionality
    print("5. LangChain Functionality Test:")
    langchain_func_ok = test_langchain_functionality()
    print()

    # Summary
    print("📋 Summary:")
    if core_ok:
        print("✅ Core fmp-data package is properly installed")
    else:
        print("❌ Core installation has issues")
        sys.exit(1)

    if langchain_ok:
        print("✅ LangChain integration is available")
    else:
        print("ℹ️  LangChain integration not available (optional)")

    if api_keys["fmp"]:
        print("✅ FMP API key is configured")
    else:
        print("⚠️  FMP API key not configured")

    if langchain_ok and not api_keys["openai"]:
        print("⚠️  OpenAI API key not configured (needed for LangChain)")

    print("\n🎉 Installation check complete!")

    if not core_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
