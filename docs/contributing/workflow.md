# Workflow Guide

## Development Workflow

This guide explains our development workflow, branching strategy, and collaboration processes.

## Branching Strategy

We use a simplified Git Flow workflow:

### Main Branches

- **`main`**: Production-ready code, always stable
- **`develop`**: Integration branch for features (if needed for complex releases)

### Feature Branches

- **`feature/feature-name`**: New features
- **`fix/issue-description`**: Bug fixes
- **`docs/documentation-update`**: Documentation changes
- **`chore/maintenance-task`**: Maintenance tasks

### Branch Naming Conventions

```bash
# Features
feature/add-market-indicators
feature/improve-error-handling

# Bug fixes
fix/rate-limit-calculation
fix/async-client-memory-leak

# Documentation
docs/api-reference-update
docs/getting-started-guide

# Maintenance
chore/update-dependencies
chore/refactor-logging
```

## Development Process

### 1. Planning and Issue Creation

1. **Check Existing Issues**: Search for similar requests or bugs
2. **Create Detailed Issues**: Include requirements, expected behavior, and acceptance criteria
3. **Get Alignment**: Discuss approach for significant changes

### 2. Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature
   ```

2. **Implement Changes**
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation
   - Commit frequently with clear messages

3. **Keep Branch Updated**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### 3. Code Quality Checks

Run all checks before pushing:

```bash
# Formatting
poetry run black .
poetry run isort .

# Linting
poetry run ruff check .

# Type checking
poetry run mypy fmp_data

# Tests
poetry run pytest --cov=fmp_data

# Documentation
poetry run mkdocs build --strict
```

### 4. Pull Request Process

1. **Push Feature Branch**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create Pull Request**
   - Use descriptive title with conventional commit format
   - Fill out PR template completely
   - Add appropriate labels for semantic versioning
   - Request reviews from maintainers

3. **Address Review Feedback**
   - Make requested changes
   - Respond to comments
   - Keep discussion focused and constructive

4. **Merge Process**
   - Squash and merge for clean history
   - Delete feature branch after merge

## Commit Message Guidelines

### Conventional Commits Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Test additions or modifications
- **chore**: Maintenance tasks

### Examples

```bash
feat(client): add async support for all endpoints

fix(market): resolve rate limiting calculation bug

docs(api): update company client documentation

test(fundamental): add integration tests for financial statements

chore(deps): update httpx to latest version
```

## Code Review Standards

### Review Checklist

**Functionality**
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed

**Code Quality**
- [ ] Follows project coding standards
- [ ] Type hints are complete and accurate
- [ ] Documentation is clear and helpful
- [ ] No code duplication or over-engineering

**Testing**
- [ ] Adequate test coverage
- [ ] Tests are meaningful and well-structured
- [ ] Integration tests for API changes
- [ ] Mock usage is appropriate

**Documentation**
- [ ] Docstrings updated
- [ ] API documentation reflects changes
- [ ] Examples are provided where helpful
- [ ] CHANGELOG updated if needed

### Review Process

1. **Automated Checks**: GitHub Actions must pass
2. **Peer Review**: At least one maintainer approval required
3. **Discussion**: Address feedback constructively
4. **Final Review**: Ensure all concerns are resolved

## Release Workflow

### Semantic Versioning

We use automated semantic versioning based on PR labels:

- **major**: Breaking changes (v1.0.0 → v2.0.0)
- **minor**: New features (v1.0.0 → v1.1.0)
- **patch**: Bug fixes (v1.0.0 → v1.0.1)

### Release Process

1. **PR Labeling**: Add appropriate version labels to PRs
2. **Automated Release**: GitHub Actions handles versioning and publishing
3. **Release Notes**: Generated automatically from PR descriptions
4. **Distribution**: Published to PyPI automatically

## Collaboration Guidelines

### Communication

- **Be Clear**: Use precise language in issues and PRs
- **Be Respectful**: Maintain professional and welcoming tone
- **Be Helpful**: Assist newcomers and share knowledge
- **Be Patient**: Allow time for review and discussion

### Issue Management

- **Triage**: Label issues appropriately
- **Prioritization**: Focus on critical bugs and high-impact features
- **Assignment**: Assign issues to appropriate contributors
- **Tracking**: Update progress and status regularly

### Documentation Maintenance

- **Keep Current**: Update docs with code changes
- **Examples**: Provide practical usage examples
- **Clarity**: Write for users at different experience levels
- **Organization**: Maintain logical structure and navigation

## Tools and Automation

### GitHub Actions

- **CI/CD**: Automated testing, linting, and type checking
- **Release**: Automated versioning and PyPI publishing
- **Documentation**: Automated docs building and deployment

### Pre-commit Hooks

- **Code Formatting**: Black and isort
- **Linting**: Ruff
- **Type Checking**: mypy
- **Security**: Safety checks

### Development Dependencies

```bash
# Install all development dependencies
poetry install --with dev,docs,test

# Update dependencies
poetry update

# Add new dependency
poetry add package-name
poetry add --group dev package-name  # Development only
```

## Troubleshooting Common Issues

### Environment Setup

```bash
# Reset environment
poetry env remove python
poetry install

# Clear cache
poetry cache clear --all .
```

### Git Issues

```bash
# Sync with main
git fetch origin
git rebase origin/main

# Fix merge conflicts
git rebase --continue

# Reset branch
git reset --hard origin/main
```

### Testing Issues

```bash
# Run specific tests
poetry run pytest tests/test_client.py -v

# Debug failing tests
poetry run pytest tests/test_client.py::test_function_name -s

# Update test snapshots
poetry run pytest --snapshot-update
```

## Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Discord/Slack**: Real-time chat (if available)
- **Documentation**: Check existing guides and API docs
- **Issues**: Report bugs or request clarification
