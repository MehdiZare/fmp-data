"""Publish jobs pin hatchling/hatch-vcs and build without PEP 517 isolation."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
REQUIREMENTS = REPO_ROOT / ".github" / "requirements-build.txt"


def test_requirements_build_pins_backend_with_hashes() -> None:
    text = REQUIREMENTS.read_text(encoding="utf-8")
    for package in ("build==", "hatchling==", "hatch-vcs=="):
        assert package in text
    assert "--hash=sha256:" in text


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
