#!/usr/bin/env python3
"""Build GitHub Release notes from a Keep-a-Changelog version section (#370).

The published GitHub Release used to be the squash-commit stub that
``release.yml`` generated from ``git log``. That body is not
``CHANGELOG.md``. This script extracts ``## [X.Y.Z]`` (minus the heading
and minus Unreleased / other versions) and wraps it with the install /
docs footer the Release page already carried.

Stdlib only: do not import ``fmp_data``. The release job fails closed
on a missing or empty section *before* it creates or pushes the tag.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

_VERSION_HEADING = re.compile(r"^## \[([^\]]+)\](?:\s+-.*)?\s*$")
# Split only on dated/undated Keep-a-Changelog version headings so a
# non-version ``## `` inside a section stays in that section's body.
_VERSION_CHUNK_START = re.compile(r"(?=^## \[[^\]]+\](?:\s+-.*)?\s*$)", re.M)


def normalize_version(version: str) -> str:
    """Strip a leading ``v`` so ``v2.7.0`` and ``2.7.0`` match the heading."""
    return version[1:] if version.startswith("v") else version


def extract_section(text: str, version: str) -> str:
    """Return the body of ``## [version]`` (no heading).

    Raises:
        ValueError: the heading is missing, or the section has no body.
    """
    wanted = normalize_version(version)
    chunks = _VERSION_CHUNK_START.split(text)
    for chunk in chunks:
        lines = chunk.splitlines()
        if not lines:
            continue
        match = _VERSION_HEADING.match(lines[0].strip())
        if match is None or match.group(1) != wanted:
            continue
        body = "\n".join(lines[1:]).strip()
        if not body:
            raise ValueError(f"CHANGELOG section ## [{wanted}] is empty")
        return body
    raise ValueError(f"CHANGELOG has no ## [{wanted}] section")


def render_github_release(*, tag: str, version: str, body: str) -> str:
    """Wrap a changelog section with the GitHub Release title and footer."""
    number = normalize_version(version)
    release_tag = tag if tag.startswith("v") else f"v{tag}"
    return "\n".join(
        (
            f"## 🎉 Release {release_tag}",
            "",
            body,
            "",
            "### 📦 Installation",
            "```bash",
            f"pip install fmp-data=={number}",
            "```",
            "",
            "### 🔗 Links",
            f"- [PyPI Package](https://pypi.org/project/fmp-data/{number}/)",
            "- [Documentation](https://mehdizare.github.io/fmp-data/)",
            "",
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        help="Path to CHANGELOG.md (default: ./CHANGELOG.md)",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version to extract, with or without a leading v",
    )
    parser.add_argument(
        "--tag",
        default="",
        help="Git tag for the Release title (default: v + version)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write notes here. Default: stdout",
    )
    args = parser.parse_args(argv)

    try:
        text = args.changelog.read_text(encoding="utf-8")
        body = extract_section(text, args.version)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    tag = args.tag or f"v{normalize_version(args.version)}"
    rendered = render_github_release(tag=tag, version=args.version, body=body)
    if args.out is None:
        sys.stdout.write(rendered)
        return 0
    try:
        args.out.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot write {args.out}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
