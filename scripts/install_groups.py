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
"""

import argparse
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
        print(
            f"⚠️  Warning: Circular dependency detected "
            f"for group '{group_name}', skipping"
        )
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


def install_groups(tool: str, groups: list[str]) -> bool:
    """Install specified dependency groups using the given tool."""
    config = load_pyproject()
    dependency_groups = config.get("dependency-groups", {})

    if not dependency_groups:
        print("⚠️  No dependency-groups found in pyproject.toml")
        return True

    print(f"🔧 Using {tool} to install dependency groups: {', '.join(groups)}")

    success = True
    for group in groups:
        print(f"\n📦 Installing group: {group}")
        expanded_deps = expand_dependencies(group, dependency_groups)

        if not expanded_deps:
            print(f"ℹ️  No dependencies found for group '{group}'")
            continue

        print(f"📋 Dependencies to install: {len(expanded_deps)}")
        for dep in expanded_deps:
            print(f"  • {dep}")

        # Build command based on tool
        if tool == "uv":
            cmd = ["uv", "pip", "install"] + expanded_deps
        elif tool == "pip":
            cmd = ["pip", "install"] + expanded_deps
        else:
            print(f"❌ Error: Unsupported tool '{tool}'. Use 'uv' or 'pip'")
            return False

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(
                f"✅ Successfully installed "
                f"{len(expanded_deps)} dependencies from '{group}' group"
                f"\n   stdout: {result.stdout}"
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install group '{group}': {e}")
            if e.stdout:
                print(f"   stdout: {e.stdout}")
            if e.stderr:
                print(f"   stderr: {e.stderr}")
            success = False

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

    success = install_groups(args.tool, args.groups)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
