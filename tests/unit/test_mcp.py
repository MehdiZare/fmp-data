# tests/unit/test_mcp.py - Fixed tests
"""
Basic tests for MCP server functionality.

Relative path: tests/unit/test_mcp.py
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import warnings

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
            "company.historical_prices",
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

    def test_ambiguous_bare_keys_are_exactly_the_documented_pair(self):
        """Bare-key resolution is only guaranteed for singly-claimed keys.

        ``_build_key_to_spec`` indexes the full discovery catalogue, so a key
        claimed by two clients cannot resolve from the bare form. Exactly two
        such keys exist and both name legitimate, distinct tools; callers must
        spell them ``<client>.<key>``. Any *other* collision is a namespace
        regression and must fail here. See issue #126.
        """
        from fmp_data.mcp.discovery import discover_all_tools

        documented_ambiguous = {"crypto_quotes", "forex_quotes"}

        tools = discover_all_tools()
        assert tools, "discover_all_tools() returned no tools"

        by_key: dict[str, list[str]] = {}
        for tool in tools:
            by_key.setdefault(tool["spec"].split(".", 1)[1], []).append(tool["spec"])

        ambiguous = {k: sorted(v) for k, v in by_key.items() if len(v) > 1}

        assert set(ambiguous) == documented_ambiguous, (
            "Ambiguous bare tool keys changed. Expected exactly "
            f"{sorted(documented_ambiguous)}, found "
            f"{dict(sorted(ambiguous.items()))}"
        )
        assert ambiguous["crypto_quotes"] == [
            "alternative.crypto_quotes",
            "batch.crypto_quotes",
        ]
        assert ambiguous["forex_quotes"] == [
            "alternative.forex_quotes",
            "batch.forex_quotes",
        ]

    def test_ambiguous_bare_key_error_names_every_candidate(self):
        """The error must be actionable: list candidates, show the fix."""
        from fmp_data.mcp.tool_loader import _build_key_to_spec, _resolve_tool_spec

        key_to_spec = _build_key_to_spec(
            [
                {"key": "crypto_quotes", "spec": "alternative.crypto_quotes"},
                {"key": "crypto_quotes", "spec": "batch.crypto_quotes"},
            ]
        )

        with pytest.raises(RuntimeError) as exc_info:
            _resolve_tool_spec("crypto_quotes", key_to_spec)

        message = str(exc_info.value)
        assert "alternative.crypto_quotes" in message
        assert "batch.crypto_quotes" in message
        assert "<client>.<key>" in message

    def test_full_spec_still_resolves_an_ambiguous_key(self):
        """Naming the client is the documented escape hatch; it must work."""
        from fmp_data.mcp.tool_loader import _build_key_to_spec, _resolve_tool_spec

        key_to_spec = _build_key_to_spec(
            [
                {"key": "crypto_quotes", "spec": "alternative.crypto_quotes"},
                {"key": "crypto_quotes", "spec": "batch.crypto_quotes"},
            ]
        )

        assert _resolve_tool_spec("batch.crypto_quotes", key_to_spec) == (
            "batch.crypto_quotes",
            "batch",
            "crypto_quotes",
        )


class TestToolKeyNamespace:
    """One tool key per ``(client, method)`` pair (#126, #130, #136)."""

    def test_cik_mapper_by_name_is_gone(self):
        """#130: a tool that cannot express its own operation is removed."""
        from fmp_data.institutional.mapping import (
            INSTITUTIONAL_ENDPOINT_MAP,
            INSTITUTIONAL_ENDPOINTS_SEMANTICS,
        )
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        assert "cik_mapper_by_name" not in INSTITUTIONAL_ENDPOINTS_SEMANTICS
        assert "search_cik_by_name" not in INSTITUTIONAL_ENDPOINT_MAP
        assert "institutional.cik_mapper_by_name" not in {
            tool["spec"] for tool in discover_all_tools()
        }
        assert "institutional.cik_mapper_by_name" not in DEFAULT_TOOLS

    def test_search_cik_by_name_client_methods_still_work(self):
        """The client wrapper is the genuine interface and stays untouched."""
        import inspect

        from fmp_data.institutional.async_client import AsyncInstitutionalClient
        from fmp_data.institutional.client import InstitutionalClient

        for cls in (InstitutionalClient, AsyncInstitutionalClient):
            method = cls.search_cik_by_name
            assert "name" in inspect.signature(method).parameters

    def test_one_tool_key_per_client_method_pair(self):
        """#136: no ``(client, method)`` may be advertised under two keys."""
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        by_pair: dict[tuple[str, str], list[str]] = {}
        for tool in discover_all_tools():
            by_pair.setdefault((tool["client"], tool["method"]), []).append(
                tool["spec"]
            )

        doubled = {
            pair: sorted(specs)
            for pair, specs in by_pair.items()
            if len(specs) > 1 and not any(spec in DEPRECATED_TOOLS for spec in specs)
        }

        assert doubled == {}, (
            "Methods advertised under more than one non-deprecated tool key:\n"
            + "\n".join(f"{pair}: {specs}" for pair, specs in sorted(doubled.items()))
        )

    def test_deprecated_keys_are_not_in_default_tools(self):
        """The default server advertises one tool per method."""
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS, DEPRECATED_TOOLS

        leaked = sorted(set(DEPRECATED_TOOLS) & set(DEFAULT_TOOLS))

        assert leaked == [], f"Deprecated tool keys still in DEFAULT_TOOLS: {leaked}"

    def test_deprecated_keys_map_to_canonical_keys_in_default_tools(self):
        """Every replacement must actually be what the default server serves."""
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS, DEPRECATED_TOOLS

        catalog = {tool["spec"] for tool in discover_all_tools()}

        assert DEPRECATED_TOOLS == {
            "company.executives": "company.key_executives",
            "company.historical_price": "company.historical_prices",
            "company.intraday_price": "company.intraday_prices",
        }
        for deprecated, replacement in DEPRECATED_TOOLS.items():
            assert deprecated in catalog, f"{deprecated} must keep resolving in 2.6"
            assert replacement in catalog
            assert replacement in DEFAULT_TOOLS

    def test_deprecated_keys_share_the_method_of_their_replacement(self):
        """An alias must be an alias, not a rename onto a different callable."""
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        method_by_spec = {tool["spec"]: tool["method"] for tool in discover_all_tools()}

        for deprecated, replacement in DEPRECATED_TOOLS.items():
            assert method_by_spec[deprecated] == method_by_spec[replacement]

    @pytest.mark.parametrize(
        ("spec", "replacement"),
        [
            ("company.executives", "company.key_executives"),
            ("company.historical_price", "company.historical_prices"),
            ("company.intraday_price", "company.intraday_prices"),
        ],
    )
    def test_resolving_a_deprecated_full_spec_warns(
        self, spec: str, replacement: str
    ) -> None:
        from fmp_data.mcp.tool_loader import _resolve_tool_spec

        with pytest.warns(DeprecationWarning) as record:
            _resolve_tool_spec(spec, {})

        message = str(record[0].message)
        assert spec in message
        assert replacement in message
        assert "3.0" in message

    def test_resolving_a_deprecated_bare_key_warns(self) -> None:
        """The bare form resolves to the same spec, so it warns too."""
        from fmp_data.mcp.tool_loader import _build_key_to_spec, _resolve_tool_spec

        key_to_spec = _build_key_to_spec(
            [{"key": "executives", "spec": "company.executives"}]
        )

        with pytest.warns(DeprecationWarning, match="company.key_executives"):
            assert _resolve_tool_spec("executives", key_to_spec) == (
                "company.executives",
                "company",
                "executives",
            )

    def test_canonical_keys_do_not_warn(self) -> None:
        import warnings

        from fmp_data.mcp.tool_loader import _resolve_tool_spec

        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            _resolve_tool_spec("company.key_executives", {})

    def test_warning_is_attributed_to_the_caller_not_the_library(self) -> None:
        """``stacklevel`` must point at the manifest author's own module.

        A warning attributed to ``tool_loader.py`` is useless: it names the
        library rather than the line to change, and no ``filterwarnings`` rule
        keyed on the caller's module can match it.
        """
        from fmp_data.client import FMPDataClient
        from fmp_data.mcp.tool_loader import register_from_manifest

        client = FMPDataClient(api_key="dummy-key-for-attribute-resolution")
        try:
            with pytest.warns(DeprecationWarning) as record:
                register_from_manifest(Mock(), client, ["company.historical_price"])
        finally:
            client.close()

        assert Path(record[0].filename).name == Path(__file__).name, (
            f"warning attributed to {record[0].filename}, expected this test file"
        )

    def test_recommended_tools_names_no_deprecated_key(self) -> None:
        """A public helper must not hand out a key this release deprecates."""
        from fmp_data.mcp.discovery import get_recommended_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        offenders = sorted(set(get_recommended_tools()) & set(DEPRECATED_TOOLS))

        assert offenders == [], (
            f"get_recommended_tools() recommends deprecated keys: {offenders}"
        )

    def test_no_removal_reminder_missed_for_3_0(self) -> None:
        """Breadcrumb: 3.0 must not ship with the deprecation cycle still open.

        ``fmp_data.__version__`` is hatch-vcs derived and resolves to the
        ``"0.0.0"`` fallback whenever the suite imports the source tree rather
        than a built wheel -- which is what happens in this repo -- so it is
        checked only when it carries a real value. The CHANGELOG is the signal
        that actually moves in-tree: cutting 3.0 adds a released ``## [3.x.y]``
        heading, and that is what trips this test.

        On failure: drop ``DEPRECATED_TOOLS``, the ``executives`` /
        ``historical_price`` / ``intraday_price`` semantics entries in
        ``fmp_data/company/mapping.py``, and ``_warn_if_deprecated`` plus its
        two call sites in ``fmp_data/mcp/tool_loader.py``.
        """
        import re

        from fmp_data import __version__

        reminder = (
            "3.0: drop DEPRECATED_TOOLS, the three alias semantics entries, "
            "and _warn_if_deprecated"
        )

        if __version__ != "0.0.0":
            assert int(__version__.split(".")[0]) < 3, reminder

        changelog = (Path(__file__).resolve().parents[2] / "CHANGELOG.md").read_text()
        released_majors = {
            int(match) for match in re.findall(r"^## \[(\d+)\.", changelog, re.M)
        }

        assert not any(major >= 3 for major in released_majors), reminder


class TestExampleManifests:
    """Shipped examples must demonstrate the policy, not violate it (#126, #136).

    ``docs/mcp/configurations.md`` tells users to copy one of these files, so a
    deprecated or unresolvable key here is advice to write broken manifests.
    """

    MANIFEST_DIR = Path(__file__).resolve().parents[2] / "examples/mcp/configurations"

    @staticmethod
    def _manifest_paths() -> list[Path]:
        paths = sorted(TestExampleManifests.MANIFEST_DIR.glob("*_manifest.py"))
        assert paths, (
            f"No example manifests found in {TestExampleManifests.MANIFEST_DIR}"
        )
        return paths

    @staticmethod
    def _load_tools(path: Path) -> list[str]:
        from fmp_data.mcp.utils import load_manifest_tools

        return load_manifest_tools(path)

    def test_no_example_manifest_names_a_deprecated_key(self) -> None:
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        specs_by_key: dict[str, list[str]] = {}
        for tool in discover_all_tools():
            specs_by_key.setdefault(tool["key"], []).append(tool["spec"])

        offenders: list[str] = []
        for path in self._manifest_paths():
            for entry in self._load_tools(path):
                candidates = [entry] if "." in entry else specs_by_key.get(entry, [])
                for spec in candidates:
                    if spec in DEPRECATED_TOOLS:
                        offenders.append(
                            f"{path.name}: '{entry}' -> use '{DEPRECATED_TOOLS[spec]}'"
                        )

        assert offenders == [], (
            "Example manifests name deprecated tool keys:\n" + "\n".join(offenders)
        )

    def test_every_example_manifest_entry_resolves(self) -> None:
        """Catches ambiguous bare keys and typos, not just deprecation.

        ``crypto_manifest.py`` listed bare ``crypto_quotes`` / ``forex_quotes``,
        which are claimed by two clients each and raise at registration (#126).
        """
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tool_loader import _build_key_to_spec, _resolve_tool_spec

        key_to_spec = _build_key_to_spec(discover_all_tools())
        catalog = {tool["spec"] for tool in discover_all_tools()}

        failures: list[str] = []
        for path in self._manifest_paths():
            for entry in self._load_tools(path):
                try:
                    full_spec, _, _ = _resolve_tool_spec(entry, key_to_spec)
                except RuntimeError as exc:
                    failures.append(f"{path.name}: '{entry}': {exc}")
                    continue
                if full_spec not in catalog:
                    failures.append(f"{path.name}: '{entry}' -> unknown {full_spec}")

        assert failures == [], (
            "Example manifest entries that do not resolve:\n" + "\n".join(failures)
        )

    def test_no_example_manifest_lists_a_tool_twice(self) -> None:
        """Two names for one method is the very thing #136 removes."""
        from fmp_data.mcp.discovery import discover_all_tools
        from fmp_data.mcp.tool_loader import _build_key_to_spec, _resolve_tool_spec

        key_to_spec = _build_key_to_spec(discover_all_tools())
        method_by_spec = {tool["spec"]: tool["method"] for tool in discover_all_tools()}

        duplicates: list[str] = []
        for path in self._manifest_paths():
            seen: dict[tuple[str, str], str] = {}
            for entry in self._load_tools(path):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", DeprecationWarning)
                        full_spec, client_slug, _ = _resolve_tool_spec(
                            entry, key_to_spec
                        )
                except RuntimeError:
                    # Unresolvable entries are test_every_example_manifest_entry
                    # _resolves' failure to report; do not double-fail here.
                    continue
                pair = (client_slug, method_by_spec[full_spec])
                if pair in seen:
                    duplicates.append(f"{path.name}: '{seen[pair]}' and '{entry}'")
                seen[pair] = entry

        assert duplicates == [], (
            "Example manifests register the same method twice:\n"
            + "\n".join(duplicates)
        )


class TestMCPCliDeprecationReporting:
    """``fmp-mcp validate`` answers 'is my manifest future-proof?' (#136)."""

    def test_validate_reports_deprecated_specs_and_still_passes(
        self, tmp_path, capsys
    ) -> None:
        from fmp_data.mcp.cli import validate_manifest

        manifest = tmp_path / "deprecated_manifest.py"
        manifest.write_text('TOOLS = ["company.historical_price", "company.profile"]\n')

        assert validate_manifest(manifest) is True

        out = capsys.readouterr().out
        assert "company.historical_price" in out
        assert "company.historical_prices" in out
        assert "3.0" in out

    def test_validate_reports_a_deprecated_bare_key(self, tmp_path, capsys) -> None:
        from fmp_data.mcp.cli import validate_manifest

        manifest = tmp_path / "bare_manifest.py"
        manifest.write_text('TOOLS = ["historical_price"]\n')

        assert validate_manifest(manifest) is True

        out = capsys.readouterr().out
        assert "company.historical_prices" in out

    def test_validate_is_quiet_for_a_canonical_manifest(self, tmp_path, capsys) -> None:
        from fmp_data.mcp.cli import validate_manifest

        manifest = tmp_path / "clean_manifest.py"
        manifest.write_text('TOOLS = ["company.historical_prices"]\n')

        assert validate_manifest(manifest) is True

        captured = capsys.readouterr()
        assert "Deprecated" not in captured.out
        assert "Unknown tools" not in captured.err

    def test_validate_flags_an_ambiguous_bare_key(self, tmp_path, capsys) -> None:
        from fmp_data.mcp.cli import validate_manifest

        manifest = tmp_path / "ambiguous_manifest.py"
        manifest.write_text('TOOLS = ["crypto_quotes"]\n')

        assert validate_manifest(manifest) is True

        err = capsys.readouterr().err
        assert "alternative.crypto_quotes" in err
        assert "batch.crypto_quotes" in err

    def test_listing_marks_deprecated_tools(self) -> None:
        from fmp_data.mcp.cli import list_available_tools

        by_spec = {tool["spec"]: tool for tool in list_available_tools()}

        assert by_spec["company.historical_price"]["deprecated"] == (
            "company.historical_prices"
        )
        assert by_spec["company.historical_prices"]["deprecated"] is None


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

        assert redacted is not None
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
        fake_fastmcp.FastMCP = _FastMCP  # type: ignore[attr-defined]
        # Parent package stubs so nested imports resolve
        fake_mcp = types.ModuleType("mcp")
        fake_mcp.server = fake_server  # type: ignore[attr-defined]

        modules = {
            "mcp": fake_mcp,
            "mcp.server": fake_server,
            "mcp.server.fastmcp": fake_fastmcp,
        }
        with patch.dict(sys.modules, modules, clear=False):
            cls = _compat.import_mcp_server_class()

        assert cls is _FastMCP
