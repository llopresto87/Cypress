#!/usr/bin/env bash
# test-spec-convert.sh — SPEC-0010: tools/spec-convert.py converts one plant
# spec from the legacy form to the kinds form, the mechanical part only.
#   X640 the dry run prints the report and writes nothing
#   X641 --write is refused without --steward-ratified and a spec path
#   X642 --write adds only the mechanical lines, keeps a backup, and a second
#        write finds nothing to do
#   X643 an unrecognised spec shape is a named error and nothing is written
#   X649 graft-audit reads the conversion's backup as a shape migration
# Every case runs on a temp copy of tests/fixtures/spec-convert/plant, whose
# spec-lint.py is the seed's engine with the plant's own test layout.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$ROOT/tools/spec-convert.py"
FIX="$ROOT/tests/fixtures/spec-convert"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
. "$ROOT/tests/helpers/lintcase.sh"

need_tool() { [ -f "$TOOL" ] || { echo "tools/spec-convert.py does not exist"; return 1; }; }
flat() { tr '\n' ' ' <"$1"; }
# plant <name>: a fresh copy of the fixture plant, its engine configured
plant() {
  local p="$TMP/$1"
  rm -rf "$p"; cp -R "$FIX/plant" "$p"
  python3 "$FIX/configure.py" "$ROOT/templates/knowledge-graph/spec-lint.py" "$p/docs/graph/spec-lint.py" || return 1
  echo "$p"
}
digest() { find "$1" -type f | LC_ALL=C sort | while read -r f; do cksum "$f"; done; }

case_dry_run_prints_the_mechanical_part() {
  # X640 SPEC_CONVERT_DRY_RUN_PRINTS_THE_MECHANICAL_PART
  local p s before rc
  need_tool || return 1
  p="$(plant x640)" || return 1; s="$p/docs/graph/specs/SPEC-0501-orders.md"
  before="$(digest "$p")"
  python3 "$TOOL" --dry-run "$s" >"$TMP/x640.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] || { echo "the dry run exited $rc: $(flat "$TMP/x640.out")"; return 1; }
  while IFS= read -r want; do
    grep -Fxq -- "$want" "$TMP/x640.out" || { echo "the dry run lacks the line [$want]: $(flat "$TMP/x640.out")"; return 1; }
  done <<'EOF'
spec-convert: SPEC-0501-orders.md (legacy form -> kinds form) — DRY RUN, nothing written
 §0: add "- **Contract form:** kinds" and "- **Trust path:** no"   (set yes if a contract is security, data-integrity or money)
 §4: 3 contracts -> "- **Check:** test" each (present mapping kept as evidence: §10 row / slug in test)
    ORDER_TOTAL_IS_SUMMED: §10 row (test_order_total_is_summed, tests/test_orders.py); slug in test (tests/test_orders.py)
    ORDER_DISCOUNT_IS_CAPPED: §10 row (test_discount_cap, vendor/lib/orders_test.py); slug in no test file the plant's TEST_GLOBS read
    ORDER_EMPTY_CART_IS_REFUSED: §10 row (test_empty_cart_is_refused, tests/test_orders.py); slug in test (tests/test_orders.py)
 unchanged: Given/When/Then, §7, §9, §10 header (legacy §10 stays valid), changelog
 judgment, NOT done here: re-labelling a contract run / review / covered, a declared-values table, a risk-based §10: the plant's architect, after the steward ratifies
EOF
  [ "$(digest "$p")" = "$before" ] || { echo "the dry run changed a file in the plant"; return 1; }
  # with no mode named, the run is the dry run
  python3 "$TOOL" "$s" >"$TMP/x640b.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && grep -q '— DRY RUN, nothing written$' "$TMP/x640b.out" \
    || { echo "a run naming no mode is not the dry run (exit $rc): $(flat "$TMP/x640b.out")"; return 1; }
  [ "$(digest "$p")" = "$before" ] || { echo "a run naming no mode changed a file"; return 1; }
  # a contract already labelled is kept as written and named
  python3 "$TOOL" --dry-run "$p/docs/graph/specs/SPEC-0502-refunds.md" >"$TMP/x640c.out" 2>&1 || true
  grep -Fxq ' §4: 1 contracts -> "- **Check:** test" each (present mapping kept as evidence: §10 row / slug in test)' "$TMP/x640c.out" \
    && grep -Fxq ' §4: kept as written, already labelled: REFUND_BUTTON_LABEL_IS_REFUND (run)' "$TMP/x640c.out" \
    && grep -Fxq '    REFUND_RESTORES_THE_BALANCE: §10 row (test_refund_restores_the_balance, checks/refund_check.py); slug in test (checks/refund_check.py)' "$TMP/x640c.out" \
    || { echo "a partly labelled spec is not reported contract by contract: $(flat "$TMP/x640c.out")"; return 1; }
}

case_write_needs_the_steward() {
  # X641 SPEC_CONVERT_WRITE_NEEDS_THE_STEWARD
  local p s before rc
  need_tool || return 1
  p="$(plant x641)" || return 1; s="$p/docs/graph/specs/SPEC-0501-orders.md"
  before="$(digest "$p")"
  python3 "$TOOL" --write "$s" >"$TMP/x641a.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 2 ] && grep -q -- "--steward-ratified" "$TMP/x641a.out" \
    || { echo "--write with no --steward-ratified exited $rc and did not name the flag: $(flat "$TMP/x641a.out")"; return 1; }
  python3 "$TOOL" --write --steward-ratified >"$TMP/x641b.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 2 ] && grep -qi "spec path" "$TMP/x641b.out" \
    || { echo "--write --steward-ratified with no spec path exited $rc and did not name the path: $(flat "$TMP/x641b.out")"; return 1; }
  [ "$(digest "$p")" = "$before" ] || { echo "a refused --write changed or added a file"; return 1; }
}

case_write_adds_only_the_mechanical_part() {
  # X642 SPEC_CONVERT_WRITES_ONLY_THE_MECHANICAL_PART
  local p s rc baks
  need_tool || return 1
  p="$(plant x642)" || return 1
  for s in "$p/docs/graph/specs/SPEC-0501-orders.md" "$p/docs/graph/specs/SPEC-0502-refunds.md"; do
    cp "$s" "$TMP/x642.orig"
    python3 "$TOOL" --write --steward-ratified "$s" >"$TMP/x642.out" 2>&1 && rc=0 || rc=$?
    [ "$rc" -eq 0 ] && grep -q "(legacy form -> kinds form) — WRITTEN, backup $(basename "$s").bak-" "$TMP/x642.out" \
      || { echo "--write --steward-ratified exited $rc or named no backup: $(flat "$TMP/x642.out")"; return 1; }
    baks="$(ls "$(dirname "$s")" | grep -c "^$(basename "$s")\.bak-")" || true
    [ "$baks" -eq 1 ] || { echo "want one backup of $(basename "$s"), found $baks"; return 1; }
    cmp -s "$s".bak-* "$TMP/x642.orig" || { echo "the backup of $(basename "$s") is not the spec as it was"; return 1; }
    python3 - "$TMP/x642.orig" "$s" "$ROOT/templates/knowledge-graph/spec-lint.py" <<'PY' || return 1
import runpy, sys
old = open(sys.argv[1], encoding="utf-8").read().splitlines()
new = open(sys.argv[2], encoding="utf-8").read().splitlines()
lint = runpy.run_path(sys.argv[3])
added, i = [], 0
for line in new:                      # the old lines, in order, with only additions between
    if i < len(old) and line == old[i]:
        i += 1
    else:
        added.append(line)
if i != len(old):
    sys.exit(f"a line of the spec changed or moved: {old[i]!r}")
want = {"- **Contract form:** kinds", "- **Trust path:** no", "- **Check:** test"}
if set(added) - want:
    sys.exit(f"lines other than the mechanical part were added: {sorted(set(added) - want)}")
text = "\n".join(new) + "\n"
secs = lint["sections"](text)
if not lint["FORM_RE"].search(secs.get(0, "")):
    sys.exit("§0 does not read `- **Contract form:** kinds` where the engine looks for it")
checks = lint["contract_checks"](text)
before = lint["contract_checks"]("\n".join(old) + "\n")
for slug, value in checks.items():
    if before.get(slug) is not None:
        if value != before[slug]:
            sys.exit(f"{slug}: its Check line {before[slug]!r} became {value!r}")
    elif value != "test":
        sys.exit(f"{slug}: the engine reads its Check as {value!r}, want test")
if added.count("- **Check:** test") != sum(1 for v in before.values() if v is None):
    sys.exit(f"want one Check line per unlabelled contract, added {added.count('- **Check:** test')}")
PY
    cp "$s" "$TMP/x642.conv"
    python3 "$TOOL" --write --steward-ratified "$s" >"$TMP/x642b.out" 2>&1 && rc=0 || rc=$?
    [ "$rc" -eq 0 ] && grep -q "already in the kinds form; nothing to convert" "$TMP/x642b.out" \
      || { echo "a second --write exited $rc and did not say there is nothing to convert: $(flat "$TMP/x642b.out")"; return 1; }
    cmp -s "$s" "$TMP/x642.conv" || { echo "a second --write changed the converted spec"; return 1; }
    baks="$(ls "$(dirname "$s")" | grep -c "^$(basename "$s")\.bak-")" || true
    [ "$baks" -eq 1 ] || { echo "a second --write left another backup ($baks)"; return 1; }
  done
  # the plant's engine reads every converted contract with the kind written
  ( cd "$p" && python3 docs/graph/spec-lint.py ) >"$TMP/x642.lint" 2>&1 || true
  grep -q '^contracts by kind: test 4, run 1, review 0, covered 0, legacy-test 0$' "$TMP/x642.lint" \
    || { echo "the plant's spec-lint does not read the converted kinds: $(flat "$TMP/x642.lint")"; return 1; }
  # a converted spec keeps its legacy §10 as the link until a risk table is written (CONVERTED_SPEC_FAILS_THE_PLANT_LINT)
  if grep -q 'no §10 row covers it' "$TMP/x642.lint"; then
    echo "the converted spec fails the plant's lint on its legacy §10: $(flat "$TMP/x642.lint")"; return 1
  fi
}

case_unrecognised_shape_is_named() {
  # X643 SPEC_CONVERT_NAMES_AN_UNRECOGNISED_SHAPE
  local p d f rc before why
  need_tool || return 1
  p="$(plant x643)" || return 1; d="$p/docs/graph/specs"
  printf -- '---\nstatus: active\n---\n# SPEC-0601: notes\n\n## 0. Metadata\n- **Owner:** architect\n\n## 1. Summary\nNo contracts.\n' > "$d/SPEC-0601-notes.md"
  printf -- '# SPEC-0602: loose\n\n## 4. Functional contracts\n\n### Contract: LOOSE_THING_HOLDS\n- **Given:** x\n' > "$d/SPEC-0602-loose.md"
  printf -- '# SPEC-0603: fenced\n\n## 0. Metadata\n- **Owner:** a\n\n## 4. Functional contracts\n\n### Contract: REAL_THING_HOLDS\n- **Given:** x\n\n```\n### Contract: QUOTED_THING_HOLDS\n```\n' > "$d/SPEC-0603-fenced.md"
  cp "$d/SPEC-0501-orders.md" "$d/orders-notes.md"
  before="$(digest "$p")"
  for f in SPEC-0601-notes.md:"no \`### Contract:\` heading" SPEC-0602-loose.md:"no \`## 0.\` metadata section" \
           SPEC-0603-fenced.md:"inside a code fence" orders-notes.md:"the file name is not SPEC-"; do
    why="${f#*:}"; f="${f%%:*}"
    python3 "$TOOL" --write --steward-ratified "$d/$f" >"$TMP/x643.out" 2>&1 && rc=0 || rc=$?
    [ "$rc" -eq 1 ] && grep -q "^spec-convert: $f: unrecognised spec shape: .*$why.*; nothing written$" "$TMP/x643.out" \
      || { echo "$f exited $rc, want 1 with an unrecognised-shape line naming [$why]: $(flat "$TMP/x643.out")"; return 1; }
  done
  python3 "$TOOL" --dry-run "$d/SPEC-0699-absent.md" >"$TMP/x643b.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 2 ] && grep -q "SPEC-0699-absent.md" "$TMP/x643b.out" \
    || { echo "a spec path that does not exist exited $rc, want 2 naming it: $(flat "$TMP/x643b.out")"; return 1; }
  [ "$(digest "$p")" = "$before" ] || { echo "an unrecognised spec was written to or backed up"; return 1; }
  python3 "$TOOL" --help >"$TMP/x643c.out" 2>&1 && grep -q -- "--steward-ratified" "$TMP/x643c.out" \
    || { echo "--help does not answer with the usage: $(flat "$TMP/x643c.out")"; return 1; }
}

case_backup_is_audited_as_a_shape_migration() {
  # X649 SPEC_CONVERT_BACKUP_IS_AUDITED
  local p s out rc
  need_tool || return 1
  p="$(plant x649)" || return 1; s="$p/docs/graph/specs/SPEC-0501-orders.md"
  mkdir -p "$TMP/x649seed"
  python3 "$TOOL" --write --steward-ratified "$s" >"$TMP/x649.out" 2>&1 \
    || { echo "fixture: the conversion did not write: $(flat "$TMP/x649.out")"; return 1; }
  out="$(python3 "$ROOT/tools/graft-audit.py" "$p" "$TMP/x649seed" 2>&1)" && rc=0 || rc=$?
  grep -q "'SHAPE-MIGRATED': 1" <<<"$out" && ! grep -q "knowledge overwrite" <<<"$out" && [ "$rc" -eq 0 ] \
    || { echo "the audit does not read the conversion's backup as a shape migration (exit $rc): $(tr '\n' ' ' <<<"$out")"; return 1; }
  # one more changed line, and the backup is plant knowledge overwritten again
  printf -- '- 2026-11-10 — a hand edit\n' >> "$s"
  out="$(python3 "$ROOT/tools/graft-audit.py" "$p" "$TMP/x649seed" 2>&1)" && rc=0 || rc=$?
  [ "$rc" -ne 0 ] && grep -q "knowledge overwrite" <<<"$out" && grep -q "SPEC-0501-orders.md.bak-" <<<"$out" \
    || { echo "a spec changed past the mechanical part still reads as a shape migration (exit $rc): $(tr '\n' ' ' <<<"$out")"; return 1; }
}

collect_case X640 case_dry_run_prints_the_mechanical_part "SPEC_CONVERT_DRY_RUN_PRINTS_THE_MECHANICAL_PART: the dry run prints the report, each contract's present mapping, and writes nothing"
collect_case X641 case_write_needs_the_steward "SPEC_CONVERT_WRITE_NEEDS_THE_STEWARD: --write without --steward-ratified or without a spec path is refused, exit 2, nothing written"
collect_case X642 case_write_adds_only_the_mechanical_part "SPEC_CONVERT_WRITES_ONLY_THE_MECHANICAL_PART: --write adds the form, trust and Check lines only, keeps one backup, and a second write does nothing"
collect_case X643 case_unrecognised_shape_is_named "SPEC_CONVERT_NAMES_AN_UNRECOGNISED_SHAPE: no contract, no metadata section, or a contract heading in a fence is a named error, exit 1, nothing written"
collect_case X649 case_backup_is_audited_as_a_shape_migration "SPEC_CONVERT_BACKUP_IS_AUDITED: graft-audit reads the conversion's backup as SHAPE-MIGRATED while only the mechanical lines differ, and as a knowledge overwrite once another line does"

[ "$CASE_FAILED" -eq 0 ] || exit 1
echo "spec-convert: all cases passed"
