# Contributing to FMP Data

Thank you for your interest in contributing to FMP Data! This guide will help you get started with development.

## Development Setup

### Prerequisites
- Python 3.10-3.14
- UV (recommended) or pip
- Git

### Setting Up Your Development Environment

1. **Clone the repository:**
```bash
git clone https://github.com/MehdiZare/fmp-data.git
cd fmp-data
```

2. **Install UV (recommended):**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **Install dependencies:**
```bash
# Quick setup with make
make install

# Or manually with UV
uv sync --group dev --group docs --group langchain --group mcp
pre-commit install
```

## Development Workflow

### Quick Commands

The project includes a comprehensive Makefile for common tasks:

```bash
make check       # Run all quick checks (lint, format, typecheck, test)
make fix         # Auto-fix all fixable issues
make test        # Run tests
make test-cov    # Run tests with coverage report
make ci          # Run full CI checks locally
```

### Manual Commands

If you prefer running commands directly:

```bash
# Format code
uv run ruff format fmp_data tests

# Fix linting issues
uv run ruff check --fix fmp_data tests

# Run type checking
uv run mypy fmp_data

# Run tests
uv run pytest

# Run tests with coverage (coverage is collected in the dedicated CI job)
uv run pytest --cov=fmp_data --cov-report=html
```

### Creating a Feature Branch

1. Create a new branch from `main`:
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure all checks pass:
```bash
# Quick validation
make check

# Or comprehensive validation
make ci
```

3. Commit your changes:
```bash
git add .
git commit -m "feat: description of your feature"
```

Pre-commit hooks will automatically run to ensure code quality.

## Code Style

This project uses:
- **ruff** for linting and import sorting (replaces flake8, isort)
- **ruff format** for code formatting
- **mypy** for type checking
- **pytest** for testing
- **pre-commit** for git hooks

All configurations are in `pyproject.toml` and `.pre-commit-config.yaml`.

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage (coverage is collected in the dedicated CI job)
make test-cov

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run tests for specific features
make test-lang    # LangChain tests
make test-mcp     # MCP server tests

# Run tests in watch mode (requires pytest-watch)
make test-watch
```

### Integration Tests

Integration tests require an API key:
```bash
FMP_TEST_API_KEY=your_test_key uv run pytest tests/integration/
```

## Type Checking

```bash
# Check core package only (fast)
make typecheck

# Check all features
make typecheck-all

# Check specific features
make typecheck-lang    # LangChain
make typecheck-mcp     # MCP server
```

## Making a Pull Request

1. **Ensure all checks pass:**
```bash
make ci
```

2. **Push your changes:**
```bash
git push origin feature/your-feature-name
```

3. **Create a pull request:**
   - Go to the repository on GitHub
   - Click "New pull request"
   - Select your branch
   - Fill in the PR template
   - Ensure all CI checks pass

### PR Requirements

- All tests must pass
- Code coverage should remain above 80%
- Code must be formatted and pass linting
- Type hints are required for new code
- Documentation should be updated for new features
- Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/)

## Commit Message Format

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

Examples:
```bash
feat(mcp): add tool discovery functionality
fix(client): handle rate limit errors properly
docs: update MCP server documentation
test(company): add tests for profile endpoint
```

## Project Structure

```
fmp_data/
├── client.py              # Main FMPDataClient
├── base.py               # BaseClient with HTTP/retry logic
├── config.py             # Configuration models
├── exceptions.py         # Custom exceptions
├── rate_limit.py         # Rate limiting
├── logger.py             # Logging infrastructure
│
├── company/              # Company data endpoints
├── market/               # Market data endpoints
├── fundamental/          # Financial statements
├── technical/            # Technical indicators
├── intelligence/         # News and intelligence
├── institutional/        # Institutional data
├── investment/           # ETF/mutual fund data
├── alternative/          # Crypto/forex/commodities
├── economics/            # Economic indicators
│
├── lc/                   # LangChain integration
└── mcp/                  # MCP server integration
```

## Development Tips

### Using UV for Dependency Management

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --group dev package-name

# Update dependencies
make deps-update

# Check for outdated packages
make deps-check
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit. To run manually:
```bash
make pre-commit

# Update hooks
make pre-commit-update
```

### Building the Package

```bash
# Build package
make build

# Build and verify
make build-check
```

## Getting Help

If you have questions or need help:
1. Check existing [issues](https://github.com/MehdiZare/fmp-data/issues)
2. Read the [documentation](./docs)
3. Open a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
