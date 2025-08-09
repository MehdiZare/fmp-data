# Changelog

All notable changes to the package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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
