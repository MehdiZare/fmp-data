"""
Nox automation for fmp-data with pure PEP 735 dependency groups
──────────────────────────────────────────────────────────────
Matrix:
  • tests     : Python 3.10-3.13 × (core | langchain | mcp-server groups)
  • lint      : ruff (style)
  • typecheck : mypy
  • security  : bandit
  • docs      : mkdocs build

Uses PEP 735 dependency groups with uv/pip for modern dependency management.
All optional features (langchain, mcp-server) are now dependency groups.
"""

import os
import shutil
from pathlib import Path

import nox
from nox import Session

# Global default: always try to re-use when possible
nox.options.reuse_venv = "yes"

# ─────────────── Matrix definitions ────────────────
PY_VERS = ["3.10", "3.11", "3.12", "3.13"]
# Note: These are now dependency groups, not extras
FEATURE_GROUPS = [None, "langchain", "mcp-server"]
FEATURE_IDS = ["core", "lang", "mcp-server"]

# For local development, you can override to test only available versions
LOCAL_PY_VERS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PY_VERS
)

# Check if uv is available and preferred
USE_UV = os.getenv("NOX_USE_UV", "1").lower() in ("1", "true", "yes")


def _has_uv() -> bool:
    """Check if uv is available in the system."""
    return shutil.which("uv") is not None


def _detect_tool() -> str:
    """Detect which tool to use based on availability and preferences."""
    if USE_UV and _has_uv():
        return "uv"
    else:
        return "pip"


# ─────────────── Install helpers ─────────────────────
def _install_with_uv(
    session: Session, *, extras: str | None = None, groups: list[str] | None = None
) -> None:
    """Install dependencies using uv with PEP 735 dependency groups."""
    session.log("📦 Installing dependencies with uv...")

    # Install the project with extras
    if extras:
        session.run("uv", "pip", "install", "-e", f".[{extras}]", external=True)
    else:
        session.run("uv", "pip", "install", "-e", ".", external=True)

    # Install dependency groups manually (uv doesn't support --dependency-groups yet)
    if groups:
        session.run(
            "python",
            "-c",
            f"""
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)

dependency_groups = config.get('dependency-groups', {{}})
for group in {groups!r}:
    if group in dependency_groups:
        deps = dependency_groups[group]
        if deps:
            import subprocess
            subprocess.run(['uv', 'pip', 'install'] + deps, check=True)
            print(f'Installed {{len(deps)}} dependencies from {{group}} group')
""",
            external=True,
        )


def _install_with_pip(
    session: Session, *, extras: str | None = None, groups: list[str] | None = None
) -> None:
    """Install dependencies using pip with dependency groups."""
    session.log("📦 Installing dependencies with pip...")

    # Install the project with extras
    if extras:
        session.install(f"-e.[{extras}]")
    else:
        session.install("-e.")

    # Install dependency groups manually
    if groups:
        session.run(
            "python",
            "-c",
            f"""
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)

dependency_groups = config.get('dependency-groups', {{}})
for group in {groups!r}:
    if group in dependency_groups:
        deps = dependency_groups[group]
        for dep in deps:
            import subprocess
            subprocess.run(['pip', 'install', dep], check=True)
        print(f'Installed {{len(deps)}} dependencies from {{group}} group')
""",
            external=True,
        )


def _install(session: Session, *, groups: list[str] | None = None) -> None:
    """Install project with specified dependency groups."""
    tool = _detect_tool()
    session.log(f"🔧 Using {tool} for dependency management")

    if tool == "uv":
        _install_with_uv(session, groups=groups)
    else:
        _install_with_pip(session, groups=groups)


def _install_deps_only(session: Session, groups: list[str] | None = None) -> None:
    """Install only dependency groups without the project itself."""
    if not groups:
        return

    tool = _detect_tool()

    if tool == "uv":
        # Install dependency groups manually since
        # uv doesn't support --dependency-groups yet
        session.run(
            "python",
            "-c",
            f"""
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)

dependency_groups = config.get('dependency-groups', {{}})
for group in {groups!r}:
    if group in dependency_groups:
        deps = dependency_groups[group]
        if deps:
            import subprocess
            subprocess.run(['uv', 'pip', 'install'] + deps, check=True)
            print(f'Installed {{len(deps)}} dependencies from {{group}} group')
""",
            external=True,
        )
    else:
        # Fallback for pip
        session.run(
            "python",
            "-c",
            f"""
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)

dependency_groups = config.get('dependency-groups', {{}})
for group in {groups!r}:
    if group in dependency_groups:
        deps = dependency_groups[group]
        for dep in deps:
            import subprocess
            subprocess.run(['pip', 'install', dep], check=True)
""",
            external=True,
        )


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=LOCAL_PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """Run tests for given Python version and optional dependency groups."""
    # Map features to dependency groups
    groups = ["test"]
    if feature_group == "langchain":
        groups.append("langchain")
    elif feature_group == "mcp-server":
        groups.append("mcp-server")

    _install(session, groups=groups)

    # Run different test sets based on feature
    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all features."""
    _install(session, groups=["test", "langchain", "mcp-server"])
    session.run("pytest", "-q", "--maxfail=1")


# ── MCP-specific test session ───────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _install(session, groups=["test", "mcp-server"])
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _install_deps_only(session, ["lint"])
    session.run("ruff", "check", "fmp_data", "tests", external=True)


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _install(session, groups=["lint"])  # lint group contains mypy
    session.run("mypy", "fmp_data", external=True)


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain dependencies."""
    _install(session, groups=["lint", "langchain"])
    session.run("mypy", "fmp_data", external=True)


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _install_deps_only(session, ["lint"])  # lint group contains bandit

    # Run bandit with project configuration from pyproject.toml
    session.run(
        "bandit",
        "-r",
        "fmp_data",
        "--configfile",
        "pyproject.toml",
        external=True,
    )


@nox.session(python="3.12", reuse_venv=True)
def docs(session: Session) -> None:
    """Build documentation with mkdocs."""
    _install(session, groups=["docs"])
    session.run("mkdocs", "build", "--strict", external=True)


@nox.session(python="3.12", reuse_venv=True)
def format_check(session: Session) -> None:
    """Check code formatting."""
    _install_deps_only(session, ["lint"])
    session.run("black", "--check", "--diff", "fmp_data", "tests", external=True)
    session.run("isort", "--check-only", "--diff", "fmp_data", "tests", external=True)


@nox.session(python="3.12", reuse_venv=True)
def format_fix(session: Session) -> None:
    """Fix code formatting."""
    _install_deps_only(session, ["lint"])
    session.run("black", "fmp_data", "tests", external=True)
    session.run("isort", "fmp_data", "tests", external=True)


# ── Coverage reporting ──────────────────────────────────────────
@nox.session(python="3.12")
def coverage(session: Session) -> None:
    """Run tests with coverage reporting."""
    _install(session, groups=["test"])
    session.run(
        "pytest",
        "--cov=fmp_data",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    )


# ── Development utilities ───────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    """Install project in development mode with all features."""
    _install(session, groups=["dev"])

    tool = _detect_tool()
    session.log("✅ Development environment ready!")

    if tool == "uv":
        session.log("💡 To activate: source .venv/bin/activate")
        session.log("💡 To run commands: uv run <command>")
    else:
        session.log("💡 To activate: source .nox/dev-install/bin/activate")


@nox.session(python="3.12")
def local_test(session: Session) -> None:
    """Quick local test suite - runs core tests on current Python version."""
    _install(session, groups=["test"])
    session.run("pytest", "-v", "--tb=short")


@nox.session(python="3.12")
def quick_check(session: Session) -> None:
    """Run quick quality checks for local development."""
    _install_deps_only(session, ["ci-lint"])

    session.log("🔍 Running quick quality checks...")

    # Format check
    session.run("black", "--check", "fmp_data", "tests", external=True)
    session.run("isort", "--check-only", "fmp_data", "tests", external=True)

    # Lint
    session.run("ruff", "check", "fmp_data", "tests", external=True)

    session.log("✅ Quick checks complete!")


@nox.session(python="3.12")
def clean(session: Session) -> None:
    """Clean up build artifacts and caches."""
    dirs_to_clean = [
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
        "htmlcov",
        "coverage.xml",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        ".venv",
        ".nox",
        "bandit-report.json",
    ]

    for pattern in dirs_to_clean:
        for path in Path(".").glob(f"**/{pattern}"):
            if path.is_dir():
                session.log(f"Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                session.log(f"Removing file: {path}")
                path.unlink()

    session.log("✅ Cleanup complete!")


# ── Tool compatibility checks ───────────────────────────────────
@nox.session(python="3.12")
def check_tools(session: Session) -> None:
    """Check which tools are available and their versions."""
    tools = {
        "uv": ["uv", "--version"],
        "pip": ["pip", "--version"],
        "nox": ["nox", "--version"],
        "git": ["git", "--version"],
    }

    session.log("🔍 Checking available tools...")

    for tool_name, cmd in tools.items():
        try:
            session.run(*cmd, external=True, silent=True)
            session.log(f"✅ {tool_name}: Available")
        except Exception:
            session.log(f"❌ {tool_name}: Not available")

    # Show current configuration
    tool = _detect_tool()
    session.log(f"🎯 Currently configured to use: {tool}")
    session.log(f"🔧 NOX_USE_UV environment variable: {os.getenv('NOX_USE_UV', '1')}")


@nox.session(python=False)
def check_python(session: Session) -> None:
    """Check which Python versions are available on the system."""
    python_versions = ["3.10", "3.11", "3.12", "3.13"]

    session.log("🐍 Checking available Python versions...")

    available_versions = []
    for version in python_versions:
        try:
            session.run(f"python{version}", "--version", external=True, silent=True)
            session.log(f"✅ Python {version}: Available")
            available_versions.append(version)
        except Exception:
            session.log(f"❌ Python {version}: Not found")

    if available_versions:
        session.log("💡 To run tests on available versions only:")
        session.log(f"   NOX_PYTHON_VERSIONS={','.join(available_versions)} nox")
        session.log(
            f"💡 To run on specific version: nox -s tests-{available_versions[0]}"
        )
    else:
        session.log("⚠️  No Python versions found. Check your Python installation.")
