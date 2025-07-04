"""
Nox automation for fmp-data — uv + PEP 735 groups
──────────────────────────────────────────────────
• Installs *runtime* group first, then requested extras.
• Python matrix: 3.10 → 3.13; feature matrix: core / LangChain / MCP.
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


# ── Helper: two-phase uv install ───────────────────────────────────────────
def _sync_with_uv(session: Session, *, extras: list[str] | None = None) -> None:
    """
    Ensure runtime + selected extras are present.

    1. `uv sync`                → runtime
    2. `uv sync --group <extra>` per requested group
    """
    # 1. runtime (default)
    session.run("uv", "sync", external=True)

    # 2. extras
    if extras:
        for grp in extras:
            session.run("uv", "sync", "--group", grp, external=True)
        session.log(f"✓ installed extras: {', '.join(extras)}")


def _handle_typecheck_error(session: Session, exc: Exception, ctx: str) -> None:
    if IS_CI:
        session.error(f"Type checking failed in {ctx}: {exc}")
    else:
        session.warn(f"Type checking failed in {ctx}: {exc}")


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


# Quick smoke session for newest interpreter
@nox.session(python="3.13")
def smoke(session: Session) -> None:
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
    try:
        session.run(
            "mypy",
            "fmp_data",
            "--exclude", "fmp_data/(lc|mcp)/.*",
            "--show-error-codes",
            "--pretty",
        )
    except Exception as exc:
        _handle_typecheck_error(session, exc, "core package")


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


# ── Docs sessions ──────────────────────────────────────────────────────────
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
    session.log("✅ Dev env ready — try `uv run pytest`, `mkdocs serve`.")


# ── Coverage ───────────────────────────────────────────────────────────────
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
    session.log("HTML report → reports/htmlcov/index.html")


# ── Clean artefacts ────────────────────────────────────────────────────────
@nox.session(python="3.12")
def clean(session: Session) -> None:
    to_rm = [
        "dist", "build", "*.egg-info", ".pytest_cache", "reports",
        ".coverage*", ".mypy_cache", ".ruff_cache", "__pycache__",
    ]
    removed = 0
    for patt in to_rm:
        for p in Path(".").glob(patt):
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            removed += 1
            session.log(f"🗑️  removed {p}")
    session.log("✨ nothing to clean" if removed == 0 else "✓ cleanup done")
