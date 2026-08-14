"""Makefile .env loader is data, not shell (#252 FMP-SEC-011)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "export_dotenv.py"
_SPEC = importlib.util.spec_from_file_location("export_dotenv", _SCRIPT)
assert _SPEC and _SPEC.loader
export_dotenv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(export_dotenv)


def test_export_lines_quotes_and_ignores_shell() -> None:
    text = "\n".join(
        [
            "# comment",
            "FMP_API_KEY=plain",
            'FMP_TEST_API_KEY="quoted value"',
            "EVIL=$(touch /tmp/pwned)",
            "export ALSO=ok",
            "not-a-key=nope",
            "",
        ]
    )
    lines = export_dotenv.export_lines(text)
    joined = "\n".join(lines)
    assert "export FMP_API_KEY=plain" in joined
    assert "quoted value" in joined
    assert "export ALSO=ok" in joined
    assert "not-a-key" not in joined
    # $(...) is quoted, not executed
    assert any("EVIL=" in line and "$(touch" in line for line in lines)
    assert all(line.startswith("export ") for line in lines)


def test_export_lines_drops_process_hijack_keys() -> None:
    text = "\n".join(
        [
            "FMP_API_KEY=keep",
            "PATH=/tmp/evil",
            "LD_PRELOAD=/tmp/evil.so",
            "PYTHONPATH=/tmp/evil",
            "DYLD_INSERT_LIBRARIES=/tmp/evil.dylib",
            "DYLD_CUSTOM=also-blocked",
            "IFS=x",
        ]
    )
    lines = export_dotenv.export_lines(text)
    joined = "\n".join(lines)
    assert "export FMP_API_KEY=keep" in joined
    assert "PATH=" not in joined
    assert "LD_PRELOAD=" not in joined
    assert "PYTHONPATH=" not in joined
    assert "DYLD_" not in joined
    assert "IFS=" not in joined
