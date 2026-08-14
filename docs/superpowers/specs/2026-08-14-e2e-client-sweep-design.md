# E2E client-method sweep

**Date:** 2026-08-14
**Base:** `dev`
**Status:** approved (approach B)

## Problem

Two existing layers almost cover "is this package ready?" and both miss
the thing we actually ship:

- `tests/e2e/test_live_signatures.py` probes every `Endpoint` declaration
  against the live API. It never goes through `FMPDataClient`, never
  parses models, and has no VCR. A passing run can still leave a broken
  client method.
- `tests/integration/` calls real client methods under VCR, but only the
  methods someone wrote by hand. Cassettes are gitignored.

A dead path, a wrong unwrap, or a Pydantic schema that no longer matches
the wire can therefore reach a release.

## Goal

A **local, opt-in harness** that calls every public **sync** client
method through `FMPDataClient`, records the HTTP traffic with VCR, and
reports per-method pass / empty / error. Maintainers record once (or
one group / one method), then replay while fixing models and paths
without spending quota.

This is not CI. Default `make test` / `pytest` must not run it.

## Non-goals

- Async client sweep (same models; doubles cost). Add later if needed.
- Replacing handwritten integration tests or the live signature probe.
- Committing cassettes (large, secret-sensitive; same policy as
  `tests/integration/vcr_cassettes/`).
- Rich field-by-field assertions. Those stay in `tests/integration/`.

## Design

### Discovery

Walk `FMPDataClient` group properties (`company`, `market`, …) and
collect every public method on the sync client class. A method is a
sweep case. Deprecated methods (`__fmp_deprecated__`) are listed and
skipped. Private helpers (`_unwrap_*`, `_format_date`, …) are ignored.

Endpoint maps are attached when present, for the report (`path`,
`version`). They are **not** the source of cases: the public client is
what callers use, and several live methods are not in a map.

### Samples

Required method parameters are filled from a name-based sample table
(symbol, cik, dates, …). Optional date parameters are also filled with
**anchored** dates so VCR query strings stay stable (`date.today()`
inside SEC search is the failure mode this prevents).

Inferences:

- method name contains `etf` → `SPY`
- `mutual_fund` / fund-disclosure → `VTSAX`
- `crypto` → `BTCUSD`
- `forex` → `EURUSD`
- `commodity` → `GCUSD`
- `symbols` (batch) → `["AAPL", "MSFT"]`
- economic `indicator_name` → `GDP`
- senate / house `name` → `Nancy Pelosi`

Bulk CSV methods (`*_bulk` on `batch`) run by default and can be
skipped with `--skip-bulk`. `company.get_company_logo_url` is local
(no HTTP) and is invoked without a cassette.

### VCR

Reuse the integration sanitizers (API key scrub, 401 drop, safe
persister). Cassettes live in `tests/e2e/vcr_cassettes/{group}/{method}.yaml`
and are gitignored.

| Command | Record mode |
|---|---|
| `record` | `new_episodes` |
| `record --refresh` | `all` |
| `replay` | `none` |

Replay of a missing cassette is an error for that case, not a live call.

### Assertions

A case **ok**s when the method returns without raising and the payload
is non-empty (list/bytes/string length, or a model instance). Empty
success is `empty` (fail unless the method is on an allowlist of
entity-sensitive endpoints). Any exception is `error`. Deprecated is
`skip`.

Validation mode defaults to the package default (`warn`). `--strict`
sets `FMP_VALIDATION_MODE=strict` so extra/missing fields fail loudly.

### Entry points

```text
uv run python scripts/e2e_endpoints.py list
uv run python scripts/e2e_endpoints.py record [--group G] [--method M] [--refresh]
uv run python scripts/e2e_endpoints.py replay [--group G] [--method M]
make e2e-record
make e2e-replay
```

A pytest module `tests/e2e/test_client_sweep.py` marked `e2e` wraps
replay so it can be invoked as pytest. `addopts` deselects `e2e` the
same way it already deselects `live`.

The report is JSON + a table on stdout:
`tests/e2e/reports/last-report.json` (gitignored).

## Layout

| Path | Role |
|---|---|
| `tests/e2e/harness.py` | discovery, samples, classify, run |
| `scripts/e2e_endpoints.py` | CLI |
| `tests/e2e/test_client_sweep.py` | optional pytest replay wrapper |
| `tests/unit/test_e2e_sweep.py` | unit tests (no network) |

## Quota

A full record is one request per public sync method (a few hundred),
plus retries on 429. Throttle ~200ms between live calls. Filter with
`--group` / `--method` when iterating on a fix.
