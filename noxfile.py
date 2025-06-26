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
def _install(
    session: nox.Session, *, group: str | None = None, extras: str | None = None
) -> None:
    """Install project into this session’s venv via Poetry."""
    session.install("poetry")  # ensure Poetry is available

    cmd = ["poetry", "install", "--sync", "--no-interaction"]
    if group:
        cmd += ["--with", group]
    if extras:
        cmd += ["--extras", extras]
    session.run(*cmd, external=True)


# ─────────────── Test matrix ────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: nox.Session, extra: str | None):
    """Run pytest under every interpreter / extras combo."""
    _install(session, group="dev", extras=extra)
    session.run("pytest", "-q")


# ─────────────── QA sessions (run on 3.12 only) ─────
@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def lint(session):
    _install(session, group="dev")
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def typecheck(session):
    _install(session, group="dev")
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def security(session):
    _install(session, group="dev")
    session.run("bandit", "-r", "fmp_data", "-ll")


# ─────────────── Docs build (MkDocs) ────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session):
    _install(session, group="docs,dev")
    session.run("mkdocs", "build", "--strict")
