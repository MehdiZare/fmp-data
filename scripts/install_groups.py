#!/usr/bin/env python3
"""
PEP 735 Dependency Group Installer for fmp-data
──────────────────────────────────────────────
Install dependency groups from pyproject.toml with support for include-group references.

Usage:
    python scripts/install_groups.py [tool] [group1] [group2] ...

Examples:
    python scripts/install_groups.py uv dev
    python scripts/install_groups.py pip langchain mcp-server test
    python scripts/install_groups.py uv dev --dry-run

Relative path: scripts/install_groups.py
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def load_pyproject_toml() -> dict:
    """Load pyproject.toml configuration."""
    try:
        import tomllib
    except ImportError:
        # Fallback for Python < 3.11
        try:
            import tomli as tomllib
        except ImportError:
            print("❌ Error: tomllib/tomli not available.")
            print("   Install with: pip install tomli")
            sys.exit(1)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ Error: pyproject.toml not found")
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def expand_dependency_group(
    group_name: str, all_groups: dict[str, list], visited: set[str] | None = None
) -> list[str]:
    """
    Recursively expand dependency groups, handling include-group references.

    Args:
        group_name: Name of the dependency group to expand
        all_groups: All available dependency groups from pyproject.toml
        visited: Set of already visited groups to prevent circular dependencies

    Returns:
        List of expanded dependencies
    """
    if visited is None:
        visited = set()

    if group_name in visited:
        print(f"⚠️  Warning: Circular dependency detected for group '{group_name}'")
        return []

    if group_name not in all_groups:
        print(f"⚠️  Warning: Group '{group_name}' not found in dependency-groups")
        return []

    visited.add(group_name)
    expanded_deps = []

    for dep in all_groups[group_name]:
        if isinstance(dep, dict) and "include-group" in dep:
            included_group = dep["include-group"]
            print(f"📎 Including group: {included_group}")
            nested_deps = expand_dependency_group(
                included_group, all_groups, visited.copy()
            )
            expanded_deps.extend(nested_deps)
        else:
            expanded_deps.append(str(dep))

    return expanded_deps


def collect_all_dependencies(groups: list[str], config: dict) -> list[str]:
    """
    Collect and deduplicate dependencies from multiple groups.

    Args:
        groups: List of dependency group names
        config: Loaded pyproject.toml configuration

    Returns:
        List of unique dependencies preserving order
    """
    dependency_groups = config.get("dependency-groups", {})
    all_deps = []

    for group in groups:
        print(f"📦 Processing group: {group}")
        deps = expand_dependency_group(group, dependency_groups)
        all_deps.extend(deps)

    # Remove duplicates while preserving order
    unique_deps = []
    seen = set()
    for dep in all_deps:
        if dep not in seen:
            unique_deps.append(dep)
            seen.add(dep)

    return unique_deps


def build_install_command(tool: str, dependencies: list[str]) -> list[str]:
    """
    Build the installation command for the specified tool.

    Args:
        tool: Package installer ('uv' or 'pip')
        dependencies: List of dependencies to install

    Returns:
        Command list ready for subprocess execution
    """
    if tool == "uv":
        return ["uv", "pip", "install"] + dependencies
    elif tool == "pip":
        return [sys.executable, "-m", "pip", "install"] + dependencies
    else:
        raise ValueError(f"Unsupported tool: {tool}")


def detect_installer() -> str:
    """Detect the best available package installer."""
    if shutil.which("uv"):
        return "uv"
    return "pip"


def main() -> None:
    """Main entry point for the dependency group installer."""
    parser = argparse.ArgumentParser(
        description="Install PEP 735 dependency groups from pyproject.toml"
    )
    parser.add_argument(
        "tool",
        nargs="?",
        choices=["uv", "pip", "auto"],
        default="auto",
        help="Package installer to use (default: auto-detect)",
    )
    parser.add_argument("groups", nargs="*", help="Dependency groups to install")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without actually installing",
    )
    parser.add_argument(
        "--list-groups",
        action="store_true",
        help="List all available dependency groups",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_pyproject_toml()
    dependency_groups = config.get("dependency-groups", {})

    # Handle --list-groups
    if args.list_groups:
        print("📋 Available dependency groups:")
        for group_name, deps in dependency_groups.items():
            print(f"  • {group_name}: {len(deps)} dependencies")
        return

    # Validate input
    if not args.groups:
        print("❌ Error: No dependency groups specified")
        print("Use --list-groups to see available groups")
        sys.exit(1)

    # Detect tool
    tool = detect_installer() if args.tool == "auto" else args.tool
    print(f"🔧 Using {tool} for installation")

    # Collect dependencies
    unique_deps = collect_all_dependencies(args.groups, config)

    if not unique_deps:
        print("⚠️  No dependencies found for specified groups")
        return

    print(f"📦 Found {len(unique_deps)} unique dependencies")

    # Build command
    cmd = build_install_command(tool, unique_deps)

    if args.dry_run:
        print("🔍 Dry run - would execute:")
        print(" ".join(cmd))
        print("\n📋 Dependencies to install:")
        for dep in unique_deps:
            print(f"  • {dep}")
        return

    # Execute installation
    print(f"🚀 Installing {len(unique_deps)} dependencies...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ Installation completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: {tool} not found. Please install it first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
