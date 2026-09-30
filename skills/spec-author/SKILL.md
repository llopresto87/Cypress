---
name: spec-author
description: Write an executable specification under docs/graph/specs/ that turns a clear goal into testable contracts. Use whenever a feature, endpoint, job, significant function, or AI interaction needs a contract that the tester can encode and the implementer can satisfy. Coordinates product (§3, §9), architect (§4, §6, §7), and tester (§10 testability review) into a single signed-off document. Specs are the source of truth for behavior (`rule.spec`).
id: skill.spec-author
tier: 2
kind: skill
origin: seed
title: spec-author — write executable specs whose contracts a tester can encode and an implementer can satisfy
owns:
  - spec-author.method
  - spec-author.sign-off
requires:
  - protocol.specify
peers:
  - skill.test-first
  - skill.grill-planner
  - skill.humanizer
load_when:
  - "write a spec"
  - "define functional contracts"
  - "given when then contract slugs"
  - "spec sign-off before code"
  - "code and spec disagree"
artifacts:
  - templates/spec.template.md
prevents: A spec whose contracts no tester can encode, which turns section 10 into a list of intentions and leaves the spec unfalsifiable.
est_tokens: 1640
---

# spec-author

This skill is the discipline of writing a spec that another agent can
turn into failing tests and another into passing code. It is invoked
from `docs/graph/protocols/specify.md`.

A spec is **executable** when every functional contract maps to at least
one test in the suite and the test name names the contract. Specs that
read like marketing or like implementations are not specs;
implementation detail belongs in grill.md §8.

## When to apply this skill

- `brainstorm` has converged and the next step is to formalize the
  behavior.
- An existing feature's contract is changing.
- A bug investigation revealed a contract that was implicit and is now
  being made explicit.
- An ADR introduces a new system behavior that needs a spec.

## How to write each section

### §1 Summary

One paragraph: what this spec covers and why, in the two sentences you
would give the next agent on the team before they implement it.

### §2 Scope

Two bullet lists: "in scope" and "out of scope". The out-of-scope
bullets are equally important. Reading the spec a year later, the
out-of-scope list is what tells the next agent "no, we considered that
and excluded it deliberately."

### §3 User-facing behavior (product)

Describe what the user experiences. Use the user's vocabulary, not the
system's. If the spec is for an internal API or a job, the "user" might
be another service or a developer: name them and describe their
experience.

### §4 Functional contracts (architect)

The heart of the spec. Each contract is one Given/When/Then, single-
outcome, observable from outside.

**Naming.** Use `UPPER_SNAKE_CASE` slugs that read as sentences. Tester
turns these into test names.

```
### Contract: SUBMIT_VALID_FORM_RETURNS_2XX
### Contract: SUBMIT_FORM_SCHEMA_INVALID
### Contract: SUBMIT_FORM_PERSISTS_RECORD
### Contract: GET_SUBMITTED_RECORD_RETURNS_BY_ID
```

The `### ` heading form is load-bearing: `spec-lint.py` only counts
`### Contract: SLUG` headings as live contracts, so a bare `Contract:`
line is invisible to coverage.

**One outcome per contract.** "Returns 201 *and* sends an email" is two
contracts: one for the response, one for the side effect. Many small,
single-outcome contracts compose into the behavior.

**Observable from outside.** If the test has to inspect a private field,
the contract is wrong. Move the observation to a public surface (a
returned value, a queried record, an emitted event).

### §5 Non-functional requirements

Only the constraints that bind this behavior; the template carries the
category list and the bind-only rule at point of use.

### §6 Data shapes (architect)

Schemas for inputs, outputs, persisted state. Use a language- agnostic
notation (YAML-like) by default; cross-link to native schema files when
they exist.

Required fields, types, allowed values, max sizes. These become test
fixtures and validation rules.

### §7 Failure modes (architect, with security)

For each contract, the named ways it can fail and what happens. This is
what separates a spec from a description: a happy-path-only spec is half
a spec.

```
Failure: SUBMIT_FORM_SCHEMA_INVALID
- Trigger: payload violates §6 schema
- Response: 422 with field-level error in body
- Side effects: audit log entry; nothing persisted
- Recovery: client may resubmit with corrections
```

Security adds adversarial cases here: prompt injection, tool hijacking,
data exfiltration when AI is involved.

### §8 Examples

Concrete input/output pairs. Three minimum: one happy, one edge, one
failure. Examples are the seed for test fixtures and turn abstract
contracts into concrete tests, so make them real values, not
`<placeholders>`.

### §9 Acceptance criteria (product)

Measurable conditions for "done". Each criterion maps to one or more
contracts in §4 and to one or more tests in §10.

Acceptance criteria include the non-functional ones (latency,
accessibility). Write them now, beside the functional ones, so the
tester can encode them.

### §10 Test mapping (tester)

A table mapping each contract and each acceptance criterion to the tests
that cover them. Update as tests are written. Status values: `pending`
(no test yet), `red` (test exists, fails), `green` (test exists,
passes), `skipped` (with reason).

### §11 Open questions

Every "we'll decide later" with a named resolution path. A spec with
open questions stays in `draft`.

## The sign-off rule

A spec is signed when every sign-off below that applies is recorded;
until then it is unsigned and nobody plans against it:
- **product ✓** confirms §3 and §9 reflect the user outcome.
- **architect ✓** confirms §4, §6, §7 are coherent.
- **tester ✓** confirms every contract in §4 is testable (the
  testability review).
- **security ✓** if the spec touches auth, secrets, payments, uploads,
  external integrations, or AI behaviors that act on data.

Sign-off goes in §0 (Metadata), and the signed spec stays `draft`.
Sign-off says the contract is authoritative; `active` says it is under
test. The signed spec moves to `active` in the change that lands its
first RED tests (`test-first`'s COMMIT; `verify.status-evidence` owns
the moment), and to `implemented` when every contract is green. A live
status over an empty assertion set is a false green: `active` with no
test is a red gate until RED lands, and a false green once someone
silences it.

Before a spec is signed, its prose passes
`docs/graph/skills/humanizer.md` in file mode and
`python3 docs/graph/prose-lint.py --file <spec> --against HEAD` reports
no strong tell and no dropped contract slug, number, or code span.

The sign-offs are judgment; the shape and the coverage are mechanical.
`python3 docs/graph/spec-lint.py` (the kernel §3.1 gate in the gate
table of `docs/graph/protocols/verify.md`) checks every spec's shape
(unique slugs, a §10 row per contract, §9 criteria that map to real
slugs, sign-offs present on anything past `draft`) and, for live specs,
that every slug appears in at least one test. A draft is shape-checked
and not counted for coverage, so a spec in authoring never reports
uncovered.

## Spec drift management

When the code and the spec disagree, decide deliberately which side is
right (kernel §4 owns the boundary):
- **Code is right, spec is wrong:** edit the spec deliberately, add a
  §12 changelog entry, get re-sign-off.
- **Spec is right, code is wrong:** file a bug, add a regression test,
  fix the code.
- **Both partially right:** the brainstorm needs to revisit the
  contract; back up to `brainstorm` or `specify` and write a new
  version.

## Reference files

- `docs/graph/templates/spec.template.md` : the template.
- `docs/graph/protocols/specify.md` : the protocol.
- `docs/graph/protocols/test-first.md` : what happens next.
- `docs/graph/agents/01-architect.md`, `docs/graph/agents/04-tester.md`,
  `docs/graph/agents/08-product.md` : the three co-authors.
