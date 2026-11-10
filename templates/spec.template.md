---
status: draft               # draft | active | implemented | back-written | open | deferred | hotfix | rejected | superseded | closed
status_date: YYYY-MM-DD
owner: <agent or person>
# superseded_by: SPEC-NNNN  # required when superseded
# status_evidence: <path#anchor | commit | gate-run>   # required when closed
---

<!--
Template: spec.template.md
Authored by: product + architect + tester (joint)
Lives at: docs/graph/specs/SPEC-NNNN-<slug>.md
Used: on every new behavior or behavior change
Filled by copying this template into the target path and replacing
every <placeholder>. Keep the section numbers: agents and tooling
index into them.
-->

# SPEC-NNNN: <short slug>

## 0. Metadata

- **Identifier:** SPEC-NNNN-<slug>
- **Status:** see frontmatter (single home)
- **Owner:** <agent or person>
- **Date:** YYYY-MM-DD
- **Last reviewed:** YYYY-MM-DD
- **Related grill section:** <#NNN in docs/graph/plans/grill.md>
- **Related ADRs:** <adr-NNNN-*>
- **Related wiki pages:** <docs/graph/libraries/*>
- **Supersedes:** <SPEC-NNNN-*>
- **Superseded by:** <SPEC-NNNN-*>
- **Contract form:** kinds
- **Trust path:** no   # `yes` when a contract is security, data-integrity or money; a trust-path spec always gets its tester sign-off
- **Sign-offs:** product [ ] · architect [ ] · tester [ ] · security [ ]

## 1. Summary

One paragraph: what this spec covers and why, stated as the scope of
the behavior being contracted.

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

(Authored by `architect`, who sets each contract's kind. Reviewed by
`tester`, who may challenge a kind: `spec-author.contract-kind`.)

One Given/When/Then per contract. Contracts are single-outcome,
observable from outside, and named with stable slugs §10 cites.

Each contract carries one `Check` line, its kind, and the kind says what
proves it:

- `test`: the contract holds logic (a pattern, a condition, an order or
  precedence that changes the output, a computed value) that can be
  wrong while the code is present, and someone is hurt if it is. A §10
  row covers it.
- `run`: a declarative change with nothing to get wrong, proved by a
  named run or an existing gate. Before the spec is live the line
  carries the command; once it is live, the command and `→ <result>
  (<date>)`.
- `review`: wording or presentation. `review — pending` before the spec
  is live; `review — confirmed by reviewer spawn <id> (<date>)` once it is.
- `covered`: an existing named test already asserts it:
  `covered — <path>::<name>`.

When the architect cannot tell, the kind is `test`. A spec with the
`Contract form: kinds` line in §0 gives every contract a `Check` line. A
legacy spec (no `Contract form` line) may label single contracts with a
`Check` line; its unlabelled contracts read as kind `test`, mapped in the
legacy §10 table below.

### Contract: <UPPER_SNAKE_SLUG>
- **Given:** <preconditions>
- **When:** <action>
- **Then:** <outcome>
- **And:** <additional outcomes if any>
- **Check:** test
- **Challenge:** <tester, one line> / **Answer:** <architect, one line> / **Kept:** yes|no

The `Challenge` line is written only when the tester challenged the
kind; `Kept: yes` (the architect kept its kind) goes to the owner as a
numbered decision.

### Contract: <UPPER_SNAKE_SLUG>
- ...
- **Check:** run — `<command>` → pass (YYYY-MM-DD)

### Declared values

The values the change declares, each with nothing to get wrong (a label,
a route, a flag, a key). One `Check` line of kind `run` or `review`
proves the table whole, with the evidence rules above. A value that
holds logic is a contract of kind `test`, not a row here.

| Value | Kind | Where |
|---|---|---|
| <submit button label "Send"> | label | <web/src/submit.html> |
- **Check:** run — `<command>` → pass (YYYY-MM-DD)

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

Cross-link to grill.md §4 (Operating Constraints), the home of the
project's global posture.

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
in §4, or to a declared value as `DV:<value>`.)

Each criterion is measurable: its contract's kind says what proves it,
with no further clarification.

- [ ] AC-1: <criterion> — maps to <contract slug(s)>
- [ ] AC-2: <criterion> — maps to <contract slug(s)>
- [ ] AC-3 (accessibility): <criterion> — maps to <contract slug(s)>
- [ ] AC-4 (non-functional): p95 latency under <N>ms — maps to perf
  test

Acceptance criteria are checked off when the increment that
implements them passes its gates.

## 10. Test design

(Authored by `tester` once, before any increment, after surveying the
existing suite: `specify.flow`. Updated when tests are written.)

One row per risk: what breaks, and for whom, if the test is absent. The
Covers cell is the link from a test to its contracts (a slug in the
test's code is not needed). A row may cover several contracts and a
contract may sit in several rows; every `test` contract is in the Covers
cell of at least one.

| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |
|---|---|---|---|---|
| A malformed form payload is accepted and corrupts a customer record | tests/submissions/submit_test.ts::test_rejects_schema_invalid | SUBMIT_FORM_SCHEMA_INVALID, SUBMIT_VALID_FORM_RETURNS_2XX | design | green |
| Retry after timeout double-charges | tests/pay/retry_test.py::test_retry_is_idempotent | PAY_RETRY_IS_IDEMPOTENT | bug | green |
| An upload named with a path traversal writes outside the root | tests/up/sec_test.py::test_traversal_refused | UPLOAD_NAME_IS_CONFINED | security control | green |
| Log wording differs in an error path | accepted, untested — nobody is hurt, a log line is not a contract | FAIL_LOG_WORDING | | |

Origin: `design`, `bug` or `security control`. Status: `red` (test
exists, fails), `green` (passes), `pending` (not yet written),
`skipped` (with reason); an accepted, untested row has none. A §7
failure mode with no named victim is an `accepted, untested — <why>`
row. A case the RED writer dropped or merged keeps its row, with
`dropped: <reason>`, `merged into <other test>: <reason>` or, for a test removed as catching nothing, `removed: <reason>` after the
status. A legacy spec (no `Contract form` line) keeps the table
`| Contract / Failure | Test name | Test file | Level | Status |`, one row
per contract.

Setup sharing, one line per level the table uses: how the tests at
that level share their expensive setup (one application context with
identical cache keys, one container per run, a template database,
shared fixtures), so a new test joins it instead of starting its own.

- integration: <the shared context, container or fixture, and what keeps it shared>
- e2e: <...>

A test class or file started for a review finding, instead of
extending the one that owns its contract (`test-first`, "A test joins
the class that owns its contract"), records its reason here.

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|

A spec with open questions is unsigned. Sign off (§0) only when the
table is empty or every row's "current assumption" is recorded as a
flagged assumption in grill.md §12. Sign-off keeps the status `draft`;
`active` lands with the spec's first RED tests (test-first COMMIT),
`implemented` when every contract is green.

## 12. Changelog

- YYYY-MM-DD — created in `draft`.
- YYYY-MM-DD — signed off by product, architect, tester (§0); still `draft`.
- YYYY-MM-DD — clarified §4 contract SUBMIT_… per …
- YYYY-MM-DD — promoted to `active` with the RED tests of increment N.
- YYYY-MM-DD — marked `implemented` after increment M in grill.md.
- YYYY-MM-DD — superseded by SPEC-NNNN-….
