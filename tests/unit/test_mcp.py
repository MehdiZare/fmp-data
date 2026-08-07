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

from fmp_data.mcp._compat import mcp_server_available

if not mcp_server_available():
    pytest.skip("No supported MCP server class available", allow_module_level=True)


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
        # The server class has no description attribute; check basic wiring only
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

        with pytest.raises(RuntimeError, match=r"Attribute chain .* failed"):
            _resolve_attr(test_obj, "client.missing_method")

    def test_resolve_attr_not_callable(self):
        """Test resolution of non-callable attribute."""
        from fmp_data.mcp.tool_loader import _resolve_attr

        mock_obj = Mock()
        mock_obj.client.data = "not_callable"

        with pytest.raises(RuntimeError, match=r".* is not callable"):
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

        with pytest.raises(RuntimeError, match=r"lacks.*ENDPOINTS_SEMANTICS"):
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
            assert tool in DEFAULT_TOOLS, (
                f"Expected tool {tool} not found in DEFAULT_TOOLS"
            )


@pytest.fixture(scope="module")
def live_client():
    """A real (unauthenticated) client used only for attribute resolution."""
    from fmp_data.client import FMPDataClient

    client = FMPDataClient(api_key="dummy-key-for-attribute-resolution")
    try:
        yield client
    finally:
        client.close()


class TestSemanticsMethodResolution:
    """Guard against mapping drift between semantics and client methods."""

    def test_every_semantics_method_resolves_on_client(self, live_client):
        """Every discovered tool must resolve to a callable on the client.

        Mapping drift (a ``method_name`` that no client method implements)
        makes ``register_from_manifest`` fail at runtime even though the tool
        shows up in discovery. See issues #114 and #115.
        """
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tool_loader import _resolve_attr

        tools = discover_all_tools()
        assert tools, (
            "discover_all_tools() returned no tools — semantics modules failed to "
            "import (check that fmp_data.lc.models is importable without the "
            "langchain extra)"
        )

        failures = []
        for tool in tools:
            dotted = f"{tool['client']}.{tool['method']}"
            try:
                _resolve_attr(live_client, dotted)
            except RuntimeError as exc:
                failures.append(f"{tool['spec']} -> {dotted}: {exc}")

        assert not failures, "Unresolvable semantics method names:\n" + "\n".join(
            failures
        )

    def test_search_method_names_pair_with_semantics(self):
        """Endpoint-map keys that are not get_* must still pair with semantics.

        Renaming map keys to real client methods (search_crowdfunding, etc.)
        broke the old get_-prefix-only LC join heuristic. Pairing must also
        match EndpointSemantics.method_name.
        """
        from fmp_data.institutional.mapping import INSTITUTIONAL_ENDPOINTS_SEMANTICS
        from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS
        from fmp_data.lc import resolve_semantics_for_endpoint
        from fmp_data.market.mapping import MARKET_ENDPOINTS_SEMANTICS

        cases = [
            (
                "search_crowdfunding",
                INTELLIGENCE_ENDPOINTS_SEMANTICS,
                "crowdfunding_search",
            ),
            (
                "search_equity_offering",
                INTELLIGENCE_ENDPOINTS_SEMANTICS,
                "equity_offering_search",
            ),
            (
                "search_cik_by_name",
                INSTITUTIONAL_ENDPOINTS_SEMANTICS,
                "cik_mapper_by_name",
            ),
            ("get_cik_mappings", INSTITUTIONAL_ENDPOINTS_SEMANTICS, "cik_mappings"),
            ("search_company", MARKET_ENDPOINTS_SEMANTICS, "search"),
            (
                "get_ratings_snapshot",
                INTELLIGENCE_ENDPOINTS_SEMANTICS,
                "ratings_snapshot",
            ),
        ]
        for endpoint_name, semantics_map, expected_key in cases:
            sem = resolve_semantics_for_endpoint(endpoint_name, semantics_map)
            assert sem is not None, f"No semantics for {endpoint_name}"
            assert sem.method_name == endpoint_name
            # Confirm we found the expected alias entry (key may differ)
            assert semantics_map[expected_key] is sem

    def test_intelligence_semantics_resolve_on_intelligence_client(self, live_client):
        """Intelligence semantics must only advertise intelligence methods."""
        from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS
        from fmp_data.mcp.tool_loader import _resolve_attr

        failures = []
        for key, sem in INTELLIGENCE_ENDPOINTS_SEMANTICS.items():
            assert sem.client_name == "intelligence", (
                f"Semantics '{key}' declares client_name={sem.client_name!r}"
            )
            try:
                _resolve_attr(live_client, f"intelligence.{sem.method_name}")
            except RuntimeError as exc:
                failures.append(f"{key} -> {sem.method_name}: {exc}")

        assert not failures, "Ghost intelligence semantics:\n" + "\n".join(failures)

    def test_no_ghost_intelligence_semantics(self):
        """Methods owned by other clients must not be re-declared here."""
        from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS

        ghosts = {"institutional_holders", "financial_reports_dates"}
        overlap = ghosts & set(INTELLIGENCE_ENDPOINTS_SEMANTICS)
        assert not overlap, (
            f"Intelligence semantics re-declare other clients' tools: {sorted(overlap)}"
        )

    def test_endpoint_map_keys_match_semantics_method_names(self):
        """Intelligence endpoint-map keys are method names, not aliases."""
        from fmp_data.intelligence.mapping import (
            INTELLIGENCE_ENDPOINT_MAP,
            INTELLIGENCE_ENDPOINTS_SEMANTICS,
        )

        missing = [
            f"{key} -> {sem.method_name}"
            for key, sem in INTELLIGENCE_ENDPOINTS_SEMANTICS.items()
            if sem.method_name not in INTELLIGENCE_ENDPOINT_MAP
        ]
        assert not missing, (
            "Semantics without an INTELLIGENCE_ENDPOINT_MAP entry:\n"
            + "\n".join(missing)
        )

    def test_discovered_tool_keys_are_unambiguous_in_default_tools(self):
        """Key-style MCP tool names derived from DEFAULT_TOOLS must be unique."""
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        seen: dict[str, str] = {}
        duplicates = []
        for spec in DEFAULT_TOOLS:
            key = spec.split(".", 1)[1]
            if key in seen:
                duplicates.append(f"{key}: {seen[key]} vs {spec}")
            seen[key] = spec

        assert not duplicates, "Ambiguous key-style tool names:\n" + "\n".join(
            duplicates
        )

    def test_discovered_tool_keys_are_unambiguous_globally(self):
        """Key-style names resolve against *all* discovered tools, not defaults.

        ``_build_key_to_spec`` indexes the full discovery catalogue, so a key
        shared by two clients raises at registration even when only one of them
        is in ``DEFAULT_TOOLS``. The allowlist below records collisions that
        predate this guard; it must only ever shrink. See issue #126.
        """
        from fmp_data.mcp.discovery import discover_all_tools

        known_collisions = {"crypto_quotes", "forex_quotes"}

        tools = discover_all_tools()
        assert tools, "discover_all_tools() returned no tools"

        by_key: dict[str, list[str]] = {}
        for tool in tools:
            by_key.setdefault(tool["spec"].split(".", 1)[1], []).append(tool["spec"])

        collisions = {k: v for k, v in by_key.items() if len(v) > 1}
        new_collisions = {
            k: v for k, v in collisions.items() if k not in known_collisions
        }
        assert not new_collisions, "New ambiguous key-style tool names:\n" + "\n".join(
            f"{k}: {v}" for k, v in new_collisions.items()
        )

        stale = known_collisions - collisions.keys()
        assert not stale, (
            f"Allowlist entries no longer collide, remove them: {sorted(stale)}"
        )


class TestIntelligenceGradesAndRatingsTools:
    """Grades/ratings surface must be discoverable via MCP (issue #116)."""

    GRADES_AND_RATINGS = (
        "ratings_snapshot",
        "ratings_historical",
        "price_target_news",
        "price_target_latest_news",
        "grades",
        "grades_historical",
        "grades_consensus",
        "grades_news",
        "grades_latest_news",
    )

    def test_semantics_defined(self):
        from fmp_data.intelligence.mapping import INTELLIGENCE_ENDPOINTS_SEMANTICS

        missing = [
            k
            for k in self.GRADES_AND_RATINGS
            if k not in INTELLIGENCE_ENDPOINTS_SEMANTICS
        ]
        assert not missing, f"Missing intelligence semantics: {missing}"

    def test_endpoints_mapped(self):
        from fmp_data.intelligence.mapping import (
            INTELLIGENCE_ENDPOINT_MAP,
            INTELLIGENCE_ENDPOINTS_SEMANTICS,
        )

        missing = [
            k
            for k in self.GRADES_AND_RATINGS
            if INTELLIGENCE_ENDPOINTS_SEMANTICS[k].method_name
            not in INTELLIGENCE_ENDPOINT_MAP
        ]
        assert not missing, f"Missing INTELLIGENCE_ENDPOINT_MAP entries: {missing}"

    def test_present_in_default_tools(self):
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        missing = [
            f"intelligence.{k}"
            for k in self.GRADES_AND_RATINGS
            if f"intelligence.{k}" not in DEFAULT_TOOLS
        ]
        assert not missing, f"Missing DEFAULT_TOOLS entries: {missing}"

    def test_register_from_manifest(self, live_client):
        """The nine tools must actually register, not merely be declared.

        Membership in the semantics/endpoint dicts is what issues #114/#115
        showed to be insufficient — registration is the path that fails on
        mapping drift.
        """
        from fmp_data.mcp.tool_loader import register_from_manifest

        mcp = Mock()
        specs = [f"intelligence.{k}" for k in self.GRADES_AND_RATINGS]
        register_from_manifest(mcp, live_client, specs)

        registered = {call.kwargs["name"] for call in mcp.add_tool.call_args_list}
        assert registered in (set(self.GRADES_AND_RATINGS), set(specs))

    def test_semantics_register_in_langchain_registry(self):
        """Each tool must survive LC category validation as Intelligence.

        ``price_target_news`` / ``price_target_latest_news`` sit under company's
        ``get_price_target`` prefix, so a first-match category rule misfiles
        them and aborts the whole intelligence group. See issue #122.
        """
        from fmp_data.intelligence.mapping import (
            INTELLIGENCE_ENDPOINT_MAP,
            INTELLIGENCE_ENDPOINTS_SEMANTICS,
        )
        from fmp_data.lc.registry import EndpointRegistry

        registry = EndpointRegistry()
        failures = []
        for key in self.GRADES_AND_RATINGS:
            semantics = INTELLIGENCE_ENDPOINTS_SEMANTICS[key]
            endpoint = INTELLIGENCE_ENDPOINT_MAP[semantics.method_name]
            try:
                registry.register(semantics.method_name, endpoint, semantics)
            except ValueError as exc:
                failures.append(f"{key}: {exc}")

        assert not failures, "Endpoints rejected by the LC registry:\n" + "\n".join(
            failures
        )


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


class TestMCPCompat:
    """Test suite for the MCP SDK compatibility shim."""

    def test_import_mcp_server_class_returns_usable_class(self):
        """The resolved class exposes the surface create_app relies on."""
        from fmp_data.mcp._compat import import_mcp_server_class

        server_cls = import_mcp_server_class()

        assert isinstance(server_cls, type)
        assert server_cls.__name__ in {"MCPServer", "FastMCP"}
        for attr in ("add_tool", "run"):
            assert callable(getattr(server_cls, attr))

    def test_prefers_v2_server_class(self):
        """MCPServer wins when the 2.x SDK is importable."""
        import sys

        from fmp_data.mcp._compat import import_mcp_server_class

        if "mcp.server" not in sys.modules:
            import mcp.server  # noqa: F401

        import mcp.server as mcp_server

        if not hasattr(mcp_server, "MCPServer"):
            pytest.skip("MCP SDK 1.x installed")

        assert import_mcp_server_class() is mcp_server.MCPServer

    def test_mcp_server_available_false_without_sdk(self):
        """Availability check reports False when neither SDK import works."""
        from fmp_data.mcp import _compat

        with patch.object(
            _compat, "import_mcp_server_class", side_effect=ImportError("no sdk")
        ):
            assert _compat.mcp_server_available() is False

    def test_falls_back_to_fastmcp_on_v1_sdk(self):
        """When MCPServer is missing, FastMCP from 1.x is used."""
        import sys
        import types

        from fmp_data.mcp import _compat

        class _FastMCP:
            def add_tool(self, *args, **kwargs):
                return None

            def run(self, *args, **kwargs):
                return None

        fake_server = types.ModuleType("mcp.server")
        fake_fastmcp = types.ModuleType("mcp.server.fastmcp")
        fake_fastmcp.FastMCP = _FastMCP
        # Parent package stubs so nested imports resolve
        fake_mcp = types.ModuleType("mcp")
        fake_mcp.server = fake_server

        modules = {
            "mcp": fake_mcp,
            "mcp.server": fake_server,
            "mcp.server.fastmcp": fake_fastmcp,
        }
        with patch.dict(sys.modules, modules, clear=False):
            cls = _compat.import_mcp_server_class()

        assert cls is _FastMCP
