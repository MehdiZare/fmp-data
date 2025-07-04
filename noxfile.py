"""
Nox automation for fmp-data with uv and PEP 735 dependency groups
────────────────────────────────────────────────────────────────
• Uses uv for fast dependency syncing.
• Python matrix 3.10 → 3.13; feature matrix core / LangChain / MCP-server.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

import nox
from nox import Session

# ── Global options ──────────────────────────────────────────────────────────
nox.options.reuse_venv = "yes"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
FEATURE_GROUPS  = [None, "langchain", "mcp-server"]
FEATURE_IDS     = ["core", "lang", "mcp-server"]

LOCAL_PYTHON_VERSIONS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PYTHON_VERSIONS
)

IS_CI = os.getenv("CI", "").lower() in {"true", "1", "yes"}


# ── Helpers ────────────────────────────────────────────────────────────────
def _sync_with_uv(session: Session, *, groups: list[str] | None = None) -> None:
    """
    Sync dependencies into the session's venv using uv.

    • Runtime dependencies are installed automatically (no flags needed).
    • Extra groups are appended as `--group <name>`.
    """
    cmd: list[str] = ["uv", "sync"]

    if groups:
        for grp in groups:
            cmd += ["--group", grp]

    session.log(f"⎈  {' '.join(cmd)}")
    session.run(*cmd, external=True)


def _handle_typecheck_error(session: Session, exc: Exception, ctx: str) -> None:
    if IS_CI:
        session.error(f"Type checking failed in {ctx}: {exc}")
    else:
        session.warn(f"Type checking failed in {ctx}: {exc}")
        session.warn("Run `nox -s typecheck` locally to inspect.")


# ── Test matrix ────────────────────────────────────────────────────────────
@nox.session(python=LOCAL_PYTHON_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """Run unit tests for each Python / feature combo."""
    groups = ["dev"]
    if feature_group:
        groups.append(feature_group)

    _sync_with_uv(session, groups=groups)

    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


# Smoke test for new interpreters (e.g. 3.13)
@nox.session(python="3.13")
def smoke(session: Session) -> None:
    _sync_with_uv(session, groups=["dev", "langchain", "mcp-server"])
    session.run("pytest", "-q", "--maxfail=1", "tests/smoke")


# ── Feature-focused test helpers ───────────────────────────────────────────
@nox.session(python="3.12", tags=["mcp"])
def test_mcp(session: Session) -> None:
    _sync_with_uv(session, groups=["dev", "mcp-server"])
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


@nox.session(python="3.12", tags=["langchain"])
def test_langchain(session: Session) -> None:
    _sync_with_uv(session, groups=["dev", "langchain"])
    session.run("pytest", "-q", "tests/unit/test_langchain.py", "-v")


# ── Quality gates (3.12) ──────────────────────────────────────────────────
@nox.session(python="3.12", tags=["qa"])
def lint(session: Session) -> None:
    _sync_with_uv(session, groups=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", tags=["qa"])
def typecheck(session: Session) -> None:
    _sync_with_uv(session, groups=["dev"])
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
    _sync_with_uv(session, groups=["dev"])
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
    _sync_with_uv(session, groups=["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", tags=["docs"])
def docs_serve(session: Session) -> None:
    _sync_with_uv(session, groups=["docs"])
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8000")


# ── Dev helper ─────────────────────────────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    _sync_with_uv(session, groups=["dev", "docs", "langchain", "mcp-server"])
    session.log("✅ Dev environment ready → try `uv run pytest` or `mkdocs serve`")


# ── Coverage (HTML & XML) ──────────────────────────────────────────────────
@nox.session(python="3.12")
def coverage(session: Session) -> None:
    _sync_with_uv(session, groups=["dev"])
    Path("reports").mkdir(exist_ok=True)
    session.run(
        "pytest",
        "--cov=fmp_data",
        "--cov-report=xml:reports/coverage.xml",
        "--cov-report=html:reports/htmlcov",
        "--cov-report=term-missing",
    )
    session.log("HTML coverage: reports/htmlcov/index.html")


# ── Clean artefacts ────────────────────────────────────────────────────────
@nox.session(python="3.12")
def clean(session: Session) -> None:
    patterns = [
        "dist", "build", "*.egg-info", ".pytest_cache", "reports",
        ".coverage*", ".mypy_cache", ".ruff_cache", "__pycache__",
    ]
    removed = 0
    for patt in patterns:
        for path in Path(".").glob(patt):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
            session.log(f"🗑️  Removed {path}")
            removed += 1
    session.log("✨ Cleanup complete" if removed else "Nothing to clean")
