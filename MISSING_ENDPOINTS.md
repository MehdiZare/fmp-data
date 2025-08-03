# Missing FMP API Endpoints

This document lists all endpoints that exist in the FMP API documentation but are missing from the fmp-data Python client library.

## Missing Endpoints by Module

### 📁 **Market Module** (add to `market/endpoints.py`)

#### Directory
- ✅ ~~`available-exchanges` - Available Exchanges API~~ (COMPLETED)
- ✅ ~~`available-sectors` - Available Sectors API~~ (COMPLETED)
- ✅ ~~`available-industries` - Available Industries API~~ (COMPLETED)
- ✅ ~~`available-countries` - Available Countries API~~ (COMPLETED)

### 📁 **Company Module** (add to `company/endpoints.py`)

#### Company
- `batch-market-capitalization` - Batch Market Cap API
- ✅ ~~`mergers-acquisitions-latest` - Latest Mergers & Acquisitions API~~ (COMPLETED)
- ✅ ~~`mergers-acquisitions-search` - Search Mergers & Acquisitions API~~ (COMPLETED)
- ✅ ~~`executive-compensation-benchmark` - Executive Compensation Benchmark API~~ (COMPLETED)

#### Calendar (Company-specific)
- `dividends` - Dividends Company API (company-specific dividends)
- `earnings` - Earnings Report API (company-specific earnings)
- `splits` - Stock Split Details API (company-specific splits)

#### Chart
- ✅ ~~`historical-price-eod/light` - Stock Chart Light API~~ (COMPLETED)
- ✅ ~~`historical-price-eod/non-split-adjusted` - Unadjusted Stock Price API~~ (COMPLETED)
- ✅ ~~`historical-price-eod/dividend-adjusted` - Dividend Adjusted Price Chart API~~ (COMPLETED)

### 📁 **Intelligence Module** (add to `intelligence/endpoints.py`)

#### Analyst
- `ratings-snapshot` - Ratings Snapshot API
- `ratings-historical` - Historical Ratings API
- `price-target-news` - Price Target News API
- `price-target-latest-news` - Price Target Latest News API
- `grades` - Stock Grades API
- `grades-historical` - Historical Stock Grades API
- `grades-consensus` - Stock Grades Summary API
- `grades-news` - Stock Grade News API
- `grades-latest-news` - Stock Grade Latest News API

#### Calendar
- `ipos-disclosure` - IPOs Disclosure API
- `ipos-prospectus` - IPOs Prospectus API

#### Insider Trades
- `insider-trading/latest` - Latest Insider Trading API
- `insider-trading/search` - Search Insider Trades API
- `insider-trading/reporting-name` - Search Insider Trades by Reporting Name API
- `insider-trading/statistics` - Insider Trade Statistics API
- `acquisition-of-beneficial-ownership` - Acquisition Ownership API

### 📁 **Institutional Module** (add to `institutional/endpoints.py`)

#### Form 13F
- `institutional-ownership/latest` - Institutional Ownership Filings API
- `institutional-ownership/extract` - Filings Extract API
- `institutional-ownership/dates` - Form 13F Filings Dates API
- `institutional-ownership/extract-analytics/holder` - Filings Extract With Analytics By Holder API
- `institutional-ownership/holder-performance-summary` - Holder Performance Summary API
- `institutional-ownership/holder-industry-breakdown` - Holders Industry Breakdown API
- `institutional-ownership/symbol-positions-summary` - Positions Summary API
- `institutional-ownership/industry-summary` - Industry Performance Summary API

### 📁 **Fundamental Module** (add to `fundamental/endpoints.py`)

#### Statements
- `latest-financial-statements` - Latest Financial Statements API
- `income-statement-ttm` - Income Statements TTM API
- `balance-sheet-statement-ttm` - Balance Sheet Statements TTM API
- `cash-flow-statement-ttm` - Cashflow Statements TTM API
- `key-metrics-ttm` - Key Metrics TTM API
- `ratios-ttm` - Financial Ratios TTM API
- `financial-scores` - Financial Scores API
- `enterprise-values` - Enterprise Values API
- `income-statement-growth` - Income Statement Growth API
- `balance-sheet-statement-growth` - Balance Sheet Statement Growth API
- `cash-flow-statement-growth` - Cashflow Statement Growth API
- `financial-growth` - Financial Statement Growth API
- `financial-reports-json` - Financial Reports Form 10-K JSON API
- `financial-reports-xlsx` - Financial Reports Form 10-K XLSX API
- `income-statement-as-reported` - As Reported Income Statements API
- `balance-sheet-statement-as-reported` - As Reported Balance Statements API
- `cash-flow-statement-as-reported` - As Reported Cashflow Statements API

#### DCF
- `discounted-cash-flow` - DCF Valuation API
- `custom-discounted-cash-flow` - Custom DCF Advanced API
- `custom-levered-discounted-cash-flow` - Custom DCF Levered API

### 📁 **Alternative Module** (add to `alternative/endpoints.py`)

#### Quote (Real-time batch quotes)
- `batch-commodity-quotes` - (if different from existing)
- `batch-crypto-quotes` - (if different from existing)
- `batch-forex-quotes` - (if different from existing)

### 📁 **NEW MODULE: Indexes** (create `indexes/`)

- `index-list` - (if different from market/index-list)
- `quote` - Index Quote API
- `quote-short` - Index Short Quote API
- `batch-index-quotes` - All Index Quotes API
- `historical-price-eod/light` - Historical Index Light Chart API
- `historical-price-eod/full` - Historical Index Full Chart API
- `historical-chart/1min` - 1-Minute Interval Index Price API
- `historical-chart/5min` - 5-Minute Interval Index Price API
- `historical-chart/1hour` - 1-Hour Interval Index Price API
- `sp500-constituent` - S&P 500 Index API
- `nasdaq-constituent` - Nasdaq Index API
- `dowjones-constituent` - Dow Jones API
- `historical-sp500-constituent` - Historical S&P 500 API
- `historical-nasdaq-constituent` - Historical Nasdaq API
- `historical-dowjones-constituent` - Historical Dow Jones API

### 📁 **NEW MODULE: Market Performance** (create `market_performance/`)

- `industry-performance-snapshot` - Industry Performance Snapshot API
- `historical-sector-performance` - Historical Market Sector Performance API
- `historical-industry-performance` - Historical Industry Performance API
- `sector-pe-snapshot` - Sector PE Snapshot API
- `industry-pe-snapshot` - Industry PE Snapshot API
- `historical-sector-pe` - Historical Sector PE API
- `historical-industry-pe` - Historical Industry PE API

### 📁 **NEW MODULE: Market Hours** (create `market_hours/`)

- `holidays-by-exchange` - Holidays By Exchange API
- `all-exchange-market-hours` - All Exchange Market Hours API

### 📁 **NEW MODULE: Quote** (create `quote/`)

- `aftermarket-trade` - Aftermarket Trade API
- `aftermarket-quote` - Aftermarket Quote API
- `stock-price-change` - Stock Price Change API
- `batch-quote` - Stock Batch Quote API
- `batch-quote-short` - Stock Batch Quote Short API
- `batch-aftermarket-trade` - Batch Aftermarket Trade API
- `batch-aftermarket-quote` - Batch Aftermarket Quote API
- `batch-exchange-quote` - Exchange Stock Quotes API
- `batch-mutualfund-quotes` - Mutual Fund Price Quotes API
- `batch-etf-quotes` - ETF Price Quotes API

### 📁 **NEW MODULE: COT** (create `cot/`)

- `commitment-of-traders-report` - COT Report API
- `commitment-of-traders-analysis` - COT Analysis By Dates API
- `commitment-of-traders-list` - COT Report List API

### 📁 **NEW MODULE: Earnings Transcript** (create `earnings_transcript/`)

- `earning-call-transcript-latest` - Latest Earning Transcripts API
- `earning-call-transcript` - Earnings Transcript API
- `earning-call-transcript-dates` - Transcripts Dates By Symbol API
- `earnings-transcript-list` - Available Transcript Symbols API (already in market)

### 📁 **NEW MODULE: SEC Filings** (create `sec_filings/`)

- `sec-filings-8k` - Latest 8-K SEC Filings API
- `sec-filings-financials` - Latest SEC Filings API
- `sec-filings-search/form-type` - SEC Filings By Form Type API
- `sec-filings-search/symbol` - SEC Filings By Symbol API
- `sec-filings-search/cik` - SEC Filings By CIK API
- `sec-filings-company-search/name` - SEC Filings By Name API
- `sec-filings-company-search/symbol` - SEC Filings Company Search By Symbol API
- `sec-filings-company-search/cik` - SEC Filings Company Search By CIK API
- `sec-profile` - SEC Company Full Profile API
- `standard-industrial-classification-list` - Industry Classification List API
- `industry-classification-search` - Industry Classification Search API
- `all-industry-classification` - All Industry Classification API

### 📁 **NEW MODULE: Senate** (create `senate/`)

Note: Some endpoints exist in intelligence module, consider moving them
- `senate-latest` - Latest Senate Financial Disclosures API
- `house-latest` - Latest House Financial Disclosures API
- `senate-trades` - Senate Trading Activity API
- `senate-trades-by-name` - Senate Trades By Name API
- `house-trades` - U.S. House Trades API
- `house-trades-by-name` - House Trades By Name API

### 📁 **NEW MODULE: Bulk** (create `bulk/`)

- `profile-bulk` - Company Profile Bulk API
- `rating-bulk` - Stock Rating Bulk API
- `dcf-bulk` - DCF Valuations Bulk API
- `scores-bulk` - Financial Scores Bulk API
- `price-target-summary-bulk` - Price Target Summary Bulk API
- `etf-holder-bulk` - ETF Holder Bulk API
- `upgrades-downgrades-consensus-bulk` - Upgrades Downgrades Consensus Bulk API
- `key-metrics-ttm-bulk` - Key Metrics TTM Bulk API
- `ratios-ttm-bulk` - Ratios TTM Bulk API
- `peers-bulk` - Stock Peers Bulk API
- `earnings-surprises-bulk` - Earnings Surprises Bulk API
- `income-statement-bulk` - Income Statement Bulk API
- `income-statement-growth-bulk` - Income Statement Growth Bulk API
- `balance-sheet-statement-bulk` - Balance Sheet Statement Bulk API
- `balance-sheet-statement-growth-bulk` - Balance Sheet Statement Growth Bulk API
- `cash-flow-statement-bulk` - Cash Flow Statement Bulk API
- `cash-flow-statement-growth-bulk` - Cash Flow Statement Growth Bulk API
- `eod-bulk` - Eod Bulk API

### 📁 **NEW MODULE: ESG** (create `esg/`)

Note: Some ESG endpoints exist in intelligence module, consider moving them
- `esg-disclosures` - ESG Investment Search API

## Summary Count

- **Existing Modules to Update**: 6
- **New Modules to Create**: 11
- **Total Missing Endpoints**: ~130+

## Recommendation Priority

1. **High Priority**: Quote, Market Performance, SEC Filings (commonly used)
2. **Medium Priority**: Bulk, Earnings Transcript, COT, Indexes
3. **Low Priority**: Senate (niche use case)

## Implementation Status

- [ ] Market Module - Directory endpoints
- [ ] Company Module - Additional endpoints
- [ ] Intelligence Module - Analyst & Insider endpoints
- [ ] Institutional Module - Form 13F endpoints
- [ ] Fundamental Module - Statement & DCF endpoints
- [ ] Alternative Module - Batch quote endpoints
- [ ] Indexes Module - Create new module
- [ ] Market Performance Module - Create new module
- [ ] Market Hours Module - Create new module
- [ ] Quote Module - Create new module
- [ ] COT Module - Create new module
- [ ] Earnings Transcript Module - Create new module
- [ ] SEC Filings Module - Create new module
- [ ] Senate Module - Create new module
- [ ] Bulk Module - Create new module
- [ ] ESG Module - Create new module
