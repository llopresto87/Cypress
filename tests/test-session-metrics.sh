#!/usr/bin/env bash
# test-session-metrics.sh — tools/session-metrics.py (SPEC-0006), the cases the
# consolidation kept (SPEC-0006 §10): the session's own command passes on its
# entry in either order, the span and block-defect findings with their lines,
# exemptions and --since, the heading forms, the exit codes, the line list taken
# from the deliver node, harvest's --all --json, and grep -n line numbers.
# The unreadable changelog is a row in test-lint-audibility.sh; the fresh plant
# is E14 in test-full-install.sh. Each case builds its input under $TMP from the
# shipped protocols/deliver.md. Run one case: bash tests/test-session-metrics.sh case_<name>
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SM="$ROOT/tools/session-metrics.py"
NODE="$ROOT/protocols/deliver.md"
SINCE="2026-10-05"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
CASE=""     # the contract slug the current case carries, named in every failure
fail() { echo "FAIL: ${CASE:+[$CASE] }$*" >&2; [ -f "$TMP/out" ] && cat "$TMP/out" >&2; exit 1; }

# run <expected-rc> <args...> -> output (stdout and stderr) in $TMP/out
run() {
  local want="$1" rc=0; shift
  python3 "$SM" "$@" >"$TMP/out" 2>&1 || rc=$?
  [ "$rc" -eq "$want" ] || fail "expected exit $want, got $rc (args: $*)"
}
# groot <name> -> a fresh graph root whose protocols/deliver.md is the shipped node.
groot() { local d="$TMP/$1"; mkdir -p "$d/protocols"; cp "$NODE" "$d/protocols/deliver.md"; echo "$d"; }
# lineof <file> <exact line> -> its 1-based line number.
lineof() {
  local n; n="$(grep -nxF -- "$2" "$1" | head -1 | cut -d: -f1)"
  [ -n "$n" ] || fail "harness: line not found in $1: $2"; echo "$n"
}
# has_finding <line> <CODE> <label>: a finding line names changelog.md:<line>: <CODE> and <label>.
has_finding() {
  grep -F "changelog.md:$1: $2" "$TMP/out" | grep -qF -- "$3" || fail "no $2 finding at changelog.md:$1 naming '$3'"
}
findings() { grep -cE "^  - .*: $1(:|\$)" "$TMP/out" || true; }
pass_counts() {   # pass_counts <text>...: the first line is the PASS headline and counts each <text>
  head -1 "$TMP/out" | grep -q '^session metrics: PASS' || fail "first line is not 'session metrics: PASS'"
  local t; for t in "$@"; do head -1 "$TMP/out" | grep -qE "(^|[^0-9])$t" || fail "the PASS line does not count '$t'"; done
}
no_headline() { ! grep -qE '^session metrics: (PASS|FAIL)' "$TMP/out" || fail "a run that judged no entry printed a headline"; }
# metrics [Label=value ...] -> a filled nine-line block; a value DROP removes the line.
metrics() {
  local -A v=([Tier]="T2 covered (reclassified: none)" [Spawns]="3 (tester×1, implementer×2)"
    [Route bands]="HIGH×2 MEDIUM×1 — overrides: none" [Retries]="none" [Gates]="6 run, 1 failed then fixed"
    [Full-suite runs]="2 (1 red)" [Serial waits]="1" [Overflow notes]="none" [Quality]="review 0 Critical / 1 Major")
  local kv k
  for kv in "$@"; do k="${kv%%=*}"; v[$k]="${kv#*=}"; done
  for k in "Tier" "Spawns" "Route bands" "Retries" "Gates" "Full-suite runs" "Serial waits" "Overflow notes" "Quality"; do
    [ "${v[$k]}" = DROP ] && continue
    if [ -z "${v[$k]}" ]; then echo "- $k:"; else echo "- $k: ${v[$k]}"; fi
  done
}

# X399 (and failures BLOCK_BORROWED_FROM_NEXT_ENTRY, NESTED_DELIVERY_HEADING)
# Asserts SPEC-0006 METRICS_BLOCK_MISSING_FAILS.
# Asserts SPEC-0006 METRICS_DATED_HEADING_ENDS_ENTRY.
case_entry_span() {
  CASE=METRICS_BLOCK_MISSING_FAILS
  local r f a c d; r="$(groot span)"; f="$r/changelog.md"
  # a: blockless, a nested T3 delivery with its own block below it.
  # c: blockless, a same-level graft entry with a block after it.
  # d: blockless, a dated ## close-out with a block below it.
  { printf '# Delivery — a — 2026-10-05\n\n## Files changed\n- x:a\n\n## T3 delivery — b — 2026-10-05\n\n### Session metrics\n'
    metrics "Tier=T3"
    printf '\n# Delivery — c — 2026-10-05\n\n# Graft — g — 2026-10-05\n\n## Session metrics\n'; metrics
    printf '\n# Delivery — d — 2026-10-05\n\n## Older — canonize close-out — 2026-10-05\n\n### Session metrics\n'; metrics; } >"$f"
  a="$(lineof "$f" '# Delivery — a — 2026-10-05')"; c="$(lineof "$f" '# Delivery — c — 2026-10-05')"
  d="$(lineof "$f" '# Delivery — d — 2026-10-05')"
  run 1 --root "$r" --since "$SINCE"
  has_finding "$a" METRICS_BLOCK_MISSING changelog.md   # NESTED_DELIVERY_HEADING
  has_finding "$c" METRICS_BLOCK_MISSING changelog.md   # BLOCK_BORROWED_FROM_NEXT_ENTRY
  has_finding "$d" METRICS_BLOCK_MISSING changelog.md   # METRICS_DATED_HEADING_ENDS_ENTRY
  [ "$(findings 'METRICS_[A-Z_]+')" -eq 3 ] || fail "expected exactly three findings: b is judged on its own block"
  echo "  X399 a blockless entry fails on its heading; no nested, later or close-out block is borrowed — OK"
}

# X400
# Asserts SPEC-0006 METRICS_LINE_MISSING_FAILS.
# Asserts SPEC-0006 METRICS_LINE_EMPTY_FAILS.
# Asserts SPEC-0006 METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS.
# Asserts SPEC-0006 METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED.
case_block_defects() {
  CASE=METRICS_LINE_MISSING_FAILS
  local r f b; r="$(groot defects)"; f="$r/changelog.md"
  { printf '# Delivery — t — 2026-10-05\n\n## Session metrics\n'
    metrics "Serial waits=DROP" "Retries=" "Gates=<run/failed-then-fixed counts>" \
            "Spawns=not recorded" "Overflow notes=not recorded: the host shows no notes"; } >"$f"
  b="$(lineof "$f" '## Session metrics')"
  run 1 --root "$r" --since "$SINCE"
  has_finding "$b" METRICS_LINE_MISSING "Serial waits"
  has_finding "$(lineof "$f" '- Retries:')" METRICS_LINE_EMPTY Retries
  has_finding "$(lineof "$f" '- Gates: <run/failed-then-fixed counts>')" METRICS_LINE_EMPTY Gates
  has_finding "$(lineof "$f" '- Spawns: not recorded')" METRICS_REASON_MISSING Spawns
  [ "$(findings 'METRICS_[A-Z_]+')" -eq 4 ] || fail "expected exactly four findings: 'not recorded: <reason>' is filled"
  echo "  X400 a missing line, a blank, a slot and a bare 'not recorded' each fail on their line — OK"
}

# X404
# Asserts SPEC-0006 METRICS_LOW_TIER_EXEMPT.
# Asserts SPEC-0006 METRICS_COMPACT_ENTRY_EXEMPT.
case_exemptions() {
  CASE=METRICS_LOW_TIER_EXEMPT
  local r; r="$(groot exempt)"
  printf '## T0 delivery — q — 2026-10-05\n\n# Delivery — r — 2026-10-05\n\n## Session metrics\n- Tier: T1 (reclassified: none)\n\n# Delivery (compact) — s — 2026-10-05\n' >"$r/changelog.md"
  run 0 --root "$r" --since "$SINCE"
  pass_counts "3 exempt"
  echo "  X404 T0, T1 and compact entries are exempt — OK"
}

# X406 (and failure PRE_RULE_ENTRY)
# Asserts SPEC-0006 METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED.
case_before_since_not_judged() {
  CASE=METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED
  local r; r="$(groot since)"
  { printf '# Delivery — older — 2026-10-04\n\n- a.py:old\n\n# Delivery — new — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$r/changelog.md"
  run 0 --root "$r" --since "$SINCE"
  pass_counts "1 delivery entr" "1 filled"
  echo "  X406 an entry dated before --since is not judged — OK"
}

# X407 (and failures HEADING_NOT_RECOGNIZED, UNDATED_DELIVERY_HEADING)
# Asserts SPEC-0006 METRICS_NO_ENTRY_SINCE_FAILS.
case_no_entry_since() {
  CASE=METRICS_NO_ENTRY_SINCE_FAILS
  local r u; r="$(groot noentry)"
  { printf '# Delivery — older — 2026-10-01\n\n## Session metrics\n'; metrics
    printf '\n## Add the importer — canonize close-out — 2026-10-05\n\n# Delivery — undated\n'; } >"$r/changelog.md"
  u="$(lineof "$r/changelog.md" '# Delivery — undated')"
  run 1 --root "$r" --since "$SINCE"
  [ "$(findings NO_DELIVERY_ENTRY)" -eq 1 ] || fail "expected exactly one NO_DELIVERY_ENTRY"
  grep -qF "no delivery entry dated on or after $SINCE" "$TMP/out" || fail "the message does not name --since"
  grep -qF '`Delivery — <title> — YYYY-MM-DD`' "$TMP/out" || fail "the template heading form is not named"
  grep -qF '`T<n> delivery — <title> — YYYY-MM-DD`' "$TMP/out" || fail "the tier heading form is not named"
  grep -E '^ *note:' "$TMP/out" | grep -qF "changelog.md:$u:" || fail "no note: line names the undated heading at line $u"
  echo "  X407 no entry since the date fails and names the forms; the undated heading gets a note — OK"
}

# X408
# Asserts SPEC-0006 METRICS_MISSING_CHANGELOG_FAILS.
case_missing_changelog() {
  CASE=METRICS_MISSING_CHANGELOG_FAILS
  local r; r="$(groot nochangelog)"
  run 1 --root "$r" --since "$SINCE"
  grep -E ': NO_DELIVERY_ENTRY:' "$TMP/out" | grep -qF "changelog.md does not exist" \
    || fail "no NO_DELIVERY_ENTRY finding saying '<path> does not exist'"
  echo "  X408 a missing changelog is NO_DELIVERY_ENTRY — OK"
}

# X409
# Asserts SPEC-0006 METRICS_SINCE_REQUIRED.
case_since_required() {
  CASE=METRICS_SINCE_REQUIRED
  local r; r="$(groot sincereq)"
  { printf '# Delivery — t — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$r/changelog.md"
  run 2 --root "$r"
  grep -qF -- "--since" "$TMP/out" || fail "no --since: the usage message does not name --since"; no_headline
  run 2 --root "$r" --since 05/10/2026
  grep -qF -- "--since" "$TMP/out" || fail "--since 05/10/2026: the usage message does not name --since"; no_headline
  echo "  X409 --since is required and must be YYYY-MM-DD — OK"
}

# X410
# Asserts SPEC-0006 METRICS_ENTRY_HEADINGS_RECOGNIZED.
# Asserts SPEC-0006 METRICS_SECTION_HEADINGS_STAY_IN_ENTRY.
case_entry_headings() {
  CASE=METRICS_ENTRY_HEADINGS_RECOGNIZED
  local r; r="$(groot headings)"
  # b: the T3 form; a: the template form written flat (its sections at ## too);
  # c (fenced), Standalone, Delivery-pipeline and Delivery: are not entries.
  { printf '## T3 delivery — b — 2026-10-05\n\n### Session metrics\n'; metrics "Tier=T3"
    printf '\n## Delivery — a — 2026-10-05\n\n## Files changed\n- x:a\n\n## Gates run\n- unit: executed\n\n## Session metrics\n'; metrics
    printf '\n## Delivery-pipeline cache fix — e — 2026-10-05\n\n## Delivery: moved assets to a CDN — f — 2026-10-05\n'
    printf '\n## Notes\n\n```markdown\n# Delivery — c — 2026-10-05\n```\n\n## Standalone delivery — d — 2026-10-05\n'; } >"$r/changelog.md"
  run 0 --root "$r" --since "$SINCE"
  pass_counts "2 delivery entr" "2 filled"
  echo "  X410 the two taught forms count, a flat entry keeps its block; the look-alikes do not count — OK"
}

# X412 (and failure PLANT_CUSTOMIZED_BLOCK)
# Asserts SPEC-0006 METRICS_LABELS_FROM_DELIVER_NODE.
case_labels_from_node() {
  CASE=METRICS_LABELS_FROM_DELIVER_NODE
  local r; r="$(groot tokens)"
  sed 's/^- Quality:/- Tokens: <per spawn>\n- Quality:/' "$NODE" >"$TMP/deliver-tokens.md"
  { printf '# Delivery — t — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$r/changelog.md"
  run 1 --root "$r" --deliver "$TMP/deliver-tokens.md" --since "$SINCE"
  has_finding "$(lineof "$r/changelog.md" '## Session metrics')" METRICS_LINE_MISSING Tokens
  [ "$(findings 'METRICS_[A-Z_]+')" -eq 1 ] || fail "expected exactly one finding (Tokens)"
  echo "  X412 the line list comes from the deliver node --deliver names — OK"
}

# X413 (and failure DELIVER_NODE_REWORDED). Reads the shipped node.
# Asserts SPEC-0006 METRICS_SHIPPED_DELIVER_NODE_PARSES.
case_shipped_deliver_node() {
  CASE=METRICS_SHIPPED_DELIVER_NODE_PARSES
  local l n=0
  run 0 --labels --deliver "$NODE"
  grep -qx 'Tier' "$TMP/out" || fail "the shipped deliver node's labels do not include Tier"
  while IFS= read -r l; do
    grep -qF -- "- $l:" "$NODE" || fail "printed label '$l' is not a '- $l:' item in protocols/deliver.md"
    n=$((n + 1))
  done <"$TMP/out"
  # The shipping condition (§9): deliver tells the session to run the lint on its entry.
  grep -qE 'session-metrics\.py --since .*--entry' "$NODE" \
    || fail "deliver.md lacks the shipping-condition wording: session-metrics.py --since … --entry"
  echo "  X413 the shipped deliver node parses ($n labels) and names the run — OK"
}

# X414
# Asserts SPEC-0006 METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD.
case_deliver_node_unparseable() {
  CASE=METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD
  local r; r="$(groot nofence)"
  grep -vE '^ {0,3}(```|~~~)' "$NODE" >"$TMP/deliver-nofence.md"
  { printf '# Delivery — t — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$r/changelog.md"
  run 2 --root "$r" --deliver "$TMP/deliver-nofence.md" --since "$SINCE"
  grep -qF "deliver-nofence.md" "$TMP/out" || fail "the message does not name the deliver node's path"
  grep -qi "no session metrics template" "$TMP/out" || fail "the message does not say no Session metrics template was found"
  no_headline
  echo "  X414 a deliver node with no fenced template exits 2, named — OK"
}

# X416
# Asserts SPEC-0006 METRICS_ALL_REPORTS_EVERY_ENTRY.
case_all_json() {
  CASE=METRICS_ALL_REPORTS_EVERY_ENTRY
  local r; r="$(groot all)"
  { printf '## Delivery — one — 2026-10-05\n\n### Session metrics\n'; metrics "Tier=  T3 (reclassified: none)   "
    printf '\n## Delivery — two — 2026-10-03\n\n### Files changed\n- b.py:b\n\n## Delivery (compact) — three — 2026-10-02\n\n## Some heading — a grow report — 2026-10-01\n\n### Session metrics\n'
    metrics; } >"$r/changelog.md"
  run 0 --root "$r" --all --json
  python3 - "$TMP/out" <<'PY' || fail "the --all --json records are not the four expected (see the line above)"
import json, sys
recs = json.load(open(sys.argv[1], encoding="utf-8"))
got = [(r["status"], r["marker"]) for r in recs]
want = [("filled", "delivery"), ("incomplete", "delivery"), ("exempt", "compact"), ("filled", "unmarked")]
if got != want: sys.exit(f"(status, marker) per record {got}, want {want}")
if [r["line"] for r in recs] != sorted(r["line"] for r in recs): sys.exit("records are not in file order")
if recs[0]["lines"].get("Tier") != "T3 (reclassified: none)": sys.exit(f"Tier not trimmed: {recs[0]['lines'].get('Tier')!r}")
if recs[1]["lines"] != {}: sys.exit(f"the entry with no block must carry lines {{}}, got {recs[1]['lines']!r}")
PY
  echo "  X416 --all --json reports every entry in file order with raw values — OK"
}

# X417 (and failures SAME_DAY_EARLIER_ENTRY, ENTRY_LINE_NOT_A_DELIVERY_HEADING, HEADING_NOT_RECOGNIZED; AC-9)
# Asserts SPEC-0006 METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE.
# Asserts SPEC-0006 METRICS_FILLED_ENTRY_PASSES.
# Asserts SPEC-0006 METRICS_LEADING_BOM_IGNORED.
case_other_entry_is_a_note() {
  CASE=METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE
  local r f e m; r="$(groot other)"; f="$r/changelog.md"
  # (a) the session's own filled entry below another session's blockless one.
  { printf '# Delivery — earlier — 2026-10-05\n\n- a.py:another session\n\n# Delivery — mine — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$f"
  e="$(lineof "$f" '# Delivery — earlier — 2026-10-05')"; m="$(lineof "$f" '# Delivery — mine — 2026-10-05')"
  run 0 --root "$r" --since "$SINCE" --entry "$m"
  pass_counts "1 filled"
  grep -E '^  note:' "$TMP/out" | grep -F "changelog.md:$e:" | grep -qF METRICS_BLOCK_MISSING \
    || fail "(a) no '  note:' line names line $e and METRICS_BLOCK_MISSING"
  ! grep -q '^  - ' "$TMP/out" || fail "(a) another entry's defect was reported as a finding"
  # (d) newest first, and the file starts with a byte-order mark: own entry on line 1.
  { printf '\xef\xbb\xbf# Delivery — mine — 2026-10-05\n\n## Session metrics\n'; metrics
    printf '\n# Delivery — earlier — 2026-10-05\n\n- a.py:another session\n'; } >"$f"
  e="$(grep -n 'Delivery — earlier' "$f" | cut -d: -f1)"
  run 0 --root "$r" --since "$SINCE" --entry 1
  pass_counts "1 filled"
  grep -E '^  note:' "$TMP/out" | grep -F "changelog.md:$e:" | grep -qF METRICS_BLOCK_MISSING \
    || fail "(d) no '  note:' line names line $e and METRICS_BLOCK_MISSING"
  ! grep -q '^  - ' "$TMP/out" || fail "(d) another entry's defect was reported as a finding"
  # (c) --entry on a heading in a form the reader does not accept.
  CASE=HEADING_NOT_RECOGNIZED
  { printf '# mine — canonize close-out — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$f"
  run 2 --root "$r" --since "$SINCE" --entry 1
  grep -F 'ENTRY_LINE_NOT_A_DELIVERY_HEADING' "$TMP/out" | grep -qF ':1:' || fail "(c) no ENTRY_LINE_NOT_A_DELIVERY_HEADING naming :1:"
  grep -qF 'Delivery — <title> — YYYY-MM-DD' "$TMP/out" || fail "(c) the template heading form is not named"
  grep -qF 'T<n> delivery — <title> — YYYY-MM-DD' "$TMP/out" || fail "(c) the tier heading form is not named"
  no_headline
  echo "  X417 --entry passes on the session's own entry in either order; another entry's defect is a note — OK"
}

# X423
# Asserts SPEC-0006 METRICS_LINES_COUNTED_AS_GREP_DOES.
case_lines_as_grep() {
  CASE=METRICS_LINES_COUNTED_AS_GREP_DOES
  local r f n; r="$(groot asgrep)"; f="$r/changelog.md"
  # Lines 3-7 hold U+2028, a form feed, NEL, \x1c and a lone CR: each is one line to grep -n.
  { printf '# Changelog\n\na\xe2\x80\xa8b\n\x0c\nc\xc2\x85d\ne\x1cf\ng\rh\n\n# Delivery — x — 2026-10-05\n\n## Session metrics\n'; metrics; } >"$f"
  n="$(grep -n 'Delivery — x' "$f" | cut -d: -f1)"
  [ "$n" = 9 ] || fail "harness: grep -n puts the heading on line '$n', not 9"
  run 0 --root "$r" --since "$SINCE" --entry "$n"
  pass_counts "1 filled"
  head -1 "$TMP/out" | grep -qF "(line $n)" || fail "the PASS line does not name (line $n)"
  echo "  X423 lines are counted as grep -n counts them — OK"
}

ALL="case_entry_span case_block_defects case_exemptions case_before_since_not_judged
case_no_entry_since case_missing_changelog case_since_required case_entry_headings
case_labels_from_node case_shipped_deliver_node case_deliver_node_unparseable
case_all_json case_other_entry_is_a_note case_lines_as_grep"

if [ "$#" -gt 0 ]; then
  for c in "$@"; do "$c"; done
else
  for c in $ALL; do "$c"; done
  echo "session-metrics: PASS ($(wc -w <<<"$ALL" | tr -d ' ') cases)"
fi
