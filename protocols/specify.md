---
name: specify
description: Author an executable specification under docs/graph/specs/SPEC-NNNN-<slug>.md through a phased pass — product (§3), architect (§4 §5 §6 §7 §8), then product (§9) and tester (§10, testability) side by side, security where the surface is sensitive — signed off in §0 while still draft; the spec turns active only when its RED tests land. Use whenever a goal is clear but no spec covers it, an existing feature's contract is changing, or a bug investigation reveals an implicit contract that needs to be made explicit. Specs are the source of truth for behavior — do not write code without one.
id: protocol.specify
tier: 2
kind: protocol
origin: seed
title: specify — authoring the executable spec that is the source of truth for behavior
owns:
  - rule.spec
  - specify.flow
  - specify.revision-discipline
requires:
peers:
  - protocol.brainstorm
  - protocol.grill
artifacts:
  - templates/spec.template.md
  - templates/knowledge-graph/spec-lint.py
load_when:
  - "write a spec, no spec covers this behavior"
  - "new feature, endpoint, job, or LLM interaction to define"
  - "changing an existing feature's contract"
  - "bug revealed an implicit or missing contract"
  - "acceptance criteria, Given/When/Then, failure modes"
est_tokens: 1750
command: true
---

# Protocol: specify

Use this when the goal is clear and you need to produce an executable
specification before planning the implementation. The deliverable is a
new (or refreshed) file in `docs/graph/specs/` populated through every
section of `docs/graph/templates/spec.template.md`, signed off by
product, architect, and tester.

This node owns **the spec rule** — specs are the source of truth for
*behavior*. Every non-trivial behavior — feature, endpoint, job,
significant function, LLM/VLM interaction — has a spec in
`docs/graph/specs/`, written before the code, using the template with
stable section numbers. Specs are executable: every functional
contract maps to at least one test (the test-first rule enforces
this). Superseded specs stay on disk with status `superseded` and a
link forward, catalogued in `docs/graph/specs/index.md`. If wiki and
spec disagree about how a library *can* be used, the wiki is right;
if product and spec disagree about what to build, fix the spec.

This protocol is the bridge between "we know what we want" and "we
have a plan". The spec is the contract that the plan will implement
and the tests will enforce.

## Entry conditions

One of:
- `brainstorm` has just converged on a problem statement and a first
  useful slice; the next step is to specify what that slice does.
- An existing feature is being changed in a way that affects its
  contract (new behavior, behavior removal, behavior change).
- A bug investigation revealed that the original spec was incomplete
  or wrong.
- An ADR introduces a new system behavior that needs a spec.

## The pass (`specify.flow`)

The pass is a sequence of phases, each filling named sections with a
named owner. **The table is the spawn order**: a phase's spawn is issued
only after every handback it needs has returned, and two phases run
side by side only where the last column says so
(`delegation.sequencing`, `docs/graph/method/delegation.md`). This is
spawned, clean-context work: if the host cannot spawn workers of the
required model classes, stop and report the unsupported operating model
— never simulate the personas in the orchestration chat. A specialist
the host has no *type* for is a different condition and does not stop
the pass (`delegation.harness-registration`).

| Phase | Sections | Owner | Needs | Parallel with |
|---|---|---|---|---|
| 0 | identifier; §0 Metadata, §1 Summary, §2 Scope | orchestrator, in-session | brainstorm output or the clear goal | — |
| 1 | §3 User-facing behavior | `product` | §2 | — |
| 2 | §4 Contracts, §5 NFRs, §6 Data shapes, §7 Failure modes, §8 Examples | `architect` | §3 | — |
| 3 | §9 Acceptance criteria | `product` — each criterion maps to §4 slugs | §4 | phase 4 |
| 4 | §10 Test mapping; testability review of §4 | `tester` | §4, §7, §8 | phase 3 |
| 5 | adversarial failure modes into §7, abuse cases into §5 | `security`, when the surface is sensitive | §4, §7 | phases 3–4 |
| 6 | §11 Open questions; sign-offs in §0; §12 entry; grill.md §3/§9 links | orchestrator, in-session; the signers tick §0 | phases 3–5 | — |

What the table cannot hold:

- **The identifier comes from disk.** `SPEC-NNNN-<slug>` takes the next
  free number among `docs/graph/specs/SPEC-*.md`; the catalog row in
  `docs/graph/specs/index.md` is a fact-bearing surface the
  `docs-librarian` writes at close-out (`protocol.canonize`), not a
  mid-pass spawn. Until then the file on disk is the registration.
- **§3 before §4, §4 before §9.** `product` writes the user's view
  first, in the user's vocabulary; `architect` turns it into named,
  single-outcome Given/When/Then contracts with their data shapes,
  failure modes, and three real examples; only then can `product` map
  each acceptance criterion to the slugs it accepts. A §9 written
  beside §3 maps to nothing.
- **§10 is the executable view.** `tester` writes one row per contract
  and per failure mode (status `pending`) and runs the testability
  review of §4: observable from outside, measurable in §9, fixtures
  writable from §6, failure modes triggerable in a test environment. A
  contract that fails the review goes back to `architect` — phase 2
  again for that contract — and that return is an attempt under
  `protocol.recover`'s three-attempt boundary, not a free loop. A spec
  that cannot be tested is not a spec; it is a description.
- **Sensitive surface** — auth, secrets, payments, file uploads,
  external integrations, LLM/VLM behavior that acts on data — adds a
  `security` review: abuse cases become failure modes in §7 or
  requirements in §5.
- **Sign-off is not promotion.** `product` ✓ confirms §3 and §9 reflect
  the outcome, `architect` ✓ that §4 §6 §7 cohere, `tester` ✓ that every
  contract is testable, `security` ✓ where it reviewed — each ticked in
  §0 while the spec is still `draft`. The status moves to `active` in
  the change that lands its RED tests (`test-first`'s COMMIT; the moment
  is owned by `verify.status-evidence`), and to `implemented` when every
  contract is green. A live status over an empty assertion set is a
  false green, and `spec-lint.py` counts only live specs — so a signed
  draft is planned against and encoded, never reported uncovered.
- **Hand-off.** A signed draft is what `grill` plans against: its §4
  contracts are the rows §9 of grill.md maps increments to, in
  increments small enough for one RED-GREEN-REFACTOR cycle (or a small
  handful).

## Revising an existing spec

When behavior changes:
1. Read the existing spec.
2. Decide: is this a *clarification* (the spec was unclear, the new
   text says the same thing better) or a *change* (the behavior
   itself is different)?
3. Clarifications: edit in place; add a row to the spec's §12
   Changelog with the clarification.
4. Changes: copy the spec to a new identifier, mark the old spec
   `superseded` with a link to the new one, write the new spec from
   the change. Update everything that depended on the old.

Specs never silently change behavior. The catalog tells the next
agent "this used to behave like X; now it behaves like Y; here is
when it changed and why."

## Exit conditions

"Populated" means every section §0–§12 carries either content or an
explicit one-line `not applicable — <reason>`; a template placeholder
is neither.

- `docs/graph/specs/SPEC-NNNN-<slug>.md` exists, populated, status
  `draft` with product ✓ architect ✓ tester ✓ (security ✓ where it
  reviewed) in §0.
- Every §4 contract has a §10 row; every §9 criterion maps to a slug
  that exists; every failure mode in §7 names its contract.
- §11 is empty, or every row's current assumption is a flagged
  assumption in grill.md §12.
- grill.md links the spec from §3 and §9.
- `python3 docs/graph/spec-lint.py` exits 0 — the shape checks above,
  mechanically, for every spec on disk.

## Anti-patterns

- **The spec is the README.** Specs are not marketing. They are
  contracts, executable, exhaustive about behavior.
- **The spec describes the implementation.** Specs describe
  *behavior* — what the system does, not how. "Stores the user
  record in a Postgres table" is not a spec; "User records persist
  across restarts and are retrievable by ID" is.
- **No failure modes section.** A spec that only describes the happy
  path is half a spec.
- **No examples.** Examples are the bridge between the abstract
  contract and the concrete test.
- **Spec written after the code.** That's a description, not a
  spec. It is still better than no document, but mark its status as
  `back-written` so the team knows.
- **§9 written beside §3.** An acceptance criterion that maps to no
  slug, because the slugs did not exist yet. §9 waits for §4.
- **Promoted at sign-off.** An `active` spec with no test is a red
  gate for the whole test-first phase and a false green the moment
  someone silences it. Sign in §0; promote with the RED.
