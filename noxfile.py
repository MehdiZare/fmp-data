"""
Nox configuration for *fmp-data*

▪ test matrix      : 3.10 ─ 3.12 (3.13 when available)
▪ optional groups  : dev, lint, typecheck, security, langchain, mcp-server …
▪ package manager  : uv (fast resolver / installer)

Run "nox -s tests-3.12(mcp-server)" for a single combo, or just "nox" to
execute every default session.

Author: Mehdi Zare
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import os
from pathlib import Path
import sys

import nox
from nox.sessions import Session

# --------------------------------------------------------------------------- #
#  Globals                                                                    #
# --------------------------------------------------------------------------- #

# Python interpreters used across sessions
# Use 3.12 as default for CI compatibility, 3.13 when available locally
if sys.version_info >= (3, 13) or os.getenv("CI") != "true":
    PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12", "3.13")
    DEFAULT_PYTHON = "3.13"
else:
    PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12")
    DEFAULT_PYTHON = "3.12"

# Feature-flag groups that map to [project.optional-dependencies]
FEATURE_GROUPS: Sequence[str | None] = (
    None,                # base             → install just the core package
    "langchain",         # extras = dev+langchain
    "mcp-server",
)
FEATURE_IDS: Sequence[str] = (
    "core",
    "langchain",
    "mcp-server",
)

REPO_ROOT = Path(__file__).parent
PACKAGE_NAME = "fmp_data"

# --------------------------------------------------------------------------- #
#  Helper: sync deps with uv                                                  #
# --------------------------------------------------------------------------- #


def _sync_with_uv(session: Session, extras: Iterable[str] = ()) -> None:
    """
    Synchronize the session's virtualenv with *uv*.

    Each extra becomes "--group <extra>".
    """
    if os.getenv("NOX_USE_UV", "1") != "1":
        session.install("-e", ".", *extras)
        return

    # build argument list:  ["uv", "sync", "--group", "dev", "--group", "mcp-server"]
    args: list[str] = ["uv", "sync"]
    for grp in extras:
        args.extend(["--group", grp])

    session.run(*args, external=True)


# --------------------------------------------------------------------------- #
#  Sessions                                                                   #
# --------------------------------------------------------------------------- #

@nox.session(python=PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """
    Run *pytest* with coverage.

    Coverage XML is emitted for Codecov upload when ``python == DEFAULT_PYTHON``.
    """
    extras: list[str] = ["dev"]  # dev extra contains pytest + pytest-cov
    if feature_group:
        extras.append(feature_group)

    _sync_with_uv(session, extras)

    pytest_args = [
        "-q",
        "--cov", PACKAGE_NAME,
        "--cov-report=xml",
        "--cov-report=term-missing",
    ]

    if feature_group == "mcp-server":
        session.run(
            "pytest",
            *pytest_args,
            "tests/unit/test_mcp.py",
            "-m",
            "not integration",
        )
    else:
        session.run("pytest", *pytest_args)

    # Save artefacts so GitHub-Actions can upload them if desired
    if session.python == DEFAULT_PYTHON:
        session.log(f"Copying coverage.xml for CI artifact (Python {DEFAULT_PYTHON})")
        session.run(
            "cp", "coverage.xml", str(REPO_ROOT / f"coverage.{session.python}.xml")
        )


@nox.session(python=DEFAULT_PYTHON, tags=["lint"])
def lint(session: Session) -> None:
    """Static style checks (ruff, black - no code execution)."""
    _sync_with_uv(session, extras=["dev"])
    session.run("ruff", "check", ".", "--output-format=concise")
    session.run("black", "--check", ".")


@nox.session(python=DEFAULT_PYTHON, tags=["typecheck"])
def typecheck(session: Session) -> None:
    """Run *mypy* with strict settings."""
    _sync_with_uv(session, extras=["dev"])
    session.run("mypy", PACKAGE_NAME)


@nox.session(python=DEFAULT_PYTHON, tags=["security"])
def security(session: Session) -> None:
    """Check dependencies for known CVEs."""
    _sync_with_uv(session, extras=["dev"])
    session.run("pip-audit")


@nox.session(python=DEFAULT_PYTHON, tags=["smoke"])
def smoke(session: Session) -> None:
    """
    Quick import test - useful in release pipelines to ensure fresh wheels
    start up without heavy dependencies.
    """
    _sync_with_uv(session)
    session.run(
        "python", "-c", f"import {PACKAGE_NAME}; print({PACKAGE_NAME}.__version__)"
    )
