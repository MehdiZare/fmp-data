# FMP hosted MCP vs `fmp-mcp` (this package)

FMP ships a **hosted MCP server** on their infrastructure. This package ships
**`fmp-mcp`**, a local stdio server over our typed Python client. They are
different products that both talk to the same REST API and the same API key.

This page records the posture from [#230](https://github.com/MehdiZare/fmp-data/issues/230)
(2026-08-12): **docs + coverage matrix only**. There is no runtime helper, no
FastMCP dependency, and no CI smoke against their URL.

Always say **FMP hosted MCP** vs **`fmp-mcp` (this package)**. Do not write
"FMP MCP" unqualified.

## When to use which

| Need | Use |
|---|---|
| Zero-install agent in Claude Connectors, Cursor, or Cloudflare Workers AI | **FMP hosted MCP** |
| Small tool list (one tool per dataset, ~28 tools) | **FMP hosted MCP** |
| Typed Python models, offline/local process, manifests, LangChain | **`fmp-mcp` / this client** |
| Broad catalog (current counts in [tools.md](tools.md)) and method-shaped arguments | **`fmp-mcp`** |
| Bulk CSV, cache backends, validation modes, rate limits | **this Python client** (not either MCP) |

They are complementary. Hosted MCP is the "plug the URL into an agent" path.
`fmp-mcp` is the "full catalog, local, typed" path. We are **not** deprecating
`fmp-mcp` and we are **not** proxying our tool names onto theirs.

## Comparison

| | **`fmp-mcp` (this package)** | **FMP hosted MCP** |
|---|---|---|
| Where it runs | Local process (`fmp-mcp` CLI, stdio) | `https://financialmodelingprep.com/mcp` |
| Auth | `FMP_API_KEY` in env / config | API key in the query string (`?apikey=`) |
| Tool surface | One tool per endpoint; current catalog/default counts in [tools.md](tools.md) | **28** dataset tools (live 2026-08-12; changelog 2026-03-27 said 27) |
| How a call is shaped | Python method args (`symbol`, `from_date`, …) | `endpoint` enum + shared params (`symbol`, `from_date`, …) |
| Data path | Our client + Pydantic models | Their server → their REST (opaque) |
| Billing | Caller's FMP key / plan | Same |
| Transport | stdio | Remote MCP (JSON-RPC after `initialize`; `mcp-session-id` header) |

Their Python example (from [their docs](https://site.financialmodelingprep.com/developer/docs/mcp-server)):

```python
import asyncio
import os
from fastmcp import Client


async def main() -> None:
    url = "https://financialmodelingprep.com/mcp?apikey=" + os.environ["FMP_API_KEY"]
    async with Client(url) as client:
        print(await client.list_tools())
        print(await client.call_tool("quote", {"endpoint": "quote", "symbol": "AAPL"}))


asyncio.run(main())
```

`fastmcp` is **their** snippet, not a dependency of this package. Their
published example omits `endpoint` and pastes a literal key; the live
inputSchema requires `endpoint`, and a key in the query string will appear
in proxy and access logs and in any connector config that stores the URL.
Prefer env interpolation. Do not commit the keyed URL.

## Decision (#230)

Recorded 2026-08-12:

- **A — docs-only positioning.** This page + the README / `docs/mcp/index.md`
  pointers.
- **D — coverage matrix.** The table below is from a live `tools/list` on
  2026-08-12 (redacted; no key stored). Refresh it when FMP's changelog notes
  another MCP consolidation.
- **Not B.** No `fmp_data.mcp.remote` helper. A supported snippet would imply
  we own their session/auth story.
- **Not C.** No proxy that maps our names onto their 28 tools.
- **Not E.** `fmp-mcp` stays. Their catalog is smaller and dataset-shaped;
  ours is typed and endpoint-shaped.

Deferred: runtime dependency on their URL, dual CI, header-only auth (their
docs only show `?apikey=`).

## Live probe (2026-08-12)

- `POST /mcp?apikey=…` `initialize` → 200, `serverInfo.name = "FMP MCP Server"`,
  protocol `2025-03-26`.
- Subsequent `tools/list` needs the `mcp-session-id` response header. A bare
  GET without a session is rejected (as their docs warn).
- **28 tools**, not 27. The extra relative to the 2026-03-27 changelog note is
  `tipranks` (a paid add-on, not part of any FMP plan).
- Each tool takes a required `endpoint` enum that selects the underlying REST
  path. One hosted tool covers many of our client methods.

## Coverage matrix

Closest `fmp-mcp` / client surface for each hosted tool. "Closest" is the
module or default tools that answer the same questions — not a 1:1 rename.
Hosted `endpoint` values are FMP path slugs, not our `client.method` specs.

| Hosted tool | Hosted `endpoint` count | Closest here | Notes |
|---|---:|---|---|
| `quote` | 16 | `company.quote`, `company.simple_quote`, aftermarket + `batch.*_quotes` | Hosted also folds exchange/ETF/crypto/forex/index full-market quotes into this one tool |
| `search` | 7 | `market.search`, `market.search_name`, screener, CIK/ISIN/CUSIP search | Hosted `search-company-screener` is our `market.get_company_screener` |
| `company` | 17 | `company.*` (profile, executives, float, M&A, peers, …) | Includes `delisted-companies` (wired in #233 / PR #234) |
| `chart` | 10 | `company.historical_prices`, `company.intraday_prices` | Hosted splits EOD variants (`full` / `light` / dividend / non-split) as separate endpoints |
| `statements` | 27 | `fundamental.*` + revenue segmentation | Broadest hosted tool; includes as-reported and TTM variants |
| `analyst` | 8 | `intelligence.grades*`, `company.price_target_*`, `company.analyst_estimates` | |
| `calendar` | 9 | `intelligence` earnings/dividends/splits/IPO calendars | |
| `news` | 10 | `intelligence` news / press-release tools | |
| `senate` | 6 | `intelligence` senate/house trade tools | This client also ships trades-by-id, profiles, positions, and net-worth (#323–#325) |
| `directory` | 11 | `market` lists / `company.symbol_changes` | |
| `discountedCashFlow` | 4 | `fundamental.discounted_cash_flow`, levered + custom DCF | |
| `economics` | 4 | `economics.*` | |
| `commitmentOfTraders` | 3 | `economics.commitment_of_traders_*` | Hosted marks Premium+ |
| `ESG` | 3 | `intelligence` ESG tools | Hosted marks Ultimate/Enterprise |
| `Fundraisers` | 6 | `intelligence` crowdfunding / equity-offering tools | |
| `form13F` | 8 | `institutional.form_13f*` / holdings-by-quarter | Hosted marks Ultimate/Enterprise |
| `insiderTrades` | 6 | `institutional` insider tools | |
| `secFilings` | 12 | `sec` / `intelligence` filings tools | |
| `earningsTranscript` | 4 | `transcripts.*` (`latest_transcripts`, `transcript`, `transcript_dates`, `transcript_symbols`) | 4 catalog / 0 default — large payloads, load via manifest. Hosted marks Ultimate/Enterprise |
| `etfAndMutualFunds` | 9 | `investment.*` | |
| `indexes` | 15 | `index.*` + historical constituents | |
| `marketPerformance` | 11 | `market` gainers/losers/actives, sector/industry performance | |
| `marketHours` | 3 | `market` hours / holidays | |
| `technicalIndicators` | 9 | `technical.*` | Hosted marks Starter+ |
| `commodity` | 9 | `alternative.commodity_*` + `batch.commodity_quotes` | |
| `crypto` | 9 | `alternative.crypto_*` + `batch.crypto_quotes` | |
| `forex` | 9 | `alternative.forex_*` + `batch.forex_quotes` | |
| `tipranks` | 7 | **none** | Paid TipRanks add-on. Not in this client. |

### What hosted MCP does not replace

- **Bulk CSV** (`profile-bulk`, `rating-bulk`, …) lives on our `batch` client
  and is intentionally **0 default** MCP tools (large payloads).
- **Typed models, `FMP_VALIDATION_MODE`, cache, rate limits** exist only on
  this client.
- **Manifests / `FMP_MCP_TOOL_NAME_STYLE`** exist only on `fmp-mcp`.

### What we do not ship that they do

- `tipranks` (paid add-on).
- A single dataset tool that internally multiplexes dozens of REST paths.
  Our tools stay one-endpoint-each so LangChain / MCP argument schemas stay
  honest.

## Refreshing the matrix

When FMP's changelog mentions MCP again, call `tools/list` on their URL (key
in env, never committed) and update the table. Do not add a live CI job: it
needs a session, burns quota, and their 27→28 drift already shows the set
moves.

See also: [MCP index](index.md), [tools reference](tools.md),
[FMP MCP docs](https://site.financialmodelingprep.com/developer/docs/mcp-server).
