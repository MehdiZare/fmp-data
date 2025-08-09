# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

### Testing
```bash
# Run tests with coverage (fast, local development)
make test

# Run all tests for all Python versions and features
make test-all

# Run tests with coverage report
make test-cov

# Run specific feature tests
make test-lang    # Test LangChain features
make test-mcp     # Test MCP features

# Run a single test file
pytest tests/unit/test_client.py

# Run integration tests (requires FMP_TEST_API_KEY)
FMP_TEST_API_KEY=your_test_key pytest tests/integration/
```

### Code Quality
```bash
# Run all quick checks (lint, format, typecheck, test)
make check

# Fix all auto-fixable issues
make fix

# Run linting
make lint

# Check types (core package only, fast)
make typecheck

# Check types for all features
make typecheck-all

# Run security checks
make security

# Run full CI checks locally
make ci
```

### Development Workflow
```bash
# Install development environment
make install

# Quick development cycle (fix, lint, test)
make quick

# Full validation (everything)
make full

# Clean build artifacts and caches
make clean
```

### Building and Publishing
```bash
# Build package
make build

# Build and verify package
make build-check
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
Each domain client inherits from `BaseClient` and is instantiated lazily by the main `FMPDataClient`. The base client handles:
- HTTP requests with retry logic via `tenacity`
- Rate limiting based on API tier
- Response validation using Pydantic models
- Consistent error handling

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

### Code Style
- Uses `ruff` for linting and formatting (replaces black/isort/flake8)
- Type hints are required (enforced by mypy)
- Follow existing patterns in the codebase

### Poetry & UV
- This project uses Poetry for dependency management with UV for fast installs
- Always use `make install` or `uv sync` instead of pip directly
- Lock file (`uv.lock`) ensures reproducible builds

### Pre-commit Hooks
- Automatically run on commit after `make install`
- Include ruff, mypy, and security checks
- Use `make pre-commit` to run manually on all files
