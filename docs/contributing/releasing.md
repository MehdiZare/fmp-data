# Release Management

This guide explains how releases are managed for the FMP Data project, including versioning strategy, automated processes, and manual procedures.

## Semantic Versioning

We follow [Semantic Versioning (SemVer)](https://semver.org/) with automated version bumping based on PR labels.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Breaking changes that require user action
- **MINOR**: New features and intentional public API/schema changes that remain source-compatible
- **PATCH**: Bug fixes and minor improvements
- **PRERELEASE**: Alpha, beta, or release candidate versions
- **BUILD**: Build metadata (not used in our releases)

### Version Bumping Rules

| Change Type | PR Label | Version Bump | Example |
|-------------|----------|--------------|---------|
| Breaking Changes | `release:major` | MAJOR | 1.0.0 → 2.0.0 |
| New Features / Public type changes | `release:minor` | MINOR | 1.0.0 → 1.1.0 |
| Bug Fixes | `release:patch` | PATCH | 1.0.0 → 1.0.1 |
| Documentation | `release:patch` | PATCH | 1.0.0 → 1.0.1 |
| Chores | `release:patch` | PATCH | 1.0.0 → 1.0.1 |

## Automated Release Process

### Happy path (dev → main)

1. Land work on `dev` as usual.
2. The **Release-PR** workflow runs on every push to `dev` and opens (or
   reuses) a PR with head `dev` and base `main`. It fails loudly if `main` is
   not an ancestor of `dev` — it never reports success for work it did not do
   (#203).
3. Add **exactly one** of `release:major` / `release:minor` / `release:patch`
   to that PR.
4. The **Publish-to-TestPyPI** workflow builds a unique
   `X.Y.Z.dev{run_id}{run_attempt}` version for *each* push, uploads it, and
   comments the version **and the commit SHA** on the PR. Install the version
   in the latest comment — older comments point at stale artifacts (#204).
5. Merge the release PR into `main` once CI is green and TestPyPI checks out.
6. The **Release** workflow tags, publishes to PyPI, and creates the GitHub
   release.
7. The **Sync-Main-to-Dev** workflow fires on the push to `main`. It checks
   *reachability* (`git merge-base --is-ancestor origin/main origin/dev`), not
   content equality. After a squash-merge the trees match but the histories
   have diverged; the workflow opens a PR that records a history-only merge
   (`merge -s ours`) so the *next* release PR stays MERGEABLE and gets full
   CI (#202). **Merge that sync PR with a merge commit** — squashing it would
   recreate the divergence.

### Why three workflows keep each other honest

| Failure mode | What used to happen | What happens now |
|---|---|---|
| Squash-merge `dev` → `main` | Content matched, sync no-op; next release PR opened CONFLICTING with no CI | Sync opens a reachability PR immediately after the release |
| Release-PR automation | `create-pull-request` with no working-tree changes exited green and created nothing | `gh pr create --base main --head dev`, or a red failure if histories diverged |
| TestPyPI re-run on the same PR | Version keyed on PR number + `skip-existing: true` → first build wins forever | Unique version per run; `skip-existing: false`; comment includes commit SHA |

`Guard-Main-Origin` also fails the PR when `mergeable_state=dirty`, so a
conflicting release PR shows a red X instead of a hole in the checks list.

### GitHub Actions Workflow (on merge to main)

1. **PR Merge**: When a labeled release PR is merged to `main`
2. **Label Detection**: Action reads PR labels to determine version bump
3. **Version Calculation**: New version is calculated based on current version + bump type
4. **Git Tagging**: New git tag is created with the version
5. **Release Creation**: GitHub release is created with auto-generated notes
6. **PyPI Publishing**: Package is built and published to PyPI
7. **History sync**: Sync-Main-to-Dev restores `main` as an ancestor of `dev`

### Required PR Labels

**Version Bump Labels** (exactly one required):
- `release:major`: For breaking changes
- `release:minor`: For new features and intentional public type/schema changes
- `release:patch`: For bug fixes and minor changes

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
  pull_request:
    types: [closed]
    branches: [ main ]

jobs:
  release:
    if: |
      github.event.pull_request.merged == true &&
      (contains(github.event.pull_request.labels.*.name, 'release:major') ||
       contains(github.event.pull_request.labels.*.name, 'release:minor') ||
       contains(github.event.pull_request.labels.*.name, 'release:patch'))
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6.0.2
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.14'

      - name: Install uv
        uses: astral-sh/setup-uv@v8.0.0

      - name: Build distribution
        run: python -m build --wheel --sdist

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@v1.13.0
        with:
          packages-dir: dist/
          skip-existing: true
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

2. **Confirm Release Version (Tag-based)**
   ```bash
   # Version is derived from git tags via hatch-vcs (e.g. v2.0.0)
   git describe --tags --abbrev=0
   ```

3. **Update Changelog**
   ```bash
   # Update CHANGELOG.md with release notes
   # Include all changes since last release
   ```

4. **Run Quality Checks**
   ```bash
   uv run pytest
   uv run ruff format --check fmp_data tests
   uv run ruff check fmp_data tests
   uv run mypy fmp_data
   uv run mkdocs build --strict
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "chore: prepare release v1.2.3"
   git push origin release/v1.2.3
   ```

6. **Create Release PR**
   - Create PR from release branch to main
   - Add exactly one version label: `release:major`, `release:minor`, or `release:patch`
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
   uv build --wheel --sdist
   uv publish --token "$PYPI_TOKEN"
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
git tag v1.0.0a1
git push origin v1.0.0a1

# Beta release
git tag v1.0.0b1
git push origin v1.0.0b1

# Release candidate
git tag v1.0.0rc1
git push origin v1.0.0rc1
```

### Publishing Pre-releases

```bash
# Build and publish to PyPI
uv build --wheel --sdist
uv publish --token "$PYPI_TOKEN"

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
- [ ] Release tag prepared
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
- **uv**: Dependency management, builds, and publishing
- **hatch-vcs**: Tag-based versioning
- **GitHub Actions**: CI/CD automation
- **PyPI**: Package distribution
- **MkDocs**: Documentation generation
- **Conventional Commits**: Automated changelog generation

## Troubleshooting

### Common Issues

**PyPI Publishing Fails**
```bash
# Check credentials
uv publish --dry-run --token "$PYPI_TOKEN"

# Verify package
uv build --wheel --sdist
uv run twine check dist/*
```

**Version Conflicts**
```bash
# Check current version
git describe --tags --abbrev=0

# Force version update
git tag v1.2.3
```

**GitHub Actions Failure**
- Check action logs
- Verify secrets and permissions
- Test workflow locally if possible

For additional help, consult the [Development Guide](development.md) or create an issue.
