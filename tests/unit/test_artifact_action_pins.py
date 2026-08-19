"""Upload and download artifact actions stay internally consistent.

``actions/upload-artifact`` v7 and ``actions/download-artifact`` v8 are
the paired majors for the same artifact backend. Dependabot opens one PR
per action, so a split bump can land upload v7 next to download v4.
"""

from __future__ import annotations

from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def _pins(action: str) -> list[str]:
    pins: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("uses:"):
                continue
            ref = stripped.split("uses:", 1)[1].strip()
            name, _, pin = ref.partition("@")
            if name == action:
                pins.append(f"{path.name}:{pin.split()[0]}")
    return pins


def test_upload_artifact_pins_are_identical() -> None:
    pins = [entry.split(":", 1)[1] for entry in _pins("actions/upload-artifact")]
    assert pins, "expected at least one upload-artifact pin"
    assert len(set(pins)) == 1, f"upload-artifact pins must match: {pins}"
    assert all(len(pin) == 40 for pin in pins)


def test_download_artifact_pins_are_identical() -> None:
    pins = [entry.split(":", 1)[1] for entry in _pins("actions/download-artifact")]
    assert pins, "expected at least one download-artifact pin"
    assert len(set(pins)) == 1, f"download-artifact pins must match: {pins}"
    assert all(len(pin) == 40 for pin in pins)


def test_upload_and_download_artifact_are_both_present() -> None:
    """A release workflow must not bump only one half of the pair."""
    assert _pins("actions/upload-artifact")
    assert _pins("actions/download-artifact")
