# FMP Data MCP Tools Reference

This document lists all 140 available MCP tools for the FMP Data library.
Tools are organized by client module and include descriptions.

## Table of Contents

- [Alternative (15 tools)](#alternative)
- [Company (28 tools)](#company)
- [Economics (4 tools)](#economics)
- [Fundamental (13 tools)](#fundamental)
- [Institutional (13 tools)](#institutional)
- [Intelligence (33 tools)](#intelligence)
- [Investment (11 tools)](#investment)
- [Market (14 tools)](#market)
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

**28 tools** for company data access.

| Tool Key | Description |
|----------|-------------|
| `analyst_estimates` | Retrieve detailed analyst estimates including revenue, earnings, EBITDA, and other financial metrics forecasts with h... |
| `analyst_recommendations` | Retrieve analyst buy/sell/hold recommendations and consensus ratings for stocks including detailed rating breakdowns |
| `company_logo_url` | Get the URL of the company's official logo image for use in applications, websites, or documentation |
| `company_notes` | Retrieve company financial notes and disclosures from SEC filings, providing additional context and explanations abou... |
| `core_information` | Get essential company information including CIK number, exchange listing, SIC code, state of incorporation, and fisca... |
| `employee_count` | Get historical employee count data showing how company workforce has changed over time |
| `executive_compensation` | Get detailed executive compensation information including salary, bonuses, stock awards, and total compensation packa... |
| `executives` | Get detailed information about company's key executives including their names, titles, compensation, and tenure. |
| `geographic_revenue_segmentation` | Get revenue breakdown by geographic regions, showing how company revenue is distributed across different countries an... |
| `historical_market_cap` | Retrieve historical market capitalization data to track changes in company value over time |
| `historical_price` | Retrieve historical daily price data including open, high, low, close, and adjusted prices with volume information . |
| `historical_prices` | Retrieve historical price data including OHLCV (Open, High, Low, Close, Volume) information for detailed technical an... |
| `historical_share_float` | Get historical share float data showing how the number of tradable shares has changed over time |
| `intraday_price` | Get intraday price data at various intervals (1min to 4hour) for detailed analysis of price movements within the trad... |
| `intraday_prices` | Get intraday price data with minute-by-minute or hourly intervals |
| `key_executives` | Get detailed information about company's key executives including their names, titles, tenure, and basic compensation... |
| `market_cap` | Get current market capitalization data for a company, including total market value and related metrics |
| `price_target` | Retrieve analyst price targets for a specific stock, including target prices, analyst details, and publication dates |
| `price_target_consensus` | Get detailed consensus information about analyst price targets, including target distribution, recent changes, and an... |
| `price_target_summary` | Get a summary of analyst price targets for a stock, including average, highest, and lowest targets along with number ... |
| `product_revenue_segmentation` | Get detailed revenue breakdown by product lines or services, showing how company revenue is distributed across differ... |
| `profile` | Get detailed company profile information including financial metrics, company description, sector, industry, and cont... |
| `quote` | Get real-time stock quote data including current price, volume, day range, and other key market metrics |
| `share_float` | Get current share float data showing the number and percentage of shares available for public trading |
| `simple_quote` | Get real-time basic stock quote including price, volume, and change information |
| `symbol_changes` | Get historical record of company ticker symbol changes, tracking when and why companies changed their trading symbols |
| `upgrades_downgrades` | Access stock rating changes including upgrades, downgrades, and rating adjustments with analyst and firm information |
| `upgrades_downgrades_consensus` | Get aggregated rating consensus data including buy/sell/hold counts and overall recommendation trends |

## Economics

**4 tools** for economics data access.

| Tool Key | Description |
|----------|-------------|
| `economic_calendar` | Access a comprehensive calendar of economic events, data releases, and policy announcements. |
| `economic_indicators` | Access comprehensive economic indicator data including GDP, inflation, employment statistics, trade balances, and more. |
| `market_risk_premium` | Retrieve comprehensive market risk premium data by country, including equity risk premiums, country-specific risk fac... |
| `treasury_rates` | Retrieve U.S. Treasury rates across multiple maturities including bills, notes, and bonds.  |

## Fundamental

**13 tools** for fundamental data access.

| Tool Key | Description |
|----------|-------------|
| `balance_sheet` | Access detailed balance sheet statements showing a company's assets, liabilities, and shareholders' equity. |
| `cash_flow` | Retrieve detailed cash flow statements showing operating, investing, and financing activities. |
| `custom_discounted_cash_flow` | Perform advanced DCF analysis with detailed cash flow projections, growth rates, WACC calculations, and terminal valu... |
| `custom_levered_dcf` | Calculate levered DCF valuation using free cash flow to equity (FCFE) with detailed projections and cost of equity ca... |
| `discounted_cash_flow` | Calculate discounted cash flow valuation to determine the intrinsic value of a company based on projected future cash... |
| `financial_ratios` | Access comprehensive financial ratios for analyzing company performance, efficiency, and financial health. |
| `financial_reports_dates` | Retrieve available financial report dates and access links for a company, including quarterly and annual filings. |
| `full_financial_statement` | Access complete financial statements as reported to regulatory authorities, including detailed line items, notes, and... |
| `historical_rating` | Retrieve historical company ratings and scoring metrics over time based on fundamental analysis. |
| `income_statement` | Retrieve detailed income statements showing revenue, costs, expenses and profitability metrics for a company over mul... |
| `key_metrics` | Access essential financial metrics and KPIs including profitability, efficiency, and valuation measures. |
| `levered_dcf` | Perform levered discounted cash flow valuation with detailed assumptions about growth, cost of capital, and future ca... |
| `owner_earnings` | Calculate owner earnings using Warren Buffett's methodology to evaluate true business profitability and cash generati... |

## Institutional

**13 tools** for institutional data access.

| Tool Key | Description |
|----------|-------------|
| `asset_allocation` | Analyze asset allocation data from 13F filings |
| `beneficial_ownership` | Retrieve beneficial ownership information including voting rights and dispositive power for major shareholders of a c... |
| `cik_mapper` | Get a comprehensive mapping between CIK numbers and company/institution names. |
| `cik_mapper_by_name` | Search for CIK numbers by company or institution name. |
| `fail_to_deliver` | Get data on failed trade settlements (FTDs) for a security. |
| `form_13f` | Retrieve Form 13F filings data for institutional investment managers, including detailed holdings information, share ... |
| `form_13f_dates` | Get a list of available Form 13F filing dates for a specific institutional investment manager, helping track their re... |
| `insider_roster` | Get a list of company insiders including executives, directors, and major shareholders, along with their positions an... |
| `insider_statistics` | Get aggregated statistics about insider trading activity. |
| `insider_trades` | Track insider trading activity for a specific security. |
| `institutional_holders` | Get detailed information about institutional holders of securities. |
| `institutional_holdings` | Analyze institutional ownership for a specific security. |
| `transaction_types` | Get a reference list of insider transaction types and their descriptions. |

## Intelligence

**33 tools** for intelligence data access.

| Tool Key | Description |
|----------|-------------|
| `crowdfunding_by_cik` | Retrieve crowdfunding offerings for a specific company using CIK with complete offering details |
| `crowdfunding_rss` | Access latest crowdfunding offerings and campaigns including funding details, company information, and offering terms |
| `crowdfunding_search` | Search crowdfunding offerings and campaigns by company name with detailed offering information |
| `crypto_news` | Access cryptocurrency news articles including market updates, trading information, and digital asset developments |
| `dividends_calendar` | Get upcoming and historical dividend events including ex-dividend dates, payment dates, and dividend amounts |
| `earnings_calendar` | Access comprehensive earnings calendar showing upcoming earnings releases, estimated and actual results, and historic... |
| `earnings_confirmed` | Access confirmed earnings dates and times for companies including timing details and publication information |
| `earnings_surprises` | Retrieve historical earnings surprises including actual vs estimated earnings, surprise percentages, and earnings dates |
| `equity_offering_by_cik` | Retrieve equity offerings for a specific company using CIK number including historical and current offerings |
| `equity_offering_rss` | Get real-time RSS feed of equity offerings including new issues, follow-on offerings, and capital raising events |
| `equity_offering_search` | Search for equity offerings including public and private placements, with detailed offering terms and company informa... |
| `esg_benchmark` | Retrieve industry ESG benchmarks and sector averages for environmental, social, and governance metrics |
| `esg_data` | Retrieve detailed ESG (Environmental, Social, Governance) metrics and scores for companies including component breakd... |
| `esg_ratings` | Access company ESG ratings and scores including environmental, social, and governance performance metrics and industr... |
| `financial_reports_dates` | Retrieve available financial report dates and filing deadlines |
| `fmp_articles` | Access Financial Modeling Prep articles including market analysis, company research, and financial insights |
| `forex_news` | Retrieve forex market news including currency pair updates, exchange rate movements, and international market develop... |
| `general_news` | Retrieve general financial news and market updates from various sources covering markets, economy, and business |
| `historical_earnings` | Access historical earnings reports including revenue, EPS, and dates for past quarters and fiscal years |
| `historical_social_sentiment` | Retrieve historical social media sentiment data including sentiment scores, engagement metrics, and trend analysis |
| `house_disclosure` | Access House of Representatives trading disclosures including transaction details, filing information, and trade spec... |
| `house_disclosure_rss` | Access real-time RSS feed of House Representative trading disclosures including new filings and updates |
| `institutional_holders` | Retrieve institutional ownership data including holder details, position sizes, and ownership changes |
| `ipo_calendar` | Retrieve upcoming and recent IPO events including pricing details, offering sizes, and listing dates |
| `press_releases` | Retrieve corporate press releases and official company announcements with detailed content and publication information |
| `press_releases_by_symbol` | Retrieve company-specific press releases and official announcements including corporate events and updates |
| `senate_trading` | Access Senate trading activity and disclosures including stock trades, transaction details, and filing information |
| `senate_trading_rss` | Get real-time RSS feed of Senate trading disclosures including new filings and transaction updates |
| `social_sentiment_changes` | Track changes in social media sentiment including sentiment shifts, momentum changes, and trend developments |
| `stock_news` | Access stock-specific news and updates including company events, market moves, and corporate developments |
| `stock_news_sentiments` | Get stock news with sentiment analysis including positive/negative sentiment scores and market impact assessment |
| `stock_splits_calendar` | Access upcoming and historical stock split events including split ratios, dates, and affected securities |
| `trending_social_sentiment` | Get current trending social media sentiment data including most discussed stocks and sentiment rankings |

## Investment

**11 tools** for investment data access.

| Tool Key | Description |
|----------|-------------|
| `etf_country_weightings` | Get detailed geographic allocation data for an ETF, showing the percentage of the portfolio invested in different cou... |
| `etf_exposure` | Retrieve detailed stock exposure data for an ETF, showing specific securities held and their weights in the portfolio |
| `etf_holder` | Get information about institutional holders of an ETF, including their holdings and position sizes |
| `etf_holding_dates` | Get a list of available portfolio dates for which ETF holdings data is available |
| `etf_holdings` | Retrieve detailed holdings information for an ETF including assets, weights, and market values as of a specific date |
| `etf_info` | Get comprehensive information about an ETF including expense ratio, assets under management, and fund characteristics |
| `etf_sector_weightings` | Retrieve detailed sector allocation data for an ETF, showing the percentage of the portfolio invested in different ma... |
| `mutual_fund_by_name` | Search for mutual funds by name to get their holdings and basic information |
| `mutual_fund_dates` | Retrieve available portfolio dates for mutual fund holdings data, helping track portfolio composition changes over time |
| `mutual_fund_holder` | Get information about institutional holders of a mutual fund, including their holdings and position sizes |
| `mutual_fund_holdings` | Get detailed holdings information for a mutual fund, including securities held, weights, and market values as of a sp... |

## Market

**14 tools** for market data access.

| Tool Key | Description |
|----------|-------------|
| `all_shares_float` | Get comprehensive share float data for all companies, showing the number and percentage of shares available for publi... |
| `available_indexes` | Get a list of all available market indexes including major stock market indices, sector indexes, and other benchmark ... |
| `etf_list` | Get a complete list of all available ETFs (Exchange Traded Funds) with their basic information including symbol, name... |
| `gainers` | Get list of top gaining stocks by percentage change, showing the best performing stocks in the current trading session |
| `losers` | Get list of top losing stocks by percentage change, showing the worst performing stocks in the current trading session |
| `market_hours` | Check current market status and trading hours for a specific exchange |
| `most_active` | Get list of most actively traded stocks by volume, showing stocks with the highest trading activity in the current se... |
| `pre_post_market` | Retrieve pre-market and post-market trading data including prices, volume, and trading session information outside re... |
| `search` | Search for companies by name, ticker, or other identifiers. |
| `search_by_cik` | Search for companies by their SEC Central Index Key (CIK) number |
| `search_by_cusip` | Search for companies by their CUSIP identifier |
| `search_by_isin` | Search for companies by their International Securities Identification Number (ISIN) |
| `sector_performance` | Get performance data for major market sectors, showing relative strength and weakness across different areas of the m... |
| `stock_list` | Get a complete list of all available stocks in the market including their basic information such as symbol, name, and... |

## Technical

**9 tools** for technical data access.

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
