"""
Nox automation for fmp-data
───────────────────────────
Matrix:
  • tests  : Python 3.10-3.13 × (core | langchain | mcp extra)
  • lint   : ruff (style)
  • typecheck : mypy
  • security  : bandit
  • docs   : mkdocs build

Uses poetry dependency groups for cleaner management.
"""

import nox
from nox import Session

# Global default: always try to re-use when possible
nox.options.reuse_venv = "yes"

# ─────────────── Matrix definitions ────────────────
PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
EXTRAS = [None, "langchain", "mcp-server"]
EXTRA_IDS = ["core", "lang", "mcp-server"]


# ─────────────── Helper: install with Poetry ─────────
def _install(
    session: Session, *, extras: str | None = None, groups: list[str] | None = None
) -> None:
    """Install project with specified extras and dependency groups."""
    session.install("poetry")

    cmd = ["poetry", "install", "--no-interaction"]

    # Add dependency groups
    if groups:
        for group in groups:
            cmd.extend(["--with", group])

    # Add extras
    if extras:
        cmd.extend(["--extras", extras])

    session.run(*cmd, external=True)


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: Session, extra: str | None) -> None:
    """Run tests for given Python version and optional extras."""
    _install(session, extras=extra, groups=["dev"])

    # Run different test sets based on extra
    if extra == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all extras."""
    _install(session, extras="langchain", groups=["dev"])
    session.run("pytest", "-q")


# ── MCP-specific test session ───────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _install(session, extras="mcp-server", groups=["dev"])
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _install(session, groups=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _install(session, groups=["dev"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _install(session, groups=["dev"])
    session.run("bandit", "-r", "fmp_data", "-ll")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain extras."""
    _install(session, extras="langchain", groups=["dev"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_mcp(session: Session) -> None:
    """Run mypy type checking with MCP extras."""
    _install(session, extras="mcp-server", groups=["dev"])
    session.run("mypy", "fmp_data")


# ─────────────── Docs build (MkDocs) ────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with MkDocs."""
    _install(session, groups=["docs"])
    session.run("mkdocs", "build", "--strict")
