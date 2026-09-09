---
name: from-scratch
description: Bootstrap a brand-new project through a nine-phase sequence (brainstorm → skeleton → grill creation pass → research → ADR → verification baseline → specify slice 1 → test-first slice 1 → close-out and deliver), each phase with a named owner and the sub-protocol it adopts. Use whenever the project does not yet exist, the repo is empty or near-empty, no docs/graph/plans/grill.md exists, or the session begins with "let's start a new project". The first day shapes everything; this protocol prevents skipping load-bearing steps.
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
  - protocol.grill
  - protocol.ingest-library
  - protocol.canonize
  - skill.from-scratch-bootstrap
artifacts:
  - templates/grill.template.md
load_when:
  - "start a new project, empty repo"
  - "greenfield, bootstrap from nothing"
  - "no grill.md exists yet, day one setup"
  - "project skeleton, verification baseline"
est_tokens: 1500
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

## Phases (`from-scratch.phases`)

Nine phases, each adopting a sub-protocol that carries its own owners
and failure modes — read the phase's protocol, never a summary of it.
**The table is the spawn order**: a phase's spawn is issued only after
the handback it needs has returned (`delegation.sequencing`).

| Phase | Does | Adopts | Owner | Needs |
|---|---|---|---|---|
| 1 | Brainstorm | `protocol.brainstorm` | orchestrator, in-session with the user | the goal |
| 2 | Project skeleton | `install.sh`; `skill.knowledge-graph` | `seed-installer` (the overlay), orchestrator (root node, README) | 1 |
| 3 | grill.md, creation pass phases 0–2 | `grill.flow` | orchestrator, in-session | 1, 2 |
| 4 | Research and library ingest | `grill.flow` phase 3 → `ingest-library.flow` per candidate | `research-scout` per dependency; `tester` smoke-tests | 3 |
| 5 | Architecture decision, ADR-0001 | `grill.flow` phase 4; `skill.adr-writer` | `architect` (`legal` inside its checkpoint) | 4 |
| 6 | Verification baseline | `protocol.verify` | `reliability` (runbooks, the one gate entry point); `tester` (framework, hello-world test); `research-scout` wikifies each tool | 5 |
| 7 | Specify the first useful slice | `specify.flow` | per the specify table | 5, 6 |
| 8 | Test-first the first slice | `grill.flow` phases 5–8, then `test-first.cycle` | per those tables | 7 |
| 9 | Close-out and deliver | `protocol.canonize` → `protocol.deliver` | `docs-librarian` (one spawn), then the session | 8 |

### Phase 1 — Brainstorm (Socratic)

Adopt `docs/graph/protocols/brainstorm.md`. Do not skip. The output of this
phase is a precise problem statement, the primary user, the first
useful slice, the constraints, and at least three shaped options for
the technical approach.

Pacing and the stopping rule belong to
`docs/graph/skills/brainstorm-socratic.md` — one-to-three questions per
turn under a hard cap of nine questions total. When the cap is reached
without precision, write what you have, mark the gaps as assumptions in
grill.md, and proceed.

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

### Phases 3–5 — The grill creation pass, greenfield

Phases 3–5 are `grill.flow`'s phases 0–4 and are not restated here;
what a greenfield adds:

- **Phase 3** fills §0 (phase "bootstrapping"), §2–§4 from the
  brainstorm, and §1 with `none — greenfield` on every line — the
  honest discovery of an empty repository, and what `grill-lint.py`
  accepts in place of a path. §7 carries the three-plus shaped options,
  §11 the obvious risks, §12 every assumption flagged for validation;
  §14 reads "Phase 4 — research and library ingest".
- **Phase 4** hands each candidate technology to `research-scout`
  through `ingest-library.flow` — existence, version, maintenance
  signal, license, the wiki page — and this is where shaped options
  die: a candidate turns out unmaintained, worse-licensed than
  remembered, or sharp in a way that matters. §5 and §7 are updated as
  it happens.
- **Phase 5** hands the constraints and the research to `architect`:
  the option is picked, `docs/graph/decisions/adr-0001-initial-architecture.md`
  written, grill.md §6 and §8 filled with the boundary diagram.

### Phase 6 — Verification baseline

Before any feature code, set up the verification baseline:
- `tester` picks the formatter, linter, type checker, and **test
  framework** for the chosen stack (the framework choice is an ADR,
  `protocol.test-first`), and adds a minimal "hello world" test that
  runs end-to-end; `research-scout` wikifies each tool through
  `ingest-library.flow`.
- `reliability` writes `docs/graph/runbooks/local-development.md` with
  the exact commands to install dependencies and run the project, and
  `docs/graph/runbooks/verification.md` with the exact gate commands
  behind the one entry point `protocol.verify` requires.
- The gate command must pass on a clean checkout before any feature
  is implemented.

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

### Phase 9 — Close-out and deliver

Run `docs/graph/protocols/canonize.md` — the one `docs-librarian` spawn
that finalizes every wiki page the scouts drafted, writes the
`libraries/index.md` and `sources/index.md` rows, persists what the
first day taught, and catalogs any tool it built — then
`docs/graph/protocols/deliver.md`. The recommended next step is the
second slice or the next-most-valuable item from the roadmap in
`docs/graph/product/requirements.md`.

## Exit conditions

- `docs/graph/plans/grill.md` exists and is current.
- `docs/graph/decisions/adr-0001-*.md` records the initial architecture.
- `docs/graph/libraries/index.md` lists every chosen dependency with a
  page each; `python3 docs/graph/graph-lint.py` and
  `python3 docs/graph/grill-lint.py` exit 0.
- `docs/graph/runbooks/local-development.md` and `verification.md` exist
  and their commands run.
- `docs/graph/specs/SPEC-0001-*.md` exists, status `implemented` (its
  RED landed with the slice's tests and every contract is green).
- The first useful slice's tests are green; the suite is green.
- The README explains what the project is and how to run it.
- The close-out ran: the delivery cites the librarian's handback.

## Common ways to fail this protocol

The catalog of how a first day silently goes wrong — feature code before the
gates run, code where the spec belongs, a skipped brainstorm, a stack picked
from memory, a bootstrap with no test framework — is the honesty discipline
owned by `skill.from-scratch-bootstrap` (`from-scratch-bootstrap.method`); read
it alongside this protocol. And note the structural rule it cannot: **each phase
above adopts a sub-protocol that carries its own failure modes** — brainstorm,
ingest-library, specify, test-first, the ADR/spec-first rules — so read the
phase's protocol, never a summary of it.
