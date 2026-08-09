"""The three `fmp-mcp` entry points must agree on what a manifest is.

``validate``, ``generate`` and ``register_from_manifest`` each answer a
question about a manifest entry, and each used to answer it its own way:

* ``generate`` tested membership against fully qualified specs only, so a bare
  key the loader resolves was reported "unknown" and dropped (#160);
* ``validate`` reported its findings and then printed a success verdict and
  exited 0 for manifests registration refuses (#161);
* the loader skipped its duplicate check entirely under
  ``FMP_MCP_TOOL_NAME_STYLE=spec`` (#162).

The tests here are deliberately not one-per-bug. They pin the *agreement*
across a table of manifests -- the catalog plus every known-bad shape -- under
both name styles, so a fourth divergence cannot be introduced without a
failure. That is what makes #161's class structurally impossible rather than
fixed once.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch
import warnings

import pytest

from fmp_data.mcp import tool_loader
from fmp_data.mcp.cli import (
    _validated_specs,
    generate_manifest,
    list_available_tools,
    print_tools_table,
    validate_manifest,
)

#: Manifests whose verdict both `validate` and the loader must reach.
#:
#: Every shape the resolution rule can produce is represented, plus the two
#: clash shapes that are properties of a manifest rather than of one entry.
#: Keyed by a description so a failure names the case rather than an index.
MANIFEST_CASES: dict[str, list[str]] = {
    "clean full specs": ["company.profile", "market.gainers"],
    "clean bare key": ["profile"],
    "bare key and its own spec": ["profile", "company.profile"],
    "typo in a full spec": ["company.profil"],
    "typo in a bare key": ["profil"],
    "ambiguous bare key": ["crypto_quotes"],
    "two specs claiming one name": [
        "alternative.crypto_quotes",
        "batch.crypto_quotes",
    ],
    "a deprecated spec": ["company.historical_price"],
    "a withdrawn spec": ["company.core_information"],
    "deprecated and its replacement": [
        "company.historical_price",
        "company.historical_prices",
    ],
    "empty": [],
}

NAME_STYLES = ("key", "spec")


def _write(tmp_path: Path, name: str, entries: list[str]) -> Path:
    path = tmp_path / f"{name.replace(' ', '_')}.py"
    path.write_text("TOOLS = [\n" + "".join(f'    "{e}",\n' for e in entries) + "]\n")
    return path


def _registration_raises(entries: list[str]) -> bool:
    """Whether ``register_from_manifest`` refuses this manifest.

    Warnings are silenced rather than escalated: a deprecated or withdrawn
    entry warns *and registers*, so treating the warning as an error would
    make the loader look stricter than it is and hide the very disagreement
    these tests exist to detect.
    """
    from fmp_data.client import FMPDataClient

    client = FMPDataClient(api_key="dummy-key-for-attribute-resolution")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            tool_loader.register_from_manifest(Mock(), client, entries)
    except RuntimeError:
        return True
    finally:
        client.close()
    return False


def _registration_error(entries: list[str]) -> str:
    """The message ``register_from_manifest`` refuses ``entries`` with."""
    from fmp_data.client import FMPDataClient

    client = FMPDataClient(api_key="dummy-key-for-attribute-resolution")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            with pytest.raises(RuntimeError) as excinfo:
                tool_loader.register_from_manifest(Mock(), client, entries)
    finally:
        client.close()
    return str(excinfo.value)


class TestValidateAgreesWithRegistration:
    """#161: the exit code must mean "the server will start"."""

    @pytest.mark.parametrize("style", NAME_STYLES)
    @pytest.mark.parametrize("case", sorted(MANIFEST_CASES))
    def test_verdict_matches_whether_registration_raises(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str], case: str, style: str
    ) -> None:
        entries = MANIFEST_CASES[case]
        path = _write(tmp_path, case, entries)

        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": style}):
            valid = validate_manifest(path)
            refused = _registration_raises(entries)
        capsys.readouterr()

        assert valid is not refused, (
            f"{case!r} under FMP_MCP_TOOL_NAME_STYLE={style}: validate said "
            f"{'valid' if valid else 'invalid'} but registration "
            f"{'raised' if refused else 'succeeded'}"
        )

    def test_the_table_covers_both_verdicts(self, tmp_path: Path) -> None:
        """Floor: the parametrisation above is worthless if nothing fails.

        Without this, deleting the failure branch from ``validate_manifest``
        and every bad case from the table would leave a green suite.
        """
        verdicts = {
            case: _registration_raises(entries)
            for case, entries in MANIFEST_CASES.items()
        }

        assert sum(verdicts.values()) >= 4, verdicts
        assert sum(not refused for refused in verdicts.values()) >= 4, verdicts

    @pytest.mark.parametrize(
        "case", ["a deprecated spec", "a withdrawn spec", "clean bare key"]
    )
    def test_a_resolvable_manifest_still_exits_zero(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str], case: str
    ) -> None:
        """Retirement is a report, not a failure.

        "Is my manifest future-proof?" must stay answerable without failing a
        build, so the migration table prints and the verdict stays true.
        """
        path = _write(tmp_path, case, MANIFEST_CASES[case])

        assert validate_manifest(path) is True
        assert "Manifest is valid" in capsys.readouterr().out

    def test_the_generated_catalog_manifest_validates(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The end-to-end loop: generate -> validate -> register."""
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / "generated.py"
        generate_manifest(path)
        entries = load_manifest_tools(path)

        assert len(entries) > 100, "floor: a near-empty manifest proves nothing"
        assert validate_manifest(path) is True
        assert _registration_raises(entries) is False
        capsys.readouterr()

    def test_the_verdict_line_pluralises(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = _write(tmp_path, "one", ["company.profile"])
        assert validate_manifest(path) is True

        out = capsys.readouterr().out
        assert "1 tool" in out
        assert "1 tools" not in out


class TestGenerateAgreesWithTheResolver:
    """#160: `generate` is the fourth consumer of the rule, not a fourth rule."""

    @staticmethod
    def _probe_entries() -> list[str]:
        """Every catalog spec, every bare key, and the known-bad shapes."""
        catalog = list_available_tools()
        entries = [tool["spec"] for tool in catalog]
        entries += sorted({tool["key"] for tool in catalog})
        entries += ["company.profil", "profil", "not.a.spec"]
        return entries

    def test_every_entry_is_classified_as_the_resolver_classifies_it(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The structural guard: no membership test of its own.

        ``_validated_specs`` must keep exactly the entries
        ``resolve_tool_spec`` resolves, and write the resolved spec rather than
        the entry as typed. A bare key dropped here while the loader accepts it
        is #160 verbatim.
        """
        entries = self._probe_entries()
        key_to_spec = tool_loader.build_key_to_spec(list_available_tools())

        expected: list[str] = []
        for entry in entries:
            resolution = tool_loader.resolve_tool_spec(entry, key_to_spec)
            if resolution.spec is not None and resolution.spec not in expected:
                expected.append(resolution.spec)

        actual = _validated_specs(entries)
        capsys.readouterr()

        assert expected, "floor: the catalog must not be empty"
        assert any("." not in entry for entry in entries), "floor: no bare keys probed"
        assert actual == expected

    def test_a_bare_key_reaches_the_manifest_as_its_full_spec(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The headline symptom of #160: `--tools profile` wrote nothing."""
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / "bare.py"
        generate_manifest(path, tools=["profile"], include_defaults=False)
        capsys.readouterr()

        assert load_manifest_tools(path) == ["company.profile"]

    def test_an_ambiguous_key_is_called_ambiguous_not_unknown(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """ "Unknown" sent users hunting a typo that was not there."""
        path = tmp_path / "ambiguous.py"
        generate_manifest(path, tools=["crypto_quotes"], include_defaults=False)

        err = capsys.readouterr().err
        assert "Unknown tool 'crypto_quotes'" not in err
        assert "alternative.crypto_quotes" in err
        assert "batch.crypto_quotes" in err

    def test_an_unknown_key_is_still_called_unknown(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The old message stays -- it is now actually true."""
        path = tmp_path / "unknown.py"
        generate_manifest(path, tools=["company.profil"], include_defaults=False)

        assert "Unknown tool 'company.profil'" in capsys.readouterr().err

    def test_a_key_and_its_spec_do_not_both_land_in_the_manifest(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Generate must not emit a file the loader then refuses (#162)."""
        from fmp_data.mcp.utils import load_manifest_tools

        path = tmp_path / "dup.py"
        generate_manifest(
            path, tools=["profile", "company.profile"], include_defaults=False
        )
        capsys.readouterr()

        entries = load_manifest_tools(path)
        assert entries == ["company.profile"]
        assert _registration_raises(entries) is False


class TestLoaderChecksNamesUnderBothStyles:
    """#162: the style that exists to fix name problems had no name checking."""

    @pytest.mark.parametrize("style", NAME_STYLES)
    def test_one_tool_listed_twice_raises_under_every_style(self, style: str) -> None:
        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": style}):
            message = _registration_error(["profile", "company.profile"])

        assert "profile" in message
        # Advice must fit the style in effect: telling someone already on
        # `spec` to set `spec` is the useless message #162 calls out.
        assert "listed more than once" in message or "same tool" in message
        if style == "spec":
            assert "FMP_MCP_TOOL_NAME_STYLE=spec" not in message

    def test_two_different_tools_can_share_a_key_under_spec_style(self) -> None:
        """The collision case `spec` style exists to serve must still work."""
        entries = ["alternative.crypto_quotes", "batch.crypto_quotes"]

        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "spec"}):
            assert _registration_raises(entries) is False
        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": "key"}):
            assert _registration_raises(entries) is True

    @pytest.mark.parametrize("style", NAME_STYLES)
    @pytest.mark.parametrize("case", sorted(MANIFEST_CASES))
    def test_validates_clash_report_matches_the_loaders_verdict(
        self, case: str, style: str
    ) -> None:
        """`validate`'s clash report and the loader's refusal are one rule."""
        from fmp_data.mcp.cli import _manifest_name_clashes

        entries = MANIFEST_CASES[case]
        with patch.dict(os.environ, {"FMP_MCP_TOOL_NAME_STYLE": style}):
            duplicates, collisions = _manifest_name_clashes(entries)
            clashes_reported = bool(duplicates or collisions)
            # Isolate name clashes from resolution failures: an unknown or
            # ambiguous entry raises for a different reason entirely.
            key_to_spec = tool_loader.build_key_to_spec(list_available_tools())
            resolvable = all(
                tool_loader.resolve_tool_spec(e, key_to_spec).is_resolved
                for e in entries
            )
            if not resolvable:
                pytest.skip("resolution failure, not a name clash")
            refused = _registration_raises(entries)

        assert clashes_reported is refused, (
            f"{case!r} under {style}: clashes={duplicates or collisions}, "
            f"registration {'raised' if refused else 'succeeded'}"
        )


class TestListOutputIsCopyPasteable:
    """#163: `fmp-mcp list` is how you discover what to put in a manifest."""

    FORMATS = ("table", "json", "list", "tree")

    @staticmethod
    def _render(tools: list[dict[str, Any]], fmt: str) -> str:
        from contextlib import redirect_stdout
        import io

        buffer = io.StringIO()
        # Rich sizes its output to the terminal; without a width the default
        # 80 columns re-truncates the very column this test is about.
        with patch.dict(os.environ, {"COLUMNS": "400", "TERM": "dumb"}):
            with redirect_stdout(buffer):
                print_tools_table(tools, fmt)
        return buffer.getvalue()

    @pytest.mark.parametrize("fmt", FORMATS)
    def test_every_format_emits_the_full_spec_of_every_tool(self, fmt: str) -> None:
        tools = list_available_tools()
        rendered = self._render(tools, fmt)

        assert len(tools) > 100, "floor: an empty catalog would pass vacuously"
        missing = [tool["spec"] for tool in tools if tool["spec"] not in rendered]
        assert missing == [], f"{fmt} format hides {len(missing)} specs: {missing[:5]}"

    @pytest.mark.parametrize("fmt", FORMATS)
    def test_no_two_tools_render_identically(self, fmt: str) -> None:
        """`company.historical_price` and `...prices` were the same string."""
        tools = list_available_tools()
        rendered = self._render(tools, fmt)

        pair = ["company.historical_price", "company.historical_prices"]
        assert {tool["spec"] for tool in tools} >= set(pair), "floor: pair is gone"
        for spec in pair:
            assert spec in rendered
        # The truncated cell rendered both as `company.historica…`; the
        # singular surviving only as a prefix of the plural is the bug.
        assert rendered.count("company.historical_price") >= 2

    def test_the_spec_column_is_never_ellipsised_on_a_default_terminal(self) -> None:
        """The bug was only visible at the width people actually use.

        A wide render hides it: rich ellipsises only when it has to shrink. At
        the default 80 columns the spec column was cut to
        ``company.historica…``, rendering the deprecated tool and its
        replacement as the same string. Folding costs a wrapped line instead.
        """
        from contextlib import redirect_stdout
        import io

        buffer = io.StringIO()
        with patch.dict(os.environ, {"COLUMNS": "80", "TERM": "dumb"}):
            with redirect_stdout(buffer):
                print_tools_table(list_available_tools(), "table")
        rendered = buffer.getvalue()

        cut = [
            line
            for line in rendered.splitlines()
            if "│" in line and line.split("│")[1].rstrip().endswith("…")
        ]
        assert cut == [], f"{len(cut)} specs truncated, e.g. {cut[:2]}"

    @pytest.mark.parametrize("fmt", FORMATS)
    def test_the_deprecation_marker_and_replacement_survive(self, fmt: str) -> None:
        from fmp_data.mcp.tools_manifest import DEPRECATED_TOOLS

        rendered = self._render(list_available_tools(), fmt)

        assert DEPRECATED_TOOLS, "floor: nothing is deprecated"
        for spec, replacement in DEPRECATED_TOOLS.items():
            assert spec in rendered
            assert replacement in rendered, f"{fmt} loses the replacement for {spec}"
