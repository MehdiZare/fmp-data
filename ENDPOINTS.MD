# FMP API Endpoints

## 1. Company Information & Search
### Basic Company Data
- Company Profile `/v3/profile/{symbol}`
- Company Core Information `/v4/company-core-information`
- Company Logo `/image-stock/{symbol}.png`
- Company Notes `/v4/company-notes`
- Employee Count `/v4/employee_count`
- Historical Employee Count `/v4/historical/employee_count`
- Company Executives `/v3/key-executives`

### Search & Lists
- General Search `/v3/search`
- Symbol List `/v3/stock/list`
- Exchange Traded Fund List `/v3/etf/list`
- Available Indexes `/v3/symbol/available-indexes`
- Exchange Symbols `/v3/symbol/{exchange}`
- Statement Symbols List `/v3/financial-statement-symbol-lists`
- Tradable Search `/v3/available-traded/list`
- Symbol Changes `/v4/symbol_change`
- Delisted Companies `/v3/delisted-companies`

### Identifiers & Mapping
- CIK Search `/v3/cik-search`
- CUSIP Search `/v3/cusip`
- ISIN Search `/v4/search/isin`
- CIK List `/v3/cik_list`

## 2. Market Data
### Price Data
- Full Quote `/v3/quote/{symbol}`
- Quote Order `/v3/quote-order/{symbol}`
- Simple Quote `/v3/quote-short/{symbol}`
- OTC Quote `/v3/otc/real-time-price/{symbol}`
- Exchange Prices `/v3/quotes/{exchange}`
- Stock Price Change `/v3/stock-price-change/{symbol}`
- Historical Price (Daily) `/v3/historical-price-full/{symbol}`
- Intraday Price `/v3/historical-chart/{interval}/{symbol}`

### Pre/Post Market
- Aftermarket Trade `/v4/pre-post-market-trade/{symbol}`
- Aftermarket Quote `/v4/pre-post-market/{symbol}`
- Batch Quote `/v4/batch-pre-post-market/{symbol}`
- Batch Trade `/v4/batch-pre-post-market-trade/{symbol}`

### Market Analysis
- Market Capitalization `/v3/market-capitalization/{symbol}`
- Historical Market Cap `/v3/historical-market-capitalization/{symbol}`
- Market Gainers `/v3/stock_market/gainers`
- Market Losers `/v3/stock_market/losers`
- Most Active `/v3/stock_market/actives`
- Sector Performance `/v3/sectors-performance`
- Sector Historical Performance `/v3/historical-sectors-performance`
- Trading Hours `/v3/is-the-market-open`
- All Exchanges Trading Hours `/v3/is-the-market-open-all`

## 3. Fundamental Analysis
### Financial Statements
- Income Statement `/v3/income-statement/{symbol}`
- Balance Sheet `/v3/balance-sheet-statement/{symbol}`
- Cash Flow Statement `/v3/cash-flow-statement/{symbol}`
- Income Statement As Reported `/v3/income-statement-as-reported/{symbol}`
- Balance Sheet As Reported `/v3/balance-sheet-statement-as-reported/{symbol}`
- Cash Flow Statement As Reported `/v3/cash-flow-statement-as-reported/{symbol}`
- Full Financial Statement As Reported `/v3/financial-statement-full-as-reported/{symbol}`
- Financial Reports Dates `/v4/financial-reports-dates`
- Annual Reports (Form 10-K) `/v4/financial-reports-json`, `/v4/financial-reports-xlsx`

### Financial Analysis
- Key Metrics `/v3/key-metrics/{symbol}`
- Key Metrics TTM `/v3/key-metrics-ttm/{symbol}`
- Financial Ratios `/v3/ratios/{symbol}`
- Financial Ratios TTM `/v3/ratios-ttm/{symbol}`
- Financial Growth `/v3/financial-growth/{symbol}`
- Financial Score `/v4/score`
- Owner Earnings `/v4/owner_earnings`
- Income Growth `/v3/income-statement-growth/{symbol}`
- Balance Sheet Growth `/v3/balance-sheet-statement-growth/{symbol}`
- Cash Flow Growth `/v3/cash-flow-statement-growth/{symbol}`

### Valuation
- Discounted Cash Flow `/v3/discounted-cash-flow/{symbol}`
- Advanced DCF `/v4/advanced_discounted_cash_flow`
- Levered DCF `/v4/advanced_levered_discounted_cash_flow`
- Company Rating `/v3/rating/{symbol}`
- Historical Rating `/v3/historical-rating/{symbol}`
- Enterprise Values `/v3/enterprise-values/{symbol}`

## 4. Technical Analysis
- Simple Moving Average (SMA) `/v3/technical_indicator/{interval}/{symbol}?type=sma`
- Exponential Moving Average (EMA) `/v3/technical_indicator/{interval}/{symbol}?type=ema`
- Weighted Moving Average (WMA) `/v3/technical_indicator/{interval}/{symbol}?type=wma`
- Double EMA (DEMA) `/v3/technical_indicator/{interval}/{symbol}?type=dema`
- Triple EMA (TEMA) `/v3/technical_indicator/{interval}/{symbol}?type=tema`
- Williams %R `/v3/technical_indicator/{interval}/{symbol}?type=williams`
- Relative Strength Index (RSI) `/v3/technical_indicator/{interval}/{symbol}?type=rsi`
- Average Directional Index (ADX) `/v3/technical_indicator/{interval}/{symbol}?type=adx`
- Standard Deviation `/v3/technical_indicator/{interval}/{symbol}?type=standardDeviation`

## 5. Market Intelligence
### Price Targets & Analysis
- Price Targets `/v4/price-target`
- Price Target Summary `/v4/price-target-summary`
- Price Target By Name `/v4/price-target-analyst-name`
- Price Target By Company `/v4/price-target-analyst-company`
- Price Target Consensus `/v4/price-target-consensus`
- Price Target RSS Feed `/v4/price-target-rss-feed`
- Analyst Estimates `/v3/analyst-estimates/{symbol}`
- Analyst Recommendations `/v3/analyst-stock-recommendations/{symbol}`

### Upgrades & Downgrades
- Upgrades & Downgrades `/v4/upgrades-downgrades`
- RSS Feed `/v4/upgrades-downgrades-rss-feed`
- Consensus `/v4/upgrades-downgrades-consensus`
- By Company `/v4/upgrades-downgrades-grading-company`

### Corporate Events
- Earnings Calendar `/v3/earning_calendar`
- Earnings Historical & Upcoming `/v3/historical/earning_calendar/{symbol}`
- Earnings Confirmed `/v4/earning-calendar-confirmed`
- Earnings Surprises `/v3/earnings-surprises/{symbol}`
- Dividends Calendar `/v3/stock_dividend_calendar`
- Stock Splits Calendar `/v3/stock_split_calendar`
- IPO Calendar `/v3/ipo_calendar`

## 6. Institutional Activity
### Form 13F
- Form 13F `/v3/form-thirteen/{cik}`
- 13F Asset Allocation `/v4/13f-asset-allocation`
- Institutional Holders List `/v4/institutional-ownership/list`
- Holdings by Symbol `/v4/institutional-ownership/symbol-ownership`

### Insider Trading
- Insider Trades RSS `/v4/insider-trading-rss-feed`
- Insider Trades Search `/v4/insider-trading`
- Transaction Types `/v4/insider-trading-transaction-type`
- Insiders By Symbol `/v4/insider-roaster`
- Insider Trade Statistics `/v4/insider-roaster-statistic`

## 7. Investment Products
### ETFs
- ETF Holdings `/v4/etf-holdings`
- ETF Holding Dates `/v4/etf-holdings/portfolio-date`
- ETF Information `/v4/etf-info`
- ETF Sector Weightings `/v3/etf-sector-weightings/{symbol}`
- ETF Country Weightings `/v3/etf-country-weightings/{symbol}`
- ETF Exposure `/v3/etf-stock-exposure/{symbol}`
- ETF Holder `/v3/etf-holder/{symbol}`

### Mutual Funds
- Fund Dates `/v4/mutual-fund-holdings/portfolio-date`
- Fund Holdings `/v4/mutual-fund-holdings`
- Fund By Name `/v4/mutual-fund-holdings/name`
- Fund Holder `/v3/mutual-fund-holder/{symbol}`

## 8. Alternative Markets
### Cryptocurrency
- Cryptocurrencies List `/v3/symbol/available-cryptocurrencies`
- Full Quote List `/v3/quotes/crypto`
- Single Quote `/v3/quote/{cryptoPair}`
- Historical Price `/v3/historical-price-full/{cryptoPair}`
- Intraday Price `/v3/historical-chart/{interval}/{cryptoPair}`

### Forex
- Forex List `/v3/symbol/available-forex-currency-pairs`
- Full Quote List `/v3/quotes/forex`
- Single Quote `/v3/quote/{forexPair}`
- Historical Price `/v3/historical-price-full/{forexPair}`
- Intraday Price `/v3/historical-chart/{interval}/{forexPair}`

### Commodities
- Commodities List `/v3/symbol/available-commodities`
- Full Quote List `/v3/quotes/commodity`
- Single Quote `/v3/quote/{commodity}`
- Historical Price `/v3/historical-price-full/{commodity}`
- Intraday Price `/v3/historical-chart/{interval}/{commodity}`

## 9. Economic Data
- Treasury Rates `/v4/treasury`
- Economic Indicators `/v4/economic`
- Economics Calendar `/v3/economic_calendar`
- Market Risk Premium `/v4/market_risk_premium`

## 10. Bulk Data Access
- Multiple Company Prices `/v3/quote/{symbols}`
- Batch EOD Prices `/v4/batch-historical-eod`
- Bulk Income Statements `/v4/income-statement-bulk`
- Bulk Balance Sheets `/v4/balance-sheet-statement-bulk`
- Bulk Cash Flow Statements `/v4/cash-flow-statement-bulk`
- Bulk Ratios `/v4/ratios-bulk`
- Bulk Key Metrics `/v4/key-metrics-bulk`
- Bulk Earnings Surprises `/v4/earnings-surprises-bulk`
- Bulk Company Profiles `/profile-bulk`
- Bulk Stock Peers `/v4/stock_peers_bulk`
- Bulk Financial Growth `/v4/financial-growth-bulk`
-
## Notes
- All endpoints require API authentication
- Rate limits apply based on your subscription plan
- Some endpoints support additional optional parameters not shown here
- Documentation for specific endpoint parameters can be found in the code docstrings
