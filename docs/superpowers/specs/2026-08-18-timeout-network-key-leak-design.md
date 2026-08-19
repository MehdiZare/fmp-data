# Timeout / network httpx errors must not leak `apikey`

**Date:** 2026-08-18
**Base:** `origin/dev` @ `3f13902`
**Issue:** #350
**Status:** approved (two subclasses; no public redaction helper)

## Problem

`#94` / `#97` closed this for HTTP **status** errors: typed `FMPError`s
raise `from None`, so a 429/401 traceback no longer carries `apikey=`.

Timeouts and connect failures never reach `handle_response`. Sync and
async `_execute_request` still log `str(httpx_exc)` with `exc_info=True`
and re-raise the raw `httpx.TimeoutException` / `httpx.NetworkError`.
httpx puts the request URL on those objects; the key is a query param.
Sentry serialises `__cause__` / `.request.url`. `#94` only pinned 4xx/5xx.

`SecretStr` (#252) does not help: the key is still unwrapped into
`query_params["apikey"]` before the request.

## Goal

One PR that:

1. Maps `httpx.TimeoutException` → `FMPTimeoutError` and
   `httpx.NetworkError` → `FMPNetworkError` inside `_execute_request`
   / `_execute_request_async`, `raise … from None`.
2. Logs a fixed line (`"Request timed out"` / `"Network error"`) with
   `endpoint` extra only. No `str(httpx_exc)`, no `exc_info=True`.
3. Keeps those failures retryable.
4. Pins the secret is absent from `str(exc)`, `repr(exc.__cause__)`,
   `traceback.format_exc()`, and the error log. Sync and async.
5. Re-exports the new types from `fmp_data` next to `RateLimitError`.

## Non-goals

- Public `raise_secret_safe` / exporting `_redaction` (explicit A).
- bina-fmp / bina-capital#2610 (PR #2690 already open there).
- Other `httpx.RequestError`s (`ProtocolError`, `ProxyError`, …).
- `#352` Structure export (separate PR).

## Decisions

| Fork | Choice |
|---|---|
| Packaging | Isolated PR, then `#352` |
| Types | `FMPTimeoutError` and `FMPNetworkError` |
| Helper export | None |

## Design

### Types

In `fmp_data/exceptions.py`:

```python
class FMPTimeoutError(FMPError):
    """Raised when an FMP HTTP request times out."""

class FMPNetworkError(FMPError):
    """Raised when an FMP HTTP request fails at the transport layer."""
```

No `status_code`, no `response`. Import and list both in
`fmp_data/__init__.py` / `__all__`.

### Mapping

Catch **before** the generic `except Exception` logger, so tenacity
sees the typed error and `before_sleep_log` never prints a URL.

```python
except RateLimitError:
    raise
except httpx.TimeoutException:
    self.logger.error(
        "Request timed out",
        extra={"endpoint": endpoint.name},
    )
    raise FMPTimeoutError("Request timed out") from None
except httpx.NetworkError:
    self.logger.error(
        "Network error",
        extra={"endpoint": endpoint.name},
    )
    raise FMPNetworkError("Network error") from None
except Exception as e:
    ...
```

Same arms in the async twin.

### Retry

`_is_retryable_error` treats `FMPTimeoutError | FMPNetworkError` as
retryable. Keep the existing `httpx.TimeoutException | httpx.NetworkError`
arms as defense in depth.

### Tests

Same pin shape as `#97`:

- Build a `TimeoutException` / `ConnectError` whose `.request.url`
  contains `apikey=SECRET_…`
- Drive sync `request` / `_execute_request` and the async twins
- Assert type, `__cause__ is None`, `__suppress_context__`
- Assert the secret is in none of `str(exc)`, `repr(exc)`,
  `repr(exc.__cause__)`, `traceback.format_exc()`, or the error log
- Flip `test_request_max_retries_exceeded` and
  `test_metrics_callback_called_on_failure` to `FMPTimeoutError`
- Leave retry-then-success tests (they raise httpx from the mock;
  the client maps, then retries)
- Keep the `test_mcp_utils` fake that raises `httpx.TimeoutException`
  (adapters/fakes still use it)
- Also pin `FMPTimeoutError` → `timeout` and `FMPNetworkError` →
  `unavailable` in `validate_api_key`. Both are `FMPError` subclasses
  with `status_code is None`; the generic `except FMPError` branch
  would otherwise report a valid key.

### Changelog

Unreleased **Fixed**, `#97` voice: timeouts/network no longer leak
`apikey=` via URL / `__cause__` / logs; they raise `FMPTimeoutError`
/ `FMPNetworkError` instead of raw httpx.
