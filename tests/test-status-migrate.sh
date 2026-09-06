#!/usr/bin/env bash
# test-status-migrate.sh — the one-time body-prose → frontmatter migration is
# exact, idempotent, and never invents a fact:
#   a dry run lists work and exits 1; --write applies and a second run finds nothing;
#   "superseded by ADR-NNNN" becomes superseded + superseded_by; deprecated becomes
#   superseded with a `not recorded` successor (named, not invented); the body
#   status line becomes the pointer; an already-migrated file is untouched.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$ROOT/tools/status-migrate.py"
SRC="$ROOT/tests/fixtures/status-migrate/docs/graph"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp -R "$SRC" "$TMP/graph"
fail() { echo "FAIL: $*" >&2; [ -f "$TMP/out" ] && cat "$TMP/out" >&2; exit 1; }
run() { local want="$1"; shift; set +e; python3 "$TOOL" "$@" >"$TMP/out" 2>&1; local rc=$?; set -e; [ "$rc" = "$want" ] || fail "expected exit $want, got $rc (args: $*)"; }

# 1. dry run finds 4, exits 1, writes nothing
run 1 --root "$TMP/graph" --today 2026-09-06
grep -q "5 to migrate, 1 already in frontmatter, 1 need a decision" "$TMP/out" || fail "dry-run count"
grep -q '^status:' "$TMP/graph/decisions/adr-0001-old.md" && fail "dry run must not write"
echo "  dry run lists work, exits 1, writes nothing — OK"

# 2. write, then verify each mapping
run 0 --root "$TMP/graph" --write --today 2026-09-06
a1="$TMP/graph/decisions/adr-0001-old.md"
grep -q '^status: superseded$' "$a1" || fail "adr-0001 status"
grep -q '^superseded_by: ADR-0002$' "$a1" || fail "adr-0001 superseded_by"
grep -q '^status_date: 2026-03-01$' "$a1" || fail "adr-0001 date from ## Date"
grep -q 'See frontmatter — the single home' "$a1" || fail "adr-0001 body pointer"
grep -q 'superseded by ADR-0002' "$a1" && fail "adr-0001 old body value still present"
a3="$TMP/graph/decisions/adr-0003-gone.md"
grep -q '^status: superseded$' "$a3" || fail "deprecated → superseded"
grep -q '^superseded_by: not recorded — deprecated without a named successor$' "$a3" || fail "deprecated successor must be 'not recorded', never invented"
s1="$TMP/graph/specs/SPEC-0001-old.md"
grep -q '^status: draft$' "$s1" || fail "spec draft"
grep -q '^owner: acme-architect$' "$s1" || fail "spec owner carried"
grep -q '^status_date: 2026-02-02$' "$s1" || fail "spec date from bullet"
grep -q 'Status:\*\* see frontmatter' "$s1" || fail "spec body pointer"
s3="$TMP/graph/specs/SPEC-0003-annotated.md"
grep -q '^status: active$' "$s3" || fail "annotated status must map on its leading token"
grep -q '^status_note: INC-0..INC-3 implemented and verified 2026-07-11; promotes to `implemented` after staging$' "$s3" || fail "annotation must be carried as status_note, not dropped"
grep -q '^status:' "$TMP/graph/specs/SPEC-0004-wrongvocab.md" && fail "a spec using ADR vocabulary (ACCEPTED) is a real inconsistency and must stay a decision, not be migrated"
echo "  annotated status split into token + status_note; wrong-vocabulary spec left for a decision — OK"
cmp -s "$SRC/specs/SPEC-0002-done.md" "$TMP/graph/specs/SPEC-0002-done.md" || fail "already-migrated file must be untouched"
echo "  mappings exact; not-recorded never invented; pointer written; migrated file untouched — OK"

# 3. idempotent: second run finds nothing
run 0 --root "$TMP/graph" --today 2026-09-06
grep -q "0 to migrate, 6 already in frontmatter, 1 need a decision" "$TMP/out" || fail "second run must find nothing"
echo "  idempotent — OK"

# 4. the migrated tree passes the status linter, if it is present
if [ -f "$ROOT/tools/status-register.py" ]; then
  python3 "$ROOT/tools/status-register.py" --root "$TMP/graph" >"$TMP/out" 2>&1 || fail "migrated tree must lint clean"
  echo "  migrated tree passes status-register lint — OK"
fi
echo "test-status-migrate: PASS"
