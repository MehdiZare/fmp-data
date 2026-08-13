"""Security session audits a hashed, pinned extras export."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = REPO_ROOT / ".github" / "requirements-audit.txt"
NOXFILE = REPO_ROOT / "noxfile.py"


def test_requirements_audit_is_hashed_and_covers_published_extras() -> None:
    text = REQUIREMENTS.read_text(encoding="utf-8")
    assert "--hash=sha256:" in text
    for package in ("httpx==", "pydantic==", "langchain-core==", "mcp==", "redis=="):
        assert package in text
    assert "mkdocs==" not in text


def test_security_session_uses_strict_file_audit() -> None:
    source = NOXFILE.read_text(encoding="utf-8")
    assert "--strict" in source
    assert "--no-deps" in source
    assert "--disable-pip" in source
    assert "requirements-audit.txt" in source
