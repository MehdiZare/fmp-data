"""Extras coverage stays a separate gate (#273).

The core 80% report still omits ``lc`` / ``mcp`` / Redis. A dedicated
config + nox session + CI job fail under the measured extras baseline
without folding those trees into the core 80% job.
"""

from __future__ import annotations

import configparser
from pathlib import Path
import re
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
NOXFILE = REPO_ROOT / "noxfile.py"
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
GITIGNORE = REPO_ROOT / ".gitignore"
EXTRAS_COVERAGERC = REPO_ROOT / "extras.coveragerc"

# Raised from 65 once dedicated tests took the measured extras number from
# 66.78% to 86.99% (#282). Keep the config and the nox session in step.
EXTRAS_FAIL_UNDER = 80


def _coverage_run_omit_block() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    start = text.index("[tool.coverage.run]")
    end = text.index("[tool.coverage.paths]")
    return text[start:end]


def _coverage_extras_session_source() -> str:
    text = NOXFILE.read_text(encoding="utf-8")
    start = text.index("def coverage_extras(")
    rest = text[start:]
    next_session = rest.find("\n@nox.session", 1)
    return rest if next_session == -1 else rest[:next_session]


def _test_matrix_expected_job() -> str:
    text = CI.read_text(encoding="utf-8")
    start = text.index("  test-matrix-expected:")
    next_job = text.find("\n  ", start + 1)
    while next_job != -1 and text[next_job + 3 : next_job + 4] in {" ", "\t"}:
        next_job = text.find("\n  ", next_job + 1)
    return text[start:] if next_job == -1 else text[start:next_job]


def test_core_coverage_still_omits_extras() -> None:
    block = _coverage_run_omit_block()
    assert '"fmp_data/lc/*"' in block
    assert '"fmp_data/mcp/*"' in block
    assert '"fmp_data/cache/redis_backend.py"' in block


def test_extras_coveragerc_gates_the_omitted_trees() -> None:
    assert EXTRAS_COVERAGERC.is_file()
    parser = configparser.ConfigParser()
    parser.read(EXTRAS_COVERAGERC, encoding="utf-8")
    source = parser.get("run", "source")
    assert "fmp_data.lc" in source
    assert "fmp_data.mcp" in source
    assert "fmp_data.cache.redis_backend" in source
    assert "fmp_data/cache/redis_backend.py" not in source
    assert parser.getint("report", "fail_under") == EXTRAS_FAIL_UNDER


def test_coverage_extras_session_uses_the_dedicated_config() -> None:
    source = _coverage_extras_session_source()
    assert "--cov-config=extras.coveragerc" in source
    assert f"--cov-fail-under={EXTRAS_FAIL_UNDER}" in source
    assert "--cov=fmp_data.lc" in source
    assert "--cov=fmp_data.mcp" in source
    assert "--cov=fmp_data.cache.redis_backend" in source
    assert "cache-redis" in source
    assert "langchain" in source
    assert "mcp-server" in source


def test_mcp_server_session_collects_every_test_mcp_star() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert 'glob("test_mcp*.py")' in source or "glob('test_mcp*.py')" in source
    assert "_mcp_unit_tests" in source
    collected = {p.name for p in (REPO_ROOT / "tests" / "unit").glob("test_mcp*.py")}
    assert {
        "test_mcp.py",
        "test_mcp_cli.py",
        "test_mcp_config_perms.py",
        "test_mcp_entry_point_coherence.py",
    } <= collected


def test_ci_runs_extras_coverage_separately() -> None:
    text = CI.read_text(encoding="utf-8")
    assert "nox -s coverage_extras" in text
    assert "coverage_local" in text
    expected = _test_matrix_expected_job()
    assert "extras-coverage" in expected
    assert "needs.extras-coverage.result" in expected


def test_exclude_lines_regexes_actually_compile_and_match() -> None:
    """``extras.coveragerc`` is INI, so TOML double-escaping is wrong (#282).

    ``class .*\\\\(Protocol\\\\):`` was copied from ``pyproject.toml``, where
    TOML collapses ``\\\\(`` to ``\\(``. In an INI file it stays a literal
    backslash, so the pattern compiled but could never match a real
    ``class Foo(Protocol):`` line and the exclusion silently did nothing.
    """
    parser = configparser.ConfigParser()
    parser.read(EXTRAS_COVERAGERC, encoding="utf-8")
    patterns = [
        line.strip()
        for line in parser.get("report", "exclude_lines").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for pattern in patterns:
        re.compile(pattern)  # must not raise

    protocol = [p for p in patterns if "Protocol" in p]
    assert protocol, f"no Protocol exclusion found in {patterns}"
    assert any(re.search(p, "class Foo(Protocol):") for p in protocol), (
        f"Protocol exclusion never matches a real declaration: {protocol}"
    )


def test_ci_jobs_that_must_be_required_checks_run_unconditionally() -> None:
    """Every job named in #282 must run on all PRs to be a safe gate.

    A required check that never reports on some PRs blocks them forever, so
    none of these may carry a ``paths:``/``paths-ignore:`` filter or a job
    level ``if:``.
    """
    text = CI.read_text(encoding="utf-8")
    assert "paths:" not in text
    assert "paths-ignore:" not in text

    for job in ("coverage:", "extras-coverage:", "secret-scan:", "actions-shell:"):
        start = text.index(f"  {job}")
        body = text[start : start + 400]
        assert "\n    if:" not in body, f"{job} is conditional; unsafe to require"


def test_uv_lock_stays_uncommitted() -> None:
    """``uv.lock`` is ignored *and* actually absent from the index (#273).

    Grepping ``.gitignore`` alone would still pass if someone force-added the
    lock, so assert the tracked-file set too.
    """
    assert "uv.lock" in GITIGNORE.read_text(encoding="utf-8")
    tracked = subprocess.run(
        ["git", "ls-files", "--", "uv.lock", "poetry.lock"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert tracked == [], f"lock files must stay untracked, found: {tracked}"


def test_lock_file_policy_is_documented() -> None:
    """The decision is recorded, not just enforced (#273).

    The previous ``.gitignore`` rationale cited a non-existent "GitHub 500KB
    warning" (that is pre-commit's ``check-added-large-files`` default), so
    pin the real reasoning against silent reversion.
    """
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "### Lock file policy" in contributing
    assert "not committed" in contributing
    assert "pip-audit --strict" in contributing

    gitignore = GITIGNORE.read_text(encoding="utf-8")
    assert "500KB" not in gitignore
    assert "CONTRIBUTING.md" in gitignore
