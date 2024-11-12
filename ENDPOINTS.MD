# Financial Modeling Prep (FMP) API Structure

## 1. Company Information & Search
### Basic Company Data
- Company Profile `/v3/profile/{symbol}`
- Company Core Information `/v4/company-core-information`
- Company Logo `/image-stock/{symbol}.png`
- Company Notes `/v4/company-notes`
- Employee Count & History `/v4/employee_count`, `/v4/historical/employee_count`
- Company Executives `/v3/key-executives`

### Search & Lists
- General Search `/v3/search`
- Symbol List `/v3/stock/list`
- Exchange Traded Fund List `/v3/etf/list`
- Available Indexes `/v3/symbol/available-indexes`
- Exchange Symbols `/v3/symbol/{exchange}`

### Identifiers & Mapping
- CIK Search `/v3/cik-search`
- CUSIP Search `/v3/cusip`
- ISIN Search `/v4/search/isin`

## 2. Market Data
### Price Data
- Real-time Quote `/v3/quote/{symbol}`
- Simple Quote `/v3/quote-short/{symbol}`
- Historical Price (Daily) `/v3/historical-price-full/{symbol}`
- Intraday Price `/v3/historical-chart/{interval}/{symbol}`
- Pre/Post Market Data `/v4/pre-post-market`, `/v4/pre-post-market-trade`

### Market Analysis
- Market Capitalization `/v3/market-capitalization`, `/v3/historical-market-capitalization`
- Market Gainers `/v3/stock_market/gainers`
- Market Losers `/v3/stock_market/losers`
- Most Active `/v3/stock_market/actives`
- Sector Performance `/v3/sectors-performance`
- Trading Hours `/v3/is-the-market-open`, `/v3/is-the-market-open-all`

## 3. Fundamental Analysis
### Financial Statements
- Income Statement `/v3/income-statement`
- Balance Sheet `/v3/balance-sheet-statement`
- Cash Flow Statement `/v3/cash-flow-statement`
- As-Reported Statements `/v3/income-statement-as-reported`, `/v3/balance-sheet-statement-as-reported`, `/v3/cash-flow-statement-as-reported`

### Financial Analysis
- Key Metrics `/v3/key-metrics`, `/v3/key-metrics-ttm`
- Financial Ratios `/v3/ratios`, `/v3/ratios-ttm`
- Financial Growth `/v3/financial-growth`
- Financial Score `/v4/score`

### Valuation
- Discounted Cash Flow `/v3/discounted-cash-flow`
- Advanced DCF `/v4/advanced_discounted_cash_flow`
- Company Rating `/v3/rating`
- Enterprise Values `/v3/enterprise-values`

## 4. Market Intelligence
### Analyst Coverage
- Price Targets `/v4/price-target`
- Analyst Estimates `/v3/analyst-estimates`
- Analyst Recommendations `/v3/analyst-stock-recommendations`
- Upgrades & Downgrades `/v4/upgrades-downgrades`

### Corporate Events
- Earnings Calendar `/v3/earning_calendar`
- Earnings Surprises `/v3/earnings-surprises`
- Dividends `/v3/stock_dividend_calendar`
- Stock Splits `/v3/stock_split_calendar`
- IPO Calendar `/v3/ipo_calendar`

### Institutional Activity
- Form 13F Filings `/v3/form-thirteen`
- Institutional Holders `/v3/institutional-holder`
- Insider Trading `/v4/insider-trading`

## 5. Alternative Markets
### Cryptocurrency
- Crypto List `/v3/symbol/available-cryptocurrencies`
- Crypto Quotes `/v3/quotes/crypto`
- Crypto Historical Data `/v3/historical-price-full/{cryptoPair}`

### Forex
- Forex Pairs List `/v3/symbol/available-forex-currency-pairs`
- Forex Quotes `/v3/quotes/forex`
- Forex Historical Data `/v3/historical-price-full/{forexPair}`

### Commodities
- Commodities List `/v3/symbol/available-commodities`
- Commodities Quotes `/v3/quotes/commodity`
- Commodities Historical Data `/v3/historical-price-full/{commodity}`

## 6. Technical Analysis
- Simple Moving Average `/v3/technical_indicator/{interval}/{symbol}?type=sma`
- Exponential Moving Average `/v3/technical_indicator/{interval}/{symbol}?type=ema`
- Relative Strength Index `/v3/technical_indicator/{interval}/{symbol}?type=rsi`
- Other Technical Indicators (MACD, Bollinger Bands, etc.)

## 7. Investment Products
### ETFs
- ETF Holdings `/v4/etf-holdings`
- ETF Information `/v4/etf-info`
- ETF Sector Weightings `/v3/etf-sector-weightings`
- ETF Country Weightings `/v3/etf-country-weightings`

### Mutual Funds
- Mutual Fund Holdings `/v4/mutual-fund-holdings`
- Mutual Fund Information `/v4/mutual-fund-holdings/name`

## 8. Economic Data
- Treasury Rates `/v4/treasury`
- Economic Indicators `/v4/economic`
- Economics Calendar `/v3/economic_calendar`
- Market Risk Premium `/v4/market_risk_premium`

## 9. Bulk Data Access
- Bulk Income Statements `/v4/income-statement-bulk`
- Bulk Balance Sheets `/v4/balance-sheet-statement-bulk`
- Bulk Cash Flow Statements `/v4/cash-flow-statement-bulk`
- Bulk Company Profiles `/profile-bulk`
- Bulk Financial Metrics `/v4/key-metrics-bulk`, `/v4/ratios-bulk`

## 10. Real-time Data Streams
### WebSocket Feeds
- Company WebSocket `wss://websockets.financialmodelingprep.com`
- Crypto WebSocket `wss://crypto.financialmodelingprep.com`
- Forex WebSocket `wss://forex.financialmodelingprep.com`
