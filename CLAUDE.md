# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

This project has two Makefiles:
- **`Makefile`**: End-user commands (simple, no special tools required)
- **`Makefile.dev`**: Maintainer/developer commands (requires nox, poetry via uvx)

### Testing
```bash
# Run tests (basic)
make test

# Run tests for all Python versions and features (requires nox)
make -f Makefile.dev test-all

# Run specific feature tests
make -f Makefile.dev test-lang    # Test LangChain features
make -f Makefile.dev test-mcp     # Test MCP features

# Run a single test file
pytest tests/unit/test_client.py

# Run integration tests (requires FMP_TEST_API_KEY)
FMP_TEST_API_KEY=your_test_key pytest tests/integration/

# Run smoke tests (quick validation)
make -f Makefile.dev smoke
```

### Code Quality
```bash
# Run linting
make lint

# Check code formatting
make format

# Fix all auto-fixable issues
make fix

# Check types for all features (requires nox)
make -f Makefile.dev typecheck-all

# Run full CI checks locally (requires nox)
make -f Makefile.dev ci

# Audit dependencies for security issues
make -f Makefile.dev deps-audit
```

### Development Workflow
```bash
# Install package with all features
make install

# Install with MCP server support only
make install-mcp

# Update all dependencies
make update

# Clean build artifacts and caches
make clean
```

### Building and Publishing (Maintainers)
```bash
# Build package
make -f Makefile.dev build

# Build and verify package with twine
make -f Makefile.dev build-check

# Publish to Test PyPI
make -f Makefile.dev publish-test

# Publish to PyPI
make -f Makefile.dev publish

# List all available nox sessions
make -f Makefile.dev nox-list
```

### Documentation
```bash
# Build documentation
make -f Makefile.dev docs

# Serve documentation locally
make -f Makefile.dev docs-serve
```

## Architecture Overview

### Core Structure
The codebase follows a modular client architecture where each financial data domain has its own dedicated client module:

```
fmp_data/
├── client.py              # Main FMPDataClient that aggregates all sub-clients
├── base.py               # BaseClient with core HTTP/retry logic
├── config.py             # Configuration models (ClientConfig, LoggingConfig, etc.)
├── exceptions.py         # Custom exception hierarchy
├── rate_limit.py         # Rate limiting implementation
├── logger.py             # Logging infrastructure
│
├── company/              # Company information endpoints
├── market/               # Market data endpoints
├── fundamental/          # Financial statements
├── technical/            # Technical indicators
├── intelligence/         # Market intelligence & news
├── institutional/        # Institutional holdings & insider trading
├── investment/           # ETF & mutual fund data
├── alternative/          # Crypto, forex, commodities
├── economics/            # Economic indicators
│
├── lc/                   # LangChain integration (optional)
└── mcp/                  # MCP server integration (optional)
```

### Client Initialization Pattern
Each domain client is an `EndpointGroup` wrapper around a shared `BaseClient` and is instantiated lazily by the main `FMPDataClient`. The base client handles:
- HTTP requests with retry logic via `tenacity` (exponential backoff: configurable attempts, default=3; 4-10 second waits)
- Rate limiting based on API tier (configurable daily limit, requests per second/minute)
- Response validation using Pydantic models
- Consistent error handling with custom exceptions

### Retry and Rate Limiting
The `BaseClient` uses `tenacity` for automatic retries on transient failures:
- Retries on `TimeoutException`, `NetworkError`, `HTTPStatusError`
- Exponential backoff: multiplier=1, min=4s, max=10s
- Configurable maximum attempts (default=3)

Rate limiting is handled by `FMPRateLimiter` with configurable quotas per API tier.

### Endpoint Definition Pattern
Each domain module follows this structure:
- `client.py` - The client class with methods for each endpoint
- `endpoints.py` - Endpoint definitions (paths, parameters)
- `models.py` - Pydantic models for responses
- `mapping.py` - Maps endpoints to their response models
- `schema.py` - Additional validation schemas

### Optional Features
The project uses lazy imports for optional dependencies:
- **LangChain Integration** (`fmp_data.lc`): Vector store for semantic search of endpoints
- **MCP Server** (`fmp_data.mcp`): Model Context Protocol server for AI assistants

These are only imported when accessed, preventing import errors if extras aren't installed.

## Exception Hierarchy

Custom exceptions for error handling (all in `fmp_data/exceptions.py`):

```python
FMPError                  # Base exception for all FMP API errors
├── RateLimitError        # 429 - includes retry_after attribute
├── AuthenticationError   # 401 - invalid or missing API key
├── ValidationError       # 400 - invalid request parameters
└── ConfigError           # Configuration errors
```

All exceptions include `message`, `status_code`, and `response` attributes.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FMP_API_KEY` | Yes | Main API key for FMP API access |
| `FMP_TEST_API_KEY` | For tests | API key for integration tests |
| `FMP_BASE_URL` | No | Override default API base URL |
| `FMP_TIMEOUT` | No | Request timeout in seconds (default: 30) |
| `FMP_MAX_RETRIES` | No | Max retry attempts (default: 3) |

## Important Development Notes

### API Key Management
- Use `FMP_API_KEY` environment variable for the main API key
- Use `FMP_TEST_API_KEY` for integration tests
- Never commit API keys to the repository

### Testing Strategy
- Unit tests mock HTTP responses and test business logic
- Integration tests use VCR.py cassettes to record/replay API calls
- Coverage target is 80% (excluding predefined endpoints)
- Run `make test` frequently during development
- Use `make -f Makefile.dev test-all` for comprehensive cross-version testing via nox

### Code Style
- Uses `ruff` for linting and formatting (replaces black/isort/flake8)
- Type hints are required (enforced by mypy)
- Follow existing patterns in the codebase

### Dependency Management
- This project uses UV for dependency management and fast installs
- Lock file (`uv.lock`) ensures reproducible builds
- Use `make install` or `uv sync` instead of pip directly
- Poetry is used only for publishing (via `uvx poetry`)

### Pre-commit Hooks
- Automatically run on commit after `make install`
- Include ruff, mypy, and security checks
- Use `pre-commit run --all-files` to run manually on all files
- Use `make -f Makefile.dev pre-commit-update` to update hooks
