# Claude Code Review (advisory)

This repository runs [Claude Code Review](https://github.com/anthropics/claude-code-action)
on pull requests via `.github/workflows/claude-code-review.yml`.

## Status

- **Advisory only.** Required product checks live in `ci.yml`. A failed or
  skipped Claude review must never block merge.
- The job **does not start** when `CLAUDE_CODE_OAUTH_TOKEN` is empty
  (`if: secrets.CLAUDE_CODE_OAUTH_TOKEN != ''`), so missing configuration is
  a no-op rather than a red X (#184 / #185).
- When the secret is present but the review step fails (expired token,
  plugin error, outage), the step uses `continue-on-error: true` and a
  follow-up step writes a **job summary** so the failure is visible (#187).

## Restore / rotate the OAuth token

1. On a maintainer machine with the Claude Code CLI, create a fresh token
   (typically `claude setup-token`, or the flow documented for
   [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action)).
2. GitHub → repository **Settings → Secrets and variables → Actions**.
3. Update `CLAUDE_CODE_OAUTH_TOKEN` with the new value (never commit it).
4. Open or re-run the workflow on any same-repo PR and confirm a review
   comment appears.

## When soft-fail fires

Open the **Claude Code Review** workflow run → **Summary**. The soft-failure
step lists likely causes and the restore steps above. Fix the secret or the
action config; do not make the check required.
