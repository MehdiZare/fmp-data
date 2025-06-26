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

import tempfile

import nox

PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
EXTRAS = [None, "langchain"]  # core + optional stack


def _install(session, group: str | None = None, extras: str | None = None) -> None:
    """
    Fast installer helper.
    * group   – poetry group to include (e.g. 'dev', 'docs')
    * extras  – extras tag (e.g. 'langchain')
    """
    # prefer uv if available (3-4× faster on CI)
    try:
        session.run("uv", "--version", silent=True)
        use_uv = True
    except nox.command.CommandFailed:
        use_uv = False

    base_cmd = ["poetry", "install", "--sync", "--no-interaction"]
    if group:
        base_cmd += ["--with", group]
    if extras:
        base_cmd += ["--extras", extras]

    if use_uv:
        # Export lock-file requirements and feed to uv
        with tempfile.NamedTemporaryFile() as reqs:
            session.run(
                *(
                    "poetry",
                    "export",
                    "--without-hashes",
                    "--format=requirements.txt",
                    f"--with={group}" if group else "",
                    f"--extras={extras}" if extras else "",
                    "--output",
                    reqs.name,
                ),
                external=True,
                silent=True,
            )
            session.run("uv", "pip", "install", "-r", reqs.name, external=True)
    else:
        session.run(*base_cmd, external=True)


# ─────────────────────────────────  TESTS  ───────────────────────────────────
@nox.parametrize("python", PY_VERS)
@nox.parametrize("extra", EXTRAS, ids=lambda e: e or "core")
@nox.session(reuse_venv=True)
def tests(session: nox.Session, python: str, extra: str | None) -> None:
    """Run pytest for given Python + extras combo."""
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
