"""Release-PR must not open a slot when ``dev`` and ``main`` share a tree (#375).

After a squash onto ``main`` and a history-only Sync-Main-to-Dev merge,
``dev`` is commits-ahead of ``main`` with an identical tree. SHA equality
and ``git rev-list --count`` miss that, so the job used to open an
unlabeled empty ``Release: dev → main`` PR (#374). Squash-merging that
slot recreates the #202 ancestry break for no package change.

These assertions walk the workflow source so the tree-identity check cannot
be deleted without CI failing. Behaviour of ``gh`` itself is not executed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release-pr.yml"

_TREE_DIFF = "git diff --quiet origin/dev origin/main"
_CREATE = "gh pr create --base main --head dev"
_EMPTY_ACTION = "action=empty-slot"
_UNDO_DRAFT = "gh pr ready"


def _loaded() -> dict[str, Any]:
    loaded = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{WORKFLOW.name} is not a mapping"
    return loaded


def _plan_script() -> str:
    jobs = _loaded().get("jobs") or {}
    job = jobs.get("create-release-pr") or {}
    steps = job.get("steps") or []
    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("id") == "plan":
            run = step.get("run")
            assert isinstance(run, str) and run.strip(), "plan step has no run script"
            return run
    raise AssertionError("create-release-pr job has no plan step")


def test_release_pr_workflow_is_parseable() -> None:
    loaded = _loaded()
    assert loaded.get("name") == "Release-PR"
    jobs = loaded.get("jobs") or {}
    assert "create-release-pr" in jobs


def test_trees_match_is_defined_and_used_before_create() -> None:
    script = _plan_script()
    assert "trees_match()" in script
    assert _TREE_DIFF in script
    tree_at = script.index(_TREE_DIFF)
    create_at = script.index(_CREATE)
    assert tree_at < create_at, "tree-identity check must run before gh pr create"


def test_create_path_noops_when_trees_match() -> None:
    """The no-existing-PR path must refuse to open a slot on identical trees."""
    script = _plan_script()
    create_at = script.index(_CREATE)
    prefix = script[:create_at]
    # Existing-PR path + create path each have their own call.
    assert prefix.count("if trees_match; then") == 2
    ahead_at = prefix.index("AHEAD=$(git rev-list --count origin/main..origin/dev)")
    create_path = prefix[ahead_at:]
    skip_at = create_path.index("if trees_match; then")
    then_arm = create_path[skip_at : create_path.index("fi", skip_at)]
    assert 'echo "action=noop"' in then_arm
    assert "exit 0" in then_arm
    assert "gh pr create" not in then_arm
    # Unique vs the SHA / rev-list noops that #374 already bypassed.
    assert "trees match; nothing to release" in then_arm


def test_existing_pr_becomes_empty_slot_when_trees_match() -> None:
    script = _plan_script()
    assert "mark_empty_slot()" in script
    assert _EMPTY_ACTION in script
    assert f'{_UNDO_DRAFT} "$pr_number" --undo' in script or (
        f"{_UNDO_DRAFT} " in script and "--undo" in script
    )
    assert "empty slot — do not merge" in script
    assert "<!-- empty-tree-release-slot -->" in script
    # Restore the checklist when a later push introduces a content delta.
    assert "restore_release_pr()" in script
    assert "Content delta present; restoring release checklist" in script
    # Restore keys off the HTML stamp, not a title glob like "do not merge".
    assert 'contains("<!-- empty-tree-release-slot -->")' in script
    assert '*"do not merge"*' not in script


def test_empty_slot_still_runs_mergeable_check() -> None:
    """CONFLICTING empty slots must still fail closed (#207 / #210)."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "steps.plan.outputs.action == 'empty-slot'" in text
    loaded = _loaded()
    steps = loaded["jobs"]["create-release-pr"]["steps"]
    mergeable = next(step for step in steps if step.get("id") == "mergeable")
    condition = mergeable.get("if")
    assert isinstance(condition, str)
    assert "empty-slot" in condition
    assert "revalidate" in condition
