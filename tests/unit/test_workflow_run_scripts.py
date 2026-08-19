"""Compile every GitHub Actions ``run:`` block with ``bash -n`` (#363).

YAML ``run: |`` strips the block's common indent, then bash parses what
remains. A here-doc terminator that is still indented after that strip is
not recognized, so bash eats the rest of the script. Sync-Main-to-Dev hit
that after the 2.7.0 squash (#363): the job died at
``here-document at line 115 delimited by end-of-file`` and never pushed
the ``-s ours`` merge.

This module is both a pytest file and a CLI (``python3`` this file) so
the ``Actions shell checks`` job can run it without the test extra.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# <<EOF, <<'EOF', <<"EOF", <<-EOF (tab-stripping). Token is group 2/3/4.
_HEREDOC_START = re.compile(r"""<<(-)?(?:'([^']+)'|"([^"]+)"|\\?(\w+))\s*$""")


def _workflow_paths() -> list[Path]:
    paths = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    assert paths, f"no workflow files under {WORKFLOWS}"
    return paths


def _iter_run_scripts(node: object, prefix: str = "") -> Iterator[tuple[str, str]]:
    """Yield ``(label, script)`` for every mapping that has a string ``run``."""
    if isinstance(node, dict):
        run = node.get("run")
        if isinstance(run, str):
            name = str(node.get("name") or "run")
            label = f"{prefix}:{name}" if prefix else name
            yield label, run
        for key, value in node.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from _iter_run_scripts(value, next_prefix)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _iter_run_scripts(item, f"{prefix}[{index}]")


def _load_run_scripts(path: Path) -> list[tuple[str, str]]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(_iter_run_scripts(loaded, prefix=path.name))


def _heredoc_problems(script: str) -> list[str]:
    """Return problems for here-docs that bash would not close at column 0."""
    problems: list[str] = []
    lines = script.splitlines()
    index = 0
    while index < len(lines):
        match = _HEREDOC_START.search(lines[index])
        if match is None:
            index += 1
            continue
        strip_tabs, single, double, bare = match.groups()
        token = single or double or bare
        assert token is not None
        index += 1
        found = False
        while index < len(lines):
            raw = lines[index]
            # `<<-` strips leading tabs only. `<<` requires column 0.
            # Spaces in front of the token survive YAML strip and must
            # be flagged; matching only the exact line made the indented
            # diagnostic dead and reported those as "unclosed" instead.
            if strip_tabs and raw.lstrip("\t") == token:
                found = True
                break
            if raw == token:
                found = True
                break
            if raw.lstrip() == token:
                problems.append(
                    f"indented here-doc terminator {token!r} "
                    f"(survives YAML strip; bash will not close it)"
                )
                found = True
                break
            index += 1
        if not found:
            problems.append(f"unclosed here-doc {token!r}")
        index += 1
    return problems


# GitHub evaluates ${{ }} before bash sees the script. Replace them so
# bash -n is checking the post-expression source, not the template.
_GH_EXPR = re.compile(r"\$\{\{.*?\}\}", re.DOTALL)


def _for_bash(script: str) -> str:
    return _GH_EXPR.sub("GH_EXPR", script)


def _bash_n(script: str) -> subprocess.CompletedProcess[str]:
    rendered = _for_bash(script)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".sh",
        delete=False,
    ) as handle:
        handle.write(rendered)
        if rendered and not rendered.endswith("\n"):
            handle.write("\n")
        temp_path = handle.name
    try:
        return subprocess.run(  # noqa: S603
            ["bash", "-n", temp_path],  # noqa: S607
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        Path(temp_path).unlink(missing_ok=True)


def _collect_failures() -> list[str]:
    failures: list[str] = []
    for path in _workflow_paths():
        for label, script in _load_run_scripts(path):
            for problem in _heredoc_problems(script):
                failures.append(f"{label}: {problem}")
            compiled = _bash_n(script)
            if compiled.returncode != 0:
                detail = (compiled.stderr or compiled.stdout).strip()
                failures.append(f"{label}: bash -n failed\n{detail}")
    return failures


def test_every_workflow_run_block_compiles() -> None:
    """Every workflow ``run:`` block must be valid bash after YAML strip."""
    failures = _collect_failures()
    assert failures == [], "workflow run: blocks failed bash -n:\n" + "\n".join(
        failures
    )


def test_sync_main_to_dev_is_among_the_compiled_scripts() -> None:
    """A missing Sync-Main-to-Dev file would make the #363 pin vacuous."""
    labels = [
        label for path in _workflow_paths() for label, _ in _load_run_scripts(path)
    ]
    matching = [label for label in labels if "sync-main-to-dev" in label]
    assert matching, "sync-main-to-dev.yml produced no run: blocks"


def test_indented_heredoc_terminator_is_flagged() -> None:
    """Spaces in front of EOF survive YAML strip; bash never closes the doc."""
    script = "cat <<'EOF'\nhello\n  EOF\n"
    problems = _heredoc_problems(script)
    assert problems, "indented terminator must be reported"
    assert any("indented here-doc terminator" in item for item in problems)


def test_column0_heredoc_terminator_is_clean() -> None:
    script = "cat <<'EOF'\nhello\nEOF\n"
    assert _heredoc_problems(script) == []


def test_tab_stripped_dash_heredoc_is_clean() -> None:
    script = "cat <<-EOF\nhello\n\tEOF\n"
    assert _heredoc_problems(script) == []


def test_unclosed_heredoc_is_flagged() -> None:
    script = "cat <<'EOF'\nhello\n"
    problems = _heredoc_problems(script)
    assert problems
    assert any("unclosed here-doc" in item for item in problems)


def main() -> int:
    failures = _collect_failures()
    if failures:
        print("workflow run: blocks failed bash -n:", file=sys.stderr)
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print(f"ok: bash -n passed for run: blocks in {len(_workflow_paths())} workflows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
