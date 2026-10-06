#!/usr/bin/env bash
# grill-lint contract: plants one plan defect at a time on a valid plan and
# asserts the lint names it; then the fence rules, the --waves report
# (SPEC-0005 §6 "Wave report"), the seed ledger layout and external decisions.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/helpers/lintcase.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

G="$TMP/docs/graph"
mkdir -p "$G/plans" "$G/specs" "$G/libraries" "$G/templates"
cp "$ROOT/templates/knowledge-graph/grill-lint.py" "$G/"
cp "$ROOT/templates/grill.template.md" "$G/templates/"
touch "$G/libraries/sqlalchemy.md"
printf -- '- **Status:** active\n\n### Contract: SUBMIT_VALID_FORM\n### Contract: REJECT_BAD_SCHEMA\n' \
  > "$G/specs/SPEC-0001-forms.md"

# The valid plan, inline form (it clears a ledger a previous case left).
# Arguments: DEP1=, DEP2=, NEXT= and "sub:<old>=<new>" edits.
write_plan() {
rm -rf "$G/plans/grill"
python3 - "$G/plans/grill.md" "$@" <<'PY'
import sys, re
from pathlib import Path
out = Path(sys.argv[1]); edits = dict(a.split("=", 1) for a in sys.argv[2:])
plan = """# grill — forms

## 0. Metadata
- Project: forms  - Date: 2026-09-09  - Spec: SPEC-0001

## 1. Artifact Discovery
- Existing files inspected: src/forms/handler.py
- Existing docs inspected: docs/graph/index.md
- Existing tests inspected: tests/test_forms.py
- Existing specs inspected: docs/graph/specs/SPEC-0001-forms.md
- Existing architecture signals: none — greenfield module
- Libraries already wikified: docs/graph/libraries/sqlalchemy.md
- External sources downloaded: none — nothing new
- Constraints discovered: none — see §4

## 2. Shared Understanding
Persist valid submissions; reject bad schemas with 422.

## 3. User Goal
- Primary user: operator  - Primary outcome: durable submissions

## 4. Operating Constraints
- Runtime constraints: python 3.12

## 5. Research Summary
- Wikified libraries (link to docs/graph/libraries/<name>.md): docs/graph/libraries/sqlalchemy.md

## 6. Decisions Made
| Decision | Evidence | Reversibility |
|---|---|---|
| Use the existing session factory | src/db.py | two-way |

## 7. Options Considered
- Raw SQL — rejected: duplicates the schema.

## 8. Architecture Plan
handler -> validator -> store

## 9. Implementation Plan

### Increment 1 — Validate schema
- Spec contracts: SPEC-0001/REJECT_BAD_SCHEMA
- Files touched: src/forms/validate.py
- Tests to write (RED): test_reject_bad_schema
- Behavior added: 422 on schema mismatch
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: DEP1

### Increment 2 — Persist submissions
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM
- Files touched: src/forms/store.py
- Tests to write (RED): test_submit_valid_form_persists
- Behavior added: durable store
- Gate: integration test
- Rollback path: revert; no migration
- Effort: 1 cycle
- Depends on: DEP2

## 10. Verification Plan
not applicable — the standard gates cover this plan.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Verification |
|---|---:|---:|---|---|
| Session leak | low | high | context manager | test_store_closes_session |

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|
| 1 | Retention period? | compliance | 30 days | ask product | product | — |

## 13. Done Criteria
Both contracts green in CI.

## 14. Recommended Next Step
NEXT

## 15. Changelog
- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).
"""
plan = plan.replace("DEP1", edits.get("DEP1", "none"))
plan = plan.replace("DEP2", edits.get("DEP2", "increment 1 (schema validation); docs/graph/libraries/sqlalchemy.md"))
plan = plan.replace("NEXT", edits.get("NEXT", "Enter test-first for increment 1."))
for k, v in edits.items():
    if k.startswith("sub:"):
        plan = plan.replace(k[4:], v)
out.write_text(plan)
PY
}
# The ledger form: §9 becomes an index of rows, one file per increment.
write_ledger() {   # $1 = optional body override for increment 2's file
python3 - "$G/plans" "${1:-}" <<'PYEOF'
import sys, pathlib, re
plans = pathlib.Path(sys.argv[1]); override = sys.argv[2]
plan = (plans / "grill.md").read_text()
# Replace §9's inline increments with an index pointing at child files.
start = plan.index("## 9. Implementation Plan")
end = plan.index("## 10.")
inline = plan[start:end]
blocks = re.split(r"(?=^### Increment )", inline, flags=re.M)[1:]
(plans / "grill").mkdir(exist_ok=True)
rows = []
for b in blocks:
    n = int(re.match(r"### Increment (\d+)", b).group(1))
    title = re.match(r"### Increment \d+\s*[—-]?\s*(.*)", b).group(1).strip()
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    rel = f"plans/grill/increment-{n:02d}-{slug}.md"
    body = override if (override and n == 2) else b
    (plans / "grill" / f"increment-{n:02d}-{slug}.md").write_text(body)
    rows.append(f"| {n} | {title} | planned | `{rel}` |")
index = ("## 9. Implementation Plan\n\n"
         "| # | Increment | Status | Detail |\n|---|---|---|---|\n"
         + "\n".join(rows) + "\n\n")
(plans / "grill.md").write_text(plan[:start] + index + plan[end:])
PYEOF
}

# Every plan state and flag set the numbered cases lint is recorded, so X377
# can lint each again with and without --waves.
REC="$TMP/lint-records"
mkdir -p "$REC"
record_lint() {
  local d a
  d="$REC/$(printf '%03d' "$(ls "$REC" | wc -l | tr -d ' ')")"
  mkdir -p "$d/state"
  if [ -d "$G/plans" ]; then cp -R "$G/plans" "$d/state/plans"; fi
  if [ -d "$G/decisions" ]; then cp -R "$G/decisions" "$d/state/decisions"; fi
  : > "$d/args"
  for a in "$@"; do printf '%s\0' "$a" >> "$d/args"; done
}
lint() { record_lint "$@"; python3 "$G/grill-lint.py" "$@"; }
fails() { expect_rc 1 "$1" -- lint; }   # the lint exits 1 and names $1

# 1. clean plan -> PASS; --list prints the increment graph
write_plan
expect_rc 0 '2 Persist submissions  <- 1' -- lint --list
# 2. forward dependency: increment 1 depends on increment 2
write_plan DEP1="increment 2"; fails 'increment 1: depends on increment 2, listed after it'
# 3. dependency on a row that does not exist
write_plan DEP1="increment 9"; fails 'increment 9, which does not exist'
# 4. blank Depends on
write_plan DEP1=""; fails 'increment 1: `Depends on:` is blank'
# 5. §5 silent about a library §9 depends on
write_plan "sub:- Wikified libraries (link to docs/graph/libraries/<name>.md): docs/graph/libraries/sqlalchemy.md=- Key findings: nothing new"
fails '§5: silent about docs/graph/libraries/sqlalchemy.md, which increment 2 depends on'
# 6. a library page the plan names does not exist
write_plan DEP2="increment 1; docs/graph/libraries/redis.md"
fails 'docs/graph/libraries/redis.md is named by the plan but does not exist'
# 7. an invented contract, and then the real contract has no increment
write_plan "sub:SPEC-0001/REJECT_BAD_SCHEMA=SPEC-0001/REJECT_EVERYTHING"
fails 'SPEC-0001/REJECT_EVERYTHING is not a'
fails 'contract REJECT_BAD_SCHEMA appears in no §9 increment'
# 8. §14 is a list
write_plan NEXT=$'- enter test-first\n- also refactor the store'; fails 'one action, not a list'
# 9. a blank §1 line
write_plan "sub:- Existing tests inspected: tests/test_forms.py=- Existing tests inspected:"
fails '§1: `- Existing tests inspected:` has no path'
# 10. [verify] in §9 fails; in §6 only warns
write_plan "sub:- Behavior added: durable store=- Behavior added: durable store [verify]"
fails 'increment 2: carries `[verify]`'
write_plan "sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory [verify] | src/db.py | two-way |"
expect_rc 0 'WARN §6' -- lint
# 11. a section left as the form's own prose is not populated
write_plan "sub:not applicable — the standard gates cover this plan.=Covered by the project's standard gates — see"
fails '§10: not populated'
# 12. --warn reports but exits 0
write_plan DEP1="increment 2"; expect_rc 0 '' -- lint --warn

# 14. the ledger form lints clean, and --list resolves increments through the index
write_plan; write_ledger
expect_rc 0 '2 Persist submissions  <- 1' -- lint --list
# 15. an index row pointing at a file that does not exist
write_plan; write_ledger
rm "$G/plans/grill/increment-02-persist-submissions.md"; fails 'increment 2'
# 16. an increment file nobody indexes
write_plan; write_ledger
cp "$G/plans/grill/increment-01-validate-schema.md" "$G/plans/grill/increment-07-orphaned.md"
fails 'plans/grill/increment-07-orphaned.md is not indexed'
# 17. the required fields are enforced inside the increment's own file
write_plan
write_ledger "### Increment 2 — Persist submissions
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM
- Tests to write (RED): tests/test_forms.py::test_persist
- Rollback path: revert the commit
"
fails 'Depends on'
# 18. document order, not numeric: an appended out-of-number increment is valid
write_plan
python3 "$ROOT/tests/fixtures/grill/append_order.py" "$G/plans/grill.md"
expect_rc 0 '' -- lint
# 19. an index row may not point outside plans/grill/ (an absolute path)
write_plan; write_ledger
sed -i.bak 's#`plans/grill/increment-02[^`]*`#`/tmp/plans/grill/x.md`#' "$G/plans/grill.md" && rm -f "$G/plans/grill.md.bak"
fails 'points outside plans/grill/'
# 19b. ...nor beside the ledger inside plans/ (plans/other/grill/x.md)
write_plan; write_ledger
mkdir -p "$G/plans/other/grill"
cp "$G/plans/grill/increment-02-persist-submissions.md" "$G/plans/other/grill/"
sed -i.bak 's#`plans/grill/\(increment-02[^`]*\)`#`other/grill/\1`#' "$G/plans/grill.md" && rm -f "$G/plans/grill.md.bak"
grep -q '`other/grill/increment-02' "$G/plans/grill.md" || { echo "fixture: no increment-02 index row to repoint"; exit 1; }
fails 'points outside plans/grill/'
# 20. the index row's number must match the file it points at
write_plan; write_ledger
sed -i.bak 's/^### Increment 2/### Increment 5/' "$G/plans/grill/increment-02-persist-submissions.md" && rm -f "$G/plans/grill/increment-02-persist-submissions.md.bak"
fails 'index says increment 2'
# 21. an index row with extra columns and a markdown link still resolves
write_plan; write_ledger
python3 "$ROOT/tests/fixtures/grill/link_row.py" "$G/plans/grill.md"
expect_rc 0 '' -- lint
# 22. an orphan child under any name, at any depth
write_plan; write_ledger
mkdir -p "$G/plans/grill/2026"
cp "$G/plans/grill/increment-01-validate-schema.md" "$G/plans/grill/2026/inc-99.md"
fails 'inc-99.md is not indexed'
# 23. a decision cited by identifier must be filed; both filename forms resolve
write_plan "sub:| Decision | Evidence | Reversibility |=| Decision | Evidence | Reversibility | ADR |" \
           "sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory | src/db.py | two-way | ADR-0002 |"
fails 'ADR-0002 is named by the plan but is not filed'
mkdir -p "$G/decisions"
printf -- '---\nstatus: proposed\nstatus_date: 2026-09-09\nowner: architect\n---\n\n# ADR-0002: session factory\n' \
  > "$G/decisions/adr-0002-session-factory.md"
expect_rc 0 '' -- lint
mv "$G/decisions/adr-0002-session-factory.md" "$G/decisions/0002-session-factory.md"
expect_rc 0 '' -- lint
rm -rf "$G/decisions"
# 25. an increment heading outside §9 (well formed; only its place is wrong)
CHANGELOG='- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).'
write_plan "sub:${CHANGELOG}=${CHANGELOG}

## 16. Plan for a second spec

### Increment 9 — orphan
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM
- Files touched: src/forms/export.py
- Tests to write (RED): test_export_orphan
- Behavior added: export
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none
"
fails 'outside §9'

# 24, 27-32. The fence rules (CommonMark): a fenced example is not the plan.
# Each snippet lints PASS; misreading its fence exposes a plan defect.
# fence_ok <s9|end> <snippet> [crlf]: place it before §10 or after §15.
fence_ok() {
  if [ "$1" = s9 ]; then write_plan "sub:## 10. Verification Plan=${2}## 10. Verification Plan"
  else write_plan "sub:${CHANGELOG}=${CHANGELOG}"$'\n\n'"$2"; fi
  if [ "${3:-}" = crlf ]; then
    python3 -c 'import sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))' "$G/plans/grill.md"
  fi
  expect_rc 0 '' -- lint
}
EX=$'### Increment 3 — example of the shape\n'
FENCE=$'```markdown\n'"$EX"$'- Spec contracts: SPEC-0001/EXAMPLE\n```\n\n'
fence_ok s9 "$FENCE"                                        # 24: not a third increment
fence_ok end $'## 16. Notes\n\n'"$FENCE"                    # 24: not outside §9
fence_ok s9 $'```markdown\n~~~\n'"$EX"$'~~~\n```\n\n'         # 27: ~~~ does not close ```
fence_ok s9 $'~~~markdown\n```\n'"$EX"$'~~~\n\n'              # 27: ``` does not close ~~~
fence_ok s9 $'````markdown\n```\n'"$EX"$'```\n````\n\n'       # 28: a shorter run does not close
fence_ok s9 $'```\n```python\n'"$EX"$'```\n\n'                # 29: an info string does not close
fence_ok end $'```markdown\n### Increment 9 — example, never closed\n- Spec contracts: SPEC-0001/EXAMPLE\n'  # 30: runs to EOF
fence_ok s9 $'```markdown\n'"$EX"$'```\n\n' crlf              # 31: CRLF lints like LF
fence_ok end $'```markdown\n## 9. Implementation Plan\nan example of the header, not the plan\n```\n'  # 32
echo "  cases 24, 27-32: a fenced example is not the plan — OK"

# 26. a field whose value is a fenced block is not blank
write_plan "sub:- Tests to write (RED): test_reject_bad_schema=- Tests to write (RED):
  \`\`\`bash
  pytest tests/test_forms.py::test_reject_bad_schema
  \`\`\`"
expect_rc 0 '' -- lint

# 13. no plan at all -> SKIP, exit 0
rm -rf "$G/plans/grill" "$G/plans/grill.md"
expect_rc 0 '' -- lint
echo "  cases 1-32 — OK"

# ---------------------------------------------------------------------------
# The wave report, `grill-lint.py --waves`. Every label runs through
# collect_case, so each shows its own result in one run (R0.3); the suite exits
# 1 at the end if any failed. Rows of a survivor keep their own label (R1).
# ---------------------------------------------------------------------------
SCHED="$ROOT/tests/fixtures/grill/scheduled_plan.py"
HEADER_3='waves: 3 wave(s), 5 increment(s) — a static schedule from §9; what is committed is not read'
WAVES_5='  wave 1: increment 1 (RED) Reject bad schemas
  wave 1: increment 3 (prose) Document the form
  wave 2: increment 2 (GREEN) Validate schema <- 1
  wave 2: increment 4 (RED) Persist submissions <- 3
  wave 3: increment 5 (GREEN) Store submissions <- 2, 4'
OVERLAP_1_3='^ *WARN §9 increments 1 and 3 may run together and both name tests/test_forms\.py( — .*)?$'
NOT_COMPUTED='^waves: not computed — §9 has dependency defects'

# run the tool unrecorded: WOUT holds stdout and stderr, WRC the exit status
wrun() { WOUT="$(python3 "$G/grill-lint.py" "$@" 2>&1)" && WRC=0 || WRC=$?; }
# the scheduled fixture plan, with KEY=VALUE edits (see scheduled_plan.py)
sched() { write_plan && python3 "$SCHED" "$G/plans/grill.md" "$@"; }
# checks on WOUT/WRC: each prints why and returns 1 when red
has()    { grep -qxF -- "$1" <<<"$WOUT" || { echo "no line '$1'"; return 1; }; }
has_re() { grep -qE -- "$1" <<<"$WOUT" || { echo "no line matching /$1/"; return 1; }; }
lacks()  { ! grep -qE -- "$1" <<<"$WOUT" || { echo "a line matches /$1/: $(grep -m1 -E -- "$1" <<<"$WOUT")"; return 1; }; }
count()  { [ "$(grep -cE -- "$2" <<<"$WOUT")" -eq "$1" ] || { echo "want $1 line(s) matching /$2/"; return 1; }; }
rc()     { [ "$WRC" -eq "$1" ] || { echo "exit $WRC, want $1: $(head -1 <<<"$WOUT")"; return 1; }; }
waves_are() { [ "$(grep -E '^  wave ' <<<"$WOUT")" = "$1" ] || { echo "the wave lines are not: $1"; return 1; }; }
# row <label> <what> <commands>: one table row, run as its own case
row() { ROW="$3"; collect_case "$1" eval_row "$2"; }
eval_row() { set -e; eval "$ROW"; }

case_waves_levels_scheduled_plan() {
  # X361 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON, holds STALE_SCHEDULE; rows X362-X364
  row X361 'the header says static; five wave lines in wave-then-document order' \
    'sched; wrun --waves; has "$HEADER_3"; waves_are "$WAVES_5"; rc 0'
  row X362 'a RED with no dependency rises to wave 1' \
    'sched D4=none; wrun --waves; has "  wave 1: increment 4 (RED) Persist submissions"'
  row X363 'the ledger form prints the same wave lines' \
    'sched; write_ledger; wrun --waves; waves_are "$WAVES_5"'
  row X364 'a library page does not move a wave' \
    'sched D3=docs/graph/libraries/sqlalchemy.md; wrun --waves
     has "  wave 1: increment 3 (prose) Document the form"; has "  wave 2: increment 4 (RED) Persist submissions <- 3"'
}
case_waves_overlap_brace_pair() {
  # X366 GRILL_WAVES_OVERLAP_IS_A_WARNING; rows X367-X370 (X368 holds FALSE_OVERLAP,
  # X369 MISSED_OVERLAP)
  row X366 'one brace group expands; 1 and 3 warn, sequenced 3 and 4 do not' \
    'sched "F3=\`tests/test_{forms,store}.py\`"; wrun --waves
     has_re "$OVERLAP_1_3"; count 1 "may run together"; lacks "increments 3 and 4 may run together"; rc 0'
  row X367 'a glob warns with the path it matches (R0.6)' \
    'sched "F3=\`tests/*.py\`"; wrun --waves; has_re "$OVERLAP_1_3"; rc 0'
  row X368 'a bare name warns with the slashed path; the exit does not change' \
    'sched "F3=\`test_forms.py\`"; wrun; prc=$WRC; wrun --waves; has_re "$OVERLAP_1_3"; rc "$prc"; rc 0'
  row X369 'prose words, §6, resolve() and a dotted key are not paths' \
    'sched "F1=\`tests/test_forms.py\` (the forms.submit key; see §6 and resolve())" \
           "F3=\`docs/forms.md\` (the forms.submit key; see §6 and resolve())"
     wrun --waves; has "$HEADER_3"; lacks "may run together"'
  row X370 'without --waves the brace-pair plan prints no overlap line' \
    'sched "F3=\`tests/test_{forms,store}.py\`"; wrun; lacks "may run together"; rc 0'
}
case_waves_not_computed_forward_dependency() {
  # X373 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT; rows X374-X376, X380, and
  # X371-X372 (GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE)
  row X373 'a forward dependency stops the report; the plain defect line prints' \
    'sched "D1=increment 2"; wrun --waves; has_re "$NOT_COMPUTED"; waves_are ""
     has_re "increment 1: depends on increment 2, listed after it"; rc 1'
  row X374 'the same for a dependency on a missing increment' \
    'sched "D1=increment 9"; wrun --waves; has_re "$NOT_COMPUTED"; waves_are ""
     has_re "increment 9, which does not exist"; rc 1'
  row X375 'under --warn the not-computed report exits 0' \
    'sched "D1=increment 2"; wrun --waves --warn; has_re "$NOT_COMPUTED"; rc 0'
  row X376 'a non-dependency defect leaves the wave lines; exit 1' \
    'sched C1=SPEC-0001/REJECT_EVERYTHING C2=SPEC-0001/REJECT_EVERYTHING; wrun --waves
     waves_are "$WAVES_5"; lacks "^waves: not computed"; rc 1'
  row X380 'duplicate increment numbers: no wave map, the plain exit (R0.13)' \
    'sched N3=1 D4=none; wrun; prc=$WRC; wrun --waves
     has "waves: not computed — §9 has duplicate increment numbers"; waves_are ""; rc "$prc"'
  row X371 'no Phase: field anywhere: unscheduled, nothing more' \
    'write_plan; wrun --waves; has "waves: unscheduled — no §9 increment carries a Phase: field"
     waves_are ""; lacks WARN; rc 0'
  row X372 'a partial phase prints (no phase) and warns once for increment 2' \
    'write_plan $'"'"'sub:- Depends on: none=- Phase: RED\n- Depends on: none'"'"'; wrun --waves
     has_re "^  wave 1: increment 1 \(RED\)"; has_re "^  wave 2: increment 2 \(no phase\)"
     count 1 "WARN §9 increment 2: no Phase: field"; lacks "increment 1: no Phase: field"; rc 0'
}
case_waves_existing_plans_same_exit() {
  # X377 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED (guard): every recorded plan and
  # flag set, linted with and without --waves: the same exit, every plain line in
  # the --waves output in order, no Traceback (R0.7). X378: no plain run prints
  # a report line.
  set -e
  local d n=0 pout prc a
  for d in "$REC"/*; do
    n=$((n + 1)); rm -rf "$G/plans" "$G/decisions"; mkdir -p "$G/plans"
    if [ -d "$d/state/plans" ]; then rm -rf "$G/plans"; cp -R "$d/state/plans" "$G/plans"; fi
    if [ -d "$d/state/decisions" ]; then cp -R "$d/state/decisions" "$G/decisions"; fi
    ARGS=(); while IFS= read -r -d '' a; do ARGS+=("$a"); done < "$d/args"
    wrun ${ARGS[@]+"${ARGS[@]}"}; pout="$WOUT"; prc=$WRC
    lacks '^waves:|^  wave |may run together and both name|: no Phase: field|is not RED, GREEN or prose'  # X378
    wrun ${ARGS[@]+"${ARGS[@]}"} --waves
    lacks '^Traceback'; rc "$prc"
    python3 -c 'import sys
want = sys.argv[1].splitlines(); have = iter(sys.argv[2].splitlines())
sys.exit(0 if all(any(w == h for h in have) for w in want) else 1)' "$pout" "$WOUT" \
      || { echo "record $(basename "$d"): the plain lines are not all in the --waves output, in order"; return 1; }
  done
  [ "$n" -gt 0 ] || { echo "harness: no lint call was recorded"; return 1; }
}

case_waves_levels_scheduled_plan
case_waves_overlap_brace_pair
case_waves_not_computed_forward_dependency
collect_case X377 case_waves_existing_plans_same_exit 'every recorded plan: same exit and plain lines with --waves; no report line without'

# ---------------------------------------------------------------------------
# The seed layout (ADR-0020): docs/plans/<stem>.md, its ledger in
# docs/plans/<stem>/, specs and decisions named by --specs and --decisions.
# Each case lints a fresh copy of tests/fixtures/grill/seed-ledger/.
# ---------------------------------------------------------------------------
SEEDFX="$TMP/seed-ledger"
seedfx() { rm -rf "$SEEDFX"; cp -R "$ROOT/tests/fixtures/grill/seed-ledger" "$SEEDFX"; }
seedlint() {
  WOUT="$(cd "$SEEDFX" && python3 "$G/grill-lint.py" --plan "$SEEDFX/docs/plans/round.md" \
    --specs "$SEEDFX/docs/specs" --decisions "$SEEDFX/docs/decisions" "$@" 2>&1)" && WRC=0 || WRC=$?
}

case_seed_ledger_lints_in_place() {  # G3a
  set -e; seedfx; seedlint --list; rc 0; has_re '^ *2 Persist the round +<- 1'
}
case_seed_ledger_orphan_leaf() {  # G3b
  set -e; seedfx
  cp "$SEEDFX/docs/plans/round/increment-01-a.md" "$SEEDFX/docs/plans/round/increment-09-stray.md"
  seedlint; rc 1; has_re 'increment-09-stray\.md is not indexed'
}
case_seed_ledger_row_outside_refused() {  # G3c: the path still ends round/<file>.md
  set -e; seedfx
  sed -i.bak 's#`docs/plans/round/increment-02-b.md`#`/tmp/docs/plans/round/increment-02-b.md`#' \
    "$SEEDFX/docs/plans/round.md" && rm -f "$SEEDFX/docs/plans/round.md.bak"
  grep -q '/tmp/docs/plans/round/increment-02-b.md' "$SEEDFX/docs/plans/round.md"
  seedlint; rc 1; has_re 'increment 2 points outside'
}
case_seed_ledger_contract_from_specs_flag() {
  # G3d: a contract declared only in --specs resolves; one declared nowhere is
  # "invents a contract". The decoy beside the linter declares neither.
  set -e; seedfx
  printf -- '- **Status:** active\n\n### Contract: DECOY_ONLY\n' > "$G/specs/SPEC-0042-decoy.md"
  trap 'rm -f "$G/specs/SPEC-0042-decoy.md"' RETURN
  seedlint; rc 0; lacks 'SPEC-0042'
  sed -i.bak 's#SPEC-0042/ROUND_ALPHA#SPEC-0042/ROUND_NOWHERE#' "$SEEDFX/docs/plans/round/increment-01-a.md" \
    && rm -f "$SEEDFX/docs/plans/round/increment-01-a.md.bak"
  seedlint; rc 1; has_re 'SPEC-0042/ROUND_NOWHERE is not a .*invents a contract'
}
case_seed_ledger_decision_from_decisions_flag() {  # G3e
  set -e; seedfx; rm -rf "$G/decisions"
  seedlint; lacks 'ADR-0007 is named by the plan but is not filed'; rc 0
}
case_plant_layout_unchanged() {
  # G3f (guard): the plant ledger form lints exactly as the inline form does.
  local inline
  set -e; write_plan; wrun; inline="$WOUT"
  write_ledger; wrun; rc 0
  [ "$WOUT" = "$inline" ] || { echo "ledger form: '$WOUT', inline form: '$inline'"; return 1; }
}
case_external_decision_reported() {
  # G1a, G1b (ADR-0015): seed:ADR-0009, cited twice, with no local ADR-0009,
  # lints PASS and prints one line naming it as external and not checked.
  local line
  set -e; rm -rf "$G/decisions"
  write_plan 'sub:| Decision | Evidence | Reversibility |=| Decision | Evidence | Reversibility | ADR |' \
    'sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory | src/db.py | two-way | seed:ADR-0009 |' \
    'sub:Persist valid submissions; reject bad schemas with 422.=Persist valid submissions; reject bad schemas with 422 (seed:ADR-0009).'
  [ "$(grep -o 'seed:ADR-0009' "$G/plans/grill.md" | wc -l | tr -d ' ')" -eq 2 ]
  wrun; rc 0; count 1 'seed:ADR-0009'
  line="$(grep 'seed:ADR-0009' <<<"$WOUT")"
  grep -q 'external' <<<"$line" && grep -q 'not checked' <<<"$line" \
    || { echo "the line does not say external and not checked: $line"; return 1; }
}

collect_case G3a case_seed_ledger_lints_in_place 'a seed plan and its ledger lint in place'
collect_case G3b case_seed_ledger_orphan_leaf 'an unindexed leaf is an orphan'
collect_case G3c case_seed_ledger_row_outside_refused 'a row outside the ledger is refused'
collect_case G3d case_seed_ledger_contract_from_specs_flag 'contracts resolve from --specs'
collect_case G3e case_seed_ledger_decision_from_decisions_flag 'decisions resolve from --decisions'
collect_case G3f case_plant_layout_unchanged 'the plant ledger form lints as the inline form'
collect_case G1a case_external_decision_reported 'a qualified decision is reported once as external'

case_retired_spec_status_from_frontmatter() {
  # S1: status is read from frontmatter; the modern body line says "see frontmatter".
  # A retired spec's unplanned contract is not demanded; the plan only warns.
  local active; set -e; active="$(cat "$G/specs/SPEC-0001-forms.md")"
  trap 'printf "%s\n" "$active" > "$G/specs/SPEC-0001-forms.md"' RETURN
  printf -- '---\nstatus: retired\n---\n\n- **Status:** see frontmatter (single home)\n\n### Contract: SUBMIT_VALID_FORM\n### Contract: REJECT_BAD_SCHEMA\n' \
    > "$G/specs/SPEC-0001-forms.md"
  write_plan "sub:- Spec contracts: SPEC-0001/REJECT_BAD_SCHEMA=- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM"
  wrun; lacks 'contract REJECT_BAD_SCHEMA appears in no'; has_re 'SPEC-0001 whose status is retired'; rc 0
}
collect_case S1 case_retired_spec_status_from_frontmatter 'a spec retired in frontmatter is not demanded of the plan'

case_misnamed_spec_refused() {
  # M1: a Markdown file in the specs directory that is not `SPEC-*.md` is a
  # misnamed spec: the pattern skipped it, so a plan over it lint-passed with
  # its contracts unseen. It fails and is named; the index and readme are exempt.
  set -e
  trap 'rm -f "$G/specs/install-placement.md" "$G/specs/index.md" "$G/specs/README.md"' RETURN
  cp "$ROOT/tests/fixtures/misnamed-spec/specs/"*.md "$G/specs/"
  write_plan
  wrun; rc 1
  has_re 'misnamed spec, not checked: install-placement\.md'
  lacks 'misnamed spec, not checked: index\.md'
  lacks 'misnamed spec, not checked: README\.md'
}
collect_case M1 case_misnamed_spec_refused 'a misnamed spec fails and is named; index and readme are exempt'

[ "$CASE_FAILED" -eq 0 ] || { echo 'grill lint contract: FAIL (cases above)'; exit 1; }
echo 'grill lint contract: PASS'
