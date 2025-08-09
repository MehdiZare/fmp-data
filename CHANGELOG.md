# Changelog

All notable changes to the package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-09

### Added
- Production-ready release with stable API
- Comprehensive GitHub Actions CI/CD pipeline
- Automated versioning with semantic release labels
- TestPyPI deployment for dev branch updates
- Full test coverage across all modules

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

### Removed
- Removed deprecated sync_groups.py script
- Cleaned up duplicate dependency definitions

## [0.4.0] - 2025-7-1

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
- **Poetry-focused development workflow** with comprehensive setup instructions
- Enhanced contributor guidelines with Poetry-specific commands and quality checks

### Changed
- Updated documentation with MCP server usage examples
- Refined feature list presentation for better readability
- Consolidated integration patterns across different use cases
- **Emphasized Poetry as the primary package management tool** with detailed setup guides

### Breaking Changes
- **Breaking:** `get_quote` has moved from `MarketClient` to `CompanyClient`
  - Update: `client.market.get_quote()` → `client.company.get_quote()`

## [0.3.0] - 2025-1-5

### Added
- Langchain Integration
  - New capability to convert Financial Market Data (FMP) endpoints to Langchain Structured Tools
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

## [0.2.0] - 12/11/2024

### Added
- Full coverage of Financial Market Data (FMP) endpoints
- Comprehensive endpoint mapping
- Robust error handling for API interactions

## [0.1.0] - Initial Release Date

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
