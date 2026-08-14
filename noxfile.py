"""
Nox configuration for *fmp-data*

▪ test matrix      : 3.10 ─ 3.14
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
# Use the current Python version in CI, or the newest local version if available
def _runtime_py_version() -> tuple[int, int]:
    return (sys.version_info.major, sys.version_info.minor)


if os.getenv("CI") == "true":
    # In CI, use the versions explicitly installed in the matrix
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    PY_VERSIONS: Sequence[str] = ("3.10", "3.11", "3.12", "3.13", "3.14")
    DEFAULT_PYTHON = current_version
else:
    # Locally, prefer the newest available interpreter
    if _runtime_py_version() >= (3, 14):
        PY_VERSIONS = ("3.10", "3.11", "3.12", "3.13", "3.14")
        DEFAULT_PYTHON = "3.14"
    elif _runtime_py_version() >= (3, 13):
        PY_VERSIONS = ("3.10", "3.11", "3.12", "3.13")
        DEFAULT_PYTHON = "3.13"
    else:
        PY_VERSIONS = ("3.10", "3.11", "3.12")
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

    # Install dependency groups and extras from pyproject.toml so
    # floors live in one place and a bump there is enough to update CI.
    for extra in extras:
        if extra == "dev":
            session.run("uv", "pip", "install", "--group", "dev")
        elif extra in ["langchain", "mcp", "mcp-server"]:
            extra_name = "mcp" if extra == "mcp-server" else extra
            session.run("uv", "pip", "install", f"-e.[{extra_name}]")
        else:
            session.run("uv", "pip", "install", f"-e.[{extra}]")


def _pytest_xdist_args() -> list[str]:
    if os.getenv("CI") == "true":
        return []
    return ["-n", "auto"]


def _mcp_unit_tests() -> list[str]:
    """Every ``tests/unit/test_mcp*.py`` file for the mcp-server session."""
    return sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for p in (REPO_ROOT / "tests" / "unit").glob("test_mcp*.py")
    )


# --------------------------------------------------------------------------- #
#  Sessions                                                                   #
# --------------------------------------------------------------------------- #


@nox.session(python=PY_VERSIONS, tags=["tests"])
@nox.parametrize("feature_group", FEATURE_GROUPS, ids=FEATURE_IDS)
def tests(session: Session, feature_group: str | None) -> None:
    """
    Run *pytest* without coverage.
    """
    extras: list[str] = ["dev"]  # dev extra contains pytest + pytest-cov
    if feature_group:
        extras.append(feature_group)

    _sync_with_uv(session, extras)

    pytest_args = ["-q", *_pytest_xdist_args()]

    if feature_group == "mcp-server":
        mcp_tests = _mcp_unit_tests()
        if mcp_tests:
            session.run(
                "pytest",
                *pytest_args,
                *mcp_tests,
                "-m",
                "not integration",
                success_codes=[0, 5],  # 0=success, 5=no tests collected
            )
        else:
            session.log("Skipping mcp-server tests - no tests/unit/test_mcp*.py")
    else:
        # For core and langchain, run all tests
        session.run("pytest", *pytest_args, success_codes=[0, 5])


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

    # Apply the configured coverage threshold from pyproject.toml
    session.run("coverage", "report")

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
        pytest_args.extend(_pytest_xdist_args())

        env = {"COVERAGE_FILE": str(coverage_file)}

        # Handle different feature groups
        if feature_group == "mcp-server":
            mcp_tests = _mcp_unit_tests()
            if mcp_tests:
                session.run(
                    "pytest",
                    *pytest_args,
                    *mcp_tests,
                    "-m",
                    "not integration",
                    env=env,
                    success_codes=[0, 5],  # 0=success, 5=no tests collected
                )
            else:
                session.log("Skipping mcp-server tests - no tests/unit/test_mcp*.py")
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
    session.run("coverage", "report")


@nox.session(python=DEFAULT_PYTHON, tags=["coverage-extras"])
def coverage_extras(session: Session) -> None:
    """Separate extras coverage gate for lc / mcp / Redis (#273).

    Core 80% still omits these trees. This session installs the extras,
    measures only those files, and fails under 80%. The baseline was 66.78%
    when the gate landed; dedicated tests for ``redis_backend``,
    ``lc.validation``, ``lc.__init__``, ``mcp.utils`` and ``mcp.setup``
    raised it to 86.99%, which is the headroom that makes this safe to
    require at the ruleset layer (#282). xdist is off so local and CI
    numbers stay comparable.
    """
    _sync_with_uv(
        session,
        extras=["dev", "langchain", "mcp-server", "cache-redis"],
    )
    session.run(
        "pytest",
        "-q",
        "tests/unit",
        "--cov=fmp_data.lc",
        "--cov=fmp_data.mcp",
        "--cov=fmp_data.cache.redis_backend",
        "--cov-config=extras.coveragerc",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    )


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
        *_pytest_xdist_args(),
    )


@nox.session(python=DEFAULT_PYTHON, tags=["lint"])
def lint(session: Session) -> None:
    """Static style checks (ruff check and format - no code execution)."""
    _sync_with_uv(session, extras=["dev"])
    session.run("ruff", "check", ".", "--output-format=concise")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=DEFAULT_PYTHON, tags=["typecheck"])
def typecheck(session: Session) -> None:
    """Run *mypy* with strict settings."""
    _sync_with_uv(session, extras=["dev"])
    # tests/ is checked too (relaxed via the tests.* override in pyproject.toml)
    # so annotations in tests are verified rather than decorative.
    session.run("mypy", PACKAGE_NAME, "tests")


@nox.session(python=DEFAULT_PYTHON, tags=["security"])
def security(session: Session) -> None:
    """Static-analyse the source and audit the extra graph for known CVEs.

    Two halves:

    * ``bandit`` over the library. #278 replaced the global ``B404`` /
      ``B603`` / ``B607`` / ``B608`` skips with narrow, documented
      file-local ``# nosec`` notes, but bandit only ran from
      ``.pre-commit-config.yaml`` — there is no pre-commit CI job, so the
      narrowing was unenforced on CI and a new ``subprocess`` call could
      land unreviewed (#273).
    * ``pip-audit`` over the extras resolved from ``pyproject.toml`` at
      session time (no committed hashed lock), so a floor bump is enough
      to pick up newer deps (#252 FMP-SEC-008).
    """
    session.install("uv", "pip-audit>=2.10.1", "bandit[toml]>=1.8.0")
    session.run("bandit", "-c", "pyproject.toml", "-r", PACKAGE_NAME)
    export = Path(session.create_tmp()) / "requirements-audit.txt"
    session.run(
        "uv",
        "export",
        "--extra",
        "langchain",
        "--extra",
        "mcp",
        "--extra",
        "cache-redis",
        "--no-dev",
        "--no-emit-project",
        "--no-hashes",
        "--no-header",
        "--no-annotate",
        "-o",
        str(export),
    )
    session.run(
        "pip-audit",
        "-r",
        str(export),
        "--strict",
        "--no-deps",
        "--disable-pip",
    )


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
