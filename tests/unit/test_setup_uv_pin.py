"""setup-uv is SHA-pinned at v10 and installs uv 0.12.3."""

from __future__ import annotations

from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


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
            pin = line.split("setup-uv@", 1)[1].split()[0]
            assert len(pin) == 40
            assert all(char in "0123456789abcdef" for char in pin)
            assert "v9.0.0" not in line
            assert "v10.0.0" in line
        assert 'version: "0.12.3"' in text
    assert seen >= 1


def test_pyproject_requires_current_uv() -> None:
    text = (
        Path(__file__)
        .resolve()
        .parents[2]
        .joinpath("pyproject.toml")
        .read_text(encoding="utf-8")
    )
    assert 'required-version = ">=0.12.3"' in text
