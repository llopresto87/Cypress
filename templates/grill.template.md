<!--
Template: grill.template.md
Authored by: orchestrator, grill-planner
Lives at: docs/graph/plans/grill.md
Used: once per project; updated continuously
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
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
- Cost constraints:
- Latency constraints:
- Compliance constraints:
- Maintenance constraints:

## 5. Research Summary
- Best sources:
- Wikified libraries (link to docs/graph/libraries/<name>.md):
- Key findings:
- Current best practices:
- Project-specific implications:
- Conflicts or uncertainty:

## 6. Decisions Made
| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|

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

## 9. Implementation Plan

Each increment names: spec contracts satisfied, files touched, tests
to write (RED), behavior added, gate that proves it done, rollback
path, estimated effort, dependencies — and, when it adds structure
(a module, layer, interface, service), the single responsibility that
structure owns and the present variation justifying any abstraction.

### Increment 1 — <title>
- Spec contracts: <SPEC-NNNN/contract-slug, ...>
- Files touched:
- Tests to write (RED):
- Behavior added:
- Gate:
- Rollback path:
- Effort:
- Depends on:

### Increment 2 — <title>
- ...

## 10. Verification Plan
Covered by the project's standard gates — see
docs/graph/runbooks/verification.md. List a gate here ONLY where this
plan diverges from the runbook (a new gate this work introduces, a
standard gate deliberately skipped and why); grill.md is read every
session and must not duplicate the runbook it points at.

## 11. Risks and Mitigations
| Risk | Probability | Impact | Mitigation | Verification |
|---|---:|---:|---|---|

## 12. Open Questions
| # | Question | Why it matters | Current assumption | How to resolve | Owner | Pinned by |
|---:|---|---|---|---|---|---|

One numbered row per open decision or finding, each with an owner —
this table IS the open engineering backlog (no side list). Cite the
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
Append, don't fork. When a follow-up investigation or ad-hoc deep-dive
grows past a changelog line, capture it as a new top-level numbered
section appended here (§16, §17, …) rather than spawning a separate
document. One file stays the definitive state of the plan, consistent
with §15's append-only discipline: earlier sections are struck through
when superseded, never silently rewritten or split off.
-->

