---
name: adr-writer
description: Author an Architecture Decision Record that captures a non-obvious technical choice — its context, the decision, the consequences, the rejected alternatives, and the reversibility cost. Use whenever a non-trivial dependency is picked, a framework is chosen, a one-way door is opened, two specialists disagree and the orchestrator must pick, or anyone in a future session would ask "why did we do this?" An ADR exists so the answer is on disk, not in someone's head.
id: skill.adr-writer
tier: 2
kind: skill
origin: seed
title: adr-writer — record non-obvious technical choices as short, superseded-never-edited ADRs
owns:
  - adr-writer.method
  - adr-writer.reversibility
  - adr-writer.numbering
requires:
peers:
  - skill.grill-planner
  - agent.architect
load_when:
  - "write an ADR"
  - "record an architecture decision"
  - "why did we choose this dependency or design"
  - "supersede an existing decision record"
  - "opening a one-way door decision"
artifacts:
  - templates/adr.template.md
  - templates/docs/decisions/README.md
est_tokens: 1400
---

# adr-writer

ADRs (Architecture Decision Records) live in `docs/graph/decisions/` and
record every non-obvious technical choice. They are not philosophy
papers and not design docs; they are a recorded answer to "why did
we pick this?"

This skill encodes the discipline of writing them well.

## When to apply this skill

- A new dependency is being committed to (the wiki page handles
  the *what*; the ADR handles the *why*).
- A framework, language, or platform is being chosen.
- A one-way door is being opened (data model, public API contract,
  vendor lock-in).
- A boundary between two services or modules is being drawn.
- Two specialists disagreed and the orchestrator picked an option.
- A bug post-mortem revealed an implicit decision that should have
  been explicit.
- Anyone asks "why did we do it this way?" and the answer isn't in
  an existing ADR.

## ADR numbering

ADRs are numbered monotonically: `adr-NNNN-short-slug.md`. Find the
next free number in `docs/graph/decisions/`. **Never reuse a number.** To
replace a decision, write a new ADR with a new number; mark the old
ADR's status as `superseded by ADR-NNNN`.

The index lives at `docs/graph/decisions/README.md`.

## The template (4 sections that matter most)

Use `docs/graph/templates/adr.template.md`. The four sections that earn their
keep:

### Context

What is the situation that forces a decision? Include the
constraint that makes "do nothing" not viable. Cross-link to
grill.md and the relevant spec.

Bad: "We need a database."

Good: "Spec SPEC-0003 requires submissions to persist across
restarts. Grill.md §4 caps p95 latency at 200ms and cost at
$X/month. The current implementation uses an in-memory map,
which loses state on restart. We need to choose a persistent
store."

### Decision

What we have decided, in **one sentence**. Optionally a short
paragraph naming the central tradeoff.

Bad: "We'll use PostgreSQL."

Good: "We will persist submissions in PostgreSQL 16, using the
managed instance on platform X, accepting an additional ~$45/mo
in exchange for ACID guarantees and ecosystem maturity over the
in-memory alternative."

### Consequences

What changes downstream. Be concrete:
- New constraints (e.g. "migrations now belong in
  `migrations/` and run on deploy").
- Migration or rewrite cost if reversed.
- Effect on the verification plan (new gates, integration tests
  against a test database).
- Effect on the wiki (new library to wikify: the database driver
  and the migration tool).

### Alternatives considered

For each rejected alternative: one paragraph naming the
alternative and the **concrete** reason it lost.

Bad: "SQLite — not as good for our use case."

Good: "SQLite — rejected because grill.md §4 requires concurrent
writes from multiple workers; SQLite serializes them and would
violate the 200ms p95 budget at the projected request rate."

## Reversibility tag

Every ADR tags reversibility as one of:

- **`reversible`** — can be changed in a single session without
  data migration.
- **`expensive`** — can be changed but requires a multi-day
  project.
- **`one-way`** — changing it later requires a rewrite or a
  migration on live data.

`one-way` ADRs get extra scrutiny. They are the ones where the
"alternatives considered" section earns its keep — the next agent
needs to understand why the alternative was rejected, not just
that it was.

## What counts as a decision — don't fabricate one

An ADR records a *choice that was made*, not a fact about how the
system happens to be built. An implementation detail reconstructed
from source is an **observation**, not a decision: record it where
observations live (a node, a runbook) with its rationale marked
"not recorded", and never dress it up as a ratified ADR. If a survey
turns up no genuine decisions, the index stays empty and says so — a
fabricated ADR is worse than a missing one, because the next agent
trusts it.

Two decisions people forget to record because they feel like inaction:

- **"Do nothing now" is a decision.** Ratifying a destination while
  taking no code yet — deferring the first increment behind a named,
  checkable trigger — is an ADR. Separate the *destination* (which
  end-state is correct) from the *timing* (what licenses starting),
  and state what makes waiting safe ("the drift is now tested, not
  invisible").
- **The asymmetric cost of being wrong** is often the whole rationale.
  Record what being wrong costs *in each direction* — "wrong on X
  risks an irreversible incident; wrong on Y costs a bounded,
  recoverable delay" — and let the asymmetry decide, rather than
  arguing which option is abstractly "best".

## Workflow

1. Find the next free number. Read the most recent few ADRs to
   match the project's tone.
2. Copy `docs/graph/templates/adr.template.md` to
   `docs/graph/decisions/adr-NNNN-<slug>.md`.
3. Fill **Context** first. If you can't write the context, you
   don't yet know what decision you're making.
4. Fill **Decision** in one sentence. If you can't, the decision
   isn't yet made; back up to research or brainstorm.
5. Fill **Consequences** — concretely, with file paths and budget
   impacts where applicable.
6. Fill **Alternatives considered** — at least one alternative,
   usually two or three, each with a concrete rejection reason.
7. Fill **Reversibility** and, if `expensive` or `one-way`, name
   the cost in concrete terms.
8. Cross-link: spec, grill.md, wiki pages, external sources.
9. Add a row to `docs/graph/decisions/README.md` (the index).
10. Add a row to grill.md §6 with the ADR's identifier.

## Anti-patterns

- **ADR as design doc.** Design docs are different artifacts; ADRs
  are decision records. Keep ADRs short.
- **Decision sentence that is actually three decisions.** Split
  into three ADRs.
- **Alternatives with vague rejection reasons.** "Not as good"
  doesn't help the next agent. Be concrete.
- **No reversibility tag.** Without it, the next agent doesn't
  know how much weight this decision carries.
- **ADR with no cross-links.** Link to grill.md, the spec, the
  wiki pages — the ADR isn't an island.
- **Rewriting an ADR after the fact.** Supersede; do not edit.
- **An as-built observation dressed as a decision.** Reconstructed
  detail with no recorded rationale is an observation, not an ADR —
  don't mint one to fill an empty index.

## Reference files

- `docs/graph/templates/adr.template.md` — the template.
- `docs/graph/agents/01-architect.md` — the agent that primarily writes
  ADRs.
- `docs/graph/templates/docs/` + `decisions/README.md` — the index template installed at
  `docs/graph/decisions/README.md`.
