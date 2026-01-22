# docs/contributing/development.md
# Development Guide

## Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --group dev --group docs --group langchain --group mcp
```

4. Install pre-commit hooks:
```bash
uv run pre-commit install
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

We use `hatch-vcs` to automatically manage versions based on git tags. The version number follows [Semantic Versioning](https://semver.org/):

- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- Pre-releases: MAJOR.MINOR.PATCH-alpha.N, -beta.N, -rc.N

Version numbers are automatically generated from git tags and commits.

## Code Style

We use several tools to ensure code quality:

1. **Ruff format**: Code formatting
   ```bash
   uv run ruff format fmp_data tests
   ```

2. **Ruff**: Linting
   ```bash
   uv run ruff check fmp_data tests
   ```

3. **mypy**: Type checking
   ```bash
   uv run mypy fmp_data
   ```

Pre-commit hooks will run these checks automatically before each commit.

## Building Documentation

1. Install documentation dependencies:
```bash
uv sync --group docs
```

2. Serve documentation locally:
```bash
uv run mkdocs serve
```

3. Build documentation:
```bash
uv run mkdocs build
```
