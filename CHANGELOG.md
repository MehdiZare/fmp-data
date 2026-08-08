# Changelog

All notable changes to the package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed
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

### Deprecated
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
- **Bare-key resolution for tool keys claimed by two clients** (#126) - `register_from_manifest` accepts a bare tool key (`profile`) as well as the fully qualified spec (`company.profile`), resolving it through `_build_key_to_spec`, which indexes the whole discovery catalogue rather than `DEFAULT_TOOLS`. `crypto_quotes` and `forex_quotes` are each claimed by two clients (`alternative` and `batch`), so the bare form failed with a bare `RuntimeError: Tool key 'crypto_quotes' is ambiguous` that named neither candidate.
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
  - Not addressed here: teaching the LangChain tool layer to dispatch through client methods rather than `client.request`, so wrappers carrying real logic become reachable. That is the general form of the problem and needs its own design pass

### Fixed
- **Deprecated endpoints are no longer selectable through the LangChain vector store** (#137) - `intelligence.stock_news_sentiments`, `earnings_confirmed` and `earnings_surprises` return `[]` without calling upstream, but stayed indexed, so a semantic query could pick one and the LLM got an empty *success* — indistinguishable from "no data matched your query". `EndpointSemantics` gains `deprecated: bool = False`; the three are marked, and `EndpointVectorStore` filters on it.
  - Filtering happens **both** at index time (`add_endpoint`, `add_endpoints`) and at selection time (`search`, `get_tools`). Index-time alone would leave anyone with a store persisted by an earlier release exactly where this issue found them, since the deprecated endpoints are already baked into that index
  - **`search` widens its fetch rather than shrinking its answer.** On exactly that stale index, a deprecated hit occupies a slot in the top-`k` window, so filtering after the fetch would return two live endpoints for `k=3` and say nothing about it — under-recall in place of a dead endpoint. `search` now refetches with a doubled window while filtered-out entries are still displacing live ones (three rounds, stopping early once `k` results are live or the index is exhausted) and truncates to `k`. Results are still capped at `k`; unknown endpoint names in a stale index are recovered from the same way. Hits below `threshold` do not trigger a refetch — that is a genuine relevance cut, and widening would only surface worse matches
  - `add_endpoints` returns the number of endpoints it actually indexed. `create_new_store` logged `len(endpoint_names)`, the count it *offered*, which overstated the store by however many the filter had just dropped (215 offered, 212 indexed)
  - **The entries are not deleted, and the MCP catalog does not move** — still 223 tools, with all three keys resolvable through an explicit manifest. MCP reads the `*_ENDPOINTS_SEMANTICS` tables directly and never consults the vector store, so it is unaffected. Deleting the keys outright would remove public tool keys with no deprecation window
  - `add_endpoints` counts and logs deprecated exclusions separately from `skipped_endpoints`: being deprecated is a deliberate exclusion at `INFO`, not a defect worth a `WARNING`
  - **This is a different mechanism from `fmp_data.mcp.tools_manifest.DEPRECATED_TOOLS`** (#136), and the two must not be merged. That table maps a duplicate tool *name* onto the canonical name of a method that still works — resolve one and you get live data plus a rename warning. This flag says the endpoint itself returns nothing, whatever name you reach it by, so the fix is to stop advertising it rather than to rename it. The distinction is written into both `EndpointSemantics.deprecated` and `DEPRECATED_TOOLS`, and a test asserts the two sets stay disjoint. That test lives in `tests/unit/test_mcp.py`, the only file the `mcp-server` CI job runs: it needs the `mcp` extra, and beside the other #137 tests in `tests/unit/lc/` — skipped without `langchain`, which no `mcp` job installs — it would never have executed anywhere. Which endpoints carry the flag is likewise pinned in a top-level `tests/unit/test_deprecated_endpoint_flags.py`, so the accidental-deprecation guard runs in the default no-extras matrix rather than only in the `langchain` job
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
- **MCP bare-key resolution was implemented three times and could drift** (#149) - the rule "a bare tool key resolves only when exactly one client claims it" lived in `tool_loader._resolve_tool_spec` (the resolver registration uses), in `cli._classify_manifest_entries` (`fmp-mcp validate`'s copy) and again in the example-manifest guard test. They agreed, but nothing kept them agreeing, and validator drift is the bad case: a `validate` that blesses manifests the loader then refuses turns a startup error into a trusted green check.
  - Resolution is now split from announcement. The new pure `fmp_data.mcp.tool_loader.resolve_tool_spec(spec, key_to_spec) -> Resolution` decides; it warns nothing, logs nothing and raises nothing, which is why `validate` could not call the old resolver — looping over entries would have sprayed `DeprecationWarning`s for keys the user is merely checking. `_warn_if_deprecated` is now called only by `_resolve_tool_spec`, i.e. only on the registration path
  - `Resolution` is a frozen dataclass carrying `entry`, a `ResolutionStatus` (`RESOLVED`, `DEPRECATED`, `AMBIGUOUS`, `UNKNOWN`), the resolved `spec`/`client`/`key`, the `replacement` for a deprecated spec, every `candidates` entry for an ambiguous key, and the `message` explaining a failure — not a bare tuple callers must remember how to unpack. `is_resolved` covers `RESOLVED` and `DEPRECATED` (a deprecated key still registers until 3.0); `require()` returns the `(spec, client, key)` triple or raises `message`
  - `_resolve_tool_spec` is now a four-line wrapper over the pure function, so `validate`, the loader and the example-manifest guards share one implementation and reimplementing the rule breaks a test rather than silently diverging
  - **Behaviour change:** a fully qualified spec is now checked against the catalog. `company.profil` fails at resolution with `Tool key 'company.profil' not found in available tools` instead of being trusted through to a confusing `Endpoint semantics 'profil' not found` from `_load_semantics`. Bare keys already behaved this way; the two forms now answer to the same authority
  - New guards: the pure resolver must stay silent (no `DeprecationWarning`, no log record) on a deprecated spec; the loader's decision must match the pure resolver's for every spec and every bare key in the catalog plus known-bad entries; `validate`'s classification must match it over the same set; and stubbing `resolve_tool_spec` must change what `validate` reports, which fails if `cli.py` ever grows its own copy again
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
