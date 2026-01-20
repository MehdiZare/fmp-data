# FMP API Endpoints (Stable)

All endpoints use the `/stable` prefix unless explicitly marked as `DIRECT`.

## 1. Company Information & Search
### Basic Company Data
- Company Profile `/stable/profile?symbol={symbol}`
- Company Core Information `/stable/company-core-information?symbol={symbol}`
- Company Logo `DIRECT /image-stock/{symbol}.png`
- Company Notes `/stable/company-notes?symbol={symbol}`
- Employee Count `/stable/employee-count?symbol={symbol}`
- Historical Employee Count `/stable/historical/employee-count?symbol={symbol}`
- Company Executives `/stable/key-executives?symbol={symbol}`

### Search & Lists
- Company Name Search `/stable/search-name?query={query}`
- Stock Symbol Search `/stable/search-symbol?query={query}`
- Symbol List `/stable/stock-list`
- Exchange Traded Fund List `/stable/etf-list`
- Available Indexes `/stable/index-list`
- Statement Symbols List `/stable/financial-statement-symbol-list`
- Tradable Search `/stable/tradable-list`
- Symbol Changes `/stable/symbol-change`
- Delisted Companies `/stable/delisted-companies`

### Identifiers & Mapping
- CIK Search `/stable/search-cik?cik={cik}`
- CUSIP Search `/stable/search-cusip?query={query}`
- ISIN Search `/stable/search-isin?query={query}`
- CIK List `/stable/cik-list?page={page}&limit={limit}`

## 2. Market Data
### Price Data
- Full Quote `/stable/quote?symbol={symbol}`
- Simple Quote `/stable/quote-short?symbol={symbol}`
- Historical Price (Daily) `/stable/historical-price-eod?symbol={symbol}`
- Intraday Price `/stable/historical-chart/{interval}?symbol={symbol}`

### Pre/Post Market
- Pre/Post Market Quote `/stable/pre-post-market`
- Batch Aftermarket Quote `/stable/batch-aftermarket-quote?symbols={symbols}`
- Batch Aftermarket Trade `/stable/batch-aftermarket-trade?symbols={symbols}`

### Market Analysis
- Market Capitalization `/stable/market-capitalization?symbol={symbol}`
- Historical Market Cap `/stable/historical-market-capitalization?symbol={symbol}`
- Market Gainers `/stable/biggest-gainers`
- Market Losers `/stable/biggest-losers`
- Most Active `DIRECT /most-actives`
- Sector Performance `/stable/sector-performance-snapshot`
- Trading Hours `/stable/exchange-market-hours?exchange={exchange}`

## 3. Fundamental Analysis
### Financial Statements
- Income Statement `/stable/income-statement?symbol={symbol}`
- Balance Sheet `/stable/balance-sheet-statement?symbol={symbol}`
- Cash Flow Statement `/stable/cash-flow-statement?symbol={symbol}`
- Income Statement As Reported `/stable/income-statement-as-reported?symbol={symbol}`
- Balance Sheet As Reported `/stable/balance-sheet-statement-as-reported?symbol={symbol}`
- Cash Flow Statement As Reported `/stable/cash-flow-statement-as-reported?symbol={symbol}`
- Full Financial Statement As Reported `/stable/financial-statement-full-as-reported?symbol={symbol}`
- Financial Reports Dates `/stable/financial-reports-dates?symbol={symbol}`
- Annual Reports (Form 10-K) `/stable/financial-reports-json?symbol={symbol}`, `/stable/financial-reports-xlsx?symbol={symbol}`

### Financial Analysis
- Key Metrics `/stable/key-metrics?symbol={symbol}`
- Key Metrics TTM `/stable/key-metrics-ttm?symbol={symbol}`
- Financial Ratios `/stable/ratios?symbol={symbol}`
- Financial Ratios TTM `/stable/ratios-ttm?symbol={symbol}`
- Financial Growth `/stable/financial-growth?symbol={symbol}`
- Financial Scores `/stable/financial-scores?symbol={symbol}`
- Owner Earnings `/stable/owner-earnings?symbol={symbol}`
- Income Growth `/stable/income-statement-growth?symbol={symbol}`
- Balance Sheet Growth `/stable/balance-sheet-statement-growth?symbol={symbol}`
- Cash Flow Growth `/stable/cash-flow-statement-growth?symbol={symbol}`

### Valuation
- Discounted Cash Flow `/stable/discounted-cash-flow?symbol={symbol}`
- Advanced DCF `/stable/custom-discounted-cash-flow?symbol={symbol}`
- Levered DCF `/stable/levered-discounted-cash-flow?symbol={symbol}`
- Historical Rating `/stable/historical-rating?symbol={symbol}`
- Enterprise Values `/stable/enterprise-values?symbol={symbol}`

## 4. Technical Analysis
- Simple Moving Average (SMA) `/stable/technical-indicators/sma`
- Exponential Moving Average (EMA) `/stable/technical-indicators/ema`
- Weighted Moving Average (WMA) `/stable/technical-indicators/wma`
- Double EMA (DEMA) `/stable/technical-indicators/dema`
- Triple EMA (TEMA) `/stable/technical-indicators/tema`
- Williams %R `/stable/technical-indicators/williams`
- Relative Strength Index (RSI) `/stable/technical-indicators/rsi`
- Average Directional Index (ADX) `/stable/technical-indicators/adx`
- Standard Deviation `/stable/technical-indicators/standarddeviation`

## 5. Market Intelligence
### Price Targets & Analysis
- Price Targets `/stable/price-target?symbol={symbol}`
- Price Target Summary `/stable/price-target-summary?symbol={symbol}`
- Price Target Consensus `/stable/price-target-consensus?symbol={symbol}`
- Price Target News `/stable/price-target-news?symbol={symbol}`
- Price Target Latest News `/stable/price-target-latest-news`
- Analyst Estimates `/stable/analyst-estimates?symbol={symbol}`
- Analyst Recommendations `/stable/analyst-stock-recommendations?symbol={symbol}`

### Upgrades & Downgrades
- Upgrades & Downgrades `/stable/upgrades-downgrades?symbol={symbol}`
- Consensus `/stable/upgrades-downgrades-consensus?symbol={symbol}`

### Corporate Events
- Earnings Calendar `/stable/earnings-calendar`
- Earnings Historical & Upcoming `/stable/historical/earning-calendar?symbol={symbol}`
- Earnings Confirmed `/stable/earning-calendar-confirmed`
- Earnings Surprises `/stable/earnings-surprises?symbol={symbol}`
- Dividends Calendar `/stable/dividends-calendar`
- Stock Splits Calendar `/stable/splits-calendar`
- IPO Calendar `/stable/ipos-calendar`

## 6. Institutional Activity
### Form 13F
- Form 13F `/stable/form-thirteen/{cik}`
- Form 13F By Date `/stable/form-thirteen-date/{cik}`
- 13F Asset Allocation `/stable/13f-asset-allocation?date={date}`
- Institutional Holders List `/stable/institutional-ownership/list`
- Holdings by Symbol `/stable/institutional-ownership/symbol-ownership?symbol={symbol}`

### Insider Trading
- Insider Trades Search `/stable/insider-trading?symbol={symbol}`
- Transaction Types `/stable/insider-trading-transaction-type`
- Insiders By Symbol `/stable/insider-roaster?symbol={symbol}`
- Insider Trade Statistics `/stable/insider-roaster-statistic?symbol={symbol}`

## 7. Investment Products
### ETFs
- ETF Holdings `/stable/etf-holdings?symbol={symbol}`
- ETF Holding Dates `/stable/etf-holdings/portfolio-date?symbol={symbol}`
- ETF Information `/stable/etf-info?symbol={symbol}`
- ETF Sector Weightings `/stable/etf-sector-weightings?symbol={symbol}`
- ETF Country Weightings `/stable/etf-country-weightings?symbol={symbol}`
- ETF Exposure `/stable/etf-stock-exposure?symbol={symbol}`
- ETF Holder `/stable/etf-holder?symbol={symbol}`

### Mutual Funds
- Fund Dates `/stable/mutual-fund-holdings/portfolio-date?symbol={symbol}`
- Fund Holdings `/stable/mutual-fund-holdings?symbol={symbol}`
- Fund By Name `/stable/mutual-fund-holdings/name?name={name}`
- Fund Holder `/stable/mutual-fund-holder?symbol={symbol}`

## 8. Alternative Markets
### Cryptocurrency
- Cryptocurrencies List `/stable/cryptocurrency-list`
- Full Quote List `/stable/quotes/crypto`
- Single Quote `/stable/quote?symbol={cryptoPair}`
- Historical Price `/stable/historical-price-eod?symbol={cryptoPair}`
- Intraday Price `/stable/historical-chart/{interval}/{cryptoPair}`

### Forex
- Forex List `/stable/symbol/available-forex-currency-pairs`
- Full Quote List `/stable/quotes/forex`
- Single Quote `/stable/quote?symbol={forexPair}`
- Historical Price `/stable/historical-price-eod?symbol={forexPair}`
- Intraday Price `/stable/historical-chart/{interval}?symbol={forexPair}`

### Commodities
- Commodities List `/stable/symbol/available-commodities`
- Full Quote List `/stable/quotes/commodity`
- Single Quote `/stable/quote?symbol={commodity}`
- Historical Price `/stable/historical-price-eod?symbol={commodity}`
- Intraday Price `/stable/historical-chart/{interval}/{commodity}`

## 9. Economic Data
- Treasury Rates `/stable/treasury-rates`
- Economic Indicators `/stable/economic-indicators`
- Economics Calendar `/stable/economic-calendar`
- Market Risk Premium `/stable/market-risk-premium`

## 10. Bulk Data Access
- Batch Quotes `/stable/batch-quote?symbols={symbols}`
- Batch Quote Short `/stable/batch-quote-short?symbols={symbols}`
- Batch Exchange Quotes `/stable/batch-exchange-quote?exchange={exchange}`
- Batch Market Cap `/stable/market-capitalization-batch?symbols={symbols}`
- Batch Aftermarket Quotes `/stable/batch-aftermarket-quote?symbols={symbols}`
- Batch Aftermarket Trades `/stable/batch-aftermarket-trade?symbols={symbols}`
- Batch Mutual Fund Quotes `/stable/batch-mutualfund-quotes`
- Batch ETF Quotes `/stable/batch-etf-quotes`
- Batch Commodity Quotes `/stable/batch-commodity-quotes`
- Batch Crypto Quotes `/stable/batch-crypto-quotes`
- Batch Forex Quotes `/stable/batch-forex-quotes`
- Batch Index Quotes `/stable/batch-index-quotes`
- Bulk Company Profiles `/stable/profile-bulk?part={part}`
- Bulk DCF Valuations `/stable/dcf-bulk`
- Bulk Stock Ratings `/stable/rating-bulk`
- Bulk Financial Scores `/stable/scores-bulk`
- Bulk Ratios TTM `/stable/ratios-ttm-bulk`

## Notes
- All endpoints require API authentication
- Rate limits apply based on your subscription plan
- Some endpoints support additional optional parameters not shown here
- Documentation for specific endpoint parameters can be found in the code docstrings
