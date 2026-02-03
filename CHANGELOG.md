# Changelog

All notable changes to the package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- **New Company Endpoint** - Added `get_profile_cik()` method to retrieve company profile using CIK (Central Index Key) number
  - Available in both sync (`CompanyClient`) and async (`AsyncCompanyClient`) clients
  - Endpoint: `/stable/profile-cik`
  - MCP semantics key: `company.profile_cik`
  - Useful for SEC filing research and cross-referencing regulatory data

### Fixed
- **Stock News Null Symbol** - Fixed `ValidationError` when FMP API returns `null` for `symbol` field in stock news responses (Issue #62):
  - Made `StockNewsArticle.symbol` optional (`str | None`)
  - Made `StockNewsSentiment.symbol` optional for consistency
  - Added unit and integration tests for null symbol handling
- **Historical Price Endpoints** - Fixed 404 errors on historical price endpoints by correcting endpoint paths:
  - Updated `HISTORICAL_PRICE` (company), `CRYPTO_HISTORICAL`, `FOREX_HISTORICAL`, and `COMMODITY_HISTORICAL` to use `/full` suffix
  - Changed paths from `historical-price-eod` to `historical-price-eod/full` to match FMP API specification
  - All VCR test cassettes re-recorded with correct 200 status codes and actual price data
  - Updated integration tests to validate non-empty responses and detect future path mismatches
- **Alternative Markets Models** - Fixed Pydantic validation errors for crypto/forex/commodity historical prices:
  - Made `adj_close` and `unadjusted_volume` fields optional in `HistoricalPrice` model
  - Fixed `FOREX_HISTORICAL` endpoint to use correct response model (`ForexHistoricalPrice` instead of `ForexPriceHistory`)
  - Updated unit test mocks to match actual `/full` endpoint response format (flat list structure)
- **Test Coverage** - Improved patch coverage to 100% for deprecation warnings:
  - Added async test for `get_stock_news_sentiments()` deprecation warning
  - Enhanced sync test to validate `DeprecationWarning` emission
  - All 866 unit tests now passing with proper coverage of warning code paths
- **Missing Data Defaults** - Normalized economic and intelligence models to keep missing values as `None`:
  - `EconomicEvent.country` now defaults to `None` instead of empty string
  - `EconomicEvent.change_percent` now defaults to `None` instead of `0`
  - Government trading `owner`/`comment` fields now default to `None`
- **Comprehensive Model Field Audit** - Fixed missing fields and incorrect aliases across all Pydantic models to match actual FMP API responses (Issue #66):
  - **Index models**: Fixed `IndexConstituent.headquarter` alias (`headQuarter`), added `date_added` field to `HistoricalIndexConstituent`
  - **SEC models**: Added 20+ missing fields to `SECProfile` (sic_group, isin, city, state, country, description, ceo, website, etc.), added `has_financials` and `link` to `SECFiling8K`
  - **Transcripts models**: Fixed `year` field in `EarningsTranscript` and `TranscriptDate` to accept both `fiscalYear` and `year` via `AliasChoices`
  - **Intelligence models**: Added `publisher` field to `StockNewsArticle`, added 5 missing fields to `PressReleaseBySymbol` (publishedDate, publisher, image, site, url)
  - **Market models**: Fixed `ExchangeSymbol` aliases for `priceAvg50`, `priceAvg200`, `avgVolume`, `previousClose`; removed duplicate `IndexConstituent` class
  - **Company models**: Fixed `CompanyProfile` aliases for `vol_avg`, `mkt_cap`, `last_div`, `changes` using `AliasChoices`; added `change_percentage`, `volume`, `exchange_full_name` fields
  - **Alternative models**: Fixed `PriceQuote.change_percent` and `CryptoQuote.change_percent` to accept both `changesPercentage` and `changePercentage` variants
  - **Fundamental models**: Added 36+ fields to `FinancialGrowth`, 30+ fields to `BalanceSheet`, 8 fields to `OwnerEarnings`, 7 fields to `FinancialScore`, 4 fields to `EnterpriseValue`

### Deprecated
- **Stock News Sentiments Endpoint** - Marked `get_stock_news_sentiments()` as deprecated:
  - FMP API no longer supports the `stock-news-sentiments-rss-feed` endpoint (returns 404)
  - Both sync and async methods now emit `DeprecationWarning` with clear migration message
  - Method returns empty list to maintain backward compatibility
  - Will be removed in a future major version

### Changed
- **Documentation** - Enhanced `CLAUDE.md` with best practices:
  - Added critical testing strategy reminders for validating successful API responses
  - Documented historical price endpoint variants (`/full`, `/light`, `/non-split-adjusted`, `/dividend-adjusted`)
  - Added endpoint definition guidelines to prevent future 404 errors
  - Established deprecation handling process for removed FMP endpoints
- **Testing** - Enabled parallel pytest runs for local Makefile/nox usage and added `pytest-xdist` to dev dependencies (CI remains serial to avoid stalls).
- **Makefile** - `.venv/.installed` now tracks `pyproject.toml` changes to auto-refresh dev deps.

## [2.1.0] - 2026-01-23

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v2.0.0...v2.1.0)

### Added
- **New Centralized Exception Classes** - Added 4 new exception types to improve error handling:
  - `InvalidSymbolError(ValidationError)` - For missing or blank required symbols
  - `InvalidResponseTypeError(FMPError)` - For unexpected API response types with detailed type information
  - `DependencyError(ConfigError)` - For missing optional dependencies with installation instructions
  - `FMPNotFound(FMPError)` - For symbol/resource not found errors
- **Enhanced Error Messages** - All new exceptions provide clear, actionable error messages with context
- **Comprehensive Test Coverage** - Added 15 new test methods for exception hierarchy and behavior

### Fixed
- **Exception Handling Consistency** (21 issues resolved):
  - Centralized all local exception classes to `fmp_data/exceptions.py`
  - Fixed overly broad exception handling in `AsyncInvestmentClient.get_etf_info()` to catch specific errors
  - Added validation error handling in `AsyncBatchClient.get_dcf_bulk()` with proper row-level error logging
  - Replaced generic `ValueError`/`TypeError` with specific exception types across company and batch clients
  - Updated MCP modules to use `DependencyError` with installation instructions
- **Security** - Fixed API key exposure in integration test logging by redacting sensitive URL params and headers
- **Code Quality**:
  - Added return type annotations (`-> None`) to all 11 example `main()` functions and test helper functions
  - Fixed test lambda parameters to use underscore for unused arguments
  - Created custom `ModuleLoadError` exception for test module loading failures
  - Improved logger usage patterns across modules
- **Documentation** - Fixed Markdown formatting in API endpoint counts (changed `**N endpoints**` to `### N endpoints`)
- **429 Retry Handling** - Now respects `retry_after` wait times to avoid premature retries

### Changed
- **Improved Exception Hierarchy**: Removed local exception classes from individual modules - all exceptions now centralized in `fmp_data.exceptions`
- All custom exceptions properly inherit from `FMPError` base class
- **Better Validation**: Async batch client now validates and logs individual row errors instead of failing entire requests

## [2.0.0] - 2026-01-19

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v1.0.1...v2.0.0)

### Added
- **New Modules** - 4 new client modules with 32 new endpoints:
  - `batch/` - Batch data endpoints (12 endpoints)
    - Batch quotes for multiple symbols
    - Aftermarket trades and quotes
    - Exchange-wide stock quotes
    - Batch quotes for mutual funds, ETFs, commodities, crypto, forex, and indices
    - Batch market capitalization
  - `transcripts/` - Earnings call transcripts (4 endpoints)
    - Latest transcripts feed
    - Transcripts by symbol, year, and quarter
    - Available transcript dates
    - Symbols with available transcripts
  - `sec/` - SEC filing and company data (10 endpoints)
    - Latest 8-K and financial filings
    - Filing search by form type, symbol, or CIK
    - Company search by name, symbol, or CIK
    - SEC company profiles
    - Standard Industrial Classification (SIC) codes
  - `index/` - Market index constituents (6 endpoints)
    - S&P 500, NASDAQ, and Dow Jones constituents
    - Historical constituent changes for all three indices
- **Python 3.14 Support** - Full support for Python 3.14
- **New Tests** - 76 new unit tests for:
  - `@deprecated` decorator
  - Exception hierarchy
  - All new modules (batch, transcripts, sec, index)

### Fixed
- **Critical Bug Fixes**:
  - Fixed OpenAI embedding parameter bug (`openai_api_base` → `api_key`)
  - Fixed `FMPVectorStore` export (corrected to `EndpointVectorStore`)
  - Fixed MCP install hint (`[mcp-server]` → `[mcp]`)
  - Fixed retry configuration being ignored - now uses configurable `max_retries`
  - Fixed `_handle_rate_limit` not being called in request flow
  - Fixed vector store security issue - made `allow_dangerous_deserialization` opt-in with warning
  - Fixed `CompanyProfile` model validation errors by making optional fields nullable (e.g., `dcf`, `cik`, `isin`, etc.)

### Changed
- **Code Quality Improvements**:
  - Refactored `TechnicalClient` with generic `_get_indicator` helper (reduces code duplication)
  - Extracted `_build_date_params` helper in `MarketIntelligenceClient`
  - Refactored `BaseClient._process_response()` into smaller helper methods
  - Improved LangChain exception handling with specific exception types
- **Dependencies Updated**:
  - `pydantic` ≥ 2.12.5
  - `pydantic-settings` ≥ 2.12.0
  - `python-dotenv` ≥ 1.2.1
  - `langchain-core` ≥ 1.2.7
  - `langchain-openai` ≥ 1.1.7
  - `langgraph` ≥ 1.0.6
  - `openai` ≥ 2.15.0
  - `tiktoken` ≥ 0.12.0
  - `faiss-cpu` ≥ 1.13.2
  - `mcp` ≥ 1.25.0
  - `pyyaml` ≥ 6.0.3

### Removed
- Removed unused dependencies: `cachetools`, `structlog`, `pandas`, `tqdm`
- Removed `black` dependency (replaced by `ruff format`)

### Breaking Changes
- **LangChain v1 Requirement**: LangChain integration now requires LangChain v1 packages (`langchain-core`, `langchain-openai`) and LangGraph v1.
- **Vector Store Security**: `EndpointVectorStore.load()` now requires `allow_dangerous_deserialization=True` to load cached stores. This is a security improvement to prevent arbitrary code execution from untrusted cache sources.

  **Migration steps:**
  ```python
  # Old (pre-2.0.0)
  vector_store = EndpointVectorStore.load(cache_dir)

  # New (2.0.0+)
  vector_store = EndpointVectorStore.load(
      cache_dir,
      allow_dangerous_deserialization=True  # Only if you trust the cache source
  )
  ```

## [1.0.1] - 2025-08-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v1.0.0...v1.0.1)

### Fixed
- Fixed CI/CD workflow issues with uv package installation
- Added --system flag to uv pip install commands in GitHub Actions
- Removed unnecessary uv run prefix from build commands

## [1.0.0] - 2025-08-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.2...v1.0.0)

### Added
- Production-ready release with stable API
- Comprehensive GitHub Actions CI/CD pipeline
- Automated versioning with semantic release labels
- TestPyPI deployment for dev branch updates
- Test coverage exceeding 80% threshold for core modules

### Fixed
- Corrected field aliases in fundamental models (stockPrice)
- Fixed primitive type handling in base client
- Updated Alternative Markets endpoints to use /stable/ prefix
- Resolved isinstance() syntax for Python 3.10+ compatibility
- Fixed millisecond timestamp detection in alternative models

### Changed
- Migrated to UV package manager for faster dependency resolution
- Updated development status to Production/Stable
- Streamlined CI/CD workflows for automated releases
- Enhanced error handling and validation

### Breaking Changes
- **`get_quote` method relocation**: The `get_quote` method has been moved from `MarketClient` to `CompanyClient`

  **Migration steps:**
  ```python
  # Old (pre-1.0.0)
  quote = client.market.get_quote("AAPL")

  # New (1.0.0+)
  quote = client.company.get_quote("AAPL")
  ```

  **Rationale:** This change better aligns with the FMP API structure where company quotes are part of the company data domain.

- **Alternative Markets endpoint prefix change**: All Alternative Markets endpoints now use `/stable/` prefix instead of `/v3/`

  **Migration steps:**
  - No code changes required for users of the client library
  - Direct API users should update endpoint URLs from `/v3/` to `/stable/`

### Removed
- Removed deprecated sync_groups.py script
- Cleaned up duplicate dependency definitions

## [0.5.2] - 2025-07-04

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.1...v0.5.2)

### Fixed
- Resolved dynamic versioning issues with hatch-vcs
- Fixed CI/CD pipeline Poetry installation errors

## [0.5.1] - 2025-07-02

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.0...v0.5.1)

### Fixed
- Patched versioning configuration for proper PyPI releases
- Corrected build system requirements

## [0.5.0] - 2025-07-02

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.4.0...v0.5.0)

### Added
- MCP (Model Context Protocol) server implementation
- FastMCP integration for AI assistant compatibility
- Configurable tool manifest system

## [0.4.0] - 2025-01-07

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.0...v0.4.0)

### Added
- MCP (Model Context Protocol) Server Support
  - FastMCP-based server implementation for exposing FMP data through standardized protocol
  - Configurable tool manifest system for customizing available endpoints
  - Environment variable configuration support (`FMP_MCP_MANIFEST`)
  - Default tool set covering major FMP endpoints (company, market, fundamental, technical)
  - Tool naming convention: `<client>.<semantics_key>` (e.g., `company.profile`, `market.quote`)
  - Seamless integration with MCP-compatible AI assistants

### Improved
- Enhanced installation options with MCP extras support
- Streamlined configuration for multiple integration types
- Better separation of concerns between client, LangChain, and MCP modules
- **UV-focused development workflow** with comprehensive setup instructions
- Enhanced contributor guidelines with UV-specific commands and quality checks

### Changed
- Updated documentation with MCP server usage examples
- Refined feature list presentation for better readability
- Consolidated integration patterns across different use cases
- **Transitioned to UV as the primary package management tool** with detailed setup guides

### Breaking Changes
- **Breaking:** `get_quote` has moved from `MarketClient` to `CompanyClient`
  - Update: `client.market.get_quote()` → `client.company.get_quote()`

## [0.3.4] - 2025-01-06

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.3...v0.3.4)

### Fixed
- Minor bug fixes and performance improvements

## [0.3.3] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.2...v0.3.3)

### Fixed
- API response handling improvements

## [0.3.2] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.1...v0.3.2)

### Fixed
- Enhanced error handling for edge cases

## [0.3.1] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.0...v0.3.1)

### Fixed
- LangChain integration compatibility issues

## [0.3.0] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.2.0...v0.3.0)

### Added
- LangChain Integration
  - New capability to convert Financial Modeling Prep (FMP) endpoints to LangChain Structured Tools
  - Dynamic endpoint discovery for query-based tool selection
  - Flexible tool retrieval mechanism allowing users to:
    - Send a query
    - Retrieve top_n most relevant FMP endpoints
    - Generate Structured Tools compatible with any LLM
  - Enhanced query routing and tool selection system

### Improved
- Query processing capabilities
- Endpoint selection intelligence
- Flexibility in financial data retrieval

## [0.2.0] - 2024-12-11

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1.2...v0.2.0)

### Added
- Full coverage of Financial Modeling Prep (FMP) endpoints
- Comprehensive endpoint mapping
- Robust error handling for API interactions

## [0.1.2] - 2024-12-10

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1.1...v0.1.2)

### Fixed
- Package distribution issues
- Dependency resolution conflicts

## [0.1.1] - 2024-12-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1-beta.1...v0.1.1)

### Fixed
- Initial bug fixes post-beta release

## [0.1-beta.1] - 2024-12-08

### Added
- Initial project setup
- Basic API interaction framework
- Preliminary endpoint support

## Future Roadmap
- Advanced machine learning-driven endpoint recommendations
- Enhanced query prediction capabilities
- Additional financial data source integrations
- Expanded tool support across different protocols
- Performance optimizations for large-scale deployments

## Contribution Guidelines
- Follow semantic versioning
- Maintain comprehensive test coverage
- Document significant architectural changes
- Ensure backward compatibility
