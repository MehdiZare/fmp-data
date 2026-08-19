"""The release build job holds no persisted git credentials (#252).

``release.yml``'s build job legitimately needs ``contents: write`` -- it
pushes the release tag and creates the GitHub Release. What it did *not* need
was a repo-write token sitting in ``.git/config`` for the whole job, including
while it installs a PEP 517 frontend and backend and runs a build. Anything in
that dependency tree could read it.

Only one step ever needed remote write: the ``git push origin <tag>``. It now
goes through the API with an explicitly scoped ``GH_TOKEN``, so the checkout
can drop credentials entirely.

Two orderings make that safe, and both are easy to break by tidying:

* the tag is created **locally** before the build, because ``hatch-vcs``
  derives the version from the local tag -- a remote-only tag silently yields
  a ``.devN`` version instead of the release version;
* the remote tag is created as an **annotated** tag object, not just a ref,
  so it matches the local one.

This path cannot be exercised without performing a real release, so these
assertions stand in for that.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASE = REPO_ROOT / ".github" / "workflows" / "release.yml"


def _build_steps() -> list[dict[str, Any]]:
    loaded = yaml.safe_load(RELEASE.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    steps = loaded["jobs"]["build"]["steps"]
    assert isinstance(steps, list)
    return steps


def _step(fragment: str) -> dict[str, Any]:
    matches = [s for s in _build_steps() if fragment in str(s.get("name", ""))]
    assert len(matches) == 1, f"expected one step matching {fragment!r}, got {matches}"
    return matches[0]


def _index(fragment: str) -> int:
    for i, step in enumerate(_build_steps()):
        if fragment in str(step.get("name", "")):
            return i
    raise AssertionError(f"no step matching {fragment!r}")


def test_checkout_does_not_persist_credentials() -> None:
    checkout = _step("Checkout repository")
    with_ = checkout.get("with") or {}
    assert with_.get("persist-credentials") is False
    assert "token" not in with_, (
        "passing `token:` re-persists the credential for the whole job"
    )


def test_only_the_steps_that_need_it_receive_a_token() -> None:
    """A job-level `env: GH_TOKEN` would hand it to the build step too."""
    loaded = yaml.safe_load(RELEASE.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    assert "GH_TOKEN" not in (loaded.get("env") or {})
    build_job = loaded["jobs"]["build"]
    assert "GH_TOKEN" not in (build_job.get("env") or {})

    holders = {
        str(s.get("name")) for s in _build_steps() if "GH_TOKEN" in (s.get("env") or {})
    }
    assert len(holders) == 2, f"unexpected GH_TOKEN holders: {holders}"
    assert any("Push tag" in h for h in holders)
    assert any("Release" in h for h in holders)

    build = _step("Build distribution")
    assert "GH_TOKEN" not in (build.get("env") or {})
    assert "GH_TOKEN" not in (_step("Create local tag").get("env") or {})


def test_tag_is_created_locally_before_the_build() -> None:
    """hatch-vcs reads the *local* tag; a remote-only tag yields `.devN`."""
    assert _index("Create local tag") < _index("Build distribution")
    assert _index("Build distribution") < _index("Push tag")
    assert "git tag -a" in _step("Create local tag")["run"]
    assert "git/tags" not in _step("Create local tag")["run"]


def _code_lines(run: str) -> str:
    """Executable lines only -- comments legitimately mention `git push`."""
    return "\n".join(
        line for line in run.splitlines() if not line.lstrip().startswith("#")
    )


def test_tag_is_pushed_through_the_api_as_an_annotated_tag() -> None:
    run = _step("Push tag")["run"]

    # No git remote auth exists any more, so this must not come back.
    assert "git push" not in _code_lines(run)

    # Two calls: the tag *object* then the ref. Creating only the ref would
    # leave a lightweight tag where the local one is annotated.
    assert "git/tags" in run
    assert "git/refs" in run
    assert "-f type=commit" in run


def test_the_push_is_verified_before_downstream_steps_rely_on_it() -> None:
    assert "git/ref/tags/" in _step("Push tag")["run"]


@pytest.mark.parametrize("fragment", ["Push tag", "Create GitHub Release"])
def test_token_scoped_steps_still_fail_closed(fragment: str) -> None:
    run = _step(fragment)["run"]
    assert "set -euo pipefail" in run
    assert "|| true" not in run
