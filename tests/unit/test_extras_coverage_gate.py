"""Extras coverage stays a separate gate (#273).

The core 80% report still omits ``lc`` / ``mcp`` / Redis. A dedicated
config + nox session + CI job fail under the measured extras baseline
without folding those trees into Test-Matrix.
"""

from __future__ import annotations

import configparser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
NOXFILE = REPO_ROOT / "noxfile.py"
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
GITIGNORE = REPO_ROOT / ".gitignore"
EXTRAS_COVERAGERC = REPO_ROOT / "extras.coveragerc"


def _coverage_run_omit_block() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    start = text.index("[tool.coverage.run]")
    end = text.index("[tool.coverage.paths]")
    return text[start:end]


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
    assert "fmp_data/lc" in source
    assert "fmp_data/mcp" in source
    assert "fmp_data/cache/redis_backend.py" in source
    assert parser.getint("report", "fail_under") == 65


def test_coverage_extras_session_uses_the_dedicated_config() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert "def coverage_extras(" in source
    assert "extras.coveragerc" in source
    assert "cache-redis" in source
    assert "langchain" in source
    assert "mcp-server" in source or '"mcp"' in source


def test_mcp_server_session_collects_every_test_mcp_star() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert 'glob("test_mcp*.py")' in source or "glob('test_mcp*.py')" in source
    assert "_mcp_unit_tests" in source


def test_ci_runs_extras_coverage_separately() -> None:
    text = CI.read_text(encoding="utf-8")
    assert "nox -s coverage_extras" in text
    assert "coverage_local" in text


def test_uv_lock_stays_uncommitted() -> None:
    text = GITIGNORE.read_text(encoding="utf-8")
    assert "uv.lock" in text
