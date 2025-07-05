# Development Makefile for fmp-data
# =====================================
# Quick commands for common development tasks

.PHONY: help install clean test lint format typecheck security docs
.PHONY: test-all typecheck-all ci pre-commit fix check-all
.PHONY: build publish-test publish smoke

# Default target
.DEFAULT_GOAL := help

# Colors for output
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
RESET := \033[0m

# ══════════════════════════════════════════════════════════════════════════
# Help and Setup
# ══════════════════════════════════════════════════════════════════════════

help: ## Show this help message
	@echo "$(BOLD)$(BLUE)fmp-data Development Commands$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)🚀 Quick Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)💡 Examples:$(RESET)"
	@echo "  $(YELLOW)make check$(RESET)           # Run all checks quickly"
	@echo "  $(YELLOW)make fix$(RESET)             # Fix all auto-fixable issues"
	@echo "  $(YELLOW)make test$(RESET)            # Run tests"
	@echo "  $(YELLOW)make typecheck$(RESET)       # Check types (core only)"
	@echo "  $(YELLOW)make ci$(RESET)              # Run full CI checks"

install: ## Install all dependencies for development
	@echo "$(BOLD)$(BLUE)🔧 Installing development environment...$(RESET)"
	uv sync --group dev --group docs --group langchain --group mcp-server
	pre-commit install
	pre-commit install --hook-type pre-push
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

clean: ## Clean build artifacts and caches
	@echo "$(BOLD)$(YELLOW)🧹 Cleaning up...$(RESET)"
	uv run nox -s clean
	@echo "$(GREEN)✅ Cleanup completed!$(RESET)"

# ══════════════════════════════════════════════════════════════════════════
# Quick Development Checks (Fast, for frequent use)
# ══════════════════════════════════════════════════════════════════════════

lint: ## Run linting checks (fast)
	@echo "$(BOLD)$(MAGENTA)🔍 Running linting...$(RESET)"
	uv run ruff check fmp_data tests

format: ## Check code formatting (fast)
	@echo "$(BOLD)$(MAGENTA)📝 Checking formatting...$(RESET)"
	uv run ruff format --check fmp_data tests

typecheck: ## Run type checking on core package (fast)
	@echo "$(BOLD)$(MAGENTA)🔬 Type checking core package...$(RESET)"
	uv run mypy fmp_data --exclude "fmp_data/(lc|mcp)/.*"

test: ## Run tests (fast)
	@echo "$(BOLD)$(MAGENTA)🧪 Running tests...$(RESET)"
	uv run pytest -q

security: ## Run security checks
	@echo "$(BOLD)$(MAGENTA)🔒 Running security checks...$(RESET)"
	uv run nox -s security

# ══════════════════════════════════════════════════════════════════════════
# Auto-fix Commands
# ══════════════════════════════════════════════════════════════════════════

fix: ## Fix all auto-fixable issues
	@echo "$(BOLD)$(CYAN)🔧 Auto-fixing issues...$(RESET)"
	@echo "$(YELLOW)  Fixing imports and formatting...$(RESET)"
	uv run ruff check --fix fmp_data tests
	uv run ruff format fmp_data tests
	@echo "$(GREEN)✅ Auto-fixes completed!$(RESET)"

fix-imports: ## Fix import sorting only
	@echo "$(BOLD)$(CYAN)📦 Fixing imports...$(RESET)"
	uv run ruff check --fix --select I fmp_data tests

fix-format: ## Fix code formatting only
	@echo "$(BOLD)$(CYAN)📝 Fixing formatting...$(RESET)"
	uv run ruff format fmp_data tests

# ══════════════════════════════════════════════════════════════════════════
# Comprehensive Checks (Thorough, for CI/pre-commit)
# ══════════════════════════════════════════════════════════════════════════

check: lint format typecheck test ## Run all quick checks
	@echo "$(GREEN)✅ All quick checks passed!$(RESET)"

check-all: ## Run comprehensive checks (all features)
	@echo "$(BOLD)$(BLUE)🔍 Running comprehensive checks...$(RESET)"
	uv run nox -s ci_check

typecheck-all: ## Run type checking with all features
	@echo "$(BOLD)$(MAGENTA)🔬 Type checking all features...$(RESET)"
	uv run nox -s typecheck_all

test-all: ## Run tests for all Python versions and features
	@echo "$(BOLD)$(MAGENTA)🧪 Running comprehensive tests...$(RESET)"
	uv run nox -s tests

ci: check-all ## Run full CI checks locally
	@echo "$(GREEN)🎉 All CI checks completed!$(RESET)"

# ══════════════════════════════════════════════════════════════════════════
# Feature-specific checks
# ══════════════════════════════════════════════════════════════════════════

test-lang: ## Test LangChain features only
	@echo "$(BOLD)$(MAGENTA)🦜 Testing LangChain features...$(RESET)"
	uv run nox -s test_langchain

test-mcp: ## Test MCP features only
	@echo "$(BOLD)$(MAGENTA)🔗 Testing MCP features...$(RESET)"
	uv run nox -s test_mcp

typecheck-lang: ## Type check LangChain features
	@echo "$(BOLD)$(MAGENTA)🦜 Type checking LangChain...$(RESET)"
	uv run nox -s typecheck_lang

typecheck-mcp: ## Type check MCP features
	@echo "$(BOLD)$(MAGENTA)🔗 Type checking MCP...$(RESET)"
	uv run nox -s typecheck_mcp

# ══════════════════════════════════════════════════════════════════════════
# Pre-commit and Git
# ══════════════════════════════════════════════════════════════════════════

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BOLD)$(CYAN)🪝 Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "$(BOLD)$(CYAN)🔄 Updating pre-commit hooks...$(RESET)"
	pre-commit autoupdate

pre-commit-manual: ## Run manual-only pre-commit hooks
	@echo "$(BOLD)$(CYAN)🪝 Running manual pre-commit hooks...$(RESET)"
	pre-commit run mypy-langchain --hook-stage manual
	pre-commit run mypy-mcp --hook-stage manual
	pre-commit run mypy-all --hook-stage manual

# ══════════════════════════════════════════════════════════════════════════
# Testing and Coverage
# ══════════════════════════════════════════════════════════════════════════

test-cov: ## Run tests with coverage
	@echo "$(BOLD)$(MAGENTA)📊 Running tests with coverage...$(RESET)"
	uv run nox -s coverage

smoke: ## Run smoke tests (quick validation)
	@echo "$(BOLD)$(MAGENTA)💨 Running smoke tests...$(RESET)"
	uv run nox -s smoke

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BOLD)$(MAGENTA)👀 Running tests in watch mode...$(RESET)"
	uv run pytest --maxfail=1 --tb=short -q --disable-warnings --looponfail

# ══════════════════════════════════════════════════════════════════════════
# Documentation
# ══════════════════════════════════════════════════════════════════════════

docs: ## Build documentation
	@echo "$(BOLD)$(BLUE)📚 Building documentation...$(RESET)"
	uv run nox -s docs

docs-serve: ## Serve documentation locally
	@echo "$(BOLD)$(BLUE)🌐 Serving documentation at http://localhost:8000$(RESET)"
	uv run nox -s docs_serve

# ══════════════════════════════════════════════════════════════════════════
# Building and Publishing
# ══════════════════════════════════════════════════════════════════════════

build: ## Build package
	@echo "$(BOLD)$(BLUE)📦 Building package...$(RESET)"
	uvx poetry build
	@echo "$(GREEN)✅ Package built successfully!$(RESET)"
	@echo "$(CYAN)📁 Files created:$(RESET)"
	@ls -la dist/

build-check: ## Build and verify package
	@echo "$(BOLD)$(BLUE)📦 Building and checking package...$(RESET)"
	uvx poetry build
	uvx twine check dist/*
	@echo "$(GREEN)✅ Package built and verified!$(RESET)"

publish-test: build-check ## Publish to Test PyPI
	@echo "$(BOLD)$(YELLOW)🧪 Publishing to Test PyPI...$(RESET)"
	@echo "$(RED)⚠️  Make sure TEST_PYPI_TOKEN is set!$(RESET)"
	uvx twine upload --repository-url https://test.pypi.org/legacy/ dist/*

version: ## Show current version
	@echo "$(BOLD)$(BLUE)📋 Current version:$(RESET)"
	@uvx poetry version --short

# ══════════════════════════════════════════════════════════════════════════
# Development Utilities
# ══════════════════════════════════════════════════════════════════════════

deps-update: ## Update dependencies
	@echo "$(BOLD)$(CYAN)🔄 Updating dependencies...$(RESET)"
	uv sync --upgrade

deps-check: ## Check for dependency updates
	@echo "$(BOLD)$(CYAN)🔍 Checking for dependency updates...$(RESET)"
	uv tree --outdated

nox-list: ## List all available nox sessions
	@echo "$(BOLD)$(BLUE)📋 Available nox sessions:$(RESET)"
	uv run nox --list

env-info: ## Show environment information
	@echo "$(BOLD)$(BLUE)🔧 Environment Information:$(RESET)"
	@echo "$(CYAN)Python version:$(RESET)"
	@python --version
	@echo "$(CYAN)uv version:$(RESET)"
	@uv --version
	@echo "$(CYAN)Current virtual environment:$(RESET)"
	@echo "$$VIRTUAL_ENV"

# ══════════════════════════════════════════════════════════════════════════
# Quick Combinations (Most common workflows)
# ══════════════════════════════════════════════════════════════════════════

dev: install fix check ## Setup dev environment and run checks
	@echo "$(GREEN)🎉 Development environment ready and all checks passed!$(RESET)"

quick: fix lint test ## Quick development cycle (fix, lint, test)
	@echo "$(GREEN)⚡ Quick checks completed!$(RESET)"

full: fix check-all test-cov ## Full validation (everything)
	@echo "$(GREEN)🏆 Full validation completed!$(RESET)"

# ══════════════════════════════════════════════════════════════════════════
# Aliases for common typos/variations
# ══════════════════════════════════════════════════════════════════════════

fmt: format ## Alias for format
linting: lint ## Alias for lint
testing: test ## Alias for test
typing: typecheck ## Alias for typecheck
coverage: test-cov ## Alias for test-cov
