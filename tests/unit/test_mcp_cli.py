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
        # "key" is required: selection now resolves through
        # `resolve_tool_spec`, which is keyed on the bare key (#160).
        mock_list_tools.return_value = [
            {"spec": "company.profile", "client": "company", "key": "profile"},
            {"spec": "market.gainers", "client": "market", "key": "gainers"},
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


class TestValidateSeesWhatRegistrationSees:
    """``validate`` must not stay silent about a registration failure.

    #149 removed the drift between the two per-entry rules. Name clashes are
    the remaining asymmetry: they are a property of the manifest as a whole,
    ``generate`` learned to report them and ``validate`` had not, so the very
    file ``generate`` warned about validated without a word. Exiting zero on
    these is tracked separately -- see the issue linked from the CHANGELOG --
    but staying silent is not defensible either way.
    """

    @staticmethod
    def _validate(tmp_path: Path, entries: list[str]) -> str:
        from fmp_data.mcp.cli import validate_manifest

        path = tmp_path / "manifest.py"
        path.write_text(f"TOOLS = {entries!r}\n")
        validate_manifest(path)
        return path.name

    def test_two_tools_claiming_one_name_are_reported(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The exact pair ``generate`` refuses to put in one manifest."""
        self._validate(tmp_path, ["alternative.crypto_quotes", "batch.crypto_quotes"])

        err = capsys.readouterr().err
        assert "crypto_quotes" in err
        assert "alternative.crypto_quotes" in err
        assert "batch.crypto_quotes" in err
        assert "FMP_MCP_TOOL_NAME_STYLE=spec" in err

    def test_a_bare_key_and_its_own_spec_count_as_one_tool_twice(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Resolution has to happen before the comparison.

        ``profile`` and ``company.profile`` are the same tool, so registration
        refuses the pair -- but they are different strings, and comparing the
        entries as written would see nothing. The advice differs too: no name
        style serves one tool twice, so it must not suggest one.
        """
        self._validate(tmp_path, ["profile", "company.profile"])

        err = capsys.readouterr().err
        assert "listed more than once" in err
        assert "FMP_MCP_TOOL_NAME_STYLE=spec" not in err

    def test_spec_style_is_believed_rather_than_lectured(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A collision under ``spec`` style is not a collision at all.

        The advertised name is the whole spec there, so the two
        ``crypto_quotes`` tools are distinct and register fine. Warning
        anyway would tell the user to set the variable they have just set --
        the worst kind of false positive, since it lands only on the person
        who took the earlier advice.
        """
        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "spec"}):
            self._validate(
                tmp_path, ["alternative.crypto_quotes", "batch.crypto_quotes"]
            )

        assert capsys.readouterr().err == ""

    def test_one_tool_twice_still_clashes_under_spec_style(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The duplicate case survives the name style, because it must.

        ``profile`` and ``company.profile`` are advertised under one name
        whichever style is in effect. This is the pair the suppression above
        must not swallow.
        """
        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "spec"}):
            self._validate(tmp_path, ["profile", "company.profile"])

        err = capsys.readouterr().err
        assert "listed more than once" in err
        # The message must not promise a refusal the loader does not make:
        # `_validate_tool_names` skips the duplicate check under `spec`.
        assert "refuses" not in err

    def test_a_clean_manifest_says_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Non-vacuity: the warnings above must not fire on anything valid."""
        self._validate(tmp_path, ["company.profile", "market.gainers"])

        assert capsys.readouterr().err == ""

    def test_a_generated_manifest_draws_no_clash_warning(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The two halves of #148/#149 must agree on the same file."""
        from fmp_data.mcp.cli import generate_manifest, validate_manifest

        path = tmp_path / "generated.py"
        generate_manifest(path)
        capsys.readouterr()

        assert validate_manifest(path) is True
        assert capsys.readouterr().err == ""


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
        """Test CLI generate command.

        `generate` now exits with a code, so a successful run raises
        SystemExit(0) rather than falling off the end of `main` (#160/#161).
        """
        from fmp_data.mcp.cli import main

        mock_generate.return_value = True

        with patch("sys.argv", ["fmp-mcp", "generate", "output.py"]):
            with pytest.raises(SystemExit) as excinfo:
                main()

        assert excinfo.value.code == 0
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


class TestGeneratedManifestIsUsable:
    """`fmp-mcp generate` must emit a manifest that can start a server (#148).

    With no ``--tools`` filter it wrote every catalog spec verbatim: the three
    keys this release deprecates, plus both sides of the two tool-name
    collisions, which ``_validate_tool_names`` refuses under the default
    ``key`` name style. The result was a file that failed at registration.
    """

    @staticmethod
    def _generate(tmp_path: Path, **kwargs: object) -> tuple[list[str], str]:
        from fmp_data.mcp.cli import generate_manifest
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / "generated_manifest.py"
        generate_manifest(path, **kwargs)  # type: ignore[arg-type]
        return load_manifest_tools(path), path.read_text()

    def test_generated_manifest_omits_deprecated_keys(self, tmp_path: Path) -> None:
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        tools, _ = self._generate(tmp_path)

        assert sorted(set(tools) & set(DEPRECATED_TOOLS)) == []

    def test_generated_manifest_has_no_tool_name_collision(
        self, tmp_path: Path
    ) -> None:
        tools, _ = self._generate(tmp_path)

        by_name: dict[str, list[str]] = {}
        for spec in tools:
            by_name.setdefault(spec.split(".", 1)[1], []).append(spec)
        collisions = {k: v for k, v in by_name.items() if len(v) > 1}

        assert collisions == {}

    def test_generated_manifest_documents_the_dropped_side(
        self, tmp_path: Path
    ) -> None:
        """A dropped tool must be recoverable from the file itself.

        Renamed from ``..._documents_the_excluded_side`` (#171): it no longer
        asserts anything about the *excluded* (collision-loser) category, which
        is what the old name promised a reader scanning for collision coverage.
        It asserts the *withdrawn* one, for the reason the next paragraph gives.

        The sides swapped. ``alternative.crypto_quotes`` and
        ``alternative.forex_quotes`` are now withdrawn -- ``quotes/crypto``
        and ``quotes/forex`` 404 on the live API -- so they are dropped for
        that reason, before the collision tie-break, and the ``batch.*`` side
        survives instead of being excluded.

        The ``FMP_MCP_TOOL_NAME_STYLE=spec`` guidance is correspondingly gone:
        it exists to resolve a *surviving* ambiguity, and with one side of
        each pair withdrawn no ambiguity reaches the manifest. The guidance
        returns automatically if a future collision has two live sides --
        ``test_every_dropped_spec_is_named_in_the_header`` is the exhaustive
        guarantee that no drop, of any kind, goes unexplained.
        """
        tools, content = self._generate(tmp_path)

        header = content.split("TOOLS = [", 1)[0]
        assert "alternative.crypto_quotes" in header
        assert "alternative.forex_quotes" in header
        assert "alternative.crypto_quotes" not in tools
        assert "batch.crypto_quotes" in tools

    def test_every_dropped_spec_is_named_in_the_header(self, tmp_path: Path) -> None:
        """The claim is "nothing disappears silently" -- hold it to all of it.

        Naming only the collision losers would leave a user diffing ``fmp-mcp
        list`` against their manifest with unexplained absences, in the one
        feature whose whole point is that every drop is accounted for. Checking
        the difference exhaustively means a future exclusion rule cannot ship
        without its explanation.
        """
        tools, content = self._generate(tmp_path)
        from fmp_data.mcp.cli import list_available_tools

        header = content.split("TOOLS = [", 1)[0]
        catalog = {tool["spec"] for tool in list_available_tools()}
        dropped = catalog - set(tools)

        assert dropped, "vacuous unless something was actually dropped"
        assert [spec for spec in sorted(dropped) if spec not in header] == []

    def test_deprecated_drops_name_their_replacement(self, tmp_path: Path) -> None:
        """A drop is only explained if it says what to use instead."""
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        tools, content = self._generate(tmp_path)
        header = content.split("TOOLS = [", 1)[0]

        assert DEPRECATED_TOOLS
        for spec, replacement in sorted(DEPRECATED_TOOLS.items()):
            line = next(ln for ln in header.splitlines() if spec in ln)
            assert replacement in line, line
            # The replacement is what makes the drop lossless -- it must ship.
            assert replacement in tools

    def test_withdrawn_drops_name_their_remedy(self, tmp_path: Path) -> None:
        """The withdrawn counterpart to the test above (#171).

        ``test_every_dropped_spec_is_named_in_the_header`` proves a withdrawn
        spec *appears* in the header; it does not prove the remedy is attached
        to it. Since the whole argument for keeping withdrawn and deprecated as
        separate categories is that the remedy differs -- a deprecated tool has
        a drop-in replacement, a withdrawn one has at best a different endpoint
        with a different payload -- the remedy is the part worth asserting, and
        it was asserted for only one of the two.

        The two shapes are checked separately because they fail differently. A
        successor that silently stopped being printed leaves a user with a dead
        tool and no next step. An entry with no successor that stopped saying
        so is worse: an absent remedy reads as an oversight, and a user will go
        looking for a migration that does not exist.
        """
        from fmp_data.mcp.cli import list_available_tools
        from fmp_data.mcp.tools_manifest import WITHDRAWN_TOOLS

        tools, content = self._generate(tmp_path)
        header = content.split("TOOLS = [", 1)[0]

        # Only withdrawn specs the catalog actually offers reach the header --
        # `_select_specs` intersects the table with the available specs.
        catalog = {tool["spec"] for tool in list_available_tools()}
        gone = sorted(set(WITHDRAWN_TOOLS) & catalog)
        assert gone, "vacuous unless something withdrawn was actually dropped"

        without_successor = 0
        for spec in gone:
            line = next(ln for ln in header.splitlines() if spec in ln)
            successor = WITHDRAWN_TOOLS[spec]
            if successor is None:
                without_successor += 1
                assert "FMP publishes no replacement" in line, line
            else:
                assert successor in line, line
                # Unlike a deprecated replacement, a withdrawn successor is a
                # different endpoint and need not ship in this manifest -- but
                # the line must then say so rather than imply it is present.
                where = "included below" if successor in tools else "not in this"
                assert where in line, line

        assert without_successor, (
            "no withdrawn entry exercised the no-successor branch; "
            f"WITHDRAWN_TOOLS has {sum(v is None for v in WITHDRAWN_TOOLS.values())} "
            "of them, so this assertion has gone vacuous"
        )

    def test_generated_manifest_still_covers_the_catalog(self, tmp_path: Path) -> None:
        """Only deprecated, withdrawn, and collision losers may go.

        The collision side that loses changed: ``alternative.crypto_quotes``
        and ``alternative.forex_quotes`` are now *withdrawn* -- their paths
        (``quotes/crypto``, ``quotes/forex``) 404 on the live API and the
        working equivalents are the ``batch.*`` ones. They are dropped for
        being withdrawn, before the collision tie-break runs, so the
        ``batch.*`` side is now the one that survives rather than the one
        excluded.
        """
        from fmp_data.mcp.cli import list_available_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS, WITHDRAWN_TOOLS

        tools, _ = self._generate(tmp_path)
        catalog = {tool["spec"] for tool in list_available_tools()}

        assert set(tools) == catalog - set(DEPRECATED_TOOLS) - set(WITHDRAWN_TOOLS)

    def test_generated_manifest_registers_cleanly(self, tmp_path: Path) -> None:
        """The acceptance test: it must actually start a server.

        Registration under the default ``key`` name style is what #148 says a
        generated manifest could not survive, and no deprecation may fire.
        """
        import warnings

        from fmp_data.client import FMPDataClient
        from fmp_data.mcp.tool_loader import register_from_manifest

        tools, _ = self._generate(tmp_path)
        mcp = Mock()
        client = FMPDataClient(api_key="dummy-key-for-attribute-resolution")

        try:
            with (
                patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "key"}),
                warnings.catch_warnings(),
            ):
                warnings.simplefilter("error", DeprecationWarning)
                register_from_manifest(mcp, client, tools)
        finally:
            client.close()

        assert mcp.add_tool.call_count == len(tools)

    def test_explicit_tools_keep_both_sides_and_get_guidance(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """An explicit selection is the user's call; generate warns, not drops.

        Under ``spec`` style the pair registers, so the manifest is written
        with **both** sides -- neither is thinned behind the caller's back --
        and the header carries the guidance.

        This used to be asserted under the default ``key`` style too, where
        the pair cannot register: writing that file and exiting 0 handed back
        an artifact ``validate`` exits 1 on. The refusal at that style is
        pinned by the test below.
        """
        monkeypatch.setenv("FMP_MCP_TOOL_NAME_STYLE", "spec")

        tools, content = self._generate(
            tmp_path,
            tools=["alternative.crypto_quotes", "batch.crypto_quotes"],
            include_defaults=False,
        )

        assert sorted(tools) == ["alternative.crypto_quotes", "batch.crypto_quotes"]
        header = content.split("TOOLS = [", 1)[0]
        assert "crypto_quotes" in header
        assert "FMP_MCP_TOOL_NAME_STYLE=spec" in header
        assert "crypto_quotes" in capsys.readouterr().err

    def test_a_collision_is_refused_under_the_default_name_style(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The other half of the contract above, at the style people run.

        Neither side is dropped -- the selection is refused whole, with the
        escape hatch named -- so the user makes the call, not ``generate``.
        """
        from fmp_data.mcp.cli import generate_manifest

        monkeypatch.delenv("FMP_MCP_TOOL_NAME_STYLE", raising=False)
        path = tmp_path / "generated_manifest.py"

        written = generate_manifest(
            path,
            tools=["alternative.crypto_quotes", "batch.crypto_quotes"],
            include_defaults=False,
        )
        err = capsys.readouterr().err

        assert written is False
        assert not path.exists(), "wrote a manifest that cannot start a server"
        assert "FMP_MCP_TOOL_NAME_STYLE=spec" in err

    def test_a_default_yields_to_an_explicit_pick_of_the_other_side(
        self, tmp_path: Path
    ) -> None:
        """Defaults must not overrule an explicit pick.

        This used to also assert that the *displaced* default was named in the
        header, using ``batch.crypto_quotes`` as the side
        ``_startable_catalog`` normally dropped. That scenario no longer
        exists: ``alternative.crypto_quotes`` is withdrawn (``quotes/crypto``
        404s live), so it is never a candidate, and ``batch.crypto_quotes`` is
        now the side that survives. Asking for it explicitly displaces
        nothing, and the header is correctly silent -- there is nothing to
        explain.

        Displacement can only arise again if a collision has two live sides.
        ``test_every_dropped_spec_is_named_in_the_header`` is the exhaustive
        guarantee that whatever is dropped, for whatever reason, is named --
        so the "say when they yield" half is still enforced, just not here.

        What this asserts is the half that still has a scenario: an explicit
        selection is never thinned, and defaults are added around it.
        """
        tools, _content = self._generate(
            tmp_path, tools=["batch.crypto_quotes"], include_defaults=True
        )

        assert "batch.crypto_quotes" in tools
        # Withdrawn, so absent regardless of what was picked.
        assert "alternative.crypto_quotes" not in tools
        # Defaults still arrived -- otherwise this passes for the wrong reason.
        assert len(tools) > 1

    def test_an_explicitly_requested_deprecated_key_is_kept_but_reported(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The one path that can still put a deprecated key in a manifest.

        Honouring the ask and staying silent about it would make ``--tools``
        the only place in the CLI that does -- conspicuous now that the
        default path explains every deprecation it drops.
        """
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        spec, replacement = next(iter(sorted(DEPRECATED_TOOLS.items())))
        tools, _ = self._generate(tmp_path, tools=[spec], include_defaults=False)

        assert tools == [spec], "an explicit ask is honoured, not thinned"
        err = capsys.readouterr().err
        assert spec in err
        assert replacement in err

    def test_defaults_never_reinstate_a_deprecated_spec(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``_add_defaults`` runs after deprecations were stripped.

        The two tables are disjoint today, so only an injected overlap can
        exercise this -- but without the guard a future deprecated entry in
        ``DEFAULT_TOOLS`` would be silently put back into the manifest the
        same release just cleaned it out of.
        """
        from fmp_data.mcp import tools_manifest

        spec = next(iter(sorted(tools_manifest.DEPRECATED_TOOLS)))
        monkeypatch.setattr(
            tools_manifest, "DEFAULT_TOOLS", [*tools_manifest.DEFAULT_TOOLS, spec]
        )

        tools, _ = self._generate(tmp_path)

        assert spec not in tools

    def test_generated_manifest_ends_with_a_newline(self, tmp_path: Path) -> None:
        """A generated file is someone's source file; POSIX-terminate it."""
        _, content = self._generate(tmp_path)

        assert content.endswith("]\n")


class TestGenerateManifestFormatFromSuffix:
    """#256: suffix chooses JSON / YAML / TOML / legacy Python."""

    @staticmethod
    def _write(
        tmp_path: Path, name: str
    ) -> tuple[Path, bool, list[str] | None, str | None]:
        from fmp_data.mcp.cli import generate_manifest
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / name
        written = generate_manifest(
            path,
            tools=["company.profile", "market.gainers"],
            include_defaults=False,
        )
        if not written:
            return path, written, None, None
        return path, written, load_manifest_tools(path), path.read_text()

    def test_json_suffix_writes_tools_object(self, tmp_path: Path) -> None:
        _path, written, tools, content = self._write(tmp_path, "manifest.json")
        assert written is True
        assert tools == ["company.profile", "market.gainers"]
        assert content is not None
        assert '"tools"' in content
        assert "TOOLS =" not in content
        assert content.endswith("\n")

    def test_yaml_suffix_loads(self, tmp_path: Path) -> None:
        _, written, tools, content = self._write(tmp_path, "manifest.yaml")
        assert written is True
        assert tools == ["company.profile", "market.gainers"]
        assert content is not None
        assert content.startswith("tools:")

    def test_toml_suffix_loads(self, tmp_path: Path) -> None:
        _, written, tools, content = self._write(tmp_path, "manifest.toml")
        assert written is True
        assert tools == ["company.profile", "market.gainers"]
        assert content is not None
        assert content.startswith("tools = [")

    def test_py_suffix_still_writes_tools_assignment(self, tmp_path: Path) -> None:
        _, written, tools, content = self._write(tmp_path, "manifest.py")
        assert written is True
        assert tools == ["company.profile", "market.gainers"]
        assert content is not None
        assert "TOOLS = [" in content

    def test_no_suffix_writes_json(self, tmp_path: Path) -> None:
        from fmp_data.mcp.cli import generate_manifest
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / "manifest"
        written = generate_manifest(
            path, tools=["company.profile"], include_defaults=False
        )
        written_path = tmp_path / "manifest.json"
        assert written is True
        assert not path.exists()
        assert load_manifest_tools(written_path) == ["company.profile"]

    def test_unknown_suffix_is_refused(self, tmp_path: Path, capsys) -> None:
        from fmp_data.mcp.cli import generate_manifest

        path = tmp_path / "manifest.txt"
        written = generate_manifest(
            path, tools=["company.profile"], include_defaults=False
        )
        assert written is False
        assert not path.exists()
        assert ".json" in capsys.readouterr().err


class TestListLabelsAllThreeRetirementConcepts:
    """#158: ``list`` knew only about renames, so withdrawals read as live.

    Manifests are written by copying keys out of this listing. Three distinct
    things can be true of a key and each obliges the reader to do something
    different:

    * ``DEPRECATED_TOOLS`` -- a second *name* for a live method. Still serves
      real data; swap the name before 3.0.
    * ``WITHDRAWN_TOOLS`` / ``EndpointSemantics.deprecated`` -- FMP does not
      serve the endpoint. Resolves, registers, and answers ``[]`` forever;
      there is nothing to swap to unless a ``successor`` is named, and even
      then the payload differs.
    * live -- nothing to do.

    They stay three concepts. The listing labels them apart rather than
    collapsing them into one flag.
    """

    @staticmethod
    def _render(fmt: str) -> str:
        from contextlib import redirect_stdout
        import io

        from fmp_data.mcp.cli import list_available_tools, print_tools_table

        buffer = io.StringIO()
        with patch.dict(os.environ, {"COLUMNS": "400", "TERM": "dumb"}):
            with redirect_stdout(buffer):
                print_tools_table(list_available_tools(), fmt)
        return buffer.getvalue()

    def test_the_three_endpoints_named_in_the_issue_are_marked(self) -> None:
        """They printed ``deprecated: None``, identical to a live tool."""
        from fmp_data.mcp.cli import list_available_tools

        by_spec = {tool["spec"]: tool for tool in list_available_tools()}
        reported = [
            "intelligence.stock_news_sentiments",
            "intelligence.earnings_confirmed",
            "intelligence.earnings_surprises",
        ]

        for spec in reported:
            assert spec in by_spec, f"floor: {spec} left the catalog"
            assert by_spec[spec]["withdrawn"] is True, f"{spec} still reads as live"

    def test_withdrawal_and_rename_stay_separate_keys(self) -> None:
        """Neither mechanism may be re-derived from the other.

        ``deprecated`` keeps meaning exactly what it meant before -- the spec
        that replaces this one -- so a script reading that field is not
        silently handed withdrawals under the same name.
        """
        from fmp_data.mcp.cli import list_available_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS, WITHDRAWN_TOOLS

        tools = list_available_tools()
        assert len(tools) > 100, "floor: an empty catalog would pass vacuously"

        specs = {tool["spec"] for tool in tools}
        renamed = {t["spec"] for t in tools if t["deprecated"]}
        withdrawn = {t["spec"] for t in tools if t["withdrawn"]}

        assert renamed == set(DEPRECATED_TOOLS) & specs
        assert withdrawn >= set(WITHDRAWN_TOOLS) & specs
        assert renamed and withdrawn, "floor: both mechanisms must be populated"
        assert renamed.isdisjoint(withdrawn), (
            "a spec is now both renamed and withdrawn -- the rendering shows "
            "both labels, but that overlap is a design decision to take "
            "explicitly rather than discover"
        )

    def test_the_semantics_flag_alone_is_enough_to_label_a_tool(self) -> None:
        """``EndpointSemantics.deprecated`` is read, not merely mirrored.

        ``WITHDRAWN_TOOLS`` and the flag are kept equal by #164's guard, so a
        listing that consulted only the table would look correct today and
        drift silently tomorrow. Emptying the table proves the flag is wired.
        """
        from fmp_data.mcp import cli, tools_manifest

        with patch.object(tools_manifest, "WITHDRAWN_TOOLS", {}):
            withdrawn = {
                t["spec"] for t in cli.list_available_tools() if t["withdrawn"]
            }

        assert "intelligence.earnings_confirmed" in withdrawn
        assert len(withdrawn) >= 20, (
            f"only {len(withdrawn)} tools carry EndpointSemantics.deprecated "
            "-- the flag is no longer reaching the CLI"
        )

    def test_the_table_is_read_too_when_the_flag_is_absent(self) -> None:
        """The other half of the union: a table entry alone also labels."""
        from fmp_data.mcp import cli

        probe = [
            {
                "spec": "company.gone",
                "client": "company",
                "method": "gone",
                "key": "gone",
                "description": "d",
                "withdrawn": False,
            }
        ]
        with patch("fmp_data.mcp.discovery.discover_all_tools", return_value=probe):
            with patch.dict(
                "fmp_data.mcp.tools_manifest.WITHDRAWN_TOOLS",
                {"company.gone": "company.here"},
            ):
                tool = cli.list_available_tools()[0]

        assert tool["withdrawn"] is True
        assert tool["successor"] == "company.here"
        assert tool["deprecated"] is None

    @pytest.mark.parametrize("fmt", ["table", "json", "list", "tree"])
    def test_every_format_shows_the_withdrawal(self, fmt: str) -> None:
        """All four, because a manifest is copied out of whichever you ran."""
        rendered = self._render(fmt)

        if fmt == "json":
            assert '"withdrawn": true' in rendered
            assert '"successor"' in rendered
        else:
            assert "WITHDRAWN" in rendered

    @pytest.mark.parametrize("fmt", ["table", "list", "tree"])
    def test_a_withdrawal_is_not_labelled_a_deprecation(self, fmt: str) -> None:
        """The label has to say which of the two it is.

        ``[DEPRECATED -> x]`` on a withdrawn tool would promise a drop-in
        replacement for an endpoint that has none -- the "empty success" #137
        removed from the LangChain side, re-introduced as text.
        """
        from fmp_data.mcp.cli import _retirement_labels, list_available_tools

        withdrawn = [t for t in list_available_tools() if t["withdrawn"]]
        assert withdrawn, "floor: nothing withdrawn"

        for tool in withdrawn:
            labels = _retirement_labels(tool)
            assert labels, f"{tool['spec']} rendered no label"
            assert any(label.startswith("WITHDRAWN") for label in labels)
            assert not any(label.startswith("DEPRECATED") for label in labels)

        rendered = self._render(fmt)
        assert "no replacement" in rendered, (
            "no withdrawn tool rendered its successor-less form; FMP "
            "publishes nothing equivalent for several of them"
        )

    def test_a_rename_still_renders_its_replacement(self) -> None:
        """#163's contract is unchanged by the new label."""
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        rendered = self._render("list")
        assert DEPRECATED_TOOLS, "floor: no renames to check"
        for spec, replacement in sorted(DEPRECATED_TOOLS.items()):
            assert f"{spec} [DEPRECATED -> {replacement}]" in rendered
