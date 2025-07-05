# Release Management

This guide explains how releases are managed for the FMP Data project, including versioning strategy, automated processes, and manual procedures.

## Semantic Versioning

We follow [Semantic Versioning (SemVer)](https://semver.org/) with automated version bumping based on PR labels.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Breaking changes that require user action
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes and minor improvements
- **PRERELEASE**: Alpha, beta, or release candidate versions
- **BUILD**: Build metadata (not used in our releases)

### Version Bumping Rules

| Change Type | PR Label | Version Bump | Example |
|-------------|----------|--------------|---------|
| Breaking Changes | `major` | MAJOR | 1.0.0 → 2.0.0 |
| New Features | `minor` | MINOR | 1.0.0 → 1.1.0 |
| Bug Fixes | `patch` | PATCH | 1.0.0 → 1.0.1 |
| Documentation | `patch` | PATCH | 1.0.0 → 1.0.1 |
| Chores | `patch` | PATCH | 1.0.0 → 1.0.1 |

## Automated Release Process

### GitHub Actions Workflow

Our release process is fully automated using GitHub Actions:

1. **PR Merge**: When a PR is merged to `main`
2. **Label Detection**: Action reads PR labels to determine version bump
3. **Version Calculation**: New version is calculated based on current version + bump type
4. **Git Tagging**: New git tag is created with the version
5. **Release Creation**: GitHub release is created with auto-generated notes
6. **PyPI Publishing**: Package is built and published to PyPI
7. **Documentation**: Updated docs are deployed

### Required PR Labels

**Version Bump Labels** (exactly one required):
- `major`: For breaking changes
- `minor`: For new features
- `patch`: For bug fixes and minor changes

**Additional Labels** (optional):
- `dependencies`: Dependency updates
- `documentation`: Documentation changes
- `enhancement`: Improvements to existing features
- `bug`: Bug fixes
- `feature`: New features

### Example Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Determine Version Bump
        uses: ./.github/actions/version-bump
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Publish
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          poetry config pypi-token.pypi $PYPI_TOKEN
          poetry build
          poetry publish
```

## Manual Release Process

For emergency releases or when automation fails:

### Prerequisites

1. **Permissions**: Maintainer access to repository and PyPI
2. **Environment**: Local development environment set up
3. **Credentials**: PyPI token configured

### Steps

1. **Prepare Release Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release/v1.2.3
   ```

2. **Update Version**
   ```bash
   # Update version in pyproject.toml if needed
   poetry version patch  # or minor/major
   ```

3. **Update Changelog**
   ```bash
   # Update CHANGELOG.md with release notes
   # Include all changes since last release
   ```

4. **Run Quality Checks**
   ```bash
   poetry run pytest
   poetry run black .
   poetry run ruff check .
   poetry run mypy fmp_data
   poetry run mkdocs build --strict
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "chore: prepare release v1.2.3"
   git push origin release/v1.2.3
   ```

6. **Create Release PR**
   - Create PR from release branch to main
   - Add appropriate version label
   - Include release notes in description

7. **Merge and Tag**
   ```bash
   # After PR approval and merge
   git checkout main
   git pull origin main
   git tag v1.2.3
   git push origin v1.2.3
   ```

8. **Build and Publish**
   ```bash
   poetry build
   poetry publish
   ```

9. **Create GitHub Release**
   - Go to GitHub Releases
   - Create release from tag
   - Add release notes
   - Publish release

## Pre-release Process

For alpha, beta, and release candidate versions:

### Creating Pre-releases

```bash
# Alpha release
poetry version prerelease  # 1.0.0a1

# Beta release
poetry version 1.0.0b1

# Release candidate
poetry version 1.0.0rc1
```

### Publishing Pre-releases

```bash
# Build and publish to PyPI
poetry build
poetry publish

# Install pre-release
pip install --pre fmp-data
```

### Pre-release Labels

- `alpha`: Early development version
- `beta`: Feature-complete but may have bugs
- `rc`: Release candidate, final testing phase

## Release Notes

### Automated Generation

Release notes are automatically generated from:
- PR titles and descriptions
- Commit messages
- Issue references
- Breaking change callouts

### Manual Enhancement

Enhance auto-generated notes with:
- **Overview**: High-level summary of changes
- **Highlights**: Key new features or improvements
- **Breaking Changes**: Required user actions
- **Migration Guide**: How to upgrade from previous version
- **Contributors**: Thank contributors

### Example Release Notes

```markdown
# v1.2.0 - Enhanced Market Data Support

## Overview
This release adds comprehensive market intelligence features and improves error handling across all clients.

## ✨ New Features
- Market Intelligence client with sentiment analysis
- Enhanced company search with filtering options
- Async support for all fundamental data endpoints

## 🐛 Bug Fixes
- Fixed rate limiting calculation for concurrent requests
- Resolved memory leak in async client cleanup
- Improved error messages for invalid API responses

## 💥 Breaking Changes
- `MarketClient.get_quotes()` now returns `List[Quote]` instead of `Dict`
- Minimum Python version increased to 3.10

## 📖 Documentation
- Added comprehensive API reference
- Updated getting started guide
- New examples for market intelligence features

## 🏗️ Internal Changes
- Upgraded to Pydantic v2
- Improved test coverage to 95%
- Enhanced CI/CD pipeline

## Contributors
Thanks to @contributor1, @contributor2, and @contributor3 for their contributions!
```

## Version Strategy

### Major Releases (X.0.0)

**When to Release**:
- Breaking API changes
- Major architecture changes
- Dropping support for Python versions
- Significant dependency updates

**Planning**:
- Create milestone for major version
- Gather breaking changes over time
- Provide migration documentation
- Consider deprecation warnings in previous minor versions

### Minor Releases (X.Y.0)

**When to Release**:
- New features
- New API endpoints
- Backward-compatible improvements
- New optional dependencies

**Frequency**: Monthly or when significant features are ready

### Patch Releases (X.Y.Z)

**When to Release**:
- Bug fixes
- Documentation updates
- Security fixes
- Performance improvements

**Frequency**: As needed, typically weekly for active development

## Hotfix Process

For critical security or data corruption bugs:

1. **Create Hotfix Branch**
   ```bash
   git checkout main
   git checkout -b hotfix/security-fix
   ```

2. **Apply Minimal Fix**
   - Fix only the critical issue
   - Avoid unrelated changes
   - Add regression tests

3. **Fast-track Release**
   - Skip normal review process if needed
   - Deploy immediately after testing
   - Notify users through appropriate channels

4. **Post-hotfix Actions**
   - Backport to development branches
   - Update documentation
   - Conduct post-mortem if needed

## Release Checklist

### Pre-release
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number updated
- [ ] Migration guide written (for breaking changes)
- [ ] Security review completed (for major releases)

### Release
- [ ] Git tag created
- [ ] GitHub release published
- [ ] PyPI package published
- [ ] Documentation deployed
- [ ] Release notes published

### Post-release
- [ ] Verify PyPI package installation
- [ ] Test key functionality
- [ ] Monitor for reported issues
- [ ] Update example code if needed
- [ ] Announce release (social media, forums, etc.)

## Rollback Procedures

If a release introduces critical issues:

### PyPI Package
```bash
# Remove problematic version
pip install twine
twine delete --repository pypi fmp-data==1.2.3

# Users should pin to previous version
pip install fmp-data==1.2.2
```

### GitHub Release
1. Mark release as pre-release
2. Add warning to release notes
3. Create patch release with fix

### Communication
- Update GitHub issue/discussion
- Post on social media/forums
- Email affected enterprise users
- Update documentation with workarounds

## Monitoring and Metrics

### Release Health
- PyPI download statistics
- GitHub issue reports
- User feedback and discussions
- Performance monitoring

### Success Metrics
- Time to release (PR merge to PyPI)
- Release frequency
- Bug reports per release
- User adoption rate

## Tools and Infrastructure

### Required Access
- GitHub repository admin
- PyPI package maintainer
- Documentation hosting admin
- CI/CD system access

### Tools Used
- **Poetry**: Dependency management and publishing
- **GitHub Actions**: CI/CD automation
- **PyPI**: Package distribution
- **MkDocs**: Documentation generation
- **Conventional Commits**: Automated changelog generation

## Troubleshooting

### Common Issues

**PyPI Publishing Fails**
```bash
# Check credentials
poetry config --list

# Verify package
poetry check
poetry build
twine check dist/*
```

**Version Conflicts**
```bash
# Check current version
poetry version

# Force version update
poetry version 1.2.3
```

**GitHub Actions Failure**
- Check action logs
- Verify secrets and permissions
- Test workflow locally if possible

For additional help, consult the [Development Guide](development.md) or create an issue.
