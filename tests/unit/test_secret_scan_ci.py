"""CI secret scan must inspect the committed tree, not only cassettes."""

from __future__ import annotations

from pathlib import Path

CI = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
PRECOMMIT = Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml"


def test_secret_scan_job_uses_baseline_hook() -> None:
    text = CI.read_text(encoding="utf-8")
    assert "detect-secrets-hook --baseline .secrets.baseline" in text
    assert "Secret Scan (cassettes)" not in text
    assert "skipping credential scan" not in text


def test_pre_commit_detect_secrets_includes_tests() -> None:
    text = PRECOMMIT.read_text(encoding="utf-8")
    assert "detect-secrets" in text
    assert r"exclude: tests/.*\.py$" not in text
