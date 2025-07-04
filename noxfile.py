"""
Nox automation for fmp-data with PEP 735 dependency groups
──────────────────────────────────────────────────────────
Matrix:
  • tests: Python 3.10-3.13 × (core | langchain | mcp-server)
  • lint: ruff + mypy + bandit
  • docs: mkdocs build

Uses PEP 735 dependency groups for clean, modern dependency management.
"""

import os
import shutil
import sys
from pathlib import Path

import nox
from nox import Session

# Global settings
nox.options.reuse_venv = "yes"

# ─────────────── Matrix definitions ────────────────
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
FEATURE_GROUPS = [None, "langchain", "mcp-server"]
FEATURE_IDS = ["core", "lang", "mcp-server"]

# Allow local override for faster development
LOCAL_PYTHON_VERSIONS = (
    os.getenv("NOX_PYTHON_VERSIONS", "").split(",")
    if os.getenv("NOX_PYTHON_VERSIONS")
    else PYTHON_VERSIONS
)


def _detect_installer() -> str:
    """Detect the best available package installer."""
    if shutil.which("uv"):
        return "uv"
    return "pip"


def _load_dependency_groups() -> dict[str, list[str]]:
    """Load and expand dependency groups from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        print("Error: tomllib not available. Please use Python 3.11+ or install tomli")
        sys.exit(1)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    return config.get("dependency-groups", {})


def _expand_group(
    group_name: str, all_groups: dict[str, list[str]], visited: set[str] | None = None
) -> list[str]:
    """Recursively expand dependency groups, handling include-group references."""
    if visited is None:
        visited = set()

    if group_name in visited:
        print(f"Warning: Circular dependency detected for group '{group_name}'")
        return []

    if group_name not in all_groups:
        print(f"Warning: Group '{group_name}' not found")
        return []

    visited.add(group_name)
    expanded = []

    for dep in all_groups[group_name]:
        if isinstance(dep, dict) and "include-group" in dep:
            included_group = dep["include-group"]
            expanded.extend(_expand_group(included_group, all_groups, visited.copy()))
        else:
            expanded.append(str(dep))

    return expanded


def _install_groups(session: Session, groups: list[str]) -> None:
    """Install dependency groups using the best available installer."""
    if not groups:
        return

    installer = _detect_installer()
    all_groups = _load_dependency_groups()

    # Collect all dependencies from specified groups
    all_deps = []
    for group in groups:
        deps = _expand_group(group, all_groups)
        all_deps.extend(deps)

    # Remove duplicates while preserving order
    unique_deps = []
    seen = set()
    for dep in all_deps:
        if dep not in seen:
            unique_deps.append(dep)
            seen.add(dep)

    if not unique_deps:
        session.log(f"No dependencies found for groups: {groups}")
        return

    session.log(f"Installing {len(unique_deps)} dependencies with {installer}")

    if installer == "uv":
        session.run("uv", "pip", "install", *unique_deps, external=True)
    else:
        session.run("python", "-m", "pip", "install", *unique_deps)


def _install_project_and_groups(
    session: Session, *, extras: str | None = None, groups: list[str] | None = None
) -> None:
    """Install the project with optional extras and dependency groups."""
    installer = _detect_installer()

    # Install the project (with optional extras)
    if extras:
        install_target = f"-e.[{extras}]"
    else:
        install_target = "-e."

    session.log(f"Installing project with {installer}: {install_target}")

    if installer == "uv":
        session.run("uv", "pip", "install", install_target, external=True)
    else:
        session.run("python", "-m", "pip", "install", install_target)

    # Install dependency groups
    if groups:
        _install_groups(session, groups)


# ── Test matrix ─────────────────────────────────────────────────
@nox.session(python=LOCAL_PYTHON_VERSIONS, reuse_venv=True, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """Run tests for given Python version and optional feature group."""
    # Determine extras and groups based on feature
    extras = feature_group
    base_groups = ["test"]

    # Install project with appropriate dependencies
    _install_project_and_groups(session, extras=extras, groups=base_groups)

    # Run appropriate test suite
    if feature_group == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all features."""
    _install_project_and_groups(session, extras="langchain,mcp-server", groups=["test"])
    session.run("pytest", "-q", "--maxfail=1")


# ── MCP-specific test session ───────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _install_project_and_groups(session, extras="mcp-server", groups=["test"])
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


# ── Quality assurance sessions ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _install_groups(session, ["ci-lint"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_check(session: Session) -> None:
    """Check code formatting with black and isort."""
    _install_groups(session, ["lint"])
    session.run("black", "--check", "--diff", "fmp_data", "tests")
    session.run("isort", "--check-only", "--diff", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_fix(session: Session) -> None:
    """Fix code formatting with black and isort."""
    _install_groups(session, ["lint"])
    session.run("black", "fmp_data", "tests")
    session.run("isort", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _install_project_and_groups(session, groups=["ci-lint"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain dependencies."""
    _install_project_and_groups(session, extras="langchain", groups=["ci-lint"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_mcp(session: Session) -> None:
    """Run mypy type checking with MCP dependencies."""
    _install_project_and_groups(session, extras="mcp-server", groups=["ci-lint"])
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _install_groups(session, ["ci-lint"])
    session.run(
        "bandit",
        "-r",
        "fmp_data",
        "--configfile",
        "pyproject.toml",
    )


# ── Documentation ───────────────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with mkdocs."""
    _install_groups(session, ["docs"])
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", reuse_venv=True)
def docs_serve(session: Session) -> None:
    """Serve documentation locally for development."""
    _install_groups(session, ["docs"])
    session.run("mkdocs", "serve")


# ── Development utilities ───────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def dev_install(session: Session) -> None:
    """Install the package in development mode with all dependencies."""
    _install_project_and_groups(session, extras="langchain,mcp-server", groups=["dev"])
    session.log("✅ Development environment ready!")
    session.log("Run 'pytest' to run tests or 'mkdocs serve' for docs")


# ── CI/CD helpers ──────────────────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["ci"])
def ci_test(session: Session) -> None:
    """Minimal test suite for CI."""
    _install_project_and_groups(session, groups=["ci-test"])
    session.run("pytest", "-q", "--cov=fmp_data", "--cov-fail-under=80")


@nox.session(python="3.12", reuse_venv=True, tags=["ci"])
def ci_lint(session: Session) -> None:
    """Minimal linting for CI."""
    _install_groups(session, ["ci-lint"])
    session.run("ruff", "check", "fmp_data", "tests")
    session.run("mypy", "fmp_data")
