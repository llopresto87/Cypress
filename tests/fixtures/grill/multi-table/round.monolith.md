# grill: round

## 0. Metadata
- Project: round  - Date: 2026-09-29  - Spec: SPEC-0043

## 1. Artifact Discovery
- Existing files inspected: src/batch/parse.py
- Existing specs inspected: docs/specs/SPEC-0043-round.md
- Constraints discovered: none; see §4

## 2. Shared Understanding
A synthetic plan whose §9 grew an appended subsection, as a plant's plan does: each part carries its own index table.

## 4. Operating Constraints
- Runtime constraints: python 3.12, café-grade patience

## 9. Implementation Plan

The first index covers the increments planned with the round.

### Increment 1 — Parse the batch
- Spec contracts: SPEC-0043/BATCH_PARSE
- Files touched: src/batch/parse.py
- Tests to write (RED): test_batch_parse
- Behavior added: a malformed batch is refused with its line number
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: none

### Increment 2 — Store the batch
- Spec contracts: SPEC-0043/BATCH_STORE
- Files touched: src/batch/store.py
- Tests to write (RED): test_batch_store
- Behavior added: a parsed batch is kept as written
- Gate: integration test
- Rollback path: revert; no migration
- Effort: 1 cycle
- Depends on: increment 1

## §9b. Appended 2026-09-29: the duplicate-batch pass

A later pass, appended under §9 with its own index table.

### Increment 3 — Refuse a duplicate batch
- Spec contracts: SPEC-0043/BATCH_UNIQUE
- Files touched: src/batch/store.py
- Tests to write (RED): test_batch_duplicate_refused
- Behavior added: a second batch with the same id is refused; the first one stays
- Gate: integration test
- Rollback path: revert
- Effort: 1 cycle
- Depends on: increment 2

### Increment 4 — Report the refused batches
- Spec contracts: SPEC-0043/BATCH_REPORT
- Files touched: src/batch/report.py
- Tests to write (RED): test_batch_report_names_refusals
- Behavior added: the nightly report names each refused batch; a naïve count is not enough
- Gate: unit tests
- Rollback path: revert
- Effort: 1 cycle
- Depends on: increment 3

## 10. Verification Plan
Every contract's test runs under the round's gate.

## 15. Changelog
- 2026-09-29: synthetic fixture for the multi-table case of tests/test-grill-lint.sh.
