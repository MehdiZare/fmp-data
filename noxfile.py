"""
Nox automation for fmp-data — lock-free uv workflow
────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

import nox
from nox import Session

nox.options.reuse_venv = "yes"
nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
FEATURE_GROUPS = [None, "langchain", "mcp-server"]
FEATURE_IDS = ["core", "lang", "mcp-server"]

LOCAL_PY_VERSIONS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PYTHON_VERSIONS
)


def _install_groups(session: Session, groups: list[str]) -> None:
    """Install project and dependency groups."""
    session.install("-e", ".")

    try:
        import tomllib
    except ImportError:
        session.install("tomli")
        import tomli as tomllib

    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    dep_groups = data.get("dependency-groups", {})

    for group in groups:
        if dep_groups.get(group):
            session.install(*dep_groups[group])


# ── Tests ───────────────────────────────────────────────────────────────────
@nox.session(python=LOCAL_PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """Run the unit-test matrix."""
    groups = ["dev", "test"]
    if feature_group:
        groups.append(feature_group)

    _install_groups(session, groups)

    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.13")
def smoke(session: Session) -> None:
    """Lightweight import test for bleeding-edge interpreter."""
    _install_groups(session, ["dev"])
    session.run("python", "-c", "import fmp_data; print('✓ Import successful')")


# ── QA ──────────────────────────────────────────────────────────────────────
@nox.session(python="3.12", tags=["qa"])
def lint(session: Session) -> None:
    _install_groups(session, ["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", tags=["qa"])
def typecheck(session: Session) -> None:
    _install_groups(session, ["dev"])
    session.run("mypy", "fmp_data", "--exclude", "fmp_data/(lc|mcp)/.*")


@nox.session(python="3.12", tags=["qa"])
def security(session: Session) -> None:
    _install_groups(session, ["dev"])
    Path("reports").mkdir(exist_ok=True)
    session.run("bandit", "-r", "fmp_data", "--configfile", "pyproject.toml")


# ── Docs ────────────────────────────────────────────────────────────────────
@nox.session(python="3.12", tags=["docs"])
def docs(session: Session) -> None:
    _install_groups(session, ["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", tags=["docs"])
def docs_serve(session: Session) -> None:
    _install_groups(session, ["docs"])
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8000")


# ── Dev ─────────────────────────────────────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    _install_groups(session, ["dev", "docs", "langchain", "mcp-server"])


@nox.session(python="3.12")
def coverage(session: Session) -> None:
    _install_groups(session, ["dev"])
    Path("reports").mkdir(exist_ok=True)
    session.run("pytest", "--cov=fmp_data", "--cov-report=xml:reports/coverage.xml")


@nox.session(python="3.12")
def clean(session: Session) -> None:
    patterns = ["dist", "build", "*.egg-info", ".pytest_cache", "reports",
                ".coverage*", ".mypy_cache", ".ruff_cache", "__pycache__"]
    for pattern in patterns:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
