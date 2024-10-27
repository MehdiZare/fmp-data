# Contributing to FMP Data

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. Install Poetry (if you haven't already):
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

## Development Workflow

1. Create a new branch:
```bash
git checkout -b feature-name
```

2. Make your changes and ensure all checks pass:
```bash
# Format code
poetry run black .
poetry run isort .

# Run linters
poetry run pre-commit run --all-files

# Run tests
poetry run pytest
```

3. Commit your changes:
```bash
git add .
git commit -m "Description of changes"
```

The pre-commit hooks will automatically run on commit and ensure code quality.

## Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- ruff for linting
- mypy for type checking
- pytest for testing

All configurations are in `pyproject.toml` and `.pre-commit-config.yaml`.

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fmp_data

# Run specific test
poetry run pytest fmp_data/tests/test_specific.py
```

## Making a Pull Request

1. Push your changes to your fork
2. Create a pull request from your branch
3. Ensure all checks pass
4. Wait for review

## Questions?

Feel free to open an issue for any questions or concerns.
