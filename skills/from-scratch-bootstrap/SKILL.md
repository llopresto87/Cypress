---
name: from-scratch-bootstrap
description: Stand up a brand-new project from an empty (or near-empty) repo through the nine-phase from-scratch protocol — brainstorm, skeleton, grill, research, architecture, verification baseline, specify first slice, test-first the first slice, deliver. Use whenever a project does not yet exist, the repo is empty, no docs/graph/plans/grill.md exists, or you are about to write `mkdir my-project && cd`. The first day disproportionately shapes the project; this skill prevents skipping the load-bearing steps.
id: skill.from-scratch-bootstrap
tier: 2
kind: skill
origin: seed
title: from-scratch-bootstrap — the nine-phase first day of a brand-new project, kept honest
owns:
  - from-scratch-bootstrap.method
requires:
  - protocol.from-scratch
peers:
  - skill.brainstorm-socratic
  - skill.grill-planner
load_when:
  - "start a brand-new project"
  - "bootstrap an empty repo"
  - "mkdir a new project and cd into it"
  - "no grill.md exists yet"
  - "first day of a project"
artifacts:
  - templates/grill.template.md
est_tokens: 680
---

# from-scratch-bootstrap

The first session in a brand-new project shapes everything that
follows. This skill enforces the nine phases of
`docs/graph/protocols/from-scratch.md` so the first day produces a project an
agent can pick up cold on day two.

## When to apply this skill

- Repo is empty or only contains LICENSE / placeholder README.
- No `docs/graph/plans/grill.md` exists yet.
- The user just said "let's start a new project to do X".
- A `mkdir` for a new project is about to happen.

## The phases live in the protocol; the honesty lives here

The nine-phase sequence and each phase's orchestration — what it produces, which
sub-protocol drives it, its exit conditions — are owned by
`docs/graph/protocols/from-scratch.md` (`from-scratch.phases`). This skill does
**not** restate them; it is the discipline that keeps the first day from cutting
the corners the sequence alone cannot prevent:

- **Bootstrapping is inherently T3** (kernel §0). The full funnel is the
  proportional response, not ceremony — never discount it because the goal
  "sounds clear"; the brainstorm exists to surface the constraints the user did
  not state.
- **The skeleton phase is done only when the host tool actually loads the
  machinery** (agents, protocols, skills) from its own directory — not when the
  files merely exist. Claude Code → `.claude/` + `CLAUDE.md`; Prime Agent →
  `.prime/agent/` + `AGENTS.md`; opencode → `.opencode/` + `AGENTS.md`; Codex →
  `.codex/` + config entries; Copilot → `.github/` + `copilot-instructions.md`.
- **The stack is chosen from verified research, never memory** — version,
  maintenance signal, and license confirmed and wikified before it is committed
  to (research routinely invalidates a remembered option).
- **The verification baseline passes on a clean checkout before any feature
  code** — a test framework configured and a smoke test green come first; a
  slice without a passing gate is a draft, not a slice.
- **Specs before tests before code, always** — the specify phase authors the
  spec, not the implementation.

Each rule is a way the first day silently goes wrong; the catalog below names
the rest.

## Common failure modes

- **Skipping the brainstorm.** "It's just a CLI" — wrong; the
  brainstorm uncovers constraints.
- **Picking the stack from memory.** Verify version, maintenance,
  license; wikify before committing.
- **Writing feature code before gates pass.** A slice without a
  passing gate is a draft, not a slice.
- **Skipping ADR-0001.** Future agents will ask "why this design"
  and have no answer.
- **Skipping SPEC-0001.** Future agents won't know what the slice
  was supposed to do, only what it does.
- **Writing code in Phase 7 instead of the spec.** Specs first;
  tests second; code third. Always.
- **Phase 6 "we'll add tests later".** A bootstrap without a test
  framework configured is incomplete.

## Reference files

- `docs/graph/protocols/from-scratch.md` — the protocol that drives this.
- `docs/graph/skills/brainstorm-socratic.md` — Phase 1.
- `docs/graph/skills/grill-planner.md` — Phase 3.
- `docs/graph/skills/research-and-ingest.md` — Phase 4.
- `docs/graph/skills/library-wiki.md` — Phase 4.
- `docs/graph/skills/adr-writer.md` — Phase 5.
- `docs/graph/skills/spec-author.md` — Phase 7.
- `docs/graph/protocols/test-first.md` — Phase 8.
- `install.sh` — drops the seed system into the project per host tool.
