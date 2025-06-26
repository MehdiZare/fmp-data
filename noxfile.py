"""
Nox automation for fmp-data
──────────────────────────
Runs:
  • test matrix (core | langchain) × Python 3.10-3.13
  • style, type and security checks
  • docs build (MkDocs)   →  site/ directory
The sessions auto-switch to `uv` for speed; they fall back to `poetry install`
if uv isn’t present.
"""

import shutil
import tempfile

import nox

PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
EXTRAS = [None, "langchain"]
EXTRA_IDS = ["core", "lang"]  # list, not callable


def _install(
    session: nox.Session, *, group: str | None = None, extras: str | None = None
) -> None:
    """
    Install project with Poetry; prefer uv if available.
    """
    use_uv = shutil.which("uv") is not None

    if use_uv:
        # export lockfile subset → uv pip install
        with tempfile.NamedTemporaryFile() as reqs:
            export_cmd = [
                "poetry",
                "export",
                "--without-hashes",
                "--format=requirements.txt",
            ]
            if group:
                export_cmd += ["--with", group]
            if extras:
                export_cmd += ["--extras", extras]
            export_cmd += ["--output", reqs.name]
            session.run(*export_cmd, external=True, silent=True)
            session.run("uv", "pip", "install", "-r", reqs.name, external=True)
    else:
        base_cmd = ["poetry", "install", "--sync", "--no-interaction"]
        if group:
            base_cmd += ["--with", group]
        if extras:
            base_cmd += ["--extras", extras]
        session.run(*base_cmd, external=True)


# ───────────────────────── Test matrix ──────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: nox.Session, extra: str | None) -> None:
    """PyTest for every Python + extras combo."""
    _install(session, group="dev", extras=extra)
    session.run("pytest", "-q", *session.posargs)


# ───────────────────────────────  STYLE / STATIC  ────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def lint(session: nox.Session) -> None:
    """ruff + isort + black check."""
    _install(session, group="dev")
    session.run("ruff", "check", "fmp_data", "tests")
    session.run("black", "--check", "fmp_data", "tests")
    session.run("isort", "--check-only", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def typecheck(session: nox.Session) -> None:
    """MyPy strict mode."""
    _install(session, group="dev")
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True, tags=["qa"])
def security(session: nox.Session) -> None:
    """Bandit security scan."""
    _install(session, group="dev")
    session.run("bandit", "-r", "fmp_data", "-ll")


# ─────────────────────────────────  DOCS  ────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: nox.Session) -> None:
    """Build MkDocs site into ./site."""
    _install(session, group="docs,dev")
    session.run("mkdocs", "build", "--strict")
