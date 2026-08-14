"""CI actually runs ruff, mypy and bandit/pip-audit (#252).

``ci.yml`` used to invoke the gates as::

    uv tool run nox -s lint -s typecheck -s security

``nox``'s ``-s`` is an ordinary *store* argument taking ``nargs="*"``, not an
``append``. Repeating the flag therefore does not accumulate -- the last
occurrence wins outright, so that line selected ``security`` and nothing else.
``ruff`` and ``mypy`` had no CI enforcement at all, and ``bandit``/``pip-audit``
survived only by being last in the list.

That is the #283 finding one layer up: there, ``bandit`` was configured but
never wired to a CI job; here the job exists and *looks* right, so grepping
``ci.yml`` for ``"lint"`` passes while the session never runs. These tests
reproduce nox's own flag semantics instead of matching substrings, and
``test_repeated_s_flag_form_is_detected_as_broken`` pins that reproduction
against the real known-bad line so the check cannot rot into a tautology.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"

REQUIRED_GATES = {"lint", "typecheck", "security"}


def _ci() -> dict[str, Any]:
    loaded = yaml.safe_load(CI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _quality_gate_step() -> dict[str, Any]:
    steps = _ci()["jobs"]["tests"]["steps"]
    matches = [s for s in steps if "Quality Gates" in str(s.get("name", ""))]
    assert len(matches) == 1, f"expected exactly one Quality Gates step, got {matches}"
    step = matches[0]
    assert isinstance(step, dict)
    return step


def _sessions_nox_would_select(run_block: str) -> set[str]:
    """Sessions nox actually selects, per nox's own argument semantics.

    Mirrors ``nox``'s parser: ``-s``/``--sessions``/``--session``/``-e`` take
    ``nargs="*"`` and *store* (not append), so a repeated flag discards every
    earlier occurrence. Anything relying on repetition silently narrows.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sessions", "--session", "-e", nargs="*", default=[])

    selected: set[str] = set()
    for line in run_block.splitlines():
        line = line.strip()
        if line.startswith("#") or "nox" not in line:
            continue
        tokens = shlex.split(line, comments=True)
        if "nox" not in tokens:
            continue
        known, _ = parser.parse_known_args(tokens[tokens.index("nox") + 1 :])
        selected.update(known.sessions or [])
    return selected


def test_ci_selects_every_quality_gate() -> None:
    selected = _sessions_nox_would_select(_quality_gate_step()["run"])
    missing = REQUIRED_GATES - selected
    assert not missing, (
        f"ci.yml Quality Gates selects {sorted(selected)}; "
        f"nox would never run {sorted(missing)}"
    )


def test_repeated_s_flag_form_is_detected_as_broken() -> None:
    """The parser above must actually catch the historical regression.

    Without this, a mimic that quietly accumulated flags would report the
    broken line as healthy and ``test_ci_selects_every_quality_gate`` would
    pass on exactly the config it exists to reject.
    """
    broken = _sessions_nox_would_select(
        "uv tool run nox -s lint -s typecheck -s security"
    )
    assert broken == {"security"}, (
        f"expected the repeated -s form to collapse to just security, got {broken}"
    )

    healthy = _sessions_nox_would_select("uv tool run nox -s lint typecheck security")
    assert healthy == REQUIRED_GATES


def test_quality_gate_condition_matches_a_real_matrix_entry() -> None:
    """A gate pinned to a Python version absent from the matrix never runs.

    ``if: matrix.python == '3.14'`` is silent when 3.14 is dropped from the
    matrix: the step is skipped, the job still reports success, and the gate
    disappears without anything going red.
    """
    step = _quality_gate_step()
    condition = str(step.get("if", ""))
    assert condition, "Quality Gates step has no `if:`; expected a matrix pin"

    matrix = _ci()["jobs"]["tests"]["strategy"]["matrix"]["python"]
    versions = {str(v) for v in matrix}
    assert any(f"'{v}'" in condition or f'"{v}"' in condition for v in versions), (
        f"Quality Gates `if:` ({condition!r}) names no version in the matrix "
        f"{sorted(versions)}; the step would silently never run"
    )


def test_gates_are_not_soft_failed() -> None:
    """``continue-on-error`` / trailing ``|| true`` would make the gate cosmetic."""
    step = _quality_gate_step()
    assert step.get("continue-on-error") in (None, False)
    assert "|| true" not in step["run"]
    assert "|| :" not in step["run"]
