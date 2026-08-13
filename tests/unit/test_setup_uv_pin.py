"""setup-uv is SHA-pinned at v10 and asks for the latest uv."""

from __future__ import annotations

from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"
PIN = "ae62891fec2bb8e7d6c99fc78c9fec3a63790f8d"


def test_setup_uv_is_v10_and_tracks_latest_uv() -> None:
    seen = 0
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "astral-sh/setup-uv@" not in text:
            continue
        seen += 1
        for line in text.splitlines():
            if "astral-sh/setup-uv@" not in line:
                continue
            assert PIN in line
            assert "v9.0.0" not in line
        assert "version: latest" in text
    assert seen >= 1
