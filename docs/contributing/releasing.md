# Release Process with Dynamic Versioning

## Version Management

We use `poetry-dynamic-versioning` to automatically manage versions based on git tags. The version number follows [Semantic Versioning](https://semver.org/):

- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- Pre-releases: MAJOR.MINOR.PATCH-alpha.N, -beta.N, -rc.N
- Development versions: MAJOR.MINOR.PATCH.devN+HASH

## Creating a Release

1. Ensure all changes are committed:
```bash
git status
```

2. Create a new release:
```bash
# For a stable release
poetry run python scripts/release.py 1.0.0

# For a pre-release
poetry run python scripts/release.py 1.0.0 --pre-release alpha
```

This will:
- Create a git tag (e.g., v1.0.0 or v1.0.0-alpha.1)
- Push the tag to origin
- Build the package with the correct version
- Publish to PyPI (stable) or TestPyPI (pre-release)

## Version Patterns

- Stable Release: `v1.0.0`
  - Results in version: `1.0.0`
- Pre-release: `v1.0.0-alpha.1`
  - Results in version: `1.0.0-alpha.1`
- Development: Any commit after a tag
  - Results in version like: `1.0.0.dev2+abc123`

## Environment Setup

1. Set up PyPI credentials:
```bash
poetry config pypi-token.pypi your-token
poetry config pypi-token.testpypi your-test-token
```

2. Configure git:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## CI/CD Integration

Our GitHub Actions workflows automatically:
1. Build and test the package
2. Publish to TestPyPI for pre-releases
3. Publish to PyPI for stable releases

## Development Workflow

1. Make your changes
2. Update CHANGELOG.md
3. Create release:
```bash
# For development testing
poetry run python scripts/release.py 1.0.0 --pre-release alpha

# For stable release
poetry run python scripts/release.py 1.0.0
```

The package version will automatically be determined from the git tag, and any commits after a tag will result in development versions.
