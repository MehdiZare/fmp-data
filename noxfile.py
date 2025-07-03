"""
Nox automation for fmp-data with dual Poetry/uv support
──────────────────────────────────────────────────────
Matrix:
  • tests     : Python 3.10-3.13 × (core | langchain | mcp extra)
  • lint      : ruff (style)
  • typecheck : mypy
  • security  : bandit
  • docs      : mkdocs build

Automatically detects and uses uv when available for faster installs,
gracefully falls back to Poetry when uv is not available.
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
EXTRAS = [None, "langchain", "mcp-server"]
EXTRA_IDS = ["core", "lang", "mcp-server"]

# Check if uv is available and preferred
USE_UV = os.getenv("NOX_USE_UV", "").lower() in ("1", "true", "yes")


def _has_uv() -> bool:
    """Check if uv is available in the system."""
    return shutil.which("uv") is not None


def _has_poetry() -> bool:
    """Check if Poetry is available in the system."""
    return shutil.which("poetry") is not None


def _detect_tool() -> str:
    """Detect which tool to use based on availability and preferences."""
    if USE_UV and _has_uv():
        return "uv"
    elif _has_poetry():
        return "poetry"
    elif _has_uv():
        return "uv"
    else:
        return "pip"


# ─────────────── Install helpers ─────────────────────
def _install_with_uv(
    session: Session, *, extras: str | None = None, dev: bool = False
) -> None:
    """Install dependencies using uv."""
    session.log("📦 Installing dependencies with uv...")

    # Build the installation command
    extras_list = []
    if extras:
        extras_list.append(extras)
    if dev:
        extras_list.append("dev")

    if extras_list:
        session.run("uv", "sync", f"--extra={','.join(extras_list)}", external=True)
    else:
        session.run("uv", "sync", external=True)


def _install_with_poetry(
    session: Session, *, extras: str | None = None, dev: bool = False
) -> None:
    """Install dependencies using Poetry."""
    session.log("📦 Installing dependencies with Poetry...")
    session.install("poetry")

    cmd = ["poetry", "install", "--no-interaction"]

    # Add dev dependencies
    if dev:
        cmd.extend(["--with", "dev"])

    # Add extras
    if extras:
        cmd.extend(["--extras", extras])

    session.run(*cmd, external=True)


def _install_with_pip(
    session: Session, *, extras: str | None = None, dev: bool = False
) -> None:
    """Fallback installation using pip."""
    session.log("📦 Installing dependencies with pip...")

    # Install the project
    if extras and dev:
        session.install(f".[{extras},dev]")
    elif extras:
        session.install(f".[{extras}]")
    elif dev:
        session.install(".[dev]")
    else:
        session.install(".")


def _install(session: Session, *, extras: str | None = None, dev: bool = False) -> None:
    """Install project with specified extras using the best available tool."""
    tool = _detect_tool()
    session.log(f"🔧 Using {tool} for dependency management")

    if tool == "uv":
        _install_with_uv(session, extras=extras, dev=dev)
    elif tool == "poetry":
        _install_with_poetry(session, extras=extras, dev=dev)
    else:
        _install_with_pip(session, extras=extras, dev=dev)


def _install_deps_only(session: Session, extras: list[str] | None = None) -> None:
    """Install only dependencies without the project itself."""
    tool = _detect_tool()

    if tool == "uv":
        # For uv, we can use sync to install from lock file
        if extras:
            for extra in extras:
                session.run("uv", "sync", f"--extra={extra}", external=True)
        else:
            session.run("uv", "sync", external=True)
    else:
        # For Poetry/pip, install project which pulls dependencies
        _install(session, extras=",".join(extras) if extras else None, dev=True)


# ── test matrix ─────────────────────────────────────────────────
@nox.session(python=PY_VERS, reuse_venv=True, tags=["tests"])
@nox.parametrize("extra", EXTRAS, ids=EXTRA_IDS)
def tests(session: Session, extra: str | None) -> None:
    """Run tests for given Python version and optional extras."""
    _install(session, extras=extra, dev=True)

    # Run different test sets based on extra
    if extra == "mcp-server":
        session.run("pytest", "-q", "tests/unit/test_mcp.py", "-m", "not integration")
    else:
        session.run("pytest", "-q")


@nox.session(python="3.12")
def smoke(session: Session) -> None:
    """Quick smoke test with all extras."""
    _install(session, extras="langchain,mcp-server", dev=True)
    session.run("pytest", "-q", "--maxfail=1")


# ── MCP-specific test session ───────────────────────────────────
@nox.session(python="3.12", reuse_venv=True, tags=["mcp"])
def test_mcp(session: Session) -> None:
    """Run MCP-specific tests only."""
    _install(session, extras="mcp-server", dev=True)
    session.run("pytest", "-q", "tests/unit/test_mcp.py", "-v")


# ── QA sessions on one interpreter ─────────────────────────────
@nox.session(python="3.12", reuse_venv=True)
def lint(session: Session) -> None:
    """Run ruff linting."""
    _install_deps_only(session, ["dev"])
    session.run("ruff", "check", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def typecheck(session: Session) -> None:
    """Run mypy type checking on core package."""
    _install(session, dev=True)
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def typecheck_lang(session: Session) -> None:
    """Run mypy type checking with langchain extras."""
    _install(session, extras="langchain", dev=True)
    session.run("mypy", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def security(session: Session) -> None:
    """Run bandit security checks."""
    _install_deps_only(session, ["dev"])
    session.run("bandit", "-r", "fmp_data", "-f", "json", "-o", "bandit-report.json")
    session.run("bandit", "-r", "fmp_data")


@nox.session(python="3.12", reuse_venv=True)
def docs(session: Session) -> None:
    """Build documentation with mkdocs."""
    _install(session, extras="docs", dev=True)
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12", reuse_venv=True)
def format_check(session: Session) -> None:
    """Check code formatting."""
    _install_deps_only(session, ["dev"])
    session.run("black", "--check", "--diff", "fmp_data", "tests")
    session.run("isort", "--check-only", "--diff", "fmp_data", "tests")


@nox.session(python="3.12", reuse_venv=True)
def format_fix(session: Session) -> None:
    """Fix code formatting."""
    _install_deps_only(session, ["dev"])
    session.run("black", "fmp_data", "tests")
    session.run("isort", "fmp_data", "tests")


# ── Coverage reporting ──────────────────────────────────────────
@nox.session(python="3.12")
def coverage(session: Session) -> None:
    """Run tests with coverage reporting."""
    _install(session, dev=True)
    session.run(
        "pytest",
        "--cov=fmp_data",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-report=term-missing",
    )


# ── Development utilities ───────────────────────────────────────
@nox.session(python="3.12")
def dev_install(session: Session) -> None:
    """Install project in development mode with all extras."""
    _install(session, extras="langchain,mcp-server", dev=True)

    tool = _detect_tool()
    session.log("✅ Development environment ready!")

    if tool == "uv":
        session.log("💡 To activate: source .venv/bin/activate")
        session.log("💡 To run commands: uv run <command>")
    elif tool == "poetry":
        session.log("💡 To activate: poetry shell")
        session.log("💡 To run commands: poetry run <command>")
    else:
        session.log("💡 To activate: source .nox/dev-install/bin/activate")


@nox.session(python="3.12")
def clean(session: Session) -> None:
    """Clean up build artifacts and caches."""
    import shutil

    dirs_to_clean = [
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
        "coverage_html",
        "coverage.xml",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        ".venv",  # uv venv
        ".nox",  # nox environments
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
        "poetry": ["poetry", "--version"],
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
    session.log(
        f"🔧 NOX_USE_UV environment variable: {os.getenv('NOX_USE_UV', 'not set')}"
    )


# ── Benchmark sessions ──────────────────────────────────────────
@nox.session(python="3.12")
def benchmark_install(session: Session) -> None:
    """Benchmark installation speed of different tools."""
    import time

    # Clean slate
    session.run(
        "rm", "-rf", ".venv", ".nox/benchmark*", external=True, success_codes=[0, 1]
    )  # noqa: S607

    session.log("🏁 Benchmarking installation speed...")

    if _has_uv():
        start = time.time()
        session.run("uv", "sync", "--extra=dev", external=True)  # noqa: S607
        uv_time = time.time() - start
        session.log(f"⚡ uv installation time: {uv_time:.2f}s")
        session.run("rm", "-rf", ".venv", external=True)  # noqa: S607

    if _has_poetry():
        start = time.time()
        session.install("poetry")
        session.run("poetry", "install", "--with=dev", external=True)  # noqa: S607
        poetry_time = time.time() - start
        session.log(f"🐍 Poetry installation time: {poetry_time:.2f}s")

        if _has_uv():
            speedup = poetry_time / uv_time
            session.log(f"🚀 uv is {speedup:.1f}x faster than Poetry")

    session.log("✅ Benchmark complete!")
