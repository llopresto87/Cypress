---
name: grill
description: Produce or revise docs/graph/plans/grill.md — the project's plan-of-record — with explicit decisions, options, architecture sketch, increment plan mapped to spec contracts, verification gates, risks, and a single recommended next step. Use whenever a spec exists but no plan implements it yet, an increment shipped and the plan must record it, an increment is being scoped, an assumption broke, or the spec catalog and the plan have drifted. Every increment in §9 maps to spec contracts; that is what makes the plan spec-driven.
id: protocol.grill
tier: 2
kind: protocol
origin: seed
title: grill — producing and maintaining grill.md, the plan-of-record
owns:
  - rule.grill
  - grill.flow
  - grill.revise
  - grill.increment-shape
  - grill.press
  - grill.legal-checkpoint
requires:
peers:
  - protocol.specify
  - protocol.test-first
  - agent.devils-advocate
artifacts:
  - templates/grill.template.md
  - templates/knowledge-graph/grill-lint.py
load_when:
  - "plan the implementation, plan-of-record, grill.md"
  - "spec exists but no plan implements it"
  - "scope an increment, slice the work"
  - "an increment shipped, revise the plan, record what happened"
  - "plan is stale, assumption broke, architecture change"
est_tokens: 2300
command: true
---

# Protocol: grill

Use this when a spec exists (or is being authored in parallel) and you
need a plan-of-record before code, and again every time that plan has
to move. The deliverable is `docs/graph/plans/grill.md` populated
through §15, with explicit decisions, options, an architecture sketch,
implementation increments that map to spec contracts, verification
gates, risks, and a single recommended next step. The protocol has two
passes over the same document: **creation** (`grill.flow`) and
**revision** (`grill.revise`). Most sessions run the second.

This node owns **the grill rule** — `docs/graph/plans/grill.md` is the
living plan-of-record, the source of truth for *plans*, linked to the
specs it implements and the nodes it depends on. Open it when you
start, before you change architecture, when you finish, and whenever
an assumption breaks. Append to its changelog; strike through stale
claims, never silently rewrite. Template:
`docs/graph/templates/grill.template.md`. Gate:
`python3 docs/graph/grill-lint.py` — the plan's shape, its dependency
order, and its spec alignment, checked mechanically.

"Grill" is a verb. It is the discipline of grilling the *plan* until
it is ready to implement — pressing on the assumptions until they are
solid, pressing on the design until it is coherent, pressing on the
plan until each increment is small enough to be one RED-GREEN-REFACTOR
cycle (or a small handful). Filling the sections is how the plan is
written down; the pressing (`grill.press`) is what makes it a plan.

## Entry conditions

**Creation pass.** The goal is clear (either it came in clear or
`brainstorm` has converged it); a spec exists in `docs/graph/specs/`
or is being authored alongside this pass; and either no current
grill.md exists for this feature or the existing one is stale by more
than a major implementation phase.

**Revision pass.** grill.md exists and something moved: an increment
shipped, research or implementation changed a decision, a risk or
open question surfaced, the plan and the spec catalog drifted, or a
session is closing and §15 needs its entry.

If the spec does not yet exist, run `docs/graph/protocols/specify.md`
first or in parallel. The two protocols often interleave: the
architect drafts spec §4 and a grill.md architecture sketch together
because each informs the other.

## The creation pass (`grill.flow`)

The pass is a sequence of phases, each filling named sections with a
named owner. **The table is the spawn order.** A phase's spawn is
issued only after every handback it needs has returned; two phases run
side by side only where the last column says so. The general rule —
sequence by dependency, parallelize by independence, never merge by
hand — is `delegation.sequencing` in
`docs/graph/method/delegation.md`. The §15 entry for the pass lists its
spawns by `spawn_id` in the order they were issued, which is what makes
the order auditable afterwards.

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | §0 Metadata | orchestrator, in-session | — | — |
| 1 | §2 §3 §4 Shared Understanding, User Goal, Operating Constraints | orchestrator, in-session | §0 | — |
| 2 | §1 Artifact Discovery | orchestrator (router-bounded reads); a sonnet investigation for what the router does not bound | §2–§4 | — |
| 3 | §5 Research Summary | `research-scout`, one spawn per dependency without a wiki page (`ingest-library`) | §1 | — |
| 4 | §6 §7 §8 Decisions, Options, Architecture | `architect` → ADRs; `legal` inside its checkpoint | §5 | — |
| 5 | §9 §10 Implementation and Verification Plan | `architect` slices; `tester` confirms each row's RED tests are writable and owns §10 | §8, spec §4 | phase 6 |
| 6 | §11 Risks | `security` ∥ `reliability`; `legal` for externally-authored rules | §8 | phase 5 |
| 7 | press (`grill.press`) | orchestrator; `devils-advocate` for one-way doors | §9, §11 | — |
| 8 | §12 §13 §14 §15 | orchestrator, in-session | phase 7 | — |

What the table cannot hold:

- **§2–§4 come before §1.** They are conversation products — what the
  user asked for, the restatement both sides accept, the constraints
  the plan must operate under. Capture them before discovery colors
  them.
- **§1 is read, not recalled.** The router bounds what you read
  yourself (kernel §2; Turn 0's "do not bulk-read" is about
  orientation, not discovery); what lies outside that bound is read by
  a sonnet worker briefed from
  `docs/graph/templates/prompts/investigation-brief.md`, never guessed.
  Every §1 line cites a path or reads `none — <reason>`; a blank line
  fails the pass.
- **§5 is derived, not judged.** Its required set is every
  `docs/graph/libraries/` page an increment's `Depends on:` row names
  (increment shape below), plus any library, spec, or API a decision in
  §6 rests on. Hand each to `research-scout`; where the page is
  missing, that spawn runs `ingest-library`. A §5 with nothing to
  research says so — `no external dependency — <reason>` — and that is
  a falsifiable claim the lint checks against §9. When phase 5 names a
  dependency §5 did not, phase 3 runs again for it before the pass
  exits.
- **§6/§7** make explicit choices, record the discarded options and
  why, cite evidence, tag reversibility. Anything non-obvious gets an
  ADR; an ADR that implicates externally-authored rules (licenses,
  regulation, data protection, standards, third-party terms) clears
  the architect's `legal` checkpoint before it is accepted —
  spawn-or-instantiate mechanics per `architect.legal-checkpoint`; a
  corpus gap is a §12 row ("not recorded — needs ingest"), never a
  recalled rule. When the plan needs a recurring operation — one a
  future session will run again — decide it as a **durable tool** (an
  increment in §9 with a stable interface and a test), not an inline
  throwaway, and check `docs/graph/tools/` for one that already exists
  (§3.8).
- **§8** is the boundary diagram and the contracts, aligned with the
  spec's §4.
- **§10 records divergences only.** The standard gates live in
  `docs/graph/runbooks/verification.md`; §10 names a gate this work
  introduces or a standard gate it deliberately skips, and why.
- **§11** hands boundary, contract, and dependency exposure to
  `security` and `reliability`; exposure to externally-authored rules
  goes to `legal` alongside them, under the same checkpoint mechanics.
- **§12** turns every "we'll figure that out later" into a row with a
  named owner, a current assumption, and a resolution path
  (`grill-planner` owns the row discipline). **§13** aligns with the
  spec's §9 acceptance criteria. **§14** is one action — usually "enter
  `test-first` for increment 1". **§15** records the pass.

The creation pass is iterative: research can change the architecture
and send phase 4 round again. Record what changed in §15.

## The revision pass (`grill.revise`)

1. Append the §15 entry first — increment title, spec contracts
   covered, files touched, gates run and their outcomes, the
   `spawn_id`s of the work in the order issued.
2. Cross out completed §9 rows (never delete); add rows the increment
   revealed, in the shape below.
3. A changed decision is a new §6 row with the date; the superseded
   row is struck, not edited.
4. A new risk is a §11 row; a resolved §12 row moves to §6 or §11 in
   place (strike-through, dated, with evidence).
5. §14 names the next highest-leverage action.

A revision that adds a dependency, moves a boundary, or breaks an
assumption is not a bookkeeping change: it re-enters the creation phase
that owns what moved — phase 3 for a dependency (the scout is spawned in
revision exactly as in creation), phase 4 for a decision — then presses
and exits as below. A red gate twice on one increment reopens this pass
(`protocol.recover`). Every revision ends green under `grill-lint.py`.

## Increment shape (`grill.increment-shape`)

§9 is where grill earns its keep. A good increment looks like:

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
- Depends on: increment 2 (schema validation); docs/graph/libraries/sqlalchemy.md
```

`Depends on:` names both kinds of dependency — the earlier increments
this one builds on, and the `docs/graph/libraries/` pages it relies on
(the set §5 must cover). Increments are listed in dependency order: a
row that depends on a later row is misordered, and the orchestrator
reads §9 top to bottom when it sequences spawns. `none` is a valid
value; blank is not.

An increment is ready when it names its spec contracts, its RED tests,
its rollback, and its dependencies, and the tester can write the failing
test from the row as written. One that fails any of those — vague
tests, no contract, no rollback, blank dependencies, a test the tester
cannot write — is re-sliced.

## Press the plan (`grill.press`)

Filling the sections produces a document; this phase turns it into a
plan. It runs after §9 and §11 exist and before §14 is written, and in
a revision pass it presses only what moved.

**Spec ↔ plan alignment.** Every contract in the spec's §4 appears in
at least one increment; every acceptance criterion in the spec's §9
maps to a contract an increment implements; no increment introduces
behavior no contract covers (if one does, the spec is missing a
contract — go back to `specify`). This check is what makes spec-driven
development *actually* spec-driven; `grill-lint.py` runs the first and
third mechanically.

**Assumptions.** For each increment, name the assumption whose failure
would invalidate it and where the plan records it: a §11 row with a
verifying check, or a §12 row with the current assumption and its
resolution path. A load-bearing claim still carrying `[verify]` in §9
or §13 is an assumption with no home — resolve it or move it to §12.
The plan never resolves one by guessing; a value that needs human
input is **do-not-guess** in §12 and left for sign-off.

**Refutation.** On a T3 plan, any one-way door (`architect`
reversibility class) and the top risk by probability × impact go to
`devils-advocate` as a finished, claim-bearing deliverable for its
bounded refutation pass. A `refuted` verdict reopens the phase that
owns the claim; `could-not-refute` is recorded beside the §6 or §11
row. This is one spawn per pass, not a standing gate, and a T2
revision does not incur it.

## Exit conditions

"Populated" means every section §0–§15 carries either content or an
explicit one-line `not applicable — <reason>`; a template label with
nothing after it is neither.

- §0–§15 populated; the §15 entry for this pass lists its spawns by
  `spawn_id` in issue order.
- Every §1 line cites a path or reads `none — <reason>`.
- §5 covers every library page §9 depends on and every page it names
  exists; an empty §5 states why.
- Every non-obvious decision has an ADR or a row in §6; every one-way
  door has been pressed.
- Every §9 increment fits the shape — contracts, RED tests, rollback,
  dependencies — and the rows are in dependency order.
- Spec ↔ plan alignment holds; no `[verify]` survives in §9 or §13.
- §14 names a single next action.
- `python3 docs/graph/grill-lint.py` exits 0.

## Anti-patterns

- **"I know what's in the repo."** A §1 line with no path. Read it.
- **"I know the library."** A §5 silent about a page §9 depends on.
  The lint catches the silence; only you can catch a `no research
  needed` you did not earn.
- **Spawning across a dependency edge.** Two phases issued together
  because the list looked flat. The table says which pair is parallel;
  everything else is a merge conflict you scheduled.
- **Increments that touch ten files and add three new behaviors.**
  Slice them.
- **A risk table with three rows that all say "manageable".** Be
  specific about probability and impact.
- **A "next step" that is actually a list of next steps.** Pick the
  one that unblocks the most.
- **Plan with no spec link.** That's not a plan; that's a wish.
