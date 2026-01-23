# FMP Data MCP Tools Reference

This document lists the MCP tools available in this release.
Tools are organized by client module and include descriptions.

For full FMP endpoint coverage, use the Python client. The MCP tool catalog includes endpoints with MCP tool semantics.

## Table of Contents

- [Alternative (15 tools)](#alternative)
- [Company (31 tools)](#company)
- [Economics (7 tools)](#economics)
- [Fundamental (14 tools)](#fundamental)
- [Institutional (13 tools)](#institutional)
- [Intelligence (39 tools)](#intelligence)
- [Investment (14 tools)](#investment)
- [Market (23 tools)](#market)
- [Technical (9 tools)](#technical)

## Alternative

**15 tools** for alternative data access.

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

## Company

**31 tools** for company information and quotes.

| Tool Key | Description |
|----------|-------------|
| `aftermarket_quote` | Get after-hours bid/ask quote data for a stock with sizes, prices, and timestamp |
| `aftermarket_trade` | Get after-hours trade data for a stock, including price, size, and trade timestamp |
| `analyst_estimates` | Retrieve detailed analyst estimates including revenue, earnings, EBITDA, and other financial metrics forecasts with high/low/average ranges |
| `analyst_recommendations` | Retrieve analyst buy/sell/hold recommendations and consensus ratings for stocks including detailed rating breakdowns |
| `company_logo_url` | Get the URL of the company's official logo image for use in applications, websites, or documentation |
| `company_notes` | Retrieve company financial notes and disclosures from SEC filings, providing additional context and explanations about financial statements |
| `core_information` | Get essential company information including CIK number, exchange listing, SIC code, state of incorporation, and fiscal year details |
| `employee_count` | Get historical employee count data showing how company workforce has changed over time |
| `executive_compensation` | Get detailed executive compensation information including salary, bonuses, stock awards, and total compensation packages for company leaders |
| `executives` | Get detailed information about company's key executives including their names, titles, compensation, and tenure. |
| `geographic_revenue_segmentation` | Get revenue breakdown by geographic regions, showing how company revenue is distributed across different countries and regions |
| `historical_market_cap` | Retrieve historical market capitalization data to track changes in company value over time |
| `historical_price` | Retrieve historical daily price data including open, high, low, close, and adjusted prices with volume information . |
| `historical_prices` | Retrieve historical price data including OHLCV (Open, High, Low, Close, Volume) information for detailed technical and performance analysis. |
| `historical_share_float` | Get historical share float data showing how the number of tradable shares has changed over time |
| `intraday_price` | Get intraday price data at various intervals (1min to 4hour) for detailed analysis of price movements within the trading day |
| `intraday_prices` | Get intraday price data with minute-by-minute or hourly intervals |
| `key_executives` | Get detailed information about company's key executives including their names, titles, tenure, and basic compensation data |
| `market_cap` | Get current market capitalization data for a company, including total market value and related metrics |
| `price_target` | Retrieve analyst price targets for a specific stock, including target prices, analyst details, and publication dates |
| `price_target_consensus` | Get detailed consensus information about analyst price targets, including target distribution, recent changes, and analyst recommendations. |
| `price_target_summary` | Get a summary of analyst price targets for a stock, including average, highest, and lowest targets along with number of analysts. |
| `product_revenue_segmentation` | Get detailed revenue breakdown by product lines or services, showing how company revenue is distributed across different offerings |
| `profile` | Get detailed company profile information including financial metrics, company description, sector, industry, and contact information |
| `quote` | Get real-time stock quote data including current price, volume, day range, and other key market metrics |
| `share_float` | Get current share float data showing the number and percentage of shares available for public trading |
| `simple_quote` | Get real-time basic stock quote including price, volume, and change information |
| `stock_price_change` | Get percentage price changes across multiple time horizons for a stock |
| `symbol_changes` | Get historical record of company ticker symbol changes, tracking when and why companies changed their trading symbols |
| `upgrades_downgrades` | Access stock rating changes including upgrades, downgrades, and rating adjustments with analyst and firm information |
| `upgrades_downgrades_consensus` | Get aggregated rating consensus data including buy/sell/hold counts and overall recommendation trends |

## Economics

**7 tools** for economic indicators.

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

**14 tools** for fundamental analysis and valuation.

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

## Institutional

**13 tools** for institutional and insider data.

| Tool Key | Description |
|----------|-------------|
| `asset_allocation` | Analyze asset allocation data from 13F filings |
| `beneficial_ownership` | Retrieve beneficial ownership information including voting rights and dispositive power for major shareholders of a company. |
| `cik_mapper` | Get a comprehensive mapping between CIK numbers and company/institution names. |
| `cik_mapper_by_name` | Search for CIK numbers by company or institution name. |
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

**39 tools** for news, sentiment, and market events.

| Tool Key | Description |
|----------|-------------|
| `crowdfunding_by_cik` | Retrieve crowdfunding offerings for a specific company using CIK with complete offering details |
| `crowdfunding_rss` | Access latest crowdfunding offerings and campaigns including funding details, company information, and offering terms |
| `crowdfunding_search` | Search crowdfunding offerings and campaigns by company name with detailed offering information |
| `crypto_news` | Access cryptocurrency news articles including market updates, trading information, and digital asset developments |
| `crypto_symbol_news` | Search cryptocurrency news for a specific trading pair to track asset-specific developments |
| `dividends_calendar` | Get upcoming and historical dividend events including ex-dividend dates, payment dates, and dividend amounts |
| `earnings_calendar` | Access comprehensive earnings calendar showing upcoming earnings releases, estimated and actual results, and historical earnings data |
| `earnings_confirmed` | Access confirmed earnings dates and times for companies including timing details and publication information |
| `earnings_surprises` | Retrieve historical earnings surprises including actual vs estimated earnings, surprise percentages, and earnings dates |
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
| `historical_earnings` | Access historical earnings reports including revenue, EPS, and dates for past quarters and fiscal years |
| `historical_social_sentiment` | Retrieve historical social media sentiment data including sentiment scores, engagement metrics, and trend analysis |
| `house_disclosure` | Access House of Representatives trading disclosures including transaction details, filing information, and trade specifics |
| `house_latest` | Get the latest House financial disclosures with transaction details |
| `house_trades_by_name` | Get House trading data filtered by representative name |
| `ipo_calendar` | Retrieve upcoming and recent IPO events including pricing details, offering sizes, and listing dates |
| `press_releases` | Retrieve corporate press releases and official company announcements with detailed content and publication information |
| `press_releases_by_symbol` | Retrieve company-specific press releases and official announcements including corporate events and updates |
| `senate_latest` | Get the latest Senate financial disclosures with transaction details |
| `senate_trades_by_name` | Get Senate trading data filtered by senator name |
| `senate_trading` | Access Senate trading activity and disclosures including stock trades, transaction details, and filing information |
| `senate_trading_rss` | Get real-time RSS feed of Senate trading disclosures including new filings and transaction updates |
| `social_sentiment_changes` | Track changes in social media sentiment including sentiment shifts, momentum changes, and trend developments |
| `stock_news` | Access stock-specific news and updates including company events, market moves, and corporate developments |
| `stock_news_sentiments` | Get stock news with sentiment analysis including positive/negative sentiment scores and market impact assessment |
| `stock_splits_calendar` | Access upcoming and historical stock split events including split ratios, dates, and affected securities |
| `trending_social_sentiment` | Get current trending social media sentiment data including most discussed stocks and sentiment rankings |

## Investment

**14 tools** for ETFs and mutual funds.

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

**23 tools** for market data and search.

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

## Technical

**9 tools** for technical indicators.

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
