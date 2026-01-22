"""
Tests for MCP CLI functionality.

Relative path: tests/unit/test_mcp_cli.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

import pytest

# Skip if MCP dependencies not available
pytest.importorskip("mcp", reason="MCP dependencies not installed")


class TestMCPDiscovery:
    """Test suite for MCP tool discovery functionality."""

    def test_get_client_modules_includes_core(self):
        """Ensure dynamic client discovery includes core modules."""
        from fmp_data.mcp.discovery import _get_client_modules

        modules = _get_client_modules()

        assert "company" in modules
        assert "market" in modules
        assert "fundamental" in modules
        assert "mcp" not in modules
        assert "lc" not in modules

    @patch("fmp_data.mcp.discovery.importlib.import_module")
    def test_discover_client_tools(self, mock_import):
        """Test discovering tools for a specific client."""
        from fmp_data.mcp.discovery import discover_client_tools

        # Mock the mapping module
        mock_module = Mock()
        mock_semantics = Mock()
        mock_semantics.method_name = "get_profile"
        mock_semantics.natural_description = "Get company profile"
        mock_semantics.example_queries = ["Get Apple profile"]
        mock_semantics.related_terms = ["company", "profile"]

        mock_module.COMPANY_ENDPOINTS_SEMANTICS = {"profile": mock_semantics}
        mock_import.return_value = mock_module

        # Test with company client
        company_tools = discover_client_tools("company")
        assert isinstance(company_tools, list)
        assert len(company_tools) > 0

        # Check tool structure
        tool = company_tools[0]
        assert tool["spec"] == "company.profile"
        assert tool["client"] == "company"
        assert tool["method"] == "get_profile"
        assert tool["description"] == "Get company profile"

    @patch("fmp_data.mcp.discovery._get_client_modules")
    @patch("fmp_data.mcp.discovery.discover_client_tools")
    def test_discover_all_tools(self, mock_discover, mock_clients):
        """Test discovering all available tools."""
        from fmp_data.mcp.discovery import discover_all_tools

        mock_clients.return_value = ["company", "market"]
        mock_discover.side_effect = [
            [
                {
                    "spec": "company.profile",
                    "client": "company",
                    "method": "get_profile",
                    "description": "Profile",
                }
            ],
            [
                {
                    "spec": "market.gainers",
                    "client": "market",
                    "method": "get_gainers",
                    "description": "Gainers",
                }
            ],
        ]

        all_tools = discover_all_tools()
        assert isinstance(all_tools, list)
        assert len(all_tools) == 2

        # Check that multiple clients are represented
        clients = {tool["client"] for tool in all_tools}
        assert len(clients) == 2
        assert "company" in clients
        assert "market" in clients

    @patch("fmp_data.mcp.discovery.discover_client_tools")
    def test_get_tool_by_spec(self, mock_discover):
        """Test getting a specific tool by its spec."""
        from fmp_data.mcp.discovery import get_tool_by_spec

        # Mock tool discovery
        mock_discover.return_value = [
            {
                "spec": "company.profile",
                "client": "company",
                "method": "get_profile",
                "description": "Profile",
            }
        ]

        # Test with known tool
        tool = get_tool_by_spec("company.profile")
        assert tool is not None
        assert tool["spec"] == "company.profile"
        assert tool["client"] == "company"

        # Test with invalid spec
        tool = get_tool_by_spec("invalid.spec")
        assert tool is None

        # Test with malformed spec
        tool = get_tool_by_spec("invalid_format")
        assert tool is None

    @patch("fmp_data.mcp.discovery.discover_all_tools")
    def test_search_tools(self, mock_discover):
        """Test searching for tools by query."""
        from fmp_data.mcp.discovery import search_tools

        # Mock tools
        mock_discover.return_value = [
            {
                "spec": "company.profile",
                "client": "company",
                "method": "get_profile",
                "description": "Get company profile",
                "example_queries": [],
                "related_terms": [],
            },
            {
                "spec": "alternative.crypto_quote",
                "client": "alternative",
                "method": "get_crypto_quote",
                "description": "Get cryptocurrency quote",
                "example_queries": [],
                "related_terms": [],
            },
        ]

        # Search for profile-related tools
        results = search_tools("profile")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["spec"] == "company.profile"

        # Search for crypto-related tools
        results = search_tools("crypto")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["spec"] == "alternative.crypto_quote"

    @patch("fmp_data.mcp.discovery.discover_all_tools")
    def test_get_recommended_tools(self, mock_discover):
        """Test getting recommended tools."""
        from fmp_data.mcp.discovery import get_recommended_tools

        # Mock available tools
        mock_discover.return_value = [
            {"spec": "company.profile", "client": "company"},
            {"spec": "market.gainers", "client": "market"},
            {"spec": "alternative.crypto_quote", "client": "alternative"},
        ]

        recommended = get_recommended_tools()
        assert isinstance(recommended, list)
        # Should return only the tools that exist in our mock
        assert "company.profile" in recommended
        assert "market.gainers" in recommended
        assert all(isinstance(spec, str) for spec in recommended)

        # Check format
        for spec in recommended:
            assert "." in spec
            parts = spec.split(".")
            assert len(parts) >= 2

    @patch("fmp_data.mcp.discovery.discover_all_tools")
    def test_group_tools_by_category(self, mock_discover):
        """Test grouping tools by category."""
        from fmp_data.mcp.discovery import group_tools_by_category

        # Mock tools
        mock_discover.return_value = [
            {"spec": "company.profile", "client": "company", "method": "get_profile"},
            {"spec": "company.quote", "client": "company", "method": "get_quote"},
            {"spec": "market.gainers", "client": "market", "method": "get_gainers"},
        ]

        grouped = group_tools_by_category()
        assert isinstance(grouped, dict)
        assert len(grouped) == 2
        assert "company" in grouped
        assert "market" in grouped
        assert len(grouped["company"]) == 2
        assert len(grouped["market"]) == 1

        # Check structure
        for client, tools in grouped.items():
            assert isinstance(client, str)
            assert isinstance(tools, list)
            assert all(tool["client"] == client for tool in tools)


class TestMCPCLI:
    """Test suite for MCP CLI commands."""

    @patch("fmp_data.mcp.discovery.discover_all_tools")
    def test_list_available_tools(self, mock_discover):
        """Test listing available tools."""
        from fmp_data.mcp.cli import list_available_tools

        # Mock discovery
        mock_discover.return_value = [
            {
                "spec": "test.tool",
                "client": "test",
                "method": "test_method",
                "description": "Test",
            }
        ]

        tools = list_available_tools()
        assert isinstance(tools, list)
        assert len(tools) == 1

        # Check tool structure
        tool = tools[0]
        assert tool["spec"] == "test.tool"
        assert tool["client"] == "test"
        assert tool["method"] == "test_method"
        assert tool["description"] == "Test"

    @patch("builtins.print")
    def test_print_tools_table_json(self, mock_print):
        """Test printing tools in JSON format."""
        from fmp_data.mcp.cli import print_tools_table

        tools = [
            {
                "spec": "test.tool",
                "client": "test",
                "method": "get_test",
                "description": "Test tool",
            }
        ]

        print_tools_table(tools, format="json")
        mock_print.assert_called_once()

        # Check JSON output
        call_args = mock_print.call_args[0][0]
        parsed = json.loads(call_args)
        assert parsed == tools

    @patch("builtins.print")
    def test_print_tools_table_list(self, mock_print):
        """Test printing tools in list format."""
        from fmp_data.mcp.cli import print_tools_table

        tools = [
            {
                "spec": "test.tool",
                "client": "test",
                "method": "get_test",
                "description": "Test tool",
            }
        ]

        print_tools_table(tools, format="list")
        mock_print.assert_called_once_with("test.tool: Test tool")

    @patch("fmp_data.mcp.cli.list_available_tools")
    def test_generate_manifest(self, mock_list_tools):
        """Test generating a manifest file."""
        from fmp_data.mcp.cli import generate_manifest

        # Mock available tools
        mock_list_tools.return_value = [
            {"spec": "company.profile", "client": "company"},
            {"spec": "market.gainers", "client": "market"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Generate manifest with specific tools
            generate_manifest(
                temp_path,
                tools=["company.profile", "market.gainers"],
                include_defaults=False,
            )

            # Check file was created
            assert temp_path.exists()

            # Check content
            content = temp_path.read_text()
            assert "TOOLS = [" in content
            assert '"company.profile"' in content
            assert '"market.gainers"' in content

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_validate_manifest_valid(self):
        """Test validating a valid manifest."""
        from fmp_data.mcp.cli import validate_manifest

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('TOOLS = ["company.profile", "market.gainers"]')
            temp_path = Path(f.name)

        try:
            result = validate_manifest(temp_path)
            assert result is True

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_validate_manifest_invalid(self):
        """Test validating an invalid manifest."""
        from fmp_data.mcp.cli import validate_manifest

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# No TOOLS variable")
            temp_path = Path(f.name)

        try:
            result = validate_manifest(temp_path)
            assert result is False

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_validate_manifest_nonexistent(self):
        """Test validating a non-existent manifest."""
        from fmp_data.mcp.cli import validate_manifest

        result = validate_manifest("/nonexistent/path.py")
        assert result is False


class TestMCPMain:
    """Test suite for MCP __main__ module."""

    @patch("fmp_data.mcp.__main__.create_app")
    @patch.dict(os.environ, {"FMP_API_KEY": "test_key"})
    def test_main_default_tools(self, mock_create_app):
        """Test running main with default tools."""
        from fmp_data.mcp.__main__ import main

        mock_app = Mock()
        mock_create_app.return_value = mock_app

        with patch("builtins.print"):
            main()

        mock_create_app.assert_called_once_with()
        mock_app.run.assert_called_once()

    @patch("fmp_data.mcp.__main__.create_app")
    @patch.dict(os.environ, {"FMP_API_KEY": "test_key"})
    def test_main_custom_manifest(self, mock_create_app):
        """Test running main with custom manifest."""
        from fmp_data.mcp.__main__ import main

        mock_app = Mock()
        mock_create_app.return_value = mock_app

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('TOOLS = ["company.profile"]')
            temp_path = Path(f.name)

        try:
            with patch.dict(os.environ, {"FMP_MCP_MANIFEST": str(temp_path)}):
                with patch("builtins.print"):
                    main()

            # Check that create_app was called with the resolved path
            mock_create_app.assert_called_once()
            call_args = mock_create_app.call_args
            assert call_args[1]["tools"].endswith(".py")
            mock_app.run.assert_called_once()

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_main_no_api_key(self):
        """Test running main without API key."""
        from fmp_data.mcp.__main__ import main

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_invalid_manifest(self):
        """Test running main with invalid manifest path."""
        from fmp_data.mcp.__main__ import main

        with patch.dict(
            os.environ,
            {"FMP_API_KEY": "test_key", "FMP_MCP_MANIFEST": "/nonexistent/manifest.py"},
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1


class TestMCPCLIMain:
    """Test suite for MCP CLI main entry point."""

    @patch("fmp_data.mcp.cli.list_available_tools")
    @patch("fmp_data.mcp.cli.print_tools_table")
    def test_cli_list_command(self, mock_print_table, mock_list_tools):
        """Test CLI list command."""
        from fmp_data.mcp.cli import main

        mock_list_tools.return_value = [
            {
                "spec": "test.tool",
                "client": "test",
                "method": "test",
                "description": "Test",
            }
        ]

        with patch("sys.argv", ["fmp-mcp", "list"]):
            main()

        mock_list_tools.assert_called_once()
        mock_print_table.assert_called_once()

    @patch("fmp_data.mcp.cli.generate_manifest")
    def test_cli_generate_command(self, mock_generate):
        """Test CLI generate command."""
        from fmp_data.mcp.cli import main

        with patch("sys.argv", ["fmp-mcp", "generate", "output.py"]):
            main()

        mock_generate.assert_called_once_with("output.py", None, True)

    @patch("fmp_data.mcp.cli.validate_manifest")
    def test_cli_validate_command(self, mock_validate):
        """Test CLI validate command."""
        from fmp_data.mcp.cli import main

        mock_validate.return_value = True

        with patch("sys.argv", ["fmp-mcp", "validate", "manifest.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

        mock_validate.assert_called_once_with("manifest.py")

    @patch("fmp_data.mcp.cli.serve_with_manifest")
    def test_cli_serve_command(self, mock_serve):
        """Test CLI serve command."""
        from fmp_data.mcp.cli import main

        with patch("sys.argv", ["fmp-mcp", "serve", "--manifest", "custom.py"]):
            main()

        mock_serve.assert_called_once_with("custom.py")
