# Repository Guidelines

## Project Structure & Module Organization
- Core library lives in `fmp_data/` with feature areas in subpackages like `company/`, `market/`, `fundamental/`, and `technical/`.
- Integrations are separated: `fmp_data/lc/` for LangChain and `fmp_data/mcp/` for MCP server support.
- Tests are under `tests/unit/` and `tests/integration/`.
- Documentation is in `docs/`, examples in `examples/`, and configuration in `pyproject.toml`.

## Build, Test, and Development Commands
- `make install`: install dependencies (recommended entry point).
- `make check`: run lint, format, typecheck, and tests.
- `make test`: run the test suite.
- `make test-cov`: run tests with coverage report.
- `make fix`: auto-fix format and lint issues.
- `make build`: build the package.
If you prefer direct commands, use `uv run pytest`, `uv run ruff format`, and `uv run mypy fmp_data`.

## Coding Style & Naming Conventions
- Python formatting uses `ruff format` with line length 88.
- Linting and import sorting use `ruff`; type checking uses `mypy`.
- Follow standard Python naming: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Run `make pre-commit` to validate with repo hooks.

## Testing Guidelines
- Framework: `pytest` with `pytest-cov`.
- Unit tests live in `tests/unit/`; integration tests in `tests/integration/`.
- Integration tests require `FMP_TEST_API_KEY`, e.g. `FMP_TEST_API_KEY=... uv run pytest tests/integration/`.
- Coverage should remain above 80%.

## Commit & Pull Request Guidelines
- Commit messages follow Conventional Commits, e.g. `feat(client): add rate limit handling`.
- PRs should include a clear description, pass `make ci`, and update docs for new features.
- Ensure formatting, linting, and type hints are in place before opening a PR.
