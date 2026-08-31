---
name: grill-planner
description: Author, update, and audit the project's plan-of-record at docs/graph/plans/grill.md. Use whenever a new feature is being planned, an existing plan needs to be revised after research or implementation, an increment is being scoped, or grill.md needs a consistency pass against the spec catalog. The grill.md is the single living plan; this skill keeps it current, consistent, and indexable.
id: skill.grill-planner
tier: 2
kind: skill
origin: seed
title: grill-planner — author, update, and audit the living plan-of-record at docs/graph/plans/grill.md
owns:
  - grill-planner.method
  - grill-planner.audit
requires:
  - protocol.grill
peers:
  - skill.spec-author
load_when:
  - "update the plan of record"
  - "author or revise grill.md"
  - "scope the next increment"
  - "plan a new feature"
  - "grill.md drifted from the specs"
artifacts:
  - templates/grill.template.md
est_tokens: 1300
---

# grill-planner

`docs/graph/plans/grill.md` is the project's plan-of-record. It links to
the specs it implements and to the wiki pages it depends on, and it
is the document the next agent reads first to know what's happening.

This skill is the discipline of keeping it current.

## When to apply this skill

- A new feature or significant change is about to be planned.
- Research changed the architecture or the option set.
- An increment finished and the plan needs to record what was done.
- A new risk or open question was uncovered.
- The plan and the spec catalog (or the wiki) have drifted apart.
- A session is ending and grill.md needs its §15 changelog entry.

## The principles

### Append, don't rewrite

Sections 1–14 evolve, but you do not silently rewrite earlier
sections. When a claim becomes obsolete, cross it out (or move it to
a "history" subsection) and add the new claim with today's date.
The reason: the next agent needs to see what was believed and what
changed.

§15 (Changelog) collects the meaningful changes session by session.

### Section numbers are stable

Do not renumber. Other agents and tooling index into grill.md by
section number. If a section doesn't apply to the current project,
leave it with a single line saying so (e.g. "§10 Verification Plan
— covered by the project's standard gates, see
docs/graph/runbooks/verification.md").

### Specs upstream, plan downstream

The plan implements specs. If the plan introduces behavior not in
any spec, that's a spec-shaped hole — file an open question in §12
and back-write the spec via the `specify` protocol.

The check during grill: every increment in §9 names at least one
spec contract. Every contract in the relevant spec's §4 appears in
at least one increment.

### Increments are small and verifiable

A good increment fits one RED-GREEN-REFACTOR cycle (or a small
handful). If you can't write the failing test from the increment
description, the increment is too vague or too big. Re-slice.

### Structure earns its place at plan time

An increment that introduces structure — a module, layer, interface,
service, or extension point — names, in its §9 row, the single
responsibility that structure owns and the real, already-present
variation that justifies any abstraction (the structure-earns-its-place
posture: `docs/graph/method/design-posture.md`,
`docs/graph/method/stewardship-posture.md`). The plan's default is the smallest structure that fits; a
speculative seam is cheapest to delete here, before it is built —
the reviewer flags what the plan lets through.

### Cite, and mark what you haven't verified

Every claim in the plan is either confirmed from a primary source
(cite it) or is not — and the ones that are not carry an explicit
`[verify]` tag (or "not recorded"), so the next reader knows exactly
what to re-check instead of trusting a guess. A value or decision that
needs human input — a real origin, a credential, an irreversible go-
ahead — is marked **do-not-guess** in §12 and left for sign-off; the
plan never invents one to keep moving. When the plan is executed,
append what actually happened and how each `[verify]` resolved rather
than editing the tables in place.

## Workflow

### Creating grill.md (first time for a feature)

1. Copy `docs/graph/templates/grill.template.md` to `docs/graph/plans/grill.md`.
2. Fill §0 (Metadata) with the project name, today's date, the
   feature, the current phase.
3. Fill §1 (Artifact Discovery) — what you read, with paths.
4. Fill §2 (Shared Understanding) — the precise problem
   statement, usually from the brainstorm output.
5. Fill §3 (User Goal) — link to the spec's §3 and §9.
6. Fill §4 (Operating Constraints) — global posture and feature-
   specific constraints.
7. Hand to `research-scout` to fill §5.
8. Hand to `architect` to fill §6, §7, §8 (and to write ADRs).
9. Together with `tester`, slice §9 into increments that map to
   spec contracts.
10. Hand to `security` and `reliability` to fill §10 and §11.
11. Open questions land in §12.
12. Define §13 (Done Criteria) from the spec's §9.
13. Recommend a single §14 (Next Step).
14. Write the §15 entry.

### Updating grill.md (after an increment)

1. Append an entry to §15 (Changelog) — increment title, spec
   contracts covered, files touched, gates run, gates passed.
2. Cross out completed rows in §9 (do not delete) and add new
   rows if the increment revealed work.
3. If a decision changed, add a row to §6 with the new decision
   and the date; mark the superseded row.
4. If a new risk surfaced, add a row to §11.
5. If an open question was resolved, move it from §12 to §6
   (Decisions) or §11 (Risks) as appropriate.
6. Update §14 (Next Step) to the next highest-leverage action.

### Auditing grill.md (consistency pass)

Run this when grill.md feels out of sync:
- Every increment in §9 has at least one spec contract.
- Every active spec in `docs/graph/specs/` is referenced from §3 or §9.
- Every library named in §5 has a wiki page.
- Every ADR in `docs/graph/decisions/` matches a row in §6.
- Every gate in §10 has an entry in `docs/graph/runbooks/verification.md`.
- §14 names one action, not a list.

Record any inconsistencies as open questions in §12 with owners.

## Anti-patterns

- **§14 with five bullets.** One next step. Always.
- **§6 with no evidence column.** Decisions without evidence are
  guesses recorded as decisions.
- **§9 with rows like "implement the feature".** Each row is a
  named increment with files, tests, and a gate.
- **§11 with vague risks.** Probability and impact, both
  qualitative or quantitative — "medium / high" is acceptable,
  "manageable" is not.
- **Silent rewrites.** Append; cross out; don't delete.

## Reference files

- `docs/graph/templates/grill.template.md` — the template.
- `docs/graph/protocols/grill.md` — the protocol that drives this skill.
- `docs/graph/agents/00-orchestrator.md` — the agent that opens grill.md
  first thing every session.
