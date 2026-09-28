#!/usr/bin/env bash
# grill-lint contract: the plan-of-record's shape is a gate. Plants one
# violation at a time on a valid plan and asserts the lint names it — the
# forward dependency an orchestrator misreads as independence, the §5 that
# is silent about a page §9 depends on, the spec contract the plan invents
# or never implements, the blank §1 line, the §14 that is a list — and
# passes when clean, exits 0 under --warn, SKIPs when no plan exists.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

G="$TMP/docs/graph"
mkdir -p "$G/plans" "$G/specs" "$G/libraries" "$G/templates"
cp "$ROOT/templates/knowledge-graph/grill-lint.py" "$G/"
cp "$ROOT/templates/grill.template.md" "$G/templates/"
touch "$G/libraries/sqlalchemy.md"
printf -- '- **Status:** active\n\n### Contract: SUBMIT_VALID_FORM\n### Contract: REJECT_BAD_SCHEMA\n' \
  > "$G/specs/SPEC-0001-forms.md"

# The valid plan: derived from the template so the form's own prose is
# subtracted; every section carries content; §9 in dependency order.
write_plan() {
# Reset the ledger directory: this writes the INLINE form, and children left by
# a previous case would (correctly) read as orphans.
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

# Every plan state and flag set cases 1 to 32 lint is recorded, so the wave
# block at the end can lint each again with and without --waves (X377, X378).
REC="$TMP/lint-records"
mkdir -p "$REC"
record_lint() {
  local n d a
  n="$(ls "$REC" | wc -l | tr -d ' ')"
  d="$REC/$(printf '%03d' "$n")"
  mkdir -p "$d/state"
  if [ -d "$G/plans" ]; then cp -R "$G/plans" "$d/state/plans"; fi
  if [ -d "$G/decisions" ]; then cp -R "$G/decisions" "$d/state/decisions"; fi
  : > "$d/args"
  for a in "$@"; do printf '%s\0' "$a" >> "$d/args"; done
}
lint() { record_lint "$@"; python3 "$G/grill-lint.py" "$@"; }
expect_fail() {  # $1 = pattern the report must name, then a description
  local pat="$1" why="$2" out rc
  out="$(lint 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 1 ]] || { echo "expected exit 1 ($why), got $rc" >&2; echo "$out" >&2; exit 1; }
  grep -q -- "$pat" <<<"$out" || { echo "report does not name it ($why): want /$pat/" >&2; echo "$out" >&2; exit 1; }
}

# 1. clean plan -> PASS; --list prints the increment graph
write_plan
out="$(lint --list)" || { echo "clean plan failed:"; echo "$out"; exit 1; }
grep -q -- '2 Persist submissions  <- 1' <<<"$out" || { echo "--list did not print the graph" >&2; echo "$out" >&2; exit 1; }

# 2. forward dependency: increment 1 depends on increment 2
write_plan DEP1="increment 2"
expect_fail 'increment 1: depends on increment 2, listed after it' 'forward dependency'

# 3. dependency on a row that does not exist
write_plan DEP1="increment 9"
expect_fail 'increment 9, which does not exist' 'dangling increment'

# 4. blank Depends on
write_plan DEP1=""
expect_fail 'increment 1: `Depends on:` is blank' 'blank dependency'

# 5. §5 silent about a library §9 depends on
write_plan "sub:- Wikified libraries (link to docs/graph/libraries/<name>.md): docs/graph/libraries/sqlalchemy.md=- Key findings: nothing new"
expect_fail '§5: silent about docs/graph/libraries/sqlalchemy.md, which increment 2 depends on' '§5 silence'

# 6. a library page the plan names does not exist
write_plan DEP2="increment 1; docs/graph/libraries/redis.md"
expect_fail 'docs/graph/libraries/redis.md is named by the plan but does not exist' 'dangling library'

# 7. the plan invents a contract the spec does not declare
write_plan "sub:SPEC-0001/REJECT_BAD_SCHEMA=SPEC-0001/REJECT_EVERYTHING"
expect_fail 'SPEC-0001/REJECT_EVERYTHING is not a' 'invented contract'
# 7b. ...and then the real contract has no increment either
expect_fail 'contract REJECT_BAD_SCHEMA appears in no §9 increment' 'unimplemented contract'

# 8. §14 is a list
write_plan NEXT=$'- enter test-first\n- also refactor the store'
expect_fail '§14: .* one action, not a list' '§14 list'

# 9. a blank §1 line
write_plan "sub:- Existing tests inspected: tests/test_forms.py=- Existing tests inspected:"
expect_fail '§1: `- Existing tests inspected:` has no path' 'blank §1 line'

# 10. [verify] in §9 fails; in §6 only warns
write_plan "sub:- Behavior added: durable store=- Behavior added: durable store [verify]"
expect_fail 'increment 2: carries `\[verify\]`' '[verify] in §9'
write_plan "sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory [verify] | src/db.py | two-way |"
out="$(lint)" || { echo "[verify] in §6 must only warn" >&2; echo "$out" >&2; exit 1; }
grep -q 'WARN §6' <<<"$out"

# 11. a section left as the form's own prose is not populated
write_plan "sub:not applicable — the standard gates cover this plan.=Covered by the project's standard gates — see"
expect_fail '§10: not populated' 'template prose is not content'

# 12. --warn reports but exits 0
write_plan DEP1="increment 2"
lint --warn >/dev/null

# ---------------------------------------------------------------------------
# The ledger form. A plan-of-record grows for as long as the project does, and
# §9 grows fastest — every increment's contracts, RED tests, rollback path and
# dependencies land in it. Held in one file that is loaded whole, a mature plan
# becomes the largest thing a session reads, and the routing that exists to keep
# a context window honest is defeated by the document describing the work.
#
# So §9 may instead be an INDEX: one row per increment, pointing at a file that
# holds it. The plan stays the ledger; the increments are files under it. The
# single-file form still lints, because every plant already has one.
# ---------------------------------------------------------------------------
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

# 14. the ledger form lints clean, and --list still prints the increment graph
write_plan
write_ledger
out="$(lint --list)" || { echo "ledger-form plan failed:"; echo "$out"; exit 1; }
grep -q -- '2 Persist submissions  <- 1' <<<"$out" || {
  echo "--list did not resolve increments through the index" >&2; echo "$out" >&2; exit 1; }

# 15. an index row pointing at a file that does not exist
write_plan
write_ledger
rm "$G/plans/grill/increment-02-persist-submissions.md"
expect_fail 'increment 2' 'index row points at a missing file'

# 16. an increment file nobody indexes — work that exists and is unreachable
write_plan
write_ledger
cp "$G/plans/grill/increment-01-validate-schema.md" \
   "$G/plans/grill/increment-07-orphaned.md"
expect_fail 'plans/grill/increment-07-orphaned\.md is not indexed' 'orphan increment file'

# 17. the required fields are enforced INSIDE the increment's own file, not
# merely somewhere in the plan — otherwise the split loses the contract.
write_plan
write_ledger "### Increment 2 — Persist submissions
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM
- Tests to write (RED): tests/test_forms.py::test_persist
- Rollback path: revert the commit
"
expect_fail 'Depends on' 'required field missing from the increment file'

# 18. DOCUMENT order, not numeric. The forward-dependency check reads position
# as "is the dependency written before the thing that needs it". A plan that
# appends increment 3 after 1 and 2 — append-don't-renumber, which this seed
# prescribes — is valid, and sorting the list numerically made it fail a forward
# dependency it does not have, with no change to the plan file at all.
write_plan
python3 "$ROOT/tests/fixtures/grill/append_order.py" "$G/plans/grill.md"
lint >/dev/null || { echo "append-order plan must lint clean (document order)" >&2; lint; exit 1; }
echo "  an appended out-of-number increment lints clean — OK"

# 19. an index row may not point outside plans/grill/. `Path.__truediv__`
# discards the left side when the right is absolute, so an absolute path made
# the lint read and bless a file nowhere near the plan.
write_plan
write_ledger
sed -i.bak 's#`plans/grill/increment-02[^`]*`#`/tmp/plans/grill/x.md`#' "$G/plans/grill.md" && rm -f "$G/plans/grill.md.bak"
expect_fail 'points outside plans/grill/' 'index row escaping the plan'

# 20. the index row's number must match the file it points at, or renumbering
# one and not the other drifts silently — the drift an index exists to catch.
write_plan
write_ledger
sed -i.bak 's/^### Increment 2/### Increment 5/' "$G/plans/grill/increment-02-persist-submissions.md" && rm -f "$G/plans/grill/increment-02-persist-submissions.md.bak"
expect_fail 'index says increment 2' 'index number disagrees with the file'

# 21. an index row may be written any reasonable way — extra columns, a
# markdown link, no backticks. A row the parser cannot see is an increment
# nothing validates: the orphan failure arriving through the parser.
write_plan
write_ledger
python3 "$ROOT/tests/fixtures/grill/link_row.py" "$G/plans/grill.md"
lint >/dev/null || { echo "a 5-column markdown-link index row must resolve" >&2; lint; exit 1; }
echo "  an index row with extra columns and a markdown link still resolves — OK"

# 22. an orphan child under any name, at any depth.
write_plan
write_ledger
mkdir -p "$G/plans/grill/2026"
cp "$G/plans/grill/increment-01-validate-schema.md" "$G/plans/grill/2026/inc-99.md"
expect_fail 'inc-99.md is not indexed' 'orphan under a different name and depth'

# 23. a decision the plan cites by identifier that is not filed. §6 names a
# decision by number and nothing resolves it: the plan authorizes work by an
# identifier that reaches no record, and a reader cannot tell an unfiled
# decision from a rejected one. Both filename forms the seed ships resolve.
write_plan "sub:| Decision | Evidence | Reversibility |=| Decision | Evidence | Reversibility | ADR |" \
           "sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory | src/db.py | two-way | ADR-0002 |"
expect_fail 'ADR-0002 is named by the plan but is not filed' 'unfiled decision'
mkdir -p "$G/decisions"
printf -- '---\nstatus: proposed\nstatus_date: 2026-09-09\nowner: architect\n---\n\n# ADR-0002: session factory\n' \
  > "$G/decisions/adr-0002-session-factory.md"
lint >/dev/null || { echo "a filed decision must resolve" >&2; lint; exit 1; }
mv "$G/decisions/adr-0002-session-factory.md" "$G/decisions/0002-session-factory.md"
lint >/dev/null || { echo "the bare NNNN-<slug>.md filename form must resolve too" >&2; lint; exit 1; }
rm -rf "$G/decisions"
echo "  a filed decision resolves under either filename form — OK"

# 24. control: a fenced `### Increment` is an example of the shape, not an
# increment. Inside §9 it must not be parsed as a third increment; in a later
# section it must not trip the outside-§9 check in case 25.
FENCE=$'```markdown\n### Increment 3 — example of the shape\n- Spec contracts: SPEC-0001/EXAMPLE\n```\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
lint >/dev/null || { echo "a fenced increment heading inside §9 must stay green" >&2; lint; exit 1; }
write_plan "sub:- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).=- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).

## 16. Notes

${FENCE}"
lint >/dev/null || { echo "a fenced increment heading outside §9 must stay green" >&2; lint; exit 1; }
echo "  a fenced increment heading is not an increment — OK"

# 25. an increment heading outside §9 is invisible to every plan check: its
# dependencies, contracts and required fields go unread and the plan still
# passes. A plan for a second spec appended as a new top-level section is the
# common way to get there. The heading below is well formed, so its location
# is the only thing wrong with it.
write_plan "sub:- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).=- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).

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
expect_fail 'outside §9' 'increment heading outside §9'

# ---------------------------------------------------------------------------
# The code-fence rules. A fence is an example, not the plan, and the rules for
# where one opens and closes follow CommonMark. Each case below plants a fence
# whose misreading would expose (or hide) plan structure, so the lint's verdict
# changes if the rule is broken. Cases 27-32 run before 26 so that every rule
# is checked even while 26 is red.
# ---------------------------------------------------------------------------
expect_pass() {  # $1 = description
  local out
  out="$(lint 2>&1)" || { echo "expected PASS ($1)" >&2; echo "$out" >&2; exit 1; }
}
EXAMPLE_HEAD=$'### Increment 3 — example of the shape\n'
CHANGELOG='- 2026-09-09: grill pass; spawns orchestrator.1 (research-scout), orchestrator.2 (architect).'

# 27. a fence closes only on its own character: `~~~` inside a ``` fence, and
# a lone ``` inside a `~~~` fence, are content. And `~~~` opens a fence at all.
FENCE=$'```markdown\n~~~\n'"$EXAMPLE_HEAD"$'~~~\n```\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
expect_pass '~~~ inside a ``` fence does not close it'
FENCE=$'~~~markdown\n```\n'"$EXAMPLE_HEAD"$'~~~\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
expect_pass '``` inside a ~~~ fence does not close it'
echo "  a fence closes only on its own character — OK"

# 28. a closing run shorter than the opener does not close the fence.
FENCE=$'````markdown\n```\n'"$EXAMPLE_HEAD"$'```\n````\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
expect_pass 'a ``` run does not close a ```` fence'
echo "  a shorter closing run does not close — OK"

# 29. a line with an info string after the run opens nothing and closes nothing
# inside a fence: only a bare run closes.
FENCE=$'```\n```python\n'"$EXAMPLE_HEAD"$'```\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
expect_pass 'a run with an info string does not close'
echo "  a closing line with an info string does not close — OK"

# 30. an unclosed fence runs to the end of the file, as CommonMark reads it:
# the heading under it is an example, not an increment outside §9.
write_plan "sub:${CHANGELOG}=${CHANGELOG}

\`\`\`markdown
### Increment 9 — example, never closed
- Spec contracts: SPEC-0001/EXAMPLE
"
expect_pass 'an unclosed fence runs to EOF'
echo "  an unclosed fence runs to the end — OK"

# 31. CRLF line endings: the same plan, fence and all, lints the same.
FENCE=$'```markdown\n'"$EXAMPLE_HEAD"$'```\n\n'
write_plan "sub:## 10. Verification Plan=${FENCE}## 10. Verification Plan"
python3 -c 'import sys,pathlib; p=pathlib.Path(sys.argv[1]); p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))' "$G/plans/grill.md"
expect_pass 'a CRLF plan with a fenced example'
echo "  a CRLF plan lints like an LF plan — OK"

# 32. a `## 9.` header inside a fence opens no section: §9 stays the real one.
write_plan "sub:${CHANGELOG}=${CHANGELOG}

\`\`\`markdown
## 9. Implementation Plan
an example of the header, not the plan
\`\`\`
"
expect_pass 'a fenced ## 9. header is not a section'
echo "  a fenced section header is not a section — OK"

# 26. a field whose value is a fenced block is not blank. A RED command written
# as a fence under its label is the natural way to give the exact invocation,
# and reading the masked text made the value vanish: a false "is blank".
# Case 24 guards the other side: a fenced `- Label:` line is still no field.
write_plan "sub:- Tests to write (RED): test_reject_bad_schema=- Tests to write (RED):
  \`\`\`bash
  pytest tests/test_forms.py::test_reject_bad_schema
  \`\`\`"
out="$(lint 2>&1)" && rc=0 || rc=$?
if [[ $rc -ne 0 ]] || grep -q 'is blank' <<<"$out"; then
  echo "a fenced field value must not read as blank (exit $rc)" >&2; echo "$out" >&2; exit 1
fi
echo "  a fenced field value is a value — OK"

# 13. no plan at all -> SKIP, exit 0
rm -rf "$G/plans/grill" "$G/plans/grill.md"
lint >/dev/null

# ---------------------------------------------------------------------------
# The wave report, `grill-lint.py --waves` (SPEC-0005 §6 "Wave report"). One
# collecting block after every case above, case 13 included: each case checks
# its own conditions without relying on `set -e`, prints `FAIL <label>: <why>`
# when it fails, and the block exits 1 after its last case if any failed, so
# every label shows its own result in one run and none hides another. The
# report is read-only and never changes an exit status.
# ---------------------------------------------------------------------------
set +e
WAVES_FAILED=0
SCHED="$ROOT/tests/fixtures/grill/scheduled_plan.py"
GOLDEN="$ROOT/tests/fixtures/grill/fixture-plan.plain.golden"
HEADER_3='waves: 3 wave(s), 5 increment(s) — a static schedule from §9; what is committed is not read'
WAVES_5='  wave 1: increment 1 (RED) Reject bad schemas
  wave 1: increment 3 (prose) Document the form
  wave 2: increment 2 (GREEN) Validate schema <- 1
  wave 2: increment 4 (RED) Persist submissions <- 3
  wave 3: increment 5 (GREEN) Store submissions <- 2, 4'
OVERLAP_1_3='^ *WARN §9 increments 1 and 3 may run together and both name tests/test_forms\.py( — .*)?$'

wfail() { printf 'FAIL %s: %s\n' "$1" "$2"; WAVES_FAILED=1; }
# run the tool unrecorded: WOUT holds stdout and stderr, WRC the exit status
wrun() { WOUT="$(python3 "$G/grill-lint.py" "$@" 2>&1)"; WRC=$?; }
# the scheduled fixture plan, with KEY=VALUE edits (see scheduled_plan.py)
sched() { write_plan && python3 "$SCHED" "$G/plans/grill.md" "$@"; }
has_line() { grep -qxF -- "$2" <<<"$1"; }
has_re() { grep -qE -- "$2" <<<"$1"; }
wave_lines() { grep -E '^  wave ' <<<"$1"; }
no_traceback() { ! grep -q '^Traceback' <<<"$1"; }
# every line of $1 appears in $2, in the same relative order
in_order() {
  python3 -c 'import sys
want = sys.argv[1].splitlines(); have = iter(sys.argv[2].splitlines())
sys.exit(0 if all(any(w == h for h in have) for w in want) else 1)' "$1" "$2"
}
# report lines that must never appear without --waves
report_line() {
  grep -E '^waves:|^  wave |may run together and both name|: no Phase: field|is not RED, GREEN or prose' <<<"$1"
}
# lay a recorded plan state back under $G, and load its flags into ARGS
replay() {
  rm -rf "$G/plans" "$G/decisions"
  if [ -d "$1/state/plans" ]; then cp -R "$1/state/plans" "$G/plans"; else mkdir -p "$G/plans"; fi
  if [ -d "$1/state/decisions" ]; then cp -R "$1/state/decisions" "$G/decisions"; fi
  ARGS=()
  local a
  while IFS= read -r -d '' a; do ARGS+=("$a"); done < "$1/args"
}

case_waves_levels_scheduled_plan() {
  # X361 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON
  # Asserts SPEC-0005 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON; holds STALE_SCHEDULE
  # (the header says the schedule is static and what is committed is not read).
  # Increment 2 also depends on a library page and still sits in wave 2.
  local L=X361
  sched || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_line "$WOUT" "$HEADER_3" || { wfail $L "no header line '$HEADER_3'"; return; }
  [ "$(wave_lines "$WOUT")" = "$WAVES_5" ] || { wfail $L "the wave lines are not exactly the five of §6, in wave-then-document order"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_levels_red_without_dependency_rises() {
  # X362 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON
  # Asserts SPEC-0005 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON: a RED with no
  # dependency rises to wave 1, although §9 lists it after a GREEN.
  local L=X362
  sched D4=none || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_line "$WOUT" '  wave 1: increment 4 (RED) Persist submissions' \
    || wfail $L "no line '  wave 1: increment 4 (RED) Persist submissions'"
}
case_waves_levels_ledger_form() {
  # X363 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON
  # Asserts SPEC-0005 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON: the ledger form of the
  # scheduled plan prints the same wave lines.
  local L=X363
  { sched && write_ledger; } || { wfail $L "harness: the ledger form was not written"; return; }
  wrun --waves
  [ "$(wave_lines "$WOUT")" = "$WAVES_5" ] || wfail $L "the ledger form does not print the five wave lines of the inline form"
}
case_waves_levels_library_only_dependency() {
  # X364 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON
  # Asserts SPEC-0005 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON: a library page is not
  # an increment, so it does not move a wave.
  local L=X364
  sched D3=docs/graph/libraries/sqlalchemy.md || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_line "$WOUT" '  wave 1: increment 3 (prose) Document the form' \
    || { wfail $L "no line '  wave 1: increment 3 (prose) Document the form'"; return; }
  has_line "$WOUT" '  wave 2: increment 4 (RED) Persist submissions <- 3' \
    || wfail $L "no line '  wave 2: increment 4 (RED) Persist submissions <- 3'"
}
case_waves_levels_seed_plan_7_30_0() {
  # X365 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON
  # Asserts SPEC-0005 GRILL_WAVES_LEVELS_FROM_DEPENDS_ON on the seed's own frozen
  # docs/plans/grill-7.30.0-cycle-economy.md (read only; its specs do not resolve
  # here, which is not a dependency defect, so the report still prints).
  local L=X365
  write_plan || { wfail $L "harness: the fixture plan was not written"; return; }
  wrun --plan "$ROOT/docs/plans/grill-7.30.0-cycle-economy.md" --waves --warn
  has_re "$WOUT" '^  wave 1: increment 23 \(RED\)' || { wfail $L "no line beginning '  wave 1: increment 23 (RED)'"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0 under --warn, got $WRC"
}
case_waves_overlap_brace_pair() {
  # X366 GRILL_WAVES_OVERLAP_IS_A_WARNING
  # Asserts SPEC-0005 GRILL_WAVES_OVERLAP_IS_A_WARNING: one brace group expands;
  # 1 and 3 may run together, 3 and 4 may not (4 depends on 3).
  local L=X366
  sched 'F3=`tests/test_{forms,store}.py`' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_re "$WOUT" "$OVERLAP_1_3" || { wfail $L "no overlap warning for increments 1 and 3 naming tests/test_forms.py"; return; }
  [ "$(grep -c 'may run together' <<<"$WOUT")" -eq 1 ] || { wfail $L "expected exactly one overlap warning"; return; }
  ! has_re "$WOUT" 'increments 3 and 4 may run together' || { wfail $L "warned for increments 3 and 4, which are sequenced"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_overlap_glob_token() {
  # X367 GRILL_WAVES_OVERLAP_IS_A_WARNING
  # Asserts SPEC-0005 GRILL_WAVES_OVERLAP_IS_A_WARNING: a glob overlaps the path
  # it matches, and the warning names the path, not the glob (R0.6).
  local L=X367
  sched 'F3=`tests/*.py`' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_re "$WOUT" "$OVERLAP_1_3" || { wfail $L "no line 'WARN §9 increments 1 and 3 may run together and both name tests/test_forms.py'"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_overlap_bare_name() {
  # X368 GRILL_WAVES_OVERLAP_IS_A_WARNING
  # Asserts SPEC-0005 GRILL_WAVES_OVERLAP_IS_A_WARNING; holds FALSE_OVERLAP: a
  # bare name overlaps the path it ends, whatever directory it sits in, the
  # warning names the slashed path (R0.6), and the exit status does not change.
  local L=X368 prc
  sched 'F3=`test_forms.py`' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun; prc=$WRC
  wrun --waves
  has_re "$WOUT" "$OVERLAP_1_3" || { wfail $L "no line 'WARN §9 increments 1 and 3 may run together and both name tests/test_forms.py'"; return; }
  [ "$WRC" -eq "$prc" ] || { wfail $L "exit $WRC with --waves, $prc without"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_overlap_words_and_keys_silent() {
  # X369 GRILL_WAVES_OVERLAP_IS_A_WARNING
  # Asserts SPEC-0005 GRILL_WAVES_OVERLAP_IS_A_WARNING; holds MISSED_OVERLAP (a
  # file named only in prose gives no warning): prose words, `§6`, `resolve()`
  # and a dotted fact key two independent increments both name are not paths.
  local L=X369
  sched 'F1=`tests/test_forms.py` (the forms.submit key; see §6 and resolve())' \
        'F3=`docs/forms.md` (the forms.submit key; see §6 and resolve())' \
    || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_line "$WOUT" "$HEADER_3" || { wfail $L "no header line '$HEADER_3'"; return; }
  ! has_re "$WOUT" 'may run together' || wfail $L "a prose word or a dotted key produced an overlap warning"
}
case_waves_overlap_plain_lint_silent() {
  # X370 GRILL_WAVES_OVERLAP_IS_A_WARNING (guard)
  # Asserts SPEC-0005 GRILL_WAVES_OVERLAP_IS_A_WARNING: without --waves the same
  # brace-pair plan prints no overlap line and exits 0.
  local L=X370
  sched 'F3=`tests/test_{forms,store}.py`' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun
  ! has_re "$WOUT" 'may run together' || { wfail $L "the plain lint printed an overlap line"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_unscheduled_without_phase() {
  # X371 GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE
  # Asserts SPEC-0005 GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE: an older plant's
  # plan, with no Phase: field anywhere, is unscheduled and nothing more.
  local L=X371
  write_plan || { wfail $L "harness: the fixture plan was not written"; return; }
  wrun --waves
  has_line "$WOUT" 'waves: unscheduled — no §9 increment carries a Phase: field' \
    || { wfail $L "no line 'waves: unscheduled — no §9 increment carries a Phase: field'"; return; }
  [ -z "$(wave_lines "$WOUT")" ] || { wfail $L "printed a wave line"; return; }
  ! has_re "$WOUT" 'WARN' || { wfail $L "printed a warning"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_partial_phase_warns() {
  # X372 GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE
  # Asserts SPEC-0005 GRILL_WAVES_UNSCHEDULED_WITHOUT_PHASE: when only increment 1
  # carries a phase, increment 2 prints `(no phase)` and one warning names it.
  local L=X372
  write_plan $'sub:- Depends on: none=- Phase: RED\n- Depends on: none' \
    || { wfail $L "harness: the fixture plan was not written"; return; }
  wrun --waves
  has_re "$WOUT" '^  wave 1: increment 1 \(RED\)' || { wfail $L "no wave line for increment 1 (RED)"; return; }
  has_re "$WOUT" '^  wave 2: increment 2 \(no phase\)' || { wfail $L "no line beginning '  wave 2: increment 2 (no phase)'"; return; }
  [ "$(grep -c 'WARN §9 increment 2: no Phase: field' <<<"$WOUT")" -eq 1 ] \
    || { wfail $L "expected exactly one 'WARN §9 increment 2: no Phase: field'"; return; }
  ! has_re "$WOUT" 'increment 1: no Phase: field' || { wfail $L "warned for increment 1, which carries a phase"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}
case_waves_not_computed_forward_dependency() {
  # X373 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT
  # Asserts SPEC-0005 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT: a forward
  # dependency stops the report; the plain lint's defect line still prints.
  local L=X373
  sched 'D1=increment 2' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_re "$WOUT" '^waves: not computed — §9 has dependency defects' \
    || { wfail $L "no line beginning 'waves: not computed — §9 has dependency defects'"; return; }
  [ -z "$(wave_lines "$WOUT")" ] || { wfail $L "printed a wave line"; return; }
  has_re "$WOUT" 'increment 1: depends on increment 2, listed after it' || { wfail $L "the plain lint's forward-dependency line is missing"; return; }
  [ "$WRC" -eq 1 ] || wfail $L "expected exit 1, got $WRC"
}
case_waves_not_computed_missing_dependency() {
  # X374 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT
  # Asserts SPEC-0005 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT: the same for
  # a dependency on an increment that does not exist.
  local L=X374
  sched 'D1=increment 9' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  has_re "$WOUT" '^waves: not computed — §9 has dependency defects' \
    || { wfail $L "no line beginning 'waves: not computed — §9 has dependency defects'"; return; }
  [ -z "$(wave_lines "$WOUT")" ] || { wfail $L "printed a wave line"; return; }
  has_re "$WOUT" 'increment 9, which does not exist' || { wfail $L "the plain lint's missing-dependency line is missing"; return; }
  [ "$WRC" -eq 1 ] || wfail $L "expected exit 1, got $WRC"
}
case_waves_not_computed_under_warn() {
  # X375 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT
  # Asserts SPEC-0005 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT: under --warn
  # the not-computed report exits 0.
  local L=X375
  sched 'D1=increment 2' || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves --warn
  has_re "$WOUT" '^waves: not computed — §9 has dependency defects' \
    || { wfail $L "no line beginning 'waves: not computed — §9 has dependency defects'"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0 under --warn, got $WRC"
}
case_waves_other_defect_still_reports() {
  # X376 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT
  # Asserts SPEC-0005 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT: a defect that
  # is not a dependency defect (case 7's invented contract) leaves the wave
  # lines printed, and the exit is the plain lint's 1.
  local L=X376
  sched C1=SPEC-0001/REJECT_EVERYTHING C2=SPEC-0001/REJECT_EVERYTHING \
    || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun --waves
  [ "$(wave_lines "$WOUT")" = "$WAVES_5" ] || { wfail $L "the five wave lines did not print beside a non-dependency defect"; return; }
  ! has_re "$WOUT" '^waves: not computed' || { wfail $L "a non-dependency defect stopped the report"; return; }
  [ "$WRC" -eq 1 ] || wfail $L "expected the plain lint's exit 1, got $WRC"
}
case_waves_not_computed_duplicate_numbers() {
  # X380 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT
  # Asserts SPEC-0005 GRILL_WAVES_NOT_COMPUTED_ON_DEPENDENCY_DEFECT (R0.13): two
  # inline increments carrying one number get no wave map, and the exit stays
  # the plain lint's. Increment 4 depends on nothing, so no dependency defect
  # hides the duplicate.
  local L=X380 prc
  sched N3=1 D4=none || { wfail $L "harness: the scheduled fixture plan was not written"; return; }
  wrun; prc=$WRC
  wrun --waves
  has_line "$WOUT" 'waves: not computed — §9 has duplicate increment numbers' \
    || { wfail $L "no line 'waves: not computed — §9 has duplicate increment numbers'"; return; }
  [ -z "$(wave_lines "$WOUT")" ] || { wfail $L "printed a wave line"; return; }
  [ "$WRC" -eq "$prc" ] || wfail $L "exit $WRC with --waves, $prc without"
}
case_waves_existing_plans_same_exit() {
  # X377 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED (guard)
  # Asserts SPEC-0005 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED: every plan and flag set
  # cases 1 to 32 linted, linted again with and without --waves: the same exit
  # status, every plain line in the --waves output in the same order, and no
  # line beginning `Traceback` (R0.7).
  local L=X377 d n=0 pout prc
  for d in "$REC"/*; do
    [ -d "$d" ] || continue
    n=$((n + 1))
    replay "$d"
    wrun ${ARGS[@]+"${ARGS[@]}"}; pout="$WOUT"; prc=$WRC
    wrun ${ARGS[@]+"${ARGS[@]}"} --waves
    no_traceback "$WOUT" || { wfail $L "a traceback with --waves on record $(basename "$d")"; return; }
    [ "$WRC" -eq "$prc" ] || { wfail $L "record $(basename "$d"): exit $WRC with --waves, $prc without"; return; }
    in_order "$pout" "$WOUT" || { wfail $L "record $(basename "$d"): the plain lines are not all in the --waves output, in order"; return; }
  done
  [ "$n" -gt 0 ] || wfail $L "harness: no lint call of cases 1 to 32 was recorded"
}
case_waves_plain_output_has_no_report_lines() {
  # X378 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED (guard)
  # Asserts SPEC-0005 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED: without --waves no
  # recorded plan prints a `waves:` line, a `  wave ` line, an overlap warning
  # or a phase warning.
  local L=X378 d n=0
  for d in "$REC"/*; do
    [ -d "$d" ] || continue
    n=$((n + 1))
    replay "$d"
    wrun ${ARGS[@]+"${ARGS[@]}"}
    [ -z "$(report_line "$WOUT")" ] || { wfail $L "record $(basename "$d"): the plain lint printed a report line"; return; }
  done
  [ "$n" -gt 0 ] || wfail $L "harness: no lint call of cases 1 to 32 was recorded"
}
case_waves_plain_output_golden() {
  # X379 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED (guard)
  # Asserts SPEC-0005 GRILL_WAVES_LEAVES_THE_GATE_UNCHANGED: the plain output on
  # the fixture plan equals the golden copy captured from the unmodified tool.
  local L=X379
  [ -f "$GOLDEN" ] || { wfail $L "harness: no golden copy at tests/fixtures/grill/fixture-plan.plain.golden"; return; }
  write_plan || { wfail $L "harness: the fixture plan was not written"; return; }
  wrun
  [ "$WOUT" = "$(cat "$GOLDEN")" ] || { wfail $L "the plain output differs from the golden copy"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC"
}

for c in case_waves_levels_scheduled_plan case_waves_levels_red_without_dependency_rises \
         case_waves_levels_ledger_form case_waves_levels_library_only_dependency \
         case_waves_levels_seed_plan_7_30_0 case_waves_overlap_brace_pair \
         case_waves_overlap_glob_token case_waves_overlap_bare_name \
         case_waves_overlap_words_and_keys_silent case_waves_overlap_plain_lint_silent \
         case_waves_unscheduled_without_phase case_waves_partial_phase_warns \
         case_waves_not_computed_forward_dependency case_waves_not_computed_missing_dependency \
         case_waves_not_computed_under_warn case_waves_other_defect_still_reports \
         case_waves_not_computed_duplicate_numbers case_waves_existing_plans_same_exit \
         case_waves_plain_output_has_no_report_lines case_waves_plain_output_golden; do
  "$c"
done

# ---------------------------------------------------------------------------
# The seed layout (plan increment 2, ADR-0020). A seed round plan lives at
# docs/plans/<stem>.md, its ledger in docs/plans/<stem>/ beside it, and its
# specs and decisions in docs/specs/ and docs/decisions/, named by --specs and
# --decisions. The fixture tree is tests/fixtures/grill/seed-ledger/; each case
# lints a fresh copy of it. No spec owns this (plan increment 2).
# ---------------------------------------------------------------------------
SEEDFX_SRC="$ROOT/tests/fixtures/grill/seed-ledger"
SEEDFX="$TMP/seed-ledger"
seedfx() {  # a fresh copy of the seed-shaped fixture at $SEEDFX
  rm -rf "$SEEDFX"
  [ -f "$SEEDFX_SRC/docs/plans/round.md" ] || return 1
  cp -R "$SEEDFX_SRC" "$SEEDFX"
}
# lint the fixture plan with its spec and decision homes, from the fixture root
seedlint() {
  WOUT="$(cd "$SEEDFX" && python3 "$G/grill-lint.py" --plan "$SEEDFX/docs/plans/round.md" \
    --specs "$SEEDFX/docs/specs" --decisions "$SEEDFX/docs/decisions" "$@" 2>&1)"
  WRC=$?
}
first_line() { printf '%s' "$1" | head -1; }

case_seed_ledger_lints_in_place() {
  # G3a (increment 2a): a plan at docs/plans/round.md, its ledger rows reading
  # docs/plans/round/increment-NN-x.md, lints PASS with --specs and --decisions.
  local L=G3a
  seedfx || { wfail $L "harness: tests/fixtures/grill/seed-ledger is missing"; return; }
  seedlint --list
  [ "$WRC" -eq 0 ] || { wfail $L "expected exit 0, got $WRC: $(first_line "$WOUT")"; return; }
  has_re "$WOUT" '^ *2 Persist the round +<- 1' || wfail $L "--list did not resolve increment 2 through the index"
}
case_seed_ledger_orphan_leaf() {
  # G3b (increment 2b): a file in docs/plans/round/ that no row indexes is an
  # orphan finding naming it.
  local L=G3b
  seedfx || { wfail $L "harness: tests/fixtures/grill/seed-ledger is missing"; return; }
  cp "$SEEDFX/docs/plans/round/increment-01-a.md" "$SEEDFX/docs/plans/round/increment-09-stray.md"
  seedlint
  [ "$WRC" -eq 1 ] || { wfail $L "expected exit 1, got $WRC"; return; }
  has_re "$WOUT" 'increment-09-stray\.md is not indexed' || wfail $L "no finding 'increment-09-stray.md is not indexed'"
}
case_seed_ledger_row_outside_refused() {
  # G3c (increment 2c): a row pointing outside docs/plans/round/ is refused. The
  # path still ends round/<file>.md, so only its location is wrong (as case 19).
  local L=G3c
  seedfx || { wfail $L "harness: tests/fixtures/grill/seed-ledger is missing"; return; }
  sed -i.bak 's#`docs/plans/round/increment-02-b.md`#`/tmp/docs/plans/round/increment-02-b.md`#' \
    "$SEEDFX/docs/plans/round.md" && rm -f "$SEEDFX/docs/plans/round.md.bak"
  grep -q '/tmp/docs/plans/round/increment-02-b.md' "$SEEDFX/docs/plans/round.md" \
    || { wfail $L "harness: the row was not rewritten"; return; }
  seedlint
  [ "$WRC" -eq 1 ] || { wfail $L "expected exit 1, got $WRC"; return; }
  has_re "$WOUT" 'increment 2 points outside' || wfail $L "no finding 'increment 2 points outside'"
}
case_seed_ledger_contract_from_specs_flag() {
  # G3d (increment 2d): a contract declared only in the --specs directory
  # resolves; one declared nowhere is the "invents a contract" finding. A decoy
  # SPEC-0042 beside the linter declares neither, so reading the specs beside
  # the tool instead of --specs cannot pass.
  local L=G3d
  seedfx || { wfail $L "harness: tests/fixtures/grill/seed-ledger is missing"; return; }
  printf -- '- **Status:** active\n\n### Contract: DECOY_ONLY\n' > "$G/specs/SPEC-0042-decoy.md"
  seedlint
  if [ "$WRC" -ne 0 ] || has_re "$WOUT" 'SPEC-0042'; then
    wfail $L "a contract declared only in --specs did not resolve (exit $WRC): $(grep -m1 -E 'SPEC-0042|§9|FAIL' <<<"$WOUT")"
    rm -f "$G/specs/SPEC-0042-decoy.md"; return
  fi
  sed -i.bak 's#SPEC-0042/ROUND_ALPHA#SPEC-0042/ROUND_NOWHERE#' "$SEEDFX/docs/plans/round/increment-01-a.md" \
    && rm -f "$SEEDFX/docs/plans/round/increment-01-a.md.bak"
  seedlint
  rm -f "$G/specs/SPEC-0042-decoy.md"
  [ "$WRC" -eq 1 ] || { wfail $L "a contract declared nowhere: expected exit 1, got $WRC"; return; }
  has_re "$WOUT" 'SPEC-0042/ROUND_NOWHERE is not a .*invents a contract' \
    || wfail $L "no 'invents a contract' finding for SPEC-0042/ROUND_NOWHERE"
}
case_seed_ledger_decision_from_decisions_flag() {
  # G3e (increment 2e): an ADR filed only in the --decisions directory resolves.
  local L=G3e
  seedfx || { wfail $L "harness: tests/fixtures/grill/seed-ledger is missing"; return; }
  rm -rf "$G/decisions"
  seedlint
  ! has_re "$WOUT" 'ADR-0007 is named by the plan but is not filed' \
    || { wfail $L "ADR-0007, filed only in --decisions, did not resolve"; return; }
  [ "$WRC" -eq 0 ] || wfail $L "expected exit 0, got $WRC: $(first_line "$WOUT")"
}
case_plant_layout_unchanged() {
  # G3f (increment 2f, guard): the plant layout (plans/grill.md, plans/grill/)
  # lints exactly as before: the ledger form passes with the golden headline.
  # That an unindexed child is still an orphan is case 16 above.
  local L=G3f
  { write_plan && write_ledger; } || { wfail $L "harness: the ledger form was not written"; return; }
  wrun
  [ "$WRC" -eq 0 ] || { wfail $L "the plant ledger form: expected exit 0, got $WRC"; return; }
  [ "$WOUT" = "$(cat "$GOLDEN")" ] || wfail $L "the plant ledger form's output differs from the golden copy"
}

# ---------------------------------------------------------------------------
# Qualified decision references (plan increment 3, ADR-0015). `<name>:ADR-NNNN`
# cites another repository's decision: reported once as external and not
# checked, never resolved against the plan's own decisions. No spec owns this.
# ---------------------------------------------------------------------------
ADR_COL_H='sub:| Decision | Evidence | Reversibility |=| Decision | Evidence | Reversibility | ADR |'
adr_row() { printf 'sub:| Use the existing session factory | src/db.py | two-way |=| Use the existing session factory | src/db.py | two-way | %s |' "$1"; }

case_external_decision_reported() {
  # G1a (increment 3a): seed:ADR-0009 with no local ADR-0009 lints PASS and
  # prints one line naming it as external and not checked.
  local L=G1a
  rm -rf "$G/decisions"
  write_plan "$ADR_COL_H" "$(adr_row 'seed:ADR-0009')" || { wfail $L "harness: the plan was not written"; return; }
  wrun
  [ "$WRC" -eq 0 ] || { wfail $L "expected exit 0, got $WRC: $(grep -m1 'ADR-0009' <<<"$WOUT")"; return; }
  [ "$(grep -c 'seed:ADR-0009' <<<"$WOUT")" -eq 1 ] || { wfail $L "expected one line naming seed:ADR-0009"; return; }
  grep 'seed:ADR-0009' <<<"$WOUT" | grep -q 'external' && grep 'seed:ADR-0009' <<<"$WOUT" | grep -q 'not checked' \
    || wfail $L "the seed:ADR-0009 line does not say external and not checked"
}
case_external_decision_once() {
  # G1b (increment 3b): the same qualified reference twice prints one line.
  local L=G1b
  rm -rf "$G/decisions"
  write_plan "$ADR_COL_H" "$(adr_row 'seed:ADR-0009')" \
    "sub:Persist valid submissions; reject bad schemas with 422.=Persist valid submissions; reject bad schemas with 422 (seed:ADR-0009)." \
    || { wfail $L "harness: the plan was not written"; return; }
  [ "$(grep -o 'seed:ADR-0009' "$G/plans/grill.md" | wc -l | tr -d ' ')" -eq 2 ] \
    || { wfail $L "harness: the plan does not cite seed:ADR-0009 twice"; return; }
  wrun
  [ "$WRC" -eq 0 ] || { wfail $L "expected exit 0, got $WRC: $(grep -m1 'ADR-0009' <<<"$WOUT")"; return; }
  [ "$(grep -c 'seed:ADR-0009' <<<"$WOUT")" -eq 1 ] || wfail $L "expected exactly one line naming seed:ADR-0009"
}
# G1c and G1d (a bare ADR with no local file is still "not filed"; a bare ADR
# with a local file resolves) were guards for increment 3. Case 23 above
# asserts both on the same decision-table shape, so it is their survivor.

# ---------------------------------------------------------------------------
# The ledger verification tool (plan increment 4): tools/verify-ledger.py
# rebuilds a monolith from a ledger plan and its leaves and compares bytes. The
# fixture: tests/fixtures/grill/seed-ledger.monolith.md is
# seed-ledger/docs/plans/round.md with its §9 index table replaced by the
# leaves, in row order, one blank line between them. No spec owns this.
# ---------------------------------------------------------------------------
VL="$ROOT/tools/verify-ledger.py"
VLFX="$TMP/verify-ledger"
vlfx() {
  rm -rf "$VLFX"
  [ -f "$ROOT/tests/fixtures/grill/seed-ledger.monolith.md" ] && [ -d "$SEEDFX_SRC/docs/plans/round" ] || return 1
  mkdir -p "$VLFX"
  cp "$ROOT/tests/fixtures/grill/seed-ledger.monolith.md" "$VLFX/monolith.md"
  cp "$SEEDFX_SRC/docs/plans/round.md" "$VLFX/round.md"
  cp -R "$SEEDFX_SRC/docs/plans/round" "$VLFX/round"
}
vlrun() {
  WOUT="$(python3 "$VL" --monolith "$VLFX/monolith.md" --ledger "$VLFX/round.md" --leaves "$VLFX/round" 2>&1)"
  WRC=$?
}
has_word() { grep -qE "(^|[^0-9])$2([^0-9]|$)" <<<"$1"; }

case_verify_ledger_changed_byte() {
  # D5b (increment 4b): one changed byte in a leaf exits 1 and names the leaf
  # and the first differing byte offset (0-based; the offset in the rebuilt
  # file or in the leaf both name the byte).
  local L=D5b offs om ol
  vlfx || { wfail $L "harness: the verify-ledger fixture is missing"; return; }
  offs="$(python3 - "$VLFX/monolith.md" "$VLFX/round/increment-02-b.md" <<'PY'
import sys
m = open(sys.argv[1], "rb").read(); leaf_path = sys.argv[2]
leaf = open(leaf_path, "rb").read()
old = "rows kept as written".encode(); new = "rows kept as writteN".encode()
at_leaf = leaf.index(old) + len(old) - 1
open(leaf_path, "wb").write(leaf.replace(old, new, 1))
at_mono = m.index(old) + len(old) - 1
print(at_mono, at_leaf)
PY
)" || { wfail $L "harness: the leaf was not changed"; return; }
  om="${offs% *}"; ol="${offs#* }"
  vlrun
  [ "$WRC" -eq 1 ] || { wfail $L "expected exit 1, got $WRC: $(first_line "$WOUT")"; return; }
  grep -q 'increment-02-b.md' <<<"$WOUT" || { wfail $L "the changed leaf increment-02-b.md is not named"; return; }
  has_word "$WOUT" "$om" || has_word "$WOUT" "$ol" || wfail $L "the first differing byte offset ($om in the rebuild, $ol in the leaf) is not named"
}
case_verify_ledger_unindexed_leaf() {
  # D5c (increment 4c): a leaf no index row points at exits 1 and names it.
  local L=D5c
  vlfx || { wfail $L "harness: the verify-ledger fixture is missing"; return; }
  cp "$VLFX/round/increment-01-a.md" "$VLFX/round/increment-03-stray.md"
  vlrun
  [ "$WRC" -eq 1 ] || { wfail $L "expected exit 1, got $WRC: $(first_line "$WOUT")"; return; }
  grep -q 'increment-03-stray.md' <<<"$WOUT" || wfail $L "the unindexed leaf increment-03-stray.md is not named"
}
case_verify_ledger_counts_utf8_bytes() {
  # D5d (increment 4d): a multibyte character counts as its UTF-8 bytes. The
  # fixture holds several, so its byte and character counts differ. It is also
  # the survivor of D5a (increment 4a): the unchanged ledger and leaves rebuild
  # the monolith exactly, exit 0, and the rebuilt file's byte count is printed.
  local L=D5d nb nc
  vlfx || { wfail $L "harness: the verify-ledger fixture is missing"; return; }
  nb="$(wc -c < "$VLFX/monolith.md" | tr -d ' ')"
  nc="$(python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' "$VLFX/monolith.md")"
  [ "$nb" -ne "$nc" ] || { wfail $L "harness: the fixture has no multibyte character"; return; }
  vlrun
  [ "$WRC" -eq 0 ] || { wfail $L "expected exit 0, got $WRC: $(first_line "$WOUT")"; return; }
  has_word "$WOUT" "$nb" || { wfail $L "the UTF-8 byte count $nb is not printed"; return; }
  ! has_word "$WOUT" "$nc" || wfail $L "the character count $nc is printed as if it were bytes"
}

for c in case_seed_ledger_lints_in_place case_seed_ledger_orphan_leaf \
         case_seed_ledger_row_outside_refused case_seed_ledger_contract_from_specs_flag \
         case_seed_ledger_decision_from_decisions_flag case_plant_layout_unchanged \
         case_external_decision_reported case_external_decision_once \
         case_verify_ledger_changed_byte \
         case_verify_ledger_unindexed_leaf case_verify_ledger_counts_utf8_bytes; do
  "$c"
done
if [ "$WAVES_FAILED" -ne 0 ]; then
  printf 'grill lint contract: FAIL — the collecting block has failing cases (above)\n'
  exit 1
fi

printf 'grill lint contract: PASS\n'
