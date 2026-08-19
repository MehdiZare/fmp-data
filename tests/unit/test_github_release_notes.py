"""GitHub Release notes come from CHANGELOG.md, not the squash log (#370)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "github_release_notes.py"
_CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"
_SPEC = importlib.util.spec_from_file_location("github_release_notes", _SCRIPT)
assert _SPEC and _SPEC.loader
notes = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(notes)

_SAMPLE = """# Changelog

## Unreleased

### Added

- unreleased note

## [2.7.0] - 2026-08-19

Released from `dev`.

### FMP API surface (scan this first)

- diluted P/E

### Added

- senate trades

## [2.6.0] - 2026-08-10

### Added

- old note
"""


def test_extract_section_drops_heading_and_neighbors() -> None:
    body = notes.extract_section(_SAMPLE, "2.7.0")
    assert body.startswith("Released from `dev`.")
    assert "### FMP API surface (scan this first)" in body
    assert "### Added" in body
    assert "senate trades" in body
    assert "## [2.7.0]" not in body
    assert "unreleased note" not in body
    assert "old note" not in body
    assert "## Unreleased" not in body
    assert "## [2.6.0]" not in body


def test_extract_section_strips_v_prefix() -> None:
    assert notes.extract_section(_SAMPLE, "v2.7.0") == notes.extract_section(
        _SAMPLE, "2.7.0"
    )


def test_extract_section_missing_version_raises() -> None:
    with pytest.raises(ValueError, match=r"no ## \[2\.8\.0\] section"):
        notes.extract_section(_SAMPLE, "2.8.0")


def test_extract_section_empty_body_raises() -> None:
    text = "## [2.7.1] - 2026-08-20\n\n## [2.7.0] - 2026-08-19\n\nbody\n"
    with pytest.raises(ValueError, match=r"## \[2\.7\.1\] is empty"):
        notes.extract_section(text, "2.7.1")


def test_render_github_release_wraps_install_and_links() -> None:
    rendered = notes.render_github_release(
        tag="v2.7.0", version="2.7.0", body="Released from `dev`."
    )
    assert rendered.startswith("## 🎉 Release v2.7.0\n")
    assert "Released from `dev`." in rendered
    assert "pip install fmp-data==2.7.0" in rendered
    assert "https://pypi.org/project/fmp-data/2.7.0/" in rendered
    assert "https://mehdizare.github.io/fmp-data/" in rendered
    assert "### 📝 Commits" not in rendered


def test_live_changelog_2_7_0_extracts_fmp_surface_first() -> None:
    body = notes.extract_section(_CHANGELOG.read_text(encoding="utf-8"), "2.7.0")
    assert "### FMP API surface (scan this first)" in body
    assert body.index("### FMP API surface") < body.index("### Added")
    assert "## Unreleased" not in body
    assert "## [2.6.0]" not in body


def test_cli_writes_release_file(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(_SAMPLE, encoding="utf-8")
    out = tmp_path / "release-notes.md"
    rc = notes.main(
        [
            "--changelog",
            str(changelog),
            "--version",
            "2.7.0",
            "--tag",
            "v2.7.0",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "Released from `dev`." in text
    assert "pip install fmp-data==2.7.0" in text
    assert "unreleased note" not in text


def test_cli_missing_section_is_nonzero(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(_SAMPLE, encoding="utf-8")
    rc = notes.main(
        [
            "--changelog",
            str(changelog),
            "--version",
            "9.9.9",
            "--out",
            str(tmp_path / "x.md"),
        ]
    )
    assert rc == 1
