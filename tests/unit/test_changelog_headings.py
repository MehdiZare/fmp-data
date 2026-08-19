"""Keep a Changelog version sections must not repeat standard headings (#360).

Folding Unreleased into 2.7.0 left two Added / four Changed / three Fixed /
two Security under the same version heading, with FMP API surface in the
middle. The merge is editorial; this pin keeps it from happening again on
Unreleased and on 2.7.0+.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

_STANDARD = frozenset(
    {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
)
_VERSION_HEADER = re.compile(r"^## (?:Unreleased|\[(\d+)\.(\d+)\.[^\]]+\])\s*$")
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


def test_changelog_standard_headings_are_unique_from_2_7() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    sections = _gated_sections(text)
    assert sections, "expected Unreleased and/or 2.7.0+ sections"

    duplicates: dict[str, list[str]] = {}
    for header, body in sections:
        headings = _HEADING.findall(body)
        standard = [name for name in headings if name in _STANDARD]
        assert standard, f"{header}: no standard Keep a Changelog headings"
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
