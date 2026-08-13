# Changelog

All notable changes to the package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### FMP API surface (scan this first)

Source: FMP public changelog
([docs/changelog](https://site.financialmodelingprep.com/developer/docs/changelog))
plus a live `/stable` probe on 2026-08-12. Marketing-only items (dashboard,
localization, Insights Hub, plan add-ons) and FMP's hosted MCP product are
out of scope.

#### New (now first-class in this client)

| Surface | What you get | Wire key / param | Client |
|---|---|---|---|
| Financial ratios | Diluted P/E | `priceToEarningsDilutedRatio` | `FinancialRatios.price_to_earnings_diluted_ratio` |
| Financial ratios | Diluted PEG | `priceToEarningsDilutedGrowthRatio` | `FinancialRatios.price_to_earnings_diluted_growth_ratio` |
| Ratios TTM (+ `ratios-ttm-bulk`) | Diluted P/E TTM | `priceToEarningsDilutedRatioTTM` | `FinancialRatiosTTM.price_to_earnings_diluted_ratio_ttm` |
| Ratios TTM (+ `ratios-ttm-bulk`) | Diluted PEG TTM | `priceToEarningsDilutedGrowthRatioTTM` | `FinancialRatiosTTM.price_to_earnings_diluted_growth_ratio_ttm` |
| Company screener | Pagination | `page` (optional, omitted when unset) | `market.get_company_screener(..., page=None)` |
| Senate / House trades | Entity id | `senateID` (same key on House rows) | `SenateTrade.senate_id` / `HouseDisclosure.senate_id` |
| Ratings bulk | Score columns | `discountedCashFlowScore`, `returnOnEquityScore`, `returnOnAssetsScore`, `debtToEquityScore`, `priceToEarningsScore`, `priceToBookScore` | `CompanyRating.*_score` |
| Delisted companies | Slim delist list | `/stable/delisted-companies` (`page`, `limit`) | `company.get_delisted_companies` → `DelistedCompany` |

#### Updated (path or contract still matches; no caller change)

| FMP note | Path probed | Result |
|---|---|---|
| Exchange directory taxonomy (2025-06) | `/stable/available-exchanges` | 200. Keys `exchange`, `name`, `countryName`, `countryCode`, `delay`, `symbolSuffix` — already on `ExchangeSymbol`. |
| Exchange variants (2025-05/06) | `/stable/search-exchange-variants?query=Apple` | 200. Profile-shaped rows still parse as `CompanySearchResult`. |
| DCF valuations bulk naming (2025-06) | `/stable/dcf-bulk` | 200. Headers `symbol,date,dcf,Stock Price`. Client still remaps `Stock Price` → `stockPrice`. |
| Historical S&P 500 symbol naming (2025-06) | `/stable/historical-sp500-constituent` | 200. `symbol` present; `HistoricalIndexConstituent` still parses. |
| Stock ratings bulk field standardization (2025-06) | `/stable/rating-bulk` | 200. Score columns now typed on `CompanyRating` (see New). |
| CUSIP on fund disclosure holders (2025-10) | `/stable/funds/disclosure-holders-latest` | Only `securityCusip`. Already modeled; no second key. |
| ETF `isActivelyTrading` (2025-12) | `/stable/etf/info` | Present. Already modeled. |
| Splits calendar `splitType` (2025-11) | `/stable/splits-calendar` | Present (may be `null`). Already modeled. |
| Earnings `includeReportTimes` (2026-06) | `/stable/earnings-calendar?includeReportTimes=true` | Extra fields `confirmed`, `fiscalPeriod`, `fiscalYear`, `periodEnding`, `time`, `lastUpdated` already modeled. |
| Profile bulk `part=0..3` (2024-10) | `/stable/profile-bulk?part=0` | 200. Multi-part scheme unchanged. |
| Legacy route auth-gate (2025-08) | `/api/v3/profile/AAPL` | 403. No remaining live client path uses `APIVersion.V3`. The one leftover `V4` declaration is the already-withdrawn `stock-news-sentiments`. |

#### Deprecated / withdrawn in this pass

None. No FMP path we ship was newly retired by this changelog window.

### Changed

- **List-returning requests are `list[T]` without collapsing `request()` (#235).**
  `BaseClient.request` stays `Endpoint[T] -> T | list[T]`. Company list
  methods stay on `request()` (so existing mocks still work) and normalize
  through `EndpointGroup._unwrap_list`. `request_list` / `request_async_list`
  are the typed `Endpoint[T] -> list[T]` façade for callers that do not
  need to mock `request`. A lone object becomes `[row]`; an empty list
  stays empty.

- **Remaining list endpoints and methods now go through `_unwrap_list` /
  `Endpoint[T]` (#242).** Market, fundamental, investment, intelligence,
  institutional, alternative, economics, and technical list surfaces bind
  the row type (`Endpoint[T]`, not `Endpoint[list[T]]`) and normalize
  `request()` / `request_async()` with `_unwrap_list`. Company historical
  EOD helpers unwrap rows then wrap `HistoricalData`. `request()` stays
  `T | list[T]`. Methods are not switched to `request_list`.
  `get_mutual_fund_dates` / `get_fund_disclosure_dates` are annotated
  `list[PortfolioDate]` (runtime already returned `PortfolioDate` rows).

- **Leftover index, SEC, transcripts, and batch quote lists go through
  `_unwrap_list` / `Endpoint[T]` (#245).** Index constituents, SEC list
  surfaces (not `SEC_PROFILE`), transcripts, and batch JSON quote lists
  bind the row type and normalize `request()` / `request_async()`.
  `get_profile` stays `_unwrap_single`. Bulk-bytes / CSV paths stay on
  `_request_csv`. `request()` stays `T | list[T]`.

- **Batch bulk-bytes / CSV endpoints are `Endpoint[bytes]` (#247).**
  All 18 `*_BULK` CSV downloads bind `bytes` (not a row type). In batch,
  `_request_csv` is the only bytes helper. Quote lists stay on
  `_unwrap_list` (#246). `request()` stays `T | list[T]`.
  `FINANCIAL_REPORTS_XLSX` is unchanged: company XLSX download, still a
  bare `Endpoint`, not `_request_csv`.

- **`request(Endpoint[bytes])` is `bytes`; `request_list` refuses bytes
  (#249).** `request()` / `request_async()` overload to `bytes` for file
  downloads and stay `T | list[T]` for every other `T`.
  `request_list` / `request_async_list` overload to `NoReturn` and raise
  `TypeError` on `response_model is bytes` instead of wrapping the file
  as `[bytes]`. Quote lists still unwrap to `list[T]`.

- **Company financial-report endpoints are `Endpoint[T]` (#250).**
  `FINANCIAL_REPORTS_JSON` is `Endpoint[FinancialReportJSON]`;
  `FINANCIAL_REPORTS_XLSX` is `Endpoint[bytes]`. Client methods keep
  their existing type checks and still return `dict` / `bytes`. XLSX
  stays off batch `_request_csv`.

### Added

- **FMP hosted MCP vs `fmp-mcp` positioning (#230).** Docs-only: we are not
  wrapping FMP's remote MCP URL. README + `docs/mcp/index.md` point at
  `docs/mcp/hosted.md`, which records the 2026-08-12 decision (A+D: position
  + coverage matrix), a live `tools/list` of **28** dataset tools (changelog
  said 27; `tipranks` is a paid add-on), and when to use hosted MCP vs this
  package. No runtime helper, no FastMCP dependency, no CI smoke.

- **FMP changelog alignment (#229).** Three confirmed 2026 wire gaps, the
  leftover 2025-10 delisted-companies wiring (#233), plus the older-note
  re-probe above. Live `/stable` checks used the current API key on
  2026-08-12.

  - **Diluted P/E on ratios.** `FinancialRatios` and `FinancialRatiosTTM` now
    declare the diluted PE / diluted PEG pair FMP added on 2026-07-30
    (`priceToEarningsDilutedRatio`, `priceToEarningsDilutedGrowthRatio`, and
    the `*TTM` names on TTM + `ratios-ttm-bulk`). They previously landed only
    in `__pydantic_extra__` and could warn under `FMP_VALIDATION_MODE=warn`.
  - **Screener `page`.** `market.get_company_screener` / async accept optional
    `page: int | None = None`. Unset is omitted from the request (existing
    callers keep the same wire). `page=0` is sent. Live: `limit=2&page=0`
    and `limit=2&page=1` return distinct first rows.
  - **`senateID` on Senate and House trades.** `SenateTrade.senate_id` and
    `HouseDisclosure.senate_id` alias `senateID`. The wire name is kept on
    House rows (Pelosi → `P000197`); we do not invent `house_id`.
  - **`CompanyRating` score columns.** `rating-bulk` headers
    `discountedCashFlowScore` / `returnOnEquityScore` / `returnOnAssetsScore`
    / `debtToEquityScore` / `priceToEarningsScore` / `priceToBookScore` are
    now typed attributes. Fractional CSV cells such as ``"3.0"`` coerce to
    ``int`` so ``parse_csv_models`` does not skip the whole company row.
  - **`company.get_delisted_companies`.** The 2025-10 delisted-companies
    architecture sync left a live `/stable/delisted-companies` path whose
    declaration used `CompanyProfile` and had no client method. Sync and
    async clients now expose `get_delisted_companies(page=0, limit=100)`
    returning `DelistedCompany` (`symbol`, `companyName`, `exchange`,
    `ipoDate`, `delistedDate`). MCP: `company.delisted_companies` (in
    `DEFAULT_TOOLS`). LangChain indexes the same semantics key.

### Fixed

- **`FMPLogger.get_logger(__name__)` no longer doubles `fmp_data.` (#238).**
  The root logger is already `fmp_data`; `getChild(__name__)` was emitting
  `fmp_data.fmp_data.base`, so `caplog` and log aggregators filtering
  `fmp_data.base` missed extras / HTTP warnings. Qualified `fmp_data.*`
  names are now used as-is. If you already filtered the doubled name
  (`fmp_data.fmp_data.*`), switch to `fmp_data.*`. Handler and filter
  attachment is unchanged.

- **Remaining logging entry points go through `FMPLogger` (#241).**
  Production `logging.getLogger(__name__)` call sites (CSV extras, secure
  log-file chmod, cache backends, rate limiter, investment async) now use
  `FMPLogger().get_logger(__name__)`. LangChain class-name loggers use
  `__name__` + `.getChild(class)` so `ValidationRule` lands on
  `fmp_data.lc.validation.ValidationRule` rather than `fmp_data.ValidationRule`.
  Extras tests listen on `fmp_data.base` via `caplog`. Handler and filter
  attachment is unchanged.

- **CSV bulk parsing now honors `FMP_VALIDATION_MODE` (#232).** `parse_csv_models`
  used `model.model_validate` directly, so unknown bulk headers (`overallScore`
  on `rating-bulk`, a misspelled diluted-PE column) landed in
  `__pydantic_extra__` with no warn and no failure. They now share the JSON
  extras policy (`warn` / `strict` / `lenient`), keyed per bulk endpoint +
  field set. Invalid cells still retry URL fields, then **skip the row** in
  `lenient`/`warn` (logged) or **fail the request** in `strict`. Default mode
  is unchanged (`warn`). `rating-bulk` scores coerce only whole values
  (`"3.0"` → `3`); `"3.5"` is no longer truncated to `3`.

- **CI: post-release main→dev sync auto-merges and no longer needs admin bypass.**
  Sync-Main-to-Dev enables `gh pr merge --auto --merge` on the history-reachability
  PR so green Test-Matrix lands it without a human. Squash is never requested
  (it would re-break ancestry). Protect Dev dropped `required_signatures`, which
  had made every unsigned automation commit need `--admin` despite green checks;
  required Test-Matrix jobs, no force-push, and no branch deletion remain.

### Security

- **Isolated PyPI publishing and immutable Actions pins (#252).** Release,
  Dev-Release, and Publish-to-TestPyPI now build in a job with no OIDC token
  and publish from a second job that only downloads hashed artifacts. Publish
  jobs use the `pypi` / `testpypi` GitHub environments. All external
  `uses:` entries are pinned to full commit SHAs. The PEP 517 frontend is
  installed from `.github/requirements-build.txt` with `--require-hashes`.
  `workflow_dispatch` on Dev-Release is bound to `refs/heads/dev`. The
  TestPyPI PR path requires `head.repo.full_name == github.repository`.
  Tag-based TestPyPI publishes no longer `skip-existing`. **Before the next
  release**, set the PyPI and TestPyPI Trusted Publisher environment names
  to `pypi` and `testpypi` to match the workflows.

- **MCP manifests are data, not executed code (#252).** `load_manifest_tools`
  and `fmp-mcp validate` no longer `exec` user-supplied Python. Legacy
  `TOOLS = ["..."]` files are parsed with a restricted AST (docstring + that
  assignment only). Imports, calls, and any other statement are rejected.
  JSON and YAML accept a top-level list or `{"tools": ["..."]}`. TOML
  accepts `tools = ["..."]` only (no top-level array). On Python 3.10
  TOML uses `tomli` from the `mcp` extra; 3.11+ uses stdlib `tomllib`.
  Existing generated and example `.py` manifests keep working. A file
  that previously ran arbitrary code as "validation" now fails closed.

### Fixed

- **`_unwrap_list_result` refuses a bytes file (#253).** `request_list` already
  raised `TypeError` for `Endpoint[bytes]`, but the shared unwrap helper still
  treated `isinstance(payload, bytes)` as a lone row and returned `[bytes]`.
  Quote-list unwrap is unchanged.

### Changed

- **`fmp-mcp generate` writes JSON / YAML / TOML from the output suffix (#256).**
  `.json` is preferred (`{"tools": [...]}`). `.yaml` / `.yml` and `.toml` use
  the same `tools` object. A path with no suffix becomes `<name>.json`.
  `.py` still writes the restricted `TOOLS = ["..."]` form so existing
  scripts keep working. Unknown suffixes are refused.

### Security

- **API key stays on origin (#252 FMP-SEC-004).** `base_url` must be HTTPS
  except loopback HTTP. The key is sent only as the `apikey` query parameter
  (no client-wide header that a 302 would forward). Cross-origin redirects
  are refused.
- **Log redaction applies to child loggers and ``api_key=%s`` (#252 FMP-SEC-005).**
  The filter formats the message before masking, so a ``%s`` value is not
  treated as the secret (which previously crashed logging and printed the
  raw key). The filter is attached to each handler and each child logger.
  JSON extras and exception text are redacted.
- **MCP Claude config is written ``0600`` and the API key is prompted with
  echo off (#252 FMP-SEC-006).** Directory ``0700``; backups ``0600``;
  atomic replace.
- **Secondary secrets no longer survive ``str``/``repr`` (#252 FMP-SEC-007).**
  ``embedding_api_key`` and embedding ``api_key`` are ``repr=False``.
  ``CacheConfig.redis_url`` userinfo is redacted. Nested cache URLs on
  ``ClientConfig`` are redacted the same way.

## [2.6.0] - 2026-08-10

Released from `dev`. A correctness-and-contracts release: the LangChain and MCP
integrations now bind to client methods through **one** shared layer
(`fmp_data.tool_binding`) instead of two drifting copies, and every tool in the
catalogue reaches a real client method rather than falling back to
`client.request`. The endpoint catalogue, its documentation and its tool
manifests are each guarded row for row, so the drift this release fixes cannot
silently return.

This cut also hardens the **release automation** itself: unique TestPyPI
versions, real release-PR creation, post-squash history sync, PAT-triggered
CI on automation PRs, and a shared fail-closed mergeability check — so the
next release cannot go out on a green check for work that did not happen.

**Read before upgrading.** Four changes are breaking, all narrow:

| Change | Who it affects | Migration |
|---|---|---|
| `search-name` → `search_name` (#166) | anyone with a `ttl_overrides` key for it; `file`/`redis` cache users | rename the override key — you get a warning naming the replacement if you forget |
| MCP `form_13f` / `institutional_holdings` args (#188) | MCP clients | pass `year`/`quarter` instead of `report_date` |
| LangChain 13F tool names (#188) | stacks keying tools by name | `get_form_13f` → `get_form_13f_by_quarter` (args unchanged) |
| `setup_registry` / `create_vector_store` return shapes | direct callers | unpack `(registry, failures)`; catch `VectorStoreCreationError` instead of checking for `None` |

The Python client API is otherwise untouched — every date-shaped institutional
method keeps its signature and delegates to a new wire-shaped sibling.

Deprecations announced here (`Endpoint.arg_model` and the hand-written argument
models, `EndpointParam(required=...)`, the duplicate MCP tool keys, and the
withdrawn endpoints) are removed in **3.0**, not in this release.

### Added

- **Remaining wire-shaped institutional year/quarter client methods** (#192) - `InstitutionalClient` and `AsyncInstitutionalClient` gain `get_institutional_ownership_extract_by_quarter`, `get_institutional_ownership_analytics_by_quarter`, `get_holder_performance_summary_by_quarter`, `get_holder_industry_breakdown_by_quarter`, `get_symbol_positions_summary_by_quarter`, and `get_industry_performance_summary_by_quarter`. Same pattern as #188's `get_form_13f_by_quarter` / `get_institutional_holdings_by_quarter`: the `*_by_quarter` methods take the wire parameters (`year`/`quarter`, plus any pagination) and issue the request; the existing date-shaped methods derive the pair and delegate. `get_holder_performance_summary` is special: year/quarter remain optional — when `report_date` is omitted the request still goes without them. Python API only; mapping/tool semantics/MCP/LC are unchanged.
  - **`holder-performance-summary` ignores `year`/`quarter`, and now says so.** Alone among the six, this endpoint accepts the pair and applies neither. Probed against the live API: `cik=0001067983` returns a byte-identical 52-row payload spanning 2013-06-30 to 2026-03-31 unfiltered, with `year=2023&quarter=3`, and with `year=2019&quarter=1`. The other five were probed the same way and *do* filter (a 2023 Q3 request returns 2023-09-30 rows; 2019 Q1 returns 2019-03-31 rows).
  - So `get_holder_performance_summary_by_quarter(cik, 2023, 3)` returns the holder's entire history while its name promises one quarter — a silent wrong answer, and a more convincing one than the date-shaped form. Both routes into it now emit a `UserWarning` pointing at the `date` field on each row. Omitting `report_date` is the supported call and stays silent.
  - The parameters are still sent, in case FMP starts honouring them, and the public signatures are unchanged. The two public methods deliberately do **not** delegate to each other, so the warning fires once and is attributed to the caller's line on either route rather than to `client.py`.
- **`fmp_data.tool_binding`: one shared endpoint↔method binding layer for MCP and LangChain** (#188) - both integrations answer the same question (given an endpoint and the semantics naming its client method, how do I call that method?) and both answered it separately: `mcp.tool_loader._resolve_attr` walked the attribute chain, while `lc.vector_store` kept the alias table, the coverage gate and the invoke-time kwargs mapping. The rules now live in one core module that imports nothing but `inspect`, so neither integration can drift from it and neither needs an optional extra installed to use it.
  - New `uncovered_required_params()` names the required method parameters no wire field can fill; `method_dispatch_compatible()` is defined as its absence, so the two cannot disagree. The catalogue guard imports both instead of keeping private copies — a guard that reimplements the rule it guards can only check itself.
  - `resolve_attr()` (raises) and `resolve_client_method()` (returns `None`) are two reporting styles over **one walk**: the lenient resolver is implemented via the strict one (`try`/`except RuntimeError`), so edge cases (non-callable, missing link, multi-segment names) cannot diverge later. MCP must refuse to start on a ghost `method_name`; LangChain must fall back to `client.request` on a client with no sub-clients.
  - Every name previously importable from `fmp_data.lc.vector_store` still is, including the private `_camel_to_snake` / `_ENDPOINT_TO_METHOD_ALIASES` and `fmp_data.mcp.tool_loader._resolve_attr`. No caller has to change.
  - `tests/unit/test_tool_binding.py` pins the contract and runs in the core-only environment, which is what CI installs.
- **Wire-shaped institutional 13F client methods** (#188) - `InstitutionalClient.get_form_13f_by_quarter(cik, year, quarter)` and `get_institutional_holdings_by_quarter(symbol, year, quarter)`, plus their `AsyncInstitutionalClient` counterparts. This is the shape the API takes: `/stable/institutional-ownership/extract` and `/stable/institutional-ownership/symbol-positions-summary` both declare `year` and `quarter` mandatory and answer `400 Query Error: Invalid or missing query parameter - year` without them, and neither accepts a date at all — the period end `date` is a *response* field. The existing `get_form_13f(cik, report_date)` and `get_institutional_holdings(symbol, report_date, ...)` are **unchanged**; they now derive the year/quarter pair and delegate, so error handling and empty-result logging live on the wire-shaped methods that the tool layers call.
- **Catalogue-wide LangChain endpoint↔method parameter coverage guard** (#188) - after #172 / #186, tools dispatch through `client.<client>.<method>` when every required method parameter can be filled from wire/endpoint fields, otherwise fall back to `client.request`. That gate is per-tool at create time; a new shape mismatch could still land only as a silent request-fallback or a mandatory wire field omitted from the tool schema. `tests/unit/lc/test_endpoint_method_coverage.py` walks every `(endpoint_map × semantics)` pair, requires each method to resolve on a live client, pins the set of request-fallback tools (empty — the two institutional 13F tools that populated it were realigned later in this same release, see **Changed**; each allowlist entry pins its uncovered required params so known debt cannot silently grow), and pins the two known dropped-mandatory wire fields (revenue segmentation `structure`). Any *new* mismatch fails CI until allowlisted with a comment or fixed.

### Changed

- **Dependency floors raised to current PyPI stables** (2026-08-10 audit). Core (`httpx`, `pydantic`, `tenacity`) was already current. Optional/dev/docs floors move to: `mcp[cli]>=2.0.0` (1.x is security-fixes only; `_compat` still imports 1.x if present), `redis>=8.1.0`, `faiss-cpu>=1.15.0`, `langchain-core>=1.5.3`, `langchain-openai>=1.4.2`, `langgraph>=1.2.10`, `openai>=2.53.0`, `ruff>=0.16.2`, `mypy>=2.3.0`, `coverage>=7.15.4`, `pre-commit>=4.6.1`, `twine>=7.0.0`, `mkdocs-material>=9.7.7`. Pre-commit `ruff-pre-commit` rev → `v0.16.2`. GitHub Actions pins were already latest.
- **`fmp-mcp list` honours `COLUMNS` under `TERM=dumb`.** Rich short-circuits dumb terminals to 80×25 before reading `COLUMNS`, which folded Tool Spec mid-name and broke the #163 copy-paste guards. Console construction now passes explicit width+height when `COLUMNS` is set.
- **CI: three green-checks-for-work-that-did-not-happen in the release path** (#202, #203, #204).
  - **#202 — `Sync-Main-to-Dev` now keys on history reachability, not content.** After a squash-merge release, `dev` and `main` share a tree but not an ancestor link; the old `git diff` guard saw an empty delta and correctly did nothing, so the *next* release PR opened CONFLICTING and got no merge-ref CI. The workflow now runs `git merge-base --is-ancestor origin/main origin/dev` and, when false, opens a `sync/main-to-dev` PR that records a history-only merge (`merge -s ours` when trees match) or a real merge (when a hotfix landed on `main`). On merge *conflicts*, the job fails with recovery steps and does **not** force-push an empty tip over an open sync PR. `Guard-Main-Origin` fails when `mergeable_state=dirty` **or** when mergeability stays `unknown` after retries, so a conflicting/unresolved release PR is a red X rather than a hole in the checks list.
  - **#203 — `Release-PR` actually opens a `dev → main` PR.** It previously used `peter-evans/create-pull-request` with no working-tree changes, which always concluded "branch is not ahead of base" and exited green while creating nothing (both 2.5.0 and 2.6.0 were cut through hand-made PRs). It now calls `gh pr create --base main --head dev` when no such PR is open, fails if `main` is not an ancestor of `dev` instead of opening a silent CONFLICTING PR, and documents the `GITHUB_TOKEN` “no CI until next push/reopen” platform gap in the PR body and releasing docs.
  - **#204 — TestPyPI versions are unique per run, and collisions fail.** The test version was `${NEW_VERSION}.dev${PR_NUMBER}` with `skip-existing: true`, so the first push to a release PR published forever and every later green check re-advertised a stale wheel (observed on #201: `2.6.0.dev201` kept serving the pre-`a5badb4` build). The version is now `${NEW_VERSION}.dev${run_id * 1000 + run_attempt}`, the sdist `Version:` is asserted before upload, `skip-existing` is off for the PR path, and the bot comment states the commit SHA the artifact was built from.
- **CI audit: more silent-success and validation defects in adjacent workflows.**
  - **`Claude Code Review` used `secrets.*` in a job-level `if`.** That context is not allowed there; GitHub validates the workflow as a failed check named after the file on pushes that touch it, and the soft-fail gate from #184 never actually evaluated the secret. Token presence is now checked in a step (env), with checkout/review gated on the result.
  - **`Dev Release` had the same #204 shape.** Version was `X.Y.Z.dev{commit_count}` with `skip-existing: true`, so a workflow re-run (and any force-push that preserves commit count) re-advertised a stale TestPyPI wheel as success. Versions are now unique per `run_id`/`run_attempt`; collisions fail.
  - **`Release` (real PyPI) could skip creation and still report success.** An existing tag was "skipped", the job continued, and `skip-existing: true` on PyPI made a collision green. Tag and GitHub Release collisions now fail; PyPI publish uses `skip-existing: false`; empty version calc fails; untrusted PR fields pass through env (script-injection hardening); checkout prefers `merge_commit_sha`.
  - **`Rebase-Reminder` spammed a new comment on every `synchronize`.** It now updates a single bot comment via `body-includes` / `edit-mode: replace`, and deletes it when the branch catches up.
  - **Cassette secret scan claimed "new findings only" but never compared the baseline.** Dropped the misleading `--baseline` flag; cassettes are zero-tolerance.
  - **`Documentation` granted `pages: write` / `id-token: write` on every PR build.** Deploy-only permissions move to the deploy job.


- **BREAKING (cache/config): the `market` company-search endpoint is named `search_name`, not `search-name`** (#166) - it was the only endpoint in the catalogue whose `Endpoint.name` used a hyphen, and the only one whose `name` was identical to its `path`. `name` is now `search_name`; **`path` is unchanged at `search-name`**, because that is the real API path (re-probed live while making this change: `/stable/search-name` returns 200).
  - **`Endpoint.name` is not cosmetic**, which is why this waited. It is the literal, unhashed cache-key prefix in `_build_cache_key` and the lookup key in `_get_cache_ttl`, so the rename moves both.
  - **If you set a TTL override for this endpoint, rename the key.** `ttl_overrides={"search-name": 3600}` must become `ttl_overrides={"search_name": 3600}`. You will be told if you forget: unmatched override keys now warn and name the endpoint they nearly matched (see **Fixed**), and that warning shipped in this same release specifically so this rename announces itself instead of silently reverting you to `default_ttl`. That guard is what unblocked the change.
  - **Persisted cache entries for this endpoint are orphaned on upgrade.** The `file` and `redis` backends survive process exit, so previously written entries under the `search-name:` prefix become unreachable: one extra live API call per distinct query the first time you run 2.6.0, plus rows that sit until their TTL expires or they are evicted. The `memory` backend is unaffected. This is self-healing and needs no action; it is stated because it is a real, if small, behaviour change.
  - The row-level `docs/api/endpoints.md` guard forced the documentation to follow in the same commit.
  - **The second oddity #166 raised, `fail_to_deliver`, is deliberately left alone.** Its `path` uses underscores where every other path uses hyphens, but probed live, `fail_to_deliver`, `fail-to-deliver` and `fails-to-deliver` all return 404 (with a known-good control returning 200 in the same run). FMP no longer serves it; the method is `@deprecated` and the tool is in `WITHDRAWN_TOOLS` with no successor. Changing the path would swap one 404 for another. It goes away with the endpoint in 3.0.
- **BREAKING (MCP): `form_13f` / `institutional_holdings` args are now `year`/`quarter`, not `report_date`** (#188) - the tools keep their names, but callers must pass the wire shape the API actually requires. Migration: `form_13f(cik, report_date="2023-09-30")` → `form_13f(cik, year=2023, quarter=3)` (same for `institutional_holdings` with `symbol`). These now match the `parameter_hints` those semantics entries already declared, and an assistant no longer has to invent a quarter-end date to ask for a quarter. The Python client API is untouched: `get_form_13f(cik, report_date)` and `get_institutional_holdings(symbol, report_date, ...)` still accept dates and delegate.
- **BREAKING (LangChain): 13F tool names rename to `get_*_by_quarter`** (#188) - tools are renamed from `get_form_13f` / `get_institutional_holdings` to `get_form_13f_by_quarter` / `get_institutional_holdings_by_quarter` (LangChain tool names come from `EndpointSemantics.method_name`). Argument schemas are unchanged — `cik`/`symbol`, `year`, `quarter` — because these tools already used the wire schema under request-fallback. Stacks that key tools by name need the new names.
- **Institutional 13F tools now dispatch through client methods** (#188) - the `form_13f` and `institutional_holdings` semantics point at the new wire-shaped methods, so the request-fallback allowlist in `tests/unit/lc/test_endpoint_method_coverage.py` is now **empty**: every tool in the catalog dispatches through a client method. Side effect for LangChain Form 13F only: API/validation errors from the method now surface as `status: success` with empty `data` (matching the Python method's empty-on-error convenience), instead of `status: error` from the old request-fallback `except Exception` path. Holdings never swallowed errors and are unchanged.
- **Document LangChain wire names vs MCP method parameter names** (#188) - LangChain tool schemas keep API/wire parameter names and map at invoke when method-compatible; MCP tools expose Python method parameter names. README (LangChain section) and `docs/mcp/index.md` state the difference, and now record that no catalog tool falls back to `client.request`, so callers do not treat one schema as wrong.
- **`test_endpoint_group_organization` resolves semantics the way the registry does** (#188) - the guard stripped a leading `get_` and looked the remainder up directly, which is one of the three rules in `resolve_semantics_for_endpoint`. An endpoint-map key resolving by exact match or by `method_name` read as *missing* while registering correctly in the real registry. It now calls the resolver instead of reimplementing part of it.

- **Generated LangChain tool schemas now derive their examples from `valid_values` and narrow the field type to a `Literal`** (#156) - `ToolFactory.create_parameter_fields` previously advertised a parameter's hand-written `ParameterHint.examples` regardless of what the endpoint actually accepted (`EndpointParam.valid_values`, enforced client-side by `EndpointParam.validate_value`). The two sources described the same parameter and nothing kept them in sync, so a hint could advertise a value the client would reject with a `ValidationError` the model had no way to anticipate. #150 hit this concretely enough to split one shared `PERIOD_HINT` three ways just to keep every set of `valid_values` correctly advertised.
  - When an endpoint declares `valid_values`, the generated field's examples (and the description line that lists them) are now derived entirely from `valid_values` (via `ToolFactory.get_examples_for_param`) instead of from the hint; the hint keeps owning `natural_names`, `context_clues` and extraction patterns. **Schema-path agreement is therefore true by construction under `ToolFactory`.** That is a different pipeline from #150: `test_hint_examples_are_within_valid_values` still guards the *hand-written* `ParameterHint.examples` content, which continues to feed embedding text via `EndpointRegistry.get_embedding_text` and is not rewritten by #156.
  - The field type is also narrowed to a `Literal` of those values (`ToolFactory.get_field_type`), so the constraint reaches the pydantic model — and therefore the JSON schema the LLM sees — instead of only being discovered on a rejected call. `economics.get_economic_indicators`'s `name` parameter, for example, now advertises `Literal["GDP", "realGDP", ..., "15YearFixedRateMortgageAverage"]` (24 values) rather than a plain `str`.
  - Both derivations unwrap `Enum`-valued `valid_values` (as `economics` declares them, via `list(EconomicIndicatorType)`) to their wire value, mirroring the existing defensive handling in `EndpointRegistry._get_type_pattern` — `EndpointParam.__post_init__` already does this once at construction, so this is belt-and-braces for any future caller that builds an `EndpointParam` outside the dataclass path.
  - **This is a user-visible schema change, in the shape of #128's:** every constrained parameter's advertised examples and allowed values may change, and a caller that previously supplied a value only a hand-written hint (never `valid_values`) advertised will now see it rejected by the schema before the call is even made, rather than by the API afterward.
  - New guard `tests/unit/lc/test_tool_schema.py::test_constrained_params_advertise_only_valid_values` asserts, catalog-wide, that a generated schema's examples are a subset of the parameter's `valid_values` — floored at 20 constrained parameters checked (29 observed) so it cannot pass on an empty scan. A second, data-independent test, `test_examples_and_field_type_prefer_valid_values_over_a_drifted_hint`, manufactures a disagreement and drives it through `create_parameter_fields` (a hint example not in `valid_values`) so the production wiring — not only the helpers — is proven to catch a regression even on a day when every real hint in the catalog happens to agree with its `valid_values`. Mutation-tested: reverting either the examples-derivation or the `Literal` narrowing fails this pair.
- **`technical/mapping.py`'s local date hints folded onto the shared `fmp_data.lc.hints.DATE_HINTS`** (#179, closing #157's option 1) - `technical/mapping.py` bound its own `FROM_DATE_HINT`/`TO_DATE_HINT` for the `from`/`to` parameters shared by all nine indicator tools (`sma`, `ema`, `wma`, `dema`, `tema`, `williams`, `rsi`, `adx`, `standard_deviation`), describing the same start/end-of-range concept as `DATE_HINTS["start_date"]`/`["end_date"]` under different names, with different `natural_names`, `extraction_patterns`, `examples` and `context_clues` — exactly the same-concept-different-name gap #157 added a guard for, tracked as a deliberate, reviewed exception in `KNOWN_SAME_CONCEPT_DIVERGENCES` until this issue closed it.
  - `COMMON_PARAMS["from"]`/`["to"]` now point at `DATE_HINTS["start_date"]`/`["end_date"]` directly; the two local `ParameterHint` constants are deleted.
  - **What actually shifts for the nine tools' natural-language extraction:** `natural_names` gains `"since"` (start) and `"through"`/`"to"` (end) as recognized phrasings; `extraction_patterns` gains a bare `(\d{4}-\d{2}-\d{2})` pattern, so a date is now recognized even without a leading "from"/"to"/"until"/"starting" word; `examples` moves from 2024-dated (`"2024-01-01"`, `"2024-12-31"`) to `["2023-01-01", "2022-12-31"]` / `["2024-01-01", "2023-12-31"]`; `context_clues` gains `"after"` and loses `"start"` (start), gains `"ending"` and loses `"end"` (end). All of this is rendered into each tool's parameter description and into the embedding text the tool is indexed under (`EndpointRegistry.get_embedding_text`), so both the text an LLM reads and semantic-search ranking for these nine tools shift accordingly. `extraction_patterns` is documentation only today — nothing compiles or applies it — so that part changes what a reader sees, not what a query resolves to.
  - `KNOWN_SAME_CONCEPT_DIVERGENCES` in `tests/unit/test_hint_consolidation.py` is now empty; the four entries recording this divergence are removed rather than left to rot, since the fold makes `technical.mapping`'s bindings the same object as the shared hints (`hint_a is hint_b`), which the detector already skips. `test_no_same_concept_hint_under_a_different_name` passing with the baseline entry removed — rather than merely present — is the guard confirming the fold actually happened; mutation-tested by reverting the fold with the entries removed (fails on 36 newly-unallowlisted candidates) and by restoring the entries with the fold applied (fails on 4 stale, no-longer-detected entries).
- **BREAKING (CLI): `fmp-mcp list` now labels withdrawn endpoints, and the table's `Deprecated` column is renamed `Retirement`** (#158) - `list` derived deprecation from `DEPRECATED_TOOLS` alone, the table of duplicate *names* for a live method. It knew nothing about `EndpointSemantics.deprecated`, the flag marking endpoints FMP no longer serves, so `intelligence.stock_news_sentiments`, `intelligence.earnings_confirmed` and `intelligence.earnings_surprises` printed `deprecated: None` — indistinguishable from a live tool. Manifests are built by copying keys out of that listing, so this shipped users a tool that can only ever return an empty success, the same failure #137 removed from the LangChain side.
  - **The three retirement concepts stay three concepts.** They are not merged, because each asks something different of the reader: `DEPRECATED_TOOLS` is a second *name* for a method that still serves real data (swap the name, the replacement is a drop-in, the old key stops resolving in 3.0); `WITHDRAWN_TOOLS` / `EndpointSemantics.deprecated` means FMP does not serve the endpoint at all (it resolves and registers, and answers `[]` forever). Collapsing them would tell a user a withdrawal has a drop-in replacement when it has none.
  - **`--format json` gained two fields and changed none.** `deprecated` still holds the replacement spec or `null` and still means "renamed"; new `withdrawn` (boolean) and `successor` (nearest live spec for a withdrawal, or `null`) carry the other mechanism. A script reading `deprecated` sees exactly what it saw before — withdrawals are not folded into it — but a script that enumerated the keys of each entry will see two more.
  - **`table`, `list` and `tree` render `[DEPRECATED -> spec]`, `[WITHDRAWN, nearest live tool spec]` or `[WITHDRAWN, no replacement]`.** The rich and plain tables carry it in one column, headed `Retirement` rather than `Deprecated`: it now holds withdrawals too, and calling those "deprecated" would state the one thing that is untrue of them.
  - **`withdrawn` is the union of both sources, not a mirror of one.** `WITHDRAWN_TOOLS` and the semantics flag are held equal by #164's guard and agree exactly today (22 specs each), but they are separate tables — reading only one would look correct now and let drift decide what the CLI prints later. A guard empties `WITHDRAWN_TOOLS` and asserts the labels survive, so the flag cannot quietly stop being read.
  - Unchanged: every one of these keys still resolves, registers and serves. An explicit manifest naming one keeps working, `generate` keeps excluding them from a default catalog, and `validate` keeps exiting 0. This is labelling, not removal.
- **BREAKING (CLI): `fmp-mcp generate` exits non-zero rather than writing an empty manifest** (#160, #161) - an explicit `--tools` selection where nothing resolved wrote `TOOLS = []` and exited 0. That is #161's defect one command over: an artifact that cannot start a server, reported as success. An empty result that looks like a healthy one is worse than an error, because nothing prompts anyone to look.
  - **Before:** `fmp-mcp generate out.py --no-defaults --tools profil` → `Manifest saved to: out.py` / `Total tools: 0`, `$? == 0`, and `out.py` overwritten with an empty manifest.
  - **After:** nothing is written, `$? == 1`, and stderr names every failed ask beside its reason — `company.profil: unknown -- names nothing in the catalog`, `crypto_quotes: ambiguous -- claimed by alternative.crypto_quotes, batch.crypto_quotes; name the client` — so you can act without re-running `fmp-mcp list` and diffing by hand.
  - **The output file is not touched on failure.** The manifest already at that path may well be the good one, and clobbering it with an empty file was the more damaging half of the bug.
  - **This holds whether or not `--no-defaults` is passed.** `_add_defaults` used to run *before* the emptiness check, so on the default path a selection in which nothing resolved was topped up with the 137 default tools, the failures were discarded, and the command reported success — `fmp-mcp generate out.py --tools profil` wrote a 137-tool manifest and exited 0. The defaults are not an answer to an ask that named only tools which do not exist, so an explicit selection's emptiness is now judged before defaults are considered.
  - **A collision inside an explicit selection is also fatal, under the default name style.** `generate` still never *thins* an explicit selection — dropping one side behind the caller's back is what the `--tools` contract exists to prevent — but writing both sides and exiting 0 produced a file `validate` exits 1 on and that cannot start a server, so `generate && validate` failed in a pipeline on a file `generate` had just called a success. Nothing is written now and the exit is non-zero under `FMP_MCP_TOOL_NAME_STYLE=key`. Under `spec` both sides are advertised at their full spec and register fine, so the manifest is written and the exit is 0 — the same verdict `validate` and `register_from_manifest` reach. The refusal tracks the *active* style rather than a fixed one, so `generate` cannot invent a second opinion in either direction.
  - **`--strict` is not implemented and is not planned** (#161's open sub-question, recorded here rather than left hanging). It would mean a second, stricter verdict beside the exit code, and the work above makes the exit code itself the verdict for every shape that cannot start a server — a flag to opt into correctness implies the default is something else. Deprecated and withdrawn entries stay deliberately non-fatal: they resolve and register, so a manifest naming one is stale, not broken.
  - One unresolvable entry among resolvable ones is *not* fatal: it is warned about and skipped, exactly as before. Only a selection that yields nothing at all fails.
  - `generate_manifest()` returns `bool` (it returned `None`). A programmatic caller ignoring the return is unaffected; one that wants the verdict can now read it.
- **BREAKING (CLI): `fmp-mcp validate` exits non-zero for manifests registration refuses** (#161) - it printed its warnings to stderr and then printed `Manifest is valid with N tools` and exited 0 regardless. The exit code is the part a machine reads, so `fmp-mcp validate manifest.py` in CI was a green check on a manifest that could not start a server — turning a startup error into a trusted green check, which is the one failure mode a validator exists to prevent.
  - `validate_manifest` now returns `False` for exactly the four conditions under which `register_from_manifest` raises: an unknown entry, an ambiguous bare key, the same tool listed twice, and two tools claiming one advertised name. Nothing else.
  - **Deprecated and withdrawn entries still exit 0.** Both resolve and register today, and "is my manifest future-proof?" must stay answerable without failing a build. The migration tables still print.
  - The contradictory verdict is gone: a fatal finding prints `Manifest is invalid: N tools listed, but the findings above stop the server starting.` on stderr instead of `Manifest is valid` on stdout. The `1 tools` pluralisation bug went with it.
  - **If you have `fmp-mcp validate` in a pipeline**, a manifest with a typo'd, ambiguous, duplicated or clashing entry will now fail that build. That is the intended outcome, but it may fail on first upgrade.
  - The guard is not "validate rejects this one manifest". A parametrised table of manifests — the generated catalog plus every known-bad shape — asserts, under **both** name styles, that validate's verdict is exactly the inverse of whether `register_from_manifest` raises. Drift is what #149 fixed once; this is what stops it recurring.
- **BREAKING (CLI): `fmp-mcp list` output changed shape so every format shows a usable manifest entry** (#163) - `list` is the documented way to discover what to put in a manifest, and two of its four formats did not show one.
  - **`table`** no longer truncates the Tool Spec column. At the default 80-column width rich cut it to `company.historical_…`, rendering `company.historical_price` and `company.historical_prices` as the same string — flattening precisely the pair a reader most needs to tell apart, since one is deprecated in favour of the other. The column now folds (wraps) instead, and the `[DEPRECATED -> ...]` marker moved into **its own `Deprecated` column**: as a suffix on the spec cell it sat inside the truncated region, so the one piece of text explaining the duplicate row was the first thing cut.
  - **`tree`** labelled leaves with the *method* name, so the actual manifest entry never appeared anywhere in the output. Worse, a deprecated key shares its replacement's method, so the deprecated row was labelled with the replacement's name and read as self-referential. Leaves are now the full spec, with the method kept as trailing detail.
  - A guard asserts every format emits, for each of the 223 tools, a string containing its full spec, and that the deprecation marker and its replacement survive in all four.
  - **Folding is a wrap, not a truncation, and the difference is now pinned at the width that matters.** The "every format emits the full spec" guard renders at `COLUMNS=400`, where rich never has to shrink anything — so it cannot tell a lossless fold from a lossy cut. A second guard renders at `COLUMNS=80`, reassembles the spec column across its folded lines, and requires the two specs #163 is about to come back intact; a hard truncation that used no ellipsis character would slip past the ellipsis check but not this one. Note the practical consequence, now documented in `docs/mcp/configurations.md`: at 80 columns a long spec is split across two lines, so it is readable and unambiguous but not directly copy-pasteable — `--format json` remains the interface for scripts.
  - The output-shape change is now recorded in `docs/mcp/configurations.md` §3 as well as here. It was previously only in this file, while the PR describing it claimed both.
- **`fmp-mcp generate --tools` accepts bare tool keys** (#160) - `--tools profile` reported `Warning: Unknown tool 'profile', skipping` and wrote an empty manifest with exit 0, while `validate` and the loader both resolved the same entry happily. `generate` was the last entry point still doing its own membership test, and it tested against fully qualified specs only, so every bare key missed.
  - It now routes through `resolve_tool_spec`, the pure rule introduced in #151 — the **fourth consumer** of that rule rather than a fourth implementation of it. A guard asserts `generate`'s classification of every catalog spec, every bare key and the known-bad shapes matches the resolver's, so the membership test cannot grow back.
  - What is written out is always the resolved `<client>.<key>` spec, never the bare key as typed: the qualified form is unambiguous under either name style, so a manifest generated from bare keys keeps working if a second client later claims one of those keys.
  - An ambiguous bare key (`crypto_quotes`) is reported as an ambiguity naming both candidates. It previously produced the same misleading "unknown" message as a typo, sending users hunting for a spelling mistake that was not there.
  - A repeated ask (`--tools profile company.profile`) collapses to one entry rather than writing the tool twice, which the loader would then refuse — `generate` must not emit a file `validate` fails.
- **BREAKING: `create_vector_store()` raises `VectorStoreCreationError` instead of returning `None`** (#133) - the function wrapped its whole body, including `setup_registry()`, in `except Exception: return None`. That cancelled out the loud-failure behaviour added in #121/#127: an `ImportError` raised while `register()` lazily built validation rules still reached a library user as a bare `None`. And `None` carried no information — the blanket handler was the only caller-reachable `return None` (the two inside `try_load_existing_store` fall through to `create_new_store` and never reach the caller), so it unconditionally meant "something threw" and never said what. The return type narrows to `EndpointVectorStore`; there is no `None` path, no deprecation shim and no opt-in flag, because a sentinel whose only meaning is "an error you cannot inspect" is the defect.

  ```python
  # before
  store = create_vector_store(fmp_api_key=..., openai_api_key=...)
  if store is None:
      ...  # no idea why

  # after
  from fmp_data import VectorStoreCreationError, create_vector_store

  try:
      store = create_vector_store(fmp_api_key=..., openai_api_key=...)
  except VectorStoreCreationError as exc:
      print(exc.cause)  # the exception that actually stopped the build
      print(exc.failures)  # {endpoint name: validation error} for skipped endpoints
  ```

  - `VectorStoreCreationError` subclasses `FMPError`, so anything already catching `FMPError` keeps working. It lives in `fmp_data.exceptions` and is re-exported from `fmp_data`, not from `fmp_data.lc`, so `except VectorStoreCreationError` is importable **without the `langchain` extra installed** — you can catch it in code that only conditionally builds a store
  - `cause` is exposed as a named attribute as well as `__cause__`, so callers can branch on the underlying failure without reaching into dunders
  - `str(exc)` appends the skipped endpoints when there are any, following `RateLimitError`'s handling of `retry_after`. `failures` is the data this change made reachable, and plenty of callers write `logger.error(exc)` rather than destructuring it
  - `try_load_existing_store`'s internal `None` returns are untouched. They mean "fall through to create", not "error", and remain internal
- **BREAKING: `setup_registry()` returns `(registry, failures)` rather than a bare `EndpointRegistry`** (#133, closing note) - `register_batch()` returns a per-endpoint failure dict; `setup_registry()` inspected it, logged a summary and discarded it, so parsing logs was the only way for a programmatic consumer to learn which endpoints were skipped. The return is now a `RegistrySetup` NamedTuple, so `registry, failures = setup_registry(client)` unpacks or `result.registry` / `result.failures` reads. Those same failures are what `create_vector_store` attaches to `VectorStoreCreationError.failures` when a later step fails. Callers doing `registry = setup_registry(client)` must unpack or take `.registry`.
- **Generated LangChain tool schemas gained optional arguments where they previously had required ones** (#128) - this is the user-visible half of the fix below. A tool for `market.get_historical_sector_pe` now requires only `sector`; `from`, `to` and `exchange` became optional. Prompts or callers that always supplied every argument keep working — the change only removes an obligation — but anything asserting on a tool's required-field set will see it shrink.
- **`ToolFactory.create_parameter_fields` signature break** (#128) - it now takes `mandatory_params` and `optional_params` as two separate arguments instead of one concatenated list. External callers constructing an args model by hand must split their list; passing the old single sequence raises `TypeError` rather than silently mis-shaping a schema.
- **Every endpoint's `arg_model` attribute now reads `None`** (#153) - the 68 `arg_model=` assignments are deleted, so `from fmp_data.technical.endpoints import SMA; SMA.arg_model` returns `None` where it used to return `TechnicalIndicatorArgs`. Reading the attribute cannot warn — it is a plain Pydantic field, and a read-side warning would need a descriptor — so this one is called out here rather than left to be discovered. Nothing in this package ever read it (see *Deprecated* below), and the field itself stays until 3.0; only the per-endpoint values are gone. Code that introspected `endpoint.arg_model` to build its own schemas should read `mandatory_params`/`optional_params` instead, which is what the package itself does.

### Deprecated

- **`EndpointParam(required=...)` is deprecated in 2.7 and removed in 3.0; requiredness is now derived from list membership** (#165) - an endpoint declares its parameters in `mandatory_params` or `optional_params`, and every parameter *also* carried a `required` flag restating the same fact. Two representations of one thing can disagree, and #144 found 14 that did: params sitting in `optional_params` while declaring `required=True`. #155 reconciled them and added a guard; this removes the second representation so there is nothing left to reconcile.
  - `EndpointParam.required` is now a **read-only property**. `Endpoint` stamps it from the list the parameter sits in, so the two cannot drift apart — and because there is no setter, they cannot be pushed apart at runtime either. The 544 `required=` declarations across the 13 endpoint modules are gone.
  - **Behaviour at the one read site is unchanged.** `EndpointParam.validate_value` is public and raises `Missing required parameter` for a `None` on a required param. That path is only reachable by calling it directly — `validate_params` skips `None` for non-mandatory params first — so it could not simply be dropped. It still reads `self.required`; the value now arrives from the endpoint rather than from the declaration.
  - **The argument still works until 3.0.** Passing `required=` warns but is accepted, and it keeps its **positional slot 4** so an existing positional `EndpointParam("q", loc, typ, True, "desc")` call is not silently shifted one place and left with `True` in `description`. For a parameter attached to an endpoint the declared value is discarded; for a standalone parameter it is still honoured, so a caller who kept the argument keeps the behaviour they had. Requiredness is stamped once at endpoint construction; post-construction mutation of the param lists does not re-stamp.
  - A declaration that *contradicts* its list gets its own warning naming the endpoint and the parameter, rather than being folded into the generic deprecation notice. List membership wins.
  - Holding `required` in slot 4 costs `description` its no-default status, so omitting a description is no longer a type error. `test_every_param_has_a_description` covers what mypy no longer can.
  - Declaring the same parameter name in both `mandatory_params` and `optional_params` now raises at endpoint construction. Nothing in the package does it; it is the only remaining route to a parameter that is required and optional at once.
  - `tests/unit/test_param_required_consistency.py` no longer reconciles flags, it asserts the derivation: that no endpoint source declares `required=` (a source-level scan, since a value overridden at runtime leaves no runtime trace), that every one of the 544 params reports its list's answer, that the property has no setter, and that the deprecated argument still works and still warns.

- **`Endpoint.arg_model` and the hand-written argument models are deprecated; they go in 3.0** (#153, #167) - `arg_model` was declared once in `fmp_data/models.py`, assigned 68 times across six domains, and **read by nothing**. `grep -rn "\.arg_model"` finds no read site anywhere in the package. LangChain argument schemas are and always were built *dynamically*, in `fmp_data/lc/vector_store.py`, from each endpoint's `mandatory_params`/`optional_params` plus its `parameter_hints`. So the 106 `*Args` classes in the nine `schema.py` modules never reached a tool, whether or not their endpoint assigned `arg_model`.
  - **The 68 `arg_model=` assignments are removed now, not in 3.0.** No code path *inside this package* reads the field, so deleting the assignments changes no behaviour here — but an external caller reading `SOME_ENDPOINT.arg_model` now gets `None`, silently and without a warning. That is recorded under *Changed* above rather than buried here. What they did do is mislead — `arg_model=ETFHoldingsArgs` reads as "this model validates that endpoint's arguments", and it never did. #141 was filed on exactly that misreading, reporting three domains as unwired when all nine were equally inert
  - **The `arg_model` field itself is kept and deprecated**, so an external caller constructing an `Endpoint` with it still imports and still works. Supplying a non-`None` value now emits a `DeprecationWarning`; `arg_model=None` and omitting it stay silent
  - **All 116 argument classes stay importable** (106 `*Args` plus 10 singular `*Arg`) and now emit a `DeprecationWarning` on two paths, via a new no-field, no-config `fmp_data.schema.DeprecatedArgModel` base: when validated (`Model(...)` or `Model.model_validate(...)`), and when a JSON schema is generated from one (`Model.model_json_schema()`). The second path matters because an "argument model" an external caller kept is most naturally handed to a tool/function-schema generator, which never validates anything — covering only validation would let that caller reach 3.0 without a single warning. Importing one is still silent — an import is not use, and JSON-schema generation is lazy in pydantic v2, so nothing fires at class-creation time. The runtime enums that happen to live in those modules (`EconomicIndicatorType`, `IntradayTimeInterval`) are untouched and are not deprecated
  - **Every one of those 116 classes now carries its own `.. deprecated:: 2.7` marker in `__doc__`** (#178) - only the eight roots (`BaseArgModel`, `BaseListArgs`, `BaseQuoteArgs`, `BaseSearchArg`, `BaseExchangeArg`, `QuoteArgs`, `MarketCapArgs`, `BaseSymbolArg`) had one, and docstrings are not inherited for documentation purposes, so `help(ETFHoldingsArgs)`, IDE hover and Sphinx all showed nothing. The runtime warning only reaches someone who *runs* the code; someone reading the docs before writing the call — the audience most able to avoid the migration entirely — was told nothing. `DeprecatedArgModel.__init_subclass__` appends the directive to any subclass that does not already state one, so the concrete models and any future subclass are covered from one place rather than by 116 hand-edited docstrings that can drift. The class's own summary is kept and the note appended after it as its own paragraph; a class with no docstring gets a generated one-line summary. **Import stays silent** — this is a docstring rewrite at class-creation time, not a warning. One visible side effect: pydantic derives a model's JSON-schema `description` from `__doc__`, so `Model.model_json_schema()["description"]` now carries the note for any model that does not override it via `json_schema_extra` (the `BaseArgModel` subtree does, and is unaffected). That is the same audience the `model_json_schema()` warning targets, told in the artifact rather than only in stderr
  - **#167's drift is resolved by deletion rather than repair.** `TechnicalIndicatorArgs`, shared by all nine indicator endpoints, has *zero* parameter-name overlap with its endpoint — the model offers `start_date`/`end_date`/`period`/`interval` where the endpoint wants `from`/`to`/`periodLength`/`timeframe`, and both `periodLength` and `timeframe` are mandatory with nothing in the model able to fill them. Five further models carry the same defect. Correcting them would mean maintaining a second hand-written copy of parameter declarations that a live-API audit found wrong in ~33 places on the *first* copy this week (#135, #144, #146, #167 are all that drift class), against a mechanism nothing reads
  - `tests/unit/test_arg_model_consistency.py` (added in #154) is **removed** and replaced by `tests/unit/test_arg_model_deprecation.py`. The old guard paired models to endpoints via `Endpoint.arg_model`, so removing the assignments removes its only pairing source; and freezing a drift baseline for a layer scheduled for deletion buys nothing. Its two endpoint-side facts — #143's `ETF_HOLDINGS.date` being optional and #152's `MUTUAL_FUND_HOLDINGS.date` being mandatory — are kept in the new file, because those are declarations on the *endpoint* and outlive the models. `_KNOWN_PARAM_DRIFT` goes with the old file
  - The new guard also carries the 3.0 breadcrumb, in the idiom of #136/#147: it fails once a `## [3.x.y]` heading lands in this file, and names exactly what to delete
- **Reading the numbers in the #169 entries below** (#171) - they are all correct and they do not add up, because they are measured at two different layers and a reader will try to reconcile them and fail. **Endpoint declarations**: the live probe found **28** paths that 404 for every request (see `tests/e2e/test_live_signatures.py`); of those, the **eight** under *Eight endpoints FMP no longer serves* get the `@deprecated` early-return treatment, and the **fifteen** in the table below are left pointing at an equivalent this package already ships. **MCP tool keys**: `WITHDRAWN_TOOLS` had **19** entries at #169 and **22** after #164 added three, of which **4** and then **7** respectively have no successor at all. The two layers are not subsets of one another — one endpoint can back more than one tool key, and a dead endpoint with no MCP tool contributes no key — so a spec count and an endpoint count are not expected to meet. #169's PR body also quotes **21** for endpoint declarations deprecated with a replacement the library already ships; that is a third scoping again, and the entries here are the authority.
- **Withdrawal is now a resolution status, so a withdrawn tool key actually announces itself** - `_warn_if_deprecated` grew a branch for `WITHDRAWN_TOOLS` with wording that deliberately avoids promising a drop-in. Nothing reached it. `_resolved` set `ResolutionStatus.DEPRECATED` only from `DEPRECATED_TOOLS`, and the two sets are disjoint *by assertion*, so every withdrawn spec resolved as plain `RESOLVED` and the call site's `if resolution.is_deprecated` gate was never true. The entire branch was unreachable in production while its unit test — which called the private helper directly — passed.
  - `ResolutionStatus.WITHDRAWN` is a real member now, set by `_resolved`, and the registration path gates on `is_retired` (deprecated **or** withdrawn) rather than `is_deprecated`. `is_resolved` includes it, because a withdrawn tool still registers and answers empty; it is not a failure to resolve
  - `Resolution.successor` is kept separate from `Resolution.replacement`. A deprecation is a rename and its replacement is a drop-in; a withdrawal is a migration whose payload differs, and four of the 19 have no successor at all. Collapsing them would make `fmp-mcp validate` print "use X" for an endpoint that has no X
  - **`fmp-mcp validate` reported a manifest full of dead tools as perfectly healthy.** `_classify_manifest_entries` bucketed on `resolution.replacement is not None`, and a withdrawal carries no replacement, so all 19 fell through every branch. It now buckets on status and reports withdrawn as its own category, saying the endpoint answers with no data. `validate` and `generate` agreeing is the whole point of #149; they had drifted
  - `fmp-mcp generate --tools <withdrawn-spec>` now warns on stderr, mirroring the deprecated branch beside it. The default path drops withdrawn specs before the collision pass, so an explicit `--tools` is the only way one reaches a generated manifest — and it was the one place a dead tool was written with nothing said about it
  - `_add_defaults` skips withdrawn as well as deprecated specs. Dead defence today, since neither set intersects `DEFAULT_TOOLS`, but a future withdrawn default would otherwise be reinstated into a manifest the same release just cleaned
  - The regression test goes through `_resolved`, not around it, and sweeps every entry in `WITHDRAWN_TOOLS`. Testing a helper by calling it directly cannot show that anything calls it
- **The LangChain vector store still indexed and offered all 19 withdrawn endpoints** - the MCP surface was taught to drop them; the semantic-search surface was not, and no `mapping.py` was touched. A LangChain agent asked for crypto quotes or analyst price targets still retrieved the dead endpoint, called it, and got an empty *success* indistinguishable from "no data matched" — the precise failure #137 exists to prevent. All 19 `EndpointSemantics` entries now carry `deprecated=True`, which is the mechanism that actually filters: `_is_deprecated` covers `add_endpoint`, `add_endpoints`, the load path and the search-result filter in one move. A new guard derives the expected set from `WITHDRAWN_TOOLS` itself, so the next withdrawal cannot fix one surface and forget the other.
- **Live-API tests are opt-in from `make test` too, not just from CI** - `tests/e2e/` is marked `live` and deselected by a `-m "not live"` default in `addopts`. The `FMP_TEST_API_KEY` check alone was not enough: `make test` sources `.env` and promotes `FMP_API_KEY` to `FMP_TEST_API_KEY`, and `testpaths` is `tests`, so a maintainer running the project's own test command with a populated `.env` fired roughly 700 live requests against a default quota of 250 a day. Run them with `pytest tests/e2e -m live`.
- **A default MCP server no longer advertises 19 tools that cannot work** - `DEFAULT_TOOLS` goes **156 → 137**. Every removed key names an FMP endpoint that returns 404 for every request, so the tool could only ever answer with nothing while still competing for an LLM's attention against the tool that does work. The catalog is unchanged at 223: all 19 stay loadable by explicit manifest until 3.0, and resolving one now emits a `DeprecationWarning`. That last clause was false when first written, and the fix is described under *Withdrawal is now a resolution status* below.
  - This is **breaking for default-server users** in a minor release, in the same way and for the same reason as #136: the defect is that the tools are advertised, and it cannot be fixed while they remain advertised. If a saved prompt or hard-coded call names one, switch to the successor below or add the old key to an explicit manifest.
  - The successors are recorded in a **new `WITHDRAWN_TOOLS` map**, deliberately *not* merged into `DEPRECATED_TOOLS`. Those mean different things: `DEPRECATED_TOOLS` is two keys for one callable, and its warning says in as many words that the replacement is a drop-in. Every `WITHDRAWN_TOOLS` successor is a *different* endpoint with a different payload, and four have no successor at all. Merging them would have made the drop-in promise false — a guard test now asserts the two maps stay disjoint and that no `WITHDRAWN_TOOLS` pair shares a `(client, method)`.
  - The withdrawn-key warning uses its own wording: it says the endpoint is gone, names the closest live tool where one exists with an explicit "its payload differs — check the fields you rely on", and says "FMP publishes no replacement" where none does.
- **Eight endpoints FMP no longer serves** - each 404s on the `stable` API. They now warn through the existing `@deprecated` helper, return empty **without issuing the request**, and name the closest live alternative. A call that can only earn a 404 should not cost a rate-limit slot.

  | Deprecated method | Closest live alternative | How it differs |
  |---|---|---|
  | `company.get_core_information` | `company.get_profile` | flatter; drops SIC, state of incorporation, fiscal-year registration detail |
  | `company.get_price_target` | `company.get_price_target_summary` / `_consensus` | an aggregate, not the per-analyst series |
  | `company.get_analyst_recommendations` | `intelligence.get_grades_consensus` | one current tally, not a monthly series |
  | `company.get_upgrades_downgrades` | `intelligence.get_grades` | same grade changes, different field names; no action/price-target columns |
  | `company.get_upgrades_downgrades_consensus` | `intelligence.get_grades_consensus` | same tally, without the derived `consensus` label |
  | `institutional.get_asset_allocation` | *(none)* | nearest live data is per-filer 13F holdings, aggregated by hand |
  | `institutional.get_fail_to_deliver` | *(none)* | the SEC publishes the same fails-to-deliver files itself |

  - **The dead paths are deliberately not repointed.** A candidate path returning 200 with a different shape is worse than an honest 404, so each docstring states exactly how the replacement differs rather than silently swapping payloads
  - **These use `@deprecated`, not `@removed`, and that is a deliberate 3.0 decision.** `@removed` raises `RemovedEndpointError`, but every endpoint here carries `allow_empty_on_404=True`, so today they already return `[]` — a caller handling the empty list works now and would start raising. That is a breaking change, and this is a minor release. `@deprecated` preserves the current return contract exactly while making the warning loud, which is the same 2.6-deprecate / 3.0-remove cycle #136 and #147 established for tool keys. **The switch to `@removed` belongs in 3.0**, alongside dropping the endpoints themselves; `institutional.get_asset_allocation` and `institutional.get_fail_to_deliver` are the two with no successor at all and so the clearest candidates
  - `company.COMPANY_OUTLOOK` was already orphaned — declared, but reachable from no client method and no mapping. Its description is corrected rather than left advertising a dead path to the LangChain and MCP surfaces
  - Endpoint descriptions for all eight now open with `DEPRECATED and non-functional … Do not select it`, matching the wording `intelligence` already used for `stock_news_sentiments`. **Wording alone does not exclude anything, and an earlier draft of this entry claimed it did.** `registry.py` builds embedding text from `semantics.natural_description`, `example_queries` and `related_terms`; the endpoint `description` is never embedded. What actually keeps an endpoint out of the vector store is `EndpointSemantics.deprecated`, which `_is_deprecated` reads on the add, load and search-result paths alike — the mechanism #137 introduced, and the reason `stock_news_sentiments` is excluded today. All 19 withdrawn endpoints now carry `deprecated=True`, so semantic search really does stop offering them
  - `@deprecated` and `@removed` now stamp `__fmp_deprecated__` on the wrapper, making deprecation detectable programmatically instead of by a hand-maintained list. `get_stock_news_sentiments` open-coded its warning with a function-local `import warnings`; it now uses the decorator like its neighbours
- **Fifteen further endpoints whose live replacement the library already shipped** - these were *not* repointed, and the reason is the point. Each declares a dead path whose working equivalent is already a separate, live endpoint in this package, so repointing would have created 15 duplicate `(path, params)` pairs — exactly the duplication #130 and #136 spent two PRs removing. Nine would also have failed validation against their own `response_model`, turning a clean 404 into a runtime parse error. Each method now warns, returns empty without issuing the request, and names the method that already works:

  | Deprecated method | Already shipped as | How it differs |
  |---|---|---|
  | `alternative.get_crypto_quotes` | `batch.get_crypto_quotes` | batch payload is `symbol`/`price`/`change`/`volume` only |
  | `alternative.get_forex_quotes` | `batch.get_forex_quotes` | same narrowing |
  | `alternative.get_commodities_quotes` | `batch.get_commodity_quotes` | same narrowing |
  | `company.get_historical_share_float` | `company.get_share_float` | current snapshot, not a history |
  | `fundamental.get_historical_rating` | `intelligence.get_ratings_historical` | `overallScore` + per-metric scores, not `ratingScore` |
  | `intelligence.get_senate_trading_rss` | `intelligence.get_senate_latest` | same rows |
  | `investment.get_etf_holding_dates` | `investment.get_mutual_fund_dates` | `date`/`year`/`quarter` record, not a bare date |
  | `investment.get_mutual_fund_holdings` | `investment.get_etf_holdings` | `securityCusip`/`sharesNumber`; no `cik`/`reportedDate` |
  | `investment.get_etf_holder` | `investment.get_fund_disclosure_holders_latest` | holder-level, not asset-level |
  | `investment.get_mutual_fund_holder` | same | **declared the same dead path as `get_etf_holder`** — the two were duplicates of each other |
  | `investment.get_mutual_fund_by_name` | *(none)* | a dozen path variants probed, all 404 |
  | `market.get_tradable_list` | *(none)* | `get_stock_list`/`get_etf_list`/`get_actively_trading_list` are partial — "tradable" is a different universe |
  | `market.get_pre_post_market` | *(none signature-compatible)* | the market-wide call is gone; extended-hours data is per symbol via `company.get_aftermarket_quote` |
  | `company.HISTORICAL_EMPLOYEE_COUNT` | `company.get_employee_count` | orphaned declaration — no client method, no mapping |
  | `company.STOCK_SCREENER` | `market.get_company_screener` | orphaned declaration — no client method, no mapping |
- **Duplicate MCP tool keys, one per `(client, method)` pair from 3.0** (#136) - three company methods were advertised under two tool keys each, so an MCP client saw two tools that did exactly the same thing and an LLM had to pick between them with nothing to distinguish them. The plural key is canonical; the singular one is deprecated and **removed in 3.0**:

  | Deprecated key | Replacement | Method |
  |---|---|---|
  | `company.executives` | `company.key_executives` | `get_executives` |
  | `company.historical_price` | `company.historical_prices` | `get_historical_prices` |
  | `company.intraday_price` | `company.intraday_prices` | `get_intraday_prices` |

  - The deprecated keys still resolve through 2.6, in both the bare (`historical_price`) and fully qualified (`company.historical_price`) form. Resolving one emits a `DeprecationWarning` naming the replacement and the 3.0 removal — raised from `fmp_data.mcp.tool_loader._warn_if_deprecated`, on the single path (`_resolve_tool_spec`) that both forms funnel through
  - The same message is also logged at `WARNING` on the `fmp_data.mcp.tool_loader` logger, because the `DeprecationWarning` alone does not reach the people who most need it. `stacklevel=4` attributes the warning to whoever called `register_from_manifest`, and on the dominant path — `python -m fmp_data.mcp`, `fmp-mcp serve`, Claude Desktop — that caller is `fmp_data.mcp.server.create_app`, a library module. Python's default filter chain (`default::DeprecationWarning:__main__`, then `ignore::DeprecationWarning`) discards any `DeprecationWarning` not attributed to `__main__`, so without the log line a running server announced the migration to nobody. The log line lands on the server's stderr, where MCP hosts collect it
  - The pairs are declared in `fmp_data.mcp.tools_manifest.DEPRECATED_TOOLS` as `{deprecated spec: replacement spec}`
  - **They are removed from `DEFAULT_TOOLS` now** (159 → 156), so a default server already advertises exactly one tool per method. This half is **breaking for default-server users in a minor release**, and deliberately so: advertising two identical tools per method is the defect #136 reports, and it cannot be fixed while both remain advertised. If you run the default server and something you control names the tools `executives`, `historical_price` or `intraday_price` — a saved prompt, a hard-coded tool call — switch it to `key_executives`, `historical_prices` or `intraday_prices`. These users cannot be warned in code: they never name the key, so no resolution happens and there is no call path on which a warning could fire. To keep the old names for now, list them explicitly in a manifest — they still resolve, with a warning, until 3.0
  - Manifests naming a deprecated key explicitly are unaffected and keep working with a warning until 3.0
  - Catalog is unchanged at this step: both names remain loadable via an explicit manifest until 3.0, when the catalog drops 223 → 220
  - `fmp-mcp validate` now reports every deprecated spec in a manifest alongside its replacement and still exits 0 — deprecated is valid, just not future-proof — and `fmp-mcp list` marks deprecated rows in all four output formats (`list`, `tree`, `table`, and a `deprecated` field in `--format json`)
  - The shipped example manifests no longer name deprecated keys. `trading_manifest.py` listed `historical_price` *and* `historical_prices`, `intraday_price` *and* `intraday_prices`; `research_manifest.py` listed `executives` *and* `key_executives`; `minimal_manifest.py` listed `historical_price`. Registering the first two emitted deprecation warnings and registered the same method twice — the examples `docs/mcp/configurations.md` tells users to copy demonstrated the exact problem #136 exists to fix. A guard test now fails if any example manifest names a deprecated key, lists one method twice, or contains an entry that does not resolve
  - `discovery.get_recommended_tools()` recommended `company.historical_price`; it now recommends `company.historical_prices`
- **Bare-key resolution for tool keys claimed by two clients** (#126) - `register_from_manifest` accepts a bare tool key (`profile`) as well as the fully qualified spec (`company.profile`), resolving it through `build_key_to_spec`, which indexes the whole discovery catalogue rather than `DEFAULT_TOOLS`. `crypto_quotes` and `forex_quotes` are each claimed by two clients (`alternative` and `batch`), so the bare form failed with a bare `RuntimeError: Tool key 'crypto_quotes' is ambiguous` that named neither candidate.
  - Both tools are legitimate and distinct, so neither is removed and neither is renamed. What is now stated is the guarantee: **a bare tool key resolves only when exactly one client claims it.** For the two ambiguous keys, write `alternative.crypto_quotes` / `batch.crypto_quotes` (likewise for `forex_quotes`)
  - The error now names every candidate and the exact form to use instead, so the fix is readable off the message without consulting the catalogue
  - The guard test no longer carries a shrinking allowlist. It asserts the set of ambiguous bare keys is exactly this documented pair — a new, undocumented collision still fails, and so does silently *resolving* one of the two
  - **`examples/mcp/configurations/crypto_manifest.py` was broken by this and nobody noticed:** it listed bare `crypto_quotes` and `forex_quotes`, so the shipped crypto example raised `RuntimeError` at registration. Both are now written `alternative.crypto_quotes` / `alternative.forex_quotes`, and the new example-manifest guard fails on any entry that does not resolve
  - `fmp-mcp validate` warns when a manifest names an ambiguous bare key, listing the candidates, instead of mislabelling it an unknown tool. It also resolves bare keys before judging them, so a valid bare-key manifest is no longer reported as full of unknown tools

### Removed

- **`institutional.cik_mapper_by_name` MCP tool and its endpoint** (#130) - `CIK_MAPPER_BY_NAME` declared the same `cik-list` path and the same `page`/`limit` parameters as `CIK_MAPPER`, and no `name` parameter, so the tool generated from it had no way to express the search it claimed. LangChain tools call `client.request(endpoint, **kwargs)` directly, bypassing the client wrapper where the filtering actually happens, which made it a byte-for-byte duplicate of `cik_mappings`.
  - Confirmed against the live `stable` API on 2026-08-07: `GET /stable/cik-list` with `name=Apple`, with `company=Apple`, and unfiltered returned byte-identical unfiltered pages. There is no server-side name filter to model
  - Removed: the `cik_mapper_by_name` entry in `INSTITUTIONAL_ENDPOINTS_SEMANTICS`, the `search_cik_by_name` entry in `INSTITUTIONAL_ENDPOINT_MAP`, and the now-unreferenced `CIK_MAPPER_BY_NAME` endpoint definition. Catalog 224 → 223; institutional endpoints 25 → 24
  - **`InstitutionalClient.search_cik_by_name` and its async twin are unchanged and keep working.** They are the genuine interface: they call `CIK_MAPPER` with `limit=10000` and filter locally, which the probe confirms is the only option. This removal takes away a dead tool, not a capability
  - It is removed outright rather than deprecated because it is not a second name for a working tool — it is a tool that cannot perform the operation it advertises. There is nothing for a deprecation cycle to migrate callers *from*
  - Not addressed here: teaching the LangChain tool layer to dispatch through client methods rather than `client.request`, so wrappers carrying real logic become reachable. That is the general form of the problem and needs its own design pass (addressed in #172)

### Fixed

- **CI: shared mergeable.jq + primary rate-limit retry** (#223). check-pr-mergeable loads extraction from `mergeable.jq` (single fixture for production and mocks); primary REST rate-limit 403 retries like secondary; mock matrix exercises the production jq path end-to-end.
- **CI: harden check-pr-mergeable mock matrix** (#215). Matrix asserts `GITHUB_OUTPUT` / step summary on success and key failure paths; adds `true\tunknown` exhausted, `true\tdirty` short-circuit, invalid `SLEEP_SECONDS` / `API_MAX_RETRIES`, unknown-shape API errors; locks expected PASS count so silent case drops fail CI.
- **CI: retry transient gh api failures in check-pr-mergeable** (#217). Bounded `api-max-retries` (default 3) with linear backoff for HTTP 408/425/429/5xx and transport blips; permanent 401/403/404/410/422 fail immediately. Secondary rate-limit 403 is retried. Does not change the `mergeable=true` success criteria.
- **CI: explicit mergeable extraction (no `@tsv` null→empty)** (#216). `check-pr-mergeable` now extracts REST `.mergeable` with `jq tostring` so JSON `null` is the literal token `null` in logs, outputs, and mocks (bare `@tsv` encoded null as an empty field). Fail-closed contract unchanged: green only when `mergeable=true`.
- **CI: document Guard base-pin lag for mergeability contract** (#218). Guard-Main-Origin overlays `.github/actions/check-pr-mergeable` from `origin/<base>` when present; contract tightenings therefore apply to Guard only after they land on the PR base (usually `main`), while Release-PR on `dev` picks them up immediately. Documented in `docs/contributing/releasing.md` and `action.yml` so operators can explain Guard vs Release-PR mismatches after a `dev`-only contract change.
- **CI: mergeability green requires `mergeable=true`** (#213). `.github/actions/check-pr-mergeable` previously treated any non-`dirty` / non-`unknown` `mergeable_state` with `mergeable != false` as success, so empty/`null` (JSON null via `jq @tsv`) could paint green without proof the PR is mergeable. Exit 0 now requires `mergeable=true`; empty/null with a resolved state fails closed. Contract comments in `action.yml` document the choice.
- **CI: run check-pr-mergeable mock matrix in Test-Matrix** (#212). New lightweight `actions-shell` job runs `bash .github/actions/check-pr-mergeable/test-check.sh` and `shellcheck` on `.github/actions/**/*.sh` on every PR; `Test-MatrixExpected` requires it. Keeps the local fail-closed matrix from #211 from rotting out of CI.
- **CI: shared fail-closed PR mergeability check** (#210). Guard-Main-Origin and Release-PR both used the same REST `mergeable` / `mergeable_state` retry contract (added for #202 / #207) as two independent copies. That logic now lives in `.github/actions/check-pr-mergeable` (composite action + `check.sh`); both workflows call it so the fail-closed semantics cannot drift. Guard checks out the PR **head** (not the merge ref) so a CONFLICTING PR still reaches the clear red X, then overlays the action from the PR base when present (hotfix-safe; head copy only during bootstrap). Optional `max-attempts` / `sleep-seconds` / `conflict-guidance` inputs; classified `gh api` failures; step summary + outputs for operators.
- **CI: automation PRs trigger normal CI; release PR health re-checked; sync hardened** (#206, #207, #208).
  - **#206 — `secrets.GH_TOKEN` (PAT) for Release-PR and Sync-Main-to-Dev.** PRs opened with the automatic `GITHUB_TOKEN` do not re-fire `pull_request` workflows (Test-Matrix, Guard-Main-Origin missing until a human push). Both workflows now prefer `secrets.GH_TOKEN` for `gh pr create` / automation pushes, with a documented fallback to `GITHUB_TOKEN` and a job warning when the PAT is absent. This is independent of the Actions “read/write” permission toggle.
  - **#207 — Release-PR re-validates an already-open `dev → main` PR on every push.** The old “already open → exit 0” path skipped ancestry and mergeability checks, so a release PR that went CONFLICTING after a squash stayed green on every later `dev` push. Ancestry plus REST `mergeable` / `mergeable_state` (with retries) now fail the job on `dirty`, `mergeable=false`, or still-`unknown` after retries — same fail-closed contract as Guard-Main-Origin (GraphQL `mergeStateStatus` is uppercase and was easy to mis-match). Deduplicated into the shared action in #210.
  - **#208 — Sync-Main-to-Dev concurrency and WIP.** `cancel-in-progress` is false so a second `main` push does not cancel an in-flight sync; force-push refuses to drop non-`github-actions` commits on `sync/main-to-dev`; merge conflicts open or update a tracking GitHub Issue with recovery steps (in addition to the step summary).


- **`fmp_data.__version__` reported `0.0.0` in every published release** - `[tool.hatch.version] source = "vcs"` sets the *distribution* version, but without the matching build hook `fmp_data/_version.py` was never generated, so the import in `fmp_data/__init__.py` always fell back to the `"0.0.0"` literal. Confirmed against PyPI 2.5.0: dist metadata `2.5.0`, `fmp_data.__version__` `0.0.0`. Adding `[tool.hatch.build.hooks.vcs] version-file = "fmp_data/_version.py"` makes the two agree — verified by building a wheel and installing it. `__version__` is exported in `__all__`, so this is public API, and it is what users paste into bug reports. Side effect: two 3.0 tripwires in the suite are written `if __version__ != "0.0.0": assert major < 3` and had therefore never actually run; they are live now.
- **LangChain request-fallback is announced, not silent** (#194) - when `EndpointVectorStore.create_tool` cannot bind a client method and falls back to `client.request`, it now logs the reason at tool-creation time: DEBUG when the store's client has no such sub-client (normal for a bare `BaseClient` / test double; a warning per catalogue endpoint would bury real issues), WARNING when the sub-client is present but the named method is missing, and WARNING naming the uncovered required params (via `uncovered_required_params`) when the method shape is incompatible with the wire fields.
- **`bindable_params` drops `cls`, not just `self`** (#195) - a bound classmethod hides its receiver, but the catalogue guard and unit tests pass the underlying function, where `cls` read as a required parameter no wire field could fill.
- **Required positional-only parameters block method dispatch** (#195) - `bindable_params` lists parameters fillable *by name*, and dispatch is `method(**mapped)`. A required `POSITIONAL_ONLY` parameter was merely absent from that map, which read as "nothing required is missing": the gate reported compatible and the call then raised `TypeError: missing 1 required positional argument`. `uncovered_required_params` now counts them as uncovered so such a method falls back to `client.request`. No catalog method has one today.
- **`map_tool_kwargs_to_method` last-wins for aliased names is documented** (#195) - when multiple input keys resolve to the same method parameter (e.g. `from` and `from_date` both mapping onto `from_date`), later keys overwrite earlier ones. Well-formed tool schemas do not emit both; the docstring and unit tests pin the direct-caller behaviour. `**kwargs` remains excluded from bindable params (unmapped wire fields are dropped, not passed through).
- **Async Form 13F methods no longer swallow non-API exceptions** (#193) - `AsyncInstitutionalClient.get_form_13f_by_quarter` and `get_form_13f_dates` caught bare `Exception`, so programming bugs (`AttributeError`, `TypeError`, …) were logged as "no 13F data" and returned `[]`. They now catch only `(FMPError, ValidationError)`, matching the sync client. Empty-on-API-error remains the intentional Python (and LangChain tool) contract; only the over-broad catch is fixed.
- **`bindable_params` unifies four disagreeing parameter filters** (#188) - the "which parameters of this method can receive a value" filter existed in **four** hand-written copies — three in `vector_store`, one more in the catalogue guard — and they disagreed: `partition_params_for_method` filtered only on the name `self`, while the dispatch gate also filtered on parameter *kind*. A method with `**kwargs` therefore looked like it required a parameter named `kwargs` to one copy and not to the other. `bindable_params()` is now the single definition, and the fixed behaviour is the stricter one (`*args`/`**kwargs` excluded).

- **LangChain tools dispatch through the client method, not bare `client.request`** (#172) - tools built by `EndpointVectorStore.create_tool` used to call `client.request(endpoint, **kwargs)`, skipping every behaviour the matching client method adds on top of its endpoint: default date windows, one-of constraints, pagination defaults, post-processing. #169 made `from`/`to` mandatory on the SEC filings-search endpoints because the live API requires them; that is safe for direct client callers only because `SECClient.search_by_symbol` (and siblings) default the window to the last 30 days. An LLM tool that only had a symbol raised a local `ValidationError` instead. Dispatch now resolves `client.<semantics.client_name>.<semantics.method_name>` — the same path MCP already uses — and maps wire/tool kwargs onto the method signature (`from`→`from_date`/`start_date`, `periodLength`→`period_length`, `sicCode`→`sic_code`, …). Parameters the method defaults become optional in the generated tool schema, so an LLM may omit them. Endpoint params that do not map onto any method parameter are omitted from the tool schema under method dispatch (e.g. revenue `structure`, employee `limit`), since unmapped kwargs are dropped at invoke. `ValueError` from method-level checks (e.g. industry classification requiring at least one of `symbol`/`cik`/`sicCode`) is returned as a structured `validation_error`. When the store holds a bare `BaseClient` or a test double without sub-clients, or when a method signature cannot be fully mapped from endpoint params (e.g. Form 13F wire `year`/`quarter` vs method `report_date`), dispatch falls back to `client.request` and the pre-#172 schema.
- **Claude Code Review no longer fails every PR when its OAuth token is missing or expired** (#184) - the job treated a missing/invalid `CLAUDE_CODE_OAUTH_TOKEN` as a hard failure (`is_error: true`, 0 cost, no review posted), so every PR targeting `dev` carried a red non-required check. The job now skips when the secret is empty, and the review step uses `continue-on-error: true` so an expired token cannot fail the workflow either. Review stays advisory; required checks remain in `ci.yml`.
- **A cache TTL override naming no endpoint now warns instead of silently doing nothing** (#166, follow-up) - `BaseClient._get_cache_ttl` reads `CacheConfig.ttl_overrides` with a plain `.get(endpoint_name, default)`, so a key matching no endpoint was not an error, not a warning and not visible. `CacheConfig(ttl_overrides={"serch-name": 60})` was accepted in full and the override simply never applied; the only symptom was request volume quietly disagreeing with the configuration. A typo, a name copied from a newer version, or a name the library has since changed all failed the same silent way.
  - The warning names each unmatched key and, when one is close enough, the endpoint it nearly matched: `'serch-name' (closest endpoint: 'search-name')`.
  - **Warned, not raised, and the entry is kept.** Configuration is routinely carried across versions; a stale override is not a reason to stop a client being constructed, and deleting the entry would add a second silent behaviour on top of the one being fixed.
  - The endpoint catalogue is walked lazily and **only when `ttl_overrides` is non-empty**, so the check costs nothing for the configuration almost everyone has. It cannot be walked at import time — this module is reached from `fmp_data/__init__.py`, so importing the catalogue to define a config model would invert the dependency.
  - An empty catalogue (every endpoint module failed to import) is treated as "could not tell" rather than "everything is wrong", so a broken environment does not warn about every key.
  - Found while establishing the blast radius of #166, which renames `market.search-name`. That rename was blocked partly because it would silently orphan a user's TTL override; with this in place the loss is announced rather than silent, which is what made the rename shippable **in this same release** — see the `search-name` → `search_name` entry under **Changed**.
- **MCP `COLUMNS=80` fold guard skipped when the `rich` extra is absent** (#180) - without `rich`, `print_tools_table` falls through to the plain table path, so the guard was failing for the wrong reason in the no-extras CI shape.
- **`DeprecationWarning`s from deprecated `async` client methods were blamed on `asyncio`, not on your code** (#177) - `@deprecated`'s async branch called `warnings.warn(..., stacklevel=2)` from inside the coroutine body. A coroutine body does not run in its caller's stack — it runs wherever the event loop resumed it — so `stacklevel=2` resolved to a frame in CPython's event loop. Measured against the same call site: the sync path reported `probe.py:85`, the async path `.../asyncio/events.py:88`. A user could not locate the line they had to change, which is the entire purpose of the warning, and `filterwarnings(..., module="my_package")` rules never matched, so the warning could be neither silenced nor escalated from user code.
  - **The location is now looked up rather than counted.** The wrapper walks outward from the warning site to the first frame that is neither in `fmp_data.helpers` nor in known event-loop packages (`asyncio`, `uvloop`), and reports it with `warnings.warn_explicit`. That is correct for every shape: `await client.old()` blames the awaiting line; `asyncio.run(client.old())` blames the `asyncio.run(...)` line, the only user frame left on the stack; `asyncio.gather(client.old(), ...)` blames the user frame still driving the loop, since the frame that built the call is suspended and its line is genuinely unrecoverable. The caller's module and `__warningregistry__` are passed through too, so `module=` filters match and the `"default"` action still dedups per location.
  - **The decorator's public shape is unchanged.** In particular the async branch is still an `async def`, so `inspect.iscoroutinefunction` stays true — warning eagerly from a sync wrapper that returns a coroutine would have fixed the attribution by reintroducing exactly the lie #170 removed.
  - **The sync path was already correct and now shares the same mechanism**, so the two cannot drift apart again. New guards assert the recorded `filename` *is the caller's file* for both paths, and that a `filterwarnings(module=...)` rule naming the caller fires — asserting only that a warning was emitted is what let this survive four releases of async tests.
  - **Async generator functions get an async generator wrapper** (`@deprecated` and `@removed` alike). `inspect.iscoroutinefunction` is `False` for `async def ... yield`, so both decorators fell through to the plain `def` wrapper: `inspect.isasyncgenfunction` on the result was `False`, and the warning — or, for `@removed`, the `RemovedEndpointError` — fired when the generator object was *created* rather than when it was iterated. That is #170's defect in the third shape. There are no async generators in `fmp_data` today, so nothing changes for callers; the wrapper and its guards exist so the next one is not born broken.
- **`fmp-mcp generate` shipped three tools that answer empty on every call** (#164) - two mechanisms record that a tool is retired, and `generate` filtered on one. `EndpointSemantics.deprecated` (#137) hides a dead endpoint from the LangChain vector store; `WITHDRAWN_TOOLS` (#169) hides it from MCP. They describe the same fact, but three specs carried the flag and were absent from the table — `intelligence.earnings_confirmed`, `intelligence.earnings_surprises` and `intelligence.stock_news_sentiments` — so every generated manifest advertised them. `stock_news_sentiments` even describes itself to an LLM as "DEPRECATED and non-functional ... always returns an empty list". An LLM handed that tool gets an empty *success*, indistinguishable from "no data matched", which is #137's original complaint.
  - **Decision: the three are withdrawn, and are now in `WITHDRAWN_TOOLS` with no successor.** All three paths (`earning-calendar-confirmed`, `earnings-surprises`, `stock-news-sentiments-rss-feed`) were probed against the live `stable` API and 404. This is not a judgement call about where to file them — the table means "FMP no longer serves this endpoint", which is literally true of all three, so this completes a table that was three entries short of reality rather than stretching it to fit. FMP publishes nothing equivalent for any of them.
  - **`WITHDRAWN_TOOLS` goes 19 → 22; a generated catalog manifest goes 201 → 198.** `DEFAULT_TOOLS` is unchanged at 137 — none of the three was ever a default — so **a default server is unaffected**.
  - **Resolution is untouched.** All three still resolve, so an explicit manifest naming one keeps working until 3.0, and `fmp-mcp validate` reports it as withdrawn while still exiting 0. This is not a removal.
  - **`DEPRECATED_TOOLS` deliberately does not participate**, which is what #137's note was protecting. It records a *different* fact — a second name for a method that still works — and its warning promises the replacement is a drop-in. It keeps its 3 alias entries and stays disjoint from both the flag and the withdrawal table. Populating a table is not merging two mechanisms.
  - **The agreement is now enforced, not remembered.** `test_withdrawn_tools_match_the_semantics_flag` asserts `set(WITHDRAWN_TOOLS) == {specs flagged deprecated}` exactly, deriving the flagged set by walking the mapping tables, with a floor (`>= 20` flagged) so a broken walk cannot pass it against an empty set. A future withdrawal can no longer fix the LangChain surface and forget the MCP one, or the reverse.
- **Duplicate tool names went undetected under `FMP_MCP_TOOL_NAME_STYLE=spec`** (#162) - `_validate_tool_names` opened with `if name_style != "key": return`, so the duplicate check existed only under the default style. A manifest naming one tool twice — `["profile", "company.profile"]`, both resolving to `company.profile` — registered it twice under `spec`, and whether the MCP server object then rejected the repeated name or silently kept the last registration is server-dependent. Either outcome is bad and neither was announced. The style that exists to *fix* name problems was the only one with no name checking.
  - The early return conflated two different things. A **collision** is two *different* specs wanting one advertised name (`alternative.crypto_quotes` and `batch.crypto_quotes` both advertise as `crypto_quotes`); it is genuinely impossible under `spec`, and skipping it there is correct. A **duplicate** is one spec listed twice, reachable because a manifest accepts both the bare key and the qualified form for the same tool; no name style separates it. The check now computes advertised names under the effective style and splits the two, so `key` behaves exactly as before while `spec` newly catches duplicates and still permits collisions.
  - The error message branches. Telling someone already running `FMP_MCP_TOOL_NAME_STYLE=spec` to set `FMP_MCP_TOOL_NAME_STYLE=spec` is useless advice; a duplicate is now reported as "the same tool is listed more than once … remove the duplicates", and only a collision suggests the style switch.
  - The grouping (`advertised_names`) and the split (`split_name_clashes`) live in `tool_loader` and are used by the loader **and** by `fmp-mcp validate`'s clash report, which had its own copy. A guard asserts the two agree for every case in the manifest table under both styles. Note the direction of this one relative to #149: that was `validate` blessing what the loader refuses, this is the loader accepting what `validate` warns about — same class of divergence, opposite sign.
- **`@removed` did not preserve coroutine-ness, unlike its sibling `@deprecated`** (#170) - `removed()` in `fmp_data/helpers.py` always returned a plain synchronous wrapper, regardless of what it decorated. `deprecated()` in the same file already branched on `inspect.iscoroutinefunction(func)` to return an `async def` wrapper so introspection stays honest; `removed()` had no such branch. Three `async def` methods on `AsyncMarketIntelligenceClient` carry `@removed` (`get_historical_social_sentiment`, `get_trending_social_sentiment`, `get_social_sentiment_changes`), so after decoration none of them were coroutine functions.
  - **Confirmed behaviour change, not merely theoretical:** a `RemovedEndpointError` from one of these methods used to raise while the *caller's argument list* was still being evaluated — before an `await` ever happened — rather than when the coroutine was awaited. Inside `asyncio.gather(removed_endpoint(), other())`, that meant `other()`'s coroutine object was constructed but its body never ran at all, since the exception aborted evaluation before `gather()` was even called. After this fix the exception surfaces at `await` time like every other async client method, and siblings passed alongside it in the same `gather()` call run normally.
  - `removed()` now mirrors `deprecated()`'s branch exactly: an `async def` wrapper for a coroutine function, the existing plain wrapper otherwise. `inspect.iscoroutinefunction()` on a `@removed`-decorated coroutine function is now `True` directly, with no `inspect.unwrap()` needed to see it.
  - `tests/unit/test_deprecated_methods_warn.py`'s async sweep (added in #169) used `inspect.iscoroutinefunction(inspect.unwrap(method))` to classify sync vs. async — which, thanks to `functools.wraps` setting `__wrapped__` to the original coroutine function, already unwrapped to the right answer despite the bug, so the sweep was not actually blind to these three methods as originally suspected while investigating this issue. The `unwrap()` is removed now that the wrapper is honest on its own, so a future decorator that stops preserving coroutine-ness fails this sweep directly instead of being silently compensated for. The sweep also gains a floor asserting a non-zero count of `@removed` async methods actually reached, so a regression that drops these three back into the sync bucket (where they would still incidentally pass, since a sync raise still satisfies that test's contract) is caught rather than silently tolerated.
  - New guards in `tests/unit/test_helpers.py`: a parameterised check that both `@deprecated` and `@removed` preserve `inspect.iscoroutinefunction` across sync and async inputs (four combinations, floored so the parameterisation cannot silently shrink), a direct test that a `@removed` coroutine only raises on `await` and not on call, and a behavioural test asserting a sibling coroutine in the same `asyncio.gather()` call actually starts. `TestRemovedDecorator` also gains the basic sync coverage `@removed` never had (raises with/without a reason, preserves `__name__`/`__doc__`, never reaches the decorated body). Mutation-tested by disabling the new branch: four tests across both files fail, including the pre-existing `checked > 25` floor in the async sweep (23 methods reached instead of 26)
- **Endpoint signatures that no request could satisfy** - five declarations were measured against the live `stable` API and could never have worked as written.
  - `alternative.crypto_intraday` and `alternative.commodity_intraday` declared `historical-chart/{interval}/{symbol}`, modelling `symbol` as a path segment where the API wants a query parameter, so every call 404'd. Both now match the already-correct `alternative.forex_intraday` shape. Verified live: `historical-chart/5min?symbol=BTCUSD` returns 2826 rows, `?symbol=GCUSD` returns 2416
  - `investment.mutual_fund_holdings` declared `symbol` as a **path** parameter while its path carries no `{symbol}` placeholder. `build_url` substitutes only placeholders and `get_query_params` sends only query params, so the symbol a caller passed was substituted nowhere and sent nowhere — dropped without a word. It is now a query parameter
  - `sec.sec_filings_search_symbol`, `_cik` and `_form_type` declared `from`/`to` optional; the API answers `400 Invalid or missing query parameter - from` without them. Both are now mandatory. **No client method changed** — all three already defaulted the window to the last 30 days, so they could never hit the 400 and the declaration was simply lying about the contract
  - `sec.industry_classification_search` requires at least one of `cik`/`sicCode`/`symbol` but each is individually optional, which `mandatory_params` cannot express. `SECClient.search_industry_classification` already enforced it; the endpoint description now records the constraint instead of leaving it undocumented
  - `market.cik_search` sent the right parameter name all along — it carries `alias="cik"` and the wire key is `param.alias or param.name`. The real defect was the **type**: `ParamType.STRING` sent `320193` where FMP matches a fixed-width 10-digit CIK. It is now `ParamType.CIK`, matching `sec.sec_filings_search_cik`. Because the parameter is named `query`, the description and both client docstrings now state that a CIK is required and a company name returns 400. The parameter is deliberately **not** renamed: that would change the public `search_by_cik` signature and the shared `BaseSearchArg` schema
- **A new guard for path templates that no unit test could see** - `PATH`-located parameters and `{placeholder}`s in a path must correspond one-to-one, asserted across all 275 declarations without an API key. Each direction fails silently in its own way: a placeholder with no `PATH` param leaves a literal `{symbol}` in the URL and 404s, and a `PATH` param absent from the template is sent nowhere at all. The pre-existing e2e check only caught the first, and would have missed both bugs above — `crypto_intraday` did declare `symbol`, just in the wrong location.
- **`EndpointParam.required` contradicted the list its parameter was declared in** (#144) - 14 parameters sat in an endpoint's `optional_params` while declaring `required=True`. `Endpoint.validate_params` skips a `None` value for any param not in `mandatory_params` *before* `validate_value` consults `required`, so omitting one always worked — but `validate_value` is public, and calling it directly with `None` raised "Missing required parameter" for a parameter the endpoint treats as optional. The flags now follow list membership, which is what every consumer reads, and a guard keeps the two from drifting apart. Confirmed against the live API that the affected parameters really are optional: `news/stock` returns rows with and without `symbol`.
- **`docs/api/endpoints.md` documented endpoints under names and paths the code does not use** (#146) - `docs/mcp/tools.md` has been guarded by `test_docs_tools_sync.py` for some time, which is why the catalog change in #130 could not leave a stale number behind; `endpoints.md` and `docs/mcp/configurations.md` had no equivalent, and both had drifted. The document is now asserted against the code row for row, not just in aggregate.
  - **Counts, in both of the two places the document states them.** The table of contents claimed 47 Market Intelligence endpoints while the code and the document's own table had 46 — and the section's own `### N endpoints` heading is a third, independent copy of that number, so correcting only the TOC would have left the document contradicting itself. All three are now checked against the real `Endpoint` count
  - **Row-set equality, because a rename miscounts as zero.** Three rows named endpoints that did not exist: `search_name` (the endpoint was `search-name` — #166 has since renamed the code to match, see **Changed**), `crypto_symbol_news` and `forex_symbol_news` (they are `crypto_news_symbol` and `forex_news_symbol`). Every count in those two sections matched, so nothing could have noticed
  - **Paths are compared too**, and this is the one a reader could act on: four rows documented the bare `/stable/historical-price-eod`, the exact path `CLAUDE.md` forbids because it needs a variant suffix. The code correctly requests `historical-price-eod/full`, so anyone following the document rather than the library got a URL the library never sends. `search-name`'s path was documented as `/stable/search_name`, which does not resolve either
  - **The code is the authority, so every correction landed in the document.** `Endpoint.name` is not cosmetic — it is the cache-key prefix and the argument to `_get_cache_ttl` — so renaming `search-name` to match its documentation would have quietly changed cache behaviour. That naming oddity was filed as #166 and is resolved in this release, deliberately and with a migration note, rather than as a drive-by documentation fix
  - **The code ⊆ doc direction is checked too.** Every other assertion iterates over the document's sections, so a brand-new client documented nowhere has no section to iterate over and every guard stays green — the exact drift this issue is about. A separate check requires each client with an `endpoints` module to have a section. (A *renamed* section was already caught: its label stops resolving to a module.)
  - Duplicate rows are reported rather than collapsed. Row-set equality alone cannot see a row listed twice, which the row-*count* check it replaced would have caught
  - Every `examples/...` path `configurations.md` names must exist — the check that would have caught it pointing at `examples/mcp_configurations/` when the real directory is `examples/mcp/configurations/`. Paths are matched bare, not only inside backticks: the three concrete manifests a reader copy-pastes live inside fenced `export FMP_MCP_MANIFEST=...` and `create_app(...)` snippets and carry no backticks, so a backtick-only match validated the directory and none of the files
  - Modules that fall out of the package walk are recorded and named in any failure message, so a mismatch is never reported from a partial scan as though it were a complete one. This needs two mechanisms, not one: `walk_packages` re-raises a non-`ImportError` from the `for` header itself, outside any `try` around the import, so it also takes an `onerror` callback
  - Mutation-tested: a wrong TOC count, a wrong section heading, a renamed row, a changed path, a deleted row, a duplicated row and an undocumented client each fail, naming the specific mismatch
- **Deprecated endpoints are no longer selectable through the LangChain vector store** (#137) - `intelligence.stock_news_sentiments`, `earnings_confirmed` and `earnings_surprises` return `[]` without calling upstream, but stayed indexed, so a semantic query could pick one and the LLM got an empty *success* — indistinguishable from "no data matched your query". `EndpointSemantics` gains `deprecated: bool = False`; the three are marked, and `EndpointVectorStore` filters on it.
  - Filtering happens **both** at index time (`add_endpoint`, `add_endpoints`) and at selection time (`search`, `get_tools`). Index-time alone would leave anyone with a store persisted by an earlier release exactly where this issue found them, since the deprecated endpoints are already baked into that index
  - **`search` widens its fetch rather than shrinking its answer.** On exactly that stale index, a deprecated hit occupies a slot in the top-`k` window, so filtering after the fetch would return two live endpoints for `k=3` and say nothing about it — under-recall in place of a dead endpoint. `search` now refetches with a doubled window while filtered-out entries are still displacing live ones (three rounds, stopping early once `k` results are live or the index is exhausted) and truncates to `k`. Results are still capped at `k`; unknown endpoint names in a stale index are recovered from the same way. Hits below `threshold` do not trigger a refetch — that is a genuine relevance cut, and widening would only surface worse matches
  - `add_endpoints` returns the number of endpoints it actually indexed. `create_new_store` logged `len(endpoint_names)`, the count it *offered*, which overstated the store by however many the filter had just dropped (215 offered, 212 indexed)
  - **The entries are not deleted, and the MCP catalog does not move** — still 223 tools, with all three keys resolvable through an explicit manifest. MCP reads the `*_ENDPOINTS_SEMANTICS` tables directly and never consults the vector store, so it is unaffected. Deleting the keys outright would remove public tool keys with no deprecation window
  - `add_endpoints` counts and logs deprecated exclusions separately from `skipped_endpoints`: being deprecated is a deliberate exclusion at `INFO`, not a defect worth a `WARNING`
  - **This is a different mechanism from `fmp_data.mcp.tools_manifest.DEPRECATED_TOOLS`** (#136), and the two must not be merged. That table maps a duplicate tool *name* onto the canonical name of a method that still works — resolve one and you get live data plus a rename warning. This flag says the endpoint itself returns nothing, whatever name you reach it by, so the fix is to stop advertising it rather than to rename it. The distinction is written into both `EndpointSemantics.deprecated` and `DEPRECATED_TOOLS`, and a test asserts the two sets stay disjoint. That test lives in `tests/unit/test_mcp.py`, the only file the `mcp-server` CI job runs: it needs the `mcp` extra, and beside the other #137 tests in `tests/unit/lc/` — skipped without `langchain`, which no `mcp` job installs — it would never have executed anywhere. Which endpoints carry the flag is likewise pinned in a top-level `tests/unit/test_deprecated_endpoint_flags.py`, so the accidental-deprecation guard runs in the default no-extras matrix rather than only in the `langchain` job
  - **`EndpointVectorStore._is_deprecated` typed its argument `Any` and read the flag with `getattr(info.semantics, "deprecated", False)`** (#159) - renaming or dropping `EndpointSemantics.deprecated` degraded every filtering call site to "nothing is deprecated" silently, with the suite green except for the two tests pinning the field and exercising it end to end. The parameter is now typed `EndpointInfo`, and the flag is read as `info.semantics.deprecated`, so a rename is a `mypy` `attr-defined` error and, absent type-checking, an `AttributeError` rather than a quiet no-op. Where that `AttributeError` surfaces depends on the path: on the `search`/`get_tools` filters it propagates to the caller, while on the `add_endpoints` path `_classify_endpoint`'s broad `except Exception` turns it into a skipped endpoint plus an ERROR log. Either way it is loud — the old `getattr(..., False)` was silent on every path. Confirmed by renaming the field: `mypy` reports it immediately, and three `tests/unit/lc/test_deprecated_endpoints.py` tests fail rather than passing on an empty filter
- **Duplicated `ParameterHint` constants consolidated into `fmp_data.lc.hints`** (#135) - ten concept names were bound in more than one module at once, with *different* contents, so the same parameter was described one way to a tool in `intelligence` and another way to a tool in `institutional`. Nothing compared them, so the divergence was invisible. `SYMBOL_HINT` had six definitions, `CIK_HINT` and `PAGE_HINT` four each, `DATE_HINTS` four, `LIMIT_HINT` and `PERIOD_HINT` three each, and `DATE_HINT`, `INTERVAL_HINT`, `QUARTER_HINT` and `YEAR_HINT` two each. Each concept now has exactly one definition in `fmp_data.lc.hints`, imported by the domain modules.
  - **What this changes for a caller:** a hint's `examples` and `context_clues` are rendered into every generated tool's parameter description, and its `natural_names`/`context_clues`/`examples` into the embedding text the endpoint is indexed under. So tool descriptions and semantic-search ranking shift wherever a module's local copy differed from the union. `extraction_patterns` is documentation only — nothing in the package compiles or applies it — so pattern edits below change what a reader sees, not what a query resolves to
  - Six unions were taken verbatim. Six pairs genuinely conflicted, in the sense that the union would have produced *wrong* extraction rather than merely a longer list; each resolution is recorded in a comment on the hint itself:
    - **`PERIOD_HINT` split four ways.** `technical/mapping.py` bound the name for its `periodLength` parameter — an indicator lookback in bars (14, 20, 50, 200) — while `fundamental` and `lc` bound it for the statement `period`. Merging would have advertised `annual` as an RSI window and `50` as a statement period. The lookback is now `PERIOD_LENGTH_HINT`; `technical` imports that one. The statement `period` then splits again, because the catalog enforces three different `valid_values` sets under that one parameter name and `examples` are rendered verbatim into the tool description while `EndpointParam.validate_value` rejects anything outside `valid_values`: `PERIOD_HINT` (`annual`/`quarter`, the three `company` endpoints), `PERIOD_WITH_FISCAL_HINT` (adds `FY`/`Q1`–`Q4`, the seven `fundamental` endpoints) and `FISCAL_PERIOD_HINT` (`FY`/`Q1`–`Q4` only, the six bulk endpoints, which do not accept `annual`/`quarter` at all). A single union hint advertised values that fail client-side on nine endpoints — three of them a regression this consolidation introduced, six of them pre-existing on the bulk side
    - **`QUARTER_HINT` examples.** `investment` listed `["Q1", "Q4"]`, `lc` listed `["1", "2", "3", "4"]`. The wire parameter is declared `ParamType.INTEGER` ("Disclosure quarter (1-4)"), and `examples` goes straight into the tool's parameter description, so `Q1` would invite a 400. Numeric examples win; `investment`'s pattern is unioned in
    - **`CIK_HINT`** dropped `institutional`'s unanchored `(\d{10})`, which takes the first ten digits out of a longer run and yields a truncated CIK; the anchored `\b\d{10}\b` already covered the real case. Its unbounded `CIK[:\s]+(\d+)` merged with `investment`'s into one case-insensitive, ten-digit-bounded form
    - **`SYMBOL_HINT`** dropped `institutional`'s unanchored `[A-Z]{1,5}`, which matches inside a longer token (`NASDAQ` → `NASDA`). The anchored form already present is deliberately *narrower*, not equivalent — it declines that token rather than truncating it. (Its case-sensitive `symbol[:\s]+([A-Z]{1,5})` is a separate case, and genuinely is subsumed by `intelligence`'s `(?i)` form)
    - **`PAGE_HINT`** narrowed `institutional`'s `p(\d+)` to `\bp(\d+)\b` — unanchored it read `sp500` as page 500 — rather than dropping the `p2` shorthand it was reaching for. The main pattern is anchored for the same reason: the widest of the four copies, `page[:\s]*(\d+)`, read `webpage3` as page 3
    - **`AS_OF_DATE_HINT`** dropped `institutional`'s `(\d{2}/\d{2}/\d{4})`. Every FMP date parameter takes ISO `YYYY-MM-DD`, so unioning a US-order pattern in would have advertised an unsendable format across every as-of-date parameter in the catalog
  - The `DATE_HINT` / `DATE_HINTS` name collision is resolved rather than carried forward. The two module-local `DATE_HINT` constants (`investment`, `institutional`) were the one-day as-of concept and fold into the existing `AS_OF_DATE_HINT`; `DATE_HINT` no longer exists. One character separated it from the `DATE_HINTS` range mapping, with opposite meanings
  - `INTERVAL_HINT` moved out of `company/hints.py`, where its examples were `list(IntradayTimeInterval)`. Spelling the values literally keeps the shared hints module free of domain-schema imports; a test pins them to the enum so adding an interval fails until the hint catches up
  - **Import paths gone, not just moved:** `fmp_data.company.hints.CIK_HINT` and `fmp_data.company.hints.INTERVAL_HINT` no longer exist. Nothing in the package imported them and `company/hints.py` is an internal mapping helper, but an out-of-tree importer of those two names must switch to `fmp_data.lc.hints`
  - **Guard:** `tests/unit/test_hint_consolidation.py` walks every importable `fmp_data` submodule and fails if one concept name has two distinct definitions, unpacking dict-valued collections (`DATE_HINTS`, `SYMBOL_HINTS`) so an entry inside one is compared too. It carries floor assertions on modules scanned, hints found and names shared, plus a separate test that every hint-bearing module imports — otherwise a module could drop out of the scan on an `ImportError` and take its divergent hints with it. Both failure modes are mutation-tested
  - **Second guard:** a hint's `examples` must be values the endpoint accepts. `test_hint_examples_are_within_valid_values` walks all 215 registered endpoints and fails when any hint advertises an example outside the bound parameter's `valid_values` — the defect the three-way `period` split fixes, which no test could previously see. Floors on endpoints scanned and on constrained parameters found keep it from passing on an empty walk, and it is mutation-tested by re-merging the `period` hints
  - **Third guard, closing a gap the first left open (#157):** the #135 guard above compares `ParameterHint` bindings by *name*, so a concept redefined under a *different* name in another module stays invisible — `fmp_data.technical.mapping.FROM_DATE_HINT`/`TO_DATE_HINT` are exactly the "date range boundary" concept as `DATE_HINTS["start_date"]`/`["end_date"]`, with different examples and `extraction_patterns`, and neither existing guard sees the pair (different names; technical is the sole importer of its own copies). `test_no_same_concept_hint_under_a_different_name` flags a cross-module, cross-name pair when both a) their `natural_names` overlap and b) one hint's `extraction_patterns` contains a long-enough literal substring of the other's — requiring both keeps a shared generic word like "period" alone from tripping it. A hint whose patterns are an exact subset of another's is treated as a deliberate refinement, not a drifted copy, so the reviewed three-way `PERIOD_HINT`/`PERIOD_WITH_FISCAL_HINT` split above is not flagged. The one pre-existing instance this guard finds (`technical`'s local date hints) is recorded in `KNOWN_SAME_CONCEPT_DIVERGENCES` rather than fixed here — folding `technical` onto the shared hint changes the embedding text and tool descriptions of nine indicator tools, which wants its own before/after review rather than riding along in a guard fix — and the allowlist is checked against the live detector each run, so a stale entry (fixed, or no longer matching) fails the test rather than quietly widening. Floored and mutation-tested
- **`fmp-mcp generate` emitted a manifest that could not start a server** (#148) - with no `--tools` filter it wrote all 223 catalog specs verbatim, and registering the result failed with `Duplicate tool keys detected for MCP tool names: crypto_quotes, forex_quotes`. It also seeded the file with the three keys this release deprecates, so a user following the documented path got a manifest that warned on every start. A generated manifest now registers cleanly: 218 tools, no deprecated keys, no name collisions.
  - **Deprecation-aware**, as `list` and `validate` became in #136: `DEPRECATED_TOOLS` is filtered out of the default spec list. Each dropped key is named in the header and on stdout beside the replacement that ships in its place (`company.executives (deprecated; use company.key_executives, included below)`), listed under its own heading rather than mixed in with the collision drops — the reason and the remedy differ, and a deprecated key needs no name-style change to recover, only a rename. Whether the replacement is actually in the manifest is checked against the final list rather than asserted
  - **One side of each collision is excluded from the generated default set.** Under the default `FMP_MCP_TOOL_NAME_STYLE=key` the advertised name is the bare key, so `alternative.crypto_quotes` and `batch.crypto_quotes` both want to be `crypto_quotes` and `_validate_tool_names` refuses the pair — "every tool in the catalog" is not an expressible manifest under that style. Emitting guidance alone would have left the file still unable to start, so guidance *and* exclusion ship together: the header names every excluded spec, what was kept in its place and the `FMP_MCP_TOOL_NAME_STYLE=spec` setting that lets both sides coexist, and the same list is printed on generation. The kept side is whichever spec `DEFAULT_TOOLS` already serves (`alternative.*` for both pairs), so `generate` agrees with the default server rather than inventing a second opinion; sorted order breaks any future tie deterministically
  - **Colliding names are not auto-qualified.** That would change what a tool is called under the `key` style — a contract change needing its own discussion, not a side effect of fixing `generate`
  - **An explicit `--tools` selection is never thinned.** A collision inside it is the caller's own choice, so it is reported on stderr and in the file header instead of silently resolved. Defaults added on top of an explicit selection do yield to it, and say so in the header
  - The acceptance test is behavioural: a manifest generated with no filter is fed to `register_from_manifest` under `FMP_MCP_TOOL_NAME_STYLE=key` with `DeprecationWarning` raised as an error, and must register every tool it lists
  - **A deprecated key named explicitly in `--tools` is kept but reported.** An explicit ask is honoured, as with collisions — but silently, `--tools` would have been the only path in the CLI that puts a deprecated key in a manifest without saying so, which is conspicuous next to a default path that now explains every deprecation it drops
  - `_add_defaults` skips deprecated specs. The two tables are disjoint today so this is dead defence, but it runs *after* `_startable_catalog` has stripped deprecations, and without it a future deprecated entry in `DEFAULT_TOOLS` would be silently reinstated into the manifest the same release just cleaned. Guarded by injecting the overlap
  - Generated manifests now end with a newline, and an unknown entry points at `fmp-mcp list` — in `generate --tools` and in `validate` alike, which had the same dead-end message
  - **"Nothing disappears silently" is guarded exhaustively, not by example.** A test diffs the generated manifest against the full catalog and fails if *any* absent spec goes unnamed in the header, so a future exclusion rule cannot ship without its explanation; a second test pins that each deprecated drop names a replacement which is itself present. Both are mutation-tested
- **MCP bare-key resolution was implemented three times and could drift** (#149) - the rule "a bare tool key resolves only when exactly one client claims it" lived in `tool_loader._resolve_tool_spec` (the resolver registration uses), in `cli._classify_manifest_entries` (`fmp-mcp validate`'s copy) and again in the example-manifest guard test. They agreed, but nothing kept them agreeing, and validator drift is the bad case: a `validate` that blesses manifests the loader then refuses turns a startup error into a trusted green check.
  - Resolution is now split from announcement. The new pure `fmp_data.mcp.tool_loader.resolve_tool_spec(spec, key_to_spec) -> Resolution` decides; it warns nothing, logs nothing and raises nothing, which is why `validate` could not call the old resolver — looping over entries would have sprayed `DeprecationWarning`s for keys the user is merely checking. `_warn_if_deprecated` is now called only by `_resolve_tool_spec`, i.e. only on the registration path
  - `Resolution` is a frozen dataclass carrying `entry`, a `ResolutionStatus` (`RESOLVED`, `DEPRECATED`, `AMBIGUOUS`, `UNKNOWN`), the resolved `spec`/`client`/`key`, the `replacement` for a deprecated spec, every `candidates` entry for an ambiguous key, and the `message` explaining a failure — not a bare tuple callers must remember how to unpack. `is_resolved` covers `RESOLVED` and `DEPRECATED` (a deprecated key still registers until 3.0); `require()` returns the `(spec, client, key)` triple or raises `message`
  - `_resolve_tool_spec` is now a four-line wrapper over the pure function, so `validate`, the loader and the example-manifest guards share one implementation and reimplementing the rule breaks a test rather than silently diverging
  - **Behaviour change:** a fully qualified spec is now checked against the catalog. `company.profil` fails at resolution with `Tool key 'company.profil' not found in available tools` instead of being trusted through to a confusing `Endpoint semantics 'profil' not found` from `_load_semantics`. Bare keys already behaved this way; the two forms now answer to the same authority
  - **`fmp-mcp validate` now reports name clashes, the one registration failure it could not see.** The per-entry rule is shared, but a clash is a property of the manifest as a whole, so it falls outside `_classify_manifest_entries` — and `generate` learned about clashes in this same release while `validate` did not, so the very file `generate` warned about validated without a word. Entries are resolved before being compared, because `["profile", "company.profile"]` is one tool listed twice and comparing the strings as written sees nothing. The two causes are reported separately since the advice differs: two different tools claiming one name are servable with `FMP_MCP_TOOL_NAME_STYLE=spec`, while one tool named twice is refused under *either* style and the only fix is to drop one. Mutation-tested, including the mutation that collapses the two cases and hands out the misleading advice. Names are computed under the **effective** `FMP_MCP_TOOL_NAME_STYLE`, not the default, so a collision draws no warning under `spec` — warning there would tell a user to set the variable they had just set, a false positive landing only on the person who took the earlier advice. The duplicate case survives the style change, because one tool listed twice is one advertised name whichever way names are derived. The duplicate message deliberately stops short of claiming registration refuses it: under `spec`, `_validate_tool_names` skips the duplicate check entirely, which is filed as #162
  - **Not fixed here:** `validate` still exits 0 for a manifest registration would refuse. That is pre-existing on `dev` and changes the CLI's contract for anyone scripting it, so it is filed as #161 rather than slipped into this PR
  - `_build_key_to_spec` is promoted to **`fmp_data.mcp.tool_loader.build_key_to_spec`**. It builds the only argument `resolve_tool_spec` takes, and this change is what first gives it a caller outside `tool_loader` (`cli.py` did not import the module at all before), so leaving it private would have shipped a public function reachable only by reaching into a private name. Renaming a private helper breaks no documented contract
  - New guards: the pure resolver must stay silent (no `DeprecationWarning`, no log record) on a deprecated spec; the loader's decision must match the pure resolver's for every spec and every bare key in the catalog plus known-bad entries; `validate`'s classification must match it over the same set; and stubbing `resolve_tool_spec` must change what **both** `validate` and the loader report, which fails if either grows its own copy again. The equivalence guards and the stub guards catch different regressions and neither subsumes the other — an *identical* reimplementation agrees on every input and only the stub notices, while a *diverging* one is invisible to the stub. All four are mutation-tested
- **`ETFHoldingsArgs.date` is no longer required, and arg models are now guarded against being stricter than their endpoints** (#143) - `ETF_HOLDINGS` declares `date` an *optional* parameter while `ETFHoldingsArgs` declared it *required*, so a caller who satisfied the endpoint's contract was rejected by the tool schema before a request was ever built. The endpoint was right: probed against the live API on 2026-08-08, `etf/holdings?symbol=SPY` returns 505 rows with *and* without `date`. The field is now `dt_date | None = None`.
  - Latent until now only because nothing in the package imports `fmp_data/investment/schema.py` (#141); it would have become live the moment those models were wired in
  - **Superseded later in this same unreleased cycle by the #153 deprecation above**: `test_arg_model_consistency.py` has since been removed along with the `arg_model` wiring it read, and `tests/unit/test_arg_model_deprecation.py` took its place. The finding below is what motivated deprecating the layer rather than repairing it, so it is kept for the record.
  - `tests/unit/test_arg_model_consistency.py` was the guard, and it covered **all nine** `schema.py` modules rather than the three #141 names — `Endpoint.arg_model` is read by nothing anywhere in the package, so every domain's arg models were equally unchecked. It pairs 52 models to their endpoints via `Endpoint.arg_model` where that is declared, plus a hand-verified table for the three domains that declare it nowhere, and checks 148 fields
  - Three rules, in decreasing strictness. **(1)** A field required where the endpoint's param is optional — #143's defect — is never tolerated. **(2)** A field optional where the endpoint's param is mandatory is allowed only when *some* default exists on either side, so a complete request still reaches the wire; `LatestFinancialStatementsArgs.page` defaulting to `0` against a mandatory `page` passes on that basis. **(3)** Every field must name a real parameter of its endpoint
  - Rule 3 found **9 pre-existing drift sites**, none introduced here. They are frozen in `_KNOWN_PARAM_DRIFT` with a reason each, so the set cannot grow — and cannot go stale either, since an entry that gets fixed must be deleted or the test fails. The largest is `TechnicalIndicatorArgs`, whose `start_date`/`end_date`/`period`/`interval` correspond to endpoint params actually named `from`/`to`/`periodLength`/`timeframe` with no alias bridging them, across 9 indicator endpoints; also `Form13FArgs.filing_date` (the endpoint takes `year`+`quarter`), `AssetAllocationArgs.filing_date` (the param is `date`), `InstitutionalHoldingsArgs.include_current_quarter`, `FailToDeliverArgs.limit` and `SearchArgs.page` (no such parameters). This is exactly the silent rot #141 warned about
  - Models with no single unambiguous endpoint — an abstract base, a `fund_type` selector spanning two endpoints, or a model for an endpoint deleted in #130 — are **skipped and counted, not guessed at**. The count (56) is asserted as a ceiling so a new orphan cannot hide among them
  - **`MUTUAL_FUND_HOLDINGS` is deliberately left alone.** Its `date` is declared mandatory and `ParamType.STRING` (rather than `ParamType.DATE`, which would give it local date validation), disagreeing with `ETF_HOLDINGS` on both counts — but neither declaration can be verified, because the `mutual-fund-holdings` path returns 404 for every request, every symbol, with and without `date`. `MutualFundHoldingsArgs.date` therefore stays required, matching its endpoint, and both sides carry comments pointing at #152 — where the question of what that endpoint should point at belongs. Changing declarations to match an endpoint that never answers would be a guess dressed up as a fix
- **23 latent field-name/type shadowing sites removed, and a guard added so they cannot come back** (#142) - #139 was a pydantic field whose *name* shadowed the type imported for its *annotation* (`from datetime import date` plus `date: date`), which makes the entire module un-importable, not just the one field. An AST scan found 23 more class attributes named `date` in modules doing `from datetime import date`. None were broken, because each was annotated `datetime` or `str` — a *different* name — but narrowing any one of them to the semantically-correct `date`, an entirely ordinary refactor, reproduces #139 instantly and takes the whole module with it.
  - Five modules switched to the aliased import already used in `technical/schema.py` and `investment/schema.py`: `fmp_data/models.py`, `fmp_data/alternative/models.py`, `fmp_data/company/models.py`, `fmp_data/economics/models.py` and `fmp_data/intelligence/models.py` now do `from datetime import date as dt_date`, and the 20 annotations in them that referenced the bare `date` were updated to match
  - **No field names, aliases, annotations or wire behaviour changed.** `date` is still `date` on every model; only the *name the annotation is written under* moved, so validation, serialisation and JSON schema output are byte-identical
  - `tests/unit/test_datetime_shadowing.py` is the new guard. It parses every module in the package and rejects any class attribute whose name equals a name that module binds from `datetime` — covering `from datetime import ...` (honouring `as` aliases, which is exactly why aliasing is the fix), plain `import datetime`, and nested classes. It reports `file:line Class.attr` for every offender
  - The guard rejects the *shadowing*, not just the subset of it that is fatal today. `tests/unit/test_imports.py` (#140) catches the explosion after someone steps on the landmine; this removes the landmine
  - Floors (≥120 modules and ≥2500 class attributes scanned, against 127 and 3138 today) stop the scan reporting success after walking nothing
- **`batch`, `index`, `sec` and `transcripts` semantics were unguarded** (#129) - `_get_endpoint_groups()` registered nine client groups, so those four modules never reached `EndpointRegistry.validate_endpoint()` and nothing checked their `parameter_hints`. All four are now registered: the LangChain registry serves **215 endpoints, up from 168**.
  - 33 endpoints declared `parameter_hints={}` while taking real parameters (batch 22, sec 9, transcripts 2; index was already clean). All filled, reusing `fmp_data.lc.hints` wherever a shared constant fit — `LIMIT_HINT`, `PAGE_HINT`, `YEAR_HINT`, `QUARTER_HINT`, `PERIOD_HINT`, `EXCHANGE_HINT`, `SYMBOL_HINT`, `CIK_HINT`, `FROM_TO_DATE_HINTS`
  - Two new shared hints in `fmp_data.lc.hints`: `SYMBOLS_HINT` (a comma-separated ticker list, the plural of `SYMBOL_HINT`) and `AS_OF_DATE_HINT` (a single as-of day; `DATE_HINTS` only covers range endpoints, and its `start_date` entry would tell the model a one-day snapshot means "from" — named `AS_OF_DATE_HINT` rather than `DATE_HINT` so it cannot be misread as the similarly-named range mapping beside it). Five module-local hints cover concepts no other client has: `SHORT_HINT` and `PART_HINT` in `batch`, `FORM_TYPE_HINT`, `SIC_CODE_HINT` and `COMPANY_NAME_HINT` in `sec`
  - **Groups are now derived from the mapping modules, not hand-listed.** A group carries exactly one category — `ValidationRuleRegistry.validate_category` compares each entry's own `category` against the category of whichever rule owns the longest matching prefix, and a group's endpoint-map keys are exact matches for its own endpoints, so a group's own rule always wins. `batch` declares five categories and `sec` two, so the new `_partition_by_category` splits each client module into one group per category it declares: `batch_market` (11), `batch_fundamental` (11), `batch_intelligence` (3), `batch_company` (2), `batch_institutional` (1), `sec_company` (6), `sec_intelligence` (4). **No declared `category` was changed** — `category` feeds the semantic search the registry exists to serve, so rewriting `batch.income_statement_bulk` to `MARKET_DATA` would have stopped it matching "fundamentals". Partitioning is derived rather than listed, so a future category change repartitions instead of silently re-drifting; a test asserts it is a no-op for all eleven uniform clients
  - `GroupConfig` gains a `client` key naming the client module a group came from, since a module may now contribute several groups. `get_endpoint_groups()` returns 18 groups across 13 clients
  - `resolve_semantics_for_endpoint` moved from `fmp_data.lc` to `fmp_data.lc.registry` (partitioning needs it before a group exists) and is re-exported, so `from fmp_data.lc import resolve_semantics_for_endpoint` is unchanged
  - **Four endpoints stay out of the LangChain registry**, listed in the new `fmp_data.lc.registry.PENDING_COLLISION_EXCLUSIONS`: `batch.get_crypto_quotes` and `batch.get_forex_quotes` (owned by `alternative`), `sec.get_profile` (owned by `company`) and `sec.search_by_cik` (owned by `market`). The registry is a flat `name -> EndpointInfo` map and LangChain tool names come from `semantics.method_name`, so two tools called `get_profile` cannot coexist; registering them would have let the later client silently overwrite the earlier one's entry. All four remain reachable through MCP, which addresses tools as `"<client>.<key>"`. This is a stopgap pending #126 and #136, which settle the tool-key namespace with a deprecation cycle; nothing is renamed or deprecated here
  - New guard tests: every group's category must equal the category all of its semantics declare; every endpoint must route to its own group's rule (`batch.get_quotes` vs `company.get_quote` is a one-character near-miss, `batch.get_income_statement_bulk` extends `fundamental.get_income_statement`, and `batch_market`/`index`/`market` all claim `MARKET_DATA`); partitioning is a no-op for uniform clients and loses nothing for the two that split; every `SemanticCategory` has a group slug; and each `PENDING_COLLISION_EXCLUSIONS` entry must be a genuine cross-client clash whose hints still track its endpoint. `LC_EXCLUDED_CLIENTS` in the catalog guards is now empty
- **LangChain tools marked every endpoint parameter as required** (#128) - `ToolFactory.create_parameter_fields` built every parameter as `Field(description=...)` with no default, so pydantic marked optional endpoint parameters required and the LLM had to invent values the endpoint never wanted. `market.get_historical_sector_pe` demanded `from`, `to` and `exchange` alongside its one genuinely mandatory `sector`. 80 of the 215 registered endpoints declare optional params and emitted tools of this shape, over 167 parameters in total; the other 135 are mandatory-only and were always correct.
  - `create_parameter_fields` now takes `mandatory_params` and `optional_params` as separate arguments instead of one concatenated list. Mandatory-ness comes from which list a parameter arrives in, never from the parameter itself: 13 params sit in `optional_params` with `required=True`, and 13 more sit in `mandatory_params` carrying a `default`, so neither `EndpointParam.required` nor `param.default is not None` answers the question. `Endpoint.validate_params` already resolved it by list membership; the tool schema now matches.
  - Optional parameters are typed `| None` **and** given a pydantic default, so `is_required()` is false. The default is `param.default` rather than `None` whenever the endpoint declares one — `validate_params` marks a param seen before it skips a `None` value, so defaulting to `None` would have suppressed the default on the way out.
  - **Behaviour change:** see the two entries under **Changed** above — the generated schemas' required-field sets shrank, and `create_parameter_fields` is a signature break for any external caller.
  - A guard test asserts, for every registered endpoint, that the generated schema's required-field set equals `{p.name for p in endpoint.mandatory_params}`, with a floor on the number of endpoints checked so it cannot pass vacuously
  - A second guard drives a real `StructuredTool` and asserts an omitted optional still reaches the wrapped function carrying its declared default (`period=annual`, `limit=40`). That behaviour rests on langchain forwarding fields that hold explicit defaults — an implementation detail of `BaseTool._parse_input`, in a dependency pinned `>=1.4.9` with no upper bound — so inspecting `model_fields` alone would let a langchain change silently drop 64 optional params' defaults off the wire with the suite still green
- **Uncompilable enum validation patterns** (#134) - `EndpointBasedRule._get_type_pattern` emitted `^(annual|quarter))$` — one closing paren too many — for every string parameter declaring `valid_values`. The patterns are consumed by an uncaught `re.match` in `fmp_data/lc/validation.py`, so any caller reaching `ValidationRuleRegistry.get_parameter_requirements` on a live registry hit `re.error`. 22 parameters across 15 endpoints were affected (`period`, `interval`, `timeframe`, `name`).
  - Enum members now contribute their `.value` rather than their repr, so `economics.get_economic_indicators` matches `realGDP` instead of `EconomicIndicatorType.REAL_GDP`. The unwrapping happens once, in `EndpointParam.__post_init__`, so both consumers of `valid_values` — pattern generation and the membership check in `validate_value` — see the wire value. Only `Enum` is unwrapped; other values keep their native type, since `validate_value` compares against a *converted* request value and an integer-typed param such as `transcripts.quarter` (`valid_values=[1, 2, 3, 4]`) would otherwise never match
  - Alternatives are `re.escape`d, since `valid_values` is endpoint-declared data. A non-`str` enum value is stringified first — `re.escape` raises `TypeError` when handed an `int`
  - **Behaviour change:** these patterns previously raised `re.error` on any use and now validate correctly. No in-repo caller reaches them today, so library users on the default paths see no change; an external caller invoking the public `ValidationRuleRegistry.get_parameter_requirements` now gets working validation instead of a crash. Matching is case-sensitive against the endpoint's declared `valid_values` — `period="annual"` is accepted, `period="ANNUAL"` is not.
- **Integer CIK values rejected regardless of `validation_mode`** (#131) - `cik` fields were declared as bare `str`, and `BaseClient._validate_model` calls `model_validate` before any `validation_mode` branching, so an integer CIK raised a `ValidationError` under every mode. All 58 CIK-valued fields across 8 modules — 45 named `cik` plus 13 named `*_cik` (`reporting_cik`, `company_cik`, `targeted_cik`, `intermediary_commission_cik`) — now use the new `fmp_data.models.CIK` type, which coerces an integer to its canonical 10-digit zero-padded form (`320193` → `"0000320193"`). Strings pass through untouched, including already-unpadded ones. A guard test asserts no model can reintroduce a bare-`str` CIK field.
- **Integer CIKs rejected or silently mismatched on the request path** (#131) - the fix above covered responses only. Outbound, every `cik` parameter was declared `ParamType.STRING`, so `cik=320193` was sent as `"320193"` — a request that succeeds and returns nothing, a worse failure than the inbound rejection it mirrored. The pydantic argument models backing the LangChain tools (`Form13FArgs`, `Form13FDatesArgs`, `PortfolioDateArgs`) rejected an integer outright.
  - New `ParamType.CIK`, applied to all 16 `cik` parameter declarations across 6 modules, zero-pads on the way out
  - Unlike the response coercer, it pads numeric *strings* too: inbound, re-padding would misreport what the API sent; outbound the padded form is simply the correct request. Non-numeric strings pass through so a bad value surfaces as an API error rather than being mangled into one; `bool` is rejected, matching pydantic's response-side behaviour
  - Sync and async client methods taking a `cik` now accept `str | int`
  - The argument models use the `CIK` type, so an integer is padded before their `^\d{10}$` constraint is checked
  - Guard tests assert no `cik` parameter can revert to `ParamType.STRING` and no model can reintroduce a bare-`str` CIK field; the latter now walks every module rather than only `*.models`, which is where the argument-model drift had been hiding

- **`fmp_data.investment.schema` was un-importable** (#139) - `ETFHoldingsArgs` and `MutualFundHoldingsArgs` each declared a field named `date` annotated with the `date` imported from `datetime`. Under pydantic 2.13 the field name shadows the type before the annotation is evaluated, so building the class raised `PydanticUserError` and the entire module — every arg model in it — was unreachable at runtime. Anything importing the module — directly or via a LangChain registration path — would have failed outright; in practice nothing in the package does, which is precisely why the break went unnoticed.
  - The annotation is now imported as `dt_date`, matching the convention already used in `fmp_data/technical/schema.py`. The field is still named `date`, so the wire format is unchanged. `tests/unit/test_investment.py` pins that field name, its `datetime.date` annotation and its ISO parsing, so a rename to dodge the clash cannot pass silently
  - New `tests/unit/test_imports.py` asserts every module in the package imports, failing on any exception rather than only `ImportError` — #139 raised `PydanticUserError`, so an `ImportError`-only check would have missed it. Nothing in the suite imported this module, which is why the break sat unnoticed
    - The optional-extra exemption for `fmp_data.lc` / `fmp_data.mcp` is keyed on whether the extra is actually installed, not on the module name: CI runs `langchain` and `mcp-server` sessions with those extras present, and a name-only exemption would have swallowed genuine `ImportError`s in the very jobs meant to catch them
    - `walk_packages` is given an `onerror` handler, since by default a package that fails to import silently drops its whole subtree from the walk
  - The `_KNOWN_UNIMPORTABLE` allowlist added in #138 is now empty, so the CIK drift guard covers `investment.schema` again — raising its coverage from 63 to 64 CIK-valued fields and confirming `PortfolioDateArgs.cik` is correct

## [2.5.0] - 2026-08-07

Released from `dev` via #113. Adds earnings report times (#111), the analyst
grades/ratings MCP surface (#116), CIK company profiles, and opt-in response
caching; repairs MCP/LangChain semantics drift (#114, #115, #120, #121, #122,
#123) so the LangChain registry serves all 168 endpoints instead of 75; and
starts type-checking `tests/` (#125).

### Added
- **Analyst Grades & Ratings via MCP** (#116) - Wired the intelligence grades/ratings surface into the mapping layer so MCP discovery and `DEFAULT_TOOLS` can advertise and call them:
  - New `INTELLIGENCE_ENDPOINT_MAP` entries and `INTELLIGENCE_ENDPOINTS_SEMANTICS` for `ratings_snapshot`, `ratings_historical`, `price_target_news`, `price_target_latest_news`, `grades`, `grades_historical`, `grades_consensus`, `grades_news`, `grades_latest_news`
  - All nine added to `DEFAULT_TOOLS`, along with the now-working `intelligence.crowdfunding_search` and `intelligence.equity_offering_search` (intelligence defaults: 28 → 39)
  - `docs/mcp/tools.md` updated: Intelligence catalog lists 45 semantics tools (39 in `DEFAULT_TOOLS`); Institutional MCP tool key `cik_mapper` renamed to `cik_mappings`
- **Earnings Report Times** (#111) - Exposed FMP's `includeReportTimes` flag on the intelligence earnings endpoints:
  - `get_earnings_calendar(..., include_report_times=...)` and `get_historical_earnings(..., include_report_times=...)` on both sync and async clients
  - Python kwarg `include_report_times` maps to query `includeReportTimes` when not `None` (explicit `True`/`False` are forwarded; unset omits the param)
  - When true, responses may populate session `time` (`"bmo"` / `"amc"`), `period_ending`, `fiscal_period`, `fiscal_year`, and `confirmed` (per-row optional)
  - New `EarningEvent` fields are optional and default to `None`; without the flag the API typically omits confirmation/fiscal extras. Session `time` can still appear on base `/earnings` payloads (including company `get_earnings()`)
  - `get_historical_earnings()` also accepts optional `limit`
  - Thanks to @joshuatz for the report
- **New Company Endpoint** - Added `get_profile_cik()` method to retrieve company profile using CIK (Central Index Key) number
  - Available in both sync (`CompanyClient`) and async (`AsyncCompanyClient`) clients
  - Endpoint: `/stable/profile-cik`
  - MCP semantics key: `company.profile_cik`
  - Useful for SEC filing research and cross-referencing regulatory data
- **Opt-in Response Caching** - Added a pluggable response caching subsystem for sync and async clients:
  - New `CacheConfig` model is exported from `fmp_data` and supported on `ClientConfig`
  - Added in-memory, file-based, and Redis cache backends under `fmp_data.cache`
  - Added environment-based cache configuration via `FMP_CACHE_ENABLED`, `FMP_CACHE_BACKEND`, `FMP_CACHE_TTL`, `FMP_CACHE_DIR`, and `FMP_CACHE_REDIS_URL`
  - Added per-endpoint TTL overrides, deterministic cache keys, and `force_refresh=True` support to bypass cache reads on demand
  - Added optional `cache-redis` extra for Redis-backed caching

### Changed
- **`EndpointRegistry.register_batch()` signature and failure contract** (#121) - Was `-> None` and raised `ValueError` on the first endpoint that failed validation; is now `-> dict[str, str]` and never raises, returning a `{endpoint_name: error}` mapping of the endpoints it skipped (empty when all registered). `EndpointRegistry` is absent from `fmp_data.lc.__all__`, but `from fmp_data.lc import EndpointRegistry` still resolves, so any code holding a direct reference is affected — not only code importing from `fmp_data.lc.registry`. Callers that relied on the exception to detect drift should check the returned mapping instead. `register()` is unchanged and still raises.
- **`setup_registry()` no longer swallows non-validation errors** (#121) - It used to wrap each group's registration in `except Exception`, log an error, and continue. Validation failures are now handled per endpoint inside `register_batch()`, and anything else propagates instead of leaving a silently half-built registry — in practice an `ImportError`/`AttributeError` raised while `register()` lazily builds the validation rules via `_ensure_validation_initialized()`. (The `get_endpoint_groups()` call at the top of `setup_registry()` was never inside the removed handler, so it always propagated.) Note that `create_vector_store()` still wraps this in a blanket `except Exception` and returns `None`, so the loud failure does not yet reach that caller; see #133.
- **`create_vector_store` default argument** - The `embedding_provider` default moved from `EmbeddingProvider.OPENAI` to `None`, resolved to OpenAI inside the function, so the signature no longer forces an eager `fmp_data.lc.embedding` import at module load. Omitting the argument behaves exactly as before; passing `None` explicitly now selects OpenAI instead of raising
- **MCP SDK 2.x Support** - The MCP server now works against both MCP SDK 1.x and 2.x:
  - MCP SDK 2.0 renamed `mcp.server.fastmcp.FastMCP` to `mcp.server.MCPServer`
  - Added `fmp_data.mcp._compat` to resolve whichever class the installed SDK provides
  - The `mcp` extra floor stays at `>=1.28.1`, so no forced SDK upgrade for existing installs
- **CI / Tooling Refresh** (#112, closes #107, #108, #109, #110) - Updated GitHub Actions, pre-commit hooks, and the security session:
  - Actions: `checkout` → v7.0.1, `setup-python` → v7.0.0, `setup-uv` → v9.0.0, `gh-action-pypi-publish` → v1.14.1 (since bumped to v1.14.2 in #132)
  - Pre-commit: `ruff` + `ruff-format` at v0.16.1 (replaces the black 24.x hook, which fought ruff on assert-message wrapping); `pre-commit-hooks` v6.0.0; `bandit` 1.9.4
  - Reformatted the tree with ruff 0.16 (formatting only, including Python blocks inside Markdown — hence the docs churn)
  - `nox -s security` upgrades pip before `pip-audit` instead of suppressing `CVE-2026-1703`, so the report covers project dependencies rather than the virtualenv's bundled pip
  - Package floors in `pyproject.toml` for `mcp` / `ruff` / `mypy` are unchanged; `uv.lock` remains gitignored and is not part of the published artifact
- **MCP default toolset hygiene** - Removed dead/deprecated intelligence tools from `DEFAULT_TOOLS` so the default MCP server no longer registers tools that always fail or return empty:
  - Dropped: `intelligence.earnings_confirmed`, `intelligence.earnings_surprises`, `intelligence.stock_news_sentiments`, `intelligence.historical_social_sentiment`, `intelligence.trending_social_sentiment`, `intelligence.social_sentiment_changes`
  - Client methods remain importable; custom manifests can still opt in explicitly
- **MCP tools reference is complete and self-checking** (#123) - `docs/mcp/tools.md` was missing four whole client sections and carried stale counts:
  - Added the `Batch` (30), `Index` (6), `SEC` (12), and `Transcripts` (4) sections, plus the previously undocumented `company.profile_cik`
  - Every section now states both numbers — catalog tools and how many are in `DEFAULT_TOOLS` — with the convention explained once in the header (224 catalog / 159 default)
  - A guard test asserts every discovered tool key appears in the doc and that the header totals match, so the reference cannot silently drift again
- **tests/ is now type-checked** (#125) - Removed `tests/` from the mypy exclude list so test annotations are verified instead of decorative:
  - Added a `tests.*` override that relaxes `disallow_untyped_defs` / `disallow_incomplete_defs`, so wrong annotations are caught without requiring complete ones
  - Fixed the 76 latent errors this surfaced (narrowing asserts, explicit annotations, targeted `type: ignore`s); no test behavior or assertions changed
  - `nox -s typecheck` now runs mypy over `fmp_data` and `tests`
  - Remaining work: tighten the override directory by directory until `tests/` inherits the strict settings
- **Volume Type Normalization** - Normalized price-model volume fields to always deserialize as `float`:
  - `alternative.HistoricalPrice.volume` and `alternative.HistoricalPrice.unadjusted_volume` now normalize whole-number payloads such as `123` to `123.0`
  - `company.IntradayPrice.volume` now normalizes whole-number payloads to `float` as well
  - This keeps a single return type for price-volume fields when FMP mixes integer and fractional responses
  - Release impact: treat this as a minor release because the runtime type and generated schema change from integer to number for these fields
- **GitHub Actions Maintenance** - Updated workflow actions to current upstream releases:
  - Bumped `actions/deploy-pages` from `v4` to `v5` in the documentation workflow
  - Bumped `codecov/codecov-action` from `v5` to `v6` in CI coverage uploads
  - Bumped `actions/github-script` from `v8` to `v9` in the TestPyPI publishing workflow
  - Bumped `pypa/gh-action-pypi-publish` from `v1.13.0` to `v1.14.0` in publishing workflows
- **VCR Cassettes Excluded from Git** - Cassettes are now gitignored (`tests/integration/vcr_cassettes/`) because they are too large for GitHub (130 MB+ individual files). Developers must record cassettes locally with `FMP_TEST_API_KEY`.
- **CI Secret Scan** - The `secret-scan` job now gracefully skips when no cassette YAML files are present instead of failing.
- **Cassette Contract Test** - `test_vcr_cassettes_match_endpoint_models` now skips with a clear message when no cassettes are found, instead of silently passing.
- **Documentation** - Enhanced `CLAUDE.md` with best practices:
  - Added critical testing strategy reminders for validating successful API responses
  - Documented historical price endpoint variants (`/full`, `/light`, `/non-split-adjusted`, `/dividend-adjusted`)
  - Added endpoint definition guidelines to prevent future 404 errors
  - Established deprecation handling process for removed FMP endpoints
- **Testing** - Enabled parallel pytest runs for local Makefile/nox usage and added `pytest-xdist` to dev dependencies (CI remains serial to avoid stalls).
- **Makefile** - `.venv/.installed` now tracks `pyproject.toml` changes to auto-refresh dev deps.

### Fixed
- **Mapping drift between semantics and client methods** (#114) - Corrected `method_name` values that no client method implemented, which made `register_from_manifest` fail for tools that discovery advertised:
  - `intelligence.crowdfunding_search` → `search_crowdfunding`, `intelligence.equity_offering_search` → `search_equity_offering` (endpoint-map keys renamed to match)
  - Same class of drift fixed in neighbouring clients found by the new guard test: `market.search` → `search_company`, `institutional.cik_mapper` → `get_cik_mappings` (semantics key renamed to `cik_mappings`), `institutional.cik_mapper_by_name` → `search_cik_by_name`
  - `resolve_semantics_for_endpoint` now also matches on `method_name` (not only exact key / `get_` strip), so the renamed entries still pair with their semantics
  - New unit tests assert every discovered tool's `method_name` resolves on a live client via `_resolve_attr`, and that discovery is non-empty under the `mcp` extra alone
- **Ghost intelligence semantics** (#115) - Removed `intelligence.institutional_holders` and `intelligence.financial_reports_dates`, which advertised methods owned by the institutional and fundamental clients:
  - They could never register, and their key-only tool names collided with the real `institutional.institutional_holders` / `fundamental.financial_reports_dates` tools
  - The real tools remain available on their owning clients
- **MCP semantics import no longer requires the langchain extra** - `fmp_data.lc` defers langchain-heavy imports so `fmp_data.lc.models` (and therefore domain `mapping.py` modules / MCP discovery) load with `fmp-data[mcp]` alone
- **LC category validation picked the wrong endpoint group** (#122) - `ValidationRuleRegistry.validate_category` matched the *first* registered group whose prefix matched, so a shorter prefix in an earlier group swallowed a longer, exact match in the right one — company's `get_price_target` claimed intelligence's `get_price_target_news` and `get_price_target_latest_news`, failing them with a bogus "belongs to Company Information" mismatch. It now prefers the longest matching prefix, which the owning group always supplies because endpoint-map keys *are* method names
- **Two intelligence tools advertised capabilities they do not have** - Repairing the drifted endpoints made both of these register as live LangChain tools for the first time, which exposed the mismatch:
  - `intelligence.stock_news` described itself as "stock-specific news" with `"Get stock news for AAPL"` as its lead example, but `STOCK_NEWS_ENDPOINT` accepts only `page` / `start_date` / `end_date` / `limit`. LC's `create_tool` calls `client.request(endpoint, **kwargs)` directly rather than the sync client method that delegates when `symbol` is passed, so a symbol-scoped query matched a tool that ignored the symbol and returned the global feed. It is in `DEFAULT_TOOLS`, so this affected MCP too. Description and example queries now describe the unfiltered feed
  - `intelligence.stock_news_sentiments` is deprecated and returns `[]` without calling upstream, and `docs/mcp/tools.md` already said so — the semantics table was the one place that did not, so the vector store surfaced it for sentiment queries and returned an empty success. Now marked deprecated in its description, with its matching terms retargeted so it stops competing for live sentiment queries
- **LangChain registry drops most of the catalog** (#121) - `EndpointRegistry.register_batch()` raised on the first endpoint that failed validation, so `setup_registry()` skipped the rest of that client group:
  - `register_batch()` now registers every valid endpoint, collects the failures, and returns them as a `{endpoint_name: error}` mapping instead of raising
  - `setup_registry()` logs a per-group summary of skipped endpoints rather than dropping the group
  - Registered endpoints went from 75 to the full 168 with the semantics fixes below
- **Endpoint semantics drift** (#123) - Fixed the 27 endpoints that failed registry validation:
  - Added missing parameter hints for `analyst_estimates`, `intraday_prices`, `employee_count`, `geographic_revenue_segmentation`, `owner_earnings`, `market_hours`, `search_by_cik`, the sector/industry performance and PE endpoints, `form_13f`, `institutional_holders`, `institutional_holdings`, `insider_trades`, `cik_mapper`, `cik_mapper_by_name`, and `equity_offering_rss`
  - Removed hints for parameters the endpoints do not accept (`stock_news.tickers`, `stock_news_sentiments` date/limit hints, `institutional_holdings.includeCurrentQuarter`, `cik_mapper_by_name.name`)
  - Corrected `aftermarket_trade`, `aftermarket_quote`, and `stock_price_change` to the Company Information category that matches the client they live on
  - Historical sector/industry endpoints now hint the actual `from`/`to` query params instead of `start_date`/`end_date`
  - Added shared `PAGE_HINT`, `SECTOR_HINT`, `INDUSTRY_HINT`, `YEAR_HINT`, `QUARTER_HINT`, `CIK_HINT`, and `FROM_TO_DATE_HINTS` to `fmp_data.lc.hints`
  - New guard tests assert the whole catalog pairs with semantics and passes validation, so future drift fails in CI
- **`company.intraday_price` semantics drift** (#123) - The `intraday_price` alias shares `get_intraday_prices` with the `intraday_prices` entry but hinted only `symbol`/`interval`. It is a `DEFAULT_TOOLS` entry, and registry validation never saw it because the endpoint-map key pairs with `intraday_prices` first. It now hints `start_date`, `end_date`, and `nonadjusted` like its twin, and a semantics-first guard test covers alias entries that no endpoint key selects.
- **Stale `client_name` on company price/quote semantics** (#123) - Eight `COMPANY_ENDPOINTS_SEMANTICS` entries (`quote`, `simple_quote`, `intraday_price(s)`, `historical_price(s)`, `market_cap`, `historical_market_cap`) declared `client_name="market"`, but the methods live on `CompanyClient`. Nothing dispatches on this field, so the effect was limited to wrong metadata in the semantics table.
- **`InstitutionalOwnershipDates.cik`** - The API returns `cik` on Form 13F filing dates; it is now a declared optional field instead of relying on extra-field passthrough
- **Historical Earnings 404** (#111) - Fixed `get_historical_earnings()` returning nothing:
  - The endpoint pointed at the legacy `historical/earning-calendar` path, which 404s on `/stable`
  - Now uses the stable `/earnings` path (same family as company earnings)
  - Integration test asserts a non-empty response so a future path break fails loudly (re-record local VCR cassettes after path changes; cassettes are gitignored)
- **Dead earnings endpoints soft-fail** (#111) - `get_earnings_confirmed()` and `get_earnings_surprises()` (sync and async) now emit `DeprecationWarning` and return `[]` without calling the upstream 404 paths (same soft-fail pattern as `get_stock_news_sentiments`)
- **Cache Payload Isolation** - Prevented mutable cached payloads from being shared by reference:
  - `BaseClient` now deep-copies cache payloads on both cache read and write paths
  - Added sync and async regression coverage to prevent future cache aliasing regressions
- **Float Volume Handling** - Fixed price models that failed when FMP returned fractional volume values:
  - `alternative.HistoricalPrice.volume` and `alternative.HistoricalPrice.unadjusted_volume` now validate fractional inputs without raising
  - `company.IntradayPrice.volume` now validates fractional inputs without raising
  - Added regression tests for both float-volume validation paths
- **Quote Volume Nullability** - Fixed quote models to accept `null` volume values from the API:
  - `Quote.volume` and `SimpleQuote.volume` now use `int | None`
  - Added regression coverage for `volume=None` model validation
- **Stock News Null Symbol** - Fixed `ValidationError` when FMP API returns `null` for `symbol` field in stock news responses (Issue #62):
  - Made `StockNewsArticle.symbol` optional (`str | None`)
  - Made `StockNewsSentiment.symbol` optional for consistency
  - Added unit and integration tests for null symbol handling
- **Historical Price Endpoints** - Fixed 404 errors on historical price endpoints by correcting endpoint paths:
  - Updated `HISTORICAL_PRICE` (company), `CRYPTO_HISTORICAL`, `FOREX_HISTORICAL`, and `COMMODITY_HISTORICAL` to use `/full` suffix
  - Changed paths from `historical-price-eod` to `historical-price-eod/full` to match FMP API specification
  - All VCR test cassettes re-recorded with correct 200 status codes and actual price data
  - Updated integration tests to validate non-empty responses and detect future path mismatches
- **Alternative Markets Models** - Fixed Pydantic validation errors for crypto/forex/commodity historical prices:
  - Made `adj_close` and `unadjusted_volume` fields optional in `HistoricalPrice` model
  - Fixed `FOREX_HISTORICAL` endpoint to use correct response model (`ForexHistoricalPrice` instead of `ForexPriceHistory`)
  - Updated unit test mocks to match actual `/full` endpoint response format (flat list structure)
- **Test Coverage** - Improved patch coverage for deprecation warnings:
  - Added async test for `get_stock_news_sentiments()` deprecation warning
  - Enhanced sync test to validate `DeprecationWarning` emission
- **Missing Data Defaults** - Normalized economic and intelligence models to keep missing values as `None`:
  - `EconomicEvent.country` now defaults to `None` instead of empty string
  - `EconomicEvent.change_percent` now defaults to `None` instead of `0`
  - Government trading `owner`/`comment` fields now default to `None`
- **Comprehensive Model Field Audit** - Fixed missing fields and incorrect aliases across all Pydantic models to match actual FMP API responses (Issue #66):
  - **Index models**: Fixed `IndexConstituent.headquarter` alias (`headQuarter`), added `date_added` field to `HistoricalIndexConstituent`
  - **SEC models**: Added 20+ missing fields to `SECProfile` (sic_group, isin, city, state, country, description, ceo, website, etc.), added `has_financials` and `link` to `SECFiling8K`
  - **Transcripts models**: Fixed `year` field in `EarningsTranscript` and `TranscriptDate` to accept both `fiscalYear` and `year` via `AliasChoices`
  - **Intelligence models**: Added `publisher` field to `StockNewsArticle`, added 5 missing fields to `PressReleaseBySymbol` (publishedDate, publisher, image, site, url)
  - **Market models**: Fixed `ExchangeSymbol` aliases for `priceAvg50`, `priceAvg200`, `avgVolume`, `previousClose`; removed duplicate `IndexConstituent` class
  - **Company models**: Fixed `CompanyProfile` aliases for `vol_avg`, `mkt_cap`, `last_div`, `changes` using `AliasChoices`; added `change_percentage`, `volume`, `exchange_full_name` fields
  - **Alternative models**: Fixed `PriceQuote.change_percent` and `CryptoQuote.change_percent` to accept both `changesPercentage` and `changePercentage` variants
  - **Fundamental models**: Added 36+ fields to `FinancialGrowth`, 30+ fields to `BalanceSheet`, 8 fields to `OwnerEarnings`, 7 fields to `FinancialScore`, 4 fields to `EnterpriseValue`
- **Cassette-Driven Model Enhancement** - Added 230+ missing fields across 13 models by validating all VCR cassettes against Pydantic models:
  - **FinancialGrowth**: Added 110 line-item growth fields for income statement, balance sheet, and cash flow growth endpoints; added `AliasChoices` for `growthAccountPayables`/`growthAccountsPayables` variant
  - **CommitmentOfTradersReport**: Added 113 fields covering position breakdowns, changes, trader counts, concentration ratios, and percent of open interest
  - **Company models**: Added `change` to `SimpleQuote`; added `adjHigh`, `adjLow`, `adjOpen`, `symbol` to `HistoricalPrice`; added 7 fields to `MergerAcquisition` (`symbol`, `cik`, `targetedSymbol`, `targetedCik`, `transactionDate`, `acceptedDate`, `link`); added `symbol`, `fiscalYear`, `period`, `reportedCurrency` to `RevenueSegmentItem`
  - **Alternative models**: Added `fromCurrency`, `fromName`, `toCurrency`, `toName` to `ForexPair`; added `tradeMonth` to `Commodity`
  - **Batch models**: Added `AliasChoices` for `changePercentage` on `BatchQuote`; added `askPrice`, `bidPrice`, `askSize`, `bidSize`, `volume` to `AftermarketQuote`; added `tradeSize` to `AftermarketTrade`
  - **Fundamental models**: Added `capitalLeaseObligationsNonCurrent` to `BalanceSheet`; added `reportedCurrency` to `AsReportedFinancialStatementBase`; added `growthTaxPayables` to `FinancialGrowth`
  - **Economics models**: Added `unit` to `EconomicEvent`
  - **Other**: Added `source` to `ShareFloat`
- **AsReported Model Validator** - Fixed decorator ordering on `AsReportedFinancialStatementBase.merge_data_payload` (`@model_validator` must be outermost) so the `data` dict is properly flattened before Pydantic validation
- **Final Cassette Contract Alignment** - Added missing optional fields to 15 Pydantic models across 7 files so that `test_vcr_cassettes_match_endpoint_models` passes with zero uncaptured fields:
  - **Fundamental models**: Added `stock_price_display` (alias `Stock Price`) to `DCF`; 40 WACC/DCF component fields to `CustomDCF`; 29 levered DCF component fields to `CustomLeveredDCF`; `data`, `fiscal_year`, `reported_currency` to `FinancialStatementFull`
  - **Institutional models**: Added 6 filing metadata fields to `InstitutionalHolder`; 21 position/options fields to `InstitutionalHolding`; 13 insider detail fields to `InsiderRoster`; `cik`, `name_of_reporting_person` to `BeneficialOwnership`
  - **Intelligence models**: Added `daa` to `IPOEvent`; `publisher`, `symbol` to `GeneralNewsArticle`; `publisher` to `ForexNewsArticle`; 5 fields to `PressRelease`; `fiscal_year` to `ESGRating` and `ESGBenchmark`; 7 score fields to both `RatingsSnapshot` and `HistoricalRating`; `date` to `StockGrade`; 6 fields to `HistoricalStockGrade`
  - **Investment models**: Added `security_cusip` to `FundDisclosureHolderLatest`
  - **Market models**: Added `closing_additional`, `opening_additional` to `MarketHours`; `adj_close_time`, `adj_open_time`, `is_closed`, `is_fully_closed` to `MarketHoliday`; `country_code`, `country_name`, `delay`, `symbol_suffix` to `ExchangeSymbol`; 34 screener/profile fields to `CompanySearchResult`; `market_cap` to `ISINResult`
  - **SEC models**: Added `has_financials`, `link` to `SECFinancialFiling`; `link` to `SECFilingSearchResult`
  - **Base models**: Added `company_name`, `reporting_currency`, `trading_currency` to `CompanySymbol`
- **Cassette Contract Test** - Enhanced to run in `warn` mode and assert zero uncaptured fields (excluding dynamic SEC XBRL taxonomy keys in AsReported models)

### Deprecated
- **Confirmed Earnings & Earnings Surprises Endpoints** (#111) - Marked `get_earnings_confirmed()` and `get_earnings_surprises()` as deprecated on sync and async clients:
  - Upstream paths `earning-calendar-confirmed` and `earnings-surprises` 404 on `/stable`
  - Methods emit `DeprecationWarning` and return `[]` without making an HTTP call (soft-fail; see Fixed above)
  - Prefer `get_earnings_calendar(include_report_times=True)` and read `confirmed` plus session `time` (`"bmo"` / `"amc"` — not a drop-in for the old HH:MM clock string on `EarningConfirmed`)
  - Prefer `get_historical_earnings()` and compare `eps` vs `eps_estimated` (old surprise model used `actual_earning_result` / `estimated_earning`)
  - `EarningConfirmed` and `EarningSurprise` models remain importable; removal planned for the next major version
- **Stock News Sentiments Endpoint** - Marked `get_stock_news_sentiments()` as deprecated:
  - FMP API no longer supports the `stock-news-sentiments-rss-feed` endpoint (returns 404)
  - Both sync and async methods now emit `DeprecationWarning` with clear migration message
  - Method returns empty list to maintain backward compatibility
  - Will be removed in a future major version

### Security
- **HTTP Error Traceback Redaction** - Suppressed exception chaining for HTTP status errors so formatted tracebacks do not expose API key query parameters:
  - Updated rate limit, authentication, validation, and fallback HTTP error paths to raise sanitized package exceptions without chaining the raw `httpx.HTTPStatusError`
  - Added regression coverage for API key redaction in formatted tracebacks and exception messages

- **VCR Cassette Leak Guard** - Added unit tests that scan all committed VCR cassettes for leaked API keys:
  - `test_vcr_sanitization.py` verifies the VCR `scrub_api_key` / `scrub_response_secrets` hooks and scans every YAML cassette for real API key values
  - `test_cassette_contracts.py` validates every cassette response against its declared Pydantic endpoint model, catching schema drift and stale cassettes
  - Pre-commit `detect-secrets` hook now excludes only Python test files (`tests/.*\.py$`), ensuring cassette YAML files are always scanned
  - CI `secret-scan` job explicitly targets `tests/integration/vcr_cassettes/` as an additional safety net

## [2.4.0] - 2026-07-13

Released from `dev` via #106 (HTTP redaction, bulk volume fix, dependency refresh).

### Fixed
- **Bulk CSV Volume String Coercion** (#104) - Fixed silent bulk row drops when FMP sends volume as a fractional numeric string:
  - `coerce_volume_value` now coerces numeric strings such as `"475.9"` via `int(float(...))` for `CompanyProfile` / `Quote` volume fields
  - Empty/whitespace volume cells become `None`; non-numeric strings still surface as validation errors
  - Addresses ~9.7% row loss on `profile-bulk` (and other bulk CSV endpoints that use the same helper). Refs #70

### Security
- **HTTP Error Payload & Binary Path Redaction** (#97) - Expanded API-key redaction beyond traceback cause suppression:
  - Redact reflected keys in HTTP error detail payloads (query-string, percent-encoded, nested JSON, and known key names)
  - Route binary (`response_model is bytes`) status failures through the same typed FMP error mapper
  - Safely decode non-UTF-8 error bodies, redact 429 bodies before rate-limiter logging, and keep mapped 5xx `FMPError`s retryable
  - Added regression coverage for sync/async binary paths, non-UTF-8 bodies, and message embedding of error details

### Changed
- **Dependency Refresh** (#105) - Raised GitHub Actions and Python package floors to current stable releases:
  - Actions: `checkout` 7, `setup-python` 6.3, `setup-uv` 8.3.2, `cache` 6.1, `codecov-action` 7, and related workflow pins
  - Python: pydantic 2.13, redis 8 (cache-redis extra), mypy 2.x, rich 15, langchain/openai/mcp stack bumps, ruff/pytest/nox updates
  - Set mypy `python_version` to 3.12 for numpy 2.x stubs while keeping runtime support on 3.10+

## [2.1.0] - 2026-01-23

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v2.0.0...v2.1.0)

### Added
- **New Centralized Exception Classes** - Added 4 new exception types to improve error handling:
  - `InvalidSymbolError(ValidationError)` - For missing or blank required symbols
  - `InvalidResponseTypeError(FMPError)` - For unexpected API response types with detailed type information
  - `DependencyError(ConfigError)` - For missing optional dependencies with installation instructions
  - `FMPNotFound(FMPError)` - For symbol/resource not found errors
- **Enhanced Error Messages** - All new exceptions provide clear, actionable error messages with context
- **Comprehensive Test Coverage** - Added 15 new test methods for exception hierarchy and behavior

### Fixed
- **Exception Handling Consistency** (21 issues resolved):
  - Centralized all local exception classes to `fmp_data/exceptions.py`
  - Fixed overly broad exception handling in `AsyncInvestmentClient.get_etf_info()` to catch specific errors
  - Added validation error handling in `AsyncBatchClient.get_dcf_bulk()` with proper row-level error logging
  - Replaced generic `ValueError`/`TypeError` with specific exception types across company and batch clients
  - Updated MCP modules to use `DependencyError` with installation instructions
- **Security** - Fixed API key exposure in integration test logging by redacting sensitive URL params and headers
- **Code Quality**:
  - Added return type annotations (`-> None`) to all 11 example `main()` functions and test helper functions
  - Fixed test lambda parameters to use underscore for unused arguments
  - Created custom `ModuleLoadError` exception for test module loading failures
  - Improved logger usage patterns across modules
- **Documentation** - Fixed Markdown formatting in API endpoint counts (changed `**N endpoints**` to `### N endpoints`)
- **429 Retry Handling** - Now respects `retry_after` wait times to avoid premature retries

### Changed
- **Improved Exception Hierarchy**: Removed local exception classes from individual modules - all exceptions now centralized in `fmp_data.exceptions`
- All custom exceptions properly inherit from `FMPError` base class
- **Better Validation**: Async batch client now validates and logs individual row errors instead of failing entire requests

## [2.0.0] - 2026-01-19

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v1.0.1...v2.0.0)

### Added
- **New Modules** - 4 new client modules with 32 new endpoints:
  - `batch/` - Batch data endpoints (12 endpoints)
    - Batch quotes for multiple symbols
    - Aftermarket trades and quotes
    - Exchange-wide stock quotes
    - Batch quotes for mutual funds, ETFs, commodities, crypto, forex, and indices
    - Batch market capitalization
  - `transcripts/` - Earnings call transcripts (4 endpoints)
    - Latest transcripts feed
    - Transcripts by symbol, year, and quarter
    - Available transcript dates
    - Symbols with available transcripts
  - `sec/` - SEC filing and company data (10 endpoints)
    - Latest 8-K and financial filings
    - Filing search by form type, symbol, or CIK
    - Company search by name, symbol, or CIK
    - SEC company profiles
    - Standard Industrial Classification (SIC) codes
  - `index/` - Market index constituents (6 endpoints)
    - S&P 500, NASDAQ, and Dow Jones constituents
    - Historical constituent changes for all three indices
- **Python 3.14 Support** - Full support for Python 3.14
- **New Tests** - 76 new unit tests for:
  - `@deprecated` decorator
  - Exception hierarchy
  - All new modules (batch, transcripts, sec, index)

### Fixed
- **Critical Bug Fixes**:
  - Fixed OpenAI embedding parameter bug (`openai_api_base` → `api_key`)
  - Fixed `FMPVectorStore` export (corrected to `EndpointVectorStore`)
  - Fixed MCP install hint (`[mcp-server]` → `[mcp]`)
  - Fixed retry configuration being ignored - now uses configurable `max_retries`
  - Fixed `_handle_rate_limit` not being called in request flow
  - Fixed vector store security issue - made `allow_dangerous_deserialization` opt-in with warning
  - Fixed `CompanyProfile` model validation errors by making optional fields nullable (e.g., `dcf`, `cik`, `isin`, etc.)

### Changed
- **Code Quality Improvements**:
  - Refactored `TechnicalClient` with generic `_get_indicator` helper (reduces code duplication)
  - Extracted `_build_date_params` helper in `MarketIntelligenceClient`
  - Refactored `BaseClient._process_response()` into smaller helper methods
  - Improved LangChain exception handling with specific exception types
- **Dependencies Updated**:
  - `pydantic` ≥ 2.12.5
  - `pydantic-settings` ≥ 2.12.0
  - `python-dotenv` ≥ 1.2.1
  - `langchain-core` ≥ 1.2.7
  - `langchain-openai` ≥ 1.1.7
  - `langgraph` ≥ 1.0.6
  - `openai` ≥ 2.15.0
  - `tiktoken` ≥ 0.12.0
  - `faiss-cpu` ≥ 1.13.2
  - `mcp` ≥ 1.25.0
  - `pyyaml` ≥ 6.0.3

### Removed
- Removed unused dependencies: `cachetools`, `structlog`, `pandas`, `tqdm`
- Removed `black` dependency (replaced by `ruff format`)

### Breaking Changes
- **LangChain v1 Requirement**: LangChain integration now requires LangChain v1 packages (`langchain-core`, `langchain-openai`) and LangGraph v1.
- **Vector Store Security**: `EndpointVectorStore.load()` now requires `allow_dangerous_deserialization=True` to load cached stores. This is a security improvement to prevent arbitrary code execution from untrusted cache sources.

  **Migration steps:**
  ```python
  # Old (pre-2.0.0)
  vector_store = EndpointVectorStore.load(cache_dir)

  # New (2.0.0+)
  vector_store = EndpointVectorStore.load(
      cache_dir,
      allow_dangerous_deserialization=True,  # Only if you trust the cache source
  )
  ```

## [1.0.1] - 2025-08-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v1.0.0...v1.0.1)

### Fixed
- Fixed CI/CD workflow issues with uv package installation
- Added --system flag to uv pip install commands in GitHub Actions
- Removed unnecessary uv run prefix from build commands

## [1.0.0] - 2025-08-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.2...v1.0.0)

### Added
- Production-ready release with stable API
- Comprehensive GitHub Actions CI/CD pipeline
- Automated versioning with semantic release labels
- TestPyPI deployment for dev branch updates
- Test coverage exceeding 80% threshold for core modules

### Fixed
- Corrected field aliases in fundamental models (stockPrice)
- Fixed primitive type handling in base client
- Updated Alternative Markets endpoints to use /stable/ prefix
- Resolved isinstance() syntax for Python 3.10+ compatibility
- Fixed millisecond timestamp detection in alternative models

### Changed
- Migrated to UV package manager for faster dependency resolution
- Updated development status to Production/Stable
- Streamlined CI/CD workflows for automated releases
- Enhanced error handling and validation

### Breaking Changes
- **`get_quote` method relocation**: The `get_quote` method has been moved from `MarketClient` to `CompanyClient`

  **Migration steps:**
  ```python
  # Old (pre-1.0.0)
  quote = client.market.get_quote("AAPL")

  # New (1.0.0+)
  quote = client.company.get_quote("AAPL")
  ```

  **Rationale:** This change better aligns with the FMP API structure where company quotes are part of the company data domain.

- **Alternative Markets endpoint prefix change**: All Alternative Markets endpoints now use `/stable/` prefix instead of `/v3/`

  **Migration steps:**
  - No code changes required for users of the client library
  - Direct API users should update endpoint URLs from `/v3/` to `/stable/`

### Removed
- Removed deprecated sync_groups.py script
- Cleaned up duplicate dependency definitions

## [0.5.2] - 2025-07-04

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.1...v0.5.2)

### Fixed
- Resolved dynamic versioning issues with hatch-vcs
- Fixed CI/CD pipeline Poetry installation errors

## [0.5.1] - 2025-07-02

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.5.0...v0.5.1)

### Fixed
- Patched versioning configuration for proper PyPI releases
- Corrected build system requirements

## [0.5.0] - 2025-07-02

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.4.0...v0.5.0)

### Added
- MCP (Model Context Protocol) server implementation
- FastMCP integration for AI assistant compatibility
- Configurable tool manifest system

## [0.4.0] - 2025-01-07

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.0...v0.4.0)

### Added
- MCP (Model Context Protocol) Server Support
  - FastMCP-based server implementation for exposing FMP data through standardized protocol
  - Configurable tool manifest system for customizing available endpoints
  - Environment variable configuration support (`FMP_MCP_MANIFEST`)
  - Default tool set covering major FMP endpoints (company, market, fundamental, technical)
  - Tool naming convention: `<client>.<semantics_key>` (e.g., `company.profile`, `market.quote`)
  - Seamless integration with MCP-compatible AI assistants

### Improved
- Enhanced installation options with MCP extras support
- Streamlined configuration for multiple integration types
- Better separation of concerns between client, LangChain, and MCP modules
- **UV-focused development workflow** with comprehensive setup instructions
- Enhanced contributor guidelines with UV-specific commands and quality checks

### Changed
- Updated documentation with MCP server usage examples
- Refined feature list presentation for better readability
- Consolidated integration patterns across different use cases
- **Transitioned to UV as the primary package management tool** with detailed setup guides

### Breaking Changes
- **Breaking:** `get_quote` has moved from `MarketClient` to `CompanyClient`
  - Update: `client.market.get_quote()` → `client.company.get_quote()`

## [0.3.4] - 2025-01-06

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.3...v0.3.4)

### Fixed
- Minor bug fixes and performance improvements

## [0.3.3] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.2...v0.3.3)

### Fixed
- API response handling improvements

## [0.3.2] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.1...v0.3.2)

### Fixed
- Enhanced error handling for edge cases

## [0.3.1] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.3.0...v0.3.1)

### Fixed
- LangChain integration compatibility issues

## [0.3.0] - 2025-01-05

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.2.0...v0.3.0)

### Added
- LangChain Integration
  - New capability to convert Financial Modeling Prep (FMP) endpoints to LangChain Structured Tools
  - Dynamic endpoint discovery for query-based tool selection
  - Flexible tool retrieval mechanism allowing users to:
    - Send a query
    - Retrieve top_n most relevant FMP endpoints
    - Generate Structured Tools compatible with any LLM
  - Enhanced query routing and tool selection system

### Improved
- Query processing capabilities
- Endpoint selection intelligence
- Flexibility in financial data retrieval

## [0.2.0] - 2024-12-11

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1.2...v0.2.0)

### Added
- Full coverage of Financial Modeling Prep (FMP) endpoints
- Comprehensive endpoint mapping
- Robust error handling for API interactions

## [0.1.2] - 2024-12-10

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1.1...v0.1.2)

### Fixed
- Package distribution issues
- Dependency resolution conflicts

## [0.1.1] - 2024-12-09

[Compare changes](https://github.com/MehdiZare/fmp-data/compare/v0.1-beta.1...v0.1.1)

### Fixed
- Initial bug fixes post-beta release

## [0.1-beta.1] - 2024-12-08

### Added
- Initial project setup
- Basic API interaction framework
- Preliminary endpoint support

## Future Roadmap
- Advanced machine learning-driven endpoint recommendations
- Enhanced query prediction capabilities
- Additional financial data source integrations
- Expanded tool support across different protocols
- Performance optimizations for large-scale deployments

## Contribution Guidelines
- Follow semantic versioning
- Maintain comprehensive test coverage
- Document significant architectural changes
- Ensure backward compatibility
