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
nox.options.default_venv_backend = "uv"

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
def _install_with_uv(session: Session, *, groups: list[str] | None = None) -> None:
    """
    Install the project with optional dependency groups.

    This installs the project in editable mode along with specified groups.
    """
    # First install the project itself
    session.install("-e", ".")

    # Then install additional groups if specified
    if groups:
        for group in groups:
            _install_group_fallback(session, group)


def _install_group_fallback(session: Session, group: str) -> None:
    """Install dependency group by parsing pyproject.toml."""
    try:
        # Python 3.11+ has tomllib built-in
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            session.install("tomli")
            import tomli as tomllib

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        session.log(f"⚠️  pyproject.toml not found, skipping group {group}")
        return

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Try dependency-groups first, then project.optional-dependencies
    groups_data = data.get("dependency-groups", {})
    if group not in groups_data:
        groups_data = data.get("project", {}).get("optional-dependencies", {})

    if group in groups_data:
        deps = groups_data[group]
        if deps:
            session.log(f"📦  Installing {group} group: {len(deps)} packages")
            session.install(*deps)
        else:
            session.log(f"📦  Group {group} is empty")
    else:
        session.log(f"⚠️  Group {group} not found in pyproject.toml")




# ── Test matrix ────────────────────────────────────────────────────────────
@nox.session(python=LOCAL_PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """
    Run the unit-test matrix.

    • Always pull *dev* and *test* extras (linters + pytest)
    • Optionally pull the feature-specific runtime extras
    """
    groups: list[str] = ["dev", "test"]
    if feature_group:
        groups.append(feature_group)

    _install_with_uv(session, groups=groups)

    # ---- pytest ----------------------------------------------------------
    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.13")
def smoke(session: Session) -> None:
    """Lightweight import test for bleeding-edge interpreter."""
    _install_with_uv(session, groups=["dev", "langchain", "mcp-server"])
    session.run("pytest", "-q", "--maxfail=1", "tests/smoke")


# ── QA sessions (run on 3.12) ──────────────────────────────────────────────
@nox.session(python="3.12", tags=["qa"])
def lint(session: Session) -> None:
    _install_with_uv(session, groups=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", tags=["qa"])
def typecheck(session: Session) -> None:
    _install_with_uv(session, groups=["dev"])
    session.run(
        "mypy",
        "fmp_data",
        "--exclude", "fmp_data/(lc|mcp)/.*",
        "--show-error-codes",
        "--pretty",
    )


@nox.session(python="3.12", tags=["qa"])
def security(session: Session) -> None:
    _install_with_uv(session, groups=["dev"])
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
    _install_with_uv(session, groups=["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", tags=["docs"])
def docs_serve(session: Session) -> None:
    _install_with_uv(session, groups=["docs"])
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8000")


# ── Dev convenience ────────────────────────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    _install_with_uv(session, groups=["dev", "docs", "langchain", "mcp-server"])
    session.log("Dev env ready → try `uv run pytest` or `mkdocs serve`.")


# ── Coverage ----------------------------------------------------------------
@nox.session(python="3.12")
def coverage(session: Session) -> None:
    _install_with_uv(session, groups=["dev"])
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
