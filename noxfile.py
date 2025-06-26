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
(no poetry-plugin-export) for maximum simplicity.
"""

import nox

# ─────────────── Matrix definitions ────────────────
PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
EXTRAS = [None, "langchain"]
EXTRA_IDS = ["core", "lang"]  # ids must be a list/tuple (not lambda)


# ─────────────── Helper: install with Poetry ─────────
def _install(session, *, extras: str | None = None) -> None:
    """Install project + *test* group; add extras if requested."""
    session.install("poetry")  # put Poetry in venv
    cmd = ["poetry", "install", "--no-interaction", "--with", "test"]
    if extras:
        cmd += ["--extras", extras]  # install optional stack
    session.run(*cmd, external=True)


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session, extra):
    _install(session, extras=extra)
    session.run("pytest", "-q")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session):
    _install(session)
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session):
    _install(session)
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session):
    _install(session)
    session.run("bandit", "-r", "fmp_data", "-ll")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session):
    _install(session, extras="langchain")  # test+langchain
    session.run("mypy", "fmp_data")


# ─────────────── Docs build (MkDocs) ────────────────


@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session):
    _install(session)
    session.install("mkdocs", "mkdocs-material", "mkdocstrings-python")
    session.run("mkdocs", "build", "--strict")
