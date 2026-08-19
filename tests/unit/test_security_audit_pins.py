"""Security session audits a live extras export, not a committed lock."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOXFILE = REPO_ROOT / "noxfile.py"


def test_no_committed_hashed_audit_lock() -> None:
    assert not (REPO_ROOT / ".github" / "requirements-audit.txt").exists()


def test_security_session_exports_then_audits() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert '"export"' in source
    assert "langchain" in source
    assert "cache-redis" in source
    assert "--strict" in source
    assert "--no-deps" in source
    assert "--disable-pip" in source
    assert "create_tmp" in source


def test_dev_sync_uses_pyproject_group() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert '--group", "dev"' in source or "--group', 'dev'" in source
    assert "pytest>=8.3.3" not in source
