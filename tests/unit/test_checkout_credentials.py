"""Checkouts do not leave repo-write credentials lying in the workspace (#252).

``actions/checkout`` writes the job's token into ``.git/config`` unless told
not to, where every later step can read it -- including dependency installs,
build backends and third-party actions. Only ``sync-main-to-dev`` still
pushes, so every other checkout drops the credential.

The remaining exception is asserted by name rather than skipped, so adding
another one is a deliberate edit to this list and not an accident.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))

# job name -> why this one keeps its credential.
ALLOWED_TO_PERSIST = {
    "sync-main-to-dev": "really runs `git push origin HEAD:refs/heads/...`",
}


def _checkout_steps() -> list[tuple[str, str, dict[str, Any]]]:
    """(workflow, job, step) for every actions/checkout in the repo."""
    found = []
    for path in WORKFLOWS:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict), f"{path.name} is not a mapping"
        for job_name, job in (loaded.get("jobs") or {}).items():
            for step in job.get("steps") or []:
                if "actions/checkout" in str(step.get("uses", "")):
                    found.append((path.name, job_name, step))
    return found


def test_there_are_checkouts_to_check() -> None:
    """Guard against the glob silently matching nothing."""
    assert len(_checkout_steps()) >= 10


def test_only_the_jobs_that_push_persist_credentials() -> None:
    offenders = []
    for workflow, job, step in _checkout_steps():
        with_ = step.get("with") or {}
        persists = with_.get("persist-credentials") is not False
        if persists and job not in ALLOWED_TO_PERSIST:
            offenders.append(f"{workflow}:{job}")

    assert not offenders, (
        f"these checkouts leave a repo-write token in .git/config for the "
        f"whole job: {offenders}. Add `persist-credentials: false`, or add the "
        f"job to ALLOWED_TO_PERSIST with a reason if it genuinely pushes."
    )


@pytest.mark.parametrize("job", sorted(ALLOWED_TO_PERSIST))
def test_documented_exceptions_still_exist(job: str) -> None:
    """A stale exception would silently widen the allowlist."""
    assert any(j == job for _, j, _ in _checkout_steps()), (
        f"{job!r} is listed as a credential-persisting exception but no such "
        f"checkout exists any more; drop it from ALLOWED_TO_PERSIST"
    )


def test_read_only_checkouts_do_not_pass_an_explicit_token() -> None:
    """`token:` re-persists the credential even with persist-credentials off."""
    offenders = [
        f"{workflow}:{job}"
        for workflow, job, step in _checkout_steps()
        if "token" in (step.get("with") or {}) and job not in ALLOWED_TO_PERSIST
    ]
    assert not offenders, offenders


def test_claude_code_action_workflows_are_absent() -> None:
    """#359: do not restore the unpinned marketplace review or @claude agent."""
    workflows = REPO_ROOT / ".github" / "workflows"
    assert not (workflows / "claude.yml").exists()
    assert not (workflows / "claude-code-review.yml").exists()
    remaining = "\n".join(path.read_text(encoding="utf-8") for path in WORKFLOWS)
    assert "anthropics/claude-code-action" not in remaining
    assert "CLAUDE_CODE_OAUTH_TOKEN" not in remaining
