<!--
Template: grill.template.md
Authored by: orchestrator, grill-planner
Lives at: docs/graph/plans/grill.md
Used: once per project; updated continuously
Filled by copying this template into the target path and replacing
every <placeholder>. Keep the section numbers: agents and tooling
index into them.
-->

# grill.md — Plan of Record

## 0. Metadata
- Project:
- Feature or goal:
- Date:
- Owner:
- Current phase:
- Related files:
- Related documentation:
- Related ADRs:
- Related specs:
- Related libraries:

## 1. Artifact Discovery
Every line cites the paths read, or reads `none — <reason>`; a blank
line is unread, not empty.
- Existing files inspected:
- Existing docs inspected:
- Existing tests inspected:
- Existing specs inspected:
- Existing architecture signals:
- Libraries already wikified:
- External sources downloaded:
- Constraints discovered:

## 2. Shared Understanding
Write the current best understanding of the goal in precise language.
Include what success means, what the system will deliver, and what
belongs outside the current scope.

## 3. User Goal
- Primary user:
- Primary outcome:
- Job to be done:
- Acceptance criteria (link to spec §9):
- Non-goals:

## 4. Operating Constraints
- Runtime constraints:
- Security constraints:
- Privacy constraints:
- Data constraints:
- Cost constraints: <running cost>
  - Plan approval (`grill.plan-approval`), <date, or "skipped: the plan
    did not go to the owner">. Levers this plan uses (any cost lever the
    plant's doctrine defines, or "none defined"): <lever: the owner's
    answer, or "default: <value>">
  - Owner-only prerequisites: <step, the increment that needs it, status>
  - Scoped standing grant: <the named non-production acts and targets
    the owner granted for this unit of work, or "none asked">
- Latency constraints:
- Compliance constraints:
- Maintenance constraints:

## 5. Research Summary
Covers every docs/graph/libraries/ page a §9 `Depends on:` row names
and every library, spec, or API a §6 decision rests on — or one line,
`no external dependency — <reason>`, which grill-lint checks against §9.
- Best sources:
- Wikified libraries (link to docs/graph/libraries/<name>.md):
- Key findings:
- Current best practices:
- Project-specific implications:
- Conflicts or uncertainty:

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| Design latitude: <creative / balanced / simple> | <what the answer allows this change> | <the owner's quote, or the session's recorded reason> | reversible | — | <date> |

The session classifies the `Design latitude:` row before the spec's §3,
asking the owner only in doubt, and every later step is held to it.
Depth: `specify.design-latitude` in
`docs/graph/protocols/specify-joint-pass.md`.

Reversibility takes the same graduated value here as it does in an ADR,
under the same rule. Depth: `docs/graph/templates/adr.template.md`.

## 7. Options Considered
| Option | Benefits | Costs | Risks | Outcome |
|---|---|---|---|---|

## 8. Architecture Plan
- System boundary:
- Main components:
- Interfaces:
- Data flow:
- Error handling:
- Observability:
- Security posture:
- Deployment model:
- Environment parity (a plan that changes a deploy chain;
  `grill.press`): <the versions each environment pins for the images
  and tools the chain touches, read from source, and any drift>

## 9. Implementation Plan

Each increment names: spec contracts satisfied, files touched, tests
to write (RED), behavior added, gate that proves it done, rollback
path, effort (one label), phase (`RED`, `GREEN` or `prose`; the labels,
and the batch sizes the two set, are `delegation.effort-scale` in
docs/graph/method/delegation-cycle-economy.md),
dependencies (the earlier increments it builds on and the
docs/graph/libraries/ pages it relies on; `none` if neither)
— and, when it adds structure (a module, layer, interface, service),
the single responsibility that structure owns and the present variation
justifying any abstraction. Rows are listed in dependency order.
Increments live in §9, inline (below) or as ledger files it indexes:
grill-lint runs its plan checks on §9, so a plan for a second spec
adds rows or ledger files here. Switch to the ledger when §9 starts
dominating the file; both forms may coexist while a plan migrates.
Why and how: `grill.increment-shape` in protocols/grill.md.

### Increment 1 — <title>
- Spec contracts: <SPEC-NNNN/contract-slug, ...>
- Files touched:
- Tests to write (RED): <N cases over SPEC-NNNN/contract-slug, ...; the tester names them — or `none — <why>; proved by <run>` when nothing here can be wrong while present>
- Behavior added:
- Gate:
- Rollback path:
- Effort:
- Phase:
- Depends on:

### Increment 2 — <title>
- ...

### Increment N — Consolidate the tests this spec added
- Spec contracts: <every contract whose tests this pass touches>
- Files touched: <the test files the spec added, and the older ones they overlap>
- Tests to write (RED): none — consolidation
- Behavior added: none; survey the spec's tests and their overlaps, rule on each, then merge or delete under `skill.test-first`
- Gate: the suite stays green and no contract loses its test
- Rollback path: revert the consolidation commit
- Effort:
- Phase:
- Depends on: <the last feature increment>

<!--
The consolidation increment is a default: keep it last when this spec
added many tests; when it added few, replace the row with
`no consolidation: <reason>`. Depth: `grill.increment-shape` in
protocols/grill.md.
-->

<!--
The ledger form of §9: an index, each row pointing at one increment file
under `docs/graph/plans/grill/`. `grill-lint.py` resolves the index and
holds the same required fields inside each file:

## 9. Implementation Plan

| # | Increment | Status | Detail |
|---|---|---|---|
| 1 | Validate schema | done | `plans/grill/increment-01-validate-schema.md` |
| 2 | Persist submissions | in-progress | `plans/grill/increment-02-persist.md` |

...with `plans/grill/increment-01-validate-schema.md` holding the block exactly
as written above, `### Increment 1 — Validate schema` heading included.
-->

## 10. Verification Plan
Covered by the project's standard gates — see
docs/graph/runbooks/verification.md. List a gate here only where this
plan diverges from the runbook (a new gate this work introduces, a
standard gate deliberately skipped and why); grill.md is read every
session, so the runbook stays the gates' one home.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Owner | Verification |
|---|---:|---:|---|---|---|

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|

One numbered row per open decision or finding, each with an owner —
this table is the open engineering backlog, its only home. Cite the
pinning test in "Pinned by"; mark rows needing human input
**do-not-guess** and leave them for sign-off; resolve a row in place
(strike-through, dated, with evidence), never by deleting it. Depth:
the grill-planner skill.

## 13. Done Criteria
Objective conditions that prove the work is complete. These align
with the spec's §9 acceptance criteria.

## 14. Recommended Next Step
One action.

## 15. Changelog
- YYYY-MM-DD: <entry>

<!--
Append in place (`rule.grill`): a follow-up investigation or deep-dive
that outgrows a changelog line becomes a new numbered section here
(§16, §17, …) holding findings; new plan work goes into §9. One file
stays the definitive state of the plan: earlier sections are struck
through when superseded, never silently rewritten or split off.
-->

