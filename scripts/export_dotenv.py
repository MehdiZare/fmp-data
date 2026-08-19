#!/usr/bin/env python3
"""Print ``export KEY=value`` lines from a .env file without executing it.

Used by the Makefile so a crafted ``.env`` cannot run as the maintainer
(#252 FMP-SEC-011). Values are ``shlex.quote``-d. Lines that are empty,
comments, or missing ``=`` are ignored. Optional ``export `` prefix is
stripped. No interpolation, no command substitution. Process-hijack keys
(``PATH``, ``LD_PRELOAD``, ``PYTHONPATH``, ``DYLD_*``, …) are dropped.
"""

from __future__ import annotations

from pathlib import Path
import re
import shlex
import sys

_INLINE_COMMENT = re.compile(r"\s+#")
_SINGLE_ESCAPES = {"\\": "\\", "'": "'"}
_DOUBLE_ESCAPES = {
    "\\": "\\",
    "'": "'",
    '"': '"',
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
}

# A trusted .env can still clobber the maintainer shell if we export these.
_BLOCKED_KEYS = frozenset(
    {
        "PATH",
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH",
        "DYLD_FRAMEWORK_PATH",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTHONBREAKPOINT",
        "IFS",
        "PS4",
        "SHELLOPTS",
        "BASH_ENV",
        "ENV",
        "CDPATH",
        "PROMPT_COMMAND",
    }
)


def _quoted_value(raw: str) -> str:
    """Decode a python-dotenv quoted value; ignore text after the closer."""
    quote = raw[0]
    escapes = _SINGLE_ESCAPES if quote == "'" else _DOUBLE_ESCAPES
    decoded: list[str] = []
    index = 1
    while index < len(raw):
        char = raw[index]
        if char == "\\" and index + 1 < len(raw):
            nxt = raw[index + 1]
            decoded.append(escapes.get(nxt, char + nxt))
            index += 2
            continue
        if char == quote:
            return "".join(decoded)
        decoded.append(char)
        index += 1
    return "".join(decoded)


def export_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key or not key.isidentifier():
            continue
        if key in _BLOCKED_KEYS or key.startswith("DYLD_"):
            continue
        value = value.strip()
        if value and value[0] in {"'", '"'}:
            value = _quoted_value(value)
        else:
            value = _INLINE_COMMENT.split(value, maxsplit=1)[0].rstrip()
        lines.append(f"export {key}={shlex.quote(value)}")
    return lines


def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else ".env")
    if not path.is_file():
        return 0
    for line in export_lines(path.read_text(encoding="utf-8")):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
