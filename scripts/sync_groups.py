#!/usr/bin/env python
# /scripts/sync_groups.py
"""Sync [dependency-groups] with [project.optional-dependencies]."""
from __future__ import annotations

import pathlib
import shutil
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    import tomli_w
except ImportError:
    print("Installing tomli-w...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli-w"])
    import tomli_w

PYPROJECT = pathlib.Path("pyproject.toml")


def main() -> None:
    with open(PYPROJECT, "rb") as f:
        data = tomllib.load(f)

    opt = data.get("project", {}).get("optional-dependencies", {})
    groups = data.setdefault("dependency-groups", {})

    changed = False
    for name, pkgs in opt.items():
        if groups.get(name) != pkgs:
            groups[name] = pkgs
            changed = True

    if changed:
        backup = PYPROJECT.with_suffix(".toml.bak")
        shutil.copyfile(PYPROJECT, backup)
        PYPROJECT.write_text(tomli_w.dumps(data))
        print(f"✅ dependency-groups synced → {PYPROJECT}")
    else:
        print("✅ dependency-groups already up to date.")


if __name__ == "__main__":
    main()
