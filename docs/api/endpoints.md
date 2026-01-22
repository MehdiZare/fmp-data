# FMP API Endpoints (Stable)

This document reflects 100% coverage of the FMP stable endpoint catalog as implemented in `fmp-data`.

All endpoints use the `/stable` prefix unless explicitly marked as `DIRECT` or `IMAGE`.

## Table of Contents

- [Company (58 endpoints)](#company)
- [Market (36 endpoints)](#market)
- [Fundamental (14 endpoints)](#fundamental)
- [Technical (9 endpoints)](#technical)
- [Market Intelligence (47 endpoints)](#market-intelligence)
- [Institutional (25 endpoints)](#institutional)
- [Investment (14 endpoints)](#investment)
- [Alternative Markets (15 endpoints)](#alternative-markets)
- [Economics (7 endpoints)](#economics)
- [Batch (30 endpoints)](#batch)
- [Transcripts (4 endpoints)](#transcripts)
- [SEC (12 endpoints)](#sec)
- [Index (6 endpoints)](#index)

## Company

**58 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `aftermarket_quote` | `/stable/aftermarket-quote` | Get aftermarket (post-market) quote data for a symbol |
| `aftermarket_trade` | `/stable/aftermarket-trade` | Get aftermarket (post-market) trade data for a symbol |
| `analyst_estimates` | `/stable/analyst-estimates` | Get analyst estimates |
| `analyst_recommendations` | `/stable/analyst-stock-recommendations` | Get analyst recommendations |
| `balance_sheet_as_reported` | `/stable/balance-sheet-statement-as-reported` | Get balance sheet as originally reported without adjustments. Shows exact figures from company filings. |
| `balance_sheet_growth` | `/stable/balance-sheet-statement-growth` | Get year-over-year growth rates for balance sheet line items. Shows how assets, liabilities, and equity are changing. |
| `balance_sheet_ttm` | `/stable/balance-sheet-statement-ttm` | Get trailing twelve months (TTM) balance sheet data. Shows the company's current financial position. |
| `cash_flow_as_reported` | `/stable/cash-flow-statement-as-reported` | Get cash flow statement as originally reported without adjustments. Shows exact figures from company filings. |
| `cash_flow_growth` | `/stable/cash-flow-statement-growth` | Get year-over-year growth rates for cash flow statement line items. Shows trends in operating, investing, and financing cash flows. |
| `cash_flow_ttm` | `/stable/cash-flow-statement-ttm` | Get trailing twelve months (TTM) cash flow statement data. Shows how cash moves through the company over the past 12 months. |
| `core_information` | `/stable/company-core-information` | Retrieve essential company information including CIK, exchange, SIC code, state of incorporation, and fiscal year details. Provides core regulatory and administrative information about a company. |
| `company_notes` | `/stable/company-notes` | Retrieve company financial notes and disclosures. These notes provide additional context and detailed explanations about company financial statements and important events. |
| `company_outlook` | `/stable/company-outlook` | Get comprehensive company outlook data |
| `delisted_companies` | `/stable/delisted-companies` | Get list of delisted companies |
| `company_dividends` | `/stable/dividends` | Get historical dividend payments for a specific company. Includes ex-dividend dates, payment dates, and dividend amounts. |
| `company_earnings` | `/stable/earnings` | Get historical earnings reports for a specific company. Includes actual EPS, estimated EPS, revenue, and earnings dates. |
| `employee_count` | `/stable/employee-count` | Get historical employee count data for a company. Tracks how the company's workforce has changed over time, providing insights into company growth and operational scale. |
| `enterprise_values` | `/stable/enterprise-values` | Get historical enterprise value data including market cap, debt, cash positions, and calculated enterprise value. |
| `executive_compensation_benchmark` | `/stable/executive-compensation-benchmark` | Get executive compensation benchmark data by industry and year |
| `financial_growth` | `/stable/financial-growth` | Get comprehensive financial growth metrics across all statements. Combines income, balance sheet, and cash flow growth rates. |
| `financial_reports_json` | `/stable/financial-reports-json` | Get Form 10-K financial reports in JSON format. Provides structured access to annual report data. |
| `financial_reports_xlsx` | `/stable/financial-reports-xlsx` | Get Form 10-K financial reports in Excel format. Returns a downloadable XLSX file with financial data. |
| `financial_scores` | `/stable/financial-scores` | Get comprehensive financial health scores including Altman Z-Score, Piotroski Score, and other financial strength indicators. |
| `executive_compensation` | `/stable/governance-executive-compensation` | Get detailed executive compensation data including salary, bonuses, stock awards, and total compensation. Provides insights into how company executives are compensated. |
| `intraday_price` | `/stable/historical-chart/{interval}` | Get intraday price data |
| `historical_market_cap` | `/stable/historical-market-capitalization` | Get historical market capitalization data |
| `historical_price` | `/stable/historical-price-eod` | Get historical daily price data |
| `historical_price_dividend_adjusted` | `/stable/historical-price-eod/dividend-adjusted` | Get historical daily price data adjusted for dividends |
| `historical_price_light` | `/stable/historical-price-eod/light` | Get lightweight historical daily price data (OHLC only) |
| `historical_price_non_split_adjusted` | `/stable/historical-price-eod/non-split-adjusted` | Get historical daily price data without split adjustments |
| `historical_employee_count` | `/stable/historical/employee-count` | Get historical employee count data |
| `historical_share_float` | `/stable/historical/shares-float` | Get historical share float data showing how the number of tradable shares has changed over time. Useful for analyzing changes in stock liquidity and institutional ownership patterns over time. |
| `income_statement_as_reported` | `/stable/income-statement-as-reported` | Get income statement as originally reported without adjustments. Shows exact figures from company filings. |
| `income_statement_growth` | `/stable/income-statement-growth` | Get year-over-year growth rates for income statement line items. Shows how revenue, expenses, and profits are growing. |
| `income_statement_ttm` | `/stable/income-statement-ttm` | Get trailing twelve months (TTM) income statement data. Provides the most recent 12-month financial performance metrics. |
| `key_executives` | `/stable/key-executives` | Get detailed information about a company's key executives including their names, titles, compensation, and tenure. Provides insights into company leadership, management structure, and executive compensation. |
| `key_metrics_ttm` | `/stable/key-metrics-ttm` | Get trailing twelve months (TTM) key financial metrics. Includes important ratios and performance indicators. |
| `market_cap` | `/stable/market-capitalization` | Get market capitalization data |
| `mergers_acquisitions_latest` | `/stable/mergers-acquisitions-latest` | Get latest mergers and acquisitions transactions |
| `mergers_acquisitions_search` | `/stable/mergers-acquisitions-search` | Search mergers and acquisitions transactions by company name |
| `price_target` | `/stable/price-target` | Get price targets |
| `price_target_consensus` | `/stable/price-target-consensus` | Get price target consensus |
| `price_target_summary` | `/stable/price-target-summary` | Get price target summary |
| `profile` | `/stable/profile` | Get comprehensive company profile including financial metrics, description, sector, industry, contact information, and basic market data. Provides a complete overview of a company's business and current market status. |
| `profile_cik` | `/stable/profile-cik` | Get company profile using CIK number |
| `quote` | `/stable/quote` | Get real-time stock quote |
| `simple_quote` | `/stable/quote-short` | Get simple stock quote |
| `financial_ratios_ttm` | `/stable/ratios-ttm` | Get trailing twelve months (TTM) financial ratios. Includes profitability, liquidity, leverage, and efficiency ratios. |
| `geographic_revenue_segmentation` | `/stable/revenue-geographic-segmentation` | Get revenue segmentation by geographic region. Shows how company revenue is distributed across different countries and regions, providing insights into geographical diversification and market exposure. |
| `product_revenue_segmentation` | `/stable/revenue-product-segmentation` | Get detailed revenue segmentation by product or service line. Shows how company revenue is distributed across different products and services, helping understand revenue diversification and key product contributions. |
| `share_float` | `/stable/shares-float` | Get current share float data including number of shares available for trading and percentage of total shares outstanding. Important for understanding stock liquidity and institutional ownership. |
| `company_splits` | `/stable/splits` | Get historical stock split information for a specific company. Includes split dates, ratios (numerator/denominator), and split details. |
| `stock_peers/{symbol}` | `/stable/stock-peers` | Retrieves a list of peers of a company. |
| `stock_price_change` | `/stable/stock-price-change` | Get price change percentages across multiple time horizons |
| `stock_screener` | `/stable/stock-screener` | Screen stocks based on various criteria |
| `symbol_changes` | `/stable/symbol-change` | Get historical record of company symbol changes. Tracks when and why companies changed their ticker symbols, useful for maintaining accurate historical data and understanding corporate actions. |
| `upgrades_downgrades` | `/stable/upgrades-downgrades` | Get upgrades and downgrades |
| `upgrades_downgrades_consensus` | `/stable/upgrades-downgrades-consensus` | Get upgrades and downgrades consensus |

## Market

**36 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `actively_trading_list` | `/stable/actively-trading-list` | Get list of actively trading stocks |
| `all_exchange_market_hours` | `/stable/all-exchange-market-hours` | Get market trading hours for all exchanges |
| `available_countries` | `/stable/available-countries` | Get a comprehensive list of available countries |
| `available_exchanges` | `/stable/available-exchanges` | Get a complete list of supported stock exchanges |
| `available_industries` | `/stable/available-industries` | Get a comprehensive list of available industries |
| `available_sectors` | `/stable/available-sectors` | Get a complete list of industry sectors |
| `gainers` | `/stable/biggest-gainers` | Get market gainers |
| `losers` | `/stable/biggest-losers` | Get market losers |
| `cik_list` | `/stable/cik-list` | Get complete list of all CIK numbers |
| `company_screener` | `/stable/company-screener` | Screen companies based on various criteria |
| `etf_list` | `/stable/etf-list` | Get a complete list of all available ETFs (Exchange Traded Funds) with their basic information. Provides a comprehensive view of tradable ETF products. |
| `market_hours` | `/stable/exchange-market-hours` | Get market trading hours information |
| `financial_statement_symbol_list` | `/stable/financial-statement-symbol-list` | Get list of symbols with financial statements available |
| `historical_industry_pe` | `/stable/historical-industry-pe` | Get historical industry PE data |
| `historical_industry_performance` | `/stable/historical-industry-performance` | Get historical industry performance data |
| `historical_sector_pe` | `/stable/historical-sector-pe` | Get historical sector PE data |
| `historical_sector_performance` | `/stable/historical-sector-performance` | Get historical sector performance data |
| `holidays_by_exchange` | `/stable/holidays-by-exchange` | Get market holidays for a specific exchange |
| `available_indexes` | `/stable/index-list` | Get a comprehensive list of all available market indexes including major stock market indices, sector indexes, and other benchmark indicators. Provides information about tradable and trackable market indexes along with their basic details such as name, currency, and exchange. |
| `industry_pe_snapshot` | `/stable/industry-pe-snapshot` | Get industry PE snapshot data |
| `industry_performance_snapshot` | `/stable/industry-performance-snapshot` | Get industry performance data |
| `ipo_disclosure` | `/stable/ipos-disclosure` | Get IPO disclosure documents and filing information for companies going public. Includes disclosure URLs, filing dates, and IPO details. |
| `ipo_prospectus` | `/stable/ipos-prospectus` | Get IPO prospectus documents and detailed offering information for companies going public. Includes prospectus URLs, offer prices, and proceeds data. |
| `most_active` | `/stable/most-actives` | Get most active stocks |
| `pre_post_market` | `/stable/pre-post-market` | Get pre/post market data |
| `cik_search` | `/stable/search-cik` | Search for companies by their CIK (Central Index Key) number. Useful for finding companies using their SEC identifier and accessing regulatory filings. |
| `cusip_search` | `/stable/search-cusip` | Search for companies by their CUSIP (Committee on Uniform Securities Identification Procedures) number. Helps identify securities using their unique identifier. |
| `search_exchange_variants` | `/stable/search-exchange-variants` | Search for exchange trading variants of a company |
| `isin_search` | `/stable/search-isin` | Search for companies by their ISIN (International Securities Identification Number). Used to find securities using their globally unique identifier. |
| `search-name` | `/stable/search-name` | Search for companies by name, ticker, or other identifiers. Returns matching companies with their basic information including symbol, name, and exchange. Useful for finding companies based on keywords or partial matches. |
| `search_symbol` | `/stable/search-symbol` | Search for security symbols across all asset types |
| `sector_pe_snapshot` | `/stable/sector-pe-snapshot` | Get sector PE snapshot data |
| `sector_performance` | `/stable/sector-performance-snapshot` | Get sector performance data |
| `all_shares_float` | `/stable/shares-float-all` | Get share float data for all companies at once. Provides a comprehensive view of market-wide float data, useful for screening and comparing companies based on their float characteristics. |
| `stock_list` | `/stable/stock-list` | Get a comprehensive list of all available stocks with their basic information including symbol, name, price, and exchange details. Returns the complete universe of tradable stocks. |
| `tradable_search` | `/stable/tradable-list` | Get list of tradable securities |

## Fundamental

**14 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `balance_sheet` | `/stable/balance-sheet-statement` | Obtain detailed balance sheet statements showing assets, liabilities and shareholders' equity for a company at specific points in time |
| `cash_flow` | `/stable/cash-flow-statement` | Access cash flow statements showing operating, investing, and financing activities along with key cash flow metrics and changes in cash position |
| `custom_discounted_cash_flow` | `/stable/custom-discounted-cash-flow` | Perform advanced DCF analysis with detailed cash flow projections, growth rates, WACC calculations, and terminal value assumptions |
| `custom_levered_dcf` | `/stable/custom-levered-discounted-cash-flow` | Calculate levered DCF valuation using free cash flow to equity (FCFE) with detailed projections and cost of equity calculations |
| `discounted_cash_flow` | `/stable/discounted-cash-flow` | Calculate discounted cash flow valuation to determine the intrinsic value of a company based on projected future cash flows |
| `financial_reports_dates` | `/stable/financial-reports-dates` | Get list of financial report dates |
| `full_financial_statement` | `/stable/financial-statement-full-as-reported` | Get full financial statements as reported |
| `historical_rating` | `/stable/historical-rating` | Retrieve historical company ratings and scoring metrics over time based on fundamental analysis |
| `income_statement` | `/stable/income-statement` | Retrieve detailed income statements showing revenue, costs, expenses and profitability metrics for a company |
| `key_metrics` | `/stable/key-metrics` | Access essential financial metrics and KPIs including profitability, efficiency, and valuation measures for company analysis |
| `latest_financial_statements` | `/stable/latest-financial-statements` | Get the latest financial statement publication metadata across symbols, including date and reporting period. |
| `levered_dcf` | `/stable/levered-discounted-cash-flow` | Perform levered discounted cash flow valuation including detailed assumptions and growth projections |
| `owner_earnings` | `/stable/owner-earnings` | Calculate owner earnings metrics using Warren Buffett's methodology for evaluating true business profitability |
| `financial_ratios` | `/stable/ratios` | Retrieve comprehensive financial ratios including profitability, liquidity, solvency, and efficiency metrics for analysis |

## Technical

**9 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `adx` | `/stable/technical-indicators/adx` | Calculate Average Directional Index (ADX) for a given symbol. ADX measures the strength of a trend. |
| `dema` | `/stable/technical-indicators/dema` | Calculate Double Exponential Moving Average (DEMA) for a given symbol. DEMA is more responsive to price changes than regular EMA. |
| `ema` | `/stable/technical-indicators/ema` | Calculate Exponential Moving Average (EMA) for a given symbol. EMA gives more weight to recent prices. |
| `rsi` | `/stable/technical-indicators/rsi` | Calculate Relative Strength Index (RSI) for a given symbol. RSI measures momentum and identifies overbought/oversold conditions. |
| `sma` | `/stable/technical-indicators/sma` | Calculate Simple Moving Average (SMA) for a given symbol. SMA is the average price over a specified number of periods. |
| `standard_deviation` | `/stable/technical-indicators/standarddeviation` | Calculate Standard Deviation for a given symbol. Measures the volatility of price movements. |
| `tema` | `/stable/technical-indicators/tema` | Calculate Triple Exponential Moving Average (TEMA) for a given symbol. TEMA further reduces lag compared to DEMA. |
| `williams` | `/stable/technical-indicators/williams` | Calculate Williams %R indicator for a given symbol. Williams %R identifies overbought and oversold levels. |
| `wma` | `/stable/technical-indicators/wma` | Calculate Weighted Moving Average (WMA) for a given symbol. WMA assigns linearly decreasing weights to past prices. |

## Market Intelligence

**47 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `crowdfunding_by_cik` | `/stable/crowdfunding-offerings` | Get crowdfunding offerings by CIK |
| `crowdfunding_rss` | `/stable/crowdfunding-offerings-latest` | Get latest crowdfunding offerings |
| `crowdfunding_search` | `/stable/crowdfunding-offerings-search` | Search crowdfunding offerings |
| `dividends_calendar` | `/stable/dividends-calendar` | Get dividends calendar |
| `earnings_confirmed` | `/stable/earning-calendar-confirmed` | Get confirmed earnings dates |
| `earnings_calendar` | `/stable/earnings-calendar` | Get earnings calendar |
| `earnings_surprises` | `/stable/earnings-surprises` | Get earnings surprises |
| `esg_benchmark` | `/stable/esg-benchmark` | Get ESG benchmark data |
| `esg_data` | `/stable/esg-disclosures` | Get ESG data for a company |
| `esg_ratings` | `/stable/esg-ratings` | Get ESG ratings for a company |
| `fmp_articles` | `/stable/fmp-articles` | Get a list of the latest FMP articles |
| `equity_offering_by_cik` | `/stable/fundraising` | Get equity offerings by CIK |
| `equity_offering_rss` | `/stable/fundraising-latest` | Get latest equity offerings |
| `equity_offering_search` | `/stable/fundraising-search` | Search equity offerings |
| `grades` | `/stable/grades` | Get stock grades from analysts |
| `grades_consensus` | `/stable/grades-consensus` | Get stock grades consensus summary |
| `grades_historical` | `/stable/grades-historical` | Get historical stock grades |
| `grades_latest_news` | `/stable/grades-latest-news` | Get latest stock grade news |
| `grades_news` | `/stable/grades-news` | Get stock grade news |
| `historical_earnings` | `/stable/historical/earning-calendar` | Get historical earnings |
| `historical_social_sentiment` | `/stable/historical/social-sentiment` | Get historical social sentiment data |
| `house_latest` | `/stable/house-latest` | Get latest House financial disclosures |
| `house_disclosure` | `/stable/house-trades` | Get House trading data by symbol |
| `house_trades_by_name` | `/stable/house-trades-by-name` | Get House trading data by name |
| `ipo_calendar` | `/stable/ipos-calendar` | Get IPO calendar |
| `crypto_symbol_news` | `/stable/news/crypto` | Search crypto news articles by trading pair |
| `crypto_news` | `/stable/news/crypto-latest` | Get a list of the latest crypto news articles |
| `forex_symbol_news` | `/stable/news/forex` | Search forex news articles by currency pair |
| `forex_news` | `/stable/news/forex-latest` | Get a list of the latest forex news articles |
| `general_news` | `/stable/news/general-latest` | Get a list of the latest general news articles |
| `press_releases_by_symbol` | `/stable/news/press-releases` | Get a list of the latest press releases for a specific company |
| `press_releases` | `/stable/news/press-releases-latest` | Get a list of the latest press releases |
| `stock-news-symbol` | `/stable/news/stock` | Get a list of the latest news for a specific stock |
| `stock-news` | `/stable/news/stock-latest` | Get a list of the latest stock news articles |
| `price_target_latest_news` | `/stable/price-target-latest-news` | Get latest price target news |
| `price_target_news` | `/stable/price-target-news` | Get price target news |
| `ratings_historical` | `/stable/ratings-historical` | Get historical analyst ratings |
| `ratings_snapshot` | `/stable/ratings-snapshot` | Get current analyst ratings snapshot |
| `senate_latest` | `/stable/senate-latest` | Get latest Senate financial disclosures |
| `senate_trading` | `/stable/senate-trades` | Get Senate trading data by symbol |
| `senate_trades_by_name` | `/stable/senate-trades-by-name` | Get Senate trading data by name |
| `senate_trading_rss` | `/stable/senate-trading-rss-feed` | Get Senate trading RSS feed |
| `social_sentiment_changes` | `/stable/social-sentiments/change` | Get changes in social sentiment data |
| `trending_social_sentiment` | `/stable/social-sentiments/trending` | Get trending social sentiment data |
| `stock_splits_calendar` | `/stable/splits-calendar` | Get stock splits calendar |
| `stock_news_sentiments` | `/stable/stock-news-sentiments-rss-feed` | Get a list of the latest stock news articles with sentiment analysis |

## Institutional

**25 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `asset_allocation` | `/stable/13f-asset-allocation` | Get 13F asset allocation data |
| `beneficial_ownership` | `/stable/acquisition-of-beneficial-ownership` | Get beneficial ownership data |
| `cik_mapper` | `/stable/cik-list` | Get CIK to name mappings |
| `cik_mapper_by_name` | `/stable/cik-list` | Search CIK mappings by name |
| `fail_to_deliver` | `/stable/fail_to_deliver` | Get fail to deliver data |
| `transaction_types` | `/stable/insider-trading-transaction-type` | Get insider transaction types |
| `insider_trading_latest` | `/stable/insider-trading/latest` | Get latest insider trading activity |
| `insider_trading_by_name` | `/stable/insider-trading/reporting-name` | Search insider trades by reporting name |
| `insider_roster` | `/stable/insider-trading/search` | Get insider roster |
| `insider_trades` | `/stable/insider-trading/search` | Get insider trades |
| `insider_trading_search` | `/stable/insider-trading/search` | Search insider trades with filters |
| `insider_statistics` | `/stable/insider-trading/statistics` | Get insider trading statistics |
| `insider_trading_statistics_enhanced` | `/stable/insider-trading/statistics` | Get enhanced insider trading statistics |
| `form_13f_dates` | `/stable/institutional-ownership/dates` | Get Form 13F filing dates |
| `institutional_ownership_dates` | `/stable/institutional-ownership/dates` | Get Form 13F filing dates |
| `form_13f` | `/stable/institutional-ownership/extract` | Get Form 13F filing data |
| `institutional_ownership_extract` | `/stable/institutional-ownership/extract` | Get filings extract data |
| `institutional_ownership_analytics` | `/stable/institutional-ownership/extract-analytics/holder` | Get filings extract with analytics by holder |
| `holder_industry_breakdown` | `/stable/institutional-ownership/holder-industry-breakdown` | Get holders industry breakdown |
| `holder_performance_summary` | `/stable/institutional-ownership/holder-performance-summary` | Get holder performance summary |
| `industry_performance_summary` | `/stable/institutional-ownership/industry-summary` | Get industry performance summary |
| `institutional_holders` | `/stable/institutional-ownership/latest` | Get list of institutional holders |
| `institutional_ownership_latest` | `/stable/institutional-ownership/latest` | Get latest institutional ownership filings |
| `institutional_holdings` | `/stable/institutional-ownership/symbol-positions-summary` | Get institutional holdings by symbol |
| `symbol_positions_summary` | `/stable/institutional-ownership/symbol-positions-summary` | Get positions summary by symbol |

## Investment

**14 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `etf_exposure` | `/stable/etf/asset-exposure` | Get ETF stock exposure |
| `etf_country_weightings` | `/stable/etf/country-weightings` | Get ETF country weightings |
| `etf_holder` | `/stable/etf/holder` | Get ETF holder information |
| `mutual_fund_holder` | `/stable/etf/holder` | Get mutual fund holder information |
| `etf_holdings` | `/stable/etf/holdings` | Get ETF holdings |
| `etf_info` | `/stable/etf/info` | Get ETF information |
| `etf_holding_dates` | `/stable/etf/portfolio-dates` | Get ETF holding dates |
| `etf_sector_weightings` | `/stable/etf/sector-weightings` | Get ETF sector weightings |
| `funds_disclosure` | `/stable/funds/disclosure` | Get mutual fund/ETF disclosure holdings |
| `mutual_fund_dates` | `/stable/funds/disclosure-dates` | Get mutual fund/ETF disclosure dates |
| `funds_disclosure_holders_latest` | `/stable/funds/disclosure-holders-latest` | Get latest mutual fund/ETF disclosure holders |
| `funds_disclosure_holders_search` | `/stable/funds/disclosure-holders-search` | Search mutual fund/ETF disclosure holders by name |
| `mutual_fund_holdings` | `/stable/mutual-fund-holdings` | Get mutual fund holdings |
| `mutual_fund_by_name` | `/stable/mutual-fund-holdings/name` | Get mutual funds by name |

## Alternative Markets

**15 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `commodities_list` | `/stable/commodities-list` | Get a comprehensive list of all available commodity symbols and their basic trading information |
| `crypto_list` | `/stable/cryptocurrency-list` | Get a comprehensive list of all available cryptocurrencies and their basic information including symbol, name, and exchange details |
| `forex_list` | `/stable/forex-list` | Get a complete list of available forex currency pairs with their symbols and basic trading information |
| `forex_intraday` | `/stable/historical-chart/{interval}` | Retrieve intraday exchange rate data for forex pairs at specified intervals, ideal for day trading and short-term analysis |
| `commodity_intraday` | `/stable/historical-chart/{interval}/{symbol}` | Access detailed intraday price data for commodities at specified time intervals. Provides high-frequency price data including open, high, low, close prices and volume |
| `crypto_intraday` | `/stable/historical-chart/{interval}/{symbol}` | Get detailed intraday price data for a cryptocurrency at specified time intervals, perfect for short-term trading analysis and high-frequency data needs |
| `commodity_historical` | `/stable/historical-price-eod` | Retrieve comprehensive historical price data for a commodity over a specified date range, including daily OHLCV (Open, High, Low, Close, Volume) data, adjusted prices, and price change metrics |
| `crypto_historical` | `/stable/historical-price-eod` | Retrieve historical price data for a cryptocurrency over a specified date range, including daily OHLCV (Open, High, Low, Close, Volume) data and adjusted prices |
| `forex_historical` | `/stable/historical-price-eod` | Access historical exchange rate data for forex pairs over a specified date range, including daily rates and price changes |
| `commodity_quote` | `/stable/quote` | Get detailed real-time price quote for a specific commodity including current price, daily change, trading volume and other key market metrics |
| `crypto_quote` | `/stable/quote` | Get detailed real-time price quote and trading information for a specific cryptocurrency including price, volume, change percentage, and market metrics |
| `forex_quote` | `/stable/quote` | Get detailed real-time quote for a specific forex currency pair including current rate, daily change, and trading metrics |
| `commodities_quotes` | `/stable/quotes/commodity` | Retrieve real-time quotes for all available commodities including current prices, daily changes, and trading volumes |
| `crypto_quotes` | `/stable/quotes/crypto` | Retrieve real-time price quotes for all available cryptocurrencies including current price, daily change, volume and other key metrics |
| `forex_quotes` | `/stable/quotes/forex` | Retrieve real-time quotes for all available forex currency pairs including current exchange rates and daily changes |

## Economics

**7 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `commitment_of_traders_analysis` | `/stable/commitment-of-traders-analysis` | Get Commitment of Traders (COT) analysis data |
| `commitment_of_traders_list` | `/stable/commitment-of-traders-list` | Get list of available Commitment of Traders (COT) symbols |
| `commitment_of_traders_report` | `/stable/commitment-of-traders-report` | Get Commitment of Traders (COT) report data |
| `economic_calendar` | `/stable/economic-calendar` | Access a calendar of economic events, releases, and announcements with their expected and actual values |
| `economic_indicators` | `/stable/economic-indicators` | Retrieve economic indicator data including GDP, inflation rates, employment statistics, and other key metrics |
| `market_risk_premium` | `/stable/market-risk-premium` | Retrieve market risk premium data by country, including equity risk premiums and country-specific risk factors |
| `treasury_rates` | `/stable/treasury-rates` | Get U.S. Treasury rates across different maturities including daily rates and yield curve data |

## Batch

**30 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `balance_sheet_statement_bulk` | `/stable/balance-sheet-statement-bulk` | Get balance sheet statements in bulk |
| `balance_sheet_statement_growth_bulk` | `/stable/balance-sheet-statement-growth-bulk` | Get balance sheet statement growth in bulk |
| `batch_aftermarket_quote` | `/stable/batch-aftermarket-quote` | Get aftermarket quote data for multiple symbols |
| `batch_aftermarket_trade` | `/stable/batch-aftermarket-trade` | Get aftermarket (post-market) trade data for multiple symbols |
| `batch_commodity_quotes` | `/stable/batch-commodity-quotes` | Get batch quotes for all commodities |
| `batch_crypto_quotes` | `/stable/batch-crypto-quotes` | Get batch quotes for all cryptocurrencies |
| `batch_etf_quotes` | `/stable/batch-etf-quotes` | Get batch quotes for all ETFs |
| `batch_exchange_quote` | `/stable/batch-exchange-quote` | Get quotes for all stocks on a specific exchange |
| `batch_forex_quotes` | `/stable/batch-forex-quotes` | Get batch quotes for all forex pairs |
| `batch_index_quotes` | `/stable/batch-index-quotes` | Get batch quotes for all market indexes |
| `batch_mutualfund_quotes` | `/stable/batch-mutualfund-quotes` | Get batch quotes for all mutual funds |
| `batch_quote` | `/stable/batch-quote` | Get real-time quotes for multiple symbols in a single request |
| `batch_quote_short` | `/stable/batch-quote-short` | Get quick price snapshots for multiple symbols |
| `cash_flow_statement_bulk` | `/stable/cash-flow-statement-bulk` | Get cash flow statements in bulk |
| `cash_flow_statement_growth_bulk` | `/stable/cash-flow-statement-growth-bulk` | Get cash flow statement growth in bulk |
| `dcf_bulk` | `/stable/dcf-bulk` | Get discounted cash flow valuations in bulk |
| `earnings_surprises_bulk` | `/stable/earnings-surprises-bulk` | Get earnings surprises in bulk for a given year |
| `eod_bulk` | `/stable/eod-bulk` | Get end-of-day prices in bulk |
| `etf_holder_bulk` | `/stable/etf-holder-bulk` | Get ETF holdings in bulk |
| `income_statement_bulk` | `/stable/income-statement-bulk` | Get income statements in bulk |
| `income_statement_growth_bulk` | `/stable/income-statement-growth-bulk` | Get income statement growth in bulk |
| `key_metrics_ttm_bulk` | `/stable/key-metrics-ttm-bulk` | Get trailing twelve month key metrics in bulk |
| `batch_market_cap` | `/stable/market-capitalization-batch` | Get market capitalization for multiple symbols |
| `peers_bulk` | `/stable/peers-bulk` | Get peer lists for all symbols in bulk |
| `price_target_summary_bulk` | `/stable/price-target-summary-bulk` | Get bulk price target summary data |
| `profile_bulk` | `/stable/profile-bulk` | Get company profile data in bulk |
| `rating_bulk` | `/stable/rating-bulk` | Get stock ratings in bulk |
| `ratios_ttm_bulk` | `/stable/ratios-ttm-bulk` | Get trailing twelve month financial ratios in bulk |
| `scores_bulk` | `/stable/scores-bulk` | Get financial scores in bulk |
| `upgrades_downgrades_consensus_bulk` | `/stable/upgrades-downgrades-consensus-bulk` | Get upgrades/downgrades consensus data in bulk |

## Transcripts

**4 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `earnings_transcript` | `/stable/earning-call-transcript` | Get earnings call transcript for a specific company and quarter |
| `transcript_dates` | `/stable/earning-call-transcript-dates` | Get available transcript dates for a specific company |
| `latest_transcripts` | `/stable/earning-call-transcript-latest` | Get the most recent earnings call transcripts across all companies |
| `transcript_symbols` | `/stable/earnings-transcript-list` | Get list of all symbols with available earnings transcripts |

## SEC

**12 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `all_industry_classification` | `/stable/all-industry-classification` | Get all industry classification data |
| `industry_classification_search` | `/stable/industry-classification-search` | Search industry classification data |
| `sec_filings_8k` | `/stable/sec-filings-8k` | Get the latest SEC 8-K filings |
| `sec_company_search_cik` | `/stable/sec-filings-company-search/cik` | Search SEC companies by CIK number |
| `sec_company_search_name` | `/stable/sec-filings-company-search/name` | Search SEC companies by name |
| `sec_company_search_symbol` | `/stable/sec-filings-company-search/symbol` | Search SEC companies by stock symbol |
| `sec_filings_financials` | `/stable/sec-filings-financials` | Get the latest SEC financial filings (10-K, 10-Q) |
| `sec_filings_search_cik` | `/stable/sec-filings-search/cik` | Search SEC filings by CIK number |
| `sec_filings_search_form_type` | `/stable/sec-filings-search/form-type` | Search SEC filings by form type |
| `sec_filings_search_symbol` | `/stable/sec-filings-search/symbol` | Search SEC filings by stock symbol |
| `sec_profile` | `/stable/sec-profile` | Get SEC profile for a company |
| `sic_list` | `/stable/standard-industrial-classification-list` | Get list of all Standard Industrial Classification (SIC) codes |

## Index

**6 endpoints**

| Endpoint | Path | Description |
|----------|------|-------------|
| `dowjones_constituents` | `/stable/dowjones-constituent` | Get current Dow Jones Industrial Average constituents |
| `historical_dowjones` | `/stable/historical-dowjones-constituent` | Get historical Dow Jones constituent changes |
| `historical_nasdaq` | `/stable/historical-nasdaq-constituent` | Get historical NASDAQ constituent changes |
| `historical_sp500` | `/stable/historical-sp500-constituent` | Get historical S&P 500 constituent changes |
| `nasdaq_constituents` | `/stable/nasdaq-constituent` | Get current NASDAQ index constituents |
| `sp500_constituents` | `/stable/sp500-constituent` | Get current S&P 500 index constituents |
