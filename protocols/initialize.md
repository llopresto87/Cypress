---
name: initialize
description: The entry fork, and the coding-tool adapter that carries it. Decides which growth protocol a target enters — grow when there is executable project evidence to scout, from-scratch when the repository is empty or near-empty — and delegates to it unchanged. Also the compatibility adapter for hosts exposing /initialize or an equivalent command; the tool-neutral entry point is INSTALL_PROMPT.md (installed as EXPERT_SEED_INSTALL_PROMPT.md). Use right after installing the seed, or whenever it is unclear whether a target should be grown or bootstrapped.
id: protocol.initialize
tier: 2
kind: protocol
origin: seed
title: 'initialize — the entry fork: grow when there is source to scout, from-scratch when the repo is empty'
owns:
  - initialize.entry-fork
  - initialize.adapter-edges
requires:
peers:
  - protocol.grow
  - protocol.from-scratch
  - agent.seed-installer
load_when:
  - "/initialize command invoked"
  - "just installed the seed, which protocol do I enter"
  - "empty repo or existing code, where does growth start"
  - "set up the seed via the coding tool"
  - "dry-run the initialization"
prevents: Every repository entering the same protocol regardless of whether it has any source to scout, so an empty one is sent to grow — which authors a graph FROM evidence — and the nine-phase bootstrap that fits it is never reached.
est_tokens: 697
command: true
---

# Protocol: initialize — the entry fork

Two protocols can start a plant, and they are not interchangeable. This node
holds the decision between them, and the `/initialize` adapter that carries it
for hosts that expose a command.

## The fork (`initialize.entry-fork`)

**The test: does the target hold executable project evidence?** Source a scout
could read and make claims about — not a README, not a licence, not an empty
`src/`. This is the same judgement `grow` Phase 1 already makes when it detects
the target's shape; the fork adopts it rather than inventing a second one.

| Evidence | Enter | Because |
|---|---|---|
| **present** — one repo, a workspace, a monorepo, an umbrella | `protocol.grow` | there is source to scout; growth authors a graph *from* that evidence, through ledgers its scouts write |
| **absent** — empty or near-empty | `protocol.from-scratch` | there is nothing to scout. The nine-phase bootstrap authors the project *and* its graph, and ends at `deliver` |

Entering `grow` on an empty repository is the failure this fork exists to stop:
every scout returns an empty ledger, the completeness contract has nothing to be
complete about, and the session reports a grown plant that holds no knowledge.

**Hand off; do not resume.** Both arms are whole protocols that run to their own
exit conditions. Neither returns here, and this node owns nothing that happens
after the branch is taken.

If the target is ambiguous — a scaffold with one placeholder module, a repo
holding only config — the question is whether a scout could return claims tied
to paths and symbols. If it could, that is evidence and the arm is `grow`. If
the only readable thing is scaffolding, there is nothing to make claims about
and the arm is `from-scratch`. Say which way you read it and why before you
enter; both protocols state their own entry conditions and either will tell you
if you brought it the wrong target.

## The adapter's own hard edges (`initialize.adapter-edges`)

`/initialize` is a convenience adapter for Claude Code, Prime Agent, Codex,
opencode, Copilot, and similar coding tools. The primary tool-neutral entry
point is `INSTALL_PROMPT.md`. When invoked, take the fork above, then enter the
chosen protocol and execute it without weakening it — orchestration,
model-class, routing and evidence policy are that protocol's to define and are
never re-listed here.

The adapter adds only these edges of its own, and they bind both arms:
- the roster this adapter installs is not spawnable in the session that
  installed it — preflight and remedy per `delegation.harness-registration`
  (`docs/graph/method/delegation.md`) before any by-name dispatch;
- initialization does not run application builds or application test suites;
- initialization does not push, fetch, pull, switch, or commit Git;
- it does not modify application code or fabricate normative records.

Support `--dry-run` by performing only orchestration planning and read-only
scouting, then reporting the fork's verdict and the proposed authoring briefs
without spawning writers.

All detailed discovery, authoring, validation and maturity criteria are in
`docs/graph/protocols/grow.md` and the full-growth procedure it references; the
greenfield sequence and its entry conditions are in
`docs/graph/protocols/from-scratch.md`.
