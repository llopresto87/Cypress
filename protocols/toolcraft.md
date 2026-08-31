---
name: toolcraft
description: Doctrine (kernel §3.8) — when an operation will recur across independent sessions, the unit of work is a durable, tested, cataloged tool, not a throwaway script. Defines what counts as a durable tool and what stays disposable. EXECUTION lives in the canonize close-out (protocols/canonize.md) — the one docs-librarian spawn at task end catalogs tools and persists knowledge together; toolcraft never spawns separately.
id: protocol.toolcraft
tier: 2
kind: protocol
origin: seed
title: toolcraft — the doctrine of durable, tested, cataloged tools versus throwaway scripts
owns:
  - rule.toolcraft
  - toolcraft.durability-criteria
requires:
peers:
  - protocol.canonize
  - protocol.grill
  - protocol.harvest
artifacts:
  - templates/skill.template.md
  - templates/agent.template.md
  - templates/prompts/handback-payload.md
load_when:
  - "should this script be kept, is this a durable tool"
  - "recurring operation across sessions"
  - "catalog a tool, tools_built, skills_built"
  - "throwaway prototype versus reusable tooling"
est_tokens: 1000
---

# Protocol: toolcraft — the durable-tool doctrine

This node owns **the toolcraft rule** — durable tools compound;
throwaway scripts are rework. When an operation will recur across
independent sessions, the unit of work is a **durable, tested tool**
with a stable interface — designed so at plan time, named in
`tools_built` on every handback, and cataloged in `docs/graph/tools/`
by the librarian inside the close-out spawn. Genuine one-offs and
throwaway prototypes stay disposable. A task is **not complete**
until any durable tool is cataloged or explicitly recorded absent.

Work generates capabilities, not only knowledge. A task needs an
operation performed — seed a fixture, migrate a schema, probe an
endpoint, regenerate a client — and an agent writes code to do it. If
that code dies with the session, the next task that needs the same
operation writes it again, slightly differently, with a fresh chance to
get it wrong. Toolcraft is the doctrine that keeps a capability once it
is worth keeping.

**This file owns the doctrine only.** The execution — cataloging the
tool in `docs/graph/tools/` — happens inside the single close-out
spawn defined in `docs/graph/protocols/canonize.md`, in the same
librarian brief that persists the task's knowledge. There is no
separate toolcraft spawn; a second spawn with the same bootstrap and
lint run would be coordination waste.

## What counts as a durable tool

Catalog a piece of real code that:
- **recurs across independent sessions** — an agent, expert, or skill
  will plausibly run it again in a future task (the trigger is
  recurrence, not size);
- has a **stable interface** — a named entry point, defined inputs and
  outputs, a documented invocation, not a copy-pasted snippet;
- is **authorized by a test** (§3.4) — at least one test pins what it
  does, so a future session can trust and change it safely;
- **lives in the repository**, committed where the project keeps its
  tooling, reachable by path.

## What stays disposable

- a **genuine one-off** — needed once, no future task plausibly repeats it;
- a **throwaway prototype** written to learn a library or shape — the
  blessed carve-out of the test-first rule (§3.4); recorded, if
  anywhere, as an exception in `grill.md §9`;
- anything embedding secrets, credentials, or production/personal data;
- project-specific tooling aimed at the seed — that is `harvest`'s
  agnosticism gate.

## The procedure sibling — durable skills

A tool is durable *code*; a **skill** is a durable *procedure* — the
disciplined sequence for a recurring kind of work (a migration recipe, a
release choreography, a data-reset dance). Same recurrence trigger, different
shape: if the recurring thing is code that runs, it is a tool; if it is the
*how* — the ordered steps and the gate each one clears, usually composing
existing protocols and tools — it is a skill. When such a procedure recurs and
no core `docs/graph/skills/` discipline covers it, author it as a project skill in
`.claude/skills/<name>/SKILL.md` from `docs/graph/templates/skill.template.md`, the same
way a missing role is commissioned from `docs/graph/templates/agent.template.md`. A skill
self-catalogs by living in `.claude/skills/`; it **composes** disciplines by
reference, never restating them. The core `docs/graph/skills/` stay the fixed shared
methodology — a project skill is the optional, project-specific procedure on
top.

## Design-time half of the rule

The doctrine cuts earlier than task end: when `grill` identifies a
recurring operation, the plan-of-record names a durable tool — or, when the
recurring thing is a *procedure* rather than code, a project skill — as the
unit of work; the capability is *designed* durable, not retrofitted. Workers
name every tool they build in `tools_built` and every recurring procedure in
`skills_built` in their handback payload
(`docs/graph/templates/prompts/handback-payload.md`); those fields are what the
close-out brief forwards to the librarian.

## Fail-closed doctrine

A task is **not complete** until any durable tool it produced is
cataloged and any procedure it repeated is crystallized into a project
skill, or the close-out has explicitly recorded "no durable tool / no skill,
because …" (for Tier 0/1 tasks, the session's one-line self-record in
the delivery covers this — see `docs/graph/protocols/canonize.md`). A task that
built a reusable capability — a tool, or a procedure worn in by repetition —
but left it uncaptured is a silent capability leak: the next session cannot
find what exists, so it rewrites it.

Cross-project mirror: `harvest` folds **project-agnostic** tools into the
seed's `tool-corpus/` and **project-agnostic** skills into `skill-corpus/`,
user-triggered only.
