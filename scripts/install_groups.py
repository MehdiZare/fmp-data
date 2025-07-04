#!/usr/bin/env python3
"""
PEP 735 Dependency Group Installer
─────────────────────────────────
Install dependency groups from pyproject.toml with support for include-group references.

Usage:
    python scripts/install_groups.py [tool] [group1] [group2] ...

Examples:
    python scripts/install_groups.py uv dev
    python scripts/install_groups.py pip langchain mcp-server test
    python scripts/install_groups.py uv ci-lint ci-test
    python scripts/install_groups.py uv dev --system  # Force system install

Author: Generated for fmp-data project
License: MIT
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def load_pyproject():
    """Load pyproject.toml configuration."""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            print(
                "❌ Error: tomllib/tomli not available. Install with: pip install tomli"
            )
            sys.exit(1)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ Error: pyproject.toml not found")
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def expand_dependencies(
    group_name: str, dependency_groups: dict, visited: set | None = None
) -> list[str]:
    """Recursively expand dependency groups, handling include-group references."""
    if visited is None:
        visited = set()

    if group_name in visited:
        warning_msg = (
            f"⚠️  Warning: Circular dependency detected for group "
            f"'{group_name}', skipping"
        )
        print(warning_msg)
        return []

    visited.add(group_name)

    if group_name not in dependency_groups:
        print(f"⚠️  Warning: Group '{group_name}' not found in dependency-groups")
        return []

    expanded_deps = []
    deps = dependency_groups[group_name]

    for dep in deps:
        if isinstance(dep, dict) and "include-group" in dep:
            included_group = dep["include-group"]
            print(f"📎 Including group: {included_group}")
            expanded_deps.extend(
                expand_dependencies(included_group, dependency_groups, visited.copy())
            )
        else:
            expanded_deps.append(str(dep))

    return expanded_deps


def should_use_system_install(tool: str, force_system: bool) -> bool:
    """Determine if --system flag should be used for installation."""
    return force_system or (
        os.getenv("CI") == "true"  # GitHub Actions, GitLab CI, etc.
        or os.getenv("GITHUB_ACTIONS") == "true"  # GitHub Actions specifically
        or not os.getenv("VIRTUAL_ENV")  # Not in a virtual environment
    )


def build_install_command(
    tool: str, expanded_deps: list[str], use_system: bool
) -> list[str]:
    """Build the installation command based on tool and options."""
    if tool == "uv":
        cmd = ["uv", "pip", "install"]
        if use_system:
            cmd.append("--system")
        cmd.extend(expanded_deps)
    elif tool == "pip":
        cmd = ["pip", "install"] + expanded_deps
    else:
        raise ValueError(f"Unsupported tool '{tool}'. Use 'uv' or 'pip'")

    return cmd


def install_single_group(
    group: str, dependency_groups: dict, tool: str, use_system: bool
) -> bool:
    """Install a single dependency group."""
    print(f"\n📦 Installing group: {group}")
    expanded_deps = expand_dependencies(group, dependency_groups)

    if not expanded_deps:
        print(f"ℹ️  No dependencies found for group '{group}'")
        return True

    print(f"📋 Dependencies to install: {len(expanded_deps)}")
    for dep in expanded_deps:
        print(f"  • {dep}")

    try:
        cmd = build_install_command(tool, expanded_deps, use_system)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        success_msg = (
            f"✅ Successfully installed {len(expanded_deps)} dependencies "
            f"from '{group}' group"
        )
        print(success_msg)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install group '{group}': {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def install_groups(tool: str, groups: list[str], force_system: bool = False) -> bool:
    """Install specified dependency groups using the given tool."""
    config = load_pyproject()
    dependency_groups = config.get("dependency-groups", {})

    if not dependency_groups:
        print("⚠️  No dependency-groups found in pyproject.toml")
        return True

    print(f"🔧 Using {tool} to install dependency groups: {', '.join(groups)}")

    use_system = should_use_system_install(tool, force_system)

    if tool == "uv" and use_system:
        print("🌐 Using --system flag for uv (detected CI or no venv)")

    success = True
    for group in groups:
        group_success = install_single_group(group, dependency_groups, tool, use_system)
        success = success and group_success

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install PEP 735 dependency groups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "tool", choices=["uv", "pip"], help="Package management tool to use"
    )
    parser.add_argument("groups", nargs="+", help="Dependency groups to install")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without actually installing",
    )
    parser.add_argument(
        "--system",
        action="store_true",
        help="Force use of --system flag with uv (for CI environments)",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 Dry run mode - showing what would be installed:")
        config = load_pyproject()
        dependency_groups = config.get("dependency-groups", {})

        for group in args.groups:
            print(f"\n📦 Group: {group}")
            expanded_deps = expand_dependencies(group, dependency_groups)
            for dep in expanded_deps:
                print(f"  • {dep}")
        return

    success = install_groups(args.tool, args.groups, force_system=args.system)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
