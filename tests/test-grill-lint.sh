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

# 13. no plan at all -> SKIP, exit 0
rm "$G/plans/grill.md"
lint >/dev/null

printf 'grill lint contract: PASS\n'
