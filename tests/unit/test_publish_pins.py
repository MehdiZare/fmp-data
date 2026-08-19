"""Publish jobs install build backends from version floors, not a hashed lock."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
REQUIREMENTS = REPO_ROOT / ".github" / "requirements-build.txt"


def test_requirements_build_uses_version_floors() -> None:
    text = REQUIREMENTS.read_text(encoding="utf-8")
    for package in ("build>=", "hatchling>=", "hatch-vcs>="):
        assert package in text
    assert "==" not in text
    assert "--hash=" not in text


def test_publish_installs_without_require_hashes() -> None:
    offenders: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "requirements-build.txt" in text and "--require-hashes" in text:
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []


_SDIST_ASSERT_WORKFLOWS = (
    "release.yml",
    "publish-testpypi.yml",
    "dev-release.yml",
)

# The 2.7.0 cut failed here: `tar | awk ... exit` under pipefail is
# SIGPIPE (GNU tar exit 2) after a successful build.
_PIPE_AND_EARLY_AWK = "| awk -F': ' '/^Version:/{print $2; exit}'"


def test_sdist_version_assert_does_not_sigpipe_tar() -> None:
    """PKG-INFO must be fully extracted before the Version: line is parsed."""
    for name in _SDIST_ASSERT_WORKFLOWS:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert "tar -xOf" in text, name
        assert _PIPE_AND_EARLY_AWK not in text, name
        assert "PKG_INFO=$(tar -xOf \"$SDIST\" --wildcards '*/PKG-INFO')" in text, name


def test_publish_builds_use_no_isolation() -> None:
    offenders: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if (
                stripped.startswith("python -m build")
                and "--no-isolation" not in stripped
            ):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}:{stripped}")
    assert offenders == []
