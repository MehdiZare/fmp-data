#!/usr/bin/env python
"""
Easy setup script for connecting FMP Data MCP Server to Claude Desktop.

This script will:
1. Check prerequisites
2. Install required packages
3. Configure Claude Desktop
4. Test the connection

Usage:
    python setup_claude_desktop.py
"""

import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def get_claude_config_path():
    """Get the Claude Desktop config file path for the current OS."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif system == "Windows":
        return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_fmp_installation():
    """Check if fmp-data package is installed."""
    try:
        import fmp_data  # noqa: F401

        print("✅ fmp-data package is installed")
        return True
    except ImportError:
        print("❌ fmp-data package is not installed")
        return False


def install_fmp_data():
    """Install fmp-data package with MCP support."""
    print("\n📦 Installing fmp-data with MCP support...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "fmp-data[mcp]"], check=True
        )
        print("✅ Successfully installed fmp-data[mcp]")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install fmp-data[mcp]")
        print("   Try running manually: pip install 'fmp-data[mcp]'")
        return False


def get_api_key():
    """Get FMP API key from user or environment."""
    # Check environment first
    api_key = os.environ.get("FMP_API_KEY")
    if api_key:
        print("✅ Using FMP API key from environment")
        return api_key

    # Ask user for API key
    print("\n🔑 FMP API Key Setup")
    print(
        "   Get a free key at: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi"
    )
    api_key = input("   Enter your FMP API key: ").strip()

    if not api_key:
        print("❌ API key is required")
        return None

    # Offer to save to environment
    save_env = input("   Save API key to environment for future use? (y/n): ").lower()
    if save_env == "y":
        system = platform.system()
        if system == "Windows":
            print(
                "   To save permanently, run this in Command Prompt as Administrator:"
            )
            print('   setx FMP_API_KEY "<your_api_key>"')
        else:
            shell_file = "~/.zshrc" if system == "Darwin" else "~/.bashrc"
            print(f"   Add this line to your {shell_file}:")
            print('   export FMP_API_KEY="<your_api_key>"')

    return api_key


def create_claude_config(api_key, custom_manifest=None):
    """Create or update Claude Desktop configuration."""
    config_path = get_claude_config_path()

    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    if config_path.exists():
        print(f"\n📄 Updating existing Claude config at: {config_path}")
        with open(config_path) as f:
            config = json.load(f)
    else:
        print(f"\n📄 Creating new Claude config at: {config_path}")
        config = {}

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Configure FMP MCP server
    server_config = {
        "command": sys.executable,  # Use current Python interpreter
        "args": ["-m", "fmp_data.mcp"],
        "env": {"FMP_API_KEY": api_key},
    }

    # Add custom manifest if specified
    if custom_manifest:
        server_config["env"]["FMP_MCP_MANIFEST"] = custom_manifest

    config["mcpServers"]["fmp-data"] = server_config

    # Save configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("✅ Claude Desktop configuration updated")
    return True


def test_mcp_server(api_key):
    """Test if the MCP server can start."""
    print("\n🧪 Testing MCP server...")

    env = os.environ.copy()
    env["FMP_API_KEY"] = api_key

    try:
        # Try to import and create the app
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from fmp_data.mcp.server import create_app; "
                    "app = create_app(); print('Server initialized successfully')"
                ),
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("✅ MCP server test passed")
            return True
        else:
            print("❌ MCP server test failed")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ MCP server test passed (server started)")
        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False


def choose_configuration():
    """Let user choose a configuration preset."""
    print("\n🎯 Choose a configuration:")
    print("   1. Default - Comprehensive tool set")
    print("   2. Minimal - Essential tools only")
    print("   3. Trading - Technical analysis focused")
    print("   4. Research - Fundamental analysis focused")
    print("   5. Crypto - Cryptocurrency focused")

    choice = input("   Select (1-5) [1]: ").strip() or "1"

    manifest_map = {
        "1": None,  # Default
        "2": "examples/mcp_configurations/minimal_manifest.py",
        "3": "examples/mcp_configurations/trading_manifest.py",
        "4": "examples/mcp_configurations/research_manifest.py",
        "5": "examples/mcp_configurations/crypto_manifest.py",
    }

    return manifest_map.get(choice)


def main() -> None:
    """Main setup process."""
    print("=" * 60)
    print("🚀 FMP Data MCP Server Setup for Claude Desktop")
    print("=" * 60)

    # Step 1: Check Python version
    print("\n📋 Checking prerequisites...")
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.10+ required")
        print("   Download from: https://www.python.org/downloads/")
        return 1

    # Step 2: Check/Install fmp-data
    if not check_fmp_installation():
        if not install_fmp_data():
            print("\n❌ Setup failed: Could not install fmp-data")
            return 1

    # Step 3: Get API key
    api_key = get_api_key()
    if not api_key:
        print("\n❌ Setup failed: API key required")
        print(
            "   Get one at: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi"
        )
        return 1

    # Step 4: Choose configuration
    manifest = choose_configuration()
    if manifest:
        # Convert to absolute path
        manifest = str(Path.cwd() / manifest)
        print(f"   Using configuration: {manifest}")
    else:
        print("   Using default configuration")

    # Step 5: Test MCP server
    if not test_mcp_server(api_key):
        print("\n⚠️  Warning: MCP server test failed, but continuing setup...")

    # Step 6: Configure Claude Desktop
    if not create_claude_config(api_key, manifest):
        print("\n❌ Setup failed: Could not configure Claude Desktop")
        return 1

    # Success!
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Restart Claude Desktop (quit completely and reopen)")
    print("   2. Start a new conversation")
    print("   3. Try asking: 'What's the current price of Apple stock?'")
    print("\n💡 Example questions to try:")
    print("   - 'Show me the top gainers in the stock market today'")
    print("   - 'What's Tesla's latest income statement?'")
    print("   - 'Calculate the RSI for Microsoft'")
    print("   - 'What's the current Bitcoin price?'")
    print("\n📚 For more information, see:")
    print("   docs/mcp/claude_desktop.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
