#!/usr/bin/env bash
# Local fail-closed matrix for check.sh (no network). Run:
#   bash .github/actions/check-pr-mergeable/test-check.sh
#
# Asserts exit codes, GITHUB_OUTPUT, and (where relevant) step summary
# wording so silent case drops or output drift fail CI (#215).
# Bump EXPECTED_PASS in the same commit when adding/removing PASS lines.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CHECK="${ROOT}/check.sh"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# Bump when adding/removing PASS lines so a silent case drop fails CI (#215).
EXPECTED_PASS=24

install_mock_gh() {
  cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
# mock: first line of MOCK_STATE_FILE is mergeable\tmstate, then rotate.
state_file="${MOCK_STATE_FILE:?}"
if [ ! -s "$state_file" ]; then
  echo "mock gh: state file empty" >&2
  exit 1
fi
line=$(head -n1 "$state_file")
tail -n +2 "$state_file" >"${state_file}.tmp"
mv "${state_file}.tmp" "$state_file"
printf '%s\n' "$line"
EOF
  chmod +x "$tmpdir/gh"
}

install_mock_gh

export PATH="$tmpdir:$PATH"
export GH_TOKEN=fake REPO=o/r PR_NUMBER=1
export MAX_ATTEMPTS=3 SLEEP_SECONDS=0 API_MAX_RETRIES=3
export GITHUB_OUTPUT="$tmpdir/out" GITHUB_STEP_SUMMARY="$tmpdir/sum"
export MOCK_STATE_FILE="$tmpdir/state"

pass=0
fail=0

indent_out() {
  local line
  while IFS= read -r line || [ -n "$line" ]; do
    printf '  | %s\n' "$line"
  done <<<"$1"
}

assert_outputs() {
  # assert_outputs name expect_mergeable expect_mstate [summary_substr]
  local name="$1" em="$2" es="$3" sum_sub="${4:-}"
  local got_m got_s
  got_m=$(grep -E '^mergeable=' "$GITHUB_OUTPUT" | tail -n1 | cut -d= -f2- || true)
  got_s=$(grep -E '^mergeable_state=' "$GITHUB_OUTPUT" | tail -n1 | cut -d= -f2- || true)
  if [ "$got_m" != "$em" ] || [ "$got_s" != "$es" ]; then
    echo "FAIL: $name outputs expected mergeable=${em} mergeable_state=${es} got mergeable=${got_m} mergeable_state=${got_s}"
    indent_out "$(cat "$GITHUB_OUTPUT" 2>/dev/null || true)"
    return 1
  fi
  if [ -n "$sum_sub" ] && ! grep -Fq "$sum_sub" "$GITHUB_STEP_SUMMARY"; then
    echo "FAIL: $name step summary missing '${sum_sub}'"
    indent_out "$(cat "$GITHUB_STEP_SUMMARY" 2>/dev/null || true)"
    return 1
  fi
  return 0
}

# run_case name expect_exit [state lines...]
# Optional env before call: EXPECT_MERGEABLE, EXPECT_MSTATE, EXPECT_SUMMARY
run_case() {
  local name="$1" expect="$2"
  shift 2
  : >"$MOCK_STATE_FILE"
  local line
  for line in "$@"; do
    printf '%s\n' "$line" >>"$MOCK_STATE_FILE"
  done
  : >"$GITHUB_OUTPUT"
  : >"$GITHUB_STEP_SUMMARY"
  set +e
  out=$(bash "$CHECK" 2>&1)
  code=$?
  set -e
  if [ "$code" -ne "$expect" ]; then
    echo "FAIL: $name expected exit $expect got $code"
    indent_out "$out"
    fail=$((fail + 1))
    return
  fi
  if [ -n "${EXPECT_MERGEABLE:-}" ] || [ -n "${EXPECT_MSTATE:-}" ]; then
    if ! assert_outputs "$name" "${EXPECT_MERGEABLE:-}" "${EXPECT_MSTATE:-}" "${EXPECT_SUMMARY:-}"; then
      fail=$((fail + 1))
      unset EXPECT_MERGEABLE EXPECT_MSTATE EXPECT_SUMMARY
      return
    fi
  fi
  echo "PASS: $name (exit $code)"
  pass=$((pass + 1))
  unset EXPECT_MERGEABLE EXPECT_MSTATE EXPECT_SUMMARY
}

# --- core mergeability matrix ---
EXPECT_MERGEABLE=true EXPECT_MSTATE=clean EXPECT_SUMMARY='ok (mergeable=true)' \
  run_case "unknown->clean" 0 $'null\tunknown' $'true\tclean'

EXPECT_MERGEABLE=false EXPECT_MSTATE=dirty EXPECT_SUMMARY='failed (dirty)' \
  run_case "dirty" 1 $'false\tdirty'

EXPECT_MERGEABLE=null EXPECT_MSTATE=unknown EXPECT_SUMMARY='failed (unknown after retries)' \
  run_case "unknown-forever" 1 $'null\tunknown' $'null\tunknown' $'null\tunknown'

EXPECT_MERGEABLE=false EXPECT_MSTATE=blocked EXPECT_SUMMARY='failed (mergeable=false, state=blocked)' \
  run_case "false-blocked" 1 $'false\tblocked'

EXPECT_MERGEABLE=false EXPECT_MSTATE=unknown EXPECT_SUMMARY='failed (mergeable=false)' \
  run_case "false-unknown" 1 $'false\tunknown'

EXPECT_MERGEABLE=true EXPECT_MSTATE=unstable EXPECT_SUMMARY='ok (mergeable=true)' \
  run_case "unstable-ok" 0 $'true\tunstable'

EXPECT_MERGEABLE=null EXPECT_MSTATE=clean EXPECT_SUMMARY='failed (mergeable not true, state=clean)' \
  run_case "null-clean-fails" 1 $'null\tclean'

EXPECT_MERGEABLE=null EXPECT_MSTATE=clean EXPECT_SUMMARY='failed (mergeable not true, state=clean)' \
  run_case "empty-clean-fails" 1 $'\tclean'

EXPECT_MERGEABLE=null EXPECT_MSTATE=blocked EXPECT_SUMMARY='failed (mergeable not true, state=blocked)' \
  run_case "null-blocked-fails" 1 $'null\tblocked'

EXPECT_MERGEABLE=true EXPECT_MSTATE=blocked EXPECT_SUMMARY='ok (mergeable=true)' \
  run_case "true-blocked-ok" 0 $'true\tblocked'

# #215 edge cases
EXPECT_MERGEABLE=true EXPECT_MSTATE=unknown EXPECT_SUMMARY='failed (unknown after retries)' \
  run_case "true-unknown-exhausted" 1 $'true\tunknown' $'true\tunknown' $'true\tunknown'

EXPECT_MERGEABLE=true EXPECT_MSTATE=dirty EXPECT_SUMMARY='failed (dirty)' \
  run_case "true-dirty-short-circuit" 1 $'true\tdirty'

# Defense-in-depth: literal "null" state token (if extraction drifts) must
# exhaust as unresolved, not hit *) and go green when mergeable=true (#216).
EXPECT_MERGEABLE=true EXPECT_MSTATE=null EXPECT_SUMMARY='failed (unknown after retries)' \
  run_case "true-null-state-exhausts" 1 $'true\tnull' $'true\tnull' $'true\tnull'

# --- jq encoding locks (#216) ---
jq_prod=$(jq -rn '([(null | tostring), ((null // "unknown") | tostring)] | @tsv)')
if [ "$jq_prod" = $'null\tunknown' ]; then
  echo "PASS: jq-tostring-prod-extraction (null mergeable + null state→unknown)"
  pass=$((pass + 1))
else
  printf 'FAIL: jq-tostring-prod-extraction expected null\\tunknown got %q\n' "$jq_prod"
  fail=$((fail + 1))
fi
jq_tsv_true=$(jq -rn '([(true | tostring), (("clean" // "unknown") | tostring)] | @tsv)')
if [ "$jq_tsv_true" = $'true\tclean' ]; then
  echo "PASS: jq-tostring-true-field"
  pass=$((pass + 1))
else
  printf 'FAIL: jq-tostring-true-field expected true\\tclean got %q\n' "$jq_tsv_true"
  fail=$((fail + 1))
fi

# --- input validation (before gh) ---
set +e
out=$(MAX_ATTEMPTS=0 bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'max-attempts'; then
  echo "PASS: invalid-max (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: invalid-max expected non-zero + message"
  indent_out "$out"
  fail=$((fail + 1))
fi

set +e
out=$(SLEEP_SECONDS=-1 bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'sleep-seconds'; then
  echo "PASS: invalid-sleep (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: invalid-sleep expected non-zero + message"
  indent_out "$out"
  fail=$((fail + 1))
fi

set +e
out=$(API_MAX_RETRIES=0 bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'api-max-retries'; then
  echo "PASS: invalid-api-max-retries (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: invalid-api-max-retries expected non-zero + message"
  indent_out "$out"
  fail=$((fail + 1))
fi

# dirty + conflict-guidance printed
export CONFLICT_GUIDANCE="Sync main into dev with a merge commit, not squash."
printf '%s\n' $'false\tdirty' >"$MOCK_STATE_FILE"
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'merge commit, not squash' \
  && assert_outputs "conflict-guidance" "false" "dirty" "failed (dirty)"; then
  echo "PASS: conflict-guidance (printed on dirty)"
  pass=$((pass + 1))
else
  echo "FAIL: conflict-guidance"
  indent_out "$out"
  fail=$((fail + 1))
fi
unset CONFLICT_GUIDANCE

# --- API error paths (#217) ---
cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
echo "HTTP 500: boom" >&2
exit 1
EOF
chmod +x "$tmpdir/gh"
export MAX_ATTEMPTS=2 API_MAX_RETRIES=2 SLEEP_SECONDS=0
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'gh api failed' \
  && echo "$out" | grep -q 'transient errors exhausted' \
  && assert_outputs "gh-api-error-transient-exhausted" "null" "api_error" "failed (gh api error)"; then
  echo "PASS: gh-api-error-transient-exhausted (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-error-transient-exhausted"
  indent_out "$out"
  fail=$((fail + 1))
fi

cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
echo "HTTP 401: Bad credentials" >&2
exit 1
EOF
chmod +x "$tmpdir/gh"
export API_MAX_RETRIES=3 SLEEP_SECONDS=0
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'permanent error' \
  && ! echo "$out" | grep -q 'retrying in' \
  && assert_outputs "gh-api-error-permanent-no-retry" "null" "api_error" "failed (gh api error)"; then
  echo "PASS: gh-api-error-permanent-no-retry (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-error-permanent-no-retry"
  indent_out "$out"
  fail=$((fail + 1))
fi

# Unknown-shape API error: fail closed without retry (#217 / #215 follow-up)
cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
echo "HTTP 400: Bad Request" >&2
exit 1
EOF
chmod +x "$tmpdir/gh"
export API_MAX_RETRIES=3 SLEEP_SECONDS=0
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'cannot evaluate mergeability' \
  && ! echo "$out" | grep -q 'retrying in' \
  && assert_outputs "gh-api-error-unknown-shape" "null" "api_error" "failed (gh api error)"; then
  echo "PASS: gh-api-error-unknown-shape (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-error-unknown-shape"
  indent_out "$out"
  fail=$((fail + 1))
fi

# Flaky then success: first call 503, second returns true\tclean (#217)
cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
counter_file="${MOCK_API_COUNTER:?}"
n=$(cat "$counter_file" 2>/dev/null || echo 0)
n=$((n + 1))
echo "$n" >"$counter_file"
if [ "$n" -eq 1 ]; then
  echo "HTTP 503: service unavailable" >&2
  exit 1
fi
state_file="${MOCK_STATE_FILE:?}"
if [ ! -s "$state_file" ]; then
  echo "mock gh: state file empty" >&2
  exit 1
fi
line=$(head -n1 "$state_file")
tail -n +2 "$state_file" >"${state_file}.tmp"
mv "${state_file}.tmp" "$state_file"
printf '%s\n' "$line"
EOF
chmod +x "$tmpdir/gh"
export MOCK_API_COUNTER="$tmpdir/api_counter"
echo 0 >"$MOCK_API_COUNTER"
printf '%s\n' $'true\tclean' >"$MOCK_STATE_FILE"
export MAX_ATTEMPTS=2 API_MAX_RETRIES=3 SLEEP_SECONDS=0
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -eq 0 ] && echo "$out" | grep -q 'Transient gh api error' \
  && assert_outputs "gh-api-flaky-then-success" "true" "clean" "ok (mergeable=true)"; then
  echo "PASS: gh-api-flaky-then-success (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-flaky-then-success"
  indent_out "$out"
  fail=$((fail + 1))
fi

# Secondary rate limit is HTTP 403-shaped but must retry (#217)
cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
counter_file="${MOCK_API_COUNTER:?}"
n=$(cat "$counter_file" 2>/dev/null || echo 0)
n=$((n + 1))
echo "$n" >"$counter_file"
if [ "$n" -eq 1 ]; then
  echo "HTTP 403: You have exceeded a secondary rate limit" >&2
  exit 1
fi
state_file="${MOCK_STATE_FILE:?}"
if [ ! -s "$state_file" ]; then
  echo "mock gh: state file empty" >&2
  exit 1
fi
line=$(head -n1 "$state_file")
tail -n +2 "$state_file" >"${state_file}.tmp"
mv "${state_file}.tmp" "$state_file"
printf '%s\n' "$line"
EOF
chmod +x "$tmpdir/gh"
echo 0 >"$MOCK_API_COUNTER"
printf '%s\n' $'true\tclean' >"$MOCK_STATE_FILE"
export MAX_ATTEMPTS=2 API_MAX_RETRIES=3 SLEEP_SECONDS=0
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -eq 0 ] && echo "$out" | grep -q 'Transient gh api error' \
  && assert_outputs "gh-api-secondary-rate-limit-then-success" "true" "clean" "ok (mergeable=true)"; then
  echo "PASS: gh-api-secondary-rate-limit-then-success (exit $code)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-secondary-rate-limit-then-success"
  indent_out "$out"
  fail=$((fail + 1))
fi
unset MOCK_API_COUNTER
export API_MAX_RETRIES=3 MAX_ATTEMPTS=3

echo ""
echo "Results: $pass passed, $fail failed (expected $EXPECTED_PASS pass)"
if [ "$fail" -ne 0 ]; then
  exit 1
fi
if [ "$pass" -ne "$EXPECTED_PASS" ]; then
  echo "FAIL: pass count $pass != EXPECTED_PASS $EXPECTED_PASS (silent case drop or extra case?)"
  exit 1
fi
echo "PASS: expected-pass-count ($EXPECTED_PASS)"
