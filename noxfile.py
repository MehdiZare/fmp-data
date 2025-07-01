"""
Nox automation for fmp-data
───────────────────────────
Matrix:
  • tests  : Python 3.10-3.13 × (core | langchain extra)
  • lint   : ruff (style)
  • typecheck : mypy
  • security  : bandit
  • docs   : mkdocs build

Poetry is installed in every session; we use *poetry install* directly
with --extras for PEP 621 optional dependencies.
"""

import nox
from nox import Session

# Global default: always try to re-use when possible
nox.options.reuse_venv = "yes"

# ─────────────── Matrix definitions ────────────────
PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
EXTRAS = [None, "langchain"]
EXTRA_IDS = ["core", "lang"]  # ids must be a list/tuple (not lambda)


# ─────────────── Helper: install with Poetry ─────────
def _install(session: Session, *, extras: str | None = None) -> None:
    """
    Install project with test dependencies.

    Args:
        session: Nox session
        extras: Optional extra dependencies to install
    """
    session.install("poetry")  # put Poetry in venv

    # Build install command - always include test dependencies
    cmd = ["poetry", "install", "--no-interaction", "--extras", "test"]
    if extras:
        cmd.extend(["--extras", extras])

    session.run(*cmd, external=True)


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: Session, extra: str | None) -> None:
    """Run tests for given Python version and optional extras."""
    _install(session, extras=extra)
    session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all extras."""
    _install(session, extras="langchain")
    session.run("pytest", "-q")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _install(session)
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _install(session)
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _install(session)
    session.run("bandit", "-r", "fmp_data", "-ll")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain extras."""
    _install(session, extras="langchain")  # test+langchain
    session.run("mypy", "fmp_data")


# ─────────────── Docs build (MkDocs) ────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with MkDocs."""
    _install(session)
    # Install docs dependencies via extras
    session.run(
        "poetry", "install", "--no-interaction", "--extras", "docs", external=True
    )
    session.run("mkdocs", "build", "--strict")
