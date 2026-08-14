"""GitHub Actions Dependabot groups keep lockstep pairs together."""

from __future__ import annotations

from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / ".github" / "dependabot.yml"


def test_github_actions_groups_cover_codeql_and_artifacts() -> None:
    text = CONFIG.read_text(encoding="utf-8")
    assert 'package-ecosystem: "github-actions"' in text
    assert "codeql-action:" in text
    assert "github/codeql-action*" in text
    assert "artifact-actions:" in text
    assert "actions/upload-artifact" in text
    assert "actions/download-artifact" in text
