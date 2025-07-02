# tests/unit/test_mcp.py - Fixed tests
"""
Basic tests for MCP server functionality.

Relative path: tests/unit/test_mcp.py
"""
from __future__ import annotations

import os
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
        assert hasattr(result, "__name__")

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
            # Check if the app has tools registered (use _tools instead of tools)
            assert hasattr(app, "_tool_manager")
            assert len(app._tool_manager._tools) > 0
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
