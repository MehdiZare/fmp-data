# Contributing to FMP Data

Welcome! We appreciate your interest in contributing to the FMP Data project. This guide will help you get started with development, testing, and contributing to the codebase.

## Quick Links

- **[Development Setup](development.md)**: Set up your development environment
- **[Testing Guide](testing.md)**: Learn how to run and write tests
- **[Workflow Guide](workflow.md)**: Understand our development workflow
- **[Releasing Guide](releasing.md)**: How releases are managed

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Git for version control

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fmp-data.git
   cd fmp-data
   ```

2. **Install Dependencies**
   ```bash
   poetry install --with dev,docs,test
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   poetry run pre-commit install
   ```

4. **Run Tests to Verify Setup**
   ```bash
   poetry run pytest
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Code Style**: We use Black, isort, and Ruff for code formatting and linting
2. **Type Hints**: All functions must have accurate type hints
3. **Documentation**: Update docstrings and include relative file paths
4. **Tests**: Add or update tests for your changes

### Running Quality Checks

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy fmp_data

# Run tests
poetry run pytest --cov=fmp_data
```

### Submitting Changes

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**
   - Use clear, descriptive titles
   - Include detailed descriptions
   - Reference any related issues
   - Add appropriate labels for semantic versioning

## Coding Standards

### Python Code Style

- **Python Version**: Use Python 3.10+ syntax and features
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Include relative file paths in docstrings
- **Error Handling**: Use appropriate exception types
- **Logging**: Use structured logging with appropriate levels

### Example Code Structure

```python
# fmp_data/example/client.py
from __future__ import annotations

from typing import Any
from pydantic import BaseModel

from fmp_data.base import EndpointGroup
from fmp_data.example.models import ExampleModel


class ExampleClient(EndpointGroup):
    """
    Example client for demonstration.

    Relative path: fmp_data/example/client.py
    """

    def get_example_data(self, symbol: str) -> list[ExampleModel]:
        """
        Get example data for a symbol.

        Args:
            symbol: The stock symbol to query

        Returns:
            List of example model instances

        Raises:
            ValidationError: If symbol is invalid
            RateLimitError: If rate limit is exceeded
        """
        endpoint = self._endpoints.example_data
        return self._client.request(endpoint, symbol=symbol)
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Always include complete type information
- **Examples**: Provide usage examples in docstrings
- **File Paths**: Include relative paths in module docstrings

## Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API interactions (require test API key)
- **Mock Tests**: Use mock responses for external dependencies

### Writing Tests

```python
# tests/test_example.py
import pytest
from unittest.mock import Mock

from fmp_data import FMPDataClient
from fmp_data.exceptions import ValidationError


class TestExampleClient:
    """Test suite for ExampleClient."""

    def test_get_example_data_success(self, mock_client):
        """Test successful data retrieval."""
        # Test implementation
        pass

    def test_get_example_data_invalid_symbol(self, mock_client):
        """Test error handling for invalid symbols."""
        with pytest.raises(ValidationError):
            mock_client.example.get_example_data("INVALID")
```

## Pull Request Guidelines

### PR Title Format

Use conventional commit format for PR titles:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for test additions/changes
- `chore:` for maintenance tasks

### PR Labels

Add appropriate labels for semantic versioning:

- `major`: Breaking changes (bumps major version)
- `minor`: New features (bumps minor version)
- `patch`: Bug fixes (bumps patch version)

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated (if applicable)
```

## Code Review Process

1. **Automated Checks**: GitHub Actions will run tests, linting, and type checking
2. **Peer Review**: At least one maintainer review required
3. **Documentation**: Ensure all changes are properly documented
4. **Testing**: Verify test coverage meets requirements

## Release Process

Releases are automated using semantic versioning based on PR labels:

- **Patch**: Bug fixes and minor updates
- **Minor**: New features and improvements
- **Major**: Breaking changes

See our [Releasing Guide](releasing.md) for more details.

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check existing documentation first
- **Code Examples**: Look at the `examples/` directory

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive in all interactions
- Focus on the technical merits of contributions
- Help newcomers and share knowledge
- Follow our community guidelines

Thank you for contributing to FMP Data! 🚀
