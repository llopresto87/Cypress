---
name: initialize
description: Coding-tool compatibility adapter for CYPRESS's canonical INSTALL_PROMPT.md (installed as EXPERT_SEED_INSTALL_PROMPT.md) and grow protocol. Use only when a host exposes /initialize or an equivalent command. It delegates unchanged to docs/graph/protocols/grow.md and the full-growth procedure; it is not the primary way to use the seed.
id: protocol.initialize
tier: 2
kind: protocol
origin: seed
title: initialize — the /initialize coding-tool adapter that delegates to grow
owns:
  - initialize.adapter-edges
requires:
  - protocol.grow
peers:
load_when:
  - "/initialize command invoked"
  - "set up the seed via the coding tool"
  - "dry-run the initialization"
est_tokens: 230
command: true
---

# Protocol adapter: initialize

`/initialize` is a convenience adapter for Claude Code, Prime Agent, Codex,
opencode, Copilot, and similar coding tools. The primary tool-neutral entry point is
`INSTALL_PROMPT.md`; the canonical workflow is `docs/graph/protocols/grow.md`.

When invoked, enter the orchestration role and execute the install prompt and
grow protocol without weakening them — the orchestration, model-class,
routing, and evidence policy is `grow`'s and `INSTALL_PROMPT.md`'s to
define, never re-listed here. The adapter adds only its own hard edges:

- the roster this adapter installs is not spawnable in the session that
  installed it — preflight and remedy per `delegation.harness-registration`
  (`docs/graph/method/delegation.md`) before any by-name dispatch;
- initialization does not run application builds or application test suites;
- initialization does not push, fetch, pull, switch, or commit Git;
- it does not modify application code or fabricate normative records.

Support `--dry-run` by performing only orchestration planning and read-only
scouting, then reporting the proposed authoring briefs without spawning writers.

All detailed discovery, authoring, validation, and maturity criteria are in
`docs/graph/protocols/grow.md` and the full-growth procedure it references.
