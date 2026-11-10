#!/usr/bin/env bash
# test-cycle.sh — tools/cycle.py, the cycle driver (SPEC-0005 "Cycle driver"):
# one read of the plan, the spawn log, the batch record, the question files and
# git prints the state of a build cycle. Every case runs the placed
# docs/graph/cycle.py in a copy of one fresh install, with a hand-written plan
# (tests/fixtures/cycle/grill.md) and golden outputs written by hand beside it.
# Hashes are taken with python3, which every host of the gate has.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
FX="$ROOT/tests/fixtures/cycle"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0; ok() { echo "  $1 — OK"; }; bad() { echo "  $1 — FAIL: $2"; fail=1; }
G() { git -C "$1" -c user.name=cycle -c user.email=cycle@example.invalid "${@:2}"; }

mkdir "$T/base"
bash "$ROOT/install.sh" claude-code --project-dir "$T/base" >/dev/null 2>&1
setup() {   # a plant copy with the fixture plan and RED files, committed
  cp -R "$T/base" "$1"
  cp "$FX/grill.md" "$1/docs/graph/plans/grill.md"
  mkdir -p "$1/tests"; cp "$FX"/files/tests/* "$1/tests/"
  G "$1" init -q; G "$1" add -A; G "$1" commit -qm "install the seed and open the plan"
}
C() { local d="$1"; shift; (cd "$d" && "$PY" docs/graph/cycle.py "$@"); }
sha() { "$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
REC=docs/graph/plans/u/batch-record.txt

# X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE
P="$T/p1"; setup "$P"
rc=0; out="$(C "$P" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && [[ "$(sed -n 2p <<<"$out")" == "ready RED tester: increments 1, 2, 8 (hardest low, size 7)" ]] \
  && [[ "$(sed -n 3p <<<"$out")" == "ready prose writer: increment 7 (hardest low)" ]] \
  && grep -qx 'expected-red: none' <<<"$out" \
  && [[ "$(tail -1 <<<"$out")" == "ruling pass: not owed — no unruled question entry and nothing held" ]] \
  && ok "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE: a fresh plan prints the ready RED and prose batches" \
  || bad "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE" "rc $rc: $out"
G "$P" commit -q --allow-empty -m "chore: unrelated tidy (increments 1-8)"
rc=0; out="$(C "$P" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -q ' 0 committed' <<<"$out" \
  && ok "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE: an unrelated commit lands nothing" \
  || bad "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE (unrelated)" "rc $rc: $out"
for s in ALPHA BETA GAMMA DELTA; do G "$P" commit -q --allow-empty -m "feat(core): $s — implements SPEC-0001"; done
rc=0; out="$(C "$P" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && ! grep -q '^ready RED\|^ready GREEN' <<<"$out" \
  && grep -q ' 7 committed' <<<"$out" && grep -qx 'landed (inferred from commit subjects): increment(s) 1, 2, 3, 4, 5, 6, 8' <<<"$out" \
  && grep -qx 'landed: unknown (no commit names its contracts) — increment(s) 7' <<<"$out" \
  && ok "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE: commits in the existing format land their increments; one with no contract is unknown" \
  || bad "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE (empty)" "rc $rc: $out"

# X509 CYCLE_DRIVER_NAMES_THE_HOLD_CONDITION and X513 CYCLE_DRIVER_RECORDS_ATOMICALLY
P="$T/p2"; setup "$P"
mkdir -p "$P/docs/graph/plans/u/questions"; cp "$FX/questions/batch-1.md" "$P/docs/graph/plans/u/questions/"
rc=0
o1="$(C "$P" record-red 1 --unit u --file tests/test_alpha.sh --test alpha.case_one)" || rc=$?
C "$P" record-red 2 --unit u --file tests/test_beta.sh --test beta.case_one >/dev/null || rc=$?
C "$P" record-red 8 --unit u --wrong "fails on a missing fixture, not the contract" >/dev/null || rc=$?
G "$P" commit -q --allow-empty -m "docs: the guide"
o2="$(C "$P" record-tip --unit u --fail 7 guide.links)" || rc=$?
[[ $rc -eq 0 ]] && cmp -s "$FX/record.out" "$P/$REC" \
  && [[ "$o1" == "recorded: increment 1 — 1 file(s), 1 test id(s) in $REC" ]] \
  && [[ "$o2" == "recorded: tip — 2 expected-red, 0 not run, 1 failure(s) attributed in $REC" ]] \
  && ok "X513 CYCLE_DRIVER_RECORDS_ATOMICALLY: record-red and record-tip write the record the fixture holds" \
  || bad "X513 CYCLE_DRIVER_RECORDS_ATOMICALLY" "rc $rc; $o1; $o2; $(diff "$FX/record.out" "$P/$REC" 2>&1 | head -20)"
rc=0; out="$(C "$P" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && [[ "$out" == "$(cat "$FX/held.out")" ]] \
  && ok "X509 CYCLE_DRIVER_NAMES_THE_HOLD_CONDITION: each of the three conditions and two dependents, as held.out" \
  || bad "X509 CYCLE_DRIVER_NAMES_THE_HOLD_CONDITION" "rc $rc; $(diff <(echo "$out") "$FX/held.out" | head -20)"

# X513 a re-record with other hashes needs the ruling, and keeps the old hash
P4="$T/p4"; cp -R "$P" "$P4"
old="$(sha "$P4/tests/test_alpha.sh")"
echo 'echo "alpha.case_one: FAIL (amended)"; exit 1' > "$P4/tests/test_alpha.sh"
before="$(sha "$P4/$REC")"
rc=0; C "$P4" record-red 1 --unit u --file tests/test_alpha.sh --test alpha.case_one >/dev/null 2>"$T/err" || rc=$?
[[ $rc -eq 2 ]] && [[ "$(sha "$P4/$REC")" == "$before" ]] && grep -q -- '--ruling' "$T/err" \
  && C "$P4" record-red 1 --unit u --file tests/test_alpha.sh --test alpha.case_one --ruling R1.9 >/dev/null \
  && grep -qx "ruled R1.9 1 $old tests/test_alpha.sh" "$P4/$REC" \
  && grep -qx "red 1 $(sha "$P4/tests/test_alpha.sh") tests/test_alpha.sh" "$P4/$REC" \
  && ok "X513 CYCLE_DRIVER_RECORDS_ATOMICALLY: other hashes are refused without --ruling and kept as ruled with it" \
  || bad "X513 CYCLE_DRIVER_RECORDS_ATOMICALLY (ruling)" "rc $rc: $(cat "$T/err")"

# X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES
P3="$T/p3"; cp -R "$P" "$P3"
echo 'echo changed' > "$P3/tests/test_alpha.sh"; rm "$P3/tests/test_beta.sh"
now="$(sha "$P3/tests/test_alpha.sh")"
rc=0; out="$(C "$P3" --unit u 2>&1)" || rc=$?
[[ $rc -eq 1 ]] && grep -qx "mismatch: tests/test_alpha.sh — increment 1 recorded a1832c32a429, now ${now:0:12}" <<<"$out" \
  && grep -qx "mismatch: tests/test_beta.sh — increment 2 recorded cdd2f37440bb, now missing" <<<"$out" \
  && ok "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES: a changed and a removed RED file are mismatches, exit 1" \
  || bad "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES" "rc $rc: $out"
G "$P3" commit -q --allow-empty -m "feat(core): ALPHA — implements SPEC-0001" && G "$P3" commit -q --allow-empty -m "feat(core): BETA — implements SPEC-0001"
rc=0; out="$(C "$P3" --unit u 2>&1)" || rc=$?
! grep -q '^mismatch:' <<<"$out" && [[ $rc -eq 0 ]] \
  && ok "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES: once the own GREEN commits, the files are not checked" \
  || bad "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES (committed)" "rc $rc: $out"

# X510 a RED committed on its own stays a live lane until its own GREEN commits
P9="$T/p9"; cp -R "$P" "$P9"
C "$P9" record-red 8 --unit u --file tests/test_delta.sh --test delta.case_one >/dev/null
G "$P9" commit -q --allow-empty -m "test: RED increment 8"
G "$P9" commit -q --allow-empty -m "test(core): ALPHA — fails for SPEC-0001"
G "$P9" commit -q --allow-empty -m "docs(spec): ALPHA — implements SPEC-0001 contract text"
G "$P9" commit -q --allow-empty -m "plan: increment 3" -m "feat(core): ALPHA — implements SPEC-0001"
echo 'echo changed' > "$P9/tests/test_delta.sh"; echo 'echo changed' > "$P9/tests/test_alpha.sh"
rc=0; out="$(C "$P9" --unit u 2>&1)" || rc=$?
[[ $rc -eq 1 ]] && grep -qx 'expected-red: delta.case_one' <<<"$out" && grep -q '^mismatch: tests/test_delta.sh ' <<<"$out" \
  && grep -qx 'expected-red: alpha.case_one' <<<"$out" && grep -q '^mismatch: tests/test_alpha.sh ' <<<"$out" \
  && ! grep -q '^landed (inferred' <<<"$out" \
  && ok "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES: a RED, spec or plan commit naming the slug lands nothing: still expected-red and still checked" \
  || bad "X510 CYCLE_DRIVER_CHECKS_THE_RED_HASHES (RED committed alone)" "rc $rc: $out"

# X508 with no git history, landing is unknown and the driver still reports
P10="$T/p10"; cp -R "$P" "$P10"; rm -rf "$P10/.git"
rc=0; out="$(C "$P10" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -qx 'landed: unknown (no commit names its contracts) — increment(s) 1, 2, 3, 4, 5, 6, 7, 8' <<<"$out" \
  && ok "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE: with no git, every increment is landed: unknown, exit 0" \
  || bad "X508 CYCLE_DRIVER_PRINTS_THE_CYCLE_STATE (no git)" "rc $rc: $out"

# X511 CYCLE_DRIVER_REFUSES_MALFORMED_INPUT
refused() {   # $1 label, $2 plant, $3 stderr prefix; the rest is the command
  local label="$1" d="$2" want="$3"; shift 3
  local rc=0 o
  o="$(C "$d" "$@" 2>"$T/err")" || rc=$?
  [[ $rc -eq 2 && -z "$o" && $(wc -l <"$T/err") -eq 1 ]] && grep -q "^cycle: $want" "$T/err" \
    && ok "X511 CYCLE_DRIVER_REFUSES_MALFORMED_INPUT: $label" \
    || bad "X511 CYCLE_DRIVER_REFUSES_MALFORMED_INPUT: $label" "rc $rc; out: $o; err: $(cat "$T/err")"
}
P5="$T/p5"; cp -R "$P" "$P5"; echo "bogus line" >> "$P5/$REC"
refused "an unknown record kind" "$P5" "$REC:10: " --unit u
P5="$T/p6"; cp -R "$P" "$P5"; echo "not json" >> "$P5/docs/graph/plans/spawns.jsonl"
refused "a spawn log line that is not JSON" "$P5" "docs/graph/plans/spawns.jsonl:1: " --unit u
P5="$T/p7"; cp -R "$P" "$P5"
"$PY" - "$P5/docs/graph/plans/grill.md" <<'PY'
import sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("- Effort: low\n- Phase: RED\n- Depends on: none", "- Effort: low\n- Phase: RED\n- Depends on: increment 2", 1))
PY
refused "a forward dependency in §9" "$P5" "docs/graph/plans/grill.md: " --unit u
before="$(sha "$P/$REC")"
refused "record-red of a GREEN" "$P" "docs/graph/plans/grill.md: increment 3 " record-red 3 --unit u --file tests/test_alpha.sh --test x
[[ "$(sha "$P/$REC")" == "$before" ]] || bad "X511 CYCLE_DRIVER_REFUSES_MALFORMED_INPUT" "a refused record-red changed the record"

# X512 CYCLE_DRIVER_IS_DETERMINISTIC_AND_READ_ONLY
s1="$(G "$P" status --porcelain)"; r1="$(sha "$P/$REC")"
a="$(C "$P" --unit u)"; b="$(C "$P" --unit u)"
[[ "$a" == "$b" && "$s1" == "$(G "$P" status --porcelain)" && "$r1" == "$(sha "$P/$REC")" ]] \
  && ok "X512 CYCLE_DRIVER_IS_DETERMINISTIC_AND_READ_ONLY: two runs are byte-identical and write nothing" \
  || bad "X512 CYCLE_DRIVER_IS_DETERMINISTIC_AND_READ_ONLY" "outputs or tree differ"

# X514 CYCLE_DRIVER_RUNS_IN_A_FRESH_PLANT: a spawn log brief.py wrote
P="$T/p8"; setup "$P"
printf 'Write the RED test for increment 1.\n' > "$T/part.txt"
(cd "$P" && "$PY" docs/graph/brief.py --role tester --spawn-id orchestrator.1 \
   --task "write the RED test for increment 1" --route "protocol.test-first RED names tester" \
   --effort "low (fixture)" --part "$T/part.txt" >/dev/null 2>&1)
rc=0; out="$(C "$P" --unit u 2>&1)" || rc=$?
[[ $rc -eq 0 && "$out" == "$(cat "$FX/fresh.out")" ]] && grep -q '"tools/cycle.py"' "$ROOT/manifest.json" \
  && ok "X514 CYCLE_DRIVER_RUNS_IN_A_FRESH_PLANT: the placed tool reads the spawn log brief.py wrote" \
  || bad "X514 CYCLE_DRIVER_RUNS_IN_A_FRESH_PLANT" "rc $rc; $(diff <(echo "$out") "$FX/fresh.out" | head -20)"

if [[ $fail -ne 0 ]]; then echo "cycle driver: FAIL"; exit 1; fi
echo "cycle driver: PASS"
