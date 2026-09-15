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

lint() { python3 "$G/grill-lint.py" "$@"; }
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
expect_fail 'increment-07-orphaned.md' 'orphan increment file'

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

# 13. no plan at all -> SKIP, exit 0
rm -rf "$G/plans/grill" "$G/plans/grill.md"
lint >/dev/null

printf 'grill lint contract: PASS\n'
