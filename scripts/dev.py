"""Release management script."""

import sys
from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo


def get_repo() -> Repo:
    """Get git repository instance."""
    try:
        return Repo(Path.cwd())
    except InvalidGitRepositoryError as err:
        raise RuntimeError("Not in a git repository") from err


def get_current_version() -> str:
    """Get current version from latest tag."""
    repo = get_repo()
    try:
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        if not tags:
            return "0.0.0"
        latest = tags[-1].name
        return latest.lstrip("v")
    except GitCommandError:
        return "0.0.0"


def bump_version(version: str, bump_type: str) -> str:
    """Bump version number according to semver."""
    major, minor, patch = map(int, version.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def create_release(bump_type: str, pre_release: str | None = None) -> None:
    """Create a new release with the specified bump type."""
    repo = get_repo()

    try:
        # Get current version
        current = get_current_version()
        new_version = bump_version(current, bump_type)

        # Create tag name
        tag = f"v{new_version}"
        if pre_release:
            tag = f"{tag}-{pre_release}"

        # Create and push tag
        new_tag = repo.create_tag(tag, message=f"Release {tag}", force=False)
        repo.remotes.origin.push(new_tag)

        print(f"Created and pushed tag: {tag}")

    except GitCommandError as e:
        print(f"Git command failed: {e}")
        raise


def main() -> None:
    """Main entry point for release script."""
    import argparse

    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump",
    )
    parser.add_argument(
        "--pre-release",
        choices=["alpha", "beta", "rc"],
        help="Pre-release identifier",
    )

    args = parser.parse_args()

    try:
        create_release(args.bump_type, args.pre_release)
    except Exception as e:
        print(f"Error creating release: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
