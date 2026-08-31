<!--
Template: spec.template.md
Authored by: product + architect + tester (joint)
Lives at: docs/graph/specs/SPEC-NNNN-<slug>.md
Used: on every new behavior or behavior change
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them.
-->

# SPEC-NNNN: <short slug>

## 0. Metadata

- **Identifier:** SPEC-NNNN-<slug>
- **Status:** draft | active | implemented | superseded | back-written
- **Owner:** <agent or person>
- **Date:** YYYY-MM-DD
- **Last reviewed:** YYYY-MM-DD
- **Related grill section:** <#NNN in docs/graph/plans/grill.md>
- **Related ADRs:** <adr-NNNN-*>
- **Related wiki pages:** <docs/graph/libraries/*>
- **Supersedes:** <SPEC-NNNN-*>
- **Superseded by:** <SPEC-NNNN-*>
- **Sign-offs:** product [ ] · architect [ ] · tester [ ] · security [ ]

## 1. Summary

One paragraph. What this spec covers and why. No marketing, no
philosophy — just the scope of the behavior being contracted.

## 2. Scope

- **In scope:**
  - …
- **Out of scope:**
  - …

Explicit "out of scope" bullets are as important as "in scope". They
are how this spec stays bounded.

## 3. User-facing behavior

(Authored by `product`.)

What the user experiences, in user language. Reference
`docs/graph/product/user-flows.md` for the flow diagram. Reference the
acceptance criteria in §9 for the measurable definition of "done".

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

One Given/When/Then per contract. Contracts are single-outcome,
observable from outside, and named with stable slugs the tests
reuse.

### Contract: <UPPER_SNAKE_SLUG>
- **Given:** <preconditions>
- **When:** <action>
- **Then:** <outcome>
- **And:** <additional outcomes if any>

### Contract: <UPPER_SNAKE_SLUG>
- ...

## 5. Non-functional requirements

List only the constraints that bind this behavior and delete the rest —
an empty NFR line is noise, not thoroughness.

- **Performance:** p50/p95/p99 budgets, throughput, memory, cold
  start.
- **Security:** authentication, authorization, audit, rate limits.
- **Privacy:** data classification, retention, redaction, regional
  constraints.
- **Reliability:** SLO/SLI, recovery time objective, recovery
  point objective.
- **Accessibility:** the floor (keyboard, screen reader, contrast,
  focus, motion).
- **Cost:** per-request budget, model-token budget when AI is
  involved.
- **Compatibility:** platforms, browsers, locales, runtime
  versions.

Cross-link to grill.md §4 (Operating Constraints) so the project's
global posture isn't restated here.

## 6. Data shapes

Schemas for inputs, outputs, persisted state. Language-agnostic by
default; cross-link to native schema files where they exist
(TypeScript types, Pydantic models, Protobuf, JSON Schema, OpenAPI).

```yaml
# Example: submission payload
submission:
  required: [title, body]
  fields:
    title: { type: string, min: 1, max: 200 }
    body:  { type: string, min: 1, max: 5000 }
    tags:  { type: array, of: string, max: 10, optional: true }
```

```yaml
# Example: persisted record
submission_record:
  fields:
    id:        { type: string, format: uuid }
    title:     { type: string }
    body:      { type: string }
    tags:      { type: array, of: string }
    created_at:{ type: timestamp, tz: utc }
```

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

For each named failure mode: trigger, response shape, side effects,
recovery path.

### Failure: <UPPER_SNAKE_SLUG>
- **Trigger:** <what causes this failure>
- **Response:** <HTTP code / error code / observable outcome>
- **Side effects:** <what is written, logged, queued>
- **Recovery:** <what the user/system can do next>

## 8. Examples

Concrete input/output pairs. At least:
- One happy path.
- One edge case (boundary, large input, empty, null).
- One failure (from §7).

```yaml
# Happy
input:  { title: "Hello", body: "World" }
output: { id: "<uuid>", status: 201 }

# Edge (title at max length)
input:  { title: "<200 chars>", body: "ok" }
output: { id: "<uuid>", status: 201 }

# Failure (missing required)
input:  { title: "no body" }
output: { status: 422, error: { code: "schema_invalid", field: "body" } }
```

Examples are the seed data for tests. The tester turns them into
test fixtures in §10.

## 9. Acceptance criteria

(Authored by `product`. Each criterion maps to one or more contracts
in §4.)

Each criterion is measurable. A tester can write a test for it
without further clarification.

- [ ] AC-1: <criterion> — maps to <contract slug(s)>
- [ ] AC-2: <criterion> — maps to <contract slug(s)>
- [ ] AC-3 (accessibility): <criterion> — maps to <contract slug(s)>
- [ ] AC-4 (non-functional): p95 latency under <N>ms — maps to perf
  test

Acceptance criteria are checked off when the increment that
implements them passes its gates.

## 10. Test mapping

(Authored by `tester`. Updated when tests are written.)

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| SUBMIT_VALID_FORM_RETURNS_2XX | test_submit_valid_form_returns_2xx | tests/submissions/submit_test.ts | integration | green |
| SUBMIT_FORM_SCHEMA_INVALID    | test_submit_form_schema_invalid    | tests/submissions/submit_test.ts | integration | green |
| AC-1                          | (same as above)                    | | | |
| AC-3                          | test_submit_accessibility          | tests/submissions/a11y_test.ts | e2e | red |
| AC-4                          | bench_submit_latency_p95           | bench/submissions/perf_test.ts | perf | green |

Status values: `red` (test exists, fails), `green` (test exists,
passes), `pending` (test not yet written), `skipped` (with reason).

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|

A spec with open questions is still `draft`. Promote to `active`
only when the table is empty or every row's "current assumption" is
recorded as a flagged assumption in grill.md §12.

## 12. Changelog

- YYYY-MM-DD — created in `draft`, signed off by …
- YYYY-MM-DD — clarified §4 contract SUBMIT_… per …
- YYYY-MM-DD — promoted to `active`.
- YYYY-MM-DD — marked `implemented` after increment N in grill.md.
- YYYY-MM-DD — superseded by SPEC-NNNN-….
