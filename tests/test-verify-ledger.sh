#!/usr/bin/env bash
# verify-ledger contract: tools/verify-ledger.py rebuilds a monolith from a
# ledger plan and its leaves and compares bytes. Fixtures: seed-ledger/ with
# seed-ledger.monolith.md (its §9 index replaced by the leaves, in row order,
# one blank line between them), and multi-table/ (two index tables).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/helpers/lintcase.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FX="$ROOT/tests/fixtures/grill"

# fresh fixture copies: $TMP/one (seed-ledger) and $TMP/multi (multi-table)
fixtures() {
  rm -rf "$TMP/one" "$TMP/multi"; mkdir -p "$TMP/one/docs"
  cp "$FX/seed-ledger.monolith.md" "$TMP/one/round.monolith.md"
  cp -R "$FX/seed-ledger/docs/plans" "$TMP/one/docs/plans"
  cp -R "$FX/multi-table" "$TMP/multi"
}
vl() {  # vl <fixture dir>: WOUT holds the output, WRC the exit status
  WOUT="$(python3 "$ROOT/tools/verify-ledger.py" --monolith "$1/round.monolith.md" \
    --ledger "$1/docs/plans/round.md" --leaves "$1/docs/plans/round" 2>&1)" && WRC=0 || WRC=$?
}
rc() { [ "$WRC" -eq "$1" ] || { echo "exit $WRC, want $1: $WOUT"; return 1; }; }
names() { grep -qE -- "(^|[^0-9])$1([^0-9]|\$)" <<<"$WOUT" || { echo "output does not name $1: $WOUT"; return 1; }; }
flip() { python3 -c 'import sys; p, o, n = sys.argv[1:]; b = open(p, "rb").read()
assert o.encode() in b, "fixture text missing"; open(p, "wb").write(b.replace(o.encode(), n.encode(), 1))' "$@"; }

case_verify_ledger_changed_byte() {
  # D5b: one changed byte in a leaf exits 1, names the leaf and the first
  # differing byte offset (0-based, in the rebuild or in the leaf).
  local om ol
  set -e; fixtures
  om="$(python3 -c 'import sys; print(open(sys.argv[1],"rb").read().index(b"rows kept as written") + 19)' "$TMP/one/round.monolith.md")"
  ol="$(python3 -c 'import sys; print(open(sys.argv[1],"rb").read().index(b"rows kept as written") + 19)' "$TMP/one/docs/plans/round/increment-02-b.md")"
  flip "$TMP/one/docs/plans/round/increment-02-b.md" "rows kept as written" "rows kept as writteN"
  vl "$TMP/one"; rc 1; names 'increment-02-b.md'
  names "$om" >/dev/null || names "$ol"
}
case_verify_ledger_unindexed_leaf() {  # D5c: a leaf no row points at exits 1 and is named
  set -e; fixtures
  cp "$TMP/one/docs/plans/round/increment-01-a.md" "$TMP/one/docs/plans/round/increment-03-stray.md"
  vl "$TMP/one"; rc 1; names 'increment-03-stray.md'
}
case_verify_ledger_counts_utf8_bytes() {
  # D5d, survivor of D5a: the unchanged ledger rebuilds exactly, exit 0, and the
  # printed count is UTF-8 bytes, not characters (the fixture holds multibyte text).
  local nb nc
  set -e; fixtures
  nb="$(wc -c < "$TMP/one/round.monolith.md" | tr -d ' ')"
  nc="$(python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' "$TMP/one/round.monolith.md")"
  [ "$nb" -ne "$nc" ] || { echo "harness: the fixture has no multibyte character"; return 1; }
  vl "$TMP/one"; rc 0; names "$nb"
  ! names "$nc" >/dev/null || { echo "the character count $nc is printed as bytes"; return 1; }
}
case_verify_ledger_multi_table() {
  # D5e, D5f: both index tables count, in document order: the rebuild proves
  # exactly with four leaves; a changed byte in a leaf of the SECOND table exits
  # 1 and names that leaf as a rebuild difference.
  set -e; fixtures
  [ "$(grep -c '^| # | Increment | Status | Detail |$' "$TMP/multi/docs/plans/round.md")" -eq 2 ]
  vl "$TMP/multi"; rc 0; names "$(wc -c < "$TMP/multi/round.monolith.md" | tr -d ' ')"; names 4
  flip "$TMP/multi/docs/plans/round/increment-04-d.md" "nightly report" "nightly repOrt"   # D5f
  vl "$TMP/multi"; rc 1; names 'increment-04-d.md'
  grep -q 'differs from' <<<"$WOUT" || { echo "not named as a rebuild difference: $WOUT"; return 1; }
}
case_verify_ledger_detail_cell_names_the_leaf() {
  # D5g: a row's leaf is its Detail cell, not the first .md token; a title
  # naming INSTALL.md leaves the rebuild exact.
  set -e; fixtures
  flip "$TMP/multi/docs/plans/round.md" "| 3 | Refuse a duplicate batch |" "| 3 | Refuse a duplicate batch listed in INSTALL.md |"
  vl "$TMP/multi"; rc 0
  ! grep -q 'INSTALL.md' <<<"$WOUT" || { echo "INSTALL.md from the title was read as a leaf: $WOUT"; return 1; }
}

collect_case D5b case_verify_ledger_changed_byte 'a changed byte names the leaf and offset'
collect_case D5c case_verify_ledger_unindexed_leaf 'an unindexed leaf is named'
collect_case D5d case_verify_ledger_counts_utf8_bytes 'an exact rebuild prints its UTF-8 byte count'
collect_case D5e case_verify_ledger_multi_table 'two index tables both count'
collect_case D5g case_verify_ledger_detail_cell_names_the_leaf 'the Detail cell names the leaf'

[ "$CASE_FAILED" -eq 0 ] || { echo 'verify-ledger contract: FAIL (cases above)'; exit 1; }
echo 'verify-ledger contract: PASS'
