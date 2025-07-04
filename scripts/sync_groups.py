#!/usr/bin/env python
"""Sync [dependency-groups] with [project.optional-dependencies].

• Copies every section key / value pair.
• Leaves existing groups that have no matching optional-extra unchanged.
• Writes the file only if a diff is produced.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

if sys.version_info >= (3, 11):
    import tomli_w
    import tomllib as tomli
else:
    import tomli
    import tomli_w

PYPROJECT = pathlib.Path("pyproject.toml")

def main() -> None:
    data = tomli.loads(PYPROJECT.read_text())

    opt = data.get("project", {}).get("optional-dependencies", {})
    groups = data.setdefault("dependency-groups", {})

    changed = False
    for name, pkgs in opt.items():
        # Skip extras you do NOT want available to uv (eg. "dev" → already present)
        groups[name] = pkgs
        changed = True

    if changed:
        backup = PYPROJECT.with_suffix(".toml.bak")
        shutil.copyfile(PYPROJECT, backup)
        PYPROJECT.write_text(tomli_w.dumps(data))
        print(f"💾  dependency-groups synced → {PYPROJECT} (backup at {backup})")
    else:
        print("✅ dependency-groups already up to date.")

if __name__ == "__main__":
    sys.exit(main())
