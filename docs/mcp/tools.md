# FMP Data MCP Tools Reference

This document lists the MCP tools available in this release.
Tools are organized by client module and include descriptions.

For full FMP endpoint coverage, use the Python client. The MCP tool catalog includes endpoints with MCP tool semantics.

**Counts convention:** each section lists the number of tools in the *catalog*
(everything with MCP semantics, loadable via an explicit manifest), followed by
how many of those are in `DEFAULT_TOOLS` (what a default server registers).
The two differ where a tool is deprecated, redundant, or too heavy for the
default set — `228` catalog tools, `142` default.

**Withdrawn endpoints:** 22 tools name an FMP endpoint that no longer exists.
Probed against the live `stable` API, every one of those paths returns 404, so
the tool can only ever answer with nothing. They remain in the catalog and stay
loadable by explicit manifest, but they are **excluded from `DEFAULT_TOOLS`** —
a default server should not offer a tool that cannot work. Where a live tool
covers the same ground it is named in `WITHDRAWN_TOOLS`, but those are
migrations rather than renames: the payloads differ, so check the fields you
rely on. Seven have no successor at all.

**Tool keys:** a manifest entry may be the bare key (`profile`) or the fully
qualified spec (`company.profile`). The bare form resolves only when exactly
one client claims that key. Two keys are claimed by two clients each and must
always be written in full: `crypto_quotes` (`alternative.crypto_quotes` vs
`batch.crypto_quotes`) and `forex_quotes` (`alternative.forex_quotes` vs
`batch.forex_quotes`). Rows marked *Deprecated* below still resolve but emit a
`DeprecationWarning` and are removed in 3.0.

## Table of Contents

- [Alternative (15 tools, 12 default)](#alternative)
- [Batch (30 tools, 0 default)](#batch)
- [Company (33 tools, 22 default)](#company)
- [Economics (7 tools, 7 default)](#economics)
- [Fundamental (14 tools, 12 default)](#fundamental)
- [Index (6 tools, 0 default)](#index)
- [Institutional (12 tools, 8 default)](#institutional)
- [Intelligence (49 tools, 42 default)](#intelligence)
- [Investment (14 tools, 9 default)](#investment)
- [Market (23 tools, 21 default)](#market)
- [SEC (12 tools, 0 default)](#sec)
- [Technical (9 tools, 9 default)](#technical)
- [Transcripts (4 tools, 0 default)](#transcripts)

## Alternative

**15 tools** for alternative data access (12 default).

| Tool Key | Description |
|----------|-------------|
| `commodities_list` | Get a list of all available commodities |
| `commodities_quotes` | Get current quotes for all available commodities |
| `commodity_historical` | Get historical price data for a commodity |
| `commodity_intraday` | Get intraday price data for commodities |
| `commodity_quote` | Get detailed quote for a specific commodity |
| `crypto_historical` | Retrieve historical price data for a cryptocurrency |
| `crypto_intraday` | Get detailed intraday price data for a cryptocurrency |
| `crypto_list` | Get a list of all available cryptocurrencies and their basic information |
| `crypto_quote` | Get detailed real-time quote for a specific cryptocurrency |
| `crypto_quotes` | Get current price quotes for all available cryptocurrencies |
| `forex_historical` | Get historical exchange rate data for a currency pair |
| `forex_intraday` | Get intraday exchange rate data at specified intervals |
| `forex_list` | Get a complete list of available forex currency pairs |
| `forex_quote` | Get detailed real-time quote for a specific currency pair |
| `forex_quotes` | Get real-time quotes for all available forex currency pairs |

## Batch

**30 tools** for multi-symbol and bulk downloads (0 default — load explicitly
via a manifest; these return large payloads and several are CSV).

| Tool Key | Description |
|----------|-------------|
| `aftermarket_quotes` | Get aftermarket quote data for multiple symbols. Returns current prices and quotes from after-hours trading sessions. |
| `aftermarket_trades` | Get aftermarket (post-market) trade data for multiple symbols. Returns trading activity that occurred after regular market hours. |
| `balance_sheet_bulk` | Get bulk balance sheet statements. Returns comprehensive balance sheet data for many companies. |
| `balance_sheet_growth_bulk` | Get bulk balance sheet growth data. Returns year-over-year growth metrics for balance sheet items. |
| `batch_quote` | Get real-time quotes for multiple symbols in a single request. Get current price, volume, and market data for many stocks. |
| `batch_quote_short` | Get quick price snapshots for multiple symbols. Fast, lightweight quotes with essential price information. |
| `cash_flow_bulk` | Get bulk cash flow statements. Returns comprehensive cash flow data for many companies. |
| `cash_flow_growth_bulk` | Get bulk cash flow growth data. Returns year-over-year growth metrics for cash flow items. |
| `commodity_quotes` | Get batch quotes for all commodities. Returns prices for gold, silver, oil, and other commodity futures. |
| `crypto_quotes` | Get batch quotes for all cryptocurrencies. Returns crypto market data including Bitcoin, Ethereum, etc. |
| `dcf_bulk` | Get discounted cash flow valuations in bulk. Returns DCF analysis and intrinsic value calculations for many companies. |
| `earnings_surprises_bulk` | Get bulk earnings surprises for a given year. Returns actual vs expected earnings data for many companies. |
| `eod_bulk` | Get bulk end-of-day prices. Returns closing price data for all stocks for a specific date. |
| `etf_holder_bulk` | Get bulk ETF holdings. Returns comprehensive ETF holding data for many funds. |
| `etf_quotes` | Get batch quotes for all ETFs. Returns comprehensive quote data for entire ETF universe. |
| `exchange_quotes` | Get quotes for all stocks on a specific exchange. Returns market data for entire exchange (NYSE, NASDAQ, etc.). |
| `forex_quotes` | Get batch quotes for all forex pairs. Returns comprehensive foreign exchange rate data for all currency pairs. |
| `income_statement_bulk` | Get bulk income statements. Returns comprehensive income statement data for many companies. |
| `income_statement_growth_bulk` | Get bulk income statement growth data. Returns year-over-year growth metrics for income statement items. |
| `index_quotes` | Get batch quotes for all market indexes. Returns data for S&P 500, Dow Jones, NASDAQ, and other indexes. |
| `key_metrics_ttm_bulk` | Get bulk trailing twelve month key metrics. Returns comprehensive financial metrics and KPIs for many companies. |
| `market_caps` | Get market capitalization for multiple symbols. Returns current market cap values for specified companies. |
| `mutualfund_quotes` | Get batch quotes for all mutual funds. Returns comprehensive quote data for entire mutual fund universe. |
| `peers_bulk` | Get bulk peer lists. Returns peer company data and competitor lists for many companies. |
| `price_target_summary_bulk` | Get bulk price target summaries. Returns analyst price target data and consensus for many stocks. |
| `profile_bulk` | Get company profile data in bulk (CSV format). Returns comprehensive company information for many companies at once. |
| `rating_bulk` | Get stock ratings in bulk. Returns comprehensive rating data and recommendations for many stocks. |
| `ratios_ttm_bulk` | Get trailing twelve month financial ratios in bulk. Returns comprehensive financial ratio analysis for many companies. |
| `scores_bulk` | Get financial scores in bulk. Returns Piotroski F-Score and Altman Z-Score for many companies. |
| `upgrades_downgrades_consensus_bulk` | Get bulk upgrades/downgrades consensus data. Returns analyst rating changes and consensus for many stocks. |

## Company

**33 tools** for company information and quotes (22 default).

| Tool Key | Description |
|----------|-------------|
| `aftermarket_quote` | Get after-hours bid/ask quote data for a stock with sizes, prices, and timestamp |
| `aftermarket_trade` | Get after-hours trade data for a stock, including price, size, and trade timestamp |
| `analyst_estimates` | Retrieve detailed analyst estimates including revenue, earnings, EBITDA, and other financial metrics forecasts with high/low/average ranges |
| `analyst_recommendations` | Retrieve analyst buy/sell/hold recommendations and consensus ratings for stocks including detailed rating breakdowns |
| `company_logo_url` | Get the URL of the company's official logo image for use in applications, websites, or documentation |
| `company_notes` | Retrieve company financial notes and disclosures from SEC filings, providing additional context and explanations about financial statements |
| `core_information` | Get essential company information including CIK number, exchange listing, SIC code, state of incorporation, and fiscal year details |
| `delisted_companies` | Get companies FMP reports as delisted, including the last exchange, IPO date, and delist date |
| `employee_count` | Get historical employee count data showing how company workforce has changed over time |
| `executive_compensation` | Get detailed executive compensation information including salary, bonuses, stock awards, and total compensation packages for company leaders |
| `executives` | *Deprecated — use `key_executives`; removed in 3.0.* Get detailed information about company's key executives including their names, titles, compensation, and tenure. |
| `geographic_revenue_segmentation` | Get revenue breakdown by geographic regions, showing how company revenue is distributed across different countries and regions |
| `historical_market_cap` | Retrieve historical market capitalization data to track changes in company value over time |
| `historical_price` | *Deprecated — use `historical_prices`; removed in 3.0.* Retrieve historical daily price data including open, high, low, close, and adjusted prices with volume information . |
| `historical_prices` | Retrieve historical price data including OHLCV (Open, High, Low, Close, Volume) information for detailed technical and performance analysis. |
| `historical_share_float` | Get historical share float data showing how the number of tradable shares has changed over time |
| `intraday_price` | *Deprecated — use `intraday_prices`; removed in 3.0.* Get intraday price data at various intervals (1min to 4hour) for detailed analysis of price movements within the trading day |
| `intraday_prices` | Get intraday price data with minute-by-minute or hourly intervals |
| `key_executives` | Get detailed information about company's key executives including their names, titles, tenure, and basic compensation data |
| `market_cap` | Get current market capitalization data for a company, including total market value and related metrics |
| `price_target` | Retrieve analyst price targets for a specific stock, including target prices, analyst details, and publication dates |
| `price_target_consensus` | Get detailed consensus information about analyst price targets, including target distribution, recent changes, and analyst recommendations. |
| `price_target_summary` | Get a summary of analyst price targets for a stock, including average, highest, and lowest targets along with number of analysts. |
| `product_revenue_segmentation` | Get detailed revenue breakdown by product lines or services, showing how company revenue is distributed across different offerings |
| `profile` | Get detailed company profile information including financial metrics, company description, sector, industry, and contact information |
| `profile_cik` | Get detailed company profile information using CIK number, including financial metrics, company description, sector, industry, and contact information |
| `quote` | Get real-time stock quote data including current price, volume, day range, and other key market metrics |
| `share_float` | Get current share float data showing the number and percentage of shares available for public trading |
| `simple_quote` | Get real-time basic stock quote including price, volume, and change information |
| `stock_price_change` | Get percentage price changes across multiple time horizons for a stock |
| `symbol_changes` | Get historical record of company ticker symbol changes, tracking when and why companies changed their trading symbols |
| `upgrades_downgrades` | Access stock rating changes including upgrades, downgrades, and rating adjustments with analyst and firm information |
| `upgrades_downgrades_consensus` | Get aggregated rating consensus data including buy/sell/hold counts and overall recommendation trends |

## Economics

**7 tools** for economic indicators (7 default).

| Tool Key | Description |
|----------|-------------|
| `commitment_of_traders_analysis` | Analyze COT reports for a symbol over a date range to assess sentiment and potential reversals |
| `commitment_of_traders_list` | List available Commitment of Traders (COT) symbols |
| `commitment_of_traders_report` | Retrieve Commitment of Traders (COT) reports for a given futures contract over a specified date range |
| `economic_calendar` | Access a comprehensive calendar of economic events, data releases, and policy announcements. |
| `economic_indicators` | Access comprehensive economic indicator data including GDP, inflation, employment statistics, trade balances, and more. |
| `market_risk_premium` | Retrieve comprehensive market risk premium data by country, including equity risk premiums, country-specific risk factors, and total risk premiums |
| `treasury_rates` | Retrieve U.S. Treasury rates across multiple maturities including bills, notes, and bonds. |

## Fundamental

**14 tools** for fundamental analysis and valuation (12 default).

| Tool Key | Description |
|----------|-------------|
| `balance_sheet` | Access detailed balance sheet statements showing a company's assets, liabilities, and shareholders' equity. |
| `cash_flow` | Retrieve detailed cash flow statements showing operating, investing, and financing activities. |
| `custom_discounted_cash_flow` | Perform advanced DCF analysis with detailed cash flow projections, growth rates, WACC calculations, and terminal value assumptions. |
| `custom_levered_dcf` | Calculate levered DCF valuation using free cash flow to equity (FCFE) with detailed projections and cost of equity calculations. |
| `discounted_cash_flow` | Calculate discounted cash flow valuation to determine the intrinsic value of a company based on projected future cash flows. |
| `financial_ratios` | Access comprehensive financial ratios for analyzing company performance, efficiency, and financial health. |
| `financial_reports_dates` | Retrieve available financial report dates and access links for a company, including quarterly and annual filings. |
| `full_financial_statement` | Access complete financial statements as reported to regulatory authorities, including detailed line items, notes, and supplementary information. |
| `historical_rating` | Retrieve historical company ratings and scoring metrics over time based on fundamental analysis. |
| `income_statement` | Retrieve detailed income statements showing revenue, costs, expenses and profitability metrics for a company over multiple periods. |
| `key_metrics` | Access essential financial metrics and KPIs including profitability, efficiency, and valuation measures. |
| `latest_financial_statements` | Get the latest financial statement publication metadata across symbols with pagination. |
| `levered_dcf` | Perform levered discounted cash flow valuation with detailed assumptions about growth, cost of capital, and future cash flows. |
| `owner_earnings` | Calculate owner earnings using Warren Buffett's methodology to evaluate true business profitability and cash generation capability. |

## Index

**6 tools** for index constituents (0 default — load explicitly via a manifest).

| Tool Key | Description |
|----------|-------------|
| `dowjones_constituents` | Get current Dow Jones Industrial Average constituents. Returns list of 30 companies currently included in the DJIA. |
| `historical_dowjones` | Get historical Dow Jones constituent changes. Returns list of additions and removals from the DJIA over time. |
| `historical_nasdaq` | Get historical NASDAQ constituent changes. Returns list of additions and removals from the NASDAQ index over time. |
| `historical_sp500` | Get historical S&P 500 constituent changes. Returns list of additions and removals from the S&P 500 over time. |
| `nasdaq_constituents` | Get current NASDAQ index constituents. Returns companies currently in the NASDAQ composite index. |
| `sp500_constituents` | Get current S&P 500 index constituents. Returns list of companies currently included in the S&P 500 index. |

## Institutional

**12 tools** for institutional and insider data (8 default).

| Tool Key | Description |
|----------|-------------|
| `asset_allocation` | Analyze asset allocation data from 13F filings |
| `beneficial_ownership` | Retrieve beneficial ownership information including voting rights and dispositive power for major shareholders of a company. |
| `cik_mappings` | Get a comprehensive mapping between CIK numbers and company/institution names. |
| `fail_to_deliver` | Get data on failed trade settlements (FTDs) for a security. |
| `form_13f` | Retrieve Form 13F filings data for institutional investment managers, including detailed holdings information, share quantities, and market values. |
| `form_13f_dates` | Get a list of available Form 13F filing dates for a specific institutional investment manager, helping track their reporting history and timeline. |
| `insider_roster` | Get a list of company insiders including executives, directors, and major shareholders, along with their positions and latest transaction dates. |
| `insider_statistics` | Get aggregated statistics about insider trading activity. |
| `insider_trades` | Track insider trading activity for a specific security. |
| `institutional_holders` | Get detailed information about institutional holders of securities. |
| `institutional_holdings` | Analyze institutional ownership for a specific security. |
| `transaction_types` | Get a reference list of insider transaction types and their descriptions. |

## Intelligence

**49 tools** for news, sentiment, market events, and analyst ratings/grades (42 default).

| Tool Key | Description |
|----------|-------------|
| `crowdfunding_by_cik` | Retrieve crowdfunding offerings for a specific company using CIK with complete offering details |
| `crowdfunding_rss` | Access latest crowdfunding offerings and campaigns including funding details, company information, and offering terms |
| `crowdfunding_search` | Search crowdfunding offerings and campaigns by company name with detailed offering information |
| `crypto_news` | Access cryptocurrency news articles including market updates, trading information, and digital asset developments |
| `crypto_symbol_news` | Search cryptocurrency news for a specific trading pair to track asset-specific developments |
| `dividends_calendar` | Get upcoming and historical dividend events including ex-dividend dates, payment dates, and dividend amounts |
| `earnings_calendar` | Access comprehensive earnings calendar showing upcoming earnings releases, estimated and actual results, and historical earnings data |
| `earnings_confirmed` | **Deprecated / not in DEFAULT_TOOLS** — client returns `[]`; prefer `earnings_calendar` + `include_report_times` |
| `earnings_surprises` | **Deprecated / not in DEFAULT_TOOLS** — client returns `[]`; prefer `historical_earnings` and compare eps |
| `equity_offering_by_cik` | Retrieve equity offerings for a specific company using CIK number including historical and current offerings |
| `equity_offering_rss` | Get latest equity offerings including new issues, follow-on offerings, and capital raising events |
| `equity_offering_search` | Search for equity offerings including public and private placements, with detailed offering terms and company information |
| `esg_benchmark` | Retrieve industry ESG benchmarks and sector averages for environmental, social, and governance metrics |
| `esg_data` | Retrieve detailed ESG (Environmental, Social, Governance) metrics and scores for companies including component breakdowns and benchmarks |
| `esg_ratings` | Access company ESG ratings and scores including environmental, social, and governance performance metrics and industry rankings |
| `fmp_articles` | Access Financial Modeling Prep articles including market analysis, company research, and financial insights |
| `forex_news` | Retrieve forex market news including currency pair updates, exchange rate movements, and international market developments |
| `forex_symbol_news` | Search forex news for a specific currency pair to monitor pair-specific developments and analysis |
| `general_news` | Retrieve general financial news and market updates from various sources covering markets, economy, and business |
| `grades` | Get analyst grade actions for a company, including upgrades, downgrades and the firms behind them |
| `grades_consensus` | Get the current analyst grade consensus for a company, summarizing buy, hold and sell counts and the overall consensus |
| `grades_historical` | Retrieve the historical distribution of analyst grades for a company across buy, hold and sell buckets over time |
| `grades_latest_news` | Get the latest analyst grade news across all companies, covering recent upgrades and downgrades market-wide |
| `grades_news` | Get news articles covering analyst grade changes for a specific company, with previous and new grades |
| `historical_earnings` | Historical/upcoming earnings for a symbol (optional `limit`, `include_report_times`) |
| `historical_social_sentiment` | **Removed / not in DEFAULT_TOOLS** — raises `RemovedEndpointError` |
| `house_disclosure` | Access House of Representatives trading disclosures including transaction details, filing information, and trade specifics |
| `house_latest` | Get the latest House financial disclosures with transaction details |
| `house_trades_by_id` | Get House trading data filtered by member id |
| `house_trades_by_name` | Get House trading data filtered by representative name |
| `ipo_calendar` | Retrieve upcoming and recent IPO events including pricing details, offering sizes, and listing dates |
| `press_releases` | Retrieve corporate press releases and official company announcements with detailed content and publication information |
| `press_releases_by_symbol` | Retrieve company-specific press releases and official announcements including corporate events and updates |
| `price_target_latest_news` | Get the latest price target news across all companies, covering recent analyst target changes market-wide |
| `price_target_news` | Get news articles covering analyst price target changes for a specific company, with the new and prior targets |
| `ratings_historical` | Retrieve historical analyst ratings for a company to track how the rating and its component scores changed over time |
| `ratings_snapshot` | Get the current analyst rating snapshot for a company, including the overall rating and component scores |
| `senate_latest` | Get the latest Senate financial disclosures with transaction details |
| `senate_positions` | Get Congress member term history |
| `senate_profile` | List Congress member profiles |
| `senate_trades_by_id` | Get Senate trading data filtered by member id |
| `senate_trades_by_name` | Get Senate trading data filtered by senator name |
| `senate_trading` | Access Senate trading activity and disclosures including stock trades, transaction details, and filing information |
| `senate_trading_rss` | Get real-time RSS feed of Senate trading disclosures including new filings and transaction updates |
| `social_sentiment_changes` | **Removed / not in DEFAULT_TOOLS** — raises `RemovedEndpointError` |
| `stock_news` | Market-wide stock news feed of company events and corporate developments. Not filterable by symbol; narrow it by date range or page |
| `stock_news_sentiments` | **Deprecated / not in DEFAULT_TOOLS** — client returns `[]` |
| `stock_splits_calendar` | Access upcoming and historical stock split events including split ratios, dates, and affected securities |
| `trending_social_sentiment` | **Removed / not in DEFAULT_TOOLS** — raises `RemovedEndpointError` |

## Investment

**14 tools** for ETFs and mutual funds (9 default).

| Tool Key | Description |
|----------|-------------|
| `etf_country_weightings` | Get detailed geographic allocation data for an ETF, showing the percentage of the portfolio invested in different countries |
| `etf_exposure` | Retrieve detailed stock exposure data for an ETF, showing specific securities held and their weights in the portfolio |
| `etf_holder` | Get information about institutional holders of an ETF, including their holdings and position sizes |
| `etf_holding_dates` | Get a list of available portfolio dates for which ETF holdings data is available |
| `etf_holdings` | Retrieve detailed holdings information for an ETF including assets, weights, and market values as of a specific date |
| `etf_info` | Get comprehensive information about an ETF including expense ratio, assets under management, and fund characteristics |
| `etf_sector_weightings` | Retrieve detailed sector allocation data for an ETF, showing the percentage of the portfolio invested in different market sectors |
| `fund_disclosure` | Retrieve detailed fund disclosure holdings for a symbol and reporting period, including security metadata and portfolio percentages |
| `fund_disclosure_holders_latest` | Retrieve the latest fund disclosure holders for a symbol, including holder name, shares, and weight percentage |
| `fund_disclosure_holders_search` | Search fund disclosure holders by name to retrieve fund identifiers and entity details |
| `mutual_fund_by_name` | Search for mutual funds by name to get their holdings and basic information |
| `mutual_fund_dates` | Retrieve available portfolio dates for mutual fund holdings data, helping track portfolio composition changes over time |
| `mutual_fund_holder` | Get information about institutional holders of a mutual fund, including their holdings and position sizes |
| `mutual_fund_holdings` | Get detailed holdings information for a mutual fund, including securities held, weights, and market values as of a specific date |

## Market

**23 tools** for market data and search (21 default).

| Tool Key | Description |
|----------|-------------|
| `all_exchange_market_hours` | Get trading hours for all exchanges to compare schedules at once |
| `all_shares_float` | Get comprehensive share float data for all companies, showing the number and percentage of shares available for public trading |
| `available_indexes` | Get a list of all available market indexes including major stock market indices, sector indexes, and other benchmark indicators |
| `etf_list` | Get a complete list of all available ETFs (Exchange Traded Funds) with their basic information including symbol, name, and trading details |
| `gainers` | Get list of top gaining stocks by percentage change, showing the best performing stocks in the current trading session |
| `historical_industry_pe` | Retrieve historical industry price-to-earnings ratios over a date range |
| `historical_industry_performance` | Retrieve historical industry performance over a date range for trend and rotation analysis |
| `historical_sector_pe` | Retrieve historical sector price-to-earnings ratios over a date range |
| `historical_sector_performance` | Retrieve historical sector performance over a date range for trend and rotation analysis |
| `holidays_by_exchange` | Get exchange holiday dates for a specific exchange |
| `industry_pe_snapshot` | Get industry price-to-earnings snapshots for a specific date, optionally filtered by exchange or industry |
| `industry_performance_snapshot` | Get a snapshot of industry performance, including average changes by industry for a specific date and optional exchange |
| `losers` | Get list of top losing stocks by percentage change, showing the worst performing stocks in the current trading session |
| `market_hours` | Check current market status and trading hours for a specific exchange |
| `most_active` | Get list of most actively traded stocks by volume, showing stocks with the highest trading activity in the current session |
| `pre_post_market` | Retrieve pre-market and post-market trading data including prices, volume, and trading session information outside regular market hours |
| `search` | Search for companies by name, ticker, or other identifiers. |
| `search_by_cik` | Search for companies by their SEC Central Index Key (CIK) number |
| `search_by_cusip` | Search for companies by their CUSIP identifier |
| `search_by_isin` | Search for companies by their International Securities Identification Number (ISIN) |
| `sector_pe_snapshot` | Get sector price-to-earnings snapshots for a specific date, optionally filtered by exchange or sector |
| `sector_performance` | Get performance data for major market sectors, showing relative strength and weakness across different areas of the market |
| `stock_list` | Get a complete list of all available stocks in the market including their basic information such as symbol, name, and exchange listing |

## SEC

**12 tools** for SEC filings and registration data (0 default — load explicitly
via a manifest).

| Tool Key | Description |
|----------|-------------|
| `all_industry_classification` | Get all industry classification records. Returns industry classifications for all registered companies. |
| `company_search_cik` | Search SEC-registered companies by CIK number. Returns company SEC registration information by Central Index Key. |
| `company_search_name` | Search SEC-registered companies by name. Returns companies matching the search term in their registered name. |
| `company_search_symbol` | Search SEC-registered companies by stock symbol. Returns SEC registration information for a specific ticker symbol. |
| `filings_8k` | Get the latest SEC 8-K filings (material events). Returns recent 8-K filings which companies file to announce major events. |
| `filings_financials` | Get the latest SEC financial filings (10-K, 10-Q). Returns recent financial filings (annual and quarterly reports). |
| `filings_search_cik` | Search SEC filings by CIK number (Central Index Key). Returns all SEC filings for a company identified by CIK. |
| `filings_search_form` | Search SEC filings by form type (e.g., 10-K, 10-Q, 8-K, S-1). Returns filings matching the specified SEC form type. |
| `filings_search_symbol` | Search SEC filings by stock symbol. Returns all SEC filings for a specific company identified by stock ticker. |
| `industry_classification_search` | Search industry classification data by symbol, CIK, or SIC code. Returns industry classification information for companies. |
| `sec_profile` | Get SEC profile with CIK, SIC codes, and registration details. |
| `sic_codes` | Get list of all Standard Industrial Classification (SIC) codes. Returns complete SIC code directory used by the SEC. |

## Technical

**9 tools** for technical indicators (9 default).

| Tool Key | Description |
|----------|-------------|
| `adx` | Calculate Average Directional Index (ADX). |
| `dema` | Calculate Double Exponential Moving Average (DEMA). |
| `ema` | Calculate Exponential Moving Average (EMA) for a security. |
| `rsi` | Calculate Relative Strength Index (RSI). |
| `sma` | Calculate Simple Moving Average (SMA) for a given security. |
| `standard_deviation` | Calculate price Standard Deviation to measure volatility and dispersion. |
| `tema` | Calculate Triple Exponential Moving Average (TEMA). |
| `williams` | Calculate Williams %R indicator. This momentum indicator measures overbought and oversold levels. |
| `wma` | Calculate Weighted Moving Average (WMA). |

## Transcripts

**4 tools** for earnings call transcripts (0 default — load explicitly via a
manifest; transcript bodies are large).

| Tool Key | Description |
|----------|-------------|
| `latest_transcripts` | Get the most recent earnings call transcripts across all companies. Returns latest conference call transcripts with full text content. |
| `transcript` | Get earnings call transcript for a specific company and quarter. Returns full text of earnings conference call for specified fiscal period. |
| `transcript_dates` | Get available transcript dates for a specific company. Returns list of dates when earnings call transcripts are available. |
| `transcript_symbols` | Get list of all symbols with available earnings transcripts. Returns companies that have earnings call transcripts available. |
