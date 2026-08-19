"""Copy-paste ``json`` fences in MCP setup docs must parse (#357)."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
_FENCE = re.compile(r"```json\n(.*?)```", re.DOTALL)
_DOC_PATHS = (
    ROOT / "examples" / "mcp" / "claude_desktop" / "README.md",
    ROOT / "examples" / "mcp" / "claude_desktop" / "troubleshooting.md",
    ROOT / "examples" / "mcp" / "setup_guide.md",
)


def test_copy_paste_json_fences_parse() -> None:
    """A ``json`` fence is what users paste into Claude Desktop."""
    failures: list[str] = []
    scanned = 0
    for path in _DOC_PATHS:
        relative = path.relative_to(ROOT)
        blocks = _FENCE.findall(path.read_text(encoding="utf-8"))
        assert blocks, f"no json fences in {relative}"
        for index, block in enumerate(blocks, start=1):
            scanned += 1
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                failures.append(f"{relative} block {index}: {exc}")
    assert scanned >= 8
    assert failures == [], "invalid json fences:\n  " + "\n  ".join(failures)
