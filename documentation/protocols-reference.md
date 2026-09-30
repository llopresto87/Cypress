# CYPRESS Protocols Reference

A protocol node is the entry point for a kind of work; see the glossary's [protocol entry](../DOCUMENTATION.md#term-protocol).

This document is a complete reference for the 17 protocol nodes of the
CYPRESS seed. Each protocol is a routable graph node. It lives as a
plain Markdown file with YAML frontmatter in `protocols/`. When a plant
is grown, these files install into `docs/graph/protocols/`.

Source of this reference: every file in `protocols/*.md`, read directly
from disk. The default-sequence and tier facts are cited from
`core/AGENTS.md` (the kernel).

Each node also declares `prevents:` — the failure its own absence produces. It is not mirrored here; that would be a second home for one judgement per node. `python3 tools/roster-justification.py` prints it alongside the responsibility, the overlaps and the routing demand, reading each column out of the node that owns it ([ADR-0008](../docs/decisions/adr-0008-roster-justification-lives-in-the-node.md)).

The kernel rule
(`core/AGENTS.md` §2) says: "State which protocol you are entering
before you begin." The router maps *where the work stands* to a
`protocol.*` node.

---

## Summary table

All 17 protocols are tier 2 nodes with `origin: seed`, `kind: protocol`.

| Protocol | id | owns (facts) | requires | peers | est_tokens |
|----------|----|--------------|----------|-------|-----------|
| brainstorm | `protocol.brainstorm` | `brainstorm.mode-selection`, `brainstorm.entry-and-exit`, `brainstorm.output-landing` | — | skill.brainstorm-socratic, skill.brainstorm-internal, humanizer, specify, grill, from-scratch | 1244 |
| specify | `protocol.specify` | `rule.spec`, `specify.flow`, `specify.revision-discipline` | — | brainstorm, grill, specify-joint-pass | 2127 |
| specify-joint-pass | `protocol.specify-joint-pass` | `specify.joint-pass`, `specify.design-latitude` | — | specify, grill | 1101 |
| grill | `protocol.grill` | `rule.grill`, `grill.flow`, `grill.revise`, `grill.increment-shape`, `grill.press`, `grill.plan-approval`, `grill.legal-checkpoint` | — | specify, specify-joint-pass, test-first, agent.devils-advocate | 3820 |
| test-first | `protocol.test-first` | `rule.test-first`, `test-first.cycle`, `test-first.characterize-first`, `test-first.known-bug` | — | verify, specify, skill.test-first, skill.holistic-editing | 3391 |
| verify | `protocol.verify` | `rule.verify`, `verify.gate-states`, `verify.gate-classes`, `verify.risk-depth`, `verify.null-result`, `verify.composition`, `verify.silent-substitutes`, `verify.test-first` | — | test-first, recover, canonize, deliver, skill.validate-knowledge, verify-new-gates, verify-disagreement | 5706 |
| verify-new-gates | `protocol.verify-new-gates` | `verify.status-evidence`, `verify.tool-faults` | — | verify, verify-disagreement | 758 |
| verify-disagreement | `protocol.verify-disagreement` | `verify.characterize`, `verify.measure-integrity` | — | verify, verify-new-gates | 1800 |
| recover | `protocol.recover` | `recover.failure-classes`, `recover.three-attempt-boundary` | — | deliver, grill | 1757 |
| canonize | `protocol.canonize` | `rule.canonize`, `canonize.close-out-flow`, `canonize.status-review`, `canonize.deviation-capture`, `canonize.why-record`, `canonize.session-record` | `skill.toolcraft` | agent.tool-smith, deliver, harvest, skill.adr-writer | 3619 |
| deliver | `protocol.deliver` | `rule.deliver`, `deliver.forms`, `deliver.attribution-assertion`, `deliver.numbered-decisions` | — | canonize, recover | 2471 |
| ingest-library | `protocol.ingest-library` | `ingest-library.flow`, `ingest-library.refresh`, `ingest-library.corpus-first` | — | harvest, skill.library-wiki, skill.research-and-ingest | 1686 |
| from-scratch | `protocol.from-scratch` | `from-scratch.phases`, `from-scratch.entry` | — | brainstorm, grill, ingest-library, canonize, initialize | 2532 |
| grow | `protocol.grow` | `grow.worker-topology`, `grow.write-boundaries`, `grow.knowledge-shape`, `grow.growth-flow`, `grow.completeness-contract`, `grow.gate-table`, `grow.stack-inventory`, `grow.node-authoring`, `grow.librarian-pass`, `grow.plant-facts`, `grow.legal-corpus` | `method.delegation` | harvest, graft, initialize, ingest-library, canonize, deliver, recover, from-scratch, method.engineering-posture, method.design-posture | 13096 |
| harvest | `protocol.harvest` | `harvest.fold-back-flow`, `harvest.agnosticism-gate`, `harvest.availability-gate`, `harvest.corpus-contracts` | `method.delegation` | method.minimum-sufficient-work, skill.humanizer, canonize, graft, grow, ingest-library, skill.toolcraft | 11551 |
| graft | `protocol.graft` | `graft.reconcile-flow`, `graft.user-sovereignty`, `graft.pure-graph-mandate`, `graft.migration`, `graft.integrity-gates`, `graft.reversibility` | `method.delegation` | grow, harvest, deliver, method.engineering-posture | 19426 |
| initialize | `protocol.initialize` | `initialize.entry-fork`, `initialize.adapter-edges` | — | grow, from-scratch, seed-installer | 994 |

Six of the protocols also own one of the kernel's eight `rule.*`
facts: `rule.spec` (specify), `rule.grill` (grill), `rule.test-first`
(test-first), `rule.verify` (verify), `rule.deliver` (deliver),
`rule.canonize` (canonize). The kernel keeps only the one-line §3.x anchors;
the depth lives in the owning node. The other two live in skills:
`rule.knowledge` in `context-router`, and `rule.toolcraft` in `toolcraft`,
a skill because its three jobs sit apart: the rule every session reads, the
`tool-smith` agent that builds, and the `canonize` close-out that catalogs. So
this list is six and the kernel's is eight. `RULE_HOMES` in `tests/seed-lint.py` is the machine-checked
home for all eight.

---

## The default T3 sequence and how protocols chain

Source: `core/AGENTS.md` §0 (tier table) and §2 (protocol entry).

The kernel defines four work tiers:

| Tier | What it is | How it runs |
|------|-----------|-------------|
| T0 | a question — nothing changes | read minimal nodes, answer with citations |
| T1 | a trivial edit, no behavior/contract/spec surface | edit in-session; one focused gate |
| T2 | a contained change: authorized by an active spec + plan (*covered lane*), or small, local and reversible with no spec over it (*contained lane*) | minimal worker set + close-out |
| T3 | change beyond what that holds (architecture, contracts, dependencies, ambiguity) and anything no other row covers | full funnel, all doing delegated |

Hard edges (kernel): an edit that *could* alter behavior, an interface, a
persisted format, security posture, or anything a spec covers is T2 or
higher. The covered lane needs an active spec contract. The contained lane
needs all five: one surface, no new dependency, reversible, no spec owns it,
intent fits a decision note. Any doubt in any of them is T3. On the contained lane the RED test
is the contract and the close-out's why-record is the history; depth in
`method.tiers` (`tiers.contained-lane`).

The **default T3 sequence** (kernel §2), verbatim:

> brainstorm\* → specify → grill → ingest-library\* → test-first →
> verify → canonize → deliver (implementation lives inside test-first's GREEN phase).
> On any failure: `protocol.recover`. `harvest` and `graft` are
> user-sovereign: enter them only when the owner starts them; unprompted,
> you may only propose one.

The `*` marks steps that run only when they apply: brainstorm only when
the goal is vague; ingest-library only when a new dependency is
introduced. `implement` is the coding step; the seed drives it through
`test-first`, and ships no separate `implement` protocol file.

How the protocols chain:

1. **brainstorm** converges a vague goal into a precise problem
   statement, then feeds **specify**.
2. **specify** authors the executable spec, then hands off to **grill**.
3. **grill** builds the plan-of-record whose increments map to spec
   contracts, then names "enter test-first for increment 1".
4. **ingest-library** runs before any code touches a new dependency;
   grill and from-scratch call it.
5. **test-first** drives each increment RED → GREEN → REFACTOR →
   COMMIT, calling **verify** at the end of each increment.
6. **verify** runs the risk-proportional gates.
7. **canonize** is the single close-out spawn; it executes the
   **toolcraft** doctrine in the same pass.
8. **deliver** ends every session in a cold-pickup state, after the
   canonize close-out has run for T2/T3.
9. **recover** is entered on any failure: the failure-discipline
   detour off any step.
10. **from-scratch** wraps the whole sequence for a brand-new project
    (nine phases). **grow** / **harvest** / **graft** / **initialize**
    are the seed's own meta-loop, described below.

---

## Per-protocol reference

The protocols below are grouped by role: the core delivery funnel
(brainstorm → specify → grill → test-first → verify, with the sibling
leaves specify-joint-pass, verify-new-gates and verify-disagreement
beside their parents), the close-out and
handoff protocols (recover, canonize, deliver), the
dependency and bootstrap protocols (ingest-library, from-scratch), and
the seed meta-loop (grow, harvest, graft, initialize).

---

## brainstorm

*Source: `protocols/brainstorm.md`*

- **id:** `protocol.brainstorm`, tier 2
- **owns:** `brainstorm.mode-selection`, `brainstorm.entry-and-exit`,
  `brainstorm.output-landing`
- **requires:** —
- **peers:** `skill.brainstorm-socratic`, `skill.brainstorm-internal`,
  `skill.humanizer`, `protocol.specify`, `protocol.grill`,
  `protocol.from-scratch`
- **load_when:** "goal is vague, build me a thing"; "stakeholders disagree
  about scope"; "what should we actually build, converge the idea"; "problem
  statement, first useful slice"; "generate options for a decision nobody needs
  to confirm"; "shaped alternatives, is this mine to decide or theirs"

### What it does

Use brainstorm when the goal is vague, contested, or under-specified.
The deliverable is a precise problem statement, a primary user, a first
useful slice, the constraints, and a shaped set of options. Brainstorm
converges; code and the stack come later.

### Entry conditions

One or more of:
- The user said "build me a thing", "we should look into X", "what if
  we did Y", or otherwise expressed a goal without a defined outcome.
- The goal mentions a verb but not the user.
- The goal mentions the user but not the outcome.
- The team has competing visions for the goal.

### The technique

The questioning technique itself lives in the skill `docs/graph/skills/brainstorm-socratic.md`: question selection,
one-to-three-questions-per-turn pacing, the reflect-every-two-answers
cadence, the nine-question hard cap, the eight-point convergence
checklist, and the questioning pitfalls. This protocol owns only
*when you enter*, *where the output lands*, and *when you are done*.

### Output landing

The brainstorm output is written directly into sections of
`docs/graph/plans/grill.md`:

| grill.md section | content |
|------------------|---------|
| Section 2 | problem statement |
| Section 3 | primary user, primary outcome, acceptance criteria (drafted from success criteria), non-goals |
| Section 4 | operating constraints |
| Section 7 | shaped options |
| Section 11 | risks |
| Section 12 | assumptions and open questions |

If the project has no grill.md yet, create one from the template
(`docs/graph/templates/grill.template.md` or
`docs/graph/protocols/grill.md`).

### Exit conditions

- The skill's convergence checklist is satisfied (or each gap is a
  flagged assumption in grill.md §12).
- The user has confirmed the problem statement, the primary user, and
  the first useful slice. Confirmation is explicit ("yes", "looks
  right"), not assumed from silence.
- The next protocol (`grill` or `from-scratch` Phase 2) has an
  unambiguous entry point.

---

## specify

*Source: `protocols/specify.md`*

- **id:** `protocol.specify`, tier 2
- **owns:** `rule.spec`, `specify.flow`, `specify.revision-discipline`
- **requires:** —
- **peers:** `protocol.brainstorm`, `protocol.grill`,
  `protocol.specify-joint-pass`
- **load_when:** "write a spec, no spec covers this behavior"; "new feature,
  endpoint, job, or LLM interaction to define"; "changing an existing
  feature's contract"; "bug revealed an implicit or missing contract";
  "acceptance criteria, Given/When/Then, failure modes"
- **artifacts:** `templates/spec.template.md`,
  `templates/knowledge-graph/spec-lint.py`

### What it does

Use specify when the goal is clear and you need an executable
specification before planning the implementation. The deliverable is a
file in `docs/graph/specs/` populated through every section of the spec
template, signed off in §0 by product, architect, and tester (security
where it reviewed) — and still `draft`: the spec turns `active` in the
change that lands its RED tests.

This node owns **the spec rule** (`rule.spec`): specs are the source of
truth for *behavior*. Every non-trivial behavior has a spec, written
before the code, with stable section numbers; every functional contract
maps to at least one test; superseded specs stay on disk with a link
forward. The one exception is the **T2 contained lane**: a change whose
contract is the RED test that pins it and whose why is the close-out's
why-record. It enters `specify` only if it leaves the lane, and it holds
only while every one of the lane's conditions holds (`tiers.contained-lane`
owns them). A change that needs prose to be explicable is spec-bearing
work, and size alone never qualifies a change for the lane. If wiki and spec disagree about how a library *can* be used,
the wiki is right; if product and spec disagree about what to build,
fix the spec.

### Entry conditions

One of: `brainstorm` converged on a first useful slice; an existing
feature's contract is changing; a bug investigation revealed an
incomplete or wrong spec; an ADR introduces a new behavior.

### The pass (`specify.flow`)

A phase table with a named owner per phase; **the table is the spawn
order** (`delegation.sequencing`), and two phases run side by side only
where the table says so. The work is spawned, in clean contexts. If the
host cannot spawn the required model classes, the session stops and
reports, because an orchestration chat would produce sign-offs no
specialist gave; a missing *type* is `delegation.harness-registration`,
and the work goes on.

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | the design-latitude classification; identifier; §0 §1 §2 | orchestrator | the goal | — |
| 1 | §3 | `product` | §2 | — |
| 2 | §4 §5 §6 §7 §8 | `architect` | §3 | — |
| 3 | §9 (maps to §4 slugs) | `product` | §4 | 4 |
| 4 | §10; testability review of §4 | `tester` | §4 §7 §8 | 3 |
| 5 | adversarial §7 / §5 | `security`, sensitive surface only | §4 §7 | 3–4 |
| 6 | §11; sign-offs in §0; §12; grill.md §3/§9 links | orchestrator; signers tick §0 | 3–5 | — |

Notes: the identifier is the next free number on disk, and the catalog
row is the librarian's at close-out. §3 before §4, §4 before §9 — a §9
written beside §3 maps to nothing. §10 carries one `pending` row per
contract and failure mode; a contract that fails the testability review
returns to `architect` as an attempt under `recover`'s three-attempt
boundary. **Sign-off is not promotion**: the ticks land in §0 while the
spec is `draft`; `active` lands with the first RED (`test-first`
COMMIT, owned by `verify.status-evidence`), `implemented` when every
contract is green — `spec-lint.py` counts only live specs, so a signed
draft is planned against and encoded, never reported uncovered. A
signed draft is what `grill` plans against. When no plan exists yet
either, the spec and the plan come from one joint pass
(`protocol.specify-joint-pass`).

### Revising an existing spec

Decide clarification vs change. Clarifications edit in place with a §12
row; changes copy to a new identifier, mark the old `superseded` with a
link forward, and update everything that depended on it. A behavior
change always arrives as a new spec, so the catalog records what changed,
when and why.

### Exit conditions

"Populated" = content or an explicit `not applicable — <reason>`. The
file exists, populated, `draft` with product ✓ architect ✓ tester ✓
(security ✓ where reviewed) in §0; every §4 contract has a §10 row;
every §9 criterion maps to a real slug; §11 is empty or flagged in
grill.md §12; grill.md links the spec from §3 and §9;
`python3 docs/graph/spec-lint.py` exits 0 (the shape checks,
mechanically, for every spec on disk).

### What a spec states

A spec states behavior as an executable contract: what the system does,
not how it stores or computes it. Every contract carries its failure
modes (§7) and three real examples (§8), because a happy path alone is
half a spec and examples are the bridge from contract to test. A spec
written after the code carries status `back-written`. The spec turns
`active` with its first RED test, not at sign-off: an `active` spec with
no test would be a red gate for the whole test-first phase.

## specify-joint-pass

- **id:** `protocol.specify-joint-pass`, tier 2, from `protocols/specify-joint-pass.md`
- **owns:** `specify.joint-pass`, `specify.design-latitude`
- **requires:** none
- **peers:** `protocol.specify`, `protocol.grill`
- **load_when:** "write the spec and the plan together, joint specify and
  grill pass"; "design latitude, creative balanced or simple, how much
  design freedom"; "out of scope under simple, the owner did not ask for
  it"
- **command:** none; it is entered from `specify` or `grill`

### What it does

Writes the spec and the plan-of-record in one pass, in which each
specialist writes its spec part and its plan part in the same spawn.
Before any of it, the session classifies how much design latitude the
change has, and every later step is held to that value.

### Design latitude (`specify.design-latitude`)

`creative` lets the design propose new structure, concepts or scope,
each surfaced as a decision the owner can refuse. `balanced` allows new
structure where the change needs it and no concept the goal did not ask
for. `simple` is the smallest design that meets the goal: no new gates,
kinds, agents or renamed concepts, and when in doubt a thing is out of
scope. The session classifies the value the way it classifies a tier,
from the request, its tone and what the work is for, and states it with
its reason. It asks the owner only when the request leaves the value in
doubt, once, at the start of the spec definition. The value is a plan §6
row whose first cell begins `Design latitude:`, with the session's reason
or the owner's quote and the date. Judgment checks it at the press, at each ruling pass and in
every brief; anything outside it goes to the question file, and only the
owner widens the scope.

### The joint pass (`specify.joint-pass`)

| Step | Owner | Writes | Needs | Parallel with |
|---|---|---|---|---|
| 0 | session | latitude classification; spec §0–§2; plan §0, §2–§4, §1 | — | `research-scout` (plan §5) |
| 1 | `product` | spec §3 | 0 | the scouts |
| 2 | `architect` | spec §4–§8; plan §5 synthesis, §6–§9 with effort labels, phases, batch plan | 1, the scouts | — |
| 3 | `product` ∥ `tester` ∥ `security` (sensitive surface) ∥ `reliability` | spec §9, §10, §5/§7; plan §10, §11 | 2 | each other |
| 4 | `devils-advocate` | beside plan §6 and §11 | 3 | — |
| 5 | session | spec §11, §12, sign-offs; plan §12–§15 | 4 | — |

Section ownership does not change. A testability failure in step 3 is a
`recover` attempt back to the architect. When only one document is
being written, `specify.flow` and `grill.flow` apply.

## grill

*Source: `protocols/grill.md`*

- **id:** `protocol.grill`, tier 2
- **owns:** `rule.grill`, `grill.flow`, `grill.revise`,
  `grill.increment-shape`, `grill.press`, `grill.plan-approval`,
  `grill.legal-checkpoint`
- **requires:** —
- **peers:** `protocol.specify`, `protocol.specify-joint-pass`,
  `protocol.test-first`, `agent.devils-advocate`
- **load_when:** "plan the implementation, plan-of-record, grill.md"; "spec
  exists but no plan implements it"; "scope an increment, slice the work";
  "an increment shipped, revise the plan, record what happened"; "plan is
  stale, assumption broke, architecture change"
- **artifacts:** `templates/grill.template.md`,
  `templates/knowledge-graph/grill-lint.py`

### What it does

Use grill when a spec exists (or is authored in parallel) and you need
a plan-of-record before code — and again every time that plan has to
move. The deliverable is `docs/graph/plans/grill.md`, populated through
§15, with explicit decisions, options, an architecture sketch,
implementation increments mapped to spec contracts, verification gates,
risks, and a single recommended next step. Two passes over one
document: **creation** (`grill.flow`) and **revision** (`grill.revise`);
most sessions run the second.

This node owns **the grill rule** (`rule.grill`): `grill.md` is the
living plan-of-record, the source of truth for *plans*. Open it when you
start, before you change architecture, when you finish, and whenever an
assumption breaks. It is append-only: a change lands as a new changelog
entry, and a stale claim is struck through where it stands. The session
writes it; workers report what they did in their handback. Its gate is
`python3 docs/graph/grill-lint.py`.

"Grill" is a verb: pressing the assumptions until solid, the design
until coherent, the plan until each increment is one RED-GREEN-REFACTOR
cycle. Filling the sections writes the plan down; the press
(`grill.press`) is what makes it a plan.

### Entry conditions

- **Creation:** the goal is clear (or `brainstorm` converged it); a
  spec exists or is authored alongside; no current grill.md for this
  feature, or one stale by more than a major phase.
- **Revision:** grill.md exists and something moved — an increment
  shipped, a decision changed, a risk or question surfaced, plan and
  spec catalog drifted, or a session is closing.

### The creation pass (`grill.flow`)

A phase table with a named owner per phase; **the table is the spawn
order** (`delegation.sequencing`), and two phases run side by side only
where the table says so. The §15 entry lists the pass's spawns by
`spawn_id` in issue order. When the spec is written in the same pass,
the joint pass replaces this table (`specify.joint-pass`).

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | §0 | orchestrator | — | — |
| 1 | §2 §3 §4 | orchestrator | §0 | — |
| 2 | §1 | orchestrator (router-bounded reads); an investigation-class worker beyond | §2–§4 | — |
| 3 | §5 | `research-scout`, one spawn per un-wikified dependency | §1 | — |
| 4 | §6 §7 §8 | `architect` → ADRs; `legal` inside its checkpoint | §5 | — |
| 5 | §9 §10 | `architect` slices; `tester` confirms RED tests, owns §10 | §8, spec §4 | 6 |
| 6 | §11 | `security` ∥ `reliability`; `legal` for external rules | §8 | 5 |
| 7 | press | orchestrator; `devils-advocate` for one-way doors | §9, §11 | — |
| 8 | §12–§15 | orchestrator | 7 | — |

Notes the table cannot hold: §2–§4 come before §1 (conversation
products, captured before discovery colors them). §1 is read, not
recalled — every line cites a path or reads `none — <reason>`. §5 is
**derived, not judged**: its required set is every
`docs/graph/libraries/` page a §9 `Depends on:` row names, plus what a
§6 decision rests on; an empty §5 says `no external dependency —
<reason>`, a falsifiable claim the lint checks against §9. §6/§7 record
choices, discarded options, evidence, reversibility; non-obvious
decisions get an ADR, and one implicating externally-authored rules
clears the architect's `legal` checkpoint first; a recurring operation
is decided as a durable tool (§3.8). §10 records divergences from the
verification runbook only. §12 rows carry an owner, a current
assumption, and a resolution path; §13 aligns with the spec's §9; §14
is one action.

### The revision pass (`grill.revise`)

§15 entry first (increment, contracts, files, gates and outcomes,
`spawn_id`s in order); cross out completed §9 rows; a changed decision
is a new dated §6 row with the old one struck; new risks to §11,
resolved questions moved in place; §14 renamed. A revision that adds a
dependency, moves a boundary, or breaks an assumption re-enters the
creation phase that owns it (phase 3 for a dependency — the scout is
spawned in revision exactly as in creation), then presses and exits. A
red gate twice on one increment reopens the pass. Every revision ends
green under `grill-lint.py`.

### Increment shape (`grill.increment-shape`)

A good increment names: spec contracts, files touched, RED tests,
behavior added, the gate, the rollback path, `Effort:` (one label) and
`Phase:` (`RED`, `GREEN` or `prose`), both from `delegation.effort-scale`,
and `Depends on:`
— both the earlier increments it builds on and the
`docs/graph/libraries/` pages it relies on (`none` is a value; blank is
not). Rows are listed in dependency order. An increment is ready when
the tester can write the failing test from the row as written;
otherwise re-slice.

### Press the plan (`grill.press`)

Runs after §9 and §11 exist and before §14; a revision presses only
what moved.
- **Alignment:** every spec §4 contract has an increment; every
  acceptance criterion maps to a contract; no increment adds uncovered
  behavior (else back to `specify`). The lint runs the mechanical half.
- **Assumptions:** each increment names the assumption whose failure
  invalidates it, recorded as a §11 row with a verification or a §12
  row with a resolution path; no `[verify]` survives in §9 or §13;
  human-input values are do-not-guess.
- **Design latitude:** every §6 decision and §9 increment is checked
  against the plan's `Design latitude:` row (`specify.design-latitude`).
- **Refutation:** on a T3 plan, one-way doors and the top risk go to
  `devils-advocate` for one bounded pass; `refuted` reopens the owning
  phase; `could-not-refute` is recorded beside the row.

### Exit conditions

"Populated" = content or an explicit `not applicable — <reason>`.
§0–§15 populated with the §15 spawn list; every §1 line cited; §5
covers every page §9 depends on and every page named exists; every
non-obvious decision has an ADR or §6 row and every one-way door was
pressed; every §9 row fits the shape and the rows are in dependency
order; alignment holds with no `[verify]` in §9/§13; §14 is one action;
`grill-lint.py` exits 0.

The lint catches a silent §5; only the author can check that a "no
research needed" was earned. §11 names each risk's probability and
impact. §14 is the one step that unblocks the most. An increment that
touches ten files and adds three behaviors is re-sliced.

## test-first

*Source: `protocols/test-first.md`*

- **id:** `protocol.test-first`, tier 2
- **owns:** `rule.test-first`, `test-first.cycle`,
  `test-first.characterize-first`, `test-first.known-bug`
- **requires:** —
- **peers:** `protocol.verify`, `protocol.specify`, `skill.test-first`,
  `skill.holistic-editing`
- **load_when:** "about to write or change production code"; "RED GREEN
  REFACTOR, failing test first, TDD"; "bug fix, regression test"; "legacy
  code with no tests, characterization test"; "pure refactor, migration
  safety"

### What it does

Use test-first whenever you are about to write or change production
code. The deliverable is a sequence of RED → GREEN → REFACTOR → COMMIT
cycles, each tied to one or more spec contracts, with the verification
gates passing at the end.

This node owns **the test-first rule** (`rule.test-first`): no
production code without a failing test that authorizes it. The test
encodes a named spec contract and must fail for the right reason first;
GREEN adds the minimum new behavior, integrated into the file; REFACTOR
is not optional when you touched existing code; exceptions are explicit
and recorded in grill.md §9.

### Entry conditions

A spec covers the behavior, signed in its §0 (`draft` with the three
sign-offs is enough to encode; the T2 covered lane needs it `active`);
grill.md §9 names the increments in dependency order, `grill-lint.py`
green; the libraries are wikified. Missing one → back up to the
protocol that produces it. The T2 **contained lane** substitutes rather
than waives: the defect and its reproduction stand in for the contract
text, a grill.md entry line for the §9 row — and the cycle below runs
unchanged.

### Existing code with no test — characterize first

On legacy or adopted code with no spec and no test, write a
characterization test that pins what the code does *today* (bug
included), named `characterizes_…`, with any believed-wrong behavior
noted and linked to grill.md. Make your change; the characterization
test fails in exactly the intended way — that is your RED.

### The cycle (`test-first.cycle`)

One cycle per increment, in grill.md §9 order. **The table is the spawn
order**: a phase's spawn is issued only after the handback it needs has
returned; the next increment's RED waits for this increment's COMMIT
unless §9's `Depends on:` rows say they are independent
(`delegation.sequencing`). Independent REDs run ahead in a RED wave, and
the GREENs that follow them are `delegation.waves`. One spawn may carry a batch of increments
sized by their effort labels (`delegation.step-scope`,
`delegation.effort-scale`).

| Phase | Owner | Needs | Hands back |
|---|---|---|---|
| RED | `tester` | §9 row, contract text, target test paths | failing tests, right reason; §10 rows `red` |
| GREEN → REFACTOR | `implementer` | the RED handback | green, integrated diff; the implementer runs the RED tests itself, edits no test or fixture, and writes a doubtful test up as a question (`delegation.green-self-test`); affected gates run; §10 rows `green` |
| REVIEW | `reviewer` | the diff, the §9 row | severity findings; Critical/Major → `implementer` once more, an attempt under `recover` |
| COMMIT | the session | a clean review | grill.md §15 entry with the `spawn_id`s in order; the commit; the spec's status advanced |

The one merge the tiers allow: a T2 single-contract increment — or a
single reproduced defect on the contained lane — with a mechanical RED
is briefed whole to `implementer`; the REVIEW spawn stays
independent. Only the session writes grill.md; workers report what they
did in the handback (`rule.grill`).

- **RED**: identify the contracts; write tests named for them; confirm
  they fail because the *behavior* is missing (not an import or a
  name); if RED for the right reason is unreachable, the test or the
  contract is wrong. A test that passes without the code present, or a
  gate phase that would pass identically against the pre-change code,
  proves zero coverage of the change. Inherited green suites are proven by mutation
  before they are trusted. A tester's RED spawn stops once the §10 rows
  read `red` and hands back. Any implementation, even a throwaway one
  that proves the test can pass, is the implementer's GREEN
  (`tester.spawn-scope`).
- **GREEN**: the minimum new behavior — minimum in behavior, not diff
  size — integrated into the file's design; the surrounding tests stay
  green.
- **REFACTOR**: remove the duplication the change introduced, delete the
  branch it made dead, fix the names; mandatory when existing code was
  touched; the suite stays green throughout.
- **COMMIT**: review first (a Critical or Major returns to
  `implementer`; a third red on the increment reopens `grill`); run the
  increment's named gate; the session appends §15 with the cycle's
  `spawn_id`s; spec §10 carries the actual tests and **the spec's status
  advances in the same change** — first RED promotes `draft` → `active`,
  last green marks `implemented`; idioms and tools go to the close-out
  via the handbacks; then the commit
  (`feat(<scope>): <slug> — implements SPEC-NNNN`).

### Variants

Bug fixes (a bug is a spec the code failed to honor: regression test
RED → fix → the test stays in the suite after the fix, and consolidation
may merge it only into a named survivor that still fails if the bug
returns; a missing contract goes back to `specify`). A bug a test
uncovered (`test-first.known-bug`) is marked for a fix, recorded in
grill.md §12 and named to the owner in the delivery. The test that
uncovered it stays exactly as written and is the bug's only test: no
marker that expects its failure, and no second test that asserts the
buggy behavior. The session dispatches `implementer` to fix it and
re-runs that same test; until then the red is declared in the delivery
as WIP with its failure record. Pure refactors (existing tests green before and after; a
break means a behavior change or a test of implementation). Migration
safety gate (an unguarded schema is a blocking finding first). Recorded
exceptions (throwaway prototypes, pure configuration, type-only changes,
generated code) — each in grill.md §9 with a rationale and a date.

### Exit conditions

Every contract for the increment has a passing test named for it; its
targeted tests and the cross-cutting gates its files hit pass, and the
full suite runs once at the batch tip (`delegation.tip-cadence`); the
increment's gate ran and the full `verify` pass ran
before close-out; the review is clean; grill.md §15 carries the
increment with its `spawn_id`s, spec §10 carries the tests, the spec's
status is `active` (or `implemented`); `spec-lint.py` and
`grill-lint.py` exit 0.

## verify

*Source: `protocols/verify.md`*

- **id:** `protocol.verify`, tier 2
- **owns:** `rule.verify`, `verify.gate-states`, `verify.risk-depth`,
  `verify.null-result`, `verify.composition`, `verify.silent-substitutes`,
  `verify.test-first`, `verify.gate-classes`
- **requires:** —
- **peers:** `protocol.test-first`, `protocol.recover`, `protocol.canonize`,
  `protocol.deliver`, `skill.validate-knowledge`,
  `protocol.verify-new-gates`, `protocol.verify-disagreement`
- **load_when:** "increment done, ready to merge or deploy"; "which gates to
  run, verification runbook"; "tests pass but is it verified, green lie";
  "gate found nothing, zero results, is that a real finding"; "record a
  missing or skipped gate"; "assert the count or the composition, expected
  value derived from the subject"; "silent no-op, empty output that looks
  like success"; "gate never went red, does the green mean anything";
  "scanner configuration or suppression file passed, was the
  input applied"; "grep count inflated by comments and prose that quote the
  identifier"; "chronic red gate, always red for an unrelated cause"; "tests
  whose subject is outside the shipped perimeter, excluded or skipped"

### What it does

Use verify at the end of every increment and before any merge or
deploy. The deliverable is a list of gates run, their commands, and
their outcomes, recorded in `docs/graph/runbooks/verification.md`.

This node owns **the verify rule** (`rule.verify`): gates pass, and
mean something, before merge. No work is "done" until the gates
proportional to its blast radius have run, with commands and results
recorded. A gate not yet available is recorded **absent** with a date,
never silently dropped and never faked green. A gate that runs but
asserts nothing is a **green lie**, worse than a missing gate, because
it is trusted.

Actor: `tester` runs the gates (`reliability` for operational and
deploy gates) in its own context and reports outcomes in its handback;
the runbook entry is part of that worker's write scope. The session
writes the grill.md §15 record (step 8; `rule.grill`). When each gate runs is
`delegation.tip-cadence` and `delegation.mutation-at-end`.

### The gate menu

Select the gates that apply, at the lowest level that catches the bug
you care about; whether a check exists at all is
`test-first.proportionate-checks`. The full table:

Formatter (style drift); Linter (common bugs/anti-patterns); Type
checker (contract violations across boundaries); Unit tests
(pure-logic regressions); Integration tests (adapter/boundary);
Contract tests (API/structured-output); End-to-end tests
(critical-flow); Behavior-preservation (refactor/migration changed
observable behavior beyond an enumerated intended-delta list); Build
(artifact health); Security scan (vulnerable deps, secret leaks, static
rules); Smoke test (deployed system minimally alive); Evaluation suite
(LLM/VLM behavior); Performance test (latency/throughput/memory); Graph
lint (duplicate facts, broken edges, leaked pins); Spec-coverage lint
(live spec contracts with no test; `python3 docs/graph/spec-lint.py`);
Status register (a lifecycle status missing its required companion;
`python3 docs/graph/status-register.py`); Plan-of-record lint (grill.md out
of shape — dependency order, §5 derived from §9, plan↔spec alignment;
`python3 docs/graph/grill-lint.py`); Manual review (non-automatable
judgment).

**Gate classes** (`verify.gate-classes`, from ADR-0003). A gate table with a
`Class` column holds one of four words per row: `hard` (the harness refuses,
so the wrong act is impossible), `soft` (a contract or a tool refuses),
`detective` (asserted after the run from named evidence a person reads and
acts on) and `judgment` (a named agent or person decides, and no tool can).
A linter someone may decline to run is `soft`.

### Risk-proportional gate depth (`verify.risk-depth`)

Verification depth follows blast radius, not habit. Start from the
change class, not the gate list:

| Change class | Minimum gate depth |
|--------------|--------------------|
| T1 trivial edit (no behavior/contract surface) | the one focused check that covers it (formatter/linter/build) |
| Local logic change, contracts unchanged, path known | cheap static gates + focused unit/integration on that path |
| Shared contract, public interface, or persisted format changed | full battery on the affected boundary: contract tests, integration, neighboring regression suites |
| Central abstraction, dependency direction, concurrency, auth/security, data migration | broad system gates: full suite, security scan, e2e on critical flows, manual review |
| Affected scope genuinely uncertain | treat as the row above; uncertainty buys breadth, never a discount |

The blast radius picks the row, not the tier: a T2 contained-lane change
bought a cheaper authorization, not a cheaper gate. Escalate one row the
moment a "local" change turns out to touch a shared surface. On a provably
local change, run the battery its row names and no broader, because
wall-clock and attention are budget too. When the gate a row names does not
fit the time, merge a smaller increment and keep the gate.

### Workflow

1. Pick the applicable gates from the risk table and the gate menu.
   Order by risk: gate the assumption most capable of invalidating the
   increment first. Prefer one high-information gate over overlapping
   ones. Verification stops when the mandatory gates pass and the
   remaining uncertainty cannot materially change the result, not when
   every possible gate has run.
2. Run them cheapest first (formatter, linter, type check); proceed
   to slower gates only if cheap ones pass.
3. Record outcomes in `docs/graph/runbooks/verification.md` under
   the increment heading, with the command and result per gate.

### The three gate states (`verify.gate-states`)

Report every gate as exactly one of three states, so silence never
reads as a pass:

- executed: actually run this pass, with command and result, and only if
  its prerequisites held and its assertions ran. If it fails, fix the
  increment or hand it back.
- discovered: known to exist (read in source/config) but not run
  this pass. Record it "DISCOVERED, not run (date) — reason" so it can
  never be mistaken for an executed pass.
- absent: does not exist yet. Record it with a date, a reason, and
  the owner who will add it.

Adopting a codebase with no gate infrastructure still fills the runbook:
record each gate its blast radius calls for as
`absent (YYYY-MM-DD) — <reason>`, because a blank verification runbook is
indistinguishable from one nobody checked.

**The green-lie clause.** The three states are honest only if an
executed PASS means something. A test command with no tests, a linter
over an empty set, a type check with everything untyped: these "pass"
and mean nothing. A pass counts as evidence only when its check asserted
something, and only such a check becomes a gate. Land the real check
first; the gate follows in a later increment. A gate is trusted once a
planted violation has turned it red and its removal has turned it green
again. A gate that executes and
asserts can still lie by not discriminating: a recorded verdict uses
only the words the check proved. An invocation-*count* assertion on a
mock passes vacuously the moment the code stops calling that
collaborator for a wrong reason; assert on the actual destination,
content, or argument instead.

### Knowledge layer, LLM features, grill.md

6. For the knowledge layer, run the graph lint
   (`python3 docs/graph/graph-lint.py`) and, after a large docs change
   or an adoption, validate the graph with
   `docs/graph/skills/validate-knowledge.md`.
7. For LLM/VLM features, also record latency and (when relevant) token
   cost as metrics.
8. Update grill.md §15 with the date and verification outcome.

A gate that is genuinely flaky is fixed, or documented as such in the
runbook, and stays enabled. A test that passes on a dev machine proves that
machine; the automated run's environment is verified on its own. A confirmed
bug awaiting its fix is declared WIP under `test-first.known-bug`, not
counted as a chronic red.

## verify-new-gates

- **id:** `protocol.verify-new-gates`, tier 2, from `protocols/verify-new-gates.md`
- **owns:** `verify.status-evidence`, `verify.tool-faults`
- **requires:** none
- **peers:** `protocol.verify`, `protocol.verify-disagreement`
- **load_when:** "mark it closed, what counts as status evidence"; "gate
  script left half-applied state, environment failure or repository
  failure"; "adding a new gate or check"
- **command:** none; it is entered from `verify`

### `closed` means evidenced

`closed` means resolved with evidence: `status_evidence` names a
path#anchor, a commit or a gate-run id a reader can open. Without it the
honest states are `hotfix` and `deferred`, each with an owner. A spec is
promoted to a live status only in the change that adds passing
assertions for its contracts. The vocabulary lives in
`docs/graph/_schema.md`; `status-register.py` enforces it.

### Adding a new gate

If verification reveals a bug no existing gate would have caught: pick
the lowest level that catches it; get a RED test case that reproduces
it; add it to the verification runbook in the same increment; add it to
CI in the next reliability-owned increment.

A gate script you author is all-or-nothing, runs under strict error
handling, resolves its own root, and keeps environment failures distinct
from repository failures in remedy text and exit status.

## verify-disagreement

- **id:** `protocol.verify-disagreement`, tier 2, from `protocols/verify-disagreement.md`
- **owns:** `verify.characterize`, `verify.measure-integrity`
- **requires:** none
- **peers:** `protocol.verify`, `protocol.verify-new-gates`
- **load_when:** "refactor or migration must preserve behavior"; "golden
  master, stored oracle before a migration"; "the checker disagrees with
  the file, fix the tool or the declaration"; "tolerate a known defect,
  a known bug stays red until its fix lands"; "a gate fails and the code
  looks right, which one is wrong"
- **command:** none; it is entered from `verify`

### Behavior-preserving changes (refactors, migrations, dependency bumps)

The gate is **unchanged behavior**, a stronger claim than "it builds and
the tests pass". Two disciplines:
- Characterize first, then change. Capture a baseline oracle of
  current observable behavior (endpoint responses, persisted shapes,
  message payloads, computed outputs), normalized to mask only volatile
  leaves. This is the RED spine: it must pass on the *pre-change* code.
- Diff against the baseline; allow only an enumerated intended-delta
  list. The gate passes only if everything matches the baseline
  except an explicit list of intended deltas, each row naming the
  change and why it is a deliberate strengthening. Byte-identical output
  is the wrong contract; observable-behavior preservation is. An
  unexplained diff, or an additive-only edit to the pinning tests, is a
  red flag to justify, never a silent re-baseline.

### Tolerating a known defect

A suite that meets a confirmed bug keeps its gate as it is. The test that
uncovered the bug stays unchanged as the bug's acceptance check, and the
bug follows `test-first.known-bug` in `protocol.test-first`: marked for a
fix, the owner told, `implementer` dispatched, the same test re-run. The
declared red advertises the hole until the fix lands; a relaxed, skipped
or re-pointed gate would hide it.

### When the check and its subject disagree

A gate measures the effective state, read back through the path a real
client takes. When the check and its subject disagree, the instrument is
the first suspect: read the raw source, read the probe's exit code
rather than the emptiness of its output, and prefer the format's own
resolver to a parser you write. Satisfy a check by fixing its subject or
its instrument, never by changing what it measures. A real defect keeps
its test as written and goes to a decision owner under the known-bug rule
above. A second measurement confirms the first only if it
re-derives the result by a different method.

---

## recover

*Source: `protocols/recover.md`*

- **id:** `protocol.recover`, tier 2
- **owns:** `recover.failure-classes`, `recover.three-attempt-boundary`
- **requires:** —
- **peers:** `protocol.deliver`, `protocol.grill`
- **load_when:** "a worker or gate failed, what now"; "retry or re-route,
  flaky failure"; "delegation came back wrong or ambiguous"; "gate red twice
  on the same increment"; "permission guard refused an action the owner
  directed"; "failure cause unknown, cheapest probe first"

### What it does

Recover is the failure discipline. Failure is a normal output of real
work; the waste comes from *unclassified* reaction to it: hammering an
identical retry at a deterministic error, widening context because a
brief was ambiguous, quietly swallowing a red gate. Recover makes the
response as disciplined as the work: **classify first, then take the
single move the class allows, bounded, with the partial work
preserved.**

### Diagnosis precedes classification

Diagnosis is only as good as its evidence: before trusting any
cross-process timing comparison, prove the two clocks are aligned via a
log line carrying both processes' own timestamps, then anchor
conclusions to absolute timestamps rather than relative or elapsed
ones.

### The failure classes (`recover.failure-classes`)

| Class | Recognize it by | The one allowed move |
|-------|-----------------|----------------------|
| **Transient** | Environment flake: network, rate limit, race, resource exhaustion | Retry as-is, **max 2**, backing off. Third failure is not transient — reclassify. |
| **Deterministic** | Same input reliably produces the same failure: compile error, failing assertion, lint, schema rejection | **Change the input** (code, test, config), then re-run. A second failed theory is the signal to read the upstream documentation (the library page, or `protocol.ingest-library`) before a third. |
| **Capability** | The worker is the wrong instrument: wrong specialist, missing expertise, out-of-domain handback, LOW/NONE route band in hindsight | Re-route: run `agent-lint --route` with a *sharper* task statement, written in the domain's own words so it also composes the expertise the worker lacked. A knowledge gap closes as an `expertise.*` node; commission an agent only when the work needs its own tools, model class, stance, or isolation (kernel §1). |
| **Ambiguity** | The worker asked the brief a question, guessed, or two artifacts contradict (spec vs code, plan vs node) | Fix the **cheapest upstream artifact that owns the confusion** — brief first, then plan (grill §), then spec — and re-delegate. Widening context is not the fix. Inside a batch, the question goes to the batch's question file and the architect's ruling pass answers it (`delegation.question-file`). |
| **Systemic** | The harness or system itself: wedged delegation, depth cap hit, missing tool, broken gate infrastructure; also a permission guard that refuses an action the owner directed | Stop the line. Record in grill.md §12 and report to the human with the exact evidence, visible rather than worked around. |
| **Unregistered** | The specialist exists on disk but the host has no such type: the session predates the projection, or it is rooted at the seed rather than the plant. Reads like Systemic, but is not. | Apply `delegation.harness-registration`: preflight, re-enter rooted at the plant, or role-emulate **and record it**. Keep the line running and use the existing definition, because a second definition would be a second home for the same charter. |

After a permission refusal, a retry or a re-route first shows that
something the guard reads has changed. The owner gets the exact step in a
form that survives a paste (one short command, any credential read from
the environment, no secret printed).

An intermittent or probabilistic failure is confirmed **fixed** only on
mechanism-level evidence (a trace proving the causal path is genuinely
absent), never on a lower observed failure rate. Any incidental change
that reduces *exposure* to the defect buys a better rate while fixing
nothing. Corollary: sequence any exposure-reducing change **after** the
diagnostic evidence is captured, never before.

### The three-attempt boundary (`recover.three-attempt-boundary`)

Across all strategies combined, a unit of work gets **three attempts**.
The fourth move is always escalation: record the failure-class history
in grill.md §12, mark the increment WIP in the delivery, and hand the
decision to the human with the evidence, because a fallback chain spends
growing resources on a falling probability of success. An attempt that
ends without advancing its deliverable counts as a failed attempt.

### Gate-failure rule

A gate that fails **twice on the same increment** means the increment
is wrong-sized or the plan is wrong. Reopen `grill`, split or rescope the
increment, and come back through `test-first`. A third run of the same red
gate is a deterministic retry.

### Preserve the partial work

A failed attempt still produced evidence: the RED test that stands, the
node authored, the exact error, the classification itself. The worker's
handback carries it (`status: failed`, `failure_class`,
`in_domain_work_done`) so the next attempt starts from the frontier,
not from zero.

### Visibility doctrine

- A failure that changed the plan is recorded in grill.md §12 with its
  class, including recoveries that *worked* (a transient retry that
  succeeded is telemetry; two of them are a reliability signal).
- The delivery's session metrics count retries by class; `harvest`
  mines them for systemic seed lessons.
- Every downgrade (a weaker gate, a smaller scope, a different
  specialist) *is a plan change* and lands in grill.md before the next
  attempt.

---

## canonize

*Source: `protocols/canonize.md`*

- **id:** `protocol.canonize`, tier 2
- **owns:** `rule.canonize`, `canonize.close-out-flow`,
  `canonize.status-review`, `canonize.deviation-capture`,
  `canonize.why-record`, `canonize.session-record`
- **requires:** `skill.toolcraft`
- **peers:** `agent.tool-smith`, `protocol.deliver`, `protocol.harvest`,
  `skill.adr-writer`
- **load_when:** "task is finishing, close out, before deliver"; "persist
  what we learned into the graph"; "spawn the docs-librarian, canonize";
  "catalog a tool or skill the work produced"; "status review at close-out:
  did each register item move this session"; "we departed from the standard,
  record the deviation and why"; "small fix with no spec, where does the why
  get written down"; "handback overflow notes, read them at close-out";
  "file the session record, which harness memory entries can be retired"

### What it does

Canonize is the single end-of-task close-out spawn. This node owns
**the canonize rule** (`rule.canonize`): knowledge of interest is
captured before a task is done. Work generates knowledge and
capabilities; if either lives only in the session transcript, it dies
with the session and the next agent rediscovers or rewrites it the hard
way. Every T2/T3 task ends with **one** docs-librarian spawn, the
close-out, that persists into `docs/graph/` the facts, sharp edges,
corrected assumptions, provenance, and missed `load_when:` triggers the
work surfaced, and catalogs its durable tools (the toolcraft rule) in
the same pass. Two doctrines, one execution: a second spawn with the
same bootstrap and lint run would be pure coordination waste. On a T2
**contained-lane** task the same spawn also writes the why-record the
lane owes — one short ADR when a real choice was made, otherwise one
`changelog.md` line carrying defect → cause → fix → pinning test
(`canonize.why-record`). A contained change delivered without it is a
behavior change nobody can trace to a reason.

Only the librarian writes the graph's **fact-bearing surfaces** (nodes,
wiki pages, the tool catalog), and it keeps one home per fact; the session
writes none of them. The session writes its own operational artifacts under
the same root directly:
grill.md (`rule.grill`), changelog.md, and the session records in
`plans/sessions/`, where the librarian's one write is the status lines it
appends. The verification runbook belongs to the tester worker that ran
the gates.

### When to invoke

- At the completion of every Tier 2/3 task or increment, before
  `deliver`.
- Whenever the work surfaced a fact the graph does not own,
  contradicted one it does, or produced a tool a future session will
  run again.
- Tier 0/1 shortcut: a question answered or a trivial
  non-behavioral edit needs no spawn. The session writes one line in
  the delivery, "canonize: nothing of interest / no tool, because …",
  however minor the task, and that line satisfies the fail-closed
  doctrine. A T0/T1 task that surfaced something durable escalates:
  spawn the librarian.

### What the one brief carries

Knowledge candidates (§3.7): a new or changed fact about the
project's structure or capability; a sharp edge that bit (and the tell
to spot it next time); a corrected assumption; provenance for a claim;
a `load_when:` trigger that should have matched and didn't; a new
library idiom or pitfall.

Tool candidates (§3.8, toolcraft owns the doctrine): any durable
tool the work produced (recurs across sessions, stable interface,
test-authorized, lives in the repo). Named in `tools_built` on
handbacks.

Skill candidates (§3.8): any repeatable multi-step procedure a
future session will walk again, named in `skills_built`, or the same
sequence appearing a third time. The brief forwards candidates; the
librarian authors them.

Kept out of every candidate list: ephemeral scratch, secrets/credentials,
production or personal data, speculation (write "not recorded"),
project-specific material aimed at the seed (that is `harvest`'s
agnosticism gate), throwaway prototypes or genuine one-offs.

### The flow — one spawn (`canonize.close-out-flow`)

1. Assemble candidates from the finished work and the workers'
   handback payloads: facts with evidence, tools with path + entry
   point + invocation + covering test.
2. Spawn the docs-librarian once (authoring-class; it owns
   `docs/graph/`) with a brief embedding the canonical block from
   `docs/graph/templates/prompts/graph-session-bootstrap.md` plus the
   candidate lists. This spawn is fail-closed: if the host has no such
   type, apply `delegation.harness-registration` (re-enter rooted at the
   plant, or role-emulate and record it), and the close-out runs either
   way.
3. The librarian persists and catalogs in one pass. Each fact lands
   in exactly one node's `owns:` (dedupe: update, don't duplicate);
   each tool gets `tool-page.template.md` filled into
   `docs/graph/tools/<name>.md` plus an index row and an `artifacts:`
   edge (checking `tool-corpus/` first where the corpus is available);
   each recurring procedure gets `skill.template.md` filled into its home
   node `docs/graph/skills/<name>.md` plus the projection in each harness
   dir the plant uses (checking `skill-corpus/` first where available,
   deduping, composing existing disciplines by reference); failed
   `load_when:` triggers are sharpened. The status register is walked
   item by item, and each deviation lands as an ADR entry plus a
   `deviation.` node. One `graph-lint` run confirms the graph stays
   clean.
   With the graph reconciled, the librarian runs `python3
   docs/graph/code-anchor.py --record` once. It writes
   `.cypress/anchor.json` (the branch, the commit and the uncommitted
   code paths of each repository the plant governs), and the line it
   prints goes into the newest session record's "Canonize status". The
   next session compares against the anchor once, at its start; nothing
   runs the tool per prompt or per tool call.
4. Confirm or record-empty. The librarian hands back nodes/fact-keys
   touched and tool cards written, or an explicit "nothing of interest,
   because …" / "no durable tool, because …", with the code-anchor line
   (or its refusal) and the lint result.

### Fail-closed doctrine

A task is **not complete** until its knowledge is canonized, any durable
tool cataloged, and any recurring procedure crystallized into a project
skill, or each explicitly recorded empty with a reason. An uncaptured
fact is a silent knowledge leak; an uncaptured tool or procedure is a
silent capability leak, the same failure class as a green lie (§3.5).
`deliver` (§3.6) does not sign off until this close-out has run (or the
T0/T1 self-record line is present).

### Relationship to the other protocols

- `deliver` produces the human-facing cold-pickup **summary**; canonize
  persists the machine-facing **graph knowledge and tool catalog**.
- `toolcraft` owns the *doctrine* of what counts as a durable tool;
  canonize owns the *execution*; there is no separate toolcraft spawn.
- `harvest` folds **project-agnostic** lessons and tools into the seed,
  only when the user starts it; canonize keeps **project-specific** knowledge in
  the plant. What harvest's agnosticism gate rejects still belongs here.

---

## deliver

*Source: `protocols/deliver.md`*

- **id:** `protocol.deliver`, tier 2
- **owns:** `rule.deliver`, `deliver.forms`,
  `deliver.attribution-assertion`, `deliver.numbered-decisions`
- **requires:** —
- **peers:** `protocol.canonize`, `protocol.recover`
- **load_when:** "session is ending, wrap up, hand off"; "delivery summary,
  cold pickup"; "what did we change, session report"; "attribution,
  produced_by, routing evidence"; "decisions for the owner, options to
  approve, answer by number"; "every remaining step is the owner's, goal
  loop or stop hook keeps firing"; "session metrics after each increment,
  cost and quality so far"

### What it does

Every session ends with delivery. The deliverable is a concise summary
that lets another agent (or the same agent next time) pick the project
up cold. This node owns **the deliver rule** (`rule.deliver`): every
session ends with a delivery, compact for T0/T1, full for T2/T3: files
changed, routing attribution, docs updated, decisions, gates with
outcomes, limitations, and **one** recommended next step. The
deliver-time attribution assertion is **detective** (ADR-0003): a unit of
work with no `produced_by` is a BLOCK, and the session running the
assertion is what calls it. A session without a delivery summary is
paused, not finished, so every session runs this protocol.

### When to invoke

- At the end of every work session.
- Before the user closes the chat or moves to another task.
- Before handing off to a different specialist for a different phase.

### The two forms (`deliver.forms`)

**Compact form (Tier 0/1 only).** A question answered or a trivial
non-behavioral edit does not earn the full ceremony. Deliver in the
chat, in five lines or fewer: what changed (paths, or "nothing —
question answered with citations"); gates (the one focused check, or
"n/a (read-only)"); canonize ("nothing of interest / no tool, because
…", or "escalated to close-out"); next (one step, or "none"). A T1 edit
that turns out to touch behavior, a contract, or spec-covered code is
not T1; reclassify and take the full path. The compact form appends to
grill.md §15 only when it changed a file.

**Full form (Tier 2/3).** Runs after the `canonize` close-out spawn has
confirmed (or record-emptied) knowledge and tools. State the summary in
the chat AND append the same content to `docs/graph/changelog.md` and to
grill.md §15. The full form has sections: Files changed; Routing
attribution (per unit of work: `produced_by` + route band/line);
Documentation created or updated; Key decisions; Gates run (each as
executed, discovered or absent; a failing gate is fixed, or its increment
goes out marked WIP under Known limitations with the failure record
`recover` requires); Known limitations; Session metrics; Recommended next
step.

The **Session metrics** block is telemetry, not prose: Tier (with any
reclassification), Spawns, Route bands + overrides, Retries by class (per
`recover`), Gates run/failed-then-fixed, full-suite runs, serial waits,
overflow notes, and a Quality line. This is what lets the system improve on evidence instead of anecdote: `harvest`
aggregates these across deliveries to find *systemic* seed problems:
recurring misroutes mean a specialist's `routing_triggers` need
sharpening, frequent tier reclassifications mean the tier edges need
tuning, repeated transient retries in one area is a reliability signal.

### Quality bar

A delivery that passes names every changed file; names every
documentation update with its location, grill.md among them; cites
verification outcomes by gate; lists every limitation explicitly and
marks a half-finished increment WIP, with resuming it as the next step;
recommends exactly one next step; numbers every decision left to the
owner; covers every library the work used with its wiki page; reads as
the writer, in that the full-form summary and any
pull-request description or commit message pass the `humanizer` skill in
embedded mode with no strong tell from `docs/graph/prose-lint.py`; and is
the smallest summary that permits correct use and appropriate trust
(material caveats in, process narration out), because future context is
a cost this summary imposes on every later turn.

### Routing-attribution assertion (detective) (`deliver.attribution-assertion`)

Before sign-off, attribute every unit of work to the specialist that
produced it, reading `produced_by` and `route_evidence` from the
handback payloads. Then:

- Missing `produced_by` on any unit of work → BLOCK.
- Out-of-domain authoring → FLAG: a `produced_by` specialist whose
  `routing_triggers` do not cover the work it authored.
- Unexplained generic-role override → FLAG: a HIGH band for
  specialist X but the work was produced by a generic role or a
  different specialist with no recorded rationale.
- Role emulation → FLAG unless declared: a worker running as a
  generic type wearing a specialist's role must carry
  `harness_override: role-emulated (<reason>)` in its handback. Report
  the count in the delivery.

This assertion runs in the top session at `deliver`, where the whole
delivery is in view; no hook the seed installs reads a worker's result
(`delegation.briefs`). A top-session Stop hook that greps the delivery for
attributions stays deliberately unwired until this plant's real deliveries
carry `produced_by` (a
gate landed before the thing it checks either checks nothing or blocks
everything; kernel §3.5, the green-lie rule). Once deliveries carry the
field, wire it warn-first, then block.

### The cold-pickup test

The standard for "is this delivery complete?": another senior engineer,
with no context except the repository and the delivery summary, should
be able to (1) run the project locally, (2) run the verification gates,
(3) find the current plan-of-record, (4) know the next step. If they
can't, the delivery isn't done.

---

## ingest-library

*Source: `protocols/ingest-library.md`*

- **id:** `protocol.ingest-library`, tier 2
- **owns:** `ingest-library.flow`, `ingest-library.refresh`,
  `ingest-library.corpus-first`
- **requires:** —
- **peers:** `protocol.harvest`, `skill.library-wiki`,
  `skill.research-and-ingest`
- **load_when:** "adding a new dependency, library, SDK, or API"; "no wiki
  page for a library the code uses"; "version pin changed, refresh the
  library page"; "security advisory on a dependency"
- **artifacts:** `templates/library-page.template.md`,
  `templates/knowledge-graph/graph-lint.py`

### What it does

The core wiki-building flow: a complete, version-pinned page in
`docs/graph/libraries/<name>.md`, registered in `libraries/index.md`,
with raw and normalized sources on disk — built before any code touches
the dependency, because agent memory of library APIs is unreliable
across versions.

### Entry conditions

`architect` or `implementer` wants a dependency with no page; a pin no
longer matches what the project uses; a behavior the page does not cover
cost an agent debugging time; an advisory affects a wikified library.

### The pass (`ingest-library.flow`)

A phase table with a named owner per phase; **the table is the spawn
order**. Two callers hold it — the orchestrator inside grill phase 3
(one scout per dependency without a page) and the `docs-librarian`
during a close-out or docs audit — and in both the scout drafts and the
librarian finalizes (`delegation.model-classes`).

| Phase | Does | Owner | Needs |
|---|---|---|---|
| 0 | identify: name, exact version, ecosystem, why | the caller | lockfile / brief |
| 1 | corpus check | the caller | 0 |
| 2 | retrieve, snapshot, normalize, register sources; inspect code; **draft** §0–§3, §10 | `research-scout` | 0–1 (parallel across dependencies) |
| 3 | smoke test at the pin | `tester` | 2 |
| 4 | grill.md §5 (and §6) | the session | 3 |
| 5 | finalize page, index rows, graph-lint | `docs-librarian`, in the close-out | 2–3 |

Notes: phase 2 fetches release notes, quickstart, API reference,
security policy and advisories, license (and for LLM/VLM SDKs pricing,
rate limits, structured output, safety); advisories land in §7 and
`security` weighs them at grill §11 — no separate spawn. The draft is
brutally specific: §0–§3 and §10 on creation, §4–§12 demand-grown, never
a fabricated "none". A failed smoke test returns the page to phase 2 as
an attempt under `recover`'s three-attempt boundary. The librarian's
finalization dedupes, writes the index rows, and runs `graph-lint.py`,
whose library check reads the §0 pin and the index row.

### Corpus first (`ingest-library.corpus-first`)

In the seed repo or a plant that harvested the library corpus, check
`library-corpus/<ecosystem>/<library>.md` (keyed by library, not
version) before re-downloading: seed the page from it, then pin and
validate the version-specific layer against the lockfile from upstream.
Reuse the corpus, re-download only the delta.

### Refresh (`ingest-library.refresh`)

The same pass over an existing page — pin drift, a major release, an
advisory, or a stale "Last reviewed": phase 2 diffs the upstream
CHANGELOG into §8 and updates §0/§3/§4/§6/§7, phase 3 re-runs the smoke
test, phase 5 updates the index row. The cheap drift check between full
passes is `research-and-ingest`'s; it decides whether a refresh is due.

### Exit conditions

The page exists with its §0 pin table filled (an exact version), `Last
reviewed` dated, §10 citing sources, §1–§3 populated; sources on disk
with their index rows; a smoke test by `tester` recorded in its
handback; grill.md §5 names the page; `libraries/index.md` has the row
(written in the close-out) and `graph-lint.py` exits 0.

### Scope

Wikify what the code imports directly; trivial transitive dependencies
stay implicit. A platform feature of the runtime itself is covered in
`best-practices/engineering.md`.

## from-scratch

*Source: `protocols/from-scratch.md`*

- **id:** `protocol.from-scratch`, tier 2
- **owns:** `from-scratch.phases`, `from-scratch.entry`
- **requires:** —
- **peers:** `protocol.brainstorm`, `protocol.grill`,
  `protocol.ingest-library`, `protocol.canonize`, `protocol.initialize`
- **load_when:** "start a new project, empty repo"; "greenfield, bootstrap
  from nothing"; "no grill.md exists yet, day one setup"; "project skeleton,
  verification baseline"; "new project from the seed, nothing to scout";
  "installed the seed into an empty repo, now what"; "mkdir a new project and
  cd into it"

### What it does

Turns a goal into a project another agent can pick up cold, through
nine phases that each adopt a sub-protocol carrying its own owners and
failure modes. Read the phase's own protocol, because a summary drops the
failure modes it carries. **The table is the spawn order.**

| Phase | Does | Adopts | Owner |
|---|---|---|---|
| 1 | Brainstorm | `brainstorm` | orchestrator with the user |
| 2 | Project skeleton | `install.sh`; `knowledge-graph` | `seed-installer`; orchestrator (root node, README) |
| 3 | grill.md, creation pass phases 0–2 | `grill.flow` | orchestrator |
| 4 | Research and ingest | `grill.flow` phase 3 → `ingest-library.flow` | `research-scout` per dependency; `tester` smoke-tests |
| 5 | ADR-0001 | `grill.flow` phase 4; `adr-writer` | `architect` |
| 6 | Verification baseline | `verify` | `reliability` (runbooks, gate entry point); `tester` (framework, hello-world test) |
| 7 | Specify slice 1 | `specify.flow` | per its table |
| 8 | Test-first slice 1 | `grill.flow` 5–8, then `test-first.cycle` | per those tables |
| 9 | Close-out and deliver | `canonize` → `deliver` | `docs-librarian` once, then the session |

Greenfield notes: phase 3 fills §1 with `none — greenfield` on every
line (what `grill-lint.py` accepts in place of a path), §7 with the
shaped options, §11/§12 from the brainstorm; phase 4 is where shaped
options die on real research; phase 6 is done only when the gate passes
on a clean checkout; phase 9 is the one librarian spawn that finalizes
every page the scouts drafted and writes the index rows.

### Exit conditions

grill.md current; ADR-0001 recorded; every chosen dependency has a page
and an index row, `graph-lint.py` and `grill-lint.py` green; both
runbooks exist and their commands run; SPEC-0001 `implemented`; the
slice's tests and the suite green; the README explains the project; the
close-out ran.

### Entry — which route reached this protocol (`from-scratch.entry`)

`protocols/from-scratch.md` §"Entry". Three routes arrive here and the protocol
behaves the same for all three: the installer's own fork, `/initialize` on a
repository with no executable project evidence to scout, and a bare `mkdir` plus
a paste of `INSTALL_PROMPT.md`. The test that selects this arm rather than
`grow` is the **absence of executable project evidence** — not the absence of
files, and not the absence of a `docs/graph/`. A bootstrap states what it does
not yet know rather than inventing it.

### The honesty this day needs

`protocols/from-scratch.md` §"The honesty this day needs" judges each phase by
its exit condition, not by its files: bootstrapping is T3 even when the goal
sounds clear; the skeleton phase is done when the host tool *loads* the
machinery; the stack is chosen from verified, wikified research; the
verification baseline passes on a clean checkout before any feature code; the
specify phase only authors the spec; and ADR-0001 and SPEC-0001 are written.

## grow

*Source: `protocols/grow.md`*

- **id:** `protocol.grow`, tier 2 (note: no `command: true`)
- **owns:** `grow.worker-topology`, `grow.write-boundaries`,
  `grow.knowledge-shape`, `grow.growth-flow`, `grow.completeness-contract`,
  `grow.gate-table`, `grow.stack-inventory`, `grow.node-authoring`,
  `grow.librarian-pass`, `grow.plant-facts`, `grow.legal-corpus`
- **requires:** `method.delegation`
- **peers:** `protocol.harvest`, `protocol.graft`, `protocol.initialize`,
  `protocol.ingest-library`, `protocol.canonize`, `protocol.deliver`,
  `protocol.recover`, `protocol.from-scratch`, `method.engineering-posture`,
  `method.design-posture`
- **load_when:** "grow the knowledge graph, first growth"; "install prompt,
  EXPERT_SEED_INSTALL_PROMPT"; "docs/graph is missing or badly drifted";
  "regrow or refresh the graph after major drift"; "declare the plant block:
  environment class, commit attribution, languages"; "is this plant fully
  grown, coverage record, growth audit"; "does this plant carry the legal
  corpus, which jurisdiction, compliance scope"; "author the project nodes
  and expertise nodes, configure graph-lint kinds"; "which gates must pass
  before a growth can be called done"; "the growth audit reported UNGROWN,
  HOLLOW, UNSTAFFED, STALE — what now"

### What it does

Grow is the canonical full-growth workflow: it turns an installed
project-agnostic seed into a complete, source-grounded `docs/graph`
knowledge system. It is invoked by `INSTALL_PROMPT.md` (installed as
`EXPERT_SEED_INSTALL_PROMPT.md`); `docs/graph/protocols/initialize.md`
is a coding-tool adapter to the entry fork, not to this file: the fork
selects grow when the target has source to scout, and from-scratch
when the repository is empty.

The caller is an orchestration chat. It owns user communication,
planning, worker selection, briefing, sequencing, and acceptance, and it
only orchestrates: scouts investigate and authors write.

### Mandatory worker topology (`grow.worker-topology`)

1. Spawn clean-context **investigation-class** scouts for read-only
   source discovery, partitioned by real subsystem, repository, or
   evidence domain. Use the growth-scout brief, whose collection target is
   the evidence-ledger schema: demand paths/symbols for every claim. Each
   scout writes one ledger per boundary to the plant's gitignored
   seed-organ scratch, `.cypress/growth/<slug>.ledger.md`, outside
   `docs/graph/`, because a ledger is growth-time feedstock rather than
   plant knowledge.
2. Reconcile the per-boundary ledgers into a coherent evidence set in
   the orchestration plane, cross-referencing the persisted ledgers.
   Resolve contradictions with another bounded scout; do not guess.
3. Spawn investigation-class **`research-scout`s** for the external
   evidence, the required counterpart of step 1. Mine the reconciled ledgers' §5
   for every architecturally significant / cross-cutting / security- or
   operations-critical dependency, and the evidence set for external
   standards the project is held to; retrieve version-pinned upstream
   docs per `ingest-library` into `docs/graph/sources/`. Growth-scouts
   read this project's code, research-scouts read the upstream world it
   runs in, and growth needs both.
4. Spawn **authoring-class** authors for every written artifact or deep
   synthesis, using the growth-author brief, which consumes the ledger and
   maps each section to its deliverable: authors build only on the
   collected, cited evidence.
5. Spawn separate **authoring-class** reviewers/validators for graph
   integrity, source fidelity, navigation, and false-premise rejection.
6. Route each finding back to a bounded authoring-class author, then
   revalidate.

Every brief states purpose, exact scope, allowed reads/writes, required
graph context, evidence supplied, constraints, output contract, and
verification. Every spawned session executes
`python3 docs/graph/graph-lint.py --plan "<exact delegated task>"`
before source reads or writes. Route each spawn with
`python3 docs/graph/agent-lint.py --route "<exact delegated task>"` and
cite the ranked specialist and confidence band. Delegating workers spawn
only from their `delegates_to` allowlist and under their
`max_spawn_depth` cap; the deepest legal chain is orchestrator →
multi-agent-architect → architect → leaf (depth 3). Leaf workers carry
no `Task` tool: at an out-of-domain boundary they stop and return the
handback payload naming the next specialist. Every worker ends its turn
with a payload carrying `produced_by` and `route_evidence`.

Two host conditions look alike and only one is fatal. If the host
cannot spawn clean-context workers with selectable model classes, stop
and report that this host cannot execute the seed's operating model;
do not silently collapse delegated work into the main chat. If it can
spawn but a named specialist is **not registered as a spawnable type** (the
ordinary state of the session that just installed the roster), that is
*not* fatal: Phase 1 preflights it and applies
`delegation.harness-registration`.

### Boundaries

- Executable source is primary evidence (manifests, entry points,
  routes, models, migrations, config, deploy descriptors, tests, CI,
  prompts, evaluations). Existing prose is clues only; corroborate.
- That rule scopes to claims **about this project**: for what a
  dependency or external standard *is*, upstream documentation fetched
  by `research-scout` is primary. Web retrieval is in scope for growth;
  Git publishing is not.
- Knowledge writes stay under `docs/graph/`. Outside it, growth writes
  only three seed-organ places, all owned by Phase 1: `.cypress/growth/`,
  `.cypress/coverage.json` and the installer's `.cypress/seed.json`.
  Application code, manifests, CI, infrastructure and tests stay as growth
  found them.
- Growth runs only knowledge checks: lint, link, route and generated-view
  drift. Application builds and test suites stay with the target.
- Branch and commit are recorded as provenance only. Never fetch, pull,
  switch, commit, push, or publish Git state: it is the owner's, and a
  publish cannot be undone.
- Every claim growth writes has evidence behind it; never invent
  behavior, requirements, rationale, ADRs, commands, URLs, project
  skills, or passing status. Mark an uncertain claim `unknown` and name
  the evidence it needs.
- Observed implementation is descriptive architecture, not a normative
  spec.

### Unified knowledge shape

All maintained project knowledge lives under one root, `docs/graph/`,
with `README.md`, `index.md`, `_schema.md`, `graph-lint.py`, and the
collections: `nodes/`, `libraries/`, `sources/`, `legal/` (only when
externally-authored rules are in scope), `product/`, `architecture/`,
`api/`, `data/`, `prompts/`, `evaluations/`, `plans/`, `runbooks/`,
`specs/`, `decisions/`, `best-practices/`, `changelog.md`. Tier 1
routes; Tier 2 owns concise facts; Tier 3 provides source-backed depth.
Every useful leaf is connected from its owning node using `artifacts:`;
dependency pages use `libraries:`. A fact has one owner and links
elsewhere.

### The completeness contract (`grow.completeness-contract`)

Growth is **complete or it is not done**. It establishes the plant's
facts so that no later session has to: a fact the graph states is
settled (`rule.knowledge`), and a fact growth left out is re-derived in
every session after it. A first growth that stops at a skeleton (a root node, a router, and a handful of leaves) is a failed
growth reported as a success, and it is the single most common way this
protocol is mis-run. The contract is binding on whatever model
orchestrates growth; it does not soften with model size, context
pressure, or operator impatience. Full depth is the default, not an
upgrade.

**The rule of evidence-bounded totality.** For every knowledge
collection, growth produces one of exactly two outcomes, never a third
silent one:

- *Covered*. Authored to the full depth its evidence supports: every
  real subsystem has a node; every direct dependency is indexed and each
  architecturally-significant one has a project-specific page grounded
  in retrieved upstream documentation (topology step 3); every
  observed route/message/job/entity/migration/config/AI-contract is
  homed; every leaf is connected to its owning node by an `artifacts:`
  edge; the router resolves representative tasks to small closures.
- *Absent with a named reason*: the collection is empty because the
  **source has no such evidence**, and that absence is stated explicitly
  in the coverage record with the paths searched.

Any collection neither fully covered nor explicitly absent-with-reason
is an incomplete growth. "Ran out of context", "seemed enough", "the
templates are present", and "the common cases are done" are the failure
the contract forbids. Only authored, source-cited content counts as
coverage.

**The coverage record.** Before declaring growth done, the orchestration
chat fills `.cypress/coverage.json` (schema:
`growth-coverage-record.md`) and `tools/growth-audit.py` reads it back.
Rows: one per knowledge collection the installer creates, one per roster
agent declaring `plant_knowledge:`, one per project-specific expert the
plant's own graph carries, and one per stack-inventory item — the first
three derived rather than declared, so a collection, a specialist, or an
expert cannot be forgotten by being left out. An inventory row for a
core or significant stack element also owes an `expertise.*` node, which
is derived rather than decided: the routable handle that says when that
element is in play and points at its pin page and its standards page
without restating either. A dominant domain or a core part of the stack
additionally records whether it warrants an **agent** of its own, which
is warranted only for what a node cannot be — different tools, a
different model class, an adversarial stance, or context isolation — and
names which. Leaving that unasked is `UNSTAFFED`, as is naming no
trigger, an expert named but never authored, and an expert
that reaches `docs/graph/agents/` but no harness projection is reported
as what it is — on disk and unspawnable. Each is `COVERED` (with the
strongest source paths), `ABSENT` (with the reason and the paths
searched), or a named `UNKNOWN` blocker. The record is tracked beside
the plant's `.cypress/seed.json` stamp, never under `docs/graph/` and
never in the gitignored `.cypress/growth/` scratch. A row may not be
left blank, and the audit is what Phase 6 gates on.

**Growth ends on its exit test**, whatever the orchestrator's sense of
"enough": when `growth-audit.py` exits 0, every gate-table row is green or
declared by its named judge, and the maturity test is met against the
graph, not against the file tree. A fatal host limit, a two-round non-converging
finding (`recover`), or an unclosable evidence gap is delivered as an
honest `unknown` with the blocker named: the one legitimate way a
collection stays uncovered, and it is reported, never silent.

### The growth flow (`grow.growth-flow`) — six phases

**Phase 1: Detect and plan.** Determine whether the target is
empty/new, one repository, a workspace/monorepo, or an umbrella of
sibling repos. Stay inside user-placed scope. Record each repo's path,
branch, HEAD, worktree state, role, manifests, and stack without
mutating Git. Ensure the plant gitignores `.cypress/growth/` before
scouting, then write the boundary division to
`.cypress/growth/boundaries.md` — one line per boundary with its ledger
slug — which is the operand `grow.gate.scouts-ran` compares the ledgers
against. Settle spawnability here, not in Phase 2. Inventory cheaply
before opening large files; ignore generated/vendor/cache/build dirs.
Identify real subsystem boundaries and assign focused scouts for
cross-cutting evidence (APIs/messages, data/migrations, platform/config,
tests/CI/operations, dependencies, prompts/evaluations). If there is no
executable project evidence, the work goes to `from-scratch`
(`protocol.initialize` owns the fork). The plant-facts ask to the owner
also requests the plant's model map in `docs/graph/models.md`
(`delegation.model-map`, ADR-0022): the providers, and a model for each
class and effort on each host the plant runs.

**Phase 2: Scout and establish evidence.** Spawn the planned
investigation-class scouts on the growth-scout brief. Each writes one ledger to
`.cypress/growth/<slug>.ledger.md` with terse factual claims and exact
paths/symbols for: bootstrap/entry points/packages/imports;
inbound routes/messages/jobs and outbound integrations;
entities/schemas/migrations/persistence; config/secrets
interfaces/deployment/observability; tests/CI/scripts/operational
commands/prompts/evaluations; direct dependencies and evidence of
actual use; and discrepancies between executable source and existing
prose. The persisted per-boundary ledgers are the evidence set.
Reconcile across them; resolve contradictions by scoped follow-up
scouting; record which ledger owns each contested fact. Then run the
external pass (topology step 3) before authoring: dispatch
`research-scout`s for every §5-flagged significant dependency and the
external standards the project is held to; record the dispatch list.
Phase 4's `libraries/` rich pages, normative `best-practices/`, and
`sources/` are authored from this material, and the coverage record
audits against it. No web retrieval on the host is a named blocker in the
delivery.

**Phase 3: Model and author through authoring-class workers.** Configure
`ROOT_ID` and `KINDS` in `graph-lint.py`. Brief authoring-class authors on
the growth-author brief, pointing each at the ledgers it reads, the
exact output paths, schema, relevant existing nodes, and exclusive write
scopes. Author: one root node; one node per real subsystem/bounded
capability; shared stack/platform/data/domain/cross-cutting nodes where
they remove duplication or improve routing; a compact Tier-1
task-to-entry router using realistic developer phrases. Each node has
unique `owns`, minimal acyclic `requires`, explicit boundary `peers`,
concrete `load_when`, honest token cost, source paths, and leaf edges.
Each author gets an exclusive write scope.

**Phase 4: Grow source-backed leaves.** Through bounded authoring-class authors,
populate every collection supported by evidence: `product/`
(actors/capabilities/flows/constraints/observed behavior);
`architecture/` (context/components/boundaries/runtime flows/dated sharp
edges); `api/` (observed HTTP/RPC/event/job contracts + source
locations); `data/` (entities/ownership/persistence/migrations/
lineage/privacy); `libraries/` (every direct dependency indexed; rich
pages for significant ones, grounded in the retrieved upstream
material; a thin index where §5 flags significant deps is not coverage;
smoke tests recorded as pending backfill); `legal/` (only when subject
to externally-authored rules; check `legal-corpus/` first, re-confirm
`verified`/`legal_status` against the publisher); `sources/`
(provenance for this growth's research-scout ingests; "no external
information consumed" when none was dispatched is circular and a
completeness defect); `prompts/` and `evaluations/`;
`runbooks/verification.md` (exact
commands, labeled `discovered, not executed`); `plans/grill.md`
(evidence, gaps, next increment); `best-practices/` (**normative**: the
external standard, cited, plus the project's observed stance, not a
description of current habits); `changelog.md`.
Prepare `specs/` and `decisions/` indexes, and formalize a spec only from
a real observable and an ADR only from a decision the source shows. Where a ledger's specialist-agent
signal genuinely warrants it, author a project-specific expert agent; a signal
is a candidate, not a mandate.

**Phase 5: Connect and fertilize (the librarian rebalance pass).** A
named `docs-librarian` dispatch after Phase 4 that always runs, however
well the authors linked things: connect every leaf to its
owning node, merge duplicate fact homes, split accreted nodes, delete
pass-throughs, keep searchable paths/symbols/commands in the right home
and the router compact; re-run `graph-lint.py` after rebalancing and
carry the merge/split/move/delete report into the delivery. Depth
belongs behind edges, not in the always-loaded router or oversized
nodes.

**Phase 6: Independent validation.** Dispatch separate authoring-class reviewers
and clean-context validators. They run only knowledge checks
(`graph-lint.py` plain and `--plan`), and verify: (1) internal links and
every `artifacts:`/`libraries:` edge resolve; (2) no maintained
collection outside `docs/graph/`; (3) no template placeholders or
fabricated dates/statuses; (4) representative tasks load small
closures; (5) known-answer questions answered from routed context with
citations, including adversarial false-premise rejection; (6) observed
implementation not mislabeled as specs or ADR rationale; (7) commands
distinguish executed from discovered; (8) generated tool views pass
drift check; (9) the growth is **minimum-sufficient and well-composed**
(no artifact without a consumer, no second home for a fact, compact
router, one coherent responsibility per node); (10) the growth is
**complete** against the completeness contract (a row per collection,
each `covered` with sampled source paths or `absent` with confirmed
no-evidence); (11) the growth is **externally grounded** (every
§5-flagged dependency has a rich upstream-cited page, `sources/` rows
resolve, `best-practices/` is normative, and a `sources/` ABSENT caused
by never dispatching a research-scout is a circular-absence finding);
(12) the Phase 5 librarian rebalance pass actually ran and its report is
in the delivery. Under-growth is a defect on equal footing with
over-growth. Route findings to bounded authoring-class authors and repeat
validation, **bounded by the recover discipline**: the authoring pass and
two author-fix → revalidate rounds are the three attempts
`protocol.recover` allows. Stop there, record a finding that survives them
as an honest unknown or defect, and hand the decision to the user. The
linter stays as written (`grow.gate.graph-integrity`). When validation passes, set
`grown: true` in the frontmatter of `docs/graph/index.md` and, in the
same edit, remove the placeholder's pre-growth block, which a grown
plant has no reader for. Also configure the spec-coverage gate (`TEST_GLOBS` in `spec-lint.py`) while the stack
evidence is fresh.

### Delivery and maturity

Growth closes through `canonize` (§3.7) before reporting, so its own
lessons land in the graph. The growth session keeps its own session
record in `docs/graph/plans/sessions/` from Phase 1, listing any
memories the host already holds for the project for that close-out.
The orchestration chat reports target
boundary/revisions, worker
assignments, evidence inspected, artifacts created/refreshed, the Phase
5 librarian rebalance report, validation
results, untrusted/excluded docs, honest unknowns, and one next action
**with its tier** (kernel §0). It includes the **growth completeness
ledger** (every collection covered-to-evidence or absent-with-reason) so
the delivery proves totality instead of asserting it, plus growth
metrics (scouts and authors spawned, contradictions resolved,
findings raised and fixed, evidence gaps left open), the plant's birth
telemetry that `harvest` mines. The plant is **mature** when a
clean-context agent can orient from `index.md` without bulk-reading
source; major capabilities, integrations, data, and cross-cutting
concerns have single fact owners with concrete source paths; useful leaf
depth is connected; critical dependencies have project-specific context;
operational status is explicit; representative routing is narrow; and
adversarial navigation rejects false premises. Template presence alone
is no evidence of maturity.

---

## initialize

*Source: `protocols/initialize.md`*

- **id:** `protocol.initialize`, tier 2
- **owns:** `initialize.entry-fork`, `initialize.adapter-edges`
- **requires:** —
- **peers:** `protocol.grow`, `protocol.from-scratch`, `agent.seed-installer`
- **load_when:** "/initialize command invoked"; "just installed the seed,
  which protocol do I enter"; "empty repo or existing code, where does growth
  start"; "set up the seed via the coding tool"; "dry-run the initialization"

### What it does

`/initialize` is a convenience adapter for Claude Code, Prime Agent,
Codex, opencode, Copilot, and similar coding tools. The primary
tool-neutral entry point is `INSTALL_PROMPT.md`; the canonical workflow
is `docs/graph/protocols/grow.md`. This node forks: it selects grow when
the target has executable project evidence to scout and from-scratch when
the repository is empty or near-empty, and it only owns the branch. Each
arm is a whole protocol that runs to its own exit conditions. The two arms are
peers, each in its own table cell. No test checks those cells, so a swap or
a merge would pass the gate.

When invoked, take the fork, then enter the chosen protocol and execute
it as written: orchestration, model-class, routing and evidence policy
belong to that protocol.

### The adapter's own hard edges (`initialize.adapter-edges`)

The adapter adds only these edges of its own:
1. The roster this adapter installs is not spawnable in the session that
   installed it: preflight and remedy per
   `delegation.harness-registration` before any by-name dispatch.
2. The fork runs no application build and no application test suite.
3. The fork never pushes, fetches, pulls, switches, or commits Git.
4. The fork leaves application code as it found it and fabricates no
   normative record.

Edge 1 binds both arms. Edges 2-4 bind the fork and the `grow` arm, whose
own boundaries hold them too; the `from-scratch` arm runs, tests and
commits by its own phase table.

Support `--dry-run` by performing only orchestration planning and
read-only scouting, then reporting the fork's verdict and the proposed
authoring briefs without spawning writers. All detailed discovery, authoring, validation, and
maturity criteria are in `grow.md` and the full-growth procedure it
references.

---

## harvest

*Source: `protocols/harvest.md`*

- **id:** `protocol.harvest`, tier 2 (note: no `command: true`)
- **owns:** `harvest.fold-back-flow`, `harvest.agnosticism-gate`,
  `harvest.availability-gate`, `harvest.corpus-contracts`
- **requires:** `method.delegation`
- **peers:** `method.minimum-sufficient-work`, `skill.humanizer`,
  `protocol.canonize`, `protocol.graft`, `protocol.grow`,
  `protocol.ingest-library`, `skill.toolcraft`
- **load_when:** "harvest lessons back into the seed"; "fold generalizable
  improvements upstream"; "the plant is mature, propose a harvest"; "seed
  improvement from project experience"; "should this library, tool, skill,
  or expert page go into the seed's corpus"; "is this lesson
  project-agnostic enough to land in the seed"; "wire a harvested artifact
  so install, grow, or graft actually delivers it"; "propose promoting a
  plant-commissioned expert into the base roster"; "a harvested page is in
  the seed but no plant can reach it"

### What it does

Harvest is the inverse of grow. `grow` runs the seed *into* a project
and grows it; harvest runs the other direction, a mature project *back
into* the seed, so the next project starts ahead of where this one did.
A seed that only seeds cannot improve; a seed that harvests carelessly
rots into one project's specifics. Harvest is the disciplined gate that
lets the seed compound **without** losing its agnosticism. It takes only
the seed-worthy essence of what the plant learned, never the plant's
flesh. What goes back in must be true for *any* future plant.

### Trigger: user-started; the system proposes, the steward starts

Harvest is **user-sovereign**. Unlike `canonize`, which runs at the end of
every task, harvest starts only when the user starts it: never
automatically, on a schedule, by a hook, or as a "while I'm here" step.
- The user starts it, by invoking this protocol or pasting
  `HARVEST_PROMPT.md`.
- The system may, at most, propose it: when a mature plant clearly
  holds generalizable lessons, an agent may *suggest* "this looks worth
  harvesting" and stop. The suggestion is a doorbell, not an entry.
- Nothing reaches the seed until the user is satisfied. Every
  fold-back is a proposal the user ratifies; an unratified harvest is a
  draft.

### When to invoke

- The **user** has asked to harvest, or ratified a proposal.
- The plant is **fully grown**: delivered, gates green, plan-of-record
  closed or steady. Harvest a still-churning project and you backport
  half-baked lessons.
- The plant produced **generalizable** artifacts worth compounding: a
  shared-tooling bug fixed, a new hard rule, a protocol gap, a new
  reusable expert, a better template section, a universal failure-class
  prevention.
- You are the seed's **steward** (the user acting as owner). The plant
  is a read-only donor; the seed is the only thing this protocol writes.

### The three gates (`harvest.agnosticism-gate` and its siblings)

Every candidate improvement passes three hard tests before it may touch
the seed.

**Gate 1: Agnosticism (the heart).** "Would this help an arbitrary
next project, in a different language, framework, and domain, that has
never heard of this plant?"
- YES, verbatim → harvest as-is (rare, usually only tool-neutral
  rules).
- YES, once generalized → rewrite it stripping every plant-specific
  name, domain term, stack pin, path, and example, then harvest the
  generalized form; state the before→after explicitly.
- NO → reject; record why; leave it in the plant.

Fail-closed corollary: **a lesson is ready to harvest only when it can
be stated without naming the plant.** A single leaked project name,
domain noun, credential, dataset shape, or version-pinned specific in
the seed is a failed harvest, worse than a missed lesson.

*What counts as a project reference* (each is stripped from everything
the seed commits, including the CHANGELOG entry, harvest-log row,
provenance notes, and illustrative examples): a name (plant, product, company, service,
internal tool); a stack fingerprint (the language/framework/datastore
combo that identifies the plant); an identifying count or metric; a
description of the plant's internals (file names, config keys,
plugin names, module wiring, a security finding on its own code); a
path, host, port, credential, or absolute install location; an
illustrative example framed as the plant's own (recast every example
in the generic). Plant-identifying provenance belongs only in the
ratification proposal shown to the steward, never in the seed's
committed files.

*The mechanical floor* (`tools/agnosticism-lint.py`; the sibling
`tools/status-register.py` is the mechanical floor for lifecycle status, and
`tools/status-migrate.py` the one-time migration into it). Gate 1 is a
judgement call, but three of its classes are not: a real host address, a
pinned advisory, and a term the tree already knows it must not carry are
objective, and review is exactly where they slip through. The shared
linter scans any project-agnostic tree for those three and reports
`path:line` with the offending term.

```sh
python3 tools/agnosticism-lint.py --root <dir> [--root <dir> ...]
python3 tools/agnosticism-lint.py --root <dir> --forbid <token> \
        --forbid <another-token> --glob '*.md' --file <path>
```

Exit 0 clean, 1 with findings, 2 on a usage error, including a scan
that matched no file, which would otherwise print the pass a real scan
earns.
The `--forbid` terms are the caller's, repeatable, and matched
case-insensitively as substrings (fail-closed, so a token catches the
compounds built from it): a component meant for any project cannot
enumerate the names it must not contain without containing them, so the
adopting tree supplies its own, exactly as `graft-audit.py` takes
`--tokens`. `tests/seed-lint.py` runs this same code over the seed's
shipped prose, passing no `--forbid`, because the seed has no plant token
it could name. Everything subtler (a domain noun, a stack combination,
an identifying count) stays human judgement and is not faked
mechanically.

**Gate 2: Durability (surface, not pin).** "Will this still be true a
version from now — is it about the library, or about one pinned release
of it?"
- KEEP (surface, durable): the capability the library provides; its
  core API shape and canonical usage; idioms/best practices that hold
  across lines; conceptual gotchas; the upstream doc/repo home.
- REJECT (pinned, ephemeral): CVEs/advisories tied to an exact
  version; "version X.Y.Z is a breaking marker"; per-release
  deprecations; upgrade/migration diffs between pins; a resolved-version
  number itself. These belong in the plant's
  `docs/graph/libraries/<name>.md`. When in doubt, a fact is pinned;
  drop it.

**Gate 3: Non-redundancy (does the seed already own this?).** "Does the
seed ALREADY say this — in a kernel rule, an agent, a skill, a protocol,
or a template?" A plant grew *from* the seed, so its ADRs, plan, and
best-practices are saturated with the seed's own doctrine filled with
local facts. A survey that reads only the plant keeps "discovering"
rules the seed already ships (reversibility-with-trigger, risk-paired-
with-a-check, fail-closed defaults, released-bits-are-tested-bits,
resolve-in-place, two-axis severity). Before any candidate is proposed,
**open its would-be seed home and read it**: if the rule already lives
there, the candidate is **rejected as redundant**. A candidate that
bolts a second home onto a fact the seed already owns fails
one-home-per-fact (`seed-lint`).

### The fold-back flow (`harvest.fold-back-flow`) — five phases

Orchestrated like `grow`: the session plans, briefs, and ratifies;
clean-context workers survey, triage, and author: investigation-class for
the read-only survey, authoring-class for every generalization and
authoring.

**Phase 1: Survey the mature plant (investigation-class scouts, read-only).**
Inventory how the plant diverged from the seed and what it accumulated.
A prior `graft`'s customization-audit ledger and its KEEP-PLANT list
(`tools/graft-audit.py` output) is a ready-made divergence inventory;
start from it. Candidate donor surfaces include: shared scripts/tooling
the plant fixed; skills whose rules it sharpened and any project skill
it authored; protocols found insufficient; agent/expert definitions;
templates with better sections; the sharp-edges/case library/ADRs (mined
for the *generalizable prevention rule* only, never the narrative); the
plan-of-record's §6/§7/§11/§12 (mined for *decision and planning
discipline*, never actual decisions); best-practices pages (a durable
principle, never a stack-specific rule); runbooks (operational
*discipline*, never hosts/commands/ports); library/language wiki pages
(their **version-durable surface** only); the reusable-tool catalog
(project-agnostic durable tools); legal/regulatory leaves (the
**citation only**, never the application); session metrics (the seed's
only *quantitative* donor surface: mine the *pattern*, propose the seed
change); and a capability the seed ships that stays inert across plants
(harvest the *fix to the seed's own machinery*). Output: a **candidate
ledger** with provenance per row.

**Phase 2: Triage against all three gates (authoring-class authors).** For each
candidate, apply agnosticism, durability, and non-redundancy, and decide
KEEP-AS-IS / GENERALIZE / REJECT. For anything kept, write its
**generalized restatement** with the before→after shown (what
plant-specifics *and* pinned specifics were stripped). Reject rows carry
a one-line reason (including "redundant — the seed already owns this at
`<home>`"). Be conservative; when in doubt, reject or generalize
harder.

**Phase 3: Backport authoring (authoring-class authors).** Apply each surviving
generalized improvement to the seed artifact it belongs in (`skills/`,
`protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit**, integrated as if
it had always been there. Every fold-back records provenance (plant
lineage, generalization applied, seed files touched). A harvested
tooling fix arrives with its regression test generalized alongside it.

**Phase 4: Seed integrity gate.** The seed leaves harvest more capable
and no less agnostic; the node holds the checks as a gate table, one row
per check with its id and command. In summary:
- Agnosticism scan: grep the *entire* diff (including CHANGELOG,
  harvest-log, provenance notes) for any plant name, domain noun, stack
  fingerprint, identifying count, internal-component/file/config name,
  path, credential, dataset shape, or version pin. Any hit BLOCKS.
- Self-consistency: run the seed's own lints/tests; kernel,
  manifest, protocol table, and registries stay in sync.
- Clean install: a dry-run install into a scratch target still
  succeeds and is additive.
- Minimum-sufficient fold-back: generalize an existing rule rather
  than appending a sibling; land the lesson in the cheapest surface that
  reaches its audience (a reference file before a protocol, a protocol
  before the kernel; kernel bytes cost every session of every plant);
  prefer the smallest edit.
- Version + provenance: bump the seed version, add a CHANGELOG
  entry and a harvest-log row; each check names its command and result.

**Phase 5: Deliver (propose, do not impose).** Harvest **proposes**;
the human steward **ratifies**. Emit the fold-back as a reviewable
patch/proposal, never a silent mutation of the seed.

### The five corpora

Harvest maintains five seed-side corpora that later `grow`/`graft`
withdraw from. Each folds the durable, agnostic surface and never a
plant's own facts:

| Corpus | Path key | Keeps (durable) | Stays out (plant-bound) |
|--------|----------|-----------------|-------------------------|
| Library & language | `library-corpus/<ecosystem>/<library>.md`, keyed by library not version | capability, core API shape, idioms, conceptual pitfalls, upstream home | pinned CVEs, per-release deprecations, migration diffs, resolved version numbers |
| Legal & regulatory | `legal-corpus/<scope>/<instrument-slug>.md` (scope: eu / national / international / case-law) | the citation itself (instrument, provision, `text_form` + text, publisher URL, `verification_grade`, `legal_status`, verified absence) | any application of the law to a system, every finding/determination |
| Reusable tool | `tool-corpus/<category>/<name>.md` | capability, interface shape, approach/algorithm, portable implementation when stack-neutral | project paths, credentials, dataset shapes, version-locked deps |
| Suggested expert | `agent-corpus/<name>.md` | the role's mandate, when-to-select, boundary, `routing_triggers` exemplars | stack-specific experts, roles duplicating a base-roster mandate |
| Suggested skill | `skill-corpus/<name>.md` | the procedure's steps and the gate each clears, by composition | stack-bound recipes, anything duplicating a core skill |

Two disciplines are special. Legal currency: an entry states whether
its text is the **original** or the **consolidated/as-amended** edition
(the amendment trap), and a `verification_grade` is **never upgraded
without a new fetch**: downgrading on new evidence is expected,
upgrading without re-reading is falsification. Expert promotion:
harvested roles land in the **catalog** by default, never straight into
the always-loaded roster; promotion to the base roster is a separate,
steward-only decision whose bar is higher than "useful": the mandate
must be *universal* (every project produces the thing it addresses) and
uncovered by any base agent. Harvest may *propose* a promotion; the
steward makes it.

### Output — two distinct records

Harvest produces two records that do **not** carry the same content:
1. The ratification proposal: stated in chat / the PR for the
   steward. It *may* name the plant and show every before→after
   generalization. It is **never committed to the seed.**
2. The seed-committed record: the CHANGELOG entry and harvest-log
   row that land inside the seed, bound by the agnosticism gate: no plant
   name, stack fingerprint, count, internal name, or "from <this stack>
   plant" line. It records *that* a harvest happened and *what*
   generalized lesson landed, never *whose* plant it came from.

A harvest reads the plant's `docs/graph/` content as donor evidence and
carries back only the generalized lesson, never the content itself.

---

## graft

*Source: `protocols/graft.md`*

- **id:** `protocol.graft`, tier 2 (note: no `command: true`)
- **owns:** `graft.reconcile-flow`, `graft.user-sovereignty`,
  `graft.pure-graph-mandate`, `graft.migration`, `graft.integrity-gates`,
  `graft.reversibility`
- **requires:** `method.delegation`
- **peers:** `protocol.grow`, `protocol.harvest`, `protocol.deliver`,
  `method.engineering-posture`
- **load_when:** "upgrade this plant to the newer seed"; "graft the seed,
  re-propagate machinery"; "plant grew from an older seed version";
  "reconcile local machinery divergence"; "migrate a pre-6.0 plant out of
  the tool-dir layout into docs/graph"; "move a pre-7.0.0 plant's lifecycle
  status into frontmatter"; "this plant's plan-of-record is in a shape the
  seed has since changed"; "the graft audit reported a buried customization,
  a stale kernel, or an unmapped backup"; "undo a graft, restore a plant
  from the installer's backups"; "which installer flags are safe to use on a
  grown plant"; "does this upgraded plant carry the legal corpus, under
  which national jurisdiction"; "switch a symlinked plant back to copies
  before upgrading it"

### What it does

Graft is the distribution arm of the cross-project meta-loop and the
complement of harvest. `grow` runs the seed into a **new** project;
`harvest` runs a mature plant **back into** the seed; graft closes the
third side: it carries the enriched seed **outward onto an existing
plant**, so a plant grown from an older seed inherits everything the
seed has learned since, without being torn up and regrown.

The garden metaphor is load-bearing: you graft the new scion onto the
living rootstock. The **rootstock** is the plant's own life (its source
code and the knowledge it authored about itself), and it is inviolate.
The **scion** is the seed's evolved machinery: kernel, protocols,
skills, agents, templates, shared tooling, and the library/tool corpus.
Harvest and graft are one circulatory system: harvest is **collection**
(one plant's lessons up into the seed), graft is **distribution** (the
enriched seed back out to every sibling plant).

### Trigger: user-decided; the system proposes, the steward starts (`graft.user-sovereignty`)

Like harvest, graft is **user-sovereign**. It changes an established,
possibly production plant, so the **steward** decides when a plant is
upgraded and ratifies before it is applied.
- The user starts it, by invoking this protocol or pasting
  `GRAFT_PROMPT.md` with a plant (or a set of sibling plants).
- The system may propose it, most naturally as the tail of a
  `harvest`: "the seed now carries fruit that plants X, Y, Z predate —
  each is due for a graft" and stop. The proposal is a doorbell, not an
  entry.
- Every upgrade is ratified before it lands. Graft reconciles, then
  proposes the reconciled diff; the steward ratifies. An unratified
  graft is a draft. Because every replacement is backed up first, a
  ratified graft is also reversible.

### When to invoke

- The **user** has asked to graft, or ratified a proposal.
- The plant is **grown and steady**: its graph routes, its
  plan-of-record is closed or calm. Grafting mid-churn muddies both.
- The seed has **moved on** since the plant grew: a harvest folded in
  new fruit, a protocol sharpened, the corpus grew pages. The wider the
  gap, the more the plant gains.
- The plant's working tree is **clean** (or the steward accepts a
  backup-only safety net).

### The rootstock line — the heart

Harvest's heart is the agnosticism gate (*nothing project-specific
enters the seed*). Graft's heart is its mirror, the **rootstock line**:
*nothing the plant authored about itself is overwritten by the upgrade.*

Two territories, and graft writes to exactly one:
- Seed-owned machinery (graft's to upgrade): the kernel
  (`CLAUDE.md`/`AGENTS.md`/`.github/copilot-instructions.md`); the
  seed-owned graph subtrees
  `docs/graph/{protocols,skills,agents,method,templates}/` (every node
  marked `origin: seed`); the harness projections (`.claude/agents/`,
  `.claude/skills/`, and the `.prime/agent/`, `.opencode/`, `.codex/`,
  `.github/` equivalents); tool-specific commands/settings/hooks; the
  shared router script `docs/graph/agent-lint.py`; the config-free scripts
  that fast-forward with it, now including `docs/graph/prose-lint.py`; and
  the graph engine scripts
  `docs/graph/{graph-lint.py,spec-lint.py,grill-lint.py}` (each keeping the
  config it carries). `_schema.md` and `index.md` are
  project-instantiated and stay the plant's, always.
- The plant's own life (graft preserves, always): the plant's
  application source, and every knowledge fact the plant authored under
  `docs/graph/`: its `nodes/`, `specs/`, `decisions/`, `libraries/`,
  `plans/`, `runbooks/`, product/architecture/API/data, any node
  **without** `origin: seed`, and the pinned version-specific facts in
  its library and tool pages.

> The rootstock line: the plant's source and its authored
> `docs/graph/` facts stay as the plant left them. If an upgrade cannot
> land without rewriting something the plant authored, it stops at the
> line and becomes a proposal for the steward, never a silent
> overwrite. A plant fact the graft corrects is retracted as
> `skill.holistic-editing` retracts a recorded claim: struck through,
> with a dated correction.

The one nuance: a plant's library and tool **pages** are plant-owned,
yet graft may refresh their *surface* from the enriched corpus (Phase
4), renewing only the version-durable orientation and re-pinning the
plant's version-specific facts fresh. Renewing the orientation is a
graft; overwriting a pin is not.

### The pure-graph mandate (`graft.pure-graph-mandate`)

The rootstock line is graft's conservative heart (*preserve what the
plant authored*); the pure-graph mandate is its reconstructive heart
(*every graft leaves the plant closer to the seed's architecture than it
found it*). The seed's architecture is a **pure graph**:
everything that can activate progressively is a routable node; nothing
about how to work is always-loaded except a small bootstrap kernel;
every tool-dir surface is a *generated projection* of a node; each fact
has one home; and no obsolete era, duplicate home, or competing doctrine
survives. Anywhere a plant falls short (machinery outside the graph, a
fact with two homes, an always-loaded file that should be a node, a
hand-maintained projection drifting from source, dead compatibility
residue), it is drift, and closing it is in graft's scope. Graft
executes this as holistic reconstruction: reconstruct from evidence not
preference; one home, natural owner; integrate don't bolt on;
minimum-sufficient, sliced, reversible; verify and fix drift at its
home. The pre-6.0 layout migration is the *maximal instance* of this
mandate; the mandate is **standing**: even a plant one version behind
gets audited and rebalanced as Phase 6, every graft.

### The three-way reconciliation (`graft.reconcile-flow`)

A plant is not a blank target; its steward may have locally sharpened a
protocol, adjusted a setting, or fixed a script. Graft reconciles three
versions of every seed-owned artifact:
- base: the seed revision the plant grew from (the tag of the stamped
  version, else inferred by content lineage; Phase 1 prints it);
- theirs: the artifact in the seed today;
- ours: the artifact as it stands in the plant.

Each artifact takes one of three clean paths:
- FAST-FORWARD: the seed advanced and the plant left the artifact
  pristine. Adopt the seed's new version outright (the common case and
  the bulk of a graft's value).
- KEEP-PLANT (and flag upstream): the plant diverged and the seed
  did not. Keep the plant's version untouched, and record the divergence
  as a **harvest candidate**. Graft's outbound pass feeds the inbound
  loop.
- MERGE: both advanced the same artifact. Reconcile as a single
  **holistic re-integration**: one coherent file carrying the seed's new
  capability *and* the plant's intent, surfaced to the steward as a
  reviewable proposal. A three-way conflict is a decision, and the
  decision is the steward's.

### The flow — eight phases

Orchestrated like grow/harvest: an investigation-class survey
(read-only), and authoring-class workers for every reconciliation, merge,
corpus refresh, and validation. Every worker runs the plant's router
(`graph-lint.py --plan`) before reading plant source.

**Phase 1: Locate the plant and establish the base (session + investigation class).**
Identify the plant or sibling set; record path, host integration,
branch, HEAD, worktree cleanliness (provenance, no Git mutation). Read
the plant's **seed stamp**; `python3 <seed>/tools/graft-ledger.py
<plant> <seed> --base` prints the base: the stamped version's tag, or
else the seed commit the plant's machinery matches best, with the match
count. With no stamp the base is that inference, and this graft
establishes the stamp. Confirm
the seed's version and what changed between base and now (its CHANGELOG
and harvest log are the map of available fruit).

**Phase 2: Survey the drift (investigation-class scouts, read-only).** The
machinery half is a command, not a guess: `python3
<seed>/tools/graft-ledger.py <plant> <seed>` prints one row per
seed-owned file with its three-way class. Read-only scouts inventory the
**fruit the plant can withdraw**: libraries, tools, and legal
instruments the plant reasons against for which the corpus now holds a
page the plant predates or lacks. The **graft ledger** is the tool's
table plus one row per withdrawable page.

Before the graft calls any migration below optional, it reads the
plant's operator node (`crosscut.operator`): an owner rule recorded
there can make that migration owed.

**Layout migration 5.x → 6.0.0** (between survey and reconcile, when the
survey finds a pre-6.0 plant whose machinery lives in
`.claude/protocols/`, `.claude/templates/`, `.claude/core/` instead of
the graph subtrees): (a) install the new machinery into `docs/graph/`
as `origin: seed` nodes and regenerate projections; (b) diff old
tool-dir copies against their seed base, where a plant-local
customization is carried into the graph copy as a holistic MERGE and
also raised as a harvest candidate; (c) relocate the plant's OWN
agents and skills into `docs/graph/{agents,skills}/`, holistically
reconciled: add the node
frontmatter they lack, trim every restated fact to a cross-reference,
regenerate the `.claude/` projection; (d) list the now-redundant old
machinery, and the **steward** confirms deletion explicitly, by name
(graft never deletes unprompted); (e) rewrite stale references in
plant-authored docs only with the steward's consent; (f) sweep the
plant's own pre-graph knowledge, since a migration this old owes a
fact-sweep, not just a machinery swap: dispatch read-only scouts across
the plant's actual source to inventory facts missing from the graph,
cross-checked against existing nodes, and hand confirmed findings to
authoring-class authors to weave into the owning node.

**Memory migration** (when the host holds memories for the plant): read the harness memory read-only, write the plant's first
session record in `docs/graph/plans/sessions/` listing every entry to
migrate, and let the graft's own canonize close-out file it. Retiring
or deleting a harness entry is the steward's numbered decision, by name
(kernel §4). The kernel's §3.2 sentence arrives with the kernel
fast-forward, and the session-record form is an expected new file
under `plans/`.

**Phase 3: Reconcile the machinery (authoring-class authors).** For each ledger
row, act on its class: nothing on CURRENT; adopt on FAST-FORWARD and
SEED-NEW, and on HARVESTED, whose plant lines a harvest already carried
into the seed, so it raises no candidate; retain and raise a harvest candidate on KEEP-PLANT; author
one holistic re-integration on MERGE. Every merged file arrives whole,
as one integrated file. **The roster delta is
not spawnable in this session**: preflight and take the remedy
(`delegation.harness-registration`); carry the delta forward as a named
list for Phase 7. **The graph engines are machinery too**: the installer
drops the scaffold only if absent, and a plain re-install never
overwrites a placed engine, so an existing plant receives a new engine by
graft only. Reconcile all three as a config-preserving fast-forward:
adopt the seed's current engine body and re-inject the config that
engine carries (`ROOT_ID` / `KINDS` / `KIND_PREFIX` in `graph-lint.py`;
`TEST_GLOBS` in `spec-lint.py`; none in `grill-lint.py`). With no
`--preserve`, `tools/graft-graph-engine.py` picks the set from the plant
file's name; an explicit `--preserve` wins. A config knob the seed has *extended* is **UNIONED**,
not re-injected wholesale; the load-bearing case is `KINDS` (the seed's
`protocol`/`skill`/`agent`/`method` kinds join the plant's own set, because
keeping the plant's older set verbatim would fail every new machinery node
with `kind not in KINDS`).
`tools/graft-graph-engine.py` performs this merge, and Phase 7 audits
all three with one `--engine` pair each.
`_schema.md`/`index.md` stay the plant's (project-instantiated). **The
installer fast-forwards blindly**: a mandatory post-FF audit (Phase 7,
`tools/graft-audit.py`) catches any local divergence a blind FF buried.

**Phase 4: Refresh the plant's knowledge from the corpus
(authoring-class authors).** For each withdrawable library/tool page, **seed the refresh
from the corpus as the orientation layer**, then re-pin the plant's
version-specific facts fresh against the plant's real lockfile. A
withdrawable **legal** page adds one non-negotiable step: re-confirm each
entry's `verified` date and `legal_status` against the publisher, and
never copy a determination. **One home per dependency**: merge the
corpus orientation into the plant's existing page and keep the plant's
own grouping, because a parallel page or the corpus's internal
sub-namespace grouping would create a duplicate home the Phase 7
minimum-sufficiency gate blocks on.

**Phase 5: Grow the new capabilities onto the living plant
(authoring-class authors).** Fast-forwarding *carries* a capability; it does not *grow*
it. **Grafted is not grown.** For each new or newly-enriched capability:
grow what the plant evidently needs, grounded in its own facts
(instantiate a suggested skill/expert the plant's stack calls for,
withdraw a corpus library/tool/legal page it actually uses, ground a
runbook it can fill). **A surface is filled only from evidence**: a project
skill, ADR, or runbook whose content can only come from real recurring
use sprouts during use, owned by the close-out lifecycle (`canonize` →
`docs-librarian`), not by the graft. **Surface what was grafted but not
grown** so the steward sees the copy-but-not-actualized state. **An
own-kernel plant** (one that carries no seed machinery) still receives
the substance as a **weave**, not a summary: map each seed surface the
delta changed to the plant's equivalent surface and land each rule where
it acts, in the plant's idiom. Collapsing the delta into one summary
section is a photocopy, not a graft.

**Phase 6: Rebalance the plant toward pure graph (investigation-class
audit, then authoring-class authors).** The reconstruction pass, on **every** graft. (1) Inventory
the drift as a rebalance ledger, hunting: machinery outside the graph; a
fact with two homes; a hand-maintained projection drifted from its node;
obsolete residue; substantive thinness (the (f) sweep, now standing). (2)
Reconstruct in slices bounded by the rootstock line: move each item to
its natural node home as a holistic MERGE, collapse duplicate homes,
regenerate drifted projections, list obsolete residue for the steward's
explicit deletion confirmation. Every relocation preserves the fact
itself. (3) Leave the drift closed at its home; install a missing
fitness function the seed now ships; surface any residual drift with a
remediation.

**Phase 7: Apply, verify, and stamp (`graft.integrity-gates`;
authoring-class authors, session gates).**
Apply the ratified upgrade **additively**, backing up every replaced
file first. `python3 <seed>/tools/graft-run.py <plant> <seed> --stage
<dir>` rehearses the mechanical half on a copy outside the plant (the
ledger, the install with its log, the engines, the audits and the
lints) and prints the gate table's result column, with each judgment
row `not run`. It writes nothing in the plant and ratifies nothing. Then
prove the plant is left more capable and no less itself:
- Rootstock intact: the plant's source and authored facts are
  byte-for-byte unchanged outside machinery and the deliberately
  refreshed surfaces. Any unexpected change BLOCKS.
- Customization audit (`tools/graft-audit.py`, with `--base` set to the
  base Phase 1 printed): any seed-owned file
  whose backup differs from the seed *and* carries plant-signal content
  is a divergence the blind FF overwrote; re-integrate or ratify. An
  un-reintegrated, un-ratified customization BLOCKS.
- Unfilled scaffolds (`tools/graft-audit.py <plant> <seed> --unfilled`):
  every docs leaf still byte-identical to its `templates/docs/**` template is
  reported; `--rename` (default) turns it into `<name>.unfilled.md`, a marker
  the installer honours so the blank leaf is never re-created; `--prune`
  deletes, only on the steward's say-so (after prune the template reappears on
  the next install). `verification.md` is exempt only when it carries an
  `executed` gate row. An unfilled scaffold shadows the authored leaf a cold
  agent needed, so a surviving one BLOCKS. An unfilled model map,
  `docs/graph/models.md`, is the one exception: the audit reports it as a
  `DISCLOSED` line and passes, and every agent inherits its caller's model
  until the map is filled.
- Lifecycle status: the plant's `status:` frontmatter (ADRs, specs,
  deviations, risks) is plant-owned and never touched by the fast-forward; a
  plant that carries lifecycle status as body prose runs `tools/status-migrate.py --root docs/graph`
  (dry run, then `--write`) as part of the layout migration and the graft record
  carries its table; `docs/graph/status-register.py` then lints it.
- Machinery healthy: the plant's graph still routes on the upgraded
  engine; the agent router lints and evals clean; internal links and
  edges resolve. Report the **roster delta** as work the plant's next
  session registers.
- Minimum-sufficient upgrade (the graft reviewer): every capability
  grown cites the plant evidence that demanded it, every MERGE is the
  smallest re-integration, every refreshed page serves a used dependency,
  no artifact lands without a consumer. Over-delivery is a finding, not a
  bonus.
- Pure-graph integrity (the rebalance gate): the plant ends the
  graft at least as purely a graph as the seed's spec requires; no
  machinery outside a node, no duplicate home, no drifted projection, no
  unlisted residue. Any residual drift is surfaced with a remediation.
- Cross-author rebalance (only if reconciliation/growth/rebalance/(f)
  used parallel authors): run **one** final docs-librarian spawn to
  catch one-home-per-fact violations across author boundaries, register
  drift, and a stale shared summary file; follow with a structural audit
  (right `kind`, topology map lists every added node, `requires:`/`peers:`
  edges reflect the body). A green `graph-lint` proves well-formedness,
  not that a parallel absorption reconciled correctly.
- Stamp + provenance: record the seed version the plant now carries
  in its seed stamp, and add a provenance entry to the plant's own
  `docs/graph/changelog.md`; each check names its command and result.

**Phase 8: Deliver (propose, then ratify).** Graft **proposes**; the
plant's steward **ratifies**. Emit the reconciled upgrade as a reviewable
patch/proposal, hand the KEEP-PLANT divergences back as harvest
candidates, and end with the single highest-leverage next step.

### Provenance & the seed stamp

Graft reads and maintains a lightweight, **plant-owned** stamp (a
`.cypress/seed.json` marker or equivalent) recording the seed name, the
version last grown-or-grafted in, and the date. On the first graft of a
plant grown before stamps existed, reconstruct the base, then establish
the stamp. The stamp is provenance the plant owns, not machinery the seed
overwrites; graft updates it as the last additive step of a successful
upgrade.

### Relationship to grow, harvest, and canonize

- `grow` installs a **new** plant; graft upgrades an **existing** one.
- `harvest` is inbound (plant → seed); `graft` is outbound (seed →
  plant). They share the corpus withdraw contract from opposite ends; a
  KEEP-PLANT divergence graft finds is precisely a harvest candidate.
- `canonize` keeps the plant's **project-specific** knowledge; graft
  never disturbs it. When graft refreshes a library/tool surface, it
  renews the orientation layer canonize and ingest-library maintain and
  leaves every pinned fact in place.

### Scope

Graft writes only the plant's seed-owned machinery and the refreshed
surfaces above. The plant's application source, builds and test suites
stay the plant's; Git state is recorded as provenance only, and graft
never fetches, switches, commits or pushes. A divergence worth flowing
back to the seed is handed to `harvest`, and a three-way conflict goes to
the steward as a decision.

---

## Cross-references at a glance

- Kernel eight rules → owning node: 3.1 specify (`rule.spec`),
  3.2 context-router (`rule.knowledge`, a SKILL node), 3.3 grill
  (`rule.grill`), 3.4 test-first (`rule.test-first`), 3.5 verify
  (`rule.verify`), 3.6 deliver (`rule.deliver`), 3.7 canonize
  (`rule.canonize`), 3.8 toolcraft (`rule.toolcraft`, a SKILL node —
  `skill.toolcraft`; there is no toolcraft protocol). Six of the eight are
  owned by protocols and two by skills, which is why this list says "owning
  node".
- The delivery funnel: brainstorm* → specify → grill →
  ingest-library* → test-first → verify → canonize →
  deliver; recover on any failure.
- The seed meta-loop: grow (seed → new plant), harvest (mature plant
  → seed, started by the user), graft (enriched seed → existing plant,
  started by the user), initialize (the entry fork → grow or from-scratch).

*End of protocols reference. Every fact above is drawn from the files in
`protocols/*.md`, the support tools they name under `tools/`, and the
kernel `core/AGENTS.md`.*
