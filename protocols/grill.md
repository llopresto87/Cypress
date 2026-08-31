---
name: grill
description: Produce or refresh docs/graph/plans/grill.md — the project's plan-of-record — with explicit decisions, options, architecture sketch, increment plan mapped to spec contracts, verification gates, risks, and a single recommended next step. Use whenever a spec exists but no plan implements it yet, an existing plan is stale, an increment is being scoped, or the spec catalog and the plan have drifted. Every increment in §9 maps to spec contracts; that is what makes the plan spec-driven.
id: protocol.grill
tier: 2
kind: protocol
origin: seed
title: grill — producing and maintaining grill.md, the plan-of-record
owns:
  - rule.grill
  - grill.flow
  - grill.increment-shape
requires:
peers:
  - protocol.specify
  - protocol.test-first
artifacts:
  - templates/grill.template.md
load_when:
  - "plan the implementation, plan-of-record, grill.md"
  - "spec exists but no plan implements it"
  - "scope an increment, slice the work"
  - "plan is stale, assumption broke, architecture change"
est_tokens: 1200
command: true
---

# Protocol: grill

Use this when a spec exists (or is being authored in parallel) and you
need a plan-of-record before code. The deliverable is
`docs/graph/plans/grill.md` populated through §14, with explicit decisions,
options, an architecture sketch, implementation increments that map to
spec contracts, verification gates, risks, and a single recommended
next step.

This node owns **the grill rule** — `docs/graph/plans/grill.md` is the
living plan-of-record, the source of truth for *plans*, linked to the
specs it implements and the nodes it depends on. Open it when you
start, before you change architecture, when you finish, and whenever
an assumption breaks. Append to its changelog; strike through stale
claims, never silently rewrite. Template:
`docs/graph/templates/grill.template.md`.

"Grill" is for the discipline of grilling the *plan* until it's ready
to implement — pressing on the assumptions until they're solid,
pressing on the design until it's coherent, pressing on the plan
until each increment is small enough to be one RED-GREEN-REFACTOR
cycle (or a small handful).

## Entry conditions

- The goal is clear (either it came in clear or `brainstorm` has
  converged it).
- A spec exists in `docs/graph/specs/` or is being authored alongside this
  grill pass.
- Either no current grill.md exists for this feature, or the existing
  one is stale by more than a major implementation phase.

If the spec does not yet exist, run `docs/graph/protocols/specify.md` first or
in parallel. The two protocols often interleave: the architect drafts
spec §4 and a grill.md architecture sketch together because each
informs the other.

## Workflow

1. **Open or create grill.md** from `docs/graph/templates/grill.template.md`.
2. **§1 — Artifact Discovery.** Read what already exists. Files
   inspected, docs inspected, tests inspected, ADRs read, specs read,
   libraries already wikified, constraints already recorded. Cite
   paths. Do not guess; read.
3. **§5 — Research Summary.** Hand to `research-scout` for any
   library, spec, or API the plan depends on. For each, ensure a
   `docs/graph/libraries/` page exists; if not, run `ingest-library`.
4. **§6 — Decisions.** Make explicit choices; cite evidence; tag
   reversibility. Anything non-obvious gets an ADR (delegate to
   `architect`). When the plan needs a recurring operation — one a future
   session will run again — decide it as a **durable tool** (an increment
   in §9 with a stable interface and a test), not an inline throwaway, and
   check `docs/graph/tools/` for one that already exists (§3.8).
5. **§8 — Architecture Plan.** The boundary diagram and the
   contracts. Should align with the spec's §4.
6. **§9 — Implementation Plan.** Slice the work into increments.
   **Each increment names the spec contract(s) it satisfies, the
   files touched, the tests to write (in RED), the gate that proves
   it done, and a rollback path.**
7. **§10 — Verification Plan.** Which gates run for which
   increments.
8. **§11 — Risks and Mitigations.** Hand to `security` and
   `reliability` as relevant.
9. **§12 — Open Questions.** Every "we'll figure that out later"
   becomes a row here with a named owner and a resolution path.
10. **§13 — Done Criteria.** Objective conditions that prove the
    feature is complete. These must align with the spec's §9
    acceptance criteria.
11. **§14 — Recommended Next Step.** A single action — usually
    "enter `test-first` for increment 1".
12. **§15 — Changelog.** Add an entry describing this grill
    session.

The grill protocol is a *pass*: you might iterate it twice if
research reveals something that changes the architecture, and that's
fine — record what changed in the changelog.

## Increment shape (the most important section)

§9 is where grill earns its keep. A good increment in §9 looks like:

```markdown
### Increment 3 — Persist submissions
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM_RETURNS_2XX,
  SPEC-0001/SUBMIT_FORM_SCHEMA_INVALID
- Files touched: src/submissions/store.{ext}, tests/submissions/store_test.{ext}
- Tests to write (RED): test_submit_valid_form_persists,
  test_submit_invalid_schema_returns_422
- Behavior added: a persistence adapter that stores submissions and
  returns them by ID
- Gate: integration test against the test database; the suite stays
  green
- Rollback path: revert; no data migration
- Effort: ~1 RED-GREEN-REFACTOR cycle (~30 min)
- Depends on: increment 2 (schema validation)
```

If an increment doesn't fit this shape — vague tests, no spec
contract, no rollback — it isn't ready. Re-slice.

## Spec ↔ plan alignment check

Before exiting grill, verify:

- Every contract in the spec's §4 appears in at least one increment
  in §9.
- Every acceptance criterion in the spec's §9 maps to at least one
  contract that an increment implements.
- No increment introduces behavior not covered by a contract. (If
  one does, the spec is missing a contract — go back to `specify`.)

This check is what makes spec-driven development *actually*
spec-driven. Skip it and you'll find drift.

## Exit conditions

- §0–§14 populated for the current feature.
- Every library named in §5 has a wiki page.
- Every non-obvious decision has an ADR or a row in §6.
- Every increment in §9 names spec contracts and tests.
- Spec ↔ plan alignment check passes.
- §14 names a single next action.

## Anti-patterns

- **Skipping §1.** "I know what's in the repo." Read it.
- **Skipping §5.** "I know the library." The wiki says otherwise
  often enough that you must check.
- **Increments that touch ten files and add three new behaviors.**
  Slice them.
- **A risk table with three rows that all say "manageable".** Be
  specific about probability and impact.
- **A "next step" that is actually a list of next steps.** Pick the
  one that unblocks the most.
- **Plan with no spec link.** That's not a plan; that's a wish.
