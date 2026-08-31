---
name: specify
description: Author an executable specification under docs/graph/specs/SPEC-NNNN-<slug>.md, coordinating product (§3 user behavior, §9 acceptance), architect (§4 contracts, §6 data shapes, §7 failure modes), and tester (§10 testability review, test mapping). Use whenever a goal is clear but no spec covers it, an existing feature's contract is changing, or a bug investigation reveals an implicit contract that needs to be made explicit. Specs are the source of truth for behavior — do not write code without one.
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
load_when:
  - "write a spec, no spec covers this behavior"
  - "new feature, endpoint, job, or LLM interaction to define"
  - "changing an existing feature's contract"
  - "bug revealed an implicit or missing contract"
  - "acceptance criteria, Given/When/Then, failure modes"
est_tokens: 1500
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

## Who participates

- `product` — drafts §3 (User-facing behavior) and §9 (Acceptance
  criteria). Owns the user view.
- `architect` — drafts §4 (Functional contracts), §6 (Data shapes),
  and §7 (Failure modes). Owns the system view.
- `tester` — drafts §10 (Test mapping) and reviews §4 for
  testability. Owns the executable view.
- `docs-librarian` — registers the spec in `docs/graph/specs/index.md`
  and links it from grill.md.
- `security` — reviews when the spec touches auth, data, secrets,
  payments, file handling, or AI behaviors.

This workflow requires spawned clean-context workers. If the host cannot
spawn them with the required model classes, stop and report the unsupported
operating model; do not simulate the personas in the orchestration chat. A
specialist the host has no *type* for is not that condition and does not stop
the workflow — see `delegation.harness-registration`
(`docs/graph/method/delegation.md`) for the preflight, remedy, and recorded
fallback.

## Workflow

### 1. Allocate an identifier

Specs are numbered: `SPEC-NNNN-short-slug`. Find the next free
number in `docs/graph/specs/index.md`. File path:
`docs/graph/specs/SPEC-NNNN-<slug>.md`.

### 2. Draft from the template

Open `docs/graph/templates/spec.template.md` and fill in:

- **§0 Metadata** — id, status `draft`, owner, date, related grill
  section, related ADRs, related wiki pages.
- **§1 Summary** — one paragraph. What the spec covers and why.
- **§2 Scope** — explicit "in scope" and "out of scope" bullets.
- **§3 User-facing behavior** — what the user experiences, in user
  language. Reference `docs/graph/product/user-flows.md`.
- **§4 Functional contracts** — each contract is a Given/When/Then
  scenario, named, with one outcome. (See template.)
- **§5 Non-functional requirements** — performance budgets,
  security requirements, accessibility floor, latency, cost.
  Cross-link to grill.md §4.
- **§6 Data shapes** — schemas for inputs, outputs, persisted
  state. Use the language-agnostic schema convention in
  `docs/graph/templates/spec.template.md`.
- **§7 Failure modes** — for each contract, the named ways it can
  fail and what happens in each case. Failure is part of the spec.
- **§8 Examples** — concrete input/output pairs (one happy, at
  least one edge, at least one failure). These become the seed test
  cases.
- **§9 Acceptance criteria** — measurable conditions for "done".
  Each criterion maps to one or more contracts.
- **§10 Test mapping** — for each contract and each failure mode,
  the test(s) that cover it. Test names match contract names where
  practical.
- **§11 Open questions** — every "we will decide later" with a
  named resolution path.

### 3. Testability review

Before the spec leaves `draft`, the tester runs a testability pass:

- Is every contract observable from outside? (If you can't observe
  it, you can't test it.)
- Is every assertion in §9 measurable?
- Are the data shapes concrete enough that a test fixture could be
  written from them?
- Are the failure modes triggerable in a test environment?

If any of these fails, the spec goes back to the architect for
revision. A spec that cannot be tested is not a spec; it is a
description.

### 4. Security review (if applicable)

If the spec touches sensitive surface — auth, secrets, payments,
file uploads, external integrations, LLM/VLM behaviors that act on
data — security reviews it for abuse cases and adds them as
failure modes or non-functional requirements.

### 5. Promote to active

When product, architect, tester (and security if applicable) have
signed off, change the spec's status from `draft` to `active`.
Add it to `docs/graph/specs/index.md` and link it from grill.md §3
(User Goal) and §9 (Implementation Plan).

### 6. Hand off to `grill`

The next protocol is `grill`. The plan implements the contracts in
this spec, in increments small enough that each increment is one
RED-GREEN-REFACTOR cycle (or a small handful).

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

- `docs/graph/specs/SPEC-NNNN-<slug>.md` exists, status `active`,
  every section populated.
- `docs/graph/specs/index.md` has the row.
- grill.md links to the spec from §3 and §9.
- Every contract in §4 has at least one test in §10 (the test may
  not be written yet, but the mapping exists).
- Sign-off recorded: product ✓, architect ✓, tester ✓ (security ✓ if
  applicable).

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
