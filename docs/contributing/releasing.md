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
   (#203). On every push it also re-validates an already-open release PR:
   ancestry plus REST `mergeable` / `mergeable_state` (retried; fails closed
   on `dirty`, `mergeable` not `true`, or still-`unknown`) must stay clean
   (#207, #213). That mergeability check is the shared composite action
   `.github/actions/check-pr-mergeable`, also used by Guard-Main-Origin
   (#210); Test-Matrix runs its mock matrix on every PR (#212).
3. **Automation token.** Release-PR and Sync-Main-to-Dev prefer the repo
   secret `GH_TOKEN` (a fine-scoped PAT) for `gh pr create` / automation
   pushes so the `pull_request` **opened** event re-triggers Test-Matrix and
   Guard-Main-Origin (#206). If `GH_TOKEN` is unset they fall back to
   `GITHUB_TOKEN`, which can open the PR but will **not** re-fire those
   workflows (GitHub’s anti-recursion rule — unrelated to the Actions
   “read/write” permission toggle). Adding a release label still triggers
   TestPyPI via the `labeled` event either way.
4. Add **exactly one** of `release:major` / `release:minor` / `release:patch`
   to that PR.
5. The **Publish-to-TestPyPI** workflow builds a unique
   `X.Y.Z.devN` version (`N = run_id * 1000 + run_attempt`) for *each* push,
   asserts the sdist metadata matches that version, uploads it, and comments
   the version **and the commit SHA** on the PR. Install the version in the
   latest comment — older comments point at stale artifacts (#204).
6. Merge the release PR into `main` once CI is green and TestPyPI checks out.
7. The **Release** workflow tags, publishes to PyPI, and creates the GitHub
   release.
8. The **Sync-Main-to-Dev** workflow fires on the push to `main`. It checks
   *reachability* (`git merge-base --is-ancestor origin/main origin/dev`), not
   content equality. After a squash-merge the trees match but the histories
   have diverged; the workflow opens a PR that records a history-only merge
   (`merge -s ours`) so the *next* release PR stays MERGEABLE and gets full
   CI (#202). It then enables **auto-merge with a merge commit** so the PR
   lands when Test-Matrix is green — no human babysitting on the happy path.
   **Never squash** that PR (it would recreate the divergence). Concurrent
   main pushes do not cancel an in-flight sync; human WIP on
   `sync/main-to-dev` is not force-pushed away; merge conflicts open a
   tracking issue (#208).

### Why three workflows keep each other honest

| Failure mode | What used to happen | What happens now |
|---|---|---|
| Squash-merge `dev` → `main` | Content matched, sync no-op; next release PR opened CONFLICTING with no CI | Sync opens a reachability PR immediately after the release |
| Release-PR automation | `create-pull-request` with no working-tree changes exited green and created nothing | `gh pr create --base main --head dev`, or a red failure if histories diverged |
| TestPyPI re-run on the same PR | Version keyed on PR number + `skip-existing: true` → first build wins forever | Unique version per run; `skip-existing: false`; sdist version asserted; comment includes commit SHA |

`Guard-Main-Origin` also fails the PR when `mergeable_state=dirty`, when
`mergeable` is not `true` (including empty/JSON-`null`), **or** when
mergeability never leaves `unknown` after retries, so a conflicting,
unproven, or unresolved release PR shows a red X instead of a hole in the
checks list (#207, #213). Both workflows share
`.github/actions/check-pr-mergeable` for that check (#210); Test-Matrix runs
its mock matrix on every PR (#212). Guard checks out the PR **head** (so
CONFLICTING PRs still reach the check) and, when present on the PR base,
overlays the composite action from `origin/<base>` so hotfixes cut from an
older tip cannot omit the contract.

#### Guard base-pin lag for `check-pr-mergeable` (#218)

Guard’s overlay is intentional and hotfix-safe (#210): a head branch that
rewrites or weakens `check.sh` still runs the contract pinned on the PR
**base** (typically `main` for release PRs). The tradeoff is **lag**:

| Workflow | Which action copy runs | When a contract change applies |
|---|---|---|
| **Guard-Main-Origin** (`dev`/`hotfix-*` → `main`) | `origin/<base>` when that path exists; else head (bootstrap). Guard only targets `main`, so base is **always** `main`. | After the change is **merged into `main`** |
| **Release-PR** (push to `dev`) | Tip of the workflow run (checkout of `dev`) | As soon as the change is **on `dev`** |

Implementation: `.github/workflows/guard-main-origin.yml` step “Prefer
mergeability action from PR base” runs
`git checkout origin/${BASE_REF} -- .github/actions/check-pr-mergeable`
when that path exists on the base.

So tightenings such as “require `mergeable=true`” (#213) or explicit
`tostring` extraction (#216) land on Release-PR immediately once they reach
`dev`, but Guard keeps the previous contract until the same change is on
`main` (normally via the next release PR). Operators reading a red/green
mismatch between Guard and Release-PR after a contract change on `dev` only
should check whether `main` still has the older action.

**Pin strategy:** do **not** silently allow head to override base for minor
contract updates. Changing that tradeoff (forward-compatible pin, dual-run,
etc.) is a separate decision; document and review it rather than flipping
the overlay in a hotfix-shaped PR.

### Related automation (not the release PR itself)

- **Dev Release** (`dev-release.yml`) publishes a unique TestPyPI build on
  every push to `dev` (`X.Y.Z.devN` with `N = run_id * 1000 + run_attempt`).
  Re-runs never silently re-serve a previous wheel. Build and publish are
  separate jobs; only publish holds `id-token: write`, behind the `testpypi`
  environment. `workflow_dispatch` is bound to `refs/heads/dev`.
- **Release** (`release.yml`) tags and creates the GitHub Release in a
  `contents: write` build job, then publishes to PyPI from a second job that
  only downloads the hashed artifacts and has `id-token: write` (environment
  `pypi`). Existing tags / releases / PyPI versions fail the job instead of
  being skipped. Release notes are the matching `## [X.Y.Z]` section of
  `CHANGELOG.md` (via `scripts/github_release_notes.py`), not the squash
  commit list (#370). A missing or empty section fails the job.
- External Actions are pinned to full commit SHAs. The PEP 517 frontend
  (`build`) and backend (`hatchling`, `hatch-vcs`) are installed from
  version floors in `.github/requirements-build.txt` (not a hashed lock).
  Publish jobs run `python -m build --no-isolation` so isolation cannot
  pull a different backend than the one just installed.

### Secrets used by release automation

| Secret | Purpose |
|---|---|
| `GH_TOKEN` | Fine-scoped PAT (or App token) for Release-PR / Sync-Main-to-Dev `gh pr create`, automation branch pushes, and sync-PR auto-merge so `pull_request` CI runs on open (#206) and the history-sync PR can land without a babysitter. Not the same as the automatic `GITHUB_TOKEN`. |
| `GITHUB_TOKEN` | Automatic job token; used as fallback and for jobs that must not re-trigger workflows. |
| OIDC / PyPI trusted publishing | Real and Test PyPI uploads (no long-lived PyPI token required when configured). The GitHub environments **must** be named `pypi` and `testpypi` in the matching PyPI / TestPyPI Trusted Publisher entries, or the OIDC exchange will fail. |

### Branch protection notes (sync PR)

- **Protect Dev** requires the Test-Matrix Python jobs (`tests (3.10)` …
  `tests (3.14)`), blocks force-pushes and branch deletion, and allows
  merge/squash/rebase methods. Sync automation always requests a **merge
  commit** via `gh pr merge --auto --merge`.
- **Signed commits are not required on `dev`.** Requiring verified signatures
  forced every automation PR (and most human ones) through admin bypass,
  including the post-release history-sync PR. Quality gates remain the
  status checks; re-enabling signatures needs a signing key in CI first.

### GitHub Actions Workflow (on merge to main)

1. **PR Merge**: When a labeled release PR is merged to `main`
2. **Label Detection**: Action reads PR labels to determine version bump
3. **Version Calculation**: New version is calculated based on current version + bump type
4. **Git Tagging**: New git tag is created with the version
5. **Release Creation**: GitHub release notes are the matching
   `## [X.Y.Z]` CHANGELOG section (`scripts/github_release_notes.py`)
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

### Example Workflow (illustrative shape only)

The live release path lives in `.github/workflows/release.yml`. Do not copy
`skip-existing: true` from older snippets — real releases fail on version
collisions rather than reporting a green no-op.

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
   - Happy path: `release.yml` extracts `## [X.Y.Z]` via
     `scripts/github_release_notes.py` (fail-closed, before tagging).
   - If automation failed, generate the same file locally and publish it:
     ```bash
     python3 scripts/github_release_notes.py \
       --changelog CHANGELOG.md \
       --version 1.2.3 \
       --tag v1.2.3 \
       --out release-notes.md
     gh release create v1.2.3 --notes-file release-notes.md
     ```
   - Fold `## Unreleased` into `## [X.Y.Z] - date` *before* adding a
     `release:*` label. A heading that exists only under Unreleased
     fails the job. Preview with `--version X.Y.Z`.

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

GitHub Release notes are the matching `## [X.Y.Z]` section of
`CHANGELOG.md`, wrapped with install / docs links by
`scripts/github_release_notes.py`. They are **not** the squash commit
list, PR titles, or GitHub autogen.

Before adding a `release:*` label, fold `## Unreleased` into
`## [X.Y.Z] - YYYY-MM-DD` for the version that label will produce.
Preview:

```bash
python3 scripts/github_release_notes.py --version X.Y.Z --tag vX.Y.Z
```

A missing or empty section fails the release job before the tag is
created.

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
