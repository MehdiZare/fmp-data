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

# CI detection
IS_CI = os.getenv("CI", "").lower() in ("true", "1", "yes")


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


def _handle_typecheck_error(session: Session, error: Exception, context: str) -> None:
    """Handle typecheck errors differently in CI vs local development."""
    if IS_CI:
        session.error(f"Type checking failed in {context}: {error}")
    else:
        session.warn(f"Type checking failed in {context}: {error}")
        session.warn("Run 'nox -s typecheck' locally to see full details")


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


# ── Quality assurance sessions ─────────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _sync_with_uv(session, groups=["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_check(session: Session) -> None:
    """Check code formatting with ruff."""
    _sync_with_uv(session, groups=["dev"])
    session.run("ruff", "format", "--check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_fix(session: Session) -> None:
    """Fix code formatting with ruff."""
    _sync_with_uv(session, groups=["dev"])
    session.run("ruff", "format", "fmp_data", "tests")
    session.run("ruff", "check", "--fix", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package (excluding optional features)."""
    _sync_with_uv(session, groups=["dev"])

    try:
        # Type check core package, excluding optional feature directories
        session.run(
            "mypy",
            "fmp_data",
            "--exclude",
            "fmp_data/(lc|mcp)/.*",
            "--show-error-codes",
            "--pretty",
        )
        session.log("✅ Core type checking passed")
    except Exception as e:
        _handle_typecheck_error(session, e, "core package")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain dependencies."""
    _sync_with_uv(session, groups=["dev", "langchain"])

    try:
        # Only check langchain-specific code
        session.run("mypy", "fmp_data/lc/", "--show-error-codes", "--pretty")
        session.log("✅ LangChain type checking passed")
    except Exception as e:
        _handle_typecheck_error(session, e, "langchain package")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_mcp(session: Session) -> None:
    """Run mypy type checking with MCP dependencies."""
    _sync_with_uv(session, groups=["dev", "mcp-server"])

    try:
        # Only check MCP-specific code
        session.run("mypy", "fmp_data/mcp/", "--show-error-codes", "--pretty")
        session.log("✅ MCP type checking passed")
    except Exception as e:
        _handle_typecheck_error(session, e, "mcp package")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_all(session: Session) -> None:
    """Run comprehensive type checking with all features."""
    _sync_with_uv(session, groups=["dev", "langchain", "mcp-server"])

    failed_checks = []

    # Check core
    try:
        session.run(
            "mypy",
            "fmp_data",
            "--exclude",
            "fmp_data/(lc|mcp)/.*",
            "--show-error-codes",
        )
        session.log("✅ Core type checking passed")
    except Exception as e:
        failed_checks.append("core")
        session.warn(f"❌ Core type checking failed: {e}")

    # Check langchain
    try:
        session.run("mypy", "fmp_data/lc/", "--show-error-codes")
        session.log("✅ LangChain type checking passed")
    except Exception as e:
        failed_checks.append("langchain")
        session.warn(f"❌ LangChain type checking failed: {e}")

    # Check MCP
    try:
        session.run("mypy", "fmp_data/mcp/", "--show-error-codes")
        session.log("✅ MCP type checking passed")
    except Exception as e:
        failed_checks.append("mcp")
        session.warn(f"❌ MCP type checking failed: {e}")

    # Summary
    if failed_checks:
        msg = f"Type checking failed for: {', '.join(failed_checks)}"
        if IS_CI:
            session.error(msg)
        else:
            session.warn(msg)
    else:
        session.log("🎉 All type checking passed!")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _sync_with_uv(session, groups=["dev"])

    # Ensure output directory exists
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    try:
        session.run(
            "bandit",
            "-r",
            "fmp_data",
            "--configfile",
            "pyproject.toml",
            "--format",
            "json",
            "--output",
            "reports/bandit-report.json",
        )
        session.log("✅ Security scan completed - no issues found")
    except Exception as e:
        session.warn(f"Security scan found issues: {e}")
        session.log("Check reports/bandit-report.json for details")


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
    session.log("Available commands:")
    session.log("  uv run pytest           # Run tests")
    session.log("  uv run mkdocs serve      # Serve docs")
    session.log("  nox -s lint              # Run linting")
    session.log("  nox -s typecheck         # Type check core")
    session.log("  nox -s typecheck_all     # Type check everything")


@nox.session(python="3.12", reuse_venv=True)
def coverage(session: Session) -> None:
    """Run tests with coverage reporting."""
    _sync_with_uv(session, groups=["dev"])

    # Ensure output directory exists
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    session.run(
        "pytest",
        "--cov=fmp_data",
        "--cov-report=xml:reports/coverage.xml",
        "--cov-report=html:reports/htmlcov",
        "--cov-report=term-missing",
    )
    session.log("Coverage reports generated:")
    session.log("  📊 XML: reports/coverage.xml")
    session.log("  🌐 HTML: reports/htmlcov/index.html")


@nox.session(python="3.12", reuse_venv=True)
def clean(session: Session) -> None:
    """Clean up build artifacts and cache files."""
    import shutil

    paths_to_clean = [
        "dist",
        "build",
        "*.egg-info",
        ".pytest_cache",
        "reports",
        ".coverage*",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
    ]

    cleaned_count = 0
    for path_pattern in paths_to_clean:
        for path in Path(".").glob(path_pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    session.log(f"🗑️  Removed directory: {path}")
                else:
                    path.unlink()
                    session.log(f"🗑️  Removed file: {path}")
                cleaned_count += 1

    if cleaned_count == 0:
        session.log("✨ Already clean!")
    else:
        session.log(f"🧹 Cleanup completed! Removed {cleaned_count} items")


# ── CI/CD helpers ───────────────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def ci_check(session: Session) -> None:
    """Run all CI checks (comprehensive quality check)."""
    session.log("🚀 Running comprehensive CI checks...")

    _sync_with_uv(session, groups=["dev"])

    checks = [
        ("Format check", ["ruff", "format", "--check", "fmp_data", "tests"]),
        ("Lint check", ["ruff", "check", "fmp_data", "tests"]),
        (
            "Type check (core)",
            ["mypy", "fmp_data", "--exclude", "fmp_data/(lc|mcp)/.*"],
        ),
    ]

    failed_checks = []

    for check_name, cmd in checks:
        try:
            session.run(*cmd)
            session.log(f"✅ {check_name} passed")
        except Exception as e:
            failed_checks.append(check_name)
            session.warn(f"❌ {check_name} failed: {e}")

    # Run tests
    try:
        session.run("pytest", "-q", "--maxfail=5")
        session.log("✅ Tests passed")
    except Exception as e:
        failed_checks.append("Tests")
        session.warn(f"❌ Tests failed: {e}")

    # Summary
    if failed_checks:
        session.error(f"CI checks failed: {', '.join(failed_checks)}")
    else:
        session.log("🎉 All CI checks passed!")


@nox.session(python="3.12", reuse_venv=True)
def pre_commit_check(session: Session) -> None:
    """Run checks that would be performed by pre-commit (for local testing)."""
    session.log("🔍 Running pre-commit style checks...")

    _sync_with_uv(session, groups=["dev"])

    # Core typecheck (what pre-commit would run)
    try:
        session.run(
            "mypy",
            "fmp_data",
            "--exclude",
            "fmp_data/(lc|mcp)/.*",
            "--show-error-codes",
        )
        session.log("✅ Pre-commit typecheck would pass")
    except Exception as e:
        session.warn(f"❌ Pre-commit typecheck would fail: {e}")
        if not IS_CI:
            session.log(
                "💡 This won't block your commit, but consider fixing before pushing"
            )
