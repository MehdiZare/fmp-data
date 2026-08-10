#!/usr/bin/env bash
# Fail-closed REST mergeability poll for a single PR.
# Invoked by .github/actions/check-pr-mergeable (see #202, #207, #210).
#
# Required env:
#   GH_TOKEN, PR_NUMBER, REPO
# Optional env:
#   MAX_ATTEMPTS (default 6), SLEEP_SECONDS (default 5)
#   GITHUB_OUTPUT, GITHUB_STEP_SUMMARY (set by Actions)
set -euo pipefail

PR_NUMBER="${PR_NUMBER:?PR_NUMBER is required}"
REPO="${REPO:?REPO is required}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-6}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

if ! [[ "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
  echo "::error::max-attempts must be a positive integer (got: ${MAX_ATTEMPTS})"
  exit 1
fi
if ! [[ "$SLEEP_SECONDS" =~ ^[0-9]+$ ]]; then
  echo "::error::sleep-seconds must be a non-negative integer (got: ${SLEEP_SECONDS})"
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

# GitHub computes mergeability asynchronously; unknown is common for a few
# seconds after open/sync. Retry before deciding.
attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
  # mergeable: true | false | null
  # mergeable_state: clean | dirty | unstable | blocked | unknown | ...
  STATE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}" \
    --jq '[.mergeable, .mergeable_state] | @tsv')
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
      write_outputs "$MERGEABLE" "$MSTATE"
      write_summary "failed (dirty)" "$MERGEABLE" "$MSTATE"
      exit 1
      ;;
    unknown | "")
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
      if [ "$MERGEABLE" = "false" ]; then
        echo "::error::PR #${PR_NUMBER} is not mergeable (mergeable_state=${MSTATE})."
        write_outputs "$MERGEABLE" "$MSTATE"
        write_summary "failed (mergeable=false, state=${MSTATE})" "$MERGEABLE" "$MSTATE"
        exit 1
      fi
      echo "✅ PR #${PR_NUMBER} is not conflicting (mergeable=${MERGEABLE}, mergeable_state=${MSTATE})"
      write_outputs "$MERGEABLE" "$MSTATE"
      write_summary "ok (non-conflicting)" "$MERGEABLE" "$MSTATE"
      exit 0
      ;;
  esac
done

# Fail closed: if mergeability never resolved, we cannot prove the PR is
# non-conflicting. Exiting 0 here would reintroduce a green check while
# merge-ref-based jobs may still be absent — the same hole this step exists
# to close. See #202 / #207 / #210.
echo "::error::PR #${PR_NUMBER} mergeable_state still unknown after ${MAX_ATTEMPTS} attempt(s); refusing to report green."
echo "Re-run this check, or inspect PR #${PR_NUMBER} mergeability in the UI."
write_outputs "${MERGEABLE:-null}" "${MSTATE:-unknown}"
write_summary "failed (unknown after retries)" "${MERGEABLE:-null}" "${MSTATE:-unknown}"
exit 1
