#!/usr/bin/env bash
# Local fail-closed matrix for check.sh (no network). Run:
#   bash .github/actions/check-pr-mergeable/test-check.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CHECK="${ROOT}/check.sh"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

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
export MAX_ATTEMPTS=3 SLEEP_SECONDS=0
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
  if [ "$code" -eq "$expect" ]; then
    echo "PASS: $name (exit $code)"
    pass=$((pass + 1))
  else
    echo "FAIL: $name expected exit $expect got $code"
    indent_out "$out"
    fail=$((fail + 1))
  fi
}

run_case "unknown->clean" 0 $'null\tunknown' $'true\tclean'
run_case "dirty" 1 $'false\tdirty'
run_case "unknown-forever" 1 $'null\tunknown' $'null\tunknown' $'null\tunknown'
run_case "false-blocked" 1 $'false\tblocked'
run_case "false-unknown" 1 $'false\tunknown'
run_case "unstable-ok" 0 $'true\tunstable'
# #213 / #216: null mergeable with a resolved non-dirty state must not go green.
# Production after #216: jq tostring encodes JSON null as the literal "null"
# token ($'null\tclean'). empty-*-fails remains defensive for a drifted
# extraction that still emits an empty field.
run_case "null-clean-fails" 1 $'null\tclean'
run_case "empty-clean-fails" 1 $'\tclean'
run_case "null-blocked-fails" 1 $'null\tblocked'
run_case "true-blocked-ok" 0 $'true\tblocked'

# Lock the production jq extraction used by check.sh (#216). No network.
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
# true + null mergeable_state maps to unknown and must not go green (exhaust).
run_case "true-null-state-exhausts" 1 $'true\tunknown' $'true\tunknown' $'true\tunknown'

# invalid max via env (before gh is called)
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

# dirty + conflict-guidance printed
export CONFLICT_GUIDANCE="Sync main into dev with a merge commit, not squash."
printf '%s\n' $'false\tdirty' >"$MOCK_STATE_FILE"
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'merge commit, not squash'; then
  echo "PASS: conflict-guidance (printed on dirty)"
  pass=$((pass + 1))
else
  echo "FAIL: conflict-guidance"
  indent_out "$out"
  fail=$((fail + 1))
fi
unset CONFLICT_GUIDANCE

# API failure path: replace gh with always-fail
cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
echo "HTTP 500: boom" >&2
exit 1
EOF
chmod +x "$tmpdir/gh"
export MAX_ATTEMPTS=2
: >"$GITHUB_OUTPUT"
: >"$GITHUB_STEP_SUMMARY"
set +e
out=$(bash "$CHECK" 2>&1)
code=$?
set -e
if [ "$code" -ne 0 ] && echo "$out" | grep -q 'gh api failed'; then
  echo "PASS: gh-api-error (exit $code, classified message)"
  pass=$((pass + 1))
else
  echo "FAIL: gh-api-error"
  indent_out "$out"
  fail=$((fail + 1))
fi

echo ""
echo "Results: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
