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


def _loaded(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path.name} is not a mapping"
    return loaded


def _jobs(path: Path) -> dict[str, Any]:
    jobs = _loaded(path).get("jobs") or {}
    assert isinstance(jobs, dict)
    return jobs


def _effective_permissions(loaded: dict[str, Any], job: dict[str, Any]) -> Any:
    """Job-level permissions replace workflow-level ones; they do not merge."""
    if "permissions" in job:
        return job["permissions"]
    return loaded.get("permissions")


def _effective_env(
    loaded: dict[str, Any],
    job: dict[str, Any],
    step: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Workflow, then job, then step — later mappings win."""
    env: dict[str, Any] = {}
    for mapping in (loaded.get("env"), job.get("env"), (step or {}).get("env")):
        if isinstance(mapping, dict):
            env.update(mapping)
    return env


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
    loaded = _loaded(path)
    for name, job in _jobs(path).items():
        scopes = _write_scopes(_effective_permissions(loaded, job))
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


def test_codecov_token_is_not_in_a_job_that_runs_pr_code() -> None:
    """The upload token must not share a job with PR-supplied code (#252).

    `nox -s coverage_local` runs the PR branch's own noxfile and test suite.
    Holding an upload token in that same job hands it to whatever that code
    decides to do. Split the same way the release path splits build from
    publish: produce an artifact with no secrets, upload it from a job that
    only downloads.
    """
    path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    loaded = _loaded(path)
    jobs = _jobs(path)

    coverage = jobs["coverage"]
    coverage_env = _effective_env(loaded, coverage)
    for step in coverage.get("steps") or []:
        if isinstance(step, dict):
            coverage_env = {**coverage_env, **_effective_env(loaded, coverage, step)}
    assert "CODECOV_TOKEN" not in coverage_env, (
        "the coverage job executes PR-supplied test code; it must not hold "
        "the upload token"
    )
    assert "CODECOV_TOKEN" not in yaml.dump(coverage), (
        "the coverage job executes PR-supplied test code; it must not hold "
        "the upload token"
    )
    assert "nox" in yaml.dump(coverage), (
        "guard is vacuous if this job stops running tests"
    )

    upload = jobs["coverage-upload"]
    upload_env = _effective_env(loaded, upload)
    for step in upload.get("steps") or []:
        if isinstance(step, dict):
            upload_env = {**upload_env, **_effective_env(loaded, upload, step)}
    assert "CODECOV_TOKEN" in upload_env or "CODECOV_TOKEN" in yaml.dump(upload)
    assert "nox" not in yaml.dump(upload), (
        "the upload job must not execute repository code"
    )
    assert upload["needs"] == "coverage" or "coverage" in upload["needs"]
    assert _write_scopes(_effective_permissions(loaded, upload)) == set()


PUBLISH_WORKFLOWS = ("release.yml", "dev-release.yml", "publish-testpypi.yml")


@pytest.mark.parametrize("name", PUBLISH_WORKFLOWS)
def test_publish_workflows_serialize(name: str) -> None:
    """Concurrent publishes race on version, tag and PR comment (#252).

    Two pushes to the same PR both build and publish; the slower run's
    comment can overwrite the newer one, advertising a stale version -- the
    exact invariant #204 exists to protect.

    `cancel-in-progress` must stay false: making the second run wait is
    strictly better than aborting one mid-upload.
    """
    loaded = yaml.safe_load((REPO_ROOT / ".github" / "workflows" / name).read_text())
    concurrency = loaded.get("concurrency")
    assert concurrency, f"{name} has no concurrency group; publishes can race"
    assert concurrency.get("cancel-in-progress") is False, (
        f"{name} may cancel a run mid-upload"
    )
