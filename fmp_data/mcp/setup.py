"""
MCP Setup Module

Interactive setup wizard for configuring FMP Data MCP server with Claude Desktop.
"""

from __future__ import annotations

import sys
from typing import Any

from fmp_data.mcp.utils import (
    add_mcp_server_to_config,
    check_claude_desktop_installed,
    find_python_executable,
    get_api_key_from_env,
    get_claude_config_path,
    get_manifest_choices,
    load_claude_config,
    load_manifest_tools,
    restart_claude_desktop_instructions,
    save_claude_config,
    test_mcp_server,
    validate_api_key,
)


class SetupWizard:
    """Interactive setup wizard for MCP server configuration."""

    def __init__(self, quiet: bool = False):
        """
        Initialize the setup wizard.

        Parameters
        ----------
        quiet
            Run in quiet mode with minimal output
        """
        self.quiet = quiet
        self.api_key: str | None = None
        self.python_path: str | None = None
        self.manifest_path: str | None = None
        self.config: dict[str, Any] = {}

    def _redact_sensitive(self, message: str | None) -> str | None:
        """Redact sensitive information such as API keys from message."""
        if not message:
            return message

        result = message

        # Redact current API key if set
        if self.api_key and self.api_key in result:
            result = result.replace(self.api_key, "[REDACTED]")

        import re

        # First redact URLs with tokens/keys in query parameters (more specific)
        url_patterns = [
            r"([?&](?:api_?key|token|secret)=)[^&\s]+",
            r"([?&]apikey=)[^&\s]+",
        ]

        for pattern in url_patterns:
            result = re.sub(pattern, r"\1[REDACTED]", result)

        # Then redact remaining API key patterns (more general)
        api_key_patterns = [
            r"\b(?:sk-|pk_)[a-zA-Z0-9_-]{8,}\b",  # Keys with sk-/pk- prefixes
            # Standalone api_key assignments (not URLs)
            r"\bapi_key=[a-zA-Z0-9_-]{8,}(?=\s|:|;)",
            r"\b[a-zA-Z0-9]{32,}\b",  # Long alphanumeric strings (32+ chars)
            r"[a-fA-F0-9]{40,}",  # Hex strings 40+ chars (common for tokens)
        ]

        for pattern in api_key_patterns:
            result = re.sub(pattern, "[REDACTED]", result)

        return result

    def print(self, message: str, style: str = "") -> None:
        """Print message unless in quiet mode."""
        if not self.quiet:
            # Redact sensitive info before printing
            redacted = self._redact_sensitive(message)
            message = redacted if redacted is not None else message
            if style == "header":
                print(f"\n{'=' * 60}")
                print(f"🚀 {message}")
                print("=" * 60)
            elif style == "success":
                print(f"✅ {message}")
            elif style == "error":
                print(f"❌ {message}")
            elif style == "warning":
                print(f"⚠️  {message}")
            elif style == "info":
                print(f"💡 {message}")
            else:
                print(message)

    def prompt(self, message: str, default: str | None = None) -> str:
        """
        Prompt user for input.

        Parameters
        ----------
        message
            Prompt message
        default
            Default value if user presses Enter

        Returns
        -------
        str
            User input or default value
        """
        # Redact sensitive information from prompt message and default
        safe_message = self._redact_sensitive(message)
        safe_default = self._redact_sensitive(default) if default else None

        if safe_default:
            prompt_text = f"{safe_message} [{safe_default}]: "
        else:
            prompt_text = f"{safe_message}: "

        response = input(prompt_text).strip()
        return response if response else (default or "")

    def prompt_choice(self, message: str, choices: list[str], default: int = 0) -> int:
        """
        Prompt user to choose from a list of options.

        Parameters
        ----------
        message
            Prompt message
        choices
            List of choice descriptions
        default
            Default choice index

        Returns
        -------
        int
            Selected choice index
        """
        self.print(f"\n{message}")
        for i, choice in enumerate(choices):
            marker = ">" if i == default else " "
            self.print(f"  {marker} {i + 1}. {choice}")

        while True:
            response = input(f"\nSelect (1-{len(choices)}) [{default + 1}]: ").strip()

            if not response:
                return default

            try:
                choice_num = int(response) - 1
                if 0 <= choice_num < len(choices):
                    return choice_num
                else:
                    self.print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                self.print("Please enter a valid number")

    def check_prerequisites(self) -> bool:
        """
        Check if all prerequisites are met.

        Returns
        -------
        bool
            True if prerequisites are met
        """
        self.print("Checking prerequisites...", "info")

        # Check Python version
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            self.print(f"Python 3.10+ required (current: {sys.version})", "error")
            return False
        self.print(f"Python version: {sys.version.split()[0]}", "success")

        # Check if fmp_data is installed
        try:
            import fmp_data  # noqa: F401

            self.print("fmp-data package is installed", "success")
        except ImportError:
            self.print("fmp-data package not installed", "error")
            self.print("Install with: pip install fmp-data[mcp]", "info")
            return False

        # Check if MCP dependencies are installed
        try:
            import mcp  # noqa: F401
            from mcp.server.fastmcp import FastMCP  # noqa: F401

            self.print("MCP dependencies are installed", "success")
        except ImportError:
            self.print("MCP dependencies not installed", "error")
            self.print("Install with: pip install fmp-data[mcp]", "info")
            return False

        # Check if Claude Desktop is installed
        if not check_claude_desktop_installed():
            self.print("Claude Desktop not detected", "warning")
            response = self.prompt("Continue anyway? (y/n)", "n")
            if response.lower() != "y":
                return False
        else:
            self.print("Claude Desktop detected", "success")

        return True

    def setup_api_key(self) -> bool:
        """
        Setup FMP API key.

        Returns
        -------
        bool
            True if API key is configured
        """
        self.print("\n🔑 API Key Configuration", "info")

        # Check for existing API key in environment
        env_key = get_api_key_from_env()
        if env_key:
            self.print("Found FMP_API_KEY in environment", "success")
            use_env = self.prompt("Use API key from environment? (y/n)", "y")
            if use_env.lower() == "y":
                self.api_key = env_key
                return True

        # Prompt for API key
        self.print(
            "\nGet a free API key at: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi"
        )

        while True:
            api_key = self.prompt("Enter your FMP API key").strip()

            if not api_key:
                self.print("API key is required", "error")
                continue

            # Set API key for redaction before validation
            self.api_key = api_key

            # Validate API key
            self.print("Validating API key...", "info")
            valid, message = validate_api_key(api_key)

            if valid:
                self.print("API key validated successfully.", "success")

                # Offer to save to environment
                save_env = self.prompt(
                    "\nSave API key to environment for future use? (y/n)", "n"
                )
                if save_env.lower() == "y":
                    self._show_env_instructions(api_key)

                return True
            else:
                self.print(message, "error")
                retry = self.prompt("Try another key? (y/n)", "y")
                if retry.lower() != "y":
                    # Clear invalid API key
                    self.api_key = None
                    return False

    def _show_env_instructions(self, api_key: str) -> None:
        """Show instructions for saving API key to environment."""
        import platform

        # Show redacted version for security
        redacted_key = (
            f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "[YOUR_API_KEY]"
        )

        system = platform.system()
        if system == "Windows":
            self.print(
                "\nTo save permanently on Windows, run in Command Prompt as "
                "Administrator:"
            )
            self.print(f'  setx FMP_API_KEY "{redacted_key}"')
            self.print("\n💡 Replace the redacted portion with your actual API key")
        else:
            shell_file = "~/.zshrc" if system == "Darwin" else "~/.bashrc"
            self.print(f"\nAdd this line to your {shell_file}:")
            self.print(f'  export FMP_API_KEY="{redacted_key}"')
            self.print("\n💡 Replace the redacted portion with your actual API key")
            self.print(f"\nThen reload with: source {shell_file}")

    def choose_configuration(self) -> bool:
        """
        Choose MCP configuration profile.

        Returns
        -------
        bool
            True if configuration is chosen
        """
        self.print("\n⚙️  Configuration Profile", "info")

        manifest_choices = get_manifest_choices()

        profiles = [
            ("default", "Default", "Comprehensive toolkit"),
            ("minimal", "Minimal", "Essential tools only"),
            ("trading", "Trading", "Trading and technical analysis"),
            ("research", "Research", "Fundamental analysis and research"),
            ("crypto", "Crypto", "Cryptocurrency focused"),
        ]

        # Only show choices that have available manifests
        available_choices = []
        available_keys = []

        for key, label, suffix in profiles:
            if key not in manifest_choices:
                continue
            try:
                count = len(load_manifest_tools(manifest_choices[key]))
                desc = f"{label} ({count} tools) - {suffix}"
            except Exception:
                desc = f"{label} - {suffix}"
            available_choices.append(desc)
            available_keys.append(key)

        if len(available_choices) == 1:
            self.print("Using default configuration", "info")
            self.manifest_path = None
            return True

        choice_idx = self.prompt_choice(
            "Choose configuration profile:", available_choices, default=0
        )

        selected_key = available_keys[choice_idx]
        self.manifest_path = manifest_choices[selected_key]

        if self.manifest_path:
            self.print(f"Using {selected_key} configuration", "success")
        else:
            self.print("Using default configuration", "success")

        return True

    def find_python(self) -> bool:
        """
        Find Python executable.

        Returns
        -------
        bool
            True if Python is found
        """
        self.print("\n🐍 Finding Python executable...", "info")

        python_path = find_python_executable()
        self.print(f"Found Python: {python_path}", "success")

        # Verify it can import fmp_data
        import subprocess

        try:
            result = subprocess.run(
                [python_path, "-c", "import fmp_data"], capture_output=True, timeout=5
            )
            if result.returncode != 0:
                self.print("Python can't import fmp_data", "error")
                self.print("Using current Python instead", "info")
                python_path = sys.executable
        except Exception:
            self.print("Using current Python", "info")
            python_path = sys.executable

        self.python_path = python_path
        return True

    def update_claude_config(self) -> bool:
        """
        Update Claude Desktop configuration.

        Returns
        -------
        bool
            True if configuration is updated
        """
        self.print("\n📝 Updating Claude Desktop configuration...", "info")

        # Load existing configuration
        self.config = load_claude_config()

        if self.config:
            self.print("Found existing Claude configuration", "success")

            # Check if fmp-data is already configured
            if "mcpServers" in self.config and "fmp-data" in self.config["mcpServers"]:
                overwrite = self.prompt(
                    "FMP Data server already configured. Overwrite? (y/n)", "y"
                )
                if overwrite.lower() != "y":
                    return False
        else:
            self.print("Creating new Claude configuration", "info")

        # Add MCP server configuration
        if self.python_path is None:
            self.print("Python path not set", "error")
            return False
        if self.api_key is None:
            self.print("API key not set", "error")
            return False

        self.config = add_mcp_server_to_config(
            self.config, "fmp-data", self.python_path, self.api_key, self.manifest_path
        )

        # Save configuration with backup
        config_path = get_claude_config_path()
        backup_path = save_claude_config(self.config, backup=True)

        self.print(f"Configuration saved to: {config_path}", "success")
        if backup_path:
            self.print(f"Backup created at: {backup_path}", "info")

        return True

    def test_server(self) -> bool:
        """
        Test MCP server connection.

        Returns
        -------
        bool
            True if server test passes
        """
        self.print("\n🧪 Testing MCP server...", "info")

        if self.api_key is None:
            self.print("API key not set, skipping test", "warning")
            return True

        success, message = test_mcp_server(self.api_key, self.manifest_path)

        if success:
            self.print(message, "success")
        else:
            self.print(message, "error")
            self.print("The server may still work with Claude Desktop", "warning")

        return success

    def show_next_steps(self) -> None:
        """Show next steps to complete setup."""
        self.print("\nSetup Complete!", "header")

        self.print("\n📋 Next Steps:")
        self.print("1. Restart Claude Desktop completely")
        self.print("2. Start a new conversation")
        self.print("3. Test with: 'What's the current price of AAPL?'")

        self.print("\n💡 Example queries to try:")
        self.print("  • 'Show me today's top gainers'")
        self.print("  • 'Get Tesla's latest income statement'")
        self.print("  • 'What's the RSI for Microsoft?'")
        self.print("  • 'Show me Bitcoin's current price'")

        self.print("\n" + restart_claude_desktop_instructions())

    def run(self) -> bool:
        """
        Run the setup wizard.

        Returns
        -------
        bool
            True if setup completes successfully
        """
        self.print("FMP Data MCP Setup for Claude Desktop", "header")

        # Check prerequisites
        if not self.check_prerequisites():
            return False

        # Setup API key
        if not self.setup_api_key():
            self.print("Setup cancelled", "warning")
            return False

        # Choose configuration
        if not self.choose_configuration():
            return False

        # Find Python
        if not self.find_python():
            return False

        # Test server
        if not self.test_server():
            continue_anyway = self.prompt("Continue with setup anyway? (y/n)", "y")
            if continue_anyway.lower() != "y":
                return False

        # Update Claude configuration
        if not self.update_claude_config():
            return False

        # Show next steps
        self.show_next_steps()

        return True


def run_setup(quiet: bool = False) -> int:
    """
    Run the MCP setup wizard.

    Parameters
    ----------
    quiet
        Run in quiet mode

    Returns
    -------
    int
        Exit code (0 for success)
    """
    wizard = SetupWizard(quiet=quiet)

    try:
        if wizard.run():
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        wizard.print("\n\nSetup cancelled by user", "warning")
        return 1
    except Exception as e:
        # Use the existing wizard for error output with redaction
        # If wizard is not available, create a temporary one with enhanced redaction
        try:
            wizard.print(f"Setup failed: {e}", "error")
        except Exception:
            # Fallback: create temp wizard and copy API key if available
            temp_wizard = SetupWizard(quiet=False)
            api_key = getattr(wizard, "api_key", None)
            if api_key is not None:
                temp_wizard.api_key = api_key
            temp_wizard.print(f"Setup failed: {e}", "error")
        return 1


if __name__ == "__main__":
    sys.exit(run_setup())
