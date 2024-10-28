# scripts/release.py
"""Release management script with secure git operations."""
import re
from pathlib import Path

from git import GitCommandError, Repo


def validate_version_tag(tag: str) -> bool:
    """Validate version tag format."""
    pattern = r"^v\d+\.\d+\.\d+(-[a-zA-Z]+\.\d+)?$"
    return bool(re.match(pattern, tag))


def get_current_version(repo: Repo) -> str:
    """Get current version from latest tag."""
    try:
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        if not tags:
            return "0.0.0"
        latest = tags[-1].name
        if not validate_version_tag(latest):
            return "0.0.0"
        return latest.lstrip("v")
    except GitCommandError:
        return "0.0.0"


def create_new_version(
    current: str, bump_type: str, pre_release: str | None = None
) -> str:
    """Create new version number."""
    major, minor, patch = map(int, current.split("."))

    if bump_type == "major":
        new_version = f"{major + 1}.0.0"
    elif bump_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    if pre_release:
        return f"{new_version}-{pre_release}"
    return new_version


def create_release(bump_type: str, pre_release: str | None = None) -> None:
    """Create a new release with the specified bump type."""
    try:
        repo = Repo(Path.cwd())

        # Ensure working directory is clean
        if repo.is_dirty():
            raise ValueError("Working directory is not clean")

        # Get current version
        current_version = get_current_version(repo)
        new_version = create_new_version(current_version, bump_type, pre_release)
        tag_name = f"v{new_version}"

        if not validate_version_tag(tag_name):
            raise ValueError(f"Invalid version tag format: {tag_name}")

        # Create and push tag
        tag = repo.create_tag(tag_name, message=f"Release {tag_name}", force=False)

        # Push to origin
        repo.remotes.origin.push(tag)
        print(f"Created and pushed tag: {tag_name}")

    except GitCommandError as e:
        print(f"Git error: {e}")
        raise
    except Exception as e:
        print(f"Error creating release: {e}")
        raise


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Version bump type"
    )
    parser.add_argument(
        "--pre-release", choices=["alpha", "beta", "rc"], help="Pre-release identifier"
    )

    args = parser.parse_args()
    create_release(args.bump_type, args.pre_release)


if __name__ == "__main__":
    main()
