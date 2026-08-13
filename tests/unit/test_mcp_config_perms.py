"""Claude config writes must be owner-only (#252 FMP-SEC-006)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from fmp_data.mcp.utils import save_claude_config


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits")
def test_save_claude_config_is_owner_only(tmp_path: Path) -> None:
    target = tmp_path / "claude" / "config.json"
    with patch("fmp_data.mcp.utils.get_claude_config_path", return_value=target):
        backup = save_claude_config({"mcpServers": {}}, backup=False)

    assert backup is None
    assert target.is_file()
    assert stat_mode(target) == 0o600
    assert stat_mode(target.parent) == 0o700


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits")
def test_save_claude_config_backup_is_owner_only(tmp_path: Path) -> None:
    target = tmp_path / "claude" / "config.json"
    target.parent.mkdir()
    target.write_text("{}\n", encoding="utf-8")
    os.chmod(target, 0o644)

    with patch("fmp_data.mcp.utils.get_claude_config_path", return_value=target):
        backup = save_claude_config({"ok": True}, backup=True)

    assert backup is not None and backup.is_file()
    assert stat_mode(target) == 0o600
    assert stat_mode(backup) == 0o600


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777
