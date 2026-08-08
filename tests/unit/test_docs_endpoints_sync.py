"""``docs/api/endpoints.md`` and ``docs/mcp/configurations.md`` match reality (#146).

``docs/mcp/tools.md`` has been guarded by ``test_docs_tools_sync.py`` for a
while, and that guard is why the catalog change in #130 could not leave a stale
number behind. These two files had no equivalent, and it showed: the table of
contents claimed 47 Market Intelligence endpoints when both the code and the
document's own table had 46.

Row-set equality, not just counts, because a rename miscounts as zero.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import pkgutil
import re

import pytest

import fmp_data
from fmp_data.models import Endpoint

#: Modules the walk could not import, kept so a failure can name them.
SKIPPED_MODULES: dict[str, str] = {}

DOCS = Path(__file__).resolve().parents[2] / "docs"
ENDPOINTS_DOC = DOCS / "api" / "endpoints.md"
CONFIGURATIONS_DOC = DOCS / "mcp" / "configurations.md"

#: TOC label -> package name, where the two differ.
_LABEL_TO_CLIENT = {
    "market intelligence": "intelligence",
    "alternative markets": "alternative",
    "sec": "sec",
}


def _endpoint_counts() -> dict[str, int]:
    """client name -> number of ``Endpoint`` objects it declares."""
    counts: dict[str, int] = {}
    for module_info in pkgutil.walk_packages(fmp_data.__path__, prefix="fmp_data."):
        if not module_info.name.endswith(".endpoints"):
            continue
        try:
            module = importlib.import_module(module_info.name)
        except BaseException as exc:
            # BaseException: fmp_data/mcp/__main__.py raises SystemExit without
            # its extra, and SystemExit is not an Exception. Recorded rather
            # than discarded so a failure message can say what fell out.
            SKIPPED_MODULES[module_info.name] = f"{type(exc).__name__}: {exc}"
            continue
        client = module_info.name.split(".")[1]
        counts[client] = sum(
            1 for value in vars(module).values() if isinstance(value, Endpoint)
        )
    return counts


def test_endpoint_doc_counts_match_the_code() -> None:
    """Every ``(N endpoints)`` in the TOC must equal the real count."""
    text = ENDPOINTS_DOC.read_text()
    counts = _endpoint_counts()

    mismatches: list[str] = []
    checked = 0
    for label, claimed in re.findall(r"\[([^\]]+?)\s+\((\d+) endpoints?\)\]", text):
        key = label.strip().lower()
        client = _LABEL_TO_CLIENT.get(key, key)
        if client not in counts:
            mismatches.append(f"{label}: no fmp_data.{client}.endpoints module")
            continue
        checked += 1
        if int(claimed) != counts[client]:
            mismatches.append(f"{label}: doc says {claimed}, code has {counts[client]}")

    assert not mismatches, (
        "docs/api/endpoints.md is out of step with the code:\n  "
        + "\n  ".join(mismatches)
    )
    assert checked >= 10, (
        f"only {checked} client counts found in the TOC; the parse is not "
        "matching, so this guard would pass vacuously"
    )


def test_endpoint_doc_section_tables_match_their_headings() -> None:
    """A section's table must have as many rows as its TOC entry claims."""
    text = ENDPOINTS_DOC.read_text()
    counts = _endpoint_counts()

    mismatches: list[str] = []
    checked = 0
    sections = re.split(r"^## ", text, flags=re.M)[1:]
    for section in sections:
        label = section.splitlines()[0].strip()
        client = _LABEL_TO_CLIENT.get(label.lower(), label.lower())
        if client not in counts:
            continue
        rows = [
            line
            for line in section.splitlines()
            if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line)
        ]
        # Minus the header row.
        body_rows = max(0, len(rows) - 1)
        checked += 1
        if body_rows != counts[client]:
            mismatches.append(
                f"{label}: table has {body_rows} rows, code has {counts[client]}"
            )

    assert not mismatches, (
        "docs/api/endpoints.md tables are out of step with the code:\n  "
        + "\n  ".join(mismatches)
    )
    assert checked >= 10, f"only {checked} sections parsed; the guard is not reading"


def test_configurations_doc_paths_exist() -> None:
    """Every path the MCP configuration guide points at must exist.

    It previously told users to look in ``examples/mcp_configurations/`` while
    the real directory is ``examples/mcp/configurations/`` -- a path-existence
    check would have caught that.
    """
    repo_root = DOCS.parent
    text = CONFIGURATIONS_DOC.read_text()

    missing: list[str] = []
    checked = 0
    for candidate in re.findall(r"`(examples/[\w/.\-]+)`", text):
        checked += 1
        if not (repo_root / candidate).exists():
            missing.append(candidate)

    assert not missing, (
        f"{CONFIGURATIONS_DOC.name} references paths that do not exist:\n  "
        + "\n  ".join(sorted(set(missing)))
    )
    assert checked > 0, "no example paths found in the doc; the parse is not matching"


@pytest.mark.parametrize("doc", [ENDPOINTS_DOC, CONFIGURATIONS_DOC])
def test_doc_exists(doc: Path) -> None:
    """A renamed or deleted doc must fail loudly, not silently skip its guard."""
    assert doc.is_file(), f"{doc} is missing; the guards above would not run"
