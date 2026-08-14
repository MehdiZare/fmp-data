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


def test_codeql_init_and_analyze_share_the_same_pin() -> None:
    """init and analyze must stay on the same codeql-action release.

    Mixing v3 and v4 fails at runtime with:
    ``Loaded a configuration file for version 'X', but running version 'Y'``.
    Dependabot opens one PR per action id, so this is the lock that keeps
    the pair together after a split bump.
    """
    pins: list[str] = []
    for line in WORKFLOW.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("uses:"):
            continue
        ref = stripped.split("uses:", 1)[1].strip()
        action, _, pin = ref.partition("@")
        if not action.startswith("github/codeql-action/"):
            continue
        pins.append(pin.split()[0])
    assert len(pins) >= 2, f"expected init and analyze pins, got {pins}"
    assert len(set(pins)) == 1, f"codeql-action pins must match: {pins}"
