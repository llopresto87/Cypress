# CYPRESS Protocols Reference

This document is a complete reference for the 15 protocol nodes of the
CYPRESS seed. Each protocol is a routable graph node. It lives as a
plain Markdown file with YAML frontmatter in `protocols/`. When a plant
is grown, these files install into `docs/graph/protocols/`.

Source of this reference: every file in `protocols/*.md`, read directly
from disk. The default-sequence and tier facts are cited from
`core/AGENTS.md` (the kernel).

A protocol node is the entry point for a kind of work. The kernel rule
(`core/AGENTS.md` §2) says: "State which protocol you are entering
before you begin." The router maps *where the work stands* to a
`protocol.*` node.

---

## Summary table

All 15 protocols are tier 2 nodes with `origin: seed`, `kind: protocol`.

| Protocol | id | owns (facts) | requires | peers | est_tokens |
|----------|----|--------------|----------|-------|-----------|
| brainstorm | `protocol.brainstorm` | `brainstorm.entry-and-exit`, `brainstorm.output-landing` | `skill.brainstorm-socratic` | specify, grill, from-scratch | 400 |
| specify | `protocol.specify` | `rule.spec`, `specify.flow`, `specify.revision-discipline` | — | brainstorm, grill | 1500 |
| grill | `protocol.grill` | `rule.grill`, `grill.flow`, `grill.increment-shape` | — | specify, test-first | 1200 |
| test-first | `protocol.test-first` | `rule.test-first`, `test-first.cycle`, `test-first.characterize-first` | — | verify, specify, skill.test-first, skill.holistic-editing | 2300 |
| verify | `protocol.verify` | `rule.verify`, `verify.gate-states`, `verify.risk-depth` | — | test-first, recover, skill.validate-knowledge | 2100 |
| recover | `protocol.recover` | `recover.failure-classes`, `recover.three-attempt-boundary` | — | deliver, grill | 1150 |
| canonize | `protocol.canonize` | `rule.canonize`, `canonize.close-out-flow` | `protocol.toolcraft` | deliver, harvest | 1300 |
| toolcraft | `protocol.toolcraft` | `rule.toolcraft`, `toolcraft.durability-criteria` | — | canonize, grill, harvest | 1000 |
| deliver | `protocol.deliver` | `rule.deliver`, `deliver.forms`, `deliver.attribution-assertion` | — | canonize, recover | 1450 |
| ingest-library | `protocol.ingest-library` | `ingest-library.flow`, `ingest-library.corpus-first` | — | harvest, skill.library-wiki, skill.research-and-ingest | 1200 |
| from-scratch | `protocol.from-scratch` | `from-scratch.phases` | — | brainstorm, ingest-library, skill.from-scratch-bootstrap | 1300 |
| grow | `protocol.grow` | `grow.worker-topology`, `grow.growth-flow`, `grow.completeness-contract` | — | harvest, graft, initialize, ingest-library, canonize | 4500 |
| harvest | `protocol.harvest` | `harvest.fold-back-flow`, `harvest.agnosticism-gate` | — | graft, grow | 7000 |
| graft | `protocol.graft` | `graft.reconcile-flow`, `graft.user-sovereignty`, `graft.pure-graph-mandate` | — | harvest, grow | 9790 |
| initialize | `protocol.initialize` | `initialize.adapter-edges` | `protocol.grow` | — | 230 |

Eight of the protocols also own one of the kernel's eight `rule.*`
facts: `rule.spec` (specify), `rule.grill` (grill), `rule.test-first`
(test-first), `rule.verify` (verify), `rule.deliver` (deliver),
`rule.canonize` (canonize), `rule.toolcraft` (toolcraft). The kernel
keeps only the one-line §3.x anchors; the depth lives in the protocol
node.

---

## The default T3 sequence and how protocols chain

Source: `core/AGENTS.md` §0 (tier table) and §2 (protocol entry).

The kernel defines four work tiers:

| Tier | What it is | How it runs |
|------|-----------|-------------|
| T0 | a question — nothing changes | read minimal nodes, answer with citations |
| T1 | a trivial edit, no behavior/contract/spec surface | edit in-session; one focused gate |
| T2 | a bounded change already authorized by an active spec + plan | minimal worker set + close-out |
| T3 | new/changed behavior, architecture, contracts, dependencies, ambiguity — and anything no other row covers | full funnel, all doing delegated |

Hard edges (kernel): if an edit *could* alter behavior, an interface, a
persisted format, or security posture, it is not T1. No covering spec
means T3, however small it looks.

The **default T3 sequence** (kernel §2), verbatim:

> brainstorm\* → specify → grill → ingest-library\* → test-first →
> verify → canonize → deliver (implementation lives inside test-first's GREEN phase).
> On any failure: `protocol.recover`. `harvest` and `graft` are
> user-sovereign — never enter them unprompted.

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

# Per-protocol reference

The protocols below are grouped by role: the core delivery funnel
(brainstorm → specify → grill → test-first → verify), the close-out and
handoff protocols (recover, canonize, toolcraft, deliver), the
dependency and bootstrap protocols (ingest-library, from-scratch), and
the seed meta-loop (grow, harvest, graft, initialize).

---

## brainstorm

*Source: `protocols/brainstorm.md`*

- **id:** `protocol.brainstorm`, tier 2
- **owns:** `brainstorm.entry-and-exit`, `brainstorm.output-landing`
- **requires:** `skill.brainstorm-socratic`
- **peers:** `protocol.specify`, `protocol.grill`, `protocol.from-scratch`
- **load_when:** "goal is vague, build me a thing"; "stakeholders
  disagree about scope"; "what should we actually build, converge the
  idea"; "problem statement, first useful slice"

### What it does

Use brainstorm when the goal is vague, contested, or under-specified.
The deliverable is a precise problem statement, a primary user, a first
useful slice, the constraints, and a shaped set of options. You do not
write code and you do not pick a stack in brainstorm; you converge.

### Entry conditions

One or more of:
- The user said "build me a thing", "we should look into X", "what if
  we did Y", or otherwise expressed a goal without a defined outcome.
- The goal mentions a verb but not the user.
- The goal mentions the user but not the outcome.
- The team has competing visions for the goal.

### The technique

The questioning technique itself is **not** owned here. It lives in the
skill `docs/graph/skills/brainstorm-socratic.md`: question selection,
one-to-three-questions-per-turn pacing, the reflect-every-two-answers
cadence, the nine-question hard cap, the eight-point convergence
checklist, and the questioning anti-patterns. This protocol owns only
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
- **peers:** `protocol.brainstorm`, `protocol.grill`
- **artifacts:** `templates/spec.template.md`,
  `templates/knowledge-graph/spec-lint.py`
- **load_when:** "write a spec, no spec covers this behavior"; "new
  feature, endpoint, job, or LLM interaction to define"; "changing an
  existing feature's contract"; "bug revealed an implicit or missing
  contract"; "acceptance criteria, Given/When/Then, failure modes"

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
forward. If wiki and spec disagree about how a library *can* be used,
the wiki is right; if product and spec disagree about what to build,
fix the spec.

### Entry conditions

One of: `brainstorm` converged on a first useful slice; an existing
feature's contract is changing; a bug investigation revealed an
incomplete or wrong spec; an ADR introduces a new behavior.

### The pass (`specify.flow`)

A phase table with a named owner per phase; **the table is the spawn
order** — a phase's spawn is issued only after every handback it needs
has returned, and two phases run side by side only where the table says
so (`delegation.sequencing`). Spawned, clean-context work: if the host
cannot spawn the required model classes, stop and report; a missing
*type* is `delegation.harness-registration`, not a stop.

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | identifier; §0 §1 §2 | orchestrator | the goal | — |
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
signed draft is what `grill` plans against.

### Revising an existing spec

Decide clarification vs change. Clarifications edit in place with a §12
row; changes copy to a new identifier, mark the old `superseded` with a
link forward, and update everything that depended on it. Specs never
silently change behavior.

### Exit conditions

"Populated" = content or an explicit `not applicable — <reason>`. The
file exists, populated, `draft` with product ✓ architect ✓ tester ✓
(security ✓ where reviewed) in §0; every §4 contract has a §10 row;
every §9 criterion maps to a real slug; §11 is empty or flagged in
grill.md §12; grill.md links the spec from §3 and §9;
`python3 docs/graph/spec-lint.py` exits 0 (the shape checks,
mechanically, for every spec on disk).

### Anti-patterns

The spec is the README; the spec describes the implementation; no
failure modes; no examples; spec written after the code (mark it
`back-written`); **§9 written beside §3** (a criterion mapping to slugs
that did not exist yet); **promoted at sign-off** (an `active` spec with
no test is a red gate for the whole test-first phase and a false green
the moment someone silences it).

## grill

*Source: `protocols/grill.md`*

- **id:** `protocol.grill`, tier 2
- **owns:** `rule.grill`, `grill.flow`, `grill.revise`,
  `grill.increment-shape`, `grill.press`, `grill.legal-checkpoint`
- **requires:** —
- **peers:** `protocol.specify`, `protocol.test-first`,
  `agent.devils-advocate`
- **artifacts:** `templates/grill.template.md`,
  `templates/knowledge-graph/grill-lint.py`
- **load_when:** "plan the implementation, plan-of-record, grill.md";
  "spec exists but no plan implements it"; "scope an increment, slice
  the work"; "an increment shipped, revise the plan, record what
  happened"; "plan is stale, assumption broke, architecture change"

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
assumption breaks. Append to its changelog; strike through stale
claims, never silently rewrite. Its gate is
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
order.** A phase's spawn is issued only after every handback it needs
has returned, and two phases run side by side only where the table says
so (`delegation.sequencing`). The §15 entry lists the pass's spawns by
`spawn_id` in issue order.

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | §0 | orchestrator | — | — |
| 1 | §2 §3 §4 | orchestrator | §0 | — |
| 2 | §1 | orchestrator (router-bounded reads); a sonnet investigation beyond | §2–§4 | — |
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
behavior added, the gate, the rollback path, effort, and `Depends on:`
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

### Anti-patterns

A §1 line with no path; a §5 silent about a page §9 depends on (the
lint catches the silence, only you catch an unearned "no research
needed"); spawning across a dependency edge because the list looked
flat; ten-file increments; "manageable" risks; a next step that is a
list; a plan with no spec link.

## test-first

*Source: `protocols/test-first.md`*

- **id:** `protocol.test-first`, tier 2
- **owns:** `rule.test-first`, `test-first.cycle`,
  `test-first.characterize-first`
- **requires:** —
- **peers:** `protocol.verify`, `protocol.specify`, `skill.test-first`,
  `skill.holistic-editing`
- **load_when:** "about to write or change production code"; "RED GREEN
  REFACTOR, failing test first, TDD"; "bug fix, regression test";
  "legacy code with no tests, characterization test"; "pure refactor,
  migration safety"

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
sign-offs is enough to encode; T2 needs it `active`); grill.md §9 names
the increments in dependency order, `grill-lint.py` green; the
libraries are wikified. Missing one → back up to the protocol that
produces it.

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
(`delegation.sequencing`).

| Phase | Owner | Needs | Hands back |
|---|---|---|---|
| RED | `tester` | §9 row, contract text, target test paths | failing tests, right reason; §10 rows `red` |
| GREEN → REFACTOR | `implementer` | the RED handback | green, integrated diff; affected gates run; §10 rows `green` |
| REVIEW | `reviewer` | the diff, the §9 row | severity findings; Critical/Major → `implementer` once more, an attempt under `recover` |
| COMMIT | the session | a clean review | grill.md §15 entry with the `spawn_id`s in order; the commit; the spec's status advanced |

The one merge the tiers allow: a T2 single-contract increment with a
mechanical RED is briefed whole to `implementer`; the REVIEW spawn stays
independent. Workers report in the handback; the session writes
grill.md.

- **RED**: identify the contracts; write tests named for them; confirm
  they fail because the *behavior* is missing (not an import or a
  name); if RED for the right reason is unreachable, the test or the
  contract is wrong. Inherited green suites are proven by mutation
  before they are trusted.
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
RED → fix → the test stays forever; a missing contract goes back to
`specify`; a confirmed-but-unfixable bug is an intentionally failing
named test). Pure refactors (existing tests green before and after; a
break means a behavior change or a test of implementation). Migration
safety gate (an unguarded schema is a blocking finding first). Recorded
exceptions (throwaway prototypes, pure configuration, type-only changes,
generated code) — each in grill.md §9 with a rationale and a date.

### Exit conditions

Every contract for the increment has a passing test named for it; the
suite is green; the increment's gate ran and the full `verify` pass ran
before close-out; the review is clean; grill.md §15 carries the
increment with its `spawn_id`s, spec §10 carries the tests, the spec's
status is `active` (or `implemented`); `spec-lint.py` and
`grill-lint.py` exit 0.

### Anti-patterns

Tests written after the code; tests that pass without the code present
(or a gate phase that would pass against the pre-change code); one
giant test per increment; testing through the wrong level; mocking the
object under test; **a worker writing grill.md** (§15 is the session's
trace of what it spawned); assuming dev-machine green means CI green.

## verify

*Source: `protocols/verify.md`*

- **id:** `protocol.verify`, tier 2
- **owns:** `rule.verify`, `verify.gate-states`, `verify.risk-depth`
- **requires:** —
- **peers:** `protocol.test-first`, `protocol.recover`, `skill.validate-knowledge`
- **load_when:** "increment done, ready to merge or deploy"; "which
  gates to run, verification runbook"; "tests pass but is it verified,
  green lie"; "refactor or migration must preserve behavior"; "record a
  missing or skipped gate"

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
the runbook entry is part of that worker's write scope. The grill.md
§15 record (step 8) is the session's; the plan-of-record is a
session-owned operational artifact.

### The gate menu

Select the gates that apply. Use the lowest level that catches the bug
you care about; do not run every gate on every change. The full table:

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
Plan-of-record lint (grill.md out of shape — dependency order, §5
derived from §9, plan↔spec alignment; `python3 docs/graph/grill-lint.py`);
Manual review (non-automatable judgment).

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

Escalate one row the moment a "local" change turns out to touch a
shared surface. Never run the broad battery on a provably local change
out of ritual; wall-clock and attention are budget too.

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

Report every gate as exactly one of three states; silence must never
imply a pass:

- executed: actually run this pass, with command and result. If it
  fails, fix the increment or hand it back; do not record a fake PASS.
- discovered: known to exist (read in source/config) but not run
  this pass. Record it "DISCOVERED, not run (date) — reason" so it can
  never be mistaken for an executed pass.
- absent: does not exist yet. Record it with a date, a reason, and
  the owner who will add it.

Adopting a codebase with no gate infrastructure is not an excuse to
leave the runbook empty: record each standard gate explicitly as
`absent (YYYY-MM-DD) — <reason>`. A blank verification runbook is
indistinguishable from one nobody checked.

**The green-lie clause.** The three states are honest only if an
executed PASS means something. A test command with no tests, a linter
over an empty set, a type check with everything untyped: these "pass"
and mean nothing. Do not cite a vacuous pass; do not wire such a gate
into CI. Land the real check first, then add the gate in a later
increment, never both in the same one. A gate that executes and
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

### Adding a new gate

If verification reveals a bug no existing gate would have caught: pick
the lowest level that catches it; get a RED test case that reproduces
it; add it to the verification runbook in the same increment; add it to
CI in the next reliability-owned increment.

### Behavior-preserving changes (refactors, migrations, dependency bumps)

"It builds and the tests pass" is not the gate; **unchanged behavior**
is. Two disciplines:
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

### Tolerating a known defect (the self-expiring exception)

When a suite must pass while a confirmed bug still lives, do not weaken
or skip the gate. Assert today's broken behavior on purpose under a
named marker (`KNOWN_BUG_<id>`) and record the trigger that should
tighten it (e.g. "accept a 500 until the auth bug is fixed → then
require 401"). The assertion passes while the bug lives and flips to
FAIL the moment the bug is fixed without the assertion being tightened,
so the debt is mechanically visible and self-retiring.

### Anti-patterns

- "All gates green, but I disabled the flaky one."
- "Tests pass locally, didn't run them in CI." If the gate isn't in
  CI, it isn't a gate; it's a hope.
- "We don't have time for the eval suite this increment." That is the
  signal to merge a smaller increment, not to skip the gate.

---

## recover

*Source: `protocols/recover.md`*

- **id:** `protocol.recover`, tier 2
- **owns:** `recover.failure-classes`, `recover.three-attempt-boundary`
- **requires:** —
- **peers:** `protocol.deliver`, `protocol.grill`
- **load_when:** "a worker or gate failed, what now"; "retry or
  re-route, flaky failure"; "delegation came back wrong or ambiguous";
  "gate red twice on the same increment"

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
| **Deterministic** | Same input reliably produces the same failure: compile error, failing assertion, lint, schema rejection | **Never retry unchanged.** Change the input (code, test, config) and re-run. |
| **Capability** | The worker is the wrong instrument: wrong specialist, missing expertise, out-of-domain handback, LOW/NONE route band in hindsight | Re-route: run `agent-lint --route` with a *sharper* task statement, written in the domain's own words so it also composes the expertise the worker lacked. A knowledge gap closes as an `expertise.*` node; commission an agent only when the work needs its own tools, model class, stance, or isolation (kernel §1). Do not re-brief the same agent harder. |
| **Ambiguity** | The worker asked the brief a question, guessed, or two artifacts contradict (spec vs code, plan vs node) | Fix the **cheapest upstream artifact that owns the confusion** — brief first, then plan (grill §), then spec — and re-delegate. Widening context is not the fix. |
| **Systemic** | The harness or system itself: wedged delegation, depth cap hit, missing tool, broken gate infrastructure | Stop the line. Record in grill.md §12 and report to the human with the exact evidence. No workaround that hides it. |
| **Unregistered** | The specialist exists on disk but the host has no such type: the session predates the projection, or it is rooted at the seed rather than the plant. Reads like Systemic — it is not. | Apply `delegation.harness-registration`: preflight, re-enter rooted at the plant, or role-emulate **and record it**. Do not stop the line, and do not commission a second definition. |

An intermittent or probabilistic failure is confirmed **fixed** only on
mechanism-level evidence (a trace proving the causal path is genuinely
absent), never on a lower observed failure rate. Any incidental change
that reduces *exposure* to the defect buys a better rate while fixing
nothing. Corollary: sequence any exposure-reducing change **after** the
diagnostic evidence is captured, never before.

### The three-attempt boundary (`recover.three-attempt-boundary`)

Across ALL strategies combined, a unit of work gets **three attempts**.
The fourth move is always escalation: record the failure-class history
in grill.md §12, mark the increment WIP in the delivery, and hand the
decision to the human with the evidence: never a fourth quiet attempt,
never a fallback chain that consumes growing resources on a falling
probability of success.

### Gate-failure rule

A gate that fails **twice on the same increment** is telling you the
increment is wrong-sized or the plan is wrong. Reopen `grill`, split or
rescope the increment, and come back through `test-first`. Hammering a
red gate is the deterministic-retry anti-pattern wearing a uniform.

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
- No silent downgrades: substituting a weaker gate, a smaller scope, or
  a different specialist *is a plan change* and lands in grill.md.

### What you do not do

- Retry a deterministic failure without changing the input.
- Exceed two as-is retries for a transient failure.
- Re-brief the same specialist harder when the class is capability.
- Widen context to cure ambiguity.
- Work around a systemic failure quietly.
- Make a fourth attempt.

---

## canonize

*Source: `protocols/canonize.md`*

- **id:** `protocol.canonize`, tier 2
- **owns:** `rule.canonize`, `canonize.close-out-flow`
- **requires:** `protocol.toolcraft`
- **peers:** `protocol.deliver`, `protocol.harvest`
- **load_when:** "task is finishing, close out, before deliver";
  "persist what we learned into the graph"; "spawn the docs-librarian,
  canonize"; "catalog a tool or skill the work produced"

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
same bootstrap and lint run would be pure coordination waste.

The librarian owns the graph's **fact-bearing surfaces** (nodes, wiki
pages, the tool catalog) and one-home-per-fact; the session never
edits those. The session-owned operational artifacts under the same
root (grill.md, the verification runbook, changelog.md) are the
deliberate exception: the session writes them directly.

### When to invoke

- At the completion of every Tier 2/3 task or increment, before
  `deliver`.
- Whenever the work surfaced a fact the graph does not own,
  contradicted one it does, or produced a tool a future session will
  run again.
- Tier 0/1 shortcut: a question answered or a trivial
  non-behavioral edit needs no spawn. The session writes one line in
  the delivery, "canonize: nothing of interest / no tool, because …",
  and that satisfies the fail-closed doctrine. If a T0/T1 task *did*
  surface something durable, it escalates: spawn the librarian.

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

Neither list includes: ephemeral scratch, secrets/credentials,
production or personal data, speculation (write "not recorded"),
project-specific material aimed at the seed (that is `harvest`'s
agnosticism gate), throwaway prototypes or genuine one-offs.

### The flow — one spawn (`canonize.close-out-flow`)

1. Assemble candidates from the finished work and the workers'
   handback payloads: facts with evidence, tools with path + entry
   point + invocation + covering test.
2. Spawn the docs-librarian once (Opus-class; it owns
   `docs/graph/`) with a brief embedding the canonical block from
   `docs/graph/templates/prompts/graph-session-bootstrap.md` plus both
   candidate lists. This spawn is fail-closed. If the host has no such
   type, apply `delegation.harness-registration`; skipping the
   close-out because the type would not resolve is not an option.
3. The librarian persists and catalogs in one pass. Each fact lands
   in exactly one node's `owns:` (dedupe: update, don't duplicate);
   each tool gets `tool-page.template.md` filled into
   `docs/graph/tools/<name>.md` plus an index row and an `artifacts:`
   edge (checking `tool-corpus/` first where the corpus is available);
   each recurring procedure gets `skill.template.md` filled into its home
   node `docs/graph/skills/<name>.md` plus the projection in each harness
   dir the plant uses (checking `skill-corpus/` first where available,
   deduping, composing existing disciplines by reference); failed
   `load_when:` triggers are sharpened. Every node body, runbook, or
   README paragraph the librarian writes or refreshes this spawn gets a
   prose pass: `humanizer` in file mode, then `python3
   docs/graph/prose-lint.py --file <path> --against HEAD` before the
   graph-lint pass. One `graph-lint` run confirms the graph stays clean.
4. Confirm or record-empty. The librarian hands back nodes/fact-keys
   touched and tool cards written, or an explicit "nothing of interest,
   because …" / "no durable tool, because …", with the lint result.

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
  user-triggered only; canonize keeps **project-specific** knowledge in
  the plant. What harvest's agnosticism gate rejects still belongs here.

### What you do not do

- Close a T2/T3 task without the librarian spawn, or skip the T0/T1
  self-record line "because it was minor".
- Spawn the librarian twice for one task's close-out.
- Write the graph's fact-bearing surfaces from the main session.
- Canonize secrets, production data, or speculation.
- Duplicate a fact or tool card that already has a home: update it in
  place.

---

## toolcraft

*Source: `protocols/toolcraft.md`*

- **id:** `protocol.toolcraft`, tier 2 (note: no `command: true`)
- **owns:** `rule.toolcraft`, `toolcraft.durability-criteria`
- **requires:** —
- **peers:** `protocol.canonize`, `protocol.grill`, `protocol.harvest`
- **load_when:** "should this script be kept, is this a durable tool";
  "recurring operation across sessions"; "catalog a tool, tools_built,
  skills_built"; "throwaway prototype versus reusable tooling"

### What it does

Toolcraft is the doctrine (kernel §3.8) of durable, tested, cataloged
tools versus throwaway scripts. This node owns **the toolcraft rule**
(`rule.toolcraft`): durable tools compound; throwaway scripts are
rework. When an operation will recur across independent sessions, the
unit of work is a **durable, tested tool** with a stable interface,
designed so at plan time, named in `tools_built` on every handback, and
cataloged in `docs/graph/tools/` by the librarian inside the close-out
spawn. Genuine one-offs and throwaway prototypes stay disposable.

**This file owns the doctrine only.** The execution (cataloging the tool)
happens inside the single close-out spawn defined in
`docs/graph/protocols/canonize.md`, in the same librarian brief that
persists the task's knowledge. There is no separate toolcraft spawn.

### What counts as a durable tool (`toolcraft.durability-criteria`)

Catalog a piece of real code that:
- recurs across independent sessions: an agent, expert, or skill
  will plausibly run it again (the trigger is recurrence, not size);
- has a stable interface: a named entry point, defined inputs and
  outputs, a documented invocation, not a copy-pasted snippet;
- is authorized by a test (§3.4): at least one test pins what it
  does, so a future session can trust and change it safely;
- lives in the repository, committed where the project keeps its
  tooling, reachable by path.

### What stays disposable

- a genuine one-off: needed once, no future task plausibly repeats
  it;
- a throwaway prototype to learn a library or shape, the blessed
  carve-out of the test-first rule; recorded, if anywhere, as an
  exception in grill.md §9;
- anything embedding secrets, credentials, or production/personal data;
- project-specific tooling aimed at the seed; that is `harvest`'s
  agnosticism gate.

### The procedure sibling — durable skills

A tool is durable *code*; a **skill** is a durable *procedure*: the
disciplined sequence for a recurring kind of work (a migration recipe,
a release choreography, a data-reset dance). Same recurrence trigger,
different shape: if the recurring thing is code that runs, it is a tool;
if it is the *how*, it is a skill. When such a procedure recurs and no
core `docs/graph/skills/` discipline covers it, author it as a project
skill from the template. Its home is the graph node
`docs/graph/skills/<name>.md`; the projection is also created in each
harness dir the plant actually uses (`.claude/skills/<name>/SKILL.md` and
kin), because `install.sh` projects only the seed's own skills. It
**composes** disciplines by reference, never restating them.

### Design-time half of the rule

The doctrine cuts earlier than task end: when `grill` identifies a
recurring operation, the plan-of-record names a durable tool (or a
project skill, if the recurring thing is a procedure) as the unit of
work; the capability is *designed* durable, not retrofitted. Workers
name every tool in `tools_built` and every procedure in `skills_built`
in their handback; those fields are what the close-out brief forwards.

### Fail-closed doctrine

A task is **not complete** until any durable tool it produced is
cataloged and any repeated procedure crystallized into a project skill,
or the close-out has explicitly recorded "no durable tool / no skill,
because …". A task that built a reusable capability but left it
uncaptured is a silent capability leak.

Cross-project mirror: `harvest` folds **project-agnostic** tools into
the seed's `tool-corpus/` and **project-agnostic** skills into
`skill-corpus/`, user-triggered only.

---

## deliver

*Source: `protocols/deliver.md`*

- **id:** `protocol.deliver`, tier 2
- **owns:** `rule.deliver`, `deliver.forms`, `deliver.attribution-assertion`
- **requires:** —
- **peers:** `protocol.canonize`, `protocol.recover`
- **load_when:** "session is ending, wrap up, hand off"; "delivery
  summary, cold pickup"; "what did we change, session report";
  "attribution, produced_by, routing evidence"

### What it does

Every session ends with delivery. The deliverable is a concise summary
that lets another agent (or the same agent next time) pick the project
up cold. This node owns **the deliver rule** (`rule.deliver`): every
session ends with a delivery, compact for T0/T1, full for T2/T3: files
changed, routing attribution, docs updated, decisions, gates with
outcomes, limitations, and **one** recommended next step. The
deliver-time attribution assertion is fail-closed: a unit of work with
no `produced_by` is a BLOCK. A session without a delivery summary is
paused, not finished; never skip this protocol.

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
Documentation created or updated; Key decisions; Gates run (PASS / FAIL
/ SKIPPED with reason); Known limitations; Session metrics; Recommended
next step.

The **Session metrics** block is five lines of telemetry, not prose:
Tier (with any reclassification), Spawns, Route bands + overrides,
Retries by class (per `recover`), Gates run/failed-then-fixed. This is
what lets the system improve on evidence instead of anecdote: `harvest`
aggregates these across deliveries to find *systemic* seed problems:
recurring misroutes mean a specialist's `routing_triggers` need
sharpening, frequent tier reclassifications mean the tier edges need
tuning, repeated transient retries in one area is a reliability signal.

### Quality bar

A delivery that passes names every changed file; names every
documentation update with its location; cites verification outcomes (no
hand-waving); lists every limitation explicitly; recommends exactly one
next step; reads as the writer, in that the full-form summary and any
pull-request description or commit message pass the `humanizer` skill in
embedded mode with no strong tell from `docs/graph/prose-lint.py`; and is
the smallest summary that permits correct use and appropriate trust (material caveats in, process narration out;
proportionate communication). A delivery that fails says "implemented
X" without naming files, "tests pass" without naming gates, "do
whatever feels right" or five options, hides limitations behind
optimism, or pads the record with narration the next session must
filter out.

### Routing-attribution assertion (fail-closed) (`deliver.attribution-assertion`)

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

This assertion runs in the top session at `deliver`, the one place a
hook can reach, since subagent hooks do not fire. A top-session Stop
hook that greps the delivery for attributions stays **deliberately
unwired until this plant's real deliveries carry `produced_by`** (a
gate landed before the thing it checks either checks nothing or blocks
everything; kernel §3.5, the green-lie rule). Once deliveries carry the
field, wire it warn-first, then block.

### The cold-pickup test

The standard for "is this delivery complete?": another senior engineer,
with no context except the repository and the delivery summary, should
be able to (1) run the project locally, (2) run the verification gates,
(3) find the current plan-of-record, (4) know the next step. If they
can't, the delivery isn't done.

### What you do not do

- Deliver with red tests, undeclared.
- Use the compact form for work that changed behavior, contracts, or
  spec-covered code.
- Deliver with libraries used but not wikified.
- Deliver a unit of work with no `produced_by`.
- Deliver without updating grill.md.
- Deliver a half-finished increment as done: mark it WIP and recommend
  resuming it as the next step.

---

## ingest-library

*Source: `protocols/ingest-library.md`*

- **id:** `protocol.ingest-library`, tier 2
- **owns:** `ingest-library.flow`, `ingest-library.refresh`,
  `ingest-library.corpus-first`
- **requires:** —
- **peers:** `protocol.harvest`, `skill.library-wiki`,
  `skill.research-and-ingest`
- **artifacts:** `templates/library-page.template.md`,
  `templates/knowledge-graph/graph-lint.py`
- **load_when:** "adding a new dependency, library, SDK, or API"; "no
  wiki page for a library the code uses"; "version pin changed, refresh
  the library page"; "security advisory on a dependency"

### What it does

The core wiki-building flow: a complete, version-pinned page in
`docs/graph/libraries/<name>.md`, registered in `libraries/index.md`,
with raw and normalized sources on disk — built BEFORE any code touches
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

### When not to use it

Trivial transitive dependencies (wikify what you import); platform
features of the runtime itself (those go in
`best-practices/engineering.md`).

## from-scratch

*Source: `protocols/from-scratch.md`*

- **id:** `protocol.from-scratch`, tier 2
- **owns:** `from-scratch.phases`
- **requires:** —
- **peers:** `protocol.brainstorm`, `protocol.grill`,
  `protocol.ingest-library`, `protocol.canonize`,
  `skill.from-scratch-bootstrap`
- **load_when:** "start a new project, empty repo"; "greenfield,
  bootstrap from nothing"; "no grill.md exists yet, day one setup";
  "project skeleton, verification baseline"

### What it does

Turns a goal into a project another agent can pick up cold, through
nine phases that each adopt a sub-protocol carrying its own owners and
failure modes — read the phase's protocol, never a summary. **The table
is the spawn order.**

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

### Common ways to fail it

Owned by `skill.from-scratch-bootstrap` (`from-scratch-bootstrap.method`).

## grow

*Source: `protocols/grow.md`*

- **id:** `protocol.grow`, tier 2 (note: no `command: true`)
- **owns:** `grow.worker-topology`, `grow.growth-flow`, `grow.completeness-contract`
- **requires:** —
- **peers:** `protocol.harvest`, `protocol.graft`, `protocol.initialize`,
  `protocol.ingest-library`, `protocol.canonize`
- **load_when:** "grow the knowledge graph, first growth"; "install
  prompt, EXPERT_SEED_INSTALL_PROMPT"; "docs/graph is missing or badly
  drifted"; "regrow or refresh the graph after major drift"

### What it does

Grow is the canonical full-growth workflow: it turns an installed
project-agnostic seed into a complete, source-grounded `docs/graph`
knowledge system. It is invoked by `INSTALL_PROMPT.md` (installed as
`EXPERT_SEED_INSTALL_PROMPT.md`); `docs/graph/protocols/initialize.md`
is only a thin coding-tool adapter back to this file.

The caller is an orchestration chat. It owns user communication,
planning, worker selection, briefing, sequencing, and acceptance. It
does not perform the delegated investigation or authoring itself.

### Mandatory worker topology (`grow.worker-topology`)

1. Spawn clean-context **Sonnet-class** scouts for read-only source
   discovery, partitioned by real subsystem, repository, or evidence
   domain. Use the growth-scout brief, whose collection target IS the
   evidence-ledger schema: demand paths/symbols for every claim. Each
   scout persists ONE ledger per boundary to the plant's gitignored
   seed-organ scratch, `.cypress/growth/<slug>.ledger.md` (never under
   `docs/graph/`; the ledger is growth-time feedstock, not plant
   knowledge).
2. Reconcile the per-boundary ledgers into a coherent evidence set in
   the orchestration plane, cross-referencing the persisted ledgers.
   Resolve contradictions with another bounded scout; do not guess.
3. Spawn Sonnet-class **`research-scout`s** for the external evidence,
   the mandatory flip side of step 1. Mine the reconciled ledgers' §5
   for every architecturally significant / cross-cutting / security- or
   operations-critical dependency, and the evidence set for external
   standards the project is held to; retrieve version-pinned upstream
   docs per `ingest-library` into `docs/graph/sources/`. "Executable
   source is the truth" scopes to claims about this project; a growth
   that spawns only growth-scouts has gathered half its evidence.
4. Spawn **Opus-class** authors for every written artifact or deep
   synthesis, using the growth-author brief that CONSUMES the ledger and
   maps each section to its deliverable: authors build on cited
   evidence, never a fresh reading invented from scratch.
5. Spawn separate **Opus-class** reviewers/validators for graph
   integrity, source fidelity, navigation, and false-premise rejection.
6. Route each finding back to a bounded Opus author, then revalidate.

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
no `Task` tool: at an out-of-domain boundary they STOP and return the
handback payload naming the next specialist. Every worker ends its turn
with a payload carrying `produced_by` and `route_evidence`.

Two host conditions look alike and only one is fatal. If the host
cannot spawn clean-context workers with selectable model classes, stop
and report that this host cannot execute the seed's operating model;
do not silently collapse delegated work into the main chat. If it can
spawn but a named specialist is **not registered as a spawnable type** (the
ordinary state of the session that just installed the roster), that is
*not* fatal: preflight and apply `delegation.harness-registration`.

### Boundaries

- Executable source is primary evidence (manifests, entry points,
  routes, models, migrations, config, deploy descriptors, tests, CI,
  prompts, evaluations). Existing prose is clues only; corroborate.
- That rule scopes to claims **about this project**: for what a
  dependency or external standard *is*, upstream documentation fetched
  by `research-scout` is primary. Web retrieval is in scope for growth;
  Git publishing is not.
- Preserve target-owned files; knowledge writes stay under
  `docs/graph/`.
- Do not change application code, manifests, CI, infrastructure, or
  tests.
- Growth does not run application builds or test suites; only
  knowledge-only lint/link/route/drift checks.
- Do not fetch, pull, switch, commit, push, or publish Git state (record
  branch and commit as provenance only).
- Never invent behavior, requirements, rationale, ADRs, commands, URLs,
  project skills, or passing status. Mark uncertain claims `unknown` and
  name needed evidence.
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

Growth is **complete or it is not done**. A first growth that stops at
a skeleton (a root node, a router, and a handful of leaves) is a failed
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
the contract forbids. Template files existing at their paths is never
coverage; only authored, source-cited content is.

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

**No early stop.** Growth ends when `growth-audit.py` exits 0, Phase 6's
independent validation passes, and the maturity test is met against the
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
scouting. Settle spawnability here, not in Phase 2. Inventory cheaply
before opening large files; ignore generated/vendor/cache/build dirs.
Identify real subsystem boundaries and assign focused scouts for
cross-cutting evidence (APIs/messages, data/migrations, platform/config,
tests/CI/operations, dependencies, prompts/evaluations). If there is no
executable project evidence, route through `from-scratch` for intent
discovery while retaining this worker/model policy and graph root.

**Phase 2: Scout and establish evidence.** Spawn the planned
Sonnet-class scouts on the growth-scout brief. Each writes ONE ledger to
`.cypress/growth/<slug>.ledger.md` with terse factual claims and exact
paths/symbols for: bootstrap/entry points/packages/imports;
inbound routes/messages/jobs and outbound integrations;
entities/schemas/migrations/persistence; config/secrets
interfaces/deployment/observability; tests/CI/scripts/operational
commands/prompts/evaluations; direct dependencies and evidence of
actual use; and discrepancies between executable source and existing
prose. The persisted per-boundary ledgers ARE the evidence set.
Reconcile across them; resolve contradictions by scoped follow-up
scouting; record which ledger owns each contested fact. Then run the
external pass (topology step 3) before authoring: dispatch
`research-scout`s for every §5-flagged significant dependency and the
external standards the project is held to; record the dispatch list.
Phase 4's `libraries/` rich pages, normative `best-practices/`, and
`sources/` are authored FROM this material, and the coverage record
audits against it. No web retrieval on the host is a named blocker,
never a silent thin index.

**Phase 3: Model and author through Opus workers.** Configure
`ROOT_ID` and `KINDS` in `graph-lint.py`. Brief Opus-class authors on
the growth-author brief, pointing each at the ledgers it reads, the
exact output paths, schema, relevant existing nodes, and exclusive write
scopes. Author: one root node; one node per real subsystem/bounded
capability; shared stack/platform/data/domain/cross-cutting nodes where
they remove duplication or improve routing; a compact Tier-1
task-to-entry router using realistic developer phrases. Each node has
unique `owns`, minimal acyclic `requires`, explicit boundary `peers`,
concrete `load_when`, honest token cost, source paths, and leaf edges.
Never ask two authors to own overlapping facts or files.

**Phase 4: Grow source-backed leaves.** Through bounded Opus authors,
populate every collection supported by evidence: `product/`
(actors/capabilities/flows/constraints/observed behavior);
`architecture/` (context/components/boundaries/runtime flows/dated sharp
edges); `api/` (observed HTTP/RPC/event/job contracts + source
locations); `data/` (entities/ownership/persistence/migrations/
lineage/privacy); `libraries/` (every direct dependency indexed; rich
pages for significant ones, grounded in the retrieved upstream
material; a thin index where §5 flags significant deps is NOT coverage;
smoke tests recorded as pending backfill); `legal/` (only when subject
to externally-authored rules; check `legal-corpus/` first, re-confirm
`verified`/`legal_status` against the publisher); `sources/`
(provenance for THIS growth's research-scout ingests; "no external
information consumed" when none was dispatched is circular and a
completeness defect); `prompts/` and `evaluations/`;
`runbooks/verification.md` (exact
commands, labeled `discovered, not executed`); `plans/grill.md`
(evidence, gaps, next increment); `best-practices/` (**normative**: the
external standard, cited, plus the project's observed stance, not a
description of current habits); `changelog.md`.
Prepare `specs/` and `decisions/` indexes but do not manufacture
records: formalize a spec only from a real observable, an ADR only
from a decision the source shows. Where a ledger's specialist-agent
signal genuinely warrants it, author a project-specific expert agent; a signal
is a candidate, not a mandate.

**Phase 5: Connect and fertilize (the librarian rebalance pass).** A
mandatory named `docs-librarian` dispatch after Phase 4, never skipped
because authors "already linked things": connect every leaf to its
owning node, merge duplicate fact homes, split accreted nodes, delete
pass-throughs, keep searchable paths/symbols/commands in the right home
and the router compact; re-run `graph-lint.py` after rebalancing and
carry the merge/split/move/delete report into the delivery. Depth
belongs behind edges, not in the always-loaded router or oversized
nodes.

**Phase 6: Independent validation.** Dispatch separate Opus reviewers
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
over-growth. Route findings to bounded Opus authors and repeat
validation, **bounded by the recover discipline**: a finding surviving
two author-fix → revalidate rounds is not converging; stop, record it as
an honest unknown or defect, hand the decision to the user. Do not
weaken the linter or loop a fourth time. Also configure the
spec-coverage gate (`TEST_GLOBS` in `spec-lint.py`) while the stack
evidence is fresh.

### Delivery and maturity

Growth closes through `canonize` (§3.7) before reporting, so its own
lessons land in the graph. The orchestration chat reports target
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
is never evidence of maturity.

---

## initialize

*Source: `protocols/initialize.md`*

- **id:** `protocol.initialize`, tier 2
- **owns:** `initialize.adapter-edges`
- **requires:** `protocol.grow`
- **peers:** — (none)
- **load_when:** "/initialize command invoked"; "set up the seed via the
  coding tool"; "dry-run the initialization"

### What it does

`/initialize` is a convenience adapter for Claude Code, Prime Agent,
Codex, opencode, Copilot, and similar coding tools. The primary
tool-neutral entry point is `INSTALL_PROMPT.md`; the canonical workflow
is `docs/graph/protocols/grow.md`. This node is the smallest of the 15
(est_tokens 230) and delegates unchanged to grow.

When invoked, enter the orchestration role and execute the install
prompt and grow protocol without weakening them; the orchestration,
model-class, routing, and evidence policy is grow's and
`INSTALL_PROMPT.md`'s to define, never re-listed here.

### The adapter's own hard edges (`initialize.adapter-edges`)

The adapter adds only these edges of its own:
- the roster this adapter installs is not spawnable in the session that
  installed it; preflight and remedy per
  `delegation.harness-registration` before any by-name dispatch;
- initialization does not run application builds or application test
  suites;
- initialization does not push, fetch, pull, switch, or commit Git;
- it does not modify application code or fabricate normative records.

Support `--dry-run` by performing only orchestration planning and
read-only scouting, then reporting the proposed authoring briefs without
spawning writers. All detailed discovery, authoring, validation, and
maturity criteria are in `grow.md` and the full-growth procedure it
references.

---

## harvest

*Source: `protocols/harvest.md`*

- **id:** `protocol.harvest`, tier 2 (note: no `command: true`)
- **owns:** `harvest.fold-back-flow`, `harvest.agnosticism-gate`
- **requires:** —
- **peers:** `protocol.graft`, `protocol.grow`
- **load_when:** "harvest lessons back into the seed"; "fold
  generalizable improvements upstream"; "the plant is mature, propose a
  harvest"; "seed improvement from project experience"

### What it does

Harvest is the inverse of grow. `grow` runs the seed *into* a project
and grows it; harvest runs the other direction, a mature project *back
into* the seed, so the next project starts ahead of where this one did.
A seed that only seeds cannot improve; a seed that harvests carelessly
rots into one project's specifics. Harvest is the disciplined gate that
lets the seed compound **without** losing its agnosticism. It takes only
the seed-worthy essence of what the plant learned, never the plant's
flesh. What goes back in must be true for *any* future plant.

### Trigger — manual only, never automatic

Harvest is **user-sovereign**. Unlike `canonize`, it is never triggered
automatically, on a schedule, by a hook, or as a "while I'm here" step.
- The user starts it, by invoking this protocol or pasting
  `HARVEST_PROMPT.md`.
- The system may, at most, PROPOSE it: when a mature plant clearly
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

Fail-closed corollary: **if you cannot state the lesson without naming
the plant, it is not ready to harvest.** A single leaked project name,
domain noun, credential, dataset shape, or version-pinned specific in
the seed is a failed harvest, worse than a missed lesson.

*What counts as a project reference* (all forbidden in the seed,
including in the CHANGELOG entry, harvest-log row, provenance notes, and
illustrative examples): a name (plant, product, company, service,
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
clean-context workers survey, triage, and author. Sonnet-class for
read-only survey, Opus-class for every generalization and authoring.

**Phase 1: Survey the mature plant (Sonnet scouts, read-only).**
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

**Phase 2: Triage against all three gates (Opus authors).** For each
candidate, apply agnosticism, durability, and non-redundancy, and decide
KEEP-AS-IS / GENERALIZE / REJECT. For anything kept, write its
**generalized restatement** with the before→after shown (what
plant-specifics *and* pinned specifics were stripped). Reject rows carry
a one-line reason (including "redundant — the seed already owns this at
`<home>`"). Be conservative; when in doubt, reject or generalize
harder.

**Phase 3: Backport authoring (Opus authors).** Apply each surviving
generalized improvement to the SEED artifact it belongs in (`skills/`,
`protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit**, integrated as if
it had always been there. Every fold-back records provenance (plant
lineage, generalization applied, seed files touched). A harvested
tooling fix arrives with its regression test generalized alongside it.

**Phase 4: Seed integrity gate (fail-closed).** The seed must leave
harvest more capable and no less agnostic:
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
uncovered by any base agent. Harvest may *propose* a promotion; it never
performs one.

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

### What you do not do

- Start a harvest on your own (the most an agent does unprompted is
  *propose* one and stop).
- Merge a fold-back the user has not ratified.
- Harvest a plant that is still churning.
- Copy project-specific facts, names, domain terms, stack pins/
  fingerprints, counts, internal names, paths, secrets, or datasets into
  the seed; the agnosticism gate is absolute and applies to every
  committed byte.
- Harvest a self-healing/diagnostic case **narrative**; only its
  generalized prevention rule goes back.
- Harvest the plant's `docs/graph/` content.
- Break the seed's clean install or agnosticism to land a lesson.
- Silently mutate the seed, or fold a change in without provenance and a
  proof.

---

## graft

*Source: `protocols/graft.md`*

- **id:** `protocol.graft`, tier 2 (note: no `command: true`); the
  largest protocol node (est_tokens 9790)
- **owns:** `graft.reconcile-flow`, `graft.user-sovereignty`, `graft.pure-graph-mandate`
- **requires:** —
- **peers:** `protocol.harvest`, `protocol.grow`
- **load_when:** "upgrade this plant to the newer seed"; "graft the
  seed, re-propagate machinery"; "plant grew from an older seed
  version"; "reconcile local machinery divergence"

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

### Trigger — user-decided (`graft.user-sovereignty`)

Like harvest, graft is **user-sovereign**. It changes an established,
possibly production plant, so the **steward** decides when a plant is
upgraded and ratifies before it is applied.
- The user starts it, by invoking this protocol or pasting
  `GRAFT_PROMPT.md` with a plant (or a set of sibling plants).
- The system may PROPOSE it, most naturally as the tail of a
  `harvest`: "the seed now carries fruit that plants X, Y, Z predate —
  each is due for a graft" and stop.
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
  the graph engine scripts `docs/graph/{graph-lint.py,spec-lint.py}`
  (preserving the plant's configured `TEST_GLOBS`). `_schema.md` and `index.md` are
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
> overwrite.

The one nuance: a plant's library and tool **pages** are plant-owned,
yet graft may refresh their *surface* from the enriched corpus (Phase
4), renewing only the version-durable orientation and re-pinning the
plant's version-specific facts fresh. Renewing the orientation is a
graft; overwriting a pin is not.

### The pure-graph mandate (`graft.pure-graph-mandate`)

The rootstock line is graft's conservative heart (*preserve what the
plant authored*); the pure-graph mandate is its reconstructive heart
(*every graft leaves the plant closer to the seed's architecture than it
found it*). The seed's architecture (6.0.0) is a **pure graph**:
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
- base: the seed revision the plant grew from (read from the seed
  stamp; reconstructed from install backups or content lineage on a
  first graft);
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

Orchestrated like grow/harvest; Sonnet-class survey (read-only),
Opus-class for every reconciliation, merge, corpus refresh, and
validation. Every worker runs the plant's router
(`graph-lint.py --plan`) before reading plant source.

**Phase 1: Locate the plant and establish the base (session + Sonnet).**
Identify the plant or sibling set; record path, host integration,
branch, HEAD, worktree cleanliness (provenance, no Git mutation). Read
the plant's **seed stamp**; on a first graft with no stamp, reconstruct
the base from install backups (`*.bak-*`) or content lineage. Confirm
the seed's version and what changed between base and now (its CHANGELOG
and harvest log are the map of available fruit).

**Phase 2: Survey the drift (Sonnet scouts, read-only).** Inventory
every seed-owned artifact and classify its three-way state as a first
guess at FAST-FORWARD / KEEP-PLANT / MERGE. In parallel, inventory the
**fruit the plant can withdraw**: libraries, tools, and legal
instruments the plant reasons against for which the corpus now holds a
page the plant predates or lacks. Return a **graft ledger**, one row
per artifact or withdrawable page.

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
Opus authors to weave into the owning node.

**Phase 3: Reconcile the machinery (Opus authors).** For each
seed-owned artifact apply the three-way reconciliation: adopt on
FAST-FORWARD; retain and raise a harvest candidate on KEEP-PLANT; author
one holistic re-integration on MERGE. Every merged file arrives whole,
never a seed block bolted beside a plant block. **The roster delta is
not spawnable in this session**: preflight and take the remedy
(`delegation.harness-registration`); carry the delta forward as a named
list for Phase 7. **The graph engine is machinery too**: the installer
drops the scaffold only if absent, so a plant that already has them
keeps its OLD engine and misses every linter improvement. Reconcile the
engine as a config-preserving fast-forward: adopt the seed's current
engine body and re-inject the plant's PROJECT CONFIG (`ROOT_ID` /
`KINDS` / `KIND_PREFIX` in `graph-lint.py`; `TEST_GLOBS` in
`spec-lint.py`). A config knob the seed has *extended* is **UNIONED**,
not re-injected wholesale; the load-bearing case is `KINDS` (6.0.0
added `protocol`/`skill`/`agent`/`method`; keeping the plant's older set
verbatim would fail every new machinery node with `kind not in KINDS`).
`tools/graft-graph-engine.py` performs this merge.
`_schema.md`/`index.md` stay the plant's (project-instantiated). **The
installer fast-forwards blindly**: a mandatory post-FF audit (Phase 7,
`tools/graft-audit.py`) catches any local divergence a blind FF buried.

**Phase 4: Refresh the plant's knowledge from the corpus (Opus
authors).** For each withdrawable library/tool page, **seed the refresh
from the corpus as the orientation layer**, then re-pin the plant's
version-specific facts fresh against the plant's real lockfile. A
withdrawable **legal** page adds one non-negotiable step: re-confirm each
entry's `verified` date and `legal_status` against the publisher, and
never copy a determination. **One home per dependency**: merge the
corpus orientation into the plant's existing page, never add a parallel
one, and do not mirror the corpus's own internal sub-namespace grouping
into the plant (that would create a duplicate home the Phase 7
minimum-sufficiency gate BLOCKS on).

**Phase 5: Grow the new capabilities onto the living plant (Opus
authors).** Fast-forwarding *carries* a capability; it does not *grow*
it. **Grafted is not grown.** For each new or newly-enriched capability:
grow what the plant evidently needs, grounded in its own facts
(instantiate a suggested skill/expert the plant's stack calls for,
withdraw a corpus library/tool/legal page it actually uses, ground a
runbook it can fill). **Never fabricate to fill a surface**: a project
skill, ADR, or runbook whose content can only come from real recurring
use sprouts during use, owned by the close-out lifecycle (`canonize` →
`docs-librarian`), not by the graft. **Surface what was grafted but not
grown** so the steward sees the copy-but-not-actualized state. **An
own-kernel plant** (one that carries no seed machinery) still receives
the substance as a **weave**, not a summary: map each seed surface the
delta changed to the plant's equivalent surface and land each rule where
it acts, in the plant's idiom. Collapsing the delta into one summary
section is a photocopy, not a graft.

**Phase 6: Rebalance the plant toward pure graph (Sonnet audit → Opus
authors).** The reconstruction pass, on **every** graft. (1) Inventory
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

**Phase 7: Apply, verify, and stamp (Opus authors; session gates).**
Apply the ratified upgrade **additively**, backing up every replaced
file first. Then prove the plant is left more capable and no less
itself:
- Rootstock intact: the plant's source and authored facts are
  byte-for-byte unchanged outside machinery and the deliberately
  refreshed surfaces. Any unexpected change BLOCKS.
- Customization audit (`tools/graft-audit.py`): any seed-owned file
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
  agent needed, so a surviving one BLOCKS.
- Lifecycle status: the plant's `status:` frontmatter (ADRs, specs,
  deviations, risks) is plant-owned and never touched by the fast-forward; a
  plant arriving from pre-7.0.0 runs `tools/status-migrate.py --root docs/graph`
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

### What stays out of scope

- Graft does not start on its own (an agent may only *propose* one, then
  stop).
- Graft does not touch the plant's application source, run its builds or
  test suites, or fetch/switch/commit/push Git (records Git state as
  provenance only).
- Graft does not rewrite the plant's authored `docs/graph/` facts or
  overwrite a pinned library/tool version the plant discovered.
- Graft does not modify the seed (a divergence worth flowing back is
  handed to `harvest`).
- Graft does not collapse a three-way conflict by picking a side
  silently, and does not apply an unratified reconciliation.

---

## Cross-references at a glance

- Kernel eight rules → owning protocol: 3.1 specify (`rule.spec`),
  3.2 context-router (not a protocol node), 3.3 grill (`rule.grill`),
  3.4 test-first (`rule.test-first`), 3.5 verify (`rule.verify`), 3.6
  deliver (`rule.deliver`), 3.7 canonize (`rule.canonize`), 3.8
  toolcraft (`rule.toolcraft`).
- The delivery funnel: brainstorm* → specify → grill →
  ingest-library* → test-first → verify → canonize →
  deliver; recover on any failure.
- The seed meta-loop: grow (seed → new plant), harvest (mature plant
  → seed, user-triggered), graft (enriched seed → existing plant,
  user-triggered), initialize (coding-tool adapter → grow).

*End of protocols reference. Every fact above is drawn from the files in
`protocols/*.md`, the support tools they name under `tools/`, and the
kernel `core/AGENTS.md`.*
