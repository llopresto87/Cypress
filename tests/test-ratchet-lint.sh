#!/usr/bin/env bash
# test-ratchet-lint.sh — tools/ratchet-lint.py refuses a loosened limit.
# Runs the tool on a mini tree: the tool, a synthetic source and its lock.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
. "$ROOT/tests/helpers/lintcase.sh"

fresh() {  # $1 dir: the tool, a source with one ceiling and one ledger, their lock
  mini_tree "$1" tools/ratchet-lint.py && mkdir -p "$1/tests" || return 1
  printf 'LEAF_BODY_CEILING = 170\nOVERSIZED_LEAVES = frozenset({"a.md"})\n' > "$1/src.py"
  cat > "$1/tests/ratchets.json" <<'JSON'
{"ratchets": {"LEAF_BODY_CEILING": 170, "OVERSIZED_LEAVES": ["a.md"]},
 "registry": {"LEAF_BODY_CEILING": "max src.py", "OVERSIZED_LEAVES": "set src.py"}}
JSON
  expect_rc 0 "lock exact" -- python3 "$1/tools/ratchet-lint.py"
}

case_ce_leaf_ratchet_ceiling_raised() {  # X339 LEAF_BODY_CEILING_HELD
  fresh "$TMP/a" || return 1
  sed -i.bak 's/= 170/= 171/' "$TMP/a/src.py"
  expect_rc 1 "LEAF_BODY_CEILING was LOOSENED" -- python3 "$TMP/a/tools/ratchet-lint.py"
}

case_ce_leaf_ratchet_member_added() {  # X340 LEDGER_REGROWS
  fresh "$TMP/b" || return 1
  sed -i.bak 's/{"a.md"}/{"a.md", "b.md"}/' "$TMP/b/src.py"
  expect_rc 1 "OVERSIZED_LEAVES GREW" -- python3 "$TMP/b/tools/ratchet-lint.py"
}

collect_case X339 case_ce_leaf_ratchet_ceiling_raised "a raised ceiling exits 1, naming the key"
collect_case X340 case_ce_leaf_ratchet_member_added "a member added to a ledger exits 1, naming the key"
[ "$CASE_FAILED" -eq 0 ] || { echo "test-ratchet-lint: FAIL" >&2; exit 1; }
echo "test-ratchet-lint: PASS"
