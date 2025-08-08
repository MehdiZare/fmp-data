"""
Nox configuration for *fmp-data*

▪ test matrix      : 3.10 ─ 3.12 (3.13 when available)
▪ optional groups  : dev, lint, typecheck, security, langchain, mcp-server …
▪ package manager  : uv (fast resolver / installer)

Run "nox -s tests-3.12(mcp-server)" for a single combo, or just "nox" to
execute every default session.

Author: Mehdi Zare
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import os
from pathlib import Path
import sys

import nox
from nox.sessions import Session

# --------------------------------------------------------------------------- #
#  Globals                                                                    #
# --------------------------------------------------------------------------- #

# Python interpreters used across sessions
# Use the current Python version in CI, or 3.13 locally if available
if os.getenv("CI") == "true":
    # In CI, use the Python version that's already set up
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12", "3.13")
    DEFAULT_PYTHON = current_version
else:
    # Locally, prefer 3.13 if available
    if sys.version_info >= (3, 13):
        PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12", "3.13")
        DEFAULT_PYTHON = "3.13"
    else:
        PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12")
        DEFAULT_PYTHON = "3.12"

# Feature-flag groups that map to [project.optional-dependencies]
FEATURE_GROUPS: Sequence[str | None] = (
    None,  # base             → install just the core package
    "langchain",  # extras = dev+langchain
    "mcp-server",
)
FEATURE_IDS: Sequence[str] = (
    "core",
    "langchain",
    "mcp-server",
)

REPO_ROOT = Path(__file__).parent
PACKAGE_NAME = "fmp_data"

# --------------------------------------------------------------------------- #
#  Helper: sync deps with uv                                                  #
# --------------------------------------------------------------------------- #


def _sync_with_uv(session: Session, extras: Iterable[str] = ()) -> None:
    """
    Synchronize the session's virtualenv with *uv*.

    Uses dependency groups from pyproject.toml without duplication.
    """
    if os.getenv("NOX_USE_UV", "1") != "1":
        # Fallback to pip with extras
        extras_str = f"[{','.join(extras)}]" if extras else ""
        session.install(f"-e.{extras_str}")
        return

    # Install uv in the session if not available
    session.install("uv")

    # Install the base package first
    session.run("uv", "pip", "install", "-e", ".")

    # Install dependency groups and extras separately
    for extra in extras:
        if extra == "dev":
            # Install dev dependencies from dependency-groups
            session.run(
                "uv",
                "pip",
                "install",
                "pytest>=8.3.3",
                "pytest-asyncio>=0.24.0",
                "pytest-cov>=6.0.0",
                "pytest-mock>=3.14.0",
                "coverage>=7.6.4",
                "freezegun>=1.5.1",
                "responses>=0.25.3",
                "vcrpy>=6.0.2",
            )
        elif extra in ["langchain", "mcp", "mcp-server"]:
            # Handle actual extras from [project.optional-dependencies]
            # mcp-server maps to mcp in optional-dependencies
            extra_name = "mcp" if extra == "mcp-server" else extra
            session.run("uv", "pip", "install", f"-e.[{extra_name}]")
        else:
            # Try as an extra
            session.run("uv", "pip", "install", f"-e.[{extra}]")


# --------------------------------------------------------------------------- #
#  Sessions                                                                   #
# --------------------------------------------------------------------------- #


@nox.session(python=PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """
    Run *pytest* with coverage.

    Individual coverage files are generated for each session.
    Use the 'coverage_report' session to combine and check thresholds.
    """
    extras: list[str] = ["dev"]  # dev extra contains pytest + pytest-cov
    if feature_group:
        extras.append(feature_group)

    _sync_with_uv(session, extras)

    # Use unique coverage file names to avoid conflicts in parallel runs
    # Ensure coverage files are created in the repo root
    coverage_file = REPO_ROOT / f".coverage.{session.python}.{feature_group or 'core'}"

    # Base pytest args - no coverage threshold during individual runs
    pytest_args = [
        "-q",
        "--cov",
        PACKAGE_NAME,
        "--cov-append",
        "--cov-config=pyproject.toml",
        "--cov-report=term-missing",
        "--cov-fail-under=0",  # No threshold during individual sessions
    ]

    # Set environment variable for coverage file with absolute path
    env = {"COVERAGE_FILE": str(coverage_file)}

    if feature_group == "mcp-server":
        # Check if mcp tests exist and handle gracefully
        mcp_test_file = Path("tests/unit/test_mcp.py")
        if mcp_test_file.exists():
            # Use success_codes to handle no tests collected gracefully
            session.run(
                "pytest",
                *pytest_args,
                "tests/unit/test_mcp.py",
                "-m",
                "not integration",
                env=env,
                success_codes=[0, 5],  # 0=success, 5=no tests collected
            )
        else:
            session.log("Skipping mcp-server tests - test_mcp.py not found")
            # Create minimal coverage file for this feature group
            session.run(
                "python",
                "-c",
                f"""
import coverage
cov = coverage.Coverage(data_file='{coverage_file}')
cov.start()
cov.stop()
cov.save()
""",
            )
    else:
        # For core and langchain, run all tests
        session.run("pytest", *pytest_args, env=env, success_codes=[0, 5])

    # Verify coverage file was created
    if not coverage_file.exists():
        session.log(f"Creating fallback coverage file: {coverage_file}")
        session.run(
            "python",
            "-c",
            f"""
import coverage
cov = coverage.Coverage(data_file='{coverage_file}')
cov.start()
cov.stop()
cov.save()
""",
        )

    session.log(f"Coverage data saved to {coverage_file}")


@nox.session(python=DEFAULT_PYTHON, tags=["coverage"])
def coverage_report(session: Session) -> None:
    """Generate combined coverage report from all test runs and apply threshold."""
    _sync_with_uv(session, extras=["dev"])

    # List available coverage files for debugging
    coverage_files = list(Path(".").glob(".coverage.*"))
    session.log(f"Found coverage files: {[str(f) for f in coverage_files]}")

    if not coverage_files:
        session.error("No coverage files found. Run tests first.")

    # Combine all coverage files
    session.run("coverage", "combine")

    # Generate reports
    session.run("coverage", "xml")
    session.run("coverage", "html")

    # Apply the 80% threshold to combined coverage
    session.run("coverage", "report", "--fail-under=80")

    session.log("Coverage reports generated: coverage.xml and htmlcov/")


@nox.session(python=DEFAULT_PYTHON, tags=["coverage-local"])
def coverage_local(session: Session) -> None:
    """
    Run all feature group tests and generate
    combined coverage report (for local development).

    This runs all feature groups on the current Python version.
    """
    _sync_with_uv(session, extras=["dev"])

    # Clean up any existing coverage files
    for coverage_file in Path(".").glob(".coverage*"):
        coverage_file.unlink(missing_ok=True)

    session.log(f"Running all feature group tests with Python {session.python}")

    # Run all feature group combinations for the current Python version
    for feature_group, feature_id in zip(FEATURE_GROUPS, FEATURE_IDS, strict=False):
        session.log(f"Running tests for {feature_id} feature group")

        # Use unique coverage file names with absolute paths
        coverage_file = REPO_ROOT / f".coverage.{session.python}.{feature_id}"

        # Base pytest args
        pytest_args = [
            "-q",
            "--cov",
            PACKAGE_NAME,
            "--cov-config=pyproject.toml",
            "--cov-report=term-missing",
            "--cov-fail-under=0",
        ]

        env = {"COVERAGE_FILE": str(coverage_file)}

        # Handle different feature groups
        if feature_group == "mcp-server":
            # Check if mcp tests exist first
            mcp_test_file = Path("tests/unit/test_mcp.py")
            if mcp_test_file.exists():
                session.run(
                    "pytest",
                    *pytest_args,
                    "tests/unit/test_mcp.py",
                    "-m",
                    "not integration",
                    env=env,
                    success_codes=[0, 5],  # 0=success, 5=no tests collected
                )
            else:
                session.log("Skipping mcp-server tests - test_mcp.py not found")
                # Create minimal coverage file for this feature group
                session.run(
                    "python",
                    "-c",
                    f"""
import coverage
cov = coverage.Coverage(data_file='{coverage_file}')
cov.start()
cov.stop()
cov.save()
""",
                )
        else:
            # For all other feature groups (core, langchain),
            # run standard pytest
            session.run("pytest", *pytest_args, env=env, success_codes=[0, 5])

        # Ensure coverage file exists
        if not coverage_file.exists():
            session.run(
                "python",
                "-c",
                f"""
import coverage
cov = coverage.Coverage(data_file='{coverage_file}')
cov.start()
cov.stop()
cov.save()
""",
            )

    # Now combine and report
    session.log("Combining coverage files...")
    session.run("coverage", "combine")
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.run("coverage", "report", "--fail-under=80")


@nox.session(python=DEFAULT_PYTHON, tags=["test-local"])
def test_local(session: Session) -> None:
    """
    Run tests like your original workflow - simple and fast for local development.

    This matches your original 'pytest --cov fmp_data' workflow.
    """
    _sync_with_uv(session, extras=["dev"])

    # Clean up any existing coverage files
    for coverage_file in Path(".").glob(".coverage*"):
        coverage_file.unlink(missing_ok=True)

    # Run the standard test suite (core tests)
    session.run(
        "pytest",
        "-q",
        "--cov",
        PACKAGE_NAME,
        "--cov-config=pyproject.toml",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-report=html",
        "--fail-under=80",
    )


@nox.session(python=DEFAULT_PYTHON, tags=["lint"])
def lint(session: Session) -> None:
    """Static style checks (ruff, black - no code execution)."""
    _sync_with_uv(session, extras=["dev"])
    session.run("ruff", "check", ".", "--output-format=concise")
    session.run("black", "--check", ".")


@nox.session(python=DEFAULT_PYTHON, tags=["typecheck"])
def typecheck(session: Session) -> None:
    """Run *mypy* with strict settings."""
    _sync_with_uv(session, extras=["dev"])
    session.run("mypy", PACKAGE_NAME)


@nox.session(python=DEFAULT_PYTHON, tags=["security"])
def security(session: Session) -> None:
    """Check dependencies for known CVEs."""
    _sync_with_uv(session, extras=["dev"])
    session.run("pip-audit")


@nox.session(python=DEFAULT_PYTHON, tags=["smoke"])
def smoke(session: Session) -> None:
    """
    Quick import test - useful in release pipelines to ensure fresh wheels
    start up without heavy dependencies.
    """
    _sync_with_uv(session)
    session.run(
        "python", "-c", f"import {PACKAGE_NAME}; print({PACKAGE_NAME}.__version__)"
    )
