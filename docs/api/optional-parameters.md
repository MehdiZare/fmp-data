# Optional request parameters

The sync and async clients accept the same filters. The additions below are
keyword-only and default to `None`. Existing argument order, positional calls,
defaults, and return types are preserved. Unset additions are omitted before
request validation, so existing endpoint defaults still apply: for example,
`market.search_by_cik("320193")` still requests `limit=50`.

Pass `False` or `0` explicitly when needed; neither is treated as unset. Limits
and pages are sent to FMP as requested. The SDK does not automatically paginate,
deduplicate overlapping pages, widen date ranges, or repair calendar records.

```python
from datetime import date

from fmp_data import FMPDataClient

with FMPDataClient.from_env() as client:
    holidays = client.market.get_holidays_by_exchange(
        "NYSE", from_date=date(2026, 1, 1), to_date=date(2026, 12, 31)
    )
    companies = client.market.search_by_cik("320193", limit=2)
    prices = client.company.get_intraday_prices(
        "AAPL",
        "5min",
        from_date=date(2026, 9, 10),
        to_date=date(2026, 9, 11),
        extended=False,
    )
    valuation = client.fundamental.get_custom_discounted_cash_flow(
        "MSFT", risk_free_rate=3.5, revenue_growth_pct=5.0
    )
```

Use `await client.<group>.<method>(...)` with `AsyncFMPDataClient` and the same
arguments. Dates are `datetime.date`; timestamps are Unix seconds. Country and
SIC codes are strings. FMP documents `invalid` as a string, so use `"false"` or
`"true"` rather than a Python boolean. Country values follow FMP's vocabulary;
the audit verified `US` and `UK`, while `GB` returned no rows.

## Added controls

Provider documentation checked on 2026-09-13. Each row links to its source.

| Client method | New Python arguments | FMP query keys |
| --- | --- | --- |
| [`market.get_holidays_by_exchange`](https://site.financialmodelingprep.com/developer/docs/stable/holidays-by-exchange) | `from_date`, `to_date` | `from`, `to` |
| [`market.get_company_screener`](https://site.financialmodelingprep.com/developer/docs/stable/search-company-screener) | `avg_volume_more_than`, `avg_volume_less_than` | `avgVolumeMoreThan`, `avgVolumeLowerThan` |
| [`market.get_market_hours`](https://site.financialmodelingprep.com/developer/docs/stable/exchange-market-hours) | `timestamp` | `timestamp` |
| [`market.get_all_exchange_market_hours`](https://site.financialmodelingprep.com/developer/docs/stable/all-exchange-market-hours) | `timestamp` | `timestamp` |
| [`market.get_all_shares_float`](https://site.financialmodelingprep.com/developer/docs/stable/all-shares-float) | `page`, `limit` | `page`, `limit` |
| [`market.get_available_exchanges`](https://site.financialmodelingprep.com/developer/docs/stable/available-exchanges) | `extended` | `extended` |
| [`market.search_by_cik`](https://site.financialmodelingprep.com/developer/docs/stable/search-cik) | `limit` | `limit` |
| [`company.get_employee_count`](https://site.financialmodelingprep.com/developer/docs/stable/employee-count) | `limit` | `limit` |
| [`company.get_historical_market_cap`](https://site.financialmodelingprep.com/developer/docs/stable/historical-market-cap) | `from_date`, `to_date`, `limit` | `from`, `to`, `limit` |
| [`company.get_symbol_changes`](https://site.financialmodelingprep.com/developer/docs/stable/symbol-changes-list) | `invalid`, `limit` | `invalid`, `limit` |
| [`company.get_intraday_prices`](https://site.financialmodelingprep.com/developer/docs/stable/intraday-5-min) | `extended` | `extended` |
| [`company.get_earnings`](https://site.financialmodelingprep.com/developer/docs/stable/earnings-company) | `include_report_times` | `includeReportTimes` |
| [`economics.get_economic_indicators`](https://site.financialmodelingprep.com/developer/docs/stable/economics-indicators) | `start_date`, `end_date` | `from`, `to` |
| [`economics.get_economic_calendar`](https://site.financialmodelingprep.com/developer/docs/stable/economics-calendar) | `country` | `country` |
| [`fundamental.get_custom_discounted_cash_flow`](https://site.financialmodelingprep.com/developer/docs/stable/custom-dcf-advanced) | 18 custom DCF assumptions (below) | Corresponding camelCase keys (below) |
| [`fundamental.get_custom_levered_dcf`](https://site.financialmodelingprep.com/developer/docs/stable/custom-dcf-levered) | 18 custom DCF assumptions (below) | Corresponding camelCase keys (below) |
| [`institutional.get_beneficial_ownership`](https://site.financialmodelingprep.com/developer/docs/stable/acquisition-ownership) | `limit` | `limit` |
| [`intelligence.get_earnings_calendar`](https://site.financialmodelingprep.com/developer/docs/stable/earnings-calendar) | `page` | `page` |
| [`intelligence.get_dividends_calendar`](https://site.financialmodelingprep.com/developer/docs/stable/dividends-calendar) | `page` | `page` |
| [`intelligence.get_stock_splits_calendar`](https://site.financialmodelingprep.com/developer/docs/stable/splits-calendar) | `page` | `page` |
| [`intelligence.get_esg_benchmark`](https://site.financialmodelingprep.com/developer/docs/stable/esg-benchmark) | `year` | `year` |
| [`intelligence.get_senate_trading`](https://site.financialmodelingprep.com/developer/docs/stable/senate-trading) | `page`, `limit` | `page`, `limit` |
| [`intelligence.get_house_disclosure`](https://site.financialmodelingprep.com/developer/docs/stable/house-trading) | `page`, `limit` | `page`, `limit` |
| [`alternative.get_crypto_intraday`](https://site.financialmodelingprep.com/developer/docs/stable/cryptocurrency-intraday-1-hour) | `start_date`, `end_date` | `from`, `to` |
| [`alternative.get_forex_intraday`](https://site.financialmodelingprep.com/developer/docs/stable/forex-intraday-1-hour) | `start_date`, `end_date` | `from`, `to` |
| [`alternative.get_commodity_intraday`](https://site.financialmodelingprep.com/developer/docs/stable/commodities-intraday-1-hour) | `start_date`, `end_date` | `from`, `to` |
| [`sec.get_sic_codes`](https://site.financialmodelingprep.com/developer/docs/stable/industry-classification-list) | `industry_title`, `sic_code` | `industryTitle`, `sicCode` |

## Custom DCF assumptions

Both custom DCF methods expose all 18 assumptions as `float | None`. Values are
forwarded without unit conversion; percentage fields use the units documented
by FMP. Omitting an assumption leaves its selection to the provider.

| Python argument | FMP query key |
| --- | --- |
| `revenue_growth_pct` | `revenueGrowthPct` |
| `ebitda_pct` | `ebitdaPct` |
| `depreciation_and_amortization_pct` | `depreciationAndAmortizationPct` |
| `cash_and_short_term_investments_pct` | `cashAndShortTermInvestmentsPct` |
| `receivables_pct` | `receivablesPct` |
| `inventories_pct` | `inventoriesPct` |
| `payable_pct` | `payablePct` |
| `ebit_pct` | `ebitPct` |
| `capital_expenditure_pct` | `capitalExpenditurePct` |
| `operating_cash_flow_pct` | `operatingCashFlowPct` |
| `selling_general_and_administrative_expenses_pct` | `sellingGeneralAndAdministrativeExpensesPct` |
| `tax_rate` | `taxRate` |
| `long_term_growth_rate` | `longTermGrowthRate` |
| `cost_of_debt` | `costOfDebt` |
| `cost_of_equity` | `costOfEquity` |
| `market_risk_premium` | `marketRiskPremium` |
| `beta` | `beta` |
| `risk_free_rate` | `riskFreeRate` |

## Tool integrations

Existing LangChain and MCP catalog entries expose these optional controls with
matching types and hints. The catalog inventory is unchanged: the screener,
available-exchanges, and company earnings convenience methods remain SDK-only;
applications can wrap their public methods explicitly. The intelligence earnings
tool already exposed `include_report_times`.

`market.search_exchange_variants(query)` retains its public argument name, but
now sends FMP's required `symbol` query key. For example, pass `"MSFT"` to search
Microsoft's exchange variants. The old `query=MSFT` wire request returned Apple
variants in the live audit.

## Provider qualification

Exposing a filter is separate from verifying the returned dataset. The audit
found overlapping calendar pages, an empty date-bounded GDP response despite
an in-range row in the unbounded series, and unresolved SEC profile identifier
behavior. NYSE 2027/2028 holiday and early-close completeness also remains under
investigation. No calendar flags, provider payloads, or date boundaries are
rewritten. An empty successful response does not establish completeness.

See [issue #396](https://github.com/MehdiZare/fmp-data/issues/396) for the provider
evidence and remaining qualification work.
