"""CodeQL workflow is present, SHA-pinned, and Python-only."""

from __future__ import annotations

from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "codeql.yml"


def test_codeql_workflow_is_sha_pinned() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "languages: python" in text
    assert "build-mode: none" in text
    assert "security-events: write" in text
    assert "github/codeql-action/init@" in text
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("uses:"):
            continue
        _, ref = stripped.split("uses:", 1)
        ref = ref.strip()
        if ref.startswith("./"):
            continue
        action, _, pin = ref.partition("@")
        pin = pin.split()[0]
        assert len(pin) == 40 and all(c in "0123456789abcdef" for c in pin), (
            f"{action} is not pinned to a 40-char SHA: {pin!r}"
        )
