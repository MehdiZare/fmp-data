"""
Nox automation for fmp-data with uv and PEP 735 dependency groups
────────────────────────────────────────────────────────────────
Simplified version using uv's native dependency group support.

Relative path: noxfile.py
"""

import os
from pathlib import Path

import nox
from nox import Session

# Global settings
nox.options.reuse_venv = "yes"

# Matrix definitions
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
FEATURE_GROUPS = [None, "langchain", "mcp-server"]
FEATURE_IDS = ["core", "lang", "mcp-server"]

# Allow local override for faster development
LOCAL_PYTHON_VERSIONS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PYTHON_VERSIONS
)


def _sync_with_uv(session: Session, *, groups: list[str] | None = None) -> None:
    """Sync dependencies using uv with specified groups."""
    if not groups:
        # Base installation without groups
        session.run("uv", "sync", external=True)
        return

    # Build sync command with groups
    sync_cmd = ["uv", "sync"]
    for group in groups:
        sync_cmd.extend(["--group", group])

    session.log(f"Installing with groups: {groups}")
    session.run(*sync_cmd, external=True)


# ── Test matrix ─────────────────────────────────────────────────
@nox.session(python=LOCAL_PYTHON_VERSIONS, reuse_venv=True, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """Run tests for given Python version and optional feature group."""
    # Determine groups to install
    groups = ["dev"]  # Always include dev dependencies for testing
    if feature_group:
        groups.append(feature_group)

    # Sync dependencies
    _sync_with_uv(session, groups=groups)

    # Run appropriate test suite
    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all features."""
    _sync_with_uv(session, groups=["dev", "langchain", "mcp-server"])
    session.run("pytest", "-q", "--maxfail=1")


# ── Feature-specific test sessions ──────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _sync_with_uv(session, groups=["dev", "mcp-server"])
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


@nox.session(python="3.12", reuse_venv=True, tags=["langchain"])
def test_langchain(session: Session) -> None:
    """Run LangChain-specific tests only."""
    _sync_with_uv(session, groups=["dev", "langchain"])
    session.run("pytest", "-q", "tests/unit/test_langchain.py", "-v")


# ── Quality assurance sessions ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _sync_with_uv(session, groups=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_check(session: Session) -> None:
    """Check code formatting with black and isort."""
    _sync_with_uv(session, groups=["dev"])
    session.run("black", "--check", "--diff", "fmp_data", "tests")
    session.run("isort", "--check-only", "--diff", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_fix(session: Session) -> None:
    """Fix code formatting with black and isort."""
    _sync_with_uv(session, groups=["dev"])
    session.run("black", "fmp_data", "tests")
    session.run("isort", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _sync_with_uv(session, groups=["dev"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain dependencies."""
    _sync_with_uv(session, groups=["dev", "langchain"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_mcp(session: Session) -> None:
    """Run mypy type checking with MCP dependencies."""
    _sync_with_uv(session, groups=["dev", "mcp-server"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _sync_with_uv(session, groups=["dev"])
    session.run(
        "bandit",
        "-r",
        "fmp_data",
        "--configfile",
        "pyproject.toml",
        "--format",
        "json",
        "--output",
        "bandit-report.json",
    )


# ── Documentation ───────────────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with mkdocs."""
    _sync_with_uv(session, groups=["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", reuse_venv=True)
def docs_serve(session: Session) -> None:
    """Serve documentation locally for development."""
    _sync_with_uv(session, groups=["docs"])
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8000")


# ── Development helpers ─────────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def dev_install(session: Session) -> None:
    """Install all development dependencies (convenience session)."""
    _sync_with_uv(session, groups=["dev", "docs", "langchain", "mcp-server"])
    session.log("✅ Development environment ready!")
    session.log("Run 'uv run pytest' to test or 'uv run mkdocs serve' for docs")


@nox.session(python="3.12", reuse_venv=True)
def coverage(session: Session) -> None:
    """Run tests with coverage reporting."""
    _sync_with_uv(session, groups=["dev"])
    session.run("pytest", "--cov=fmp_data", "--cov-report=xml", "--cov-report=html")
    session.log("Coverage reports generated: coverage.xml and htmlcov/")


@nox.session(python="3.12", reuse_venv=True)
def clean(session: Session) -> None:
    """Clean up build artifacts and cache files."""
    import shutil

    paths_to_clean = [
        "dist",
        "build",
        "*.egg-info",
        ".pytest_cache",
        "htmlcov",
        ".coverage*",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
    ]

    for path_pattern in paths_to_clean:
        for path in Path(".").glob(path_pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    session.log(f"Removed directory: {path}")
                else:
                    path.unlink()
                    session.log(f"Removed file: {path}")

    session.log("🧹 Cleanup completed!")
