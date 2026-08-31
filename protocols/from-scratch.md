---
name: from-scratch
description: Bootstrap a brand-new project through a nine-phase sequence (brainstorm → skeleton → grill → research → ADR → verification baseline → specify slice 1 → test-first slice 1 → deliver). Use whenever the project does not yet exist, the repo is empty or near-empty, no docs/graph/plans/grill.md exists, or the session begins with "let's start a new project". The first day shapes everything; this protocol prevents skipping load-bearing steps.
id: protocol.from-scratch
tier: 2
kind: protocol
origin: seed
title: from-scratch — the nine-phase bootstrap of a project that does not exist yet
owns:
  - from-scratch.phases
requires:
peers:
  - protocol.brainstorm
  - protocol.ingest-library
  - skill.from-scratch-bootstrap
artifacts:
  - templates/grill.template.md
load_when:
  - "start a new project, empty repo"
  - "greenfield, bootstrap from nothing"
  - "no grill.md exists yet, day one setup"
  - "project skeleton, verification baseline"
est_tokens: 1300
command: true
---

# Protocol: from-scratch

Use this when the project does not yet exist. The repo is empty or
near-empty: no `docs/`, no `README.md`, no `grill.md`. Your job is to
turn a goal into a project that another agent can pick up cold.

This protocol is bigger than the others because the first day matters
disproportionately. Do not skip steps.

## Entry conditions

- The user has stated a goal, even vaguely.
- There is no `docs/graph/plans/grill.md` yet.
- The repository is empty, near-empty, or contains only a license and
  a README placeholder.

## Phases

### Phase 1 — Brainstorm (Socratic)

Adopt `docs/graph/protocols/brainstorm.md`. Do not skip. The output of this
phase is a precise problem statement, the primary user, the first
useful slice, the constraints, and at least three shaped options for
the technical approach.

Stop and ask the user at most three questions per exchange; do not
interview endlessly. If you cannot reach precision in three turns,
write what you have, mark the gaps as assumptions in grill.md, and
proceed.

### Phase 2 — Project skeleton

Once the brainstorm converges, create the project skeleton:

```
.
├── AGENTS.md                 → core/AGENTS.md (universal kernel)
├── CLAUDE.md                 → symlink or copy of AGENTS.md
├── .github/copilot-instructions.md → copy of AGENTS.md
├── docs/graph/agents/        → agents/ (the team; projected to .claude/agents/)
├── docs/graph/protocols/     → protocols/
├── docs/graph/skills/        → skills/ (projected to .claude/skills/)
├── README.md                 → orientation, one screen
├── docs/
│   ├── README.md
│   ├── graph/                  → knowledge-graph home
│   │   ├── _schema.md          → templates/knowledge-graph/_schema.md
│   │   ├── graph-lint.py       → templates/knowledge-graph/graph-lint.py
│   │   ├── index.md            → the router (root node listed)
│   │   └── nodes/root.md       → the one root node to start
│   ├── plans/grill.md
│   ├── specs/index.md
│   ├── decisions/adr-0001-bootstrapping.md
│   ├── libraries/index.md
│   ├── sources/index.md
│   ├── runbooks/local-development.md
│   ├── runbooks/verification.md
│   └── (other folders created as needed)
└── (language- or stack-specific files only after Phase 4)
```

The `install.sh` in this seed system can drop the right per-tool
overlay into `.claude/`, `.prime/agent/`, `.opencode/`, `.codex/`, or
`.github/`, and
the knowledge-graph scaffold (schema, lint, router) into `docs/graph/`.
That overlay includes the specialist roster, which this protocol then
dispatches **by name** in later phases — from the same session that just
wrote it. Settle spawnability before the first named hand-off:
`delegation.harness-registration` in `docs/graph/method/delegation.md`.

A new project's graph starts tiny — one root node — and grows a node
per subsystem as the architecture (Phase 5) takes shape. It is not
overhead to defer: seeding it now means every later session routes
through `docs/graph/index.md` instead of re-reading the tree. For a
program spanning several repos, the unified graph lives at
the governing root; for a single repo, at its root. See
`docs/graph/skills/knowledge-graph.md`.

### Phase 3 — Initial grill.md

Open `docs/graph/plans/grill.md` from `docs/graph/templates/grill.template.md`. Fill
at minimum:
- §0 (Metadata): project name, today's date, current phase
  "bootstrapping".
- §2 (Shared Understanding): the precise problem statement from
  the brainstorm.
- §3 (User Goal): primary user, primary outcome, acceptance
  criteria for the first useful slice, non-goals.
- §4 (Operating Constraints): everything the brainstorm uncovered.
- §7 (Options Considered): the three+ shaped options.
- §11 (Risks and Mitigations): the obvious risks from the
  brainstorm.
- §12 (Open Questions): every assumption flagged for validation.
- §14 (Recommended Next Step): "Phase 4 — research and library
  ingest".

### Phase 4 — Research and library ingest

Hand off to `research-scout` with the candidate technologies, and run
`docs/graph/protocols/ingest-library.md` for each — its steps own the existence,
version, and maintenance-signal checks and produce the wiki page in
`docs/graph/libraries/`.

This phase often updates the shaped options because a candidate
library turns out to be unmaintained, has a worse license than
remembered, or has a sharp edge that matters. Update grill.md §5
and §7 as you learn.

### Phase 5 — Architecture decision

Hand off to `architect`. The architect:
- Picks the option using the constraints and the research.
- Writes `docs/graph/decisions/adr-0001-initial-architecture.md`.
- Updates grill.md §6 (Decisions Made) and §8 (Architecture Plan).
- Drafts the boundary diagram.

### Phase 6 — Verification baseline

Before any feature code, set up the verification baseline:
- Pick the formatter, linter, type checker, and **test
  framework** for the chosen stack. Wikify each one through
  `research-scout`.
- Write `docs/graph/runbooks/local-development.md` with the exact
  commands to install dependencies and run the project.
- Write `docs/graph/runbooks/verification.md` with the exact gate
  commands.
- Add a minimal "hello world" test that runs end-to-end. The gate
  command must pass on a clean checkout before any feature is
  implemented.

A project that cannot run its gates from a clean checkout is not
yet bootstrapped. A project without a test framework configured is
not yet bootstrapped.

### Phase 7 — Specify the first useful slice

Run `docs/graph/protocols/specify.md` to produce
`docs/graph/specs/SPEC-0001-<slug>.md` for the first useful slice. This
spec is short — the slice is small — but it covers §1–§10. Get
the sign-offs (product ✓, architect ✓, tester ✓).

### Phase 8 — Test-first the first useful slice

Run `docs/graph/protocols/test-first.md` for each contract in SPEC-0001.
RED → GREEN → REFACTOR → COMMIT for each increment in grill.md
§9.

### Phase 9 — Deliver

Run `docs/graph/protocols/deliver.md`. The recommended next step is the
second slice or the next-most-valuable item from the roadmap in
`docs/graph/product/requirements.md`.

## Exit conditions

- `docs/graph/plans/grill.md` exists and is current.
- `docs/graph/decisions/adr-0001-*.md` records the initial architecture.
- `docs/graph/libraries/index.md` lists every chosen dependency with a
  page each.
- `docs/graph/runbooks/local-development.md` and `verification.md` exist
  and their commands run.
- `docs/graph/specs/SPEC-0001-*.md` exists, status `active`.
- The first useful slice's tests are green; the suite is green.
- The README explains what the project is and how to run it.

## Common ways to fail this protocol

The catalog of how a first day silently goes wrong — feature code before the
gates run, code where the spec belongs, a skipped brainstorm, a stack picked
from memory, a bootstrap with no test framework — is the honesty discipline
owned by `skill.from-scratch-bootstrap` (`from-scratch-bootstrap.method`); read
it alongside this protocol. And note the structural rule it cannot: **each phase
above adopts a sub-protocol that carries its own failure modes** — brainstorm,
ingest-library, specify, test-first, the ADR/spec-first rules — so read the
phase's protocol, never a summary of it.
