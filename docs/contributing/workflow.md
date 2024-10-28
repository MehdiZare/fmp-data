# docs/contributing/workflow.md
# Development Workflow

## Git Branch Strategy

We use a simplified Git flow with these main branches:
- `main`: Production-ready code
- `develop`: Integration branch for features
- Feature branches: For new features and changes

### Creating a New Feature Branch

1. Always create your feature branch from `develop`:
```bash
# Update your local develop branch
git checkout develop
git pull origin develop

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/`: New features or enhancements
- `fix/`: Bug fixes
- `docs/`: Documentation changes
- `refactor/`: Code refactoring
- `test/`: Adding or modifying tests

Example:
```bash
git checkout -b feature/add-balance-sheet-endpoint
git checkout -b fix/rate-limit-bug
git checkout -b docs/add-examples
```

## Development Cycle

1. **Make Changes**:
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add balance sheet endpoint"
   ```

   Commit message format:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation
   - `style`: Formatting
   - `refactor`: Code restructuring
   - `test`: Adding tests
   - `chore`: Maintenance

2. **Run Tests & Checks**:
   ```bash
   # Run test suite
   poetry run pytest

   # Run linting
   poetry run pre-commit run --all-files
   ```

3. **Push Changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Creating Pull Requests

1. Go to GitHub repository
2. Click "New Pull Request"
3. Set base branch to `develop`
4. Add description following the template
5. Link related issues
6. Request reviews

## Release Process

We use semantic versioning (MAJOR.MINOR.PATCH):

### 1. Development Releases

For testing during development:
```bash
# Create development release tag
git tag -a v0.1.0-dev.1 -m "Development release v0.1.0-dev.1"
git push origin v0.1.0-dev.1
```

### 2. Alpha/Beta Releases

For early testing:
```bash
# Alpha release
git tag -a v0.1.0-alpha.1 -m "Alpha release v0.1.0-alpha.1"
git push origin v0.1.0-alpha.1

# Beta release
git tag -a v0.1.0-beta.1 -m "Beta release v0.1.0-beta.1"
git push origin v0.1.0-beta.1
```

### 3. Release Candidates

When feature-complete:
```bash
git tag -a v0.1.0-rc.1 -m "Release candidate v0.1.0-rc.1"
git push origin v0.1.0-rc.1
```

### 4. Stable Release

1. Update CHANGELOG.md
2. Create release:
   ```bash
   # Ensure you're on main branch
   git checkout main
   git pull origin main

   # Create stable release tag
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```

### Release Automation

When you push a tag:
1. GitHub Actions builds package
2. Runs test suite
3. Creates GitHub release
4. Publishes to PyPI:
   - Pre-releases go to TestPyPI
   - Stable releases go to PyPI

## Version Numbers

Version format: MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
- `0.1.0-dev.1`: Development version
- `0.1.0-alpha.1`: Alpha release
- `0.1.0-beta.1`: Beta release
- `0.1.0-rc.1`: Release candidate
- `0.1.0`: Stable release

When to increment:
- MAJOR: Incompatible API changes
- MINOR: New features (backwards-compatible)
- PATCH: Bug fixes (backwards-compatible)

## Hotfix Process

For urgent fixes to production:

1. Create hotfix branch from `main`:
   ```bash
   git checkout main
   git checkout -b hotfix/critical-bug
   ```

2. Make fixes and test:
   ```bash
   # Make changes
   git commit -m "fix: critical bug description"

   # Run tests
   poetry run pytest
   ```

3. Create release:
   ```bash
   # Example: if current version is 1.1.0
   git tag -a v1.1.1 -m "Hotfix: critical bug"
   git push origin v1.1.1
   ```

4. Merge back to both `main` and `develop`:
   ```bash
   git checkout main
   git merge hotfix/critical-bug
   git push origin main

   git checkout develop
   git merge hotfix/critical-bug
   git push origin develop
   ```

## Managing Dependencies

1. Adding dependencies:
   ```bash
   # Main dependencies
   poetry add package-name

   # Development dependencies
   poetry add --group dev package-name

   # Documentation dependencies
   poetry add --group docs package-name
   ```

2. Updating dependencies:
   ```bash
   # Update all dependencies
   poetry update

   # Update specific package
   poetry update package-name
   ```

## Documentation Updates

1. Update docs:
   ```bash
   # Serve docs locally
   poetry run mkdocs serve

   # Build docs
   poetry run mkdocs build
   ```

2. API documentation:
   - Add docstrings to all public functions/classes
   - Include examples in docstrings
   - Update reference documentation
