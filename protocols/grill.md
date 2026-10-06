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
  - grill.plan-approval
  - grill.legal-checkpoint
requires:
peers:
  - protocol.specify
  - protocol.specify-joint-pass
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
prevents: Increments chosen one at a time with no plan-of-record, so nothing says which contract an increment satisfies and a broken assumption is discovered rather than recorded.
est_tokens: 4396
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

This node owns **the grill rule**: `docs/graph/plans/grill.md` is the
living plan-of-record, the source of truth for *plans*, linked to the
specs it implements and the nodes it depends on. Open it when you
start, before you change architecture, when you finish, and whenever
an assumption breaks. It is append-only: a change lands as a new
changelog entry, and a stale claim is struck through where it stands, so
the plan keeps its history. The session writes it; workers report
what they did in their handback. Template:
`docs/graph/templates/grill.template.md`. Gate:
`python3 docs/graph/grill-lint.py`: the plan's shape, its dependency
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
named owner. **The table is the spawn order** (`delegation.sequencing`
in `docs/graph/method/delegation-sequencing.md`: sequence by dependency,
parallelize by independence, never merge by hand). Two phases run side by
side ONLY where the last column says so. The §15 entry for the pass lists
its spawns by `spawn_id` in the order they were issued, which is what
makes the order auditable afterwards. When the spec is being written in the
same pass, run the joint pass instead (`specify.joint-pass`,
`docs/graph/protocols/specify-joint-pass.md`); the table below applies
when only the plan is being written.

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | §0 Metadata | orchestrator, in-session | — | — |
| 1 | §2 §3 §4 Shared Understanding, User Goal, Operating Constraints | orchestrator, in-session | §0 | — |
| 2 | §1 Artifact Discovery | orchestrator (router-bounded reads); an investigation-class worker for what the router does not bound | §2–§4 | — |
| 3 | §5 Research Summary | `research-scout`, one spawn per dependency without a wiki page (`ingest-library`) | §1 | — |
| 4 | §6 §7 §8 Decisions, Options, Architecture | `architect` → ADRs; `legal` inside its checkpoint | §5 | — |
| 5 | §9 §10 Implementation and Verification Plan | `architect` slices; `tester` confirms each row's RED tests are writable and owns §10 | §8, spec §4 | phase 6 |
| 6 | §11 Risks | `security` ∥ `reliability`; `legal` for externally-authored rules | §8 | phase 5 |
| 7 | press (`grill.press`) | orchestrator; `devils-advocate` for one-way doors | §9, §11 | — |
| 8 | §12 §13 §14 §15 | orchestrator, in-session | phase 7 | — |

What the table cannot hold:

- **§2–§4 come before §1.** They are conversation products: what the
  user asked for, the restatement both sides accept, the constraints
  the plan must operate under. Capture them before discovery colors
  them.
- **§1 is read, not recalled.** The router bounds what you read
  yourself; what lies outside that bound is read by an
  investigation-class worker briefed from
  `docs/graph/templates/prompts/investigation-brief.md`. Every §1 line
  cites a path or reads `none — <reason>`; a blank line fails the
  pass.
- **§5 is derived, not judged.** Its required set is every
  `docs/graph/libraries/` page an increment's `Depends on:` row names
  (increment shape below), plus any library, spec, or API a decision in
  §6 rests on. Hand each to `research-scout`; where the page is
  missing, that spawn runs `ingest-library`. A §5 with nothing to
  research says so, `no external dependency — <reason>`, and that is
  a falsifiable claim the lint checks against §9; the lint catches a
  silent §5, and ONLY you can check that the reason was earned. When phase 5 names a
  dependency §5 did not, phase 3 runs again for it before the pass
  exits.
- **§6/§7** make explicit choices, record the discarded options and
  why, cite evidence, tag reversibility. Anything non-obvious gets an
  ADR; an ADR that implicates externally-authored rules (licenses,
  regulation, data protection, standards, third-party terms) clears
  the architect's `legal` checkpoint before it is accepted
  (spawn-or-instantiate mechanics per `architect.legal-checkpoint`); a
  corpus gap is a §12 row ("not recorded — needs ingest"), never a
  recalled rule. When the plan needs a recurring operation, one a
  future session will run again, decide it as a **durable tool** (an
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
  Each risk row names its probability and its impact.
- **§12** turns every "we'll figure that out later" into a row with a
  named owner, a current assumption, and a resolution path
  (`grill-planner` owns the row discipline). **§13** aligns with the
  spec's §9 acceptance criteria. **§14** is one action, the one that
  unblocks the most (usually "enter `test-first` for increment 1").
  **§15** records the pass.

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
assumption re-enters the creation phase that owns what moved: phase 3 for
a dependency (the scout is spawned in revision exactly as in creation),
phase 4 for a decision. It then presses and exits as below. A red gate twice on one increment reopens this pass
(`protocol.recover`). Every revision ends green under `grill-lint.py`.

## Increment shape (`grill.increment-shape`)

§9 may hold increments **inline**, or as a **ledger**: an index row per
increment pointing at its own file under `docs/graph/plans/grill/`. Inline is
right while the plan is small. Switch to the ledger when §9 starts dominating
the file: a plan is read whole, and §9 is the section that grows for as long as
the project does, so a mature plan held in one file becomes the largest single
thing a session loads.

Both forms coexist, so a plan migrates one increment at a time. The contract is
unchanged either way: the required fields live with the increment, in whichever
file holds it, and `grill-lint.py` refuses an index row with no file, a file no
row points at, and an increment defined twice.

Increments live under §9 ONLY (inline, or in the ledger files it
indexes), because `grill-lint.py` runs its plan checks (dependency order,
required fields, spec alignment) on §9 and its ledger alone. A second spec
or a later phase adds §9 rows or ledger files.

§9 is where grill earns its keep. A good increment looks like:

```markdown
### Increment 3 — Persist submissions
- Spec contracts: SPEC-0001/SUBMIT_VALID_FORM_RETURNS_2XX,
  SPEC-0001/SUBMIT_FORM_SCHEMA_INVALID
- Files touched: src/submissions/store.{ext}, tests/submissions/store_test.{ext}
- Tests to write (RED): 2 cases over SPEC-0001/SUBMIT_VALID_FORM_RETURNS_2XX,
  SPEC-0001/SUBMIT_FORM_SCHEMA_INVALID; the tester names them
- Behavior added: a persistence adapter that stores submissions and
  returns them by ID
- Gate: integration test against the test database; the suite stays
  green
- Rollback path: revert; no data migration
- Effort: medium
- Phase: GREEN
- Depends on: increment 2 (schema validation); docs/graph/libraries/sqlalchemy.md
```

`Effort:` takes one label and `Phase:` one of `RED`, `GREEN` or `prose`.
Both vocabularies, and the batch sizes they set, are
`delegation.effort-scale` in `docs/graph/method/delegation-cycle-economy.md`.

`Depends on:` names both kinds of dependency: the earlier increments
this one builds on, and the `docs/graph/libraries/` pages it relies on
(the set §5 must cover). Increments are listed in dependency order: a
row that depends on a later row is misordered, and the orchestrator
reads §9 top to bottom when it sequences spawns. `none` is a valid
value; blank is not.

**A new pipeline or deploy path starts as a walking skeleton.** When the
plan adds one, its first increment lands the pipeline file, its image
and its declaration with every job stubbed, and runs it once on the real
CI target before any domain logic is written. Domain increments then
fill the skeleton, with a real run per batch. Ordered by contract group
instead, the pipeline lands last, and the defects only a real run can
show (wiring, permissions, paths, the image itself) all arrive at the
end, after the code they would have shaped. The spec can grow the same
way, one slice ahead of each RED (`specify.flow`). Until a group's
slice is signed, its increments' `Spec contracts:` field reads
`slice pending: <the behavior the slice will specify>`. Such a row is
not ready (below) and goes to no RED; when the slice lands, the row
names its slugs and the spec-plan alignment is pressed again for it.

**Ask of every increment: does it need a test?** Decide it here, while
slicing, not at RED. An increment needs a test when it adds behavior that
can be wrong while the code is present, and something breaks, for someone,
if it is (`test-first.proportionate-checks`). A declarative edit (a
selector, a pipeline stage, a flag, a config key) usually does not: its
field reads `none — <why>; proved by <run>`, naming the run that shows it
working, and the increment gets no RED spawn. `spec-lint.py` counts
the contracts that row names as covered by the run. A declaration that holds
logic (a pattern, a condition, an order that changes the output) does
need one. When the planner cannot tell, the row keeps its test and the
tester makes the call at RED, handing back unwritten if the answer is no.

`Tests to write (RED):` names contracts, not cases: the slug(s) and a case
cap no larger than the contract count. One case may cover several slugs, and
a failure mode with no real blast radius gets none
(`test-first.proportionate-checks`). The tester names the cases; a plan that
lists test names writes the suite twice, once in prose nobody runs.

An increment is ready when it names its spec contracts, its case cap
(or its `none` and the run that proves it), its rollback, and its dependencies, and the tester can write the failing
test from the row as written. An increment missing any of them is
re-sliced, and so is one that touches many files to add several
behaviors.

**The consolidation increment.** A spec whose increments added many
tests ends its §9 with one more increment, planned from the start:
survey the tests the spec added and the older tests they overlap, rule
on each overlap, then merge or delete under the proportionate-checks rules in
`skill.test-first`. Its `Spec contracts:` are the contracts whose tests
it touches, and its `Tests to write (RED):` reads `none — consolidation`.
Its gate is the suite staying green with no contract losing its test.
The template carries this row by default. The planner may drop it for a
spec that added few tests, and records the reason in the row's place.
It runs last, because only after the last feature increment has landed
can it see the whole set of tests.

## Press the plan (`grill.press`)

Filling the sections produces a document; this phase turns it into a
plan. It runs after §9 and §11 exist and before §14 is written, and in
a revision pass it presses only what moved.

**Design latitude.** Check every §6 decision and every §9 increment
against the plan's `Design latitude:` row. What the latitude allows,
and what the press does with anything outside it, is
`specify.design-latitude` in `docs/graph/protocols/specify-joint-pass.md`.

**Spec ↔ plan alignment.** Every contract in the spec's §4 appears in
at least one increment; every acceptance criterion in the spec's §9
maps to a contract an increment implements; no increment introduces
behavior no contract covers (if one does, the spec is missing a
contract: go back to `specify`). This check is what makes spec-driven
development *actually* spec-driven; `grill-lint.py` runs the first and
third mechanically.

**Assumptions.** For each increment, name the assumption whose failure
would invalidate it and where the plan records it: a §11 row with a
verifying check, or a §12 row with the current assumption and its
resolution path. A load-bearing claim still carrying `[verify]` in §9
or §13 is an assumption with no home — resolve it or move it to §12.
A value that needs human input is marked **do-not-guess** in §12 and
left for sign-off, because a guessed value would read as settled.

**Environment parity.** A plan that changes a deploy chain reads, once
and from source, the versions each environment pins for the images and
tools the chain touches, and records any drift as a §11 risk or a §9
increment. Drift between environments otherwise surfaces only when
someone happens to ask. A production pin that can be read only on the
running system, not in source, is touching a live workload and waits
for the owner (`vcs-posture.publish-authorization`).

**Refutation.** On a T3 plan, any one-way door (`architect`
reversibility class) and the top risk by probability × impact go to
`devils-advocate` as a finished, claim-bearing deliverable for its
bounded refutation pass. A `refuted` verdict reopens the phase that
owns the claim; `could-not-refute` is recorded beside the §6 or §11
row. It is one spawn per pass on T3 plans ONLY; T2 work (a covered-lane
revision or a contained-lane change) adds its grill.md line and moves on.

## Plan approval (`grill.plan-approval`)

This step runs when the pressed plan goes to the owner for approval
before the first RED; a plan that does not go to the owner skips it.
When it runs, that message asks **once** for everything only the owner
can give. It is one numbered list with two parts:

1. **The cost levers this plan uses.** Any cost lever the plant's
   doctrine defines: a setting that decides how much each increment
   costs or how fast the work moves. Ask only for the levers the plan
   actually pulls, and give the default the plan assumes for each, so
   the owner can answer "defaults" in one word. Where the doctrine
   defines none, this part is empty and says so.
2. **Every owner-only prerequisite.** Each step in §9 that only the
   owner can take: a platform setting, an approval, a merge, a
   credentialed call, access to an environment. Name the increment
   that needs it. Where the plan repeats a non-production act that
   needs the owner's authorization (pushing the feature branch,
   queueing a named test pipeline), ask here for a scoped standing
   grant that names those acts and targets, instead of one ask per act;
   its bounds are `vcs-posture.publish-authorization`'s.

Record the answers in §4 under "Cost constraints", dated, and cite them
from the briefs of the workers they bind. Asked up front, the
prerequisites land while the code is being built, instead of stalling
the increment that reaches them. A lever set before the first spawn
goes into every brief from the start. A lever set later has to be
relayed to workers already running, and each relay costs a message and
risks a worker that never got it. A lever the owner leaves open keeps
the plan's stated default; that is recorded too, so nobody asks again.

A revision pass asks again only when the plan gained a lever or a
prerequisite the owner has not already answered.

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
- Every §9 increment fits the shape (contracts, RED tests, rollback,
  dependencies), and the rows are in dependency order.
- Spec ↔ plan alignment holds; no `[verify]` survives in §9 or §13.
- Where the plan went to the owner for approval, the plan-approval ask
  went out as one message, and §4 "Cost constraints" records its
  answers or the defaults left in force.
- §14 names a single next action.
- `python3 docs/graph/grill-lint.py` exits 0.
