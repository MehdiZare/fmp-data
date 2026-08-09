"""``docs/api/endpoints.md`` and ``docs/mcp/configurations.md`` match reality (#146).

``docs/mcp/tools.md`` has been guarded by ``test_docs_tools_sync.py`` for a
while, and that guard is why the catalog change in #130 could not leave a stale
number behind. These two files had no equivalent, and it showed: the table of
contents claimed 47 Market Intelligence endpoints when both the code and the
document's own table had 46.

Row-set equality, not just counts, because a rename miscounts as zero.
"""

from __future__ import annotations

from collections import Counter
import importlib
from pathlib import Path
import pkgutil
import re

import pytest

import fmp_data
from fmp_data.models import Endpoint

#: Modules the walk could not import, kept so a failure can name them.
SKIPPED_MODULES: dict[str, str] = {}


def _record_walk_error(name: str) -> None:
    """Record a package that blew up *while being walked*.

    Without an ``onerror`` callback ``walk_packages`` re-raises anything that
    is not an ``ImportError``, and it raises it from the ``for`` header --
    outside the ``try`` below, which only wraps the explicit ``import_module``
    of a ``.endpoints`` module. So the two guards catch different failures and
    both are needed.
    """
    SKIPPED_MODULES[name] = "raised while being walked"


DOCS = Path(__file__).resolve().parents[2] / "docs"
ENDPOINTS_DOC = DOCS / "api" / "endpoints.md"
CONFIGURATIONS_DOC = DOCS / "mcp" / "configurations.md"

#: TOC label -> package name, where the two differ.
_LABEL_TO_CLIENT = {
    "market intelligence": "intelligence",
    "alternative markets": "alternative",
}


def _endpoint_paths() -> dict[str, dict[str, str]]:
    """client name -> {endpoint name: path} for every ``Endpoint`` it declares."""
    declared: dict[str, dict[str, str]] = {}
    for module_info in pkgutil.walk_packages(
        fmp_data.__path__, prefix="fmp_data.", onerror=_record_walk_error
    ):
        if not module_info.name.endswith(".endpoints"):
            continue
        try:
            module = importlib.import_module(module_info.name)
        except BaseException as exc:
            # BaseException, not Exception, because an `endpoints` module that
            # calls sys.exit at import time raises SystemExit, which is not an
            # Exception and would take the whole scan down. (The often-cited
            # fmp_data/mcp/__main__.py cannot reach here -- the `.endpoints`
            # filter above excludes it -- so this is defence, not a fix for
            # that specific module.) Recorded rather than discarded so a
            # failure message can say what fell out.
            SKIPPED_MODULES[module_info.name] = f"{type(exc).__name__}: {exc}"
            continue
        client = module_info.name.split(".")[1]
        declared[client] = {
            value.name: value.path
            for value in vars(module).values()
            if isinstance(value, Endpoint)
        }
    return declared


def _endpoint_counts() -> dict[str, int]:
    """client name -> number of ``Endpoint`` objects it declares."""
    return {client: len(paths) for client, paths in _endpoint_paths().items()}


def _skipped_suffix() -> str:
    """Name what fell out of the walk, so a failure is not read as a full scan."""
    if not SKIPPED_MODULES:
        return ""
    return "\n\nModules that did not import (excluded from the counts above):\n  " + (
        "\n  ".join(f"{name}: {why}" for name, why in sorted(SKIPPED_MODULES.items()))
    )


def _doc_rows(section: str) -> list[tuple[str, str]]:
    """``(endpoint name, path)`` for every table row in a section.

    The first column is the endpoint's ``name`` and the second its ``path``,
    both in backticks. Rows inside fenced code blocks are ignored, as is the
    ``|---|---|`` alignment row and the header.
    """
    rows: list[tuple[str, str]] = []
    fenced = False
    for line in section.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 4:
            continue
        name = re.match(r"\s*`([^`]+)`", cells[1])
        path = re.match(r"\s*`([^`]+)`", cells[2])
        if name and path:
            rows.append((name.group(1), path.group(1)))
    return rows


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
        + _skipped_suffix()
    )
    assert checked >= 10, (
        f"only {checked} client counts found in the TOC; the parse is not "
        "matching, so this guard would pass vacuously"
    )


def test_endpoint_doc_section_headings_match_the_code() -> None:
    """Each section's own ``### N endpoints`` heading must equal the real count.

    The TOC and the heading are two independent copies of the same number.
    Guarding only the TOC is what let ``## Market Intelligence`` keep claiming
    47 in its heading after the TOC was corrected to 46.
    """
    counts = _endpoint_counts()

    mismatches: list[str] = []
    checked = 0
    for section in re.split(r"^## ", ENDPOINTS_DOC.read_text(), flags=re.M)[1:]:
        label = section.splitlines()[0].strip()
        client = _LABEL_TO_CLIENT.get(label.lower(), label.lower())
        if client not in counts:
            continue
        heading = re.search(r"^### (\d+) endpoints?$", section, flags=re.M)
        if heading is None:
            mismatches.append(f"{label}: no `### N endpoints` heading")
            continue
        checked += 1
        if int(heading.group(1)) != counts[client]:
            mismatches.append(
                f"{label}: heading says {heading.group(1)}, code has {counts[client]}"
            )

    assert not mismatches, (
        "docs/api/endpoints.md section headings are out of step with the code:\n  "
        + "\n  ".join(mismatches)
        + _skipped_suffix()
    )
    assert checked >= 10, f"only {checked} section headings parsed; the guard is blind"


def test_endpoint_doc_tables_match_the_code_row_for_row() -> None:
    """Row-set equality, not just counts, because a rename miscounts as zero.

    ``crypto_symbol_news`` / ``forex_symbol_news`` and ``search_name`` were all
    documented under names the code does not use, and the counts matched
    exactly, so nothing noticed. Paths are compared too: four rows documented
    the bare ``/stable/historical-price-eod`` that ``CLAUDE.md`` forbids, while
    the code correctly requests the ``/full`` variant.

    The code is the authority. ``Endpoint.name`` is not cosmetic -- it is the
    cache-key prefix and the cache-TTL lookup key -- so a disagreement is fixed
    in the document, not by renaming the endpoint.
    """
    declared = _endpoint_paths()

    mismatches: list[str] = []
    checked = 0
    for section in re.split(r"^## ", ENDPOINTS_DOC.read_text(), flags=re.M)[1:]:
        label = section.splitlines()[0].strip()
        client = _LABEL_TO_CLIENT.get(label.lower(), label.lower())
        if client not in declared:
            continue
        paths = declared[client]
        row_list = _doc_rows(section)
        rows = dict(row_list)
        # Count the list, not the dict: a duplicated row would otherwise be
        # collapsed before it was counted, and set equality alone cannot see
        # it. The row-count check this replaced did catch that, so counting
        # the dict would have been a regression.
        checked += len(row_list)

        for name, count in sorted(Counter(name for name, _ in row_list).items()):
            if count > 1:
                mismatches.append(f"{label}: `{name}` appears in {count} rows")
        for name in sorted(rows.keys() - paths.keys()):
            mismatches.append(f"{label}: doc row `{name}` names no endpoint in code")
        for name in sorted(paths.keys() - rows.keys()):
            mismatches.append(f"{label}: endpoint `{name}` has no row in the doc")
        for name in sorted(rows.keys() & paths.keys()):
            documented = rows[name].removeprefix("/stable/").strip("/")
            if documented != paths[name].strip("/"):
                mismatches.append(
                    f"{label}: `{name}` path is `{rows[name]}` in the doc "
                    f"but `{paths[name]}` in code"
                )

    assert not mismatches, (
        "docs/api/endpoints.md rows are out of step with the code:\n  "
        + "\n  ".join(mismatches)
        + _skipped_suffix()
    )
    assert checked >= 250, (
        f"only {checked} table rows parsed, expected >= 250; the row parse is "
        "not matching, so this guard would pass vacuously"
    )


def test_configurations_doc_paths_exist() -> None:
    """Every path the MCP configuration guide points at must exist.

    It previously told users to look in ``examples/mcp_configurations/`` while
    the real directory is ``examples/mcp/configurations/`` -- a path-existence
    check would have caught that.

    Paths are matched bare rather than only inside backticks. The three that
    matter most are the concrete manifests in ``export FMP_MCP_MANIFEST=...``
    and ``create_app(...)`` snippets, which live inside fenced code blocks and
    carry no backticks -- so a backtick-only match checked the directory and
    none of the files a reader actually copy-pastes.
    """
    repo_root = DOCS.parent
    text = CONFIGURATIONS_DOC.read_text()

    missing: list[str] = []
    checked = 0
    for candidate in sorted(set(re.findall(r"examples/[\w/.\-]+", text))):
        candidate = candidate.rstrip(".,")
        checked += 1
        if not (repo_root / candidate).exists():
            missing.append(candidate)

    assert not missing, (
        f"{CONFIGURATIONS_DOC.name} references paths that do not exist:\n  "
        + "\n  ".join(sorted(set(missing)))
    )
    assert checked >= 4, (
        f"only {checked} example paths found in the doc; the directory plus "
        "three manifests are expected, so the parse is not matching"
    )


def test_every_client_has_a_documented_section() -> None:
    """Every client with an ``endpoints`` module must appear in the document.

    The other guards iterate over the document's sections, so they can only
    ever prove doc ⊆ code. A brand-new client documented nowhere has no
    section for them to iterate over, and all of them stay green -- which is
    the exact drift class #146 is about. This is the code ⊆ doc direction.

    (A *renamed* section is already caught: its TOC label no longer resolves
    to a module and ``test_endpoint_doc_counts_match_the_code`` reports it.)
    """
    documented: set[str] = set()
    for section in re.split(r"^## ", ENDPOINTS_DOC.read_text(), flags=re.M)[1:]:
        label = section.splitlines()[0].strip().lower()
        documented.add(_LABEL_TO_CLIENT.get(label, label))

    undocumented = sorted(set(_endpoint_paths()) - documented)
    assert not undocumented, (
        "clients with an `endpoints` module but no section in "
        f"docs/api/endpoints.md: {undocumented}. Add a `## <Client>` section "
        "with its `### N endpoints` heading and table, or map its label in "
        "_LABEL_TO_CLIENT if the section is named differently." + _skipped_suffix()
    )


@pytest.mark.parametrize("doc", [ENDPOINTS_DOC, CONFIGURATIONS_DOC])
def test_doc_exists(doc: Path) -> None:
    """A renamed or deleted doc must fail loudly, not silently skip its guard."""
    assert doc.is_file(), f"{doc} is missing; the guards above would not run"
