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

| # | Increment | Status | Detail |
|---|---|---|---|
| 1 | Parse the batch | planned | `docs/plans/round/increment-01-a.md` |
| 2 | Store the batch | planned | `docs/plans/round/increment-02-b.md` |

## §9b. Appended 2026-09-29: the duplicate-batch pass

A later pass, appended under §9 with its own index table.

| # | Increment | Status | Detail |
|---|---|---|---|
| 3 | Refuse a duplicate batch | planned | `docs/plans/round/increment-03-c.md` |
| 4 | Report the refused batches | planned | `docs/plans/round/increment-04-d.md` |

## 10. Verification Plan
Every contract's test runs under the round's gate.

## 15. Changelog
- 2026-09-29: synthetic fixture for the multi-table case of tests/test-grill-lint.sh.
