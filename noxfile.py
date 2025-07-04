"""
Nox automation for fmp-data — lock-free uv workflow
────────────────────────────────────────────────────
• Installs runtime deps first, then requested extras (dev, mcp-server, etc.).
• No lock files needed; everything resolves from pyproject.toml each session.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

import nox
from nox import Session

# ── Global config ──────────────────────────────────────────────────────────
nox.options.reuse_venv = "yes"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
FEATURE_GROUPS  = [None, "langchain", "mcp-server"]
FEATURE_IDS     = ["core", "lang", "mcp-server"]

LOCAL_PY_VERSIONS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PYTHON_VERSIONS
)
IS_CI = os.getenv("CI", "").lower() in {"true", "1", "yes"}


# ── Dependency installer ───────────────────────────────────────────────────
def _sync_with_uv(session: Session, *, extras: list[str] | None = None) -> None:
    """Install runtime first, then any requested extras."""
    session.run("uv", "sync", external=True)          # runtime
    if extras:
        for grp in extras:
            session.run("uv", "sync", "--group", grp, external=True)
        session.log(f"✓ installed extras: {', '.join(extras)}")


# ── Test matrix ────────────────────────────────────────────────────────────
@nox.session(python=LOCAL_PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    extras = ["dev"]
    if feature_group:
        extras.append(feature_group)

    _sync_with_uv(session, extras=extras)

    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.13")
def smoke(session: Session) -> None:
    """Lightweight import test for bleeding-edge interpreter."""
    _sync_with_uv(session, extras=["dev", "langchain", "mcp-server"])
    session.run("pytest", "-q", "--maxfail=1", "tests/smoke")


# ── QA sessions (run on 3.12) ──────────────────────────────────────────────
@nox.session(python="3.12", tags=["qa"])
def lint(session: Session) -> None:
    _sync_with_uv(session, extras=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", tags=["qa"])
def typecheck(session: Session) -> None:
    _sync_with_uv(session, extras=["dev"])
    session.run(
        "mypy",
        "fmp_data",
        "--exclude", "fmp_data/(lc|mcp)/.*",
        "--show-error-codes",
        "--pretty",
    )


@nox.session(python="3.12", tags=["qa"])
def security(session: Session) -> None:
    _sync_with_uv(session, extras=["dev"])
    Path("reports").mkdir(exist_ok=True)
    session.run(
        "bandit", "-r", "fmp_data",
        "--configfile", "pyproject.toml",
        "--format", "json",
        "--output", "reports/bandit-report.json",
    )


# ── Documentation ──────────────────────────────────────────────────────────
@nox.session(python="3.12", tags=["docs"])
def docs(session: Session) -> None:
    _sync_with_uv(session, extras=["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", tags=["docs"])
def docs_serve(session: Session) -> None:
    _sync_with_uv(session, extras=["docs"])
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8000")


# ── Dev convenience ────────────────────────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    _sync_with_uv(session, extras=["dev", "docs", "langchain", "mcp-server"])
    session.log("Dev env ready → try `uv run pytest` or `mkdocs serve`.")


# ── Coverage ----------------------------------------------------------------
@nox.session(python="3.12")
def coverage(session: Session) -> None:
    _sync_with_uv(session, extras=["dev"])
    Path("reports").mkdir(exist_ok=True)
    session.run(
        "pytest",
        "--cov=fmp_data",
        "--cov-report=xml:reports/coverage.xml",
        "--cov-report=html:reports/htmlcov",
        "--cov-report=term-missing",
    )
    session.log("HTML coverage: reports/htmlcov/index.html")


# ── Clean artefacts ----------------------------------------------------------
@nox.session(python="3.12")
def clean(session: Session) -> None:
    for pattern in [
        "dist", "build", "*.egg-info", ".pytest_cache", "reports",
        ".coverage*", ".mypy_cache", ".ruff_cache", "__pycache__",
    ]:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
            session.log(f"🗑️  removed {path}")
