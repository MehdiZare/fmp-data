# Remaining `httpx.RequestError` leftovers must not leak `apikey`

**Date:** 2026-08-19
**Base:** `origin/dev` @ `f712a4d`
**Issue:** #354
**Status:** approved (fold leftovers into `FMPNetworkError`; retry Protocol/Proxy only)

## Problem

#350 / PR #353 maps `httpx.TimeoutException` → `FMPTimeoutError` and
`httpx.NetworkError` → `FMPNetworkError` with `raise … from None`. Other
`httpx.RequestError` subclasses still hit `_handle_execute_failure`'s
generic logger (`str(exc)` + `exc_info=True`) and re-raise raw httpx.
httpx stringifies `request.url`, which carries `apikey=`.

Leftovers on httpx 0.28:

- `ProtocolError` / `ProxyError` / `UnsupportedProtocol` (`TransportError`)
- `DecodingError` / `TooManyRedirects` (`RequestError`, not `TransportError`)
- any future `RequestError` that is not a timeout or `NetworkError`

`HTTPStatusError` stays on the #97 path.

## Decisions

| Fork | Choice |
|---|---|
| Packaging | Isolated PR; #352 is a follow-up |
| Types | Fold leftovers into `FMPNetworkError` |
| Retry | `ProtocolError` / `ProxyError` retryable; other leftovers `retryable=False` |
| Helper export | None (`raise_secret_safe` stays out of scope) |

## Design

### Mapping

In `_reraise_transport_failure`, after the existing timeout / network
arms, map leftover `httpx.RequestError` with fixed log lines and
`raise … from None` **before** the generic logger.

| httpx type | message | `FMPNetworkError.retryable` |
|---|---|---|
| `TimeoutException` | `Request timed out` | n/a (`FMPTimeoutError`) |
| `NetworkError` | `Network error` | `True` (default) |
| `ProtocolError` | `Protocol error` | `True` |
| `ProxyError` | `Proxy error` | `True` |
| other `RequestError` | `Transport error` | `False` |

`_handle_execute_failure` widens its gate from
`TimeoutException | NetworkError` to `RequestError`.

### Retry

`_is_retryable_error` uses `FMPNetworkError.retryable` instead of
`isinstance(..., FMPNetworkError)`. Raw httpx defense in depth also
retries `ProtocolError` / `ProxyError`.

### First-party catcher

`validate_api_key` already maps `FMPNetworkError` → `unavailable`.
Widen that arm to `FMPNetworkError | httpx.RequestError` so leftover
fakes/adapters cannot fall through to a valid-key report.
`TimeoutException` stays in the earlier timeout arm.

## Non-goals

- Public `raise_secret_safe` / exporting `_redaction`
- `#352` Structure export
- New `FMPTransportError` parent
