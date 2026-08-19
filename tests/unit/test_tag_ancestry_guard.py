"""The TestPyPI tag guard must compare against fully-qualified refs (#252).

``git rev-parse`` resolves an unqualified name in this order (gitrevisions):
``refs/<name>``, ``refs/tags/<name>``, ``refs/heads/<name>``,
``refs/remotes/<name>``. ``actions/checkout`` with ``fetch-depth: 0`` mirrors
every tag verbatim via ``+refs/tags/*:refs/tags/*``, so a tag literally named
``origin/main`` lands at ``refs/tags/origin/main`` and outranks
``refs/remotes/origin/main``.

The #268 guard compared against the bare name ``origin/main``, so that shadow
tag made ``git merge-base --is-ancestor`` test HEAD against an attacker-chosen
commit. Git only warns ("refname is ambiguous"), which ``set -euo pipefail``
does not trap, so the job went green and published an arbitrary tree.
"""

from __future__ import annotations

from pathlib import Path
import re

WORKFLOW = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "publish-testpypi.yml"
)


def _guard_step() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Require tag commit reachable from main or dev")
    rest = text[start + 1 :]
    end = rest.find("\n      - name:")
    return rest if end == -1 else rest[:end]


def test_guard_step_still_exists() -> None:
    assert "Require tag commit reachable from main or dev" in WORKFLOW.read_text(
        encoding="utf-8"
    )


def test_ancestry_compares_fully_qualified_remote_refs() -> None:
    """Both ``--is-ancestor`` targets must be under ``refs/remotes/``."""
    step = _guard_step()
    # Trailing `;` / `\` belong to the shell, not the refname.
    targets = [
        ref.rstrip(";\\")
        for ref in re.findall(r"--is-ancestor\s+\"\$HEAD\"\s+(\S+)", step)
    ]
    assert targets, f"no --is-ancestor comparisons found in:\n{step}"
    assert set(targets) == {
        "refs/remotes/origin/main",
        "refs/remotes/origin/dev",
    }, f"unqualified rev name is shadowable by a tag: {targets}"


def test_fetch_does_not_import_tags_into_the_comparison() -> None:
    """The guard's own fetch must not repopulate ``refs/tags/*``."""
    step = _guard_step()
    assert "--no-tags" in step
    assert "+refs/heads/main:refs/remotes/origin/main" in step
    assert "+refs/heads/dev:refs/remotes/origin/dev" in step


def test_guard_fails_closed() -> None:
    step = _guard_step()
    assert "set -euo pipefail" in step
    assert "exit 1" in step
    assert "continue-on-error" not in step
    assert "|| true" not in step
