#!/usr/bin/env bash
# Fail-closed REST mergeability poll for a single PR.
# Invoked by .github/actions/check-pr-mergeable (see #202, #207, #210, #216, #217).
#
# Required env:
#   GH_TOKEN, PR_NUMBER, REPO
# Optional env:
#   MAX_ATTEMPTS (default 6), SLEEP_SECONDS (default 5)
#   API_MAX_RETRIES (default 3) — max gh api attempts per poll for transient failures
#   CONFLICT_GUIDANCE — extra operator lines on dirty (workflow-specific)
#   GITHUB_OUTPUT, GITHUB_STEP_SUMMARY (set by Actions)
set -euo pipefail

ACTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Single shared jq program used by check.sh and the mock matrix (#223).
MERGEABLE_JQ="${ACTION_DIR}/mergeable.jq"
if [ ! -f "$MERGEABLE_JQ" ]; then
  echo "::error::missing shared jq extraction program: ${MERGEABLE_JQ}"
  exit 1
fi
MERGEABLE_JQ_PROG="$(cat "$MERGEABLE_JQ")"

PR_NUMBER="${PR_NUMBER:?PR_NUMBER is required}"
REPO="${REPO:?REPO is required}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-6}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"
API_MAX_RETRIES="${API_MAX_RETRIES:-3}"  # max gh api attempts per poll (not "retries after first")
CONFLICT_GUIDANCE="${CONFLICT_GUIDANCE:-}"

if ! [[ "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
  echo "::error::max-attempts must be a positive integer (got: ${MAX_ATTEMPTS})"
  exit 1
fi
if ! [[ "$SLEEP_SECONDS" =~ ^[0-9]+$ ]]; then
  echo "::error::sleep-seconds must be a non-negative integer (got: ${SLEEP_SECONDS})"
  exit 1
fi
if ! [[ "$API_MAX_RETRIES" =~ ^[1-9][0-9]*$ ]]; then
  echo "::error::api-max-retries must be a positive integer (got: ${API_MAX_RETRIES})"
  exit 1
fi

write_outputs() {
  local mergeable="$1"
  local mstate="$2"
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    {
      echo "mergeable=${mergeable}"
      echo "mergeable_state=${mstate}"
    } >>"$GITHUB_OUTPUT"
  fi
}

write_summary() {
  local status_line="$1"
  local mergeable="$2"
  local mstate="$3"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    {
      echo "## PR mergeability"
      echo ""
      echo "- PR: \`#${PR_NUMBER}\` (\`${REPO}\`)"
      echo "- mergeable: \`${mergeable}\`"
      echo "- mergeable_state: \`${mstate}\`"
      echo "- result: ${status_line}"
    } >>"$GITHUB_STEP_SUMMARY"
  fi
}

# Permanent API failures must fail closed immediately (no retry storm on bad
# token / missing PR). Transient 5xx / rate-limit / transport blips may retry
# within API_MAX_RETRIES (#217). Success criteria still require mergeable=true.
#
# Exhausting API_MAX_RETRIES aborts the whole step (does not consume further
# MAX_ATTEMPTS unknown-poll budget) — fail closed when we cannot talk to the API.
is_rate_limit_gh_error() {
  local err="$1"
  # Primary + secondary rate limits (often HTTP 403 with rate-limit wording).
  # Real authz 403s do not include these phrases and stay permanent (#223).
  if echo "$err" | grep -Eqi \
    'secondary rate limit|exceeded a secondary rate|API rate limit exceeded|rate limit exceeded|x-ratelimit-remaining'; then
    return 0
  fi
  return 1
}

is_transient_gh_error() {
  local err="$1"
  if is_rate_limit_gh_error "$err"; then
    return 0
  fi
  # gh prints "HTTP NNN:" for API status errors; match common transient codes.
  if echo "$err" | grep -Eqi 'HTTP[[:space:]]+(408|425|429|500|502|503|504)\b'; then
    return 0
  fi
  # Transport / client blips (no durable authorization or not-found signal).
  if echo "$err" | grep -Eqi \
    'connection (reset|refused|timed out)|tls handshake|i/o timeout|temporary failure|network is unreachable|EOF|broken pipe|dial tcp'; then
    return 0
  fi
  return 1
}

is_permanent_gh_error() {
  local err="$1"
  # Rate limits are 403-shaped but transient — not permanent (#217 / #223).
  if is_rate_limit_gh_error "$err"; then
    return 1
  fi
  if echo "$err" | grep -Eqi 'HTTP[[:space:]]+(401|403|404|410|422)\b'; then
    return 0
  fi
  return 1
}

# Fetch mergeable\tmstate into STATE. Retries only transient gh failures.
# Returns 0 on success; 1 after permanent error or exhausted transient retries.
# On failure the caller must exit the step (API exhaustion aborts the check).
fetch_state() {
  local api_try=1
  local gh_err_file gh_err backoff
  while [ "$api_try" -le "$API_MAX_RETRIES" ]; do
    gh_err_file=$(mktemp)
    # Explicit tostring keeps operators/logs/mocks 1:1 with JSON null (#216).
    # mergeable_state null → "unknown" so we stay on the unresolved retry path
    # (fail closed). A literal "null" token would otherwise hit *) and could go
    # green when mergeable=true (#216 follow-up).
    if STATE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}" \
      --jq "$MERGEABLE_JQ_PROG" \
      2>"$gh_err_file"); then
      rm -f "$gh_err_file"
      return 0
    fi
    gh_err=$(cat "$gh_err_file" 2>/dev/null || true)
    rm -f "$gh_err_file"

    if is_permanent_gh_error "$gh_err"; then
      echo "::error::gh api failed for PR #${PR_NUMBER} in ${REPO} (permanent error; not retrying)."
      if [ -n "$gh_err" ]; then
        echo "$gh_err"
      fi
      return 1
    fi

    if ! is_transient_gh_error "$gh_err"; then
      # Unknown shape: fail closed without retrying (safer than infinite hope).
      echo "::error::gh api failed for PR #${PR_NUMBER} in ${REPO} (cannot evaluate mergeability)."
      if [ -n "$gh_err" ]; then
        echo "$gh_err"
      fi
      return 1
    fi

    if [ "$api_try" -eq "$API_MAX_RETRIES" ]; then
      echo "::error::gh api failed for PR #${PR_NUMBER} in ${REPO} after ${API_MAX_RETRIES} attempt(s) (transient errors exhausted)."
      if [ -n "$gh_err" ]; then
        echo "$gh_err"
      fi
      return 1
    fi

    # Bounded linear backoff: SLEEP_SECONDS * attempt (0 when sleep is 0 for tests).
    backoff=$((SLEEP_SECONDS * api_try))
    echo "Transient gh api error (attempt ${api_try}/${API_MAX_RETRIES}); retrying in ${backoff}s..."
    if [ -n "$gh_err" ]; then
      echo "$gh_err"
    fi
    sleep "$backoff"
    api_try=$((api_try + 1))
  done
  return 1
}

# GitHub computes mergeability asynchronously; unknown is common for a few
# seconds after open/sync. Retry before deciding.
attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
  # mergeable: true | false | null  (REST JSON; extracted via tostring so JSON
  # null is the literal token "null", not an empty TSV field — #216)
  # mergeable_state: clean | dirty | unstable | blocked | unknown | ...
  if ! fetch_state; then
    write_outputs "null" "api_error"
    write_summary "failed (gh api error)" "null" "api_error"
    exit 1
  fi
  MERGEABLE=$(echo "$STATE" | cut -f1)
  MSTATE=$(echo "$STATE" | cut -f2)
  echo "Attempt ${attempt}/${MAX_ATTEMPTS}: PR #${PR_NUMBER} mergeable=${MERGEABLE} mergeable_state=${MSTATE}"

  case "$MSTATE" in
    dirty)
      echo "::error::PR #${PR_NUMBER} has merge conflicts (mergeable_state=dirty)."
      echo "A conflicting PR has no merge ref, so other checks may never appear."
      echo "Resolve conflicts (merge or rebase the head onto the base), then re-push."
      echo "If this is a release PR after a squash, merge the Sync-Main-to-Dev"
      echo "reachability PR first (#202)."
      if [ -n "$CONFLICT_GUIDANCE" ]; then
        # shellcheck disable=SC2001
        echo "$CONFLICT_GUIDANCE" | sed 's/^/  /'
      fi
      write_outputs "$MERGEABLE" "$MSTATE"
      write_summary "failed (dirty)" "$MERGEABLE" "$MSTATE"
      exit 1
      ;;
    # "null" is defense-in-depth: production jq maps JSON null → "unknown"
    # (#216), but if extraction ever emits the literal token, treat it as
    # unresolved rather than falling through to *) and going green when
    # mergeable=true.
    unknown | "" | null)
      if [ "$MERGEABLE" = "false" ]; then
        echo "::error::PR #${PR_NUMBER} is not mergeable."
        write_outputs "$MERGEABLE" "${MSTATE:-unknown}"
        write_summary "failed (mergeable=false)" "$MERGEABLE" "${MSTATE:-unknown}"
        exit 1
      fi
      if [ "$attempt" -eq "$MAX_ATTEMPTS" ]; then
        break
      fi
      sleep "$SLEEP_SECONDS"
      attempt=$((attempt + 1))
      continue
      ;;
    *)
      # Success requires mergeable=true (not merely not-false). JSON null is
      # the literal token "null" after tostring extraction; empty is defensive
      # only. Fail closed rather than paint green without proof (#213, #216).
      if [ "$MERGEABLE" != "true" ]; then
        if [ "$MERGEABLE" = "false" ]; then
          echo "::error::PR #${PR_NUMBER} is not mergeable (mergeable_state=${MSTATE})."
          write_outputs "$MERGEABLE" "$MSTATE"
          write_summary "failed (mergeable=false, state=${MSTATE})" "$MERGEABLE" "$MSTATE"
        else
          # "null" is the real JSON-null encoding after tostring (#216); empty
          # or any other non-true token is also refuse-green (defensive, #213).
          echo "::error::PR #${PR_NUMBER} mergeable='${MERGEABLE:-}' (not true) with mergeable_state=${MSTATE}; refusing green without mergeable=true (#213)."
          write_outputs "${MERGEABLE:-null}" "$MSTATE"
          write_summary "failed (mergeable not true, state=${MSTATE})" "${MERGEABLE:-null}" "$MSTATE"
        fi
        exit 1
      fi
      echo "✅ PR #${PR_NUMBER} is mergeable (mergeable=${MERGEABLE}, mergeable_state=${MSTATE})"
      write_outputs "$MERGEABLE" "$MSTATE"
      write_summary "ok (mergeable=true)" "$MERGEABLE" "$MSTATE"
      exit 0
      ;;
  esac
done

# Fail closed: if mergeability never resolved to a non-unknown state with
# mergeable=true, we cannot prove the PR is mergeable. Exiting 0 here would
# reintroduce a green check while merge-ref-based jobs may still be absent —
# the same hole this step exists to close. See #202 / #207 / #210 / #213.
echo "::error::PR #${PR_NUMBER} mergeable_state still unknown after ${MAX_ATTEMPTS} attempt(s); refusing to report green."
echo "Re-run this check, or inspect PR #${PR_NUMBER} mergeability in the UI."
write_outputs "${MERGEABLE:-null}" "${MSTATE:-unknown}"
write_summary "failed (unknown after retries)" "${MERGEABLE:-null}" "${MSTATE:-unknown}"
exit 1
