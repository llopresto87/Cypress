---
name: grill-planner
description: The authoring discipline for the project's plan-of-record at docs/graph/plans/grill.md — what a worker filling any section carries, and the audit that says whether the plan is still consistent with the specs, the wiki, and the decisions. Use whenever a brief produces or updates grill.md, or grill.md needs a consistency pass. The pass itself (which section, which owner, in which order) is protocol.grill; this skill is how each section is written well.
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
  - "author or revise a section of grill.md"
  - "write the plan-of-record well, plan authoring discipline"
  - "grill.md drifted from the specs, audit the plan"
artifacts:
  - templates/grill.template.md
est_tokens: 1150
---

# grill-planner

`docs/graph/plans/grill.md` is the project's plan-of-record. It links to
the specs it implements and to the wiki pages it depends on, and it
is the document the next agent reads first to know what's happening.

This skill is the discipline of writing it well. Which section is
filled when, by whom, and in what spawn order is the protocol's
(`grill.flow` and `grill.revise` in `docs/graph/protocols/grill.md`);
a brief that produces or updates grill.md cites this skill so the
worker carries the principles below into whatever section it owns.

## When to apply this skill

- A brief hands you a section of grill.md to author or revise.
- The plan and the spec catalog, the wiki, or the decisions have
  drifted apart and the plan needs an audit.

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

The protocol presses this (`grill.press`: every increment names a
contract, every contract has an increment) before the plan exits;
`grill-lint.py` runs the mechanical half.

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

The creation and revision passes — which sections, which owner, which
spawn waits for which handback — are `grill.flow` and `grill.revise` in
`docs/graph/protocols/grill.md`, and are not restated here: a second
copy of a sequence drifts, and a worker sequencing from a copy is how
spawns come out of order. This skill's own workflow is the audit.

### Auditing grill.md (consistency pass)

Run this when grill.md feels out of sync. First the mechanical part:
`python3 docs/graph/grill-lint.py` checks the shape (every section
populated, §1 lines cited, §9 rows complete and in dependency order,
§5 covering the library pages §9 depends on, §14 a single action) and
the plan→spec half of the alignment check (every contract an increment
names exists in a live spec; every contract of those specs appears in
an increment). Then the judgment the lint cannot make:

- Every active spec in `docs/graph/specs/` is referenced from §3 or §9.
- Every ADR in `docs/graph/decisions/` matches a row in §6, and no §6
  row that changed a boundary is missing its ADR.
- Every gate named in §10 is a genuine divergence from
  `docs/graph/runbooks/verification.md`, not a duplicate of it.
- Every §11 row has a verification that would actually detect the
  risk; every §12 row has an owner who can resolve it.
- A `no external dependency` line in §5 is true — the lint sees only
  what §9 names.

Record any inconsistency as a §12 row with an owner; the fix runs
through the protocol's revision pass.

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
- `docs/graph/protocols/grill.md` — the protocol that owns the pass
  this skill writes inside: phases, owners, spawn order, the press,
  the exit conditions.
- `docs/graph/grill-lint.py` — the mechanical half of the audit.
- `docs/graph/agents/00-orchestrator.md` — the agent that opens grill.md
  first thing every session.
