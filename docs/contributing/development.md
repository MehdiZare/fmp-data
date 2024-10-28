# docs/contributing/development.md
# Development Guide

## Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

## Project Structure

```
fmp_data/
├── fmp_data/          # Main package directory
│   ├── __init__.py    # Package initialization
│   ├── client.py      # Main API client
│   └── exceptions.py  # Custom exceptions
├── tests/             # Test directory
├── docs/              # Documentation
├── pyproject.toml     # Project configuration
└── .pre-commit-config.yaml  # Pre-commit hooks configuration
```

## Version Management

We use `poetry-dynamic-versioning` to automatically manage versions based on git tags. The version number follows [Semantic Versioning](https://semver.org/):

- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- Pre-releases: MAJOR.MINOR.PATCH-alpha.N, -beta.N, -rc.N

Version numbers are automatically generated from git tags and commits.

## Code Style

We use several tools to ensure code quality:

1. **Black**: Code formatting
   ```bash
   poetry run black .
   ```

2. **isort**: Import sorting
   ```bash
   poetry run isort .
   ```

3. **Ruff**: Linting
   ```bash
   poetry run ruff check .
   ```

4. **mypy**: Type checking
   ```bash
   poetry run mypy fmp_data
   ```

Pre-commit hooks will run these checks automatically before each commit.

## Building Documentation

1. Install documentation dependencies:
```bash
poetry install --with docs
```

2. Serve documentation locally:
```bash
poetry run mkdocs serve
```

3. Build documentation:
```bash
poetry run mkdocs build
```
