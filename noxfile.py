"""
Nox automation for fmp-data
───────────────────────────
Matrix:
  • tests  : Python 3.10-3.13 × (core | langchain | mcp extra)
  • lint   : ruff (style)
  • typecheck : mypy
  • security  : bandit
  • docs   : mkdocs build

Poetry is installed in every session; we use *poetry install* directly
(no poetry-plugin-export) for maximum simplicity.
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
def _install(session: Session, *, extras: str | None = None) -> None:
    """Install project with test dependencies."""
    session.install("poetry")  # put Poetry in venv

    # Base install
    cmd = ["poetry", "install", "--no-interaction"]
    if extras:
        cmd += ["--extras", extras]
    session.run(*cmd, external=True)

    # Install test dependencies directly
    session.install(
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "freezegun",
        "responses",
        "vcrpy",
        "coverage",
    )


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: Session, extra: str | None) -> None:
    _install(session, extras=extra)

    # Run different test sets based on extra
    if extra == "mcp":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: nox.Session) -> None:
    _install(session, extras="langchain")
    session.run("pytest", "-q")


# ── MCP-specific test session ───────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _install(session, extras="mcp")
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    _install(session)
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    _install(session)
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    _install(session)
    session.run("bandit", "-r", "fmp_data", "-ll")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    _install(session, extras="langchain")  # test+langchain
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_mcp(session: Session) -> None:
    """Run mypy type checking with MCP extras."""
    _install(session, extras="mcp")
    session.run("mypy", "fmp_data")


# ─────────────── Docs build (MkDocs) ────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: Session) -> None:
    _install(session)
    session.install("mkdocs", "mkdocs-material", "mkdocstrings-python")
    session.run("mkdocs", "build", "--strict")
