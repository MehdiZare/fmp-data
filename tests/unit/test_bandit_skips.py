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


def _ruff_lint_block() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    start = text.index("[tool.ruff.lint]")
    end = text.index("[tool.ruff.lint.isort]")
    return text[start:end]


def test_ruff_does_not_globally_ignore_the_bandit_twins() -> None:
    """#278 narrowed bandit's skips but not ruff's (#252).

    `S603` / `S607` are flake8-bandit's twins of `B603` / `B607`. Removing the
    latter from `[tool.bandit] skips` while the former stayed in
    `[tool.ruff.lint] ignore` left the rule unenforced by *either* tool --
    the narrowing looked done and was not.
    """
    block = _ruff_lint_block()
    ignore = block[
        block.index("ignore = [") : block.index("[tool.ruff.lint.per-file-ignores]")
    ]
    assert '"S101"' in ignore, "guard is vacuous if the ignore list moved"
    for code in ("S603", "S607", "S608"):
        assert f'"{code}"' not in ignore, (
            f"{code} is globally ignored again; annotate the call site with a "
            f"targeted `# noqa` and a reason instead"
        )


def test_scripts_are_scanned_by_both_tools() -> None:
    """`scripts/` used to be exempt from ruff's S rules *and* bandit."""
    text = PYPROJECT.read_text(encoding="utf-8")
    per_file = text[
        text.index("[tool.ruff.lint.per-file-ignores]") : text.index(
            "[tool.ruff.lint.isort]"
        )
    ]
    assert '"scripts/*"' not in per_file

    bandit = text[text.index("[tool.bandit]") : text.index("[tool.bandit.assert_used]")]
    assert '"scripts"' not in bandit
