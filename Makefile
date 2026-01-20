# User Makefile for fmp-data
# ===========================
# Simple commands for end users of the fmp-data package
#
# For maintainer/developer commands, see Makefile.dev

.PHONY: help install install-dev test lint format fix clean update update-dev
.PHONY: mcp-setup mcp-test mcp-list mcp-status

# Default target
.DEFAULT_GOAL := help

# Colors for output
BOLD := \033[1m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
CYAN := \033[36m
RESET := \033[0m

# ══════════════════════════════════════════════════════════════════════════
# Help
# ══════════════════════════════════════════════════════════════════════════

help: ## Show available commands
	@echo "$(BOLD)$(BLUE)fmp-data Commands$(RESET)"
	@echo "$(CYAN)════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)📦 Installation:$(RESET)"
	@echo "  $(GREEN)make install$(RESET)         Install package with all features"
	@echo "  $(GREEN)make install-dev$(RESET)     Install all dependencies (dev + docs + extras)"
	@echo "  $(GREEN)make install-mcp$(RESET)     Install with MCP server support"
	@echo ""
	@echo "$(BOLD)🤖 MCP Server (Claude Desktop):$(RESET)"
	@echo "  $(GREEN)make mcp-setup$(RESET)       Setup MCP server for Claude Desktop"
	@echo "  $(GREEN)make mcp-test$(RESET)        Test MCP server connection"
	@echo "  $(GREEN)make mcp-list$(RESET)        List available MCP tools"
	@echo ""
	@echo "$(BOLD)🧪 Testing & Quality:$(RESET)"
	@echo "  $(GREEN)make test$(RESET)            Run tests"
	@echo "  $(GREEN)make lint$(RESET)            Check code quality"
	@echo "  $(GREEN)make format$(RESET)          Check code formatting"
	@echo "  $(GREEN)make fix$(RESET)             Auto-fix code issues"
	@echo ""
	@echo "$(BOLD)🧹 Maintenance:$(RESET)"
	@echo "  $(GREEN)make clean$(RESET)           Clean cache and build files"
	@echo "  $(GREEN)make update$(RESET)          Update all dependencies"
	@echo ""
	@echo "$(YELLOW)💡 Quick Start:$(RESET)"
	@echo "  1. $(CYAN)make install-mcp$(RESET)   # Install with MCP support"
	@echo "  2. $(CYAN)make mcp-setup$(RESET)     # Setup Claude Desktop integration"

# ══════════════════════════════════════════════════════════════════════════
# Installation
# ══════════════════════════════════════════════════════════════════════════

install: ## Install package with all features
	@echo "$(BOLD)$(BLUE)📦 Installing fmp-data with all features...$(RESET)"
	pip install -e ".[langchain,mcp]"
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

install-dev: ## Install all dependencies (dev + docs + extras)
	@echo "$(BOLD)$(BLUE)📦 Installing fmp-data with all dev dependencies...$(RESET)"
	pip install -e ".[dev,docs,langchain,mcp]"
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

install-mcp: ## Install package with MCP server support
	@echo "$(BOLD)$(BLUE)📦 Installing fmp-data with MCP support...$(RESET)"
	pip install -e ".[mcp]"
	@echo "$(GREEN)✅ Installation complete!$(RESET)"
	@echo ""
	@echo "$(YELLOW)Next step:$(RESET) Run $(CYAN)make mcp-setup$(RESET) to configure Claude Desktop"

install-basic: ## Install package without extras
	@echo "$(BOLD)$(BLUE)📦 Installing fmp-data (basic)...$(RESET)"
	pip install -e .
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

# ══════════════════════════════════════════════════════════════════════════
# MCP Server Commands
# ══════════════════════════════════════════════════════════════════════════

mcp-setup: ## Setup MCP server for Claude Desktop (interactive)
	@echo "$(BOLD)$(CYAN)🤖 Setting up MCP server for Claude Desktop...$(RESET)"
	@command -v fmp-mcp >/dev/null 2>&1 || (echo "$(YELLOW)Installing MCP support first...$(RESET)" && pip install -e ".[mcp]")
	@fmp-mcp setup

mcp-test: ## Test MCP server connection
	@echo "$(BOLD)$(CYAN)🧪 Testing MCP server...$(RESET)"
	@command -v fmp-mcp >/dev/null 2>&1 || (echo "$(YELLOW)Installing MCP support first...$(RESET)" && pip install -e ".[mcp]")
	@fmp-mcp test

mcp-list: ## List available MCP tools
	@echo "$(BOLD)$(CYAN)📋 Available MCP tools:$(RESET)"
	@command -v fmp-mcp >/dev/null 2>&1 || (echo "$(YELLOW)Installing MCP support first...$(RESET)" && pip install -e ".[mcp]")
	@fmp-mcp list --format table

mcp-status: ## Check MCP server status
	@echo "$(BOLD)$(CYAN)📊 MCP server status:$(RESET)"
	@command -v fmp-mcp >/dev/null 2>&1 || (echo "$(YELLOW)Installing MCP support first...$(RESET)" && pip install -e ".[mcp]")
	@fmp-mcp status

# ══════════════════════════════════════════════════════════════════════════
# Testing and Code Quality
# ══════════════════════════════════════════════════════════════════════════

test: ## Run tests
	@echo "$(BOLD)$(BLUE)🧪 Running tests (creates .venv if missing)...$(RESET)"
	@if [ ! -d ".venv" ]; then \
		echo "$(CYAN)Creating virtual environment at .venv...$(RESET)"; \
		python3 -m venv .venv; \
	fi
	@. .venv/bin/activate && pip install -e ".[dev]"
	@set -a; [ -f .env ] && . ./.env; set +a; \
		if [ -z "$$FMP_TEST_API_KEY" ] && [ -n "$$FMP_API_KEY" ]; then export FMP_TEST_API_KEY="$$FMP_API_KEY"; fi; \
		if [ -z "$$FMP_API_KEY" ] && [ -n "$$FMP_TEST_API_KEY" ]; then export FMP_API_KEY="$$FMP_TEST_API_KEY"; fi; \
		. .venv/bin/activate && pytest -q

lint: ## Check code quality with ruff
	@echo "$(BOLD)$(BLUE)🔍 Checking code quality...$(RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff check fmp_data; \
	elif [ -x ".venv/bin/ruff" ]; then \
		. .venv/bin/activate && ruff check fmp_data; \
	elif command -v ruff >/dev/null 2>&1; then \
		ruff check fmp_data; \
	else \
		if [ ! -d ".venv" ]; then \
			echo "$(CYAN)Creating virtual environment at .venv...$(RESET)"; \
			python3 -m venv .venv; \
		fi; \
		echo "$(CYAN)Installing dev dependencies in .venv...$(RESET)"; \
		. .venv/bin/activate && pip install -e ".[dev]"; \
		. .venv/bin/activate && ruff check fmp_data; \
	fi

format: ## Check code formatting
	@echo "$(BOLD)$(BLUE)📝 Checking code formatting...$(RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff format --check fmp_data; \
	elif [ -x ".venv/bin/ruff" ]; then \
		. .venv/bin/activate && ruff format --check fmp_data; \
	elif command -v ruff >/dev/null 2>&1; then \
		ruff format --check fmp_data; \
	else \
		if [ ! -d ".venv" ]; then \
			echo "$(CYAN)Creating virtual environment at .venv...$(RESET)"; \
			python3 -m venv .venv; \
		fi; \
		echo "$(CYAN)Installing dev dependencies in .venv...$(RESET)"; \
		. .venv/bin/activate && pip install -e ".[dev]"; \
		. .venv/bin/activate && ruff format --check fmp_data; \
	fi

fix: ## Auto-fix code issues
	@echo "$(BOLD)$(CYAN)🔧 Auto-fixing code issues...$(RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff check --fix fmp_data; \
		uv run ruff format fmp_data; \
	elif [ -x ".venv/bin/ruff" ]; then \
		. .venv/bin/activate && ruff check --fix fmp_data; \
		. .venv/bin/activate && ruff format fmp_data; \
	elif command -v ruff >/dev/null 2>&1; then \
		ruff check --fix fmp_data; \
		ruff format fmp_data; \
	else \
		if [ ! -d ".venv" ]; then \
			echo "$(CYAN)Creating virtual environment at .venv...$(RESET)"; \
			python3 -m venv .venv; \
		fi; \
		echo "$(CYAN)Installing dev dependencies in .venv...$(RESET)"; \
		. .venv/bin/activate && pip install -e ".[dev]"; \
		. .venv/bin/activate && ruff check --fix fmp_data; \
		. .venv/bin/activate && ruff format fmp_data; \
	fi
	@echo "$(GREEN)✅ Auto-fixes applied!$(RESET)"

# ══════════════════════════════════════════════════════════════════════════
# Maintenance
# ══════════════════════════════════════════════════════════════════════════

clean: ## Clean cache and temporary files
	@echo "$(BOLD)$(YELLOW)🧹 Cleaning up...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete!$(RESET)"

update: ## Update all dependencies using UV
	@echo "$(BOLD)$(CYAN)🔄 Updating all dependencies...$(RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --upgrade; \
		echo "$(GREEN)✅ Dependencies updated successfully!$(RESET)"; \
	else \
		echo "$(YELLOW)UV not installed. Install with:$(RESET)"; \
		echo "  $(CYAN)curl -LsSf https://astral.sh/uv/install.sh | sh$(RESET)"; \
		echo "  or"; \
		echo "  $(CYAN)pip install uv$(RESET)"; \
		exit 1; \
	fi

update-dev: ## Update development dependencies
	@echo "$(BOLD)$(CYAN)🔄 Updating development dependencies...$(RESET)"
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --upgrade --group dev; \
		echo "$(GREEN)✅ Development dependencies updated!$(RESET)"; \
	else \
		echo "$(YELLOW)UV not installed. See 'make update' for installation instructions.$(RESET)"; \
		exit 1; \
	fi

# ══════════════════════════════════════════════════════════════════════════
# Quick Start
# ══════════════════════════════════════════════════════════════════════════

quickstart: install-mcp mcp-setup ## Complete setup for new users
	@echo "$(GREEN)🎉 Setup complete! Claude Desktop is now configured with FMP Data.$(RESET)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Restart Claude Desktop"
	@echo "  2. Start a new conversation"
	@echo "  3. Try asking: 'What's the current price of AAPL?'"

# ══════════════════════════════════════════════════════════════════════════
# Aliases
# ══════════════════════════════════════════════════════════════════════════

setup: quickstart ## Alias for quickstart
