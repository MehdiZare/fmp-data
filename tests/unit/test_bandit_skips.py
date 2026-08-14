"""Bandit skips stay narrow (#273)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_bandit_global_skips_are_only_assert_used() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    start = text.index("[tool.bandit]")
    end = text.index("[tool.bandit.assert_used]")
    block = text[start:end]
    assert '"B101"' in block
    for code in ("B404", "B603", "B607", "B608"):
        assert code not in block
