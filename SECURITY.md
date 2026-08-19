# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| Latest release on PyPI | Yes |
| `dev` branch | Yes (pre-release) |
| Older PyPI releases | Best effort; please upgrade |

## Reporting a vulnerability

Do **not** open a public GitHub issue for a security report.

Use GitHub's private advisory form:

https://github.com/MehdiZare/fmp-data/security/advisories/new

Include the affected version or commit, a reproduction, and impact. You should
hear back within 7 days. A fix, workaround, or reasoned decline will be
published once we have one; we aim for 30 days on confirmed issues in the
supported line.

This project is a client library. Most reports will be hardening
(credential handling, CI, optional extras) rather than remotely exploitable
flaws in default HTTPS use.
