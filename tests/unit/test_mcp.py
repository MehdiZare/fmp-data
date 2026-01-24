# tests/unit/test_mcp.py - Fixed tests
"""
Basic tests for MCP server functionality.

Relative path: tests/unit/test_mcp.py
"""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("mcp", reason="MCP dependencies not installed")
pytest.importorskip("mcp.server.fastmcp", reason="FastMCP not available")


class TestMCPServer:
    """Test suite for MCP server functionality."""

    @patch.dict(os.environ, {"FMP_API_KEY": "test_key"})
    @patch("fmp_data.mcp.server.register_from_manifest")
    @patch("fmp_data.mcp.server.FMPDataClient")
    def test_create_app_default_tools(self, mock_client_class, mock_register):
        """Test creating MCP app with default tools."""
        from fmp_data.mcp.server import create_app

        mock_client = Mock()
        mock_client_class.from_env.return_value = mock_client

        app = create_app()

        assert app is not None
        assert app.name == "fmp-data"
        # FastMCP doesn't have a description attribute, just check basic functionality
        mock_client_class.from_env.assert_called_once()
        mock_register.assert_called_once()

    @patch.dict(os.environ, {"FMP_API_KEY": "test_key"})
    @patch("fmp_data.mcp.server.register_from_manifest")
    @patch("fmp_data.mcp.server.FMPDataClient")
    def test_create_app_custom_tools(self, mock_client_class, mock_register):
        """Test creating MCP app with custom tool list."""
        from fmp_data.mcp.server import create_app

        mock_client = Mock()
        mock_client_class.from_env.return_value = mock_client

        custom_tools = ["company.profile", "company.market_cap"]
        app = create_app(tools=custom_tools)

        assert app is not None
        mock_client_class.from_env.assert_called_once()
        mock_register.assert_called_once()

    def test_tool_iterable_type_alias(self):
        """Test that ToolIterable type alias works correctly."""
        from fmp_data.mcp.server import ToolIterable

        # Test with different types
        str_tools: ToolIterable = "company.profile"
        list_tools: ToolIterable = ["company.profile", "company.market_cap"]
        tuple_tools: ToolIterable = ("company.profile", "company.market_cap")

        assert isinstance(str_tools, str)
        assert isinstance(list_tools, list)
        assert isinstance(tuple_tools, tuple)


class TestToolLoader:
    """Test suite for MCP tool loader functionality."""

    def test_resolve_attr_success(self):
        """Test successful attribute resolution."""
        from fmp_data.mcp.tool_loader import _resolve_attr

        # Create a mock object with nested attributes and proper callable
        mock_obj = Mock()
        mock_method = Mock()
        mock_method.__name__ = "test_method"  # Add required __name__ attribute
        mock_obj.client.method = mock_method

        result = _resolve_attr(mock_obj, "client.method")
        assert callable(result)
        assert result.__name__ is not None

    def test_resolve_attr_missing_attribute(self):
        """Test attribute resolution failure."""
        from fmp_data.mcp.tool_loader import _resolve_attr

        # Use a real object instead of Mock to test missing attributes
        class TestObj:
            def __init__(self):
                self.client = Mock()
                # Don't add the missing_method

        test_obj = TestObj()
        # Ensure the attribute really doesn't exist
        del test_obj.client.missing_method

        with pytest.raises(RuntimeError, match="Attribute chain .* failed"):
            _resolve_attr(test_obj, "client.missing_method")

    def test_resolve_attr_not_callable(self):
        """Test resolution of non-callable attribute."""
        from fmp_data.mcp.tool_loader import _resolve_attr

        mock_obj = Mock()
        mock_obj.client.data = "not_callable"

        with pytest.raises(RuntimeError, match=".* is not callable"):
            _resolve_attr(mock_obj, "client.data")

    @patch("fmp_data.mcp.tool_loader.importlib.import_module")
    def test_load_semantics_missing_module(self, mock_import):
        """Test loading semantics with missing module."""
        from fmp_data.mcp.tool_loader import _load_semantics

        mock_import.side_effect = ModuleNotFoundError("No module found")

        with pytest.raises(RuntimeError, match="No mapping module"):
            _load_semantics("nonexistent", "profile")

    @patch("fmp_data.mcp.tool_loader.importlib.import_module")
    def test_load_semantics_missing_table(self, mock_import):
        """Test loading semantics with missing semantics table."""
        from fmp_data.mcp.tool_loader import _load_semantics

        # Create a mock module that definitely doesn't have the attribute
        mock_module = Mock(spec=[])  # Empty spec means no attributes
        mock_import.return_value = mock_module

        with pytest.raises(RuntimeError, match="lacks.*ENDPOINTS_SEMANTICS"):
            _load_semantics("company", "profile")

    def test_register_from_manifest_duplicate_keys_raises(self):
        """Ensure duplicate semantic keys are rejected when using key names."""
        from fmp_data.mcp.tool_loader import register_from_manifest

        mcp = Mock()
        fmp_client = Mock()
        tool_specs = [
            "fundamental.financial_reports_dates",
            "intelligence.financial_reports_dates",
        ]

        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "key"}):
            with patch("fmp_data.mcp.discovery.discover_all_tools", return_value=[]):
                with pytest.raises(RuntimeError, match="Duplicate tool keys"):
                    register_from_manifest(mcp, fmp_client, tool_specs)

    def test_register_from_manifest_name_style_spec(self):
        """Ensure tool names use fully-qualified specs when configured."""
        from fmp_data.client import FMPDataClient
        from fmp_data.mcp.tool_loader import register_from_manifest

        sem = SimpleNamespace(method_name="get_profile", natural_description="Profile")
        fmp_client = Mock(spec=FMPDataClient)
        fmp_client.company = SimpleNamespace(get_profile=Mock())
        mcp = Mock()

        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "spec"}):
            with (
                patch("fmp_data.mcp.tool_loader._load_semantics", return_value=sem),
                patch(
                    "fmp_data.mcp.discovery.discover_all_tools",
                    return_value=[{"spec": "company.profile", "key": "profile"}],
                ),
            ):
                register_from_manifest(mcp, fmp_client, ["company.profile"])

        mcp.add_tool.assert_called_once()
        _, kwargs = mcp.add_tool.call_args
        assert kwargs["name"] == "company.profile"


class TestToolsManifest:
    """Test suite for tools manifest."""

    def test_default_tools_structure(self):
        """Test that default tools follow expected format."""
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        assert isinstance(DEFAULT_TOOLS, list)
        assert len(DEFAULT_TOOLS) > 0

        for tool in DEFAULT_TOOLS:
            assert isinstance(tool, str)
            assert "." in tool, f"Tool {tool} should be in 'client.method' format"
            parts = tool.split(".")
            assert len(parts) == 2, f"Tool {tool} should have exactly one dot"

    def test_default_tools_content(self):
        """Test that default tools contain expected entries."""
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        # Check for some expected tools
        expected_tools = [
            "company.profile",
            "company.market_cap",
            "alternative.crypto_quote",
            "company.historical_price",
        ]

        for tool in expected_tools:
            assert (
                tool in DEFAULT_TOOLS
            ), f"Expected tool {tool} not found in DEFAULT_TOOLS"


class TestMCPManifestLoading:
    """Test suite for manifest loading utilities."""

    def test_load_manifest_tools_from_file(self, tmp_path):
        """Load tool specs from a manifest file."""
        from fmp_data.mcp.utils import load_manifest_tools

        manifest = tmp_path / "manifest.py"
        manifest.write_text('TOOLS = ["company.profile", "market.gainers"]')

        tools = load_manifest_tools(manifest)
        assert tools == ["company.profile", "market.gainers"]

    def test_load_manifest_tools_missing_tools(self, tmp_path):
        """Missing TOOLS should raise."""
        from fmp_data.mcp.utils import load_manifest_tools

        manifest = tmp_path / "manifest.py"
        manifest.write_text("X = 1")

        with pytest.raises(AttributeError, match="does not define"):
            load_manifest_tools(manifest)


@pytest.mark.integration
class TestMCPIntegration:
    """Integration tests for MCP server (requires API key)."""

    @pytest.mark.skipif(
        not os.getenv("FMP_TEST_API_KEY"), reason="FMP_TEST_API_KEY not set"
    )
    @patch.dict(os.environ, {"FMP_API_KEY": os.getenv("FMP_TEST_API_KEY", "")})
    def test_mcp_server_with_real_client(self):
        """Test MCP server creation with real FMP client."""
        from fmp_data.mcp.server import create_app

        try:
            app = create_app(tools=["company.profile"])
            assert app is not None
            # Tools are registered via MCP protocol, not directly inspectable
            # Successful creation without errors indicates tools were registered
        except Exception as e:
            pytest.fail(f"Failed to create MCP app with real client: {e}")

    def test_mcp_server_no_api_key(self):
        """Test MCP server behavior without API key."""
        from fmp_data.exceptions import ConfigError
        from fmp_data.mcp.server import create_app

        # Ensure no API key is set
        with patch.dict(os.environ, {}, clear=True):
            if "FMP_API_KEY" in os.environ:
                del os.environ["FMP_API_KEY"]

            with pytest.raises(ConfigError):  # Should fail without API key
                create_app()


class TestMCPSetupSecurity:
    """Test security features in MCP setup."""

    def test_api_key_redaction(self):
        """Test that API keys are properly redacted in setup messages."""
        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()
        setup.api_key = "sk-test-12345abcdef"

        # Test that sensitive info is redacted
        test_message = "Your API key sk-test-12345abcdef is valid"
        redacted = setup._redact_sensitive(test_message)

        assert "sk-test-12345abcdef" not in redacted
        assert "[REDACTED]" in redacted
        assert redacted == "Your API key [REDACTED] is valid"

    def test_api_key_redaction_no_key_set(self):
        """Test redaction when no API key is set."""
        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()
        # No API key set

        test_message = "Some message without api key"
        redacted = setup._redact_sensitive(test_message)

        # Should return original message unchanged
        assert redacted == test_message

    def test_pattern_based_api_key_redaction(self):
        """Test that common API key patterns are redacted."""
        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()

        test_cases = [
            # Test various API key patterns
            ("API key: sk-1234567890abcdef1234567890", "API key: [REDACTED]"),
            ("Token: pk_test_1234567890abcdef1234567890abcdef", "Token: [REDACTED]"),
            (
                "Key: api_key=abcdef1234567890abcdef1234567890abcdef",
                "Key: api_key=[REDACTED]",
            ),  # Preserves parameter name
            (
                "Long key: 1234567890abcdef1234567890abcdef1234567890abcdef",
                "Long key: [REDACTED]",
            ),
            (
                "Hex token: abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "Hex token: [REDACTED]",
            ),
        ]

        for original, expected in test_cases:
            redacted = setup._redact_sensitive(original)
            assert redacted == expected, f"Failed for: {original}"

    def test_url_parameter_redaction(self):
        """Test that API keys in URL parameters are redacted."""
        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()

        test_cases = [
            (
                "URL: https://api.example.com/data?api_key=secret123&symbol=AAPL",
                "URL: https://api.example.com/data?api_key=[REDACTED]&symbol=AAPL",
            ),
            (
                "Call: https://fmp.com/api?apikey=mysecret&endpoint=profile",
                "Call: https://fmp.com/api?apikey=[REDACTED]&endpoint=profile",
            ),
            (
                "Auth: https://api.com?token=abc123def456&format=json",
                "Auth: https://api.com?token=[REDACTED]&format=json",
            ),
        ]

        for original, expected in test_cases:
            redacted = setup._redact_sensitive(original)
            assert redacted == expected, f"Failed for: {original}"

    def test_empty_and_none_message_handling(self):
        """Test that empty and None messages are handled safely."""
        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()

        # Test empty string
        assert setup._redact_sensitive("") == ""

        # Test None (should not crash)
        assert setup._redact_sensitive(None) is None

    def test_prompt_redaction(self):
        """Test that prompt method redacts sensitive information."""
        from unittest.mock import patch

        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard()
        setup.api_key = "secret123key"

        # Mock input to avoid actual user interaction
        with patch("builtins.input", return_value="test_response"):
            # Test that prompt message is redacted
            with patch.object(
                setup, "_redact_sensitive", return_value="safe_message"
            ) as mock_redact:
                setup.prompt("Enter your secret123key here", "default_value")

                # Verify redaction was called on both message and default
                assert mock_redact.call_count == 2
                mock_redact.assert_any_call("Enter your secret123key here")
                mock_redact.assert_any_call("default_value")

    def test_print_method_always_redacts(self):
        """Test that all print method calls apply redaction."""
        import io
        from unittest.mock import patch

        from fmp_data.mcp.setup import SetupWizard

        setup = SetupWizard(quiet=False)
        setup.api_key = "secret123"

        # Capture stdout
        captured_output = io.StringIO()

        with patch("sys.stdout", captured_output):
            setup.print("Your API key secret123 is valid", "info")

        output = captured_output.getvalue()
        assert "secret123" not in output
        assert "[REDACTED]" in output

    def test_exception_handling_security(self):
        """Test that exception handling doesn't expose sensitive data."""
        import io
        from unittest.mock import patch

        from fmp_data.mcp.setup import run_setup

        # Mock an exception that might contain sensitive data
        sensitive_error = Exception("Error with api_key=secret123: connection failed")

        captured_output = io.StringIO()

        with patch("sys.stdout", captured_output):
            with patch(
                "fmp_data.mcp.setup.SetupWizard.run", side_effect=sensitive_error
            ):
                result = run_setup(quiet=False)

        output = captured_output.getvalue()
        # Should not contain the raw API key (pattern-based redaction should catch it)
        assert "secret123" not in output
        assert "[REDACTED]" in output or "Setup failed" in output
        assert result == 1  # Should return error code
