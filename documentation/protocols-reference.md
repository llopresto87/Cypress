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
| grow | `protocol.grow` | `grow.worker-topology`, `grow.growth-flow`, `grow.completeness-contract` | — | harvest, graft, initialize | 3600 |
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
`test-first`, not a separate `implement` protocol file.

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
9. **recover** is entered on any failure — the failure-discipline
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

- **id:** `protocol.brainstorm` — tier 2
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
write code and you do not pick a stack in brainstorm — you converge.

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

- **id:** `protocol.specify` — tier 2
- **owns:** `rule.spec`, `specify.flow`, `specify.revision-discipline`
- **requires:** —
- **peers:** `protocol.brainstorm`, `protocol.grill`
- **load_when:** "write a spec, no spec covers this behavior"; "new
  feature, endpoint, job, or LLM interaction to define"; "changing an
  existing feature's contract"; "bug revealed an implicit or missing
  contract"; "acceptance criteria, Given/When/Then, failure modes"

### What it does

Use specify when the goal is clear and you need an executable
specification before planning the implementation. The deliverable is a
new (or refreshed) file in `docs/graph/specs/`, populated through every
section of `docs/graph/templates/spec.template.md`, signed off by
product, architect, and tester.

This node owns **the spec rule** (`rule.spec`): specs are the source of
truth for *behavior*. Every non-trivial behavior — feature, endpoint,
job, significant function, LLM/VLM interaction — has a spec, written
before the code, with stable section numbers. Specs are executable:
every functional contract maps to at least one test (the test-first
rule enforces this). Superseded specs stay on disk with status
`superseded` and a link forward. If wiki and spec disagree about how a
library *can* be used, the wiki is right; if product and spec disagree
about what to build, fix the spec.

### Entry conditions

One of:
- `brainstorm` has just converged on a problem statement and a first
  useful slice.
- An existing feature is being changed in a way that affects its
  contract.
- A bug investigation revealed the original spec was incomplete or
  wrong.
- An ADR introduces a new system behavior that needs a spec.

### Who participates

| Specialist | Owns |
|-----------|------|
| `product` | §3 User-facing behavior, §9 Acceptance criteria (user view) |
| `architect` | §4 Functional contracts, §6 Data shapes, §7 Failure modes (system view) |
| `tester` | §10 Test mapping; reviews §4 for testability (executable view) |
| `docs-librarian` | registers the spec in the index, links it from grill.md |
| `security` | reviews when the spec touches auth, data, secrets, payments, file handling, or AI behaviors |

This workflow requires spawned clean-context workers. If the host
cannot spawn them with the required model classes, stop and report the
unsupported operating model; do not simulate the personas. A specialist
the host has no *type* for is a different case — see
`delegation.harness-registration`.

### The spec sections (§1–§12)

The spec is drafted from `docs/graph/templates/spec.template.md`:

| § | Section | Content |
|---|---------|---------|
| §0 | Metadata | id, status `draft`, owner, date, related grill section, related ADRs, related wiki pages |
| §1 | Summary | one paragraph — what the spec covers and why |
| §2 | Scope | explicit "in scope" and "out of scope" bullets |
| §3 | User-facing behavior | what the user experiences, in user language |
| §4 | Functional contracts | each contract is a named Given/When/Then scenario with one outcome |
| §5 | Non-functional requirements | performance budgets, security, accessibility floor, latency, cost |
| §6 | Data shapes | schemas for inputs, outputs, persisted state (language-agnostic convention) |
| §7 | Failure modes | for each contract, the named ways it can fail and what happens |
| §8 | Examples | concrete input/output pairs (one happy, one edge, one failure) — the seed test cases |
| §9 | Acceptance criteria | measurable "done" conditions, each mapped to contracts |
| §10 | Test mapping | for each contract and failure mode, the test(s) that cover it |
| §11 | Open questions | every "decide later" with a named resolution path |

(The revision changelog is the spec's §12, referenced under the
revision discipline below.)

### Workflow (`specify.flow`)

1. **Allocate an identifier** — `SPEC-NNNN-short-slug`; find the next
   free number in `docs/graph/specs/index.md`. File path:
   `docs/graph/specs/SPEC-NNNN-<slug>.md`.
2. **Draft from the template** — fill §0–§11 above.
3. **Testability review** — before the spec leaves `draft`, the tester
   checks: is every contract observable from outside? is every §9
   assertion measurable? are the data shapes concrete enough for a
   fixture? are the failure modes triggerable in a test environment? A
   spec that cannot be tested is a description, not a spec — it goes
   back to the architect.
4. **Security review (if applicable)** — for auth, secrets, payments,
   file uploads, external integrations, or LLM/VLM behaviors that act
   on data, security adds abuse cases as failure modes or
   non-functional requirements.
5. **Promote to active** — on sign-off, change status `draft` →
   `active`, add the index row, link from grill.md §3 and §9.
6. **Hand off to grill** — the plan implements the contracts in
   increments each small enough to be one RED-GREEN-REFACTOR cycle.

### Revision discipline (`specify.revision-discipline`)

When behavior changes:
1. Read the existing spec.
2. Decide: *clarification* (same meaning, said better) or *change*
   (behavior itself is different)?
3. **Clarifications:** edit in place; add a row to the spec's §12
   Changelog.
4. **Changes:** copy the spec to a new identifier, mark the old
   `superseded` with a link forward, write the new spec, update
   everything that depended on the old.

Specs never silently change behavior. The catalog tells the next agent
"this used to behave like X; now it behaves like Y; here is when it
changed and why."

### Exit conditions

- `docs/graph/specs/SPEC-NNNN-<slug>.md` exists, status `active`, every
  section populated.
- The index has the row; grill.md links from §3 and §9.
- Every §4 contract has at least one test in §10 (mapping may exist
  before the test is written).
- Sign-off recorded: product ✓, architect ✓, tester ✓ (security ✓ if
  applicable).

### Anti-patterns

- The spec is the README (marketing, not contracts).
- The spec describes the implementation, not behavior.
- No failure modes section (half a spec).
- No examples.
- Spec written after the code — mark it `back-written`.

---

## grill

*Source: `protocols/grill.md`*

- **id:** `protocol.grill` — tier 2
- **owns:** `rule.grill`, `grill.flow`, `grill.increment-shape`
- **requires:** —
- **peers:** `protocol.specify`, `protocol.test-first`
- **load_when:** "plan the implementation, plan-of-record, grill.md";
  "spec exists but no plan implements it"; "scope an increment, slice
  the work"; "plan is stale, assumption broke, architecture change"

### What it does

Use grill when a spec exists (or is authored in parallel) and you need
a plan-of-record before code. The deliverable is
`docs/graph/plans/grill.md`, populated through §14, with explicit
decisions, options, an architecture sketch, implementation increments
mapped to spec contracts, verification gates, risks, and a single
recommended next step.

This node owns **the grill rule** (`rule.grill`): `grill.md` is the
living plan-of-record, the source of truth for *plans*, linked to the
specs it implements and the nodes it depends on. Open it when you
start, before you change architecture, when you finish, and whenever an
assumption breaks. Append to its changelog; strike through stale
claims, never silently rewrite.

"Grill" is the discipline of grilling the *plan* until it is ready to
implement — pressing the assumptions until solid, the design until
coherent, the plan until each increment is one RED-GREEN-REFACTOR cycle
(or a small handful).

### Entry conditions

- The goal is clear (or `brainstorm` has converged it).
- A spec exists in `docs/graph/specs/` or is authored alongside.
- No current grill.md exists for this feature, or the existing one is
  stale by more than a major implementation phase.

If the spec does not yet exist, run `specify` first or in parallel; the
architect often drafts spec §4 and the grill architecture sketch
together.

### Workflow (`grill.flow`) — the grill.md sections

1. **Open or create grill.md** from the template.
2. **§1 Artifact Discovery** — read what exists: files, docs, tests,
   ADRs, specs, wikified libraries, recorded constraints. Cite paths;
   do not guess.
3. **§5 Research Summary** — hand to `research-scout` for every
   library/spec/API the plan depends on; ensure a
   `docs/graph/libraries/` page exists; if not, run `ingest-library`.
4. **§6 Decisions** — explicit choices, cited evidence, tagged
   reversibility. Non-obvious decisions get an ADR (delegate to
   `architect`). A recurring operation is decided as a **durable tool**
   (an increment in §9 with a stable interface and a test), and
   `docs/graph/tools/` is checked for an existing one (§3.8).
5. **§8 Architecture Plan** — boundary diagram and contracts, aligned
   with the spec's §4.
6. **§9 Implementation Plan** — slice the work into increments (see
   increment shape below).
7. **§10 Verification Plan** — which gates run for which increments.
8. **§11 Risks and Mitigations** — hand to `security` and
   `reliability` as relevant.
9. **§12 Open Questions** — each "figure out later" becomes a row with
   a named owner and resolution path.
10. **§13 Done Criteria** — objective completion conditions aligned
    with the spec's §9 acceptance criteria.
11. **§14 Recommended Next Step** — a single action, usually "enter
    test-first for increment 1".
12. **§15 Changelog** — an entry describing this grill session.

The grill protocol is a *pass*: iterate it twice if research changes
the architecture, and record what changed in the changelog.

### Increment shape (`grill.increment-shape`)

§9 is where grill earns its keep. A good increment names: the spec
contract(s) it satisfies, the files touched, the tests to write (in
RED), the behavior added, the gate that proves it done, the rollback
path, the effort (roughly one RED-GREEN-REFACTOR cycle), and its
dependencies. The protocol gives a full worked example ("Increment 3 —
Persist submissions"). If an increment does not fit this shape — vague
tests, no spec contract, no rollback — it is not ready. Re-slice.

### Spec ↔ plan alignment check

Before exiting grill, verify:
- Every contract in the spec's §4 appears in at least one increment in
  §9.
- Every acceptance criterion in the spec's §9 maps to at least one
  contract an increment implements.
- No increment introduces behavior not covered by a contract (if one
  does, go back to `specify`).

This check is what makes spec-driven development actually spec-driven.

### Exit conditions

- §0–§14 populated for the current feature.
- Every library named in §5 has a wiki page.
- Every non-obvious decision has an ADR or a §6 row.
- Every §9 increment names spec contracts and tests.
- The spec ↔ plan alignment check passes.
- §14 names a single next action.

### Anti-patterns

- Skipping §1 ("I know what's in the repo") — read it.
- Skipping §5 ("I know the library") — the wiki often says otherwise.
- Increments that touch ten files and add three behaviors — slice them.
- A risk table where every row says "manageable".
- A "next step" that is actually a list.
- A plan with no spec link (that is a wish).

---

## test-first

*Source: `protocols/test-first.md`*

- **id:** `protocol.test-first` — tier 2
- **owns:** `rule.test-first`, `test-first.cycle`, `test-first.characterize-first`
- **requires:** —
- **peers:** `protocol.verify`, `protocol.specify`, `skill.test-first`, `skill.holistic-editing`
- **load_when:** "about to write or change production code"; "RED GREEN
  REFACTOR, failing test first, TDD"; "bug fix, regression test";
  "legacy code with no tests, characterization test"; "pure refactor,
  migration safety"

### What it does

Use test-first whenever you are about to write or change production
code. The deliverable is a sequence of RED → GREEN → REFACTOR → COMMIT
cycles, each tied to one or more spec contracts, with verification
gates passing at the end.

This node owns **the test-first rule** (`rule.test-first`): tests
authorize code; you integrate, not bolt on. No production code without
a failing test that authorizes it: RED → GREEN → REFACTOR → COMMIT, per
increment. The test encodes a named spec contract and must fail for the
right reason first; GREEN adds the minimum new behavior, integrated
into the file, not stapled to its edge; REFACTOR is not optional when
you touched existing code, and an additive-only diff is a red flag to
justify. The exceptions are explicit and recorded in grill.md §9.

### Entry conditions

- A spec exists in `docs/graph/specs/` for the behavior.
- A plan exists in `docs/graph/plans/grill.md` §9 with named
  increments.
- The relevant libraries are wikified in `docs/graph/libraries/`.

If any is missing, back up to the protocol that produces it (`specify`,
`grill`, `ingest-library`).

### Characterize first (`test-first.characterize-first`)

On legacy or adopted code with no spec and no test, you cannot turn a
contract into a failing test, because nobody wrote down what the code
is *supposed* to do. Before you change such code, write a
**characterization test** that pins what it does *today* — bug
included. Run it; it passes (it describes reality). Name it so no one
mistakes it for a correctness claim (`characterizes_…`, not
`should_…`), and note any believed-wrong behavior in the docstring,
linking the grill.md item that tracks fixing it. Now you have a safety
net: make the change, the characterization test fails exactly as
intended, and that failure is your RED.

### The cycle (`test-first.cycle`)

For each increment in the plan:

**RED — write the failing test**
1. Identify the spec contract(s) — each is one Given/When/Then in the
   spec §4.
2. Write test(s) exercising each contract; names:
   `test_<spec_id>_<contract_slug>`. The test name names the contract.
3. Run the test. **Confirm it fails for the right reason.** A failure
   from a missing import or a wrong function name is *not* RED; a
   failure because the *behavior* is missing *is* RED.
4. If you cannot get RED for the right reason, the test or contract is
   wrong — fix it.
5. Update spec §10 (Test mapping): status `red`.

*Inherited suites — prove RED by mutation.* A green suite you inherited
is untrusted; you have never watched it fail. Before you rely on it,
deliberately reintroduce the historical defect a test claims to guard
against, confirm the suite fails for *that specific reason*, then
revert. Only a green you have seen turn red and back is a trusted
green.

**GREEN — minimum behavior, integrated**
1. Add the minimum *new behavior* that turns RED to GREEN. "Minimum" is
   about behavior, not diff size: no speculative generality, no
   expansion into unrelated code — but integrate it into the file's
   existing design, do not append at the bottom.
2. Run the test; confirm it passes.
3. Run the surrounding/module tests; confirm nothing else broke. A new
   green that turns another green red is a regression and must be fixed
   before proceeding.
4. Update spec §10: status `green`.

**REFACTOR — integrate cleanly, suite green**
1. Look at the code you wrote and the code around it.
2. Remove duplication, delete dead branches, fix names/docstrings, move
   code to the right module. When done, the file reads as if the
   requirement had always existed, with no visible seam (see
   `docs/graph/skills/holistic-editing.md`).
3. Run tests after each refactor; the suite stays green.
4. On a pure addition to green fields the refactor may be trivial. But
   **when you touched existing code, REFACTOR is not optional** — an
   additive-only diff that left duplication or dead code behind is
   incomplete. (Append-only artifacts — grill.md history, ADRs — are
   the deliberate exception; there you supersede.)

**COMMIT — record the increment**
1. Append to grill.md §15 (Changelog): increment title, spec contracts
   covered, files touched, tests added, gates run/passed.
2. Update spec §10 with actual test names and file paths.
3. Name any library idiom this increment taught and any durable tool it
   built in your handback payload; the close-out librarian persists
   them (§3.7/§3.8). You do not edit the wiki or the tool catalog
   inline.
4. If using version control, commit:
   `feat(<scope>): <contract slug> — implements SPEC-NNNN` or
   `fix(<scope>): <bug slug> — adds regression for SPEC-NNNN`.
5. Hand the diff to `reviewer`.

### Per-language test framework

The first time test-first runs in a project, the framework is chosen
and wikified; subsequent increments use the same one. Criteria: official
or near-official for the ecosystem; fast feedback; good failure
messages; support for fakes, fixtures, parametrization, and the test
levels in `docs/graph/agents/04-tester.md`. The choice is recorded as
an ADR.

### Bug fixes

A bug is a spec the codebase failed to honor (or a missing spec):
1. If the violated contract already exists — write a regression test
   against the buggy code, see it fail, fix, see it pass. If not — the
   spec was incomplete; run `specify` first, then write the regression.
2. A bug confirmed but not yet fixable is encoded as an
   explicitly-named, intentionally-failing test inside the regular
   suite, documenting the root cause — the debt stays visible on every
   run.
3. The regression test stays in the suite forever.

### Pure refactor (no behavior change)

1. Existing tests must pass before you start.
2. You write no new test (no new behavior).
3. You change the code.
4. Existing tests must still pass.
5. If any breaks: either (a) behavior changed accidentally — roll back,
   or (b) the test tested implementation not behavior — fix the test or
   back up to `specify` if the refactor changes the spec.

### Migration safety gate

Before any framework, ORM, or runtime **major-version** migration,
confirm the change is observable. "No migrations tool and no tests,
with the schema driven only by the ORM's auto-DDL" is itself a
**blocking** finding that must be closed first. A migration against an
unguarded schema is an unverified change waiting to surface in
production.

### Exceptions to test-first (recorded in grill.md §9 with rationale and date)

- **Throwaway prototypes** to learn a library — mark them; do not
  merge.
- **Pure configuration changes** with no behavior to verify.
- **Type-only changes** where the type checker is the verifier.
- **Generated code** where the generator itself is tested.

Reaching for "exception" frequently is a signal that test-first is not
landing — surface it to the orchestrator.

### Exit conditions

- Every spec contract for the increment has a passing test.
- The full suite is green.
- The verification gates from `verify` have run.
- grill.md and the spec are updated.

### Anti-patterns

- Writing tests after the code "to be safe" (documentation, not
  test-first).
- Tests that pass without the code present (investigate). Ask the same
  of a whole gate phase: if it would have passed identically against
  the pre-change code, it proved zero coverage.
- One giant test per increment.
- Testing through (e2e for a pure function; a unit test that mocks
  three layers).
- Mocking everything — mocks for the object under test or its immediate
  collaborators are a smell.
- Assuming dev-machine green means CI green (CI image may lack a
  browser binary or runtime).

---

## verify

*Source: `protocols/verify.md`*

- **id:** `protocol.verify` — tier 2
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
recorded. A gate not yet available is recorded **absent** with a date —
never silently dropped, never faked green. A gate that runs but asserts
nothing is a **green lie** — worse than a missing gate, because it is
trusted.

**Actor:** `tester` runs the gates (`reliability` for operational and
deploy gates) in its own context and reports outcomes in its handback;
the runbook entry is part of that worker's write scope. The grill.md
§15 record (step 8) is the session's — the plan-of-record is a
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
(live spec contracts with no test — `python3 docs/graph/spec-lint.py`);
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
out of ritual — wall-clock and attention are budget too.

### Workflow

1. **Pick the applicable gates** from the risk table and the gate menu.
   Order by risk: gate the assumption most capable of invalidating the
   increment first. Prefer one high-information gate over overlapping
   ones. Verification stops when the mandatory gates pass and the
   remaining uncertainty cannot materially change the result — not when
   every possible gate has run.
2. **Run them cheapest first** (formatter, linter, type check); proceed
   to slower gates only if cheap ones pass.
3. **Record outcomes** in `docs/graph/runbooks/verification.md` under
   the increment heading, with the command and result per gate.

### The three gate states (`verify.gate-states`)

Report every gate as exactly one of three states — silence must never
imply a pass:

- **executed** — actually run this pass, with command and result. If it
  fails, fix the increment or hand it back; do not record a fake PASS.
- **discovered** — known to exist (read in source/config) but not run
  this pass. Record it "DISCOVERED, not run (date) — reason" so it can
  never be mistaken for an executed pass.
- **absent** — does not exist yet. Record it with a date, a reason, and
  the owner who will add it.

Adopting a codebase with no gate infrastructure is not an excuse to
leave the runbook empty: record each standard gate explicitly as
`absent (YYYY-MM-DD) — <reason>`. A blank verification runbook is
indistinguishable from one nobody checked.

**The green-lie clause.** The three states are honest only if an
executed PASS means something. A test command with no tests, a linter
over an empty set, a type check with everything untyped — these "pass"
and mean nothing. Do not cite a vacuous pass; do not wire such a gate
into CI. Land the real check first, then add the gate in a later
increment — never both in the same one. A gate that executes and
asserts can still lie by not discriminating: a recorded verdict uses
only the words the check proved. An invocation-*count* assertion on a
mock passes vacuously the moment the code stops calling that
collaborator for a wrong reason — assert on the actual destination,
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
- **Characterize first, then change** — capture a baseline oracle of
  current observable behavior (endpoint responses, persisted shapes,
  message payloads, computed outputs), normalized to mask only volatile
  leaves. This is the RED spine: it must pass on the *pre-change* code.
- **Diff against the baseline; allow only an enumerated intended-delta
  list** — the gate passes only if everything matches the baseline
  except an explicit list of intended deltas, each row naming the
  change and why it is a deliberate strengthening. Byte-identical output
  is the wrong contract; observable-behavior preservation is. An
  unexplained diff, or an additive-only edit to the pinning tests, is a
  red flag to justify — never a silent re-baseline.

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
- "We don't have time for the eval suite this increment." — that is the
  signal to merge a smaller increment, not to skip the gate.

---

## recover

*Source: `protocols/recover.md`*

- **id:** `protocol.recover` — tier 2
- **owns:** `recover.failure-classes`, `recover.three-attempt-boundary`
- **requires:** —
- **peers:** `protocol.deliver`, `protocol.grill`
- **load_when:** "a worker or gate failed, what now"; "retry or
  re-route, flaky failure"; "delegation came back wrong or ambiguous";
  "gate red twice on the same increment"

### What it does

Recover is the failure discipline. Failure is a normal output of real
work; the waste comes from *unclassified* reaction to it — hammering an
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
| **Capability** | The worker is the wrong instrument: wrong specialist, missing expertise, out-of-domain handback, LOW/NONE route band in hindsight | Re-route: run `agent-lint --route` with a *sharper* task statement, or commission the missing expert (kernel §1). Do not re-brief the same agent harder. |
| **Ambiguity** | The worker asked the brief a question, guessed, or two artifacts contradict (spec vs code, plan vs node) | Fix the **cheapest upstream artifact that owns the confusion** — brief first, then plan (grill §), then spec — and re-delegate. Widening context is not the fix. |
| **Systemic** | The harness or system itself: wedged delegation, depth cap hit, missing tool, broken gate infrastructure | Stop the line. Record in grill.md §12 and report to the human with the exact evidence. No workaround that hides it. |
| **Unregistered** | The specialist exists on disk but the host has no such type: the session predates the projection, or it is rooted at the seed rather than the plant. Reads like Systemic — it is not. | Apply `delegation.harness-registration`: preflight, re-enter rooted at the plant, or role-emulate **and record it**. Do not stop the line, and do not commission a second definition. |

An intermittent or probabilistic failure is confirmed **fixed** only on
mechanism-level evidence — a trace proving the causal path is genuinely
absent — never on a lower observed failure rate. Any incidental change
that reduces *exposure* to the defect buys a better rate while fixing
nothing. Corollary: sequence any exposure-reducing change **after** the
diagnostic evidence is captured, never before.

### The three-attempt boundary (`recover.three-attempt-boundary`)

Across ALL strategies combined, a unit of work gets **three attempts**.
The fourth move is always escalation: record the failure-class history
in grill.md §12, mark the increment WIP in the delivery, and hand the
decision to the human with the evidence — never a fourth quiet attempt,
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
  class — including recoveries that *worked* (a transient retry that
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

- **id:** `protocol.canonize` — tier 2
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
way. Every T2/T3 task ends with **one** docs-librarian spawn — the
close-out — that persists into `docs/graph/` the facts, sharp edges,
corrected assumptions, provenance, and missed `load_when:` triggers the
work surfaced, and catalogs its durable tools (the toolcraft rule) in
the same pass. Two doctrines, one execution — a second spawn with the
same bootstrap and lint run would be pure coordination waste.

The librarian owns the graph's **fact-bearing surfaces** — nodes, wiki
pages, the tool catalog — and one-home-per-fact; the session never
edits those. The session-owned operational artifacts under the same
root — grill.md, the verification runbook, changelog.md — are the
deliberate exception: the session writes them directly.

### When to invoke

- At the completion of every **Tier 2/3** task or increment, before
  `deliver`.
- Whenever the work surfaced a fact the graph does not own,
  contradicted one it does, or produced a tool a future session will
  run again.
- **Tier 0/1 shortcut:** a question answered or a trivial
  non-behavioral edit needs no spawn. The session writes one line in
  the delivery — "canonize: nothing of interest / no tool, because …" —
  and that satisfies the fail-closed doctrine. If a T0/T1 task *did*
  surface something durable, it escalates: spawn the librarian.

### What the one brief carries

**Knowledge candidates (§3.7):** a new or changed fact about the
project's structure or capability; a sharp edge that bit (and the tell
to spot it next time); a corrected assumption; provenance for a claim;
a `load_when:` trigger that should have matched and didn't; a new
library idiom or pitfall.

**Tool candidates (§3.8, toolcraft owns the doctrine):** any durable
tool the work produced — recurs across sessions, stable interface,
test-authorized, lives in the repo. Named in `tools_built` on handbacks.

**Skill candidates (§3.8):** any repeatable multi-step procedure a
future session will walk again — named in `skills_built`, or the same
sequence appearing a third time. The brief forwards candidates; the
librarian authors them.

**Neither list includes:** ephemeral scratch, secrets/credentials,
production or personal data, speculation (write "not recorded"),
project-specific material aimed at the seed (that is `harvest`'s
agnosticism gate), throwaway prototypes or genuine one-offs.

### The flow — one spawn (`canonize.close-out-flow`)

1. **Assemble candidates** from the finished work and the workers'
   handback payloads: facts with evidence, tools with path + entry
   point + invocation + covering test.
2. **Spawn the docs-librarian once** (Opus-class; it owns
   `docs/graph/`) with a brief embedding the canonical block from
   `docs/graph/templates/prompts/graph-session-bootstrap.md` plus both
   candidate lists. This spawn is fail-closed. If the host has no such
   type, apply `delegation.harness-registration` — skipping the
   close-out because the type would not resolve is not an option.
3. **The librarian persists and catalogs in one pass:** each fact lands
   in exactly one node's `owns:` (dedupe — update, don't duplicate);
   each tool gets `tool-page.template.md` filled into
   `docs/graph/tools/<name>.md` plus an index row and an `artifacts:`
   edge (checking `tool-corpus/` first where the corpus is available);
   each recurring procedure gets `skill.template.md` filled into its home
   node `docs/graph/skills/<name>.md` plus the projection in each harness
   dir the plant uses (checking `skill-corpus/` first where available,
   deduping, composing existing disciplines by reference); failed
   `load_when:` triggers are sharpened. One `graph-lint` run confirms
   the graph stays clean.
4. **Confirm or record-empty.** The librarian hands back nodes/fact-keys
   touched and tool cards written, or an explicit "nothing of interest,
   because …" / "no durable tool, because …" — with the lint result.

### Fail-closed doctrine

A task is **not complete** until its knowledge is canonized, any durable
tool cataloged, and any recurring procedure crystallized into a project
skill — or each explicitly recorded empty with a reason. An uncaptured
fact is a silent knowledge leak; an uncaptured tool or procedure is a
silent capability leak — the same failure class as a green lie (§3.5).
`deliver` (§3.6) does not sign off until this close-out has run (or the
T0/T1 self-record line is present).

### Relationship to the other protocols

- `deliver` produces the human-facing cold-pickup **summary**; canonize
  persists the machine-facing **graph knowledge and tool catalog**.
- `toolcraft` owns the *doctrine* of what counts as a durable tool;
  canonize owns the *execution* — there is no separate toolcraft spawn.
- `harvest` folds **project-agnostic** lessons and tools into the seed,
  user-triggered only; canonize keeps **project-specific** knowledge in
  the plant. What harvest's agnosticism gate rejects still belongs here.

### What you do not do

- Close a T2/T3 task without the librarian spawn, or skip the T0/T1
  self-record line "because it was minor".
- Spawn the librarian twice for one task's close-out.
- Write the graph's fact-bearing surfaces from the main session.
- Canonize secrets, production data, or speculation.
- Duplicate a fact or tool card that already has a home — update it in
  place.

---

## toolcraft

*Source: `protocols/toolcraft.md`*

- **id:** `protocol.toolcraft` — tier 2 (note: no `command: true`)
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
unit of work is a **durable, tested tool** with a stable interface —
designed so at plan time, named in `tools_built` on every handback, and
cataloged in `docs/graph/tools/` by the librarian inside the close-out
spawn. Genuine one-offs and throwaway prototypes stay disposable.

**This file owns the doctrine only.** The execution — cataloging the
tool — happens inside the single close-out spawn defined in
`docs/graph/protocols/canonize.md`, in the same librarian brief that
persists the task's knowledge. There is no separate toolcraft spawn.

### What counts as a durable tool (`toolcraft.durability-criteria`)

Catalog a piece of real code that:
- **recurs across independent sessions** — an agent, expert, or skill
  will plausibly run it again (the trigger is recurrence, not size);
- has a **stable interface** — a named entry point, defined inputs and
  outputs, a documented invocation, not a copy-pasted snippet;
- is **authorized by a test** (§3.4) — at least one test pins what it
  does, so a future session can trust and change it safely;
- **lives in the repository**, committed where the project keeps its
  tooling, reachable by path.

### What stays disposable

- a **genuine one-off** — needed once, no future task plausibly repeats
  it;
- a **throwaway prototype** to learn a library or shape — the blessed
  carve-out of the test-first rule; recorded, if anywhere, as an
  exception in grill.md §9;
- anything embedding secrets, credentials, or production/personal data;
- project-specific tooling aimed at the seed — that is `harvest`'s
  agnosticism gate.

### The procedure sibling — durable skills

A tool is durable *code*; a **skill** is a durable *procedure* — the
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

- **id:** `protocol.deliver` — tier 2
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
session ends with a delivery, compact for T0/T1, full for T2/T3 — files
changed, routing attribution, docs updated, decisions, gates with
outcomes, limitations, and **one** recommended next step. The
deliver-time attribution assertion is fail-closed: a unit of work with
no `produced_by` is a BLOCK. A session without a delivery summary is
paused, not finished — never skip this protocol.

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
not T1 — reclassify and take the full path. The compact form appends to
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
aggregates these across deliveries to find *systemic* seed problems —
recurring misroutes mean a specialist's `routing_triggers` need
sharpening, frequent tier reclassifications mean the tier edges need
tuning, repeated transient retries in one area is a reliability signal.

### Quality bar

A delivery that passes names every changed file; names every
documentation update with its location; cites verification outcomes (no
hand-waving); lists every limitation explicitly; recommends exactly one
next step; and is the smallest summary that permits correct use and
appropriate trust (material caveats in, process narration out —
proportionate communication). A delivery that fails says "implemented
X" without naming files, "tests pass" without naming gates, "do
whatever feels right" or five options, hides limitations behind
optimism, or pads the record with narration the next session must
filter out.

### Routing-attribution assertion (fail-closed) (`deliver.attribution-assertion`)

Before sign-off, attribute every unit of work to the specialist that
produced it, reading `produced_by` and `route_evidence` from the
handback payloads. Then:

- **Missing `produced_by` on any unit of work → BLOCK.**
- **Out-of-domain authoring → FLAG** — a `produced_by` specialist whose
  `routing_triggers` do not cover the work it authored.
- **Unexplained generic-role override → FLAG** — a HIGH band for
  specialist X but the work was produced by a generic role or a
  different specialist with no recorded rationale.
- **Role emulation → FLAG unless declared** — a worker running as a
  generic type wearing a specialist's role must carry
  `harness_override: role-emulated (<reason>)` in its handback. Report
  the count in the delivery.

This assertion runs in the top session at `deliver` — the one place a
hook can reach, since subagent hooks do not fire. A top-session Stop
hook that greps the delivery for attributions stays **deliberately
unwired until this plant's real deliveries carry `produced_by`** (a
gate landed before the thing it checks either checks nothing or blocks
everything — kernel §3.5, the green-lie rule). Once deliveries carry the
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
- Deliver a half-finished increment as done — mark it WIP and recommend
  resuming it as the next step.

---

## ingest-library

*Source: `protocols/ingest-library.md`*

- **id:** `protocol.ingest-library` — tier 2
- **owns:** `ingest-library.flow`, `ingest-library.corpus-first`
- **requires:** —
- **peers:** `protocol.harvest`, `skill.library-wiki`, `skill.research-and-ingest`
- **load_when:** "adding a new dependency, library, SDK, or API"; "no
  wiki page for a library the code uses"; "version pin changed, refresh
  the library page"; "security advisory on a dependency"

### What it does

Use ingest-library whenever a new external dependency (library,
framework, SDK, API, protocol, spec, model provider, or significant
tool) is introduced, OR whenever an existing page is stale. The
deliverable is a complete, version-pinned page in
`docs/graph/libraries/<name>.md`, registered in the index, with raw and
normalized sources on disk. The wiki is the project's source of truth;
agent memory of library APIs is unreliable across versions, so always
ingest first.

### Entry conditions

One of: `architect`/`implementer` wants a dependency with no page; the
version pin no longer matches; a behavior was encountered the page does
not cover (and cost debugging time); a security advisory affects a
wikified library.

### Cast

- `research-scout` — retrieval and normalization.
- `docs-librarian` — finalizes the page and updates indexes.
- `architect` (lightly) — confirms the dependency fits the architecture
  before the page is committed as authoritative.

### Workflow (`ingest-library.flow`)

**0. Withdraw from the seed corpus first (`ingest-library.corpus-first`).**
Once you know the library's exact name, version, and ecosystem, check
the seed's library-documentation corpus **first** — the pages `harvest`
folded back from earlier plants
(`library-corpus/<ecosystem>/<library>.md`, keyed by library and **not
by version**). If the page exists, seed
`docs/graph/libraries/<name>.md` from it, then pin and validate the
version-specific layer (API deltas, deprecations, CVEs) against this
project's actual lockfile version from upstream — the corpus never
substitutes for the pin check. If the corpus page is absent, ingest from
upstream as usual; the fresh page's version-durable surface becomes a
harvest candidate. Reuse the corpus, re-download only the
version-specific delta.

**1. Identify** — canonical name; the exact version to pin (not
"latest"); ecosystem (npm, PyPI, Go module, Maven, OS package, container
image, IETF RFC, etc.); why this project needs it (one sentence for §2).

**2. Retrieve** — `research-scout` fetches release notes/CHANGELOG,
getting-started/quickstart, public API reference, security policy /
advisories, license file, and for LLM/VLM libraries: pricing-relevant
behavior, rate limits, structured-output features, safety policies.
Snapshot raw content to `docs/graph/sources/raw/` (when license
permits) and produce normalized clean Markdown in
`docs/graph/sources/normalized/`.

**3. Inspect (read the code, not just the docs)** — scan the public API
surface, `examples/`, and the maintenance signal (recent commit dates,
open-issue volume). Note any doc/code discrepancy.

**4. Compose the wiki page** — from
`docs/graph/templates/library-page.template.md`. The template owns the
section list; fill every section. Two constraints the template cannot
enforce: the API-surface section covers only the slice this project
actually uses (start small); and for a private dependency, record that
resolution needs registry credentials in the build/CI environment. The
page is brutally specific to this project — only the parts the project
uses or must be careful about.

**5. Register** — `docs-librarian` adds the page to the libraries index
(Library | Version | Page | Used by | Maintenance | License | Last
reviewed) and updates the sources index.

**6. Validate** — one of `architect`/`implementer`/`tester` writes a
tiny smoke test that imports/uses the library at the pinned version, to
confirm the snippet works; `security` skims for advisories affecting the
pin. If the smoke test fails, the page is wrong — fix it before calling
the protocol done.

**7. Notify grill.md** — add the wikified library to §5 (Research
Summary) and §6 (Decisions Made).

### Refresh (vs new ingest)

Update the version pin and "Last reviewed" date; diff the upstream
CHANGELOG between old and new version; update the API surface, idioms,
and pitfalls; run the smoke test at the new version.

### Exit conditions

- `docs/graph/libraries/<name>.md` exists, populated, dated, sourced.
- The libraries and sources indexes have the rows.
- A smoke test verified the pinned version works.
- grill.md is updated.

### When *not* to use this protocol

- A trivial transitive dependency the codebase doesn't directly use
  (wikify what you import, not every package in `node_modules`).
- A platform feature part of the runtime itself (stdlib, browser
  built-ins) — cover those in
  `docs/graph/best-practices/engineering.md`.

---

## from-scratch

*Source: `protocols/from-scratch.md`*

- **id:** `protocol.from-scratch` — tier 2
- **owns:** `from-scratch.phases`
- **requires:** —
- **peers:** `protocol.brainstorm`, `protocol.ingest-library`, `skill.from-scratch-bootstrap`
- **load_when:** "start a new project, empty repo"; "greenfield,
  bootstrap from nothing"; "no grill.md exists yet, day one setup";
  "project skeleton, verification baseline"

### What it does

Use from-scratch when the project does not yet exist — the repo is empty
or near-empty (no `docs/`, no `README.md`, no `grill.md`). Your job is
to turn a goal into a project another agent can pick up cold. This
protocol is bigger than the others because the first day matters
disproportionately. Do not skip steps.

### Entry conditions

- The user has stated a goal, even vaguely.
- There is no `docs/graph/plans/grill.md` yet.
- The repository is empty, near-empty, or contains only a license and a
  README placeholder.

### The nine phases (`from-scratch.phases`)

**Phase 1 — Brainstorm (Socratic).** Adopt
`docs/graph/protocols/brainstorm.md`; do not skip. Output: a precise
problem statement, the primary user, the first useful slice, the
constraints, and at least three shaped options. Ask at most three
questions per exchange; if you cannot reach precision in three turns,
write what you have, mark gaps as assumptions in grill.md, and proceed.

**Phase 2 — Project skeleton.** Once the brainstorm converges, create
the skeleton: `AGENTS.md` (← `core/AGENTS.md`, the universal kernel),
`CLAUDE.md` (symlink or copy), `.github/copilot-instructions.md`,
`docs/graph/agents/` (the team, projected to `.claude/agents/`),
`docs/graph/protocols/`, `docs/graph/skills/`, `README.md`, and the
`docs/` tree including `docs/graph/` (`_schema.md`, `graph-lint.py`,
`index.md` router, `nodes/root.md`), `plans/grill.md`, `specs/index.md`,
`decisions/adr-0001-bootstrapping.md`, `libraries/index.md`,
`sources/index.md`, `runbooks/local-development.md`,
`runbooks/verification.md`. The seed's `install.sh` can drop the right
per-tool overlay into `.claude/`, `.prime/agent/`, `.opencode/`,
`.codex/`, or `.github/`, plus the knowledge-graph scaffold. That
overlay includes the specialist roster this protocol later dispatches
**by name** — settle spawnability before the first named hand-off
(`delegation.harness-registration`). A new graph starts tiny — one root
node — and grows a node per subsystem as the architecture (Phase 5)
takes shape.

**Phase 3 — Initial grill.md.** Open grill.md from the template; fill at
minimum §0 (Metadata: project name, date, phase "bootstrapping"), §2
(problem statement), §3 (User Goal: primary user, outcome, acceptance
criteria for the first slice, non-goals), §4 (Operating Constraints),
§7 (three+ shaped options), §11 (Risks), §12 (Open Questions), §14
("Phase 4 — research and library ingest").

**Phase 4 — Research and library ingest.** Hand off to `research-scout`
with candidate technologies, and run `ingest-library` for each — its
steps own the existence, version, and maintenance-signal checks and
produce the wiki page. This phase often updates the shaped options
(§5/§7) as candidates turn out unmaintained, worse-licensed, or
sharp-edged.

**Phase 5 — Architecture decision.** Hand off to `architect`: pick the
option using constraints and research; write
`docs/graph/decisions/adr-0001-initial-architecture.md`; update grill.md
§6 (Decisions) and §8 (Architecture Plan); draft the boundary diagram.

**Phase 6 — Verification baseline.** Before any feature code: pick the
formatter, linter, type checker, and **test framework** (wikify each via
`research-scout`); write `runbooks/local-development.md` with exact
install/run commands and `runbooks/verification.md` with exact gate
commands; add a minimal "hello world" test that runs end-to-end. The
gate command must pass on a clean checkout before any feature. A project
that cannot run its gates from a clean checkout, or has no test
framework configured, is not yet bootstrapped.

**Phase 7 — Specify the first useful slice.** Run `specify` to produce
`docs/graph/specs/SPEC-0001-<slug>.md` covering §1–§10; get the
sign-offs (product ✓, architect ✓, tester ✓).

**Phase 8 — Test-first the first useful slice.** Run `test-first` for
each contract in SPEC-0001: RED → GREEN → REFACTOR → COMMIT for each
increment in grill.md §9.

**Phase 9 — Deliver.** Run `deliver`. The recommended next step is the
second slice or the next-most-valuable item from the roadmap in
`docs/graph/product/requirements.md`.

### Exit conditions

- grill.md exists and is current.
- `adr-0001-*.md` records the initial architecture.
- `libraries/index.md` lists every chosen dependency with a page each.
- `runbooks/local-development.md` and `verification.md` exist and their
  commands run.
- `specs/SPEC-0001-*.md` exists, status `active`.
- The first useful slice's tests are green; the suite is green.
- The README explains what the project is and how to run it.

### Common ways to fail this protocol

The catalog of how a first day silently goes wrong — feature code before
the gates run, code where the spec belongs, a skipped brainstorm, a
stack picked from memory, a bootstrap with no test framework — is the
honesty discipline owned by `skill.from-scratch-bootstrap`; read it
alongside this protocol. A structural rule the skill cannot own: **each
phase adopts a sub-protocol that carries its own failure modes** — read
the phase's protocol, never a summary of it.

---

# The seed meta-loop: grow, harvest, graft, initialize

These four protocols are the seed's own life cycle across projects.
`grow` runs the seed *into* a new project. `harvest` runs a mature
project *back into* the seed. `graft` carries the enriched seed
*outward onto* an existing plant. `initialize` is a thin coding-tool
adapter to `grow`. `harvest` and `graft` are user-sovereign — never
entered unprompted.

---

## grow

*Source: `protocols/grow.md`*

- **id:** `protocol.grow` — tier 2 (note: no `command: true`)
- **owns:** `grow.worker-topology`, `grow.growth-flow`, `grow.completeness-contract`
- **requires:** —
- **peers:** `protocol.harvest`, `protocol.graft`, `protocol.initialize`
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
   evidence-ledger schema — demand paths/symbols for every claim. Each
   scout persists ONE ledger per boundary to the plant's gitignored
   seed-organ scratch, `.cypress/growth/<slug>.ledger.md` (never under
   `docs/graph/` — the ledger is growth-time feedstock, not plant
   knowledge).
2. Reconcile the per-boundary ledgers into a coherent evidence set in
   the orchestration plane, cross-referencing the persisted ledgers.
   Resolve contradictions with another bounded scout; do not guess.
3. Spawn **Opus-class** authors for every written artifact or deep
   synthesis, using the growth-author brief that CONSUMES the ledger and
   maps each section to its deliverable — authors build on cited
   evidence, never a fresh reading invented from scratch.
4. Spawn separate **Opus-class** reviewers/validators for graph
   integrity, source fidelity, navigation, and false-premise rejection.
5. Route each finding back to a bounded Opus author, then revalidate.

Every brief states purpose, exact scope, allowed reads/writes, required
graph context, evidence supplied, constraints, output contract, and
verification. Every spawned session executes
`python3 docs/graph/graph-lint.py --plan "<exact delegated task>"`
before source reads or writes. Route each spawn with
`python3 docs/graph/agent-lint.py --route "<exact delegated task>"` and
cite the ranked specialist and confidence band. Delegating workers spawn
only from their `delegates_to` allowlist and under their
`max_spawn_depth` cap — the deepest legal chain is orchestrator →
multi-agent-architect → architect → leaf (depth 3). Leaf workers carry
no `Task` tool: at an out-of-domain boundary they STOP and return the
handback payload naming the next specialist. Every worker ends its turn
with a payload carrying `produced_by` and `route_evidence`.

Two host conditions look alike and only one is fatal. If the host
cannot spawn clean-context workers with selectable model classes, stop
and report that this host cannot execute the seed's operating model — do
not silently collapse delegated work into the main chat. If it can spawn
but a named specialist is **not registered as a spawnable type** (the
ordinary state of the session that just installed the roster), that is
*not* fatal — preflight and apply `delegation.harness-registration`.

### Boundaries

- Executable source is primary evidence (manifests, entry points,
  routes, models, migrations, config, deploy descriptors, tests, CI,
  prompts, evaluations). Existing prose is clues only; corroborate.
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

Growth is **complete or it is not done**. A first growth that stops at a
skeleton — a root node, a router, and a handful of leaves — is a failed
growth reported as a success, and it is the single most common way this
protocol is mis-run. The contract is binding on whatever model
orchestrates growth; it does not soften with model size, context
pressure, or operator impatience. Full depth is the default, not an
upgrade.

**The rule of evidence-bounded totality.** For every knowledge
collection, growth produces one of exactly two outcomes, never a third
silent one:

- *Covered* — authored to the full depth its evidence supports: every
  real subsystem has a node; every direct dependency is indexed and each
  architecturally-significant one has a project-specific page; every
  observed route/message/job/entity/migration/config/AI-contract is
  homed; every leaf is connected to its owning node by an `artifacts:`
  edge; the router resolves representative tasks to small closures.
- *Absent with a named reason* — the collection is empty because the
  **source has no such evidence**, and that absence is stated explicitly
  in the completeness ledger with the paths searched.

Any collection neither fully covered nor explicitly absent-with-reason
is an incomplete growth. "Ran out of context", "seemed enough", "the
templates are present", and "the common cases are done" are the failure
the contract forbids. Template files existing at their paths is never
coverage; only authored, source-cited content is.

**The growth completeness ledger.** Before declaring growth done, the
orchestration chat fills one ledger (schema:
`growth-completeness-ledger.md`) — a table over every collection in the
unified shape plus every subsystem/stack/cross-cutting node — marking
each `covered` (with counts and strongest source paths), `absent` (with
reason and searched paths), or a named `unknown` blocker. It is a
seed-organ transient written to the plant's gitignored
`.cypress/growth/completeness-ledger.md`, never under `docs/graph/`. A
collection may not be left blank. This ledger is part of the delivery
block and is what Phase 6 validation audits against.

**No early stop.** Growth ends when the ledger shows every collection is
covered-to-evidence or absent-with-reason, Phase 6's independent
validation passes, and the maturity test is met against the graph — not
against the file tree. A fatal host limit, a two-round non-converging
finding (`recover`), or an unclosable evidence gap is delivered as an
honest `unknown` with the blocker named — the one legitimate way a
collection stays uncovered, and it is reported, never silent.

### The growth flow (`grow.growth-flow`) — six phases

**Phase 1 — Detect and plan.** Determine whether the target is
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

**Phase 2 — Scout and establish evidence.** Spawn the planned
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
scouting; record which ledger owns each contested fact.

**Phase 3 — Model and author through Opus workers.** Configure
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

**Phase 4 — Grow source-backed leaves.** Through bounded Opus authors,
populate every collection supported by evidence: `product/`
(actors/capabilities/flows/constraints/observed behavior);
`architecture/` (context/components/boundaries/runtime flows/dated sharp
edges); `api/` (observed HTTP/RPC/event/job contracts + source
locations); `data/` (entities/ownership/persistence/migrations/
lineage/privacy); `libraries/` (every direct dependency indexed; rich
pages for significant ones); `legal/` (only when subject to
externally-authored rules — check `legal-corpus/` first, re-confirm
`verified`/`legal_status` against the publisher); `sources/`;
`prompts/` and `evaluations/`; `runbooks/verification.md` (exact
commands, labeled `discovered, not executed`); `plans/grill.md`
(evidence, gaps, next increment); `best-practices/`; `changelog.md`.
Prepare `specs/` and `decisions/` indexes but do not manufacture
records — formalize a spec only from a real observable, an ADR only from
a decision the source shows. Where a ledger's specialist-agent signal
genuinely warrants it, author a project-specific expert agent; a signal
is a candidate, not a mandate.

**Phase 5 — Connect and fertilize.** Dispatch an Opus librarian to
ensure every leaf has an owning-node edge, every node is reachable,
searchable paths/symbols/commands live in the right home, unknowns are
answerable questions with likely evidence locations, and the router
stays compact. Depth belongs behind edges, not in the always-loaded
router or oversized nodes.

**Phase 6 — Independent validation.** Dispatch separate Opus reviewers
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
no-evidence). Under-growth is a defect on equal footing with
over-growth. Route findings to bounded Opus authors and repeat
validation — **bounded by the recover discipline**: a finding surviving
two author-fix → revalidate rounds is not converging; stop, record it as
an honest unknown or defect, hand the decision to the user. Do not
weaken the linter or loop a fourth time. Also configure the
spec-coverage gate (`TEST_GLOBS` in `spec-lint.py`) while the stack
evidence is fresh.

### Delivery and maturity

The orchestration chat reports target boundary/revisions, worker
assignments, evidence inspected, artifacts created/refreshed, validation
results, untrusted/excluded docs, honest unknowns, and one next action —
**with its tier** (kernel §0). It includes the **growth completeness
ledger** (every collection covered-to-evidence or absent-with-reason) so
the delivery proves totality instead of asserting it, plus growth
metrics (scouts and authors spawned, contradictions resolved,
findings raised and fixed, evidence gaps left open) — the plant's birth
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

- **id:** `protocol.initialize` — tier 2
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
prompt and grow protocol without weakening them — the orchestration,
model-class, routing, and evidence policy is grow's and
`INSTALL_PROMPT.md`'s to define, never re-listed here.

### The adapter's own hard edges (`initialize.adapter-edges`)

The adapter adds only these edges of its own:
- the roster this adapter installs is not spawnable in the session that
  installed it — preflight and remedy per
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

- **id:** `protocol.harvest` — tier 2 (note: no `command: true`)
- **owns:** `harvest.fold-back-flow`, `harvest.agnosticism-gate`
- **requires:** —
- **peers:** `protocol.graft`, `protocol.grow`
- **load_when:** "harvest lessons back into the seed"; "fold
  generalizable improvements upstream"; "the plant is mature, propose a
  harvest"; "seed improvement from project experience"

### What it does

Harvest is the inverse of grow. `grow` runs the seed *into* a project
and grows it; harvest runs the other direction — a mature project *back
into* the seed — so the next project starts ahead of where this one did.
A seed that only seeds cannot improve; a seed that harvests carelessly
rots into one project's specifics. Harvest is the disciplined gate that
lets the seed compound **without** losing its agnosticism. It takes only
the seed-worthy essence of what the plant learned — never the plant's
flesh. What goes back in must be true for *any* future plant.

### Trigger — manual only, never automatic

Harvest is **user-sovereign**. Unlike `canonize`, it is never triggered
automatically, on a schedule, by a hook, or as a "while I'm here" step.
- **The user starts it** — by invoking this protocol or pasting
  `HARVEST_PROMPT.md`.
- **The system may, at most, PROPOSE it** — when a mature plant clearly
  holds generalizable lessons, an agent may *suggest* "this looks worth
  harvesting" and stop. The suggestion is a doorbell, not an entry.
- **Nothing reaches the seed until the user is satisfied.** Every
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

**Gate 1 — Agnosticism (the heart).** "Would this help an arbitrary
next project, in a different language, framework, and domain, that has
never heard of this plant?"
- **YES, verbatim** → harvest as-is (rare — usually only tool-neutral
  rules).
- **YES, once generalized** → rewrite it stripping every plant-specific
  name, domain term, stack pin, path, and example, then harvest the
  generalized form; state the before→after explicitly.
- **NO** → reject; record why; leave it in the plant.

Fail-closed corollary: **if you cannot state the lesson without naming
the plant, it is not ready to harvest.** A single leaked project name,
domain noun, credential, dataset shape, or version-pinned specific in
the seed is a failed harvest — worse than a missed lesson.

*What counts as a project reference* (all forbidden in the seed,
including in the CHANGELOG entry, harvest-log row, provenance notes, and
illustrative examples): a **name** (plant, product, company, service,
internal tool); a **stack fingerprint** (the language/framework/datastore
combo that identifies the plant); an **identifying count or metric**; a
**description of the plant's internals** (file names, config keys,
plugin names, module wiring, a security finding on its own code); a
**path, host, port, credential, or absolute install location**; an
**illustrative example framed as the plant's own** (recast every example
in the generic). Plant-identifying provenance belongs only in the
ratification proposal shown to the steward, never in the seed's
committed files.

**Gate 2 — Durability (surface, not pin).** "Will this still be true a
version from now — is it about the library, or about one pinned release
of it?"
- **KEEP (surface, durable):** the capability the library provides; its
  core API shape and canonical usage; idioms/best practices that hold
  across lines; conceptual gotchas; the upstream doc/repo home.
- **REJECT (pinned, ephemeral):** CVEs/advisories tied to an exact
  version; "version X.Y.Z is a breaking marker"; per-release
  deprecations; upgrade/migration diffs between pins; a resolved-version
  number itself. These belong in the plant's
  `docs/graph/libraries/<name>.md`. When in doubt, a fact is pinned —
  drop it.

**Gate 3 — Non-redundancy (does the seed already own this?).** "Does the
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

**Phase 1 — Survey the mature plant (Sonnet scouts, read-only).**
Inventory how the plant diverged from the seed and what it accumulated.
A prior `graft`'s customization-audit ledger and its KEEP-PLANT list
(`tools/graft-audit.py` output) is a ready-made divergence inventory —
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
only *quantitative* donor surface — mine the *pattern*, propose the seed
change); and a capability the seed ships that stays inert across plants
(harvest the *fix to the seed's own machinery*). Output: a **candidate
ledger** with provenance per row.

**Phase 2 — Triage against all three gates (Opus authors).** For each
candidate, apply agnosticism, durability, and non-redundancy, and decide
KEEP-AS-IS / GENERALIZE / REJECT. For anything kept, write its
**generalized restatement** with the before→after shown (what
plant-specifics *and* pinned specifics were stripped). Reject rows carry
a one-line reason (including "redundant — the seed already owns this at
`<home>`"). Be conservative — when in doubt, reject or generalize
harder.

**Phase 3 — Backport authoring (Opus authors).** Apply each surviving
generalized improvement to the SEED artifact it belongs in (`skills/`,
`protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit** — integrated as if
it had always been there. Every fold-back records provenance (plant
lineage, generalization applied, seed files touched). A harvested
tooling fix arrives with its regression test generalized alongside it.

**Phase 4 — Seed integrity gate (fail-closed).** The seed must leave
harvest more capable and no less agnostic:
- **Agnosticism scan** — grep the *entire* diff (including CHANGELOG,
  harvest-log, provenance notes) for any plant name, domain noun, stack
  fingerprint, identifying count, internal-component/file/config name,
  path, credential, dataset shape, or version pin. Any hit BLOCKS.
- **Self-consistency** — run the seed's own lints/tests; kernel,
  manifest, protocol table, and registries stay in sync.
- **Clean install** — a dry-run install into a scratch target still
  succeeds and is additive.
- **Minimum-sufficient fold-back** — generalize an existing rule rather
  than appending a sibling; land the lesson in the cheapest surface that
  reaches its audience (a reference file before a protocol, a protocol
  before the kernel — kernel bytes cost every session of every plant);
  prefer the smallest edit.
- **Version + provenance** — bump the seed version, add a CHANGELOG
  entry and a harvest-log row; each check names its command and result.

**Phase 5 — Deliver (propose, do not impose).** Harvest **proposes**;
the human steward **ratifies**. Emit the fold-back as a reviewable
patch/proposal — never a silent mutation of the seed.

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

Two disciplines are special. **Legal currency:** an entry states whether
its text is the **original** or the **consolidated/as-amended** edition
(the amendment trap), and a `verification_grade` is **never upgraded
without a new fetch** — downgrading on new evidence is expected,
upgrading without re-reading is falsification. **Expert promotion:**
harvested roles land in the **catalog** by default, never straight into
the always-loaded roster; promotion to the base roster is a separate,
steward-only decision whose bar is higher than "useful" — the mandate
must be *universal* (every project produces the thing it addresses) and
uncovered by any base agent. Harvest may *propose* a promotion; it never
performs one.

### Output — two distinct records

Harvest produces two records that do **not** carry the same content:
1. **The ratification proposal** — stated in chat / the PR for the
   steward. It *may* name the plant and show every before→after
   generalization. It is **never committed to the seed.**
2. **The seed-committed record** — the CHANGELOG entry and harvest-log
   row that land inside the seed, bound by the agnosticism gate: no plant
   name, stack fingerprint, count, internal name, or "from <this stack>
   plant" line. It records *that* a harvest happened and *what*
   generalized lesson landed — never *whose* plant it came from.

### What you do not do

- Start a harvest on your own (the most an agent does unprompted is
  *propose* one and stop).
- Merge a fold-back the user has not ratified.
- Harvest a plant that is still churning.
- Copy project-specific facts, names, domain terms, stack pins/
  fingerprints, counts, internal names, paths, secrets, or datasets into
  the seed — the agnosticism gate is absolute and applies to every
  committed byte.
- Harvest a self-healing/diagnostic case **narrative** — only its
  generalized prevention rule.
- Harvest the plant's `docs/graph/` content.
- Break the seed's clean install or agnosticism to land a lesson.
- Silently mutate the seed, or fold a change in without provenance and a
  proof.

---

## graft

*Source: `protocols/graft.md`*

- **id:** `protocol.graft` — tier 2 (note: no `command: true`); the
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
third side — it carries the enriched seed **outward onto an existing
plant**, so a plant grown from an older seed inherits everything the
seed has learned since, without being torn up and regrown.

The garden metaphor is load-bearing: you graft the new scion onto the
living rootstock. The **rootstock** is the plant's own life — its source
code and the knowledge it authored about itself — and it is inviolate.
The **scion** is the seed's evolved machinery: kernel, protocols,
skills, agents, templates, shared tooling, and the library/tool corpus.
Harvest and graft are one circulatory system: harvest is **collection**
(one plant's lessons up into the seed), graft is **distribution** (the
enriched seed back out to every sibling plant).

### Trigger — user-decided (`graft.user-sovereignty`)

Like harvest, graft is **user-sovereign**. It changes an established,
possibly production plant, so the **steward** decides when a plant is
upgraded and ratifies before it is applied.
- **The user starts it** — by invoking this protocol or pasting
  `GRAFT_PROMPT.md` with a plant (or a set of sibling plants).
- **The system may PROPOSE it** — most naturally as the tail of a
  `harvest`: "the seed now carries fruit that plants X, Y, Z predate —
  each is due for a graft" and stop.
- **Every upgrade is ratified before it lands.** Graft reconciles, then
  proposes the reconciled diff; the steward ratifies. An unratified
  graft is a draft. Because every replacement is backed up first, a
  ratified graft is also reversible.

### When to invoke

- The **user** has asked to graft, or ratified a proposal.
- The plant is **grown and steady** — its graph routes, its
  plan-of-record is closed or calm. Grafting mid-churn muddies both.
- The seed has **moved on** since the plant grew — a harvest folded in
  new fruit, a protocol sharpened, the corpus grew pages. The wider the
  gap, the more the plant gains.
- The plant's working tree is **clean** (or the steward accepts a
  backup-only safety net).

### The rootstock line — the heart

Harvest's heart is the agnosticism gate (*nothing project-specific
enters the seed*). Graft's heart is its mirror, the **rootstock line**:
*nothing the plant authored about itself is overwritten by the upgrade.*

Two territories, and graft writes to exactly one:
- **Seed-owned machinery (graft's to upgrade):** the kernel
  (`CLAUDE.md`/`AGENTS.md`/`.github/copilot-instructions.md`); the
  seed-owned graph subtrees
  `docs/graph/{protocols,skills,agents,method,templates}/` (every node
  marked `origin: seed`); the harness projections (`.claude/agents/`,
  `.claude/skills/`, and the `.prime/agent/`, `.opencode/`, `.codex/`,
  `.github/` equivalents); tool-specific commands/settings/hooks; the
  shared router script `docs/graph/agent-lint.py`; and the graph engine scripts
  `docs/graph/{graph-lint.py,spec-lint.py}` (preserving the plant's
  configured `TEST_GLOBS`). `_schema.md` and `index.md` are
  project-instantiated and stay the plant's, always.
- **The plant's own life (graft preserves, always):** the plant's
  application source, and every knowledge fact the plant authored under
  `docs/graph/` — its `nodes/`, `specs/`, `decisions/`, `libraries/`,
  `plans/`, `runbooks/`, product/architecture/API/data, any node
  **without** `origin: seed`, and the pinned version-specific facts in
  its library and tool pages.

> **The rootstock line:** the plant's source and its authored
> `docs/graph/` facts stay as the plant left them. If an upgrade cannot
> land without rewriting something the plant authored, it stops at the
> line and becomes a proposal for the steward — never a silent
> overwrite.

The one nuance: a plant's library and tool **pages** are plant-owned,
yet graft may refresh their *surface* from the enriched corpus (Phase
4) — renewing only the version-durable orientation and re-pinning the
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
survives. Anywhere a plant falls short — machinery outside the graph, a
fact with two homes, an always-loaded file that should be a node, a
hand-maintained projection drifting from source, dead compatibility
residue — it is drift, and closing it is in graft's scope. Graft
executes this as holistic reconstruction: reconstruct from evidence not
preference; one home, natural owner; integrate don't bolt on;
minimum-sufficient, sliced, reversible; verify and fix drift at its
home. The pre-6.0 layout migration is the *maximal instance* of this
mandate; the mandate is **standing** — even a plant one version behind
gets audited and rebalanced as Phase 6, every graft.

### The three-way reconciliation (`graft.reconcile-flow`)

A plant is not a blank target; its steward may have locally sharpened a
protocol, adjusted a setting, or fixed a script. Graft reconciles three
versions of every seed-owned artifact:
- **base** — the seed revision the plant grew from (read from the seed
  stamp; reconstructed from install backups or content lineage on a
  first graft);
- **theirs** — the artifact in the seed today;
- **ours** — the artifact as it stands in the plant.

Each artifact takes one of three clean paths:
- **FAST-FORWARD** — the seed advanced and the plant left the artifact
  pristine. Adopt the seed's new version outright (the common case and
  the bulk of a graft's value).
- **KEEP-PLANT (and flag upstream)** — the plant diverged and the seed
  did not. Keep the plant's version untouched, and record the divergence
  as a **harvest candidate**. Graft's outbound pass feeds the inbound
  loop.
- **MERGE** — both advanced the same artifact. Reconcile as a single
  **holistic re-integration**: one coherent file carrying the seed's new
  capability *and* the plant's intent, surfaced to the steward as a
  reviewable proposal. A three-way conflict is a decision, and the
  decision is the steward's.

### The flow — eight phases

Orchestrated like grow/harvest; Sonnet-class survey (read-only),
Opus-class for every reconciliation, merge, corpus refresh, and
validation. Every worker runs the plant's router
(`graph-lint.py --plan`) before reading plant source.

**Phase 1 — Locate the plant and establish the base (session + Sonnet).**
Identify the plant or sibling set; record path, host integration,
branch, HEAD, worktree cleanliness (provenance, no Git mutation). Read
the plant's **seed stamp**; on a first graft with no stamp, reconstruct
the base from install backups (`*.bak-*`) or content lineage. Confirm
the seed's version and what changed between base and now (its CHANGELOG
and harvest log are the map of available fruit).

**Phase 2 — Survey the drift (Sonnet scouts, read-only).** Inventory
every seed-owned artifact and classify its three-way state as a first
guess at FAST-FORWARD / KEEP-PLANT / MERGE. In parallel, inventory the
**fruit the plant can withdraw**: libraries, tools, and legal
instruments the plant reasons against for which the corpus now holds a
page the plant predates or lacks. Return a **graft ledger** — one row
per artifact or withdrawable page.

**Layout migration 5.x → 6.0.0** (between survey and reconcile, when the
survey finds a pre-6.0 plant whose machinery lives in
`.claude/protocols/`, `.claude/templates/`, `.claude/core/` instead of
the graph subtrees): (a) install the new machinery into `docs/graph/`
as `origin: seed` nodes and regenerate projections; (b) diff old
tool-dir copies against their seed base — a plant-local customization is
carried into the graph copy as a holistic MERGE and also raised as a
harvest candidate; (c) relocate the plant's OWN agents and skills into
`docs/graph/{agents,skills}/`, holistically reconciled — add the node
frontmatter they lack, trim every restated fact to a cross-reference,
regenerate the `.claude/` projection; (d) list the now-redundant old
machinery — the **steward** confirms deletion explicitly, by name (graft
never deletes unprompted); (e) rewrite stale references in
plant-authored docs only with the steward's consent; (f) sweep the
plant's own pre-graph knowledge — a migration this old owes a
fact-sweep, not just a machinery swap: dispatch read-only scouts across
the plant's actual source to inventory facts missing from the graph,
cross-checked against existing nodes, and hand confirmed findings to
Opus authors to weave into the owning node.

**Phase 3 — Reconcile the machinery (Opus authors).** For each
seed-owned artifact apply the three-way reconciliation: adopt on
FAST-FORWARD; retain and raise a harvest candidate on KEEP-PLANT; author
one holistic re-integration on MERGE. Every merged file arrives whole,
never a seed block bolted beside a plant block. **The roster delta is
not spawnable in this session** — preflight and take the remedy
(`delegation.harness-registration`); carry the delta forward as a named
list for Phase 7. **The graph engine is machinery too** — the installer
drops the scaffold only if absent, so a plant that already has them
keeps its OLD engine and misses every linter improvement. Reconcile the
engine as a config-preserving fast-forward: adopt the seed's current
engine body and re-inject the plant's PROJECT CONFIG (`ROOT_ID` /
`KINDS` / `KIND_PREFIX` in `graph-lint.py`; `TEST_GLOBS` in
`spec-lint.py`). A config knob the seed has *extended* is **UNIONED**,
not re-injected wholesale — the load-bearing case is `KINDS` (6.0.0
added `protocol`/`skill`/`agent`/`method`; keeping the plant's older set
verbatim would fail every new machinery node with `kind not in KINDS`).
`tools/graft-graph-engine.py` performs this merge.
`_schema.md`/`index.md` stay the plant's (project-instantiated). **The
installer fast-forwards blindly** — a mandatory post-FF audit (Phase 7,
`tools/graft-audit.py`) catches any local divergence a blind FF buried.

**Phase 4 — Refresh the plant's knowledge from the corpus (Opus
authors).** For each withdrawable library/tool page, **seed the refresh
from the corpus as the orientation layer**, then re-pin the plant's
version-specific facts fresh against the plant's real lockfile. A
withdrawable **legal** page adds one non-negotiable step: re-confirm each
entry's `verified` date and `legal_status` against the publisher, and
never copy a determination. **One home per dependency** — merge the
corpus orientation into the plant's existing page, never add a parallel
one, and do not mirror the corpus's own internal sub-namespace grouping
into the plant (that would create a duplicate home the Phase 7
minimum-sufficiency gate BLOCKS on).

**Phase 5 — Grow the new capabilities onto the living plant (Opus
authors).** Fast-forwarding *carries* a capability; it does not *grow*
it. **Grafted is not grown.** For each new or newly-enriched capability:
grow what the plant evidently needs, grounded in its own facts
(instantiate a suggested skill/expert the plant's stack calls for,
withdraw a corpus library/tool/legal page it actually uses, ground a
runbook it can fill). **Never fabricate to fill a surface** — a project
skill, ADR, or runbook whose content can only come from real recurring
use sprouts during use, owned by the close-out lifecycle (`canonize` →
`docs-librarian`), not by the graft. **Surface what was grafted but not
grown** so the steward sees the copy-but-not-actualized state. **An
own-kernel plant** (one that carries no seed machinery) still receives
the substance — as a **weave**, not a summary: map each seed surface the
delta changed to the plant's equivalent surface and land each rule where
it acts, in the plant's idiom. Collapsing the delta into one summary
section is a photocopy, not a graft.

**Phase 6 — Rebalance the plant toward pure graph (Sonnet audit → Opus
authors).** The reconstruction pass, on **every** graft. (1) Inventory
the drift as a rebalance ledger, hunting: machinery outside the graph; a
fact with two homes; a hand-maintained projection drifted from its node;
obsolete residue; substantive thinness (the (f) sweep, now standing). (2)
Reconstruct in slices bounded by the rootstock line — move each item to
its natural node home as a holistic MERGE, collapse duplicate homes,
regenerate drifted projections, list obsolete residue for the steward's
explicit deletion confirmation. Every relocation preserves the fact
itself. (3) Leave the drift closed at its home; install a missing
fitness function the seed now ships; surface any residual drift with a
remediation.

**Phase 7 — Apply, verify, and stamp (Opus authors; session gates).**
Apply the ratified upgrade **additively**, backing up every replaced
file first. Then prove the plant is left more capable and no less
itself:
- **Rootstock intact** — the plant's source and authored facts are
  byte-for-byte unchanged outside machinery and the deliberately
  refreshed surfaces. Any unexpected change BLOCKS.
- **Customization audit** (`tools/graft-audit.py`) — any seed-owned file
  whose backup differs from the seed *and* carries plant-signal content
  is a divergence the blind FF overwrote; re-integrate or ratify. An
  un-reintegrated, un-ratified customization BLOCKS.
- **Machinery healthy** — the plant's graph still routes on the upgraded
  engine; the agent router lints and evals clean; internal links and
  edges resolve. Report the **roster delta** as work the plant's next
  session registers.
- **Minimum-sufficient upgrade (the graft reviewer)** — every capability
  grown cites the plant evidence that demanded it, every MERGE is the
  smallest re-integration, every refreshed page serves a used dependency,
  no artifact lands without a consumer. Over-delivery is a finding, not a
  bonus.
- **Pure-graph integrity (the rebalance gate)** — the plant ends the
  graft at least as purely a graph as the seed's spec requires; no
  machinery outside a node, no duplicate home, no drifted projection, no
  unlisted residue. Any residual drift is surfaced with a remediation.
- **Cross-author rebalance** (only if reconciliation/growth/rebalance/(f)
  used parallel authors) — run **one** final docs-librarian spawn to
  catch one-home-per-fact violations across author boundaries, register
  drift, and a stale shared summary file; follow with a structural audit
  (right `kind`, topology map lists every added node, `requires:`/`peers:`
  edges reflect the body). A green `graph-lint` proves well-formedness,
  not that a parallel absorption reconciled correctly.
- **Stamp + provenance** — record the seed version the plant now carries
  in its seed stamp, and add a provenance entry to the plant's own
  `docs/graph/changelog.md`; each check names its command and result.

**Phase 8 — Deliver (propose, then ratify).** Graft **proposes**; the
plant's steward **ratifies**. Emit the reconciled upgrade as a reviewable
patch/proposal, hand the KEEP-PLANT divergences back as harvest
candidates, and end with the single highest-leverage next step.

### Provenance & the seed stamp

Graft reads and maintains a lightweight, **plant-owned** stamp — a
`.cypress/seed.json` marker or equivalent — recording the seed name, the
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

- **Kernel eight rules → owning protocol:** 3.1 specify (`rule.spec`),
  3.2 context-router (not a protocol node), 3.3 grill (`rule.grill`),
  3.4 test-first (`rule.test-first`), 3.5 verify (`rule.verify`), 3.6
  deliver (`rule.deliver`), 3.7 canonize (`rule.canonize`), 3.8
  toolcraft (`rule.toolcraft`).
- **The delivery funnel:** brainstorm* → specify → grill →
  ingest-library* → test-first → verify → canonize →
  deliver; recover on any failure.
- **The seed meta-loop:** grow (seed → new plant), harvest (mature plant
  → seed, user-triggered), graft (enriched seed → existing plant,
  user-triggered), initialize (coding-tool adapter → grow).

*End of protocols reference. Every fact above is drawn from the files in
`protocols/*.md` and the kernel `core/AGENTS.md`.*
