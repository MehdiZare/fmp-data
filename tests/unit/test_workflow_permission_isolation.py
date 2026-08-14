"""No job holds a publishing credential and repo-write at the same time (#252).

``id-token: write`` mints the OIDC token PyPI/TestPyPI trust to accept an
upload. Any other write scope in the *same* job is reachable by anything that
runs there -- a compromised action, a malicious build dependency, an injected
script step. Keeping the two apart is what makes the publish job's blast
radius "can upload the artifact it was handed" rather than "can upload *and*
rewrite the repository".

``publish-testpypi.yml`` carried ``pull-requests: write`` + ``issues: write``
on the job holding ``id-token: write`` purely to post a PR comment. The
comment now runs in its own job with no OIDC token.

These assertions walk every workflow rather than the one that was wrong, so a
new job cannot quietly reintroduce the combination.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))

# `actions/deploy-pages` mandates `pages: write` + `id-token: write` together;
# the token it mints is a Pages deployment token, not a package-index one, and
# the job is already artifact-only with no checkout. Scoped to the
# `github-pages` environment so the exemption cannot be borrowed by a job that
# publishes somewhere else.
PAGES_DEPLOY_ENVIRONMENT = "github-pages"


def _jobs(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path.name} is not a mapping"
    jobs = loaded.get("jobs") or {}
    assert isinstance(jobs, dict)
    return jobs


def _write_scopes(permissions: Any) -> set[str]:
    """Scopes granted at ``write`` level, ignoring ``contents: read`` etc."""
    if not isinstance(permissions, dict):
        # `permissions: write-all` (or any scalar) is never acceptable on a
        # job we are reasoning about; surface it as every scope at once.
        return {str(permissions)}
    return {scope for scope, level in permissions.items() if level == "write"}


def test_workflows_are_parseable() -> None:
    assert WORKFLOWS, "no workflows found; the glob or path is wrong"
    for path in WORKFLOWS:
        _jobs(path)


def _environment_name(job: dict[str, Any]) -> str | None:
    env = job.get("environment")
    if isinstance(env, dict):
        return str(env.get("name")) if env.get("name") else None
    return str(env) if env else None


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_no_job_mixes_oidc_with_repo_write(path: Path) -> None:
    offenders = []
    for name, job in _jobs(path).items():
        scopes = _write_scopes(job.get("permissions"))
        if "id-token" not in scopes:
            continue
        allowed = {"id-token"}
        if _environment_name(job) == PAGES_DEPLOY_ENVIRONMENT:
            allowed.add("pages")
        extra = scopes - allowed
        if extra:
            offenders.append(f"{name}: id-token + {sorted(extra)}")

    assert not offenders, (
        f"{path.name} grants repo-write alongside the publishing credential: "
        f"{offenders}. Move the write-scoped steps into their own job."
    )


def test_the_testpypi_comment_is_a_separate_job() -> None:
    """Pin the specific split, so it cannot be merged back in.

    The generic check above passes if the comment step is simply deleted;
    this asserts the capability still exists, just somewhere safe.
    """
    jobs = _jobs(REPO_ROOT / ".github" / "workflows" / "publish-testpypi.yml")

    publish = jobs["test-release-publish"]
    comment = jobs["test-release-comment"]

    assert _write_scopes(publish.get("permissions")) == {"id-token"}
    assert "id-token" not in _write_scopes(comment.get("permissions"))
    assert _write_scopes(comment.get("permissions")) == {"pull-requests", "issues"}

    # The comment must still run, and only after a successful publish --
    # otherwise it advertises a version that was never uploaded.
    assert set(comment["needs"]) == {"test-release-build", "test-release-publish"}
    assert any("Comment on PR" in str(s.get("name", "")) for s in comment["steps"])

    # And it must not have quietly kept a copy of the artifact or the token.
    assert "environment" not in comment
    step_uses = " ".join(str(s.get("uses", "")) for s in comment["steps"])
    assert "download-artifact" not in step_uses
