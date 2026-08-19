"""Keep a Changelog version sections must not repeat standard headings (#360).

Folding Unreleased into 2.7.0 left two Added / four Changed / three Fixed /
two Security under the same version heading, with FMP API surface in the
middle. The merge is editorial; this pin keeps it from happening again on
Unreleased and on dated ``## [X.Y.Z] - YYYY-MM-DD`` headings from 2.7.0+.

Empty Unreleased is allowed (the post-cut bucket). Duplicate standard
headings are not.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

_STANDARD = frozenset(
    {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
)
# Keep a Changelog dates the version: `## [2.7.0] - 2026-08-19`.
# A `$` immediately after `]` would skip every shipped section and leave
# only Unreleased gated (#360 follow-up on #369).
_VERSION_HEADER = re.compile(
    r"^## (?:Unreleased|\[(\d+)\.(\d+)\.[^\]]+\])(?:\s+-.*)?\s*$"
)
_HEADING = re.compile(r"^### (.+)$", re.M)


def _gated_sections(text: str) -> list[tuple[str, str]]:
    """``(header, body)`` for Unreleased and every ``[X.Y.*]`` with X.Y >= 2.7."""
    chunks = re.split(r"(?=^## )", text, flags=re.M)
    out: list[tuple[str, str]] = []
    for chunk in chunks:
        lines = chunk.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        match = _VERSION_HEADER.match(header)
        if match is None:
            continue
        if match.group(1) is not None:
            major, minor = int(match.group(1)), int(match.group(2))
            if (major, minor) < (2, 7):
                continue
        out.append((header, chunk))
    return out


def test_version_header_matches_dated_keep_a_changelog() -> None:
    """The uniqueness pin must see dated 2.7+ headings, not only Unreleased."""
    dated = _VERSION_HEADER.match("## [2.7.0] - 2026-08-19")
    assert dated is not None
    assert dated.group(1) == "2"
    assert dated.group(2) == "7"
    assert _VERSION_HEADER.match("## Unreleased") is not None
    assert _VERSION_HEADER.match("## [2.6.0] - 2026-08-10") is not None
    assert _VERSION_HEADER.match("## Future Roadmap") is None


def test_gated_sections_include_dated_2_7_and_allow_empty_unreleased() -> None:
    text = (
        "## Unreleased\n\n"
        "## [2.7.0] - 2026-08-19\n\n### Added\n\n- note\n\n"
        "## [2.6.0] - 2026-08-10\n\n### Added\n\n- old\n"
    )
    sections = _gated_sections(text)
    headers = [header for header, _ in sections]
    assert headers == ["## Unreleased", "## [2.7.0] - 2026-08-19"]
    unreleased_headings = [
        name for name in _HEADING.findall(sections[0][1]) if name in _STANDARD
    ]
    assert unreleased_headings == []


def test_changelog_standard_headings_are_unique_from_2_7() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    sections = _gated_sections(text)
    assert sections, "expected Unreleased and/or 2.7.0+ sections"
    dated = [header for header, _ in sections if header.startswith("## [")]
    assert dated, (
        "uniqueness pin matched no dated 2.7+ section; "
        "the version-header regex is probably ignoring `## [X.Y.Z] - date`"
    )

    duplicates: dict[str, list[str]] = {}
    for header, body in sections:
        headings = _HEADING.findall(body)
        standard = [name for name in headings if name in _STANDARD]
        # Empty Unreleased is the post-cut bucket (#360). Version sections
        # that still have notes must not repeat a standard heading.
        repeated = sorted(
            name for name, count in Counter(standard).items() if count > 1
        )
        if repeated:
            duplicates[header] = repeated

    assert duplicates == {}, f"duplicate changelog headings: {duplicates}"


def test_2_7_0_puts_fmp_api_surface_first() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    match = re.search(r"^## \[2\.7\.0\].*?(?=^## \[)", text, re.M | re.S)
    assert match is not None, "missing ## [2.7.0] section"
    headings = _HEADING.findall(match.group(0))
    assert headings, "2.7.0 has no ### headings"
    assert headings[0].startswith("FMP API surface"), headings[0]
    for name in ("Added", "Changed", "Fixed", "Security"):
        assert headings.count(name) == 1, headings
