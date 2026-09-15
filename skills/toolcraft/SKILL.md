---
name: toolcraft
description: Doctrine (kernel §3.8) — when an operation will recur across independent sessions, the unit of work is a durable, tested, cataloged tool, not a throwaway script. Defines what counts as a durable tool, what stays disposable, the procedure sibling (a project skill), and the fail-closed rule that a task is incomplete until a durable tool is cataloged or recorded absent. AUTHORING a tool is agent.tool-smith; CATALOGING one happens inside the single canonize close-out spawn. This node is the rule both of them answer to, and every session reads it.
id: skill.toolcraft
tier: 2
kind: skill
origin: seed
title: toolcraft — the doctrine of durable, tested, cataloged tools versus throwaway scripts
owns:
  - rule.toolcraft
  - toolcraft.durability-criteria
requires:
peers:
  - agent.tool-smith
  - protocol.canonize
  - protocol.grill
  - protocol.harvest
  - method.engineering-posture
artifacts:
  - templates/skill.template.md
  - templates/agent.template.md
  - templates/prompts/handback-payload.md
load_when:
  - "should this script be kept, is this a durable tool"
  - "recurring operation across sessions"
  - "catalog a tool, tools_built, skills_built"
  - "throwaway prototype versus reusable tooling"
  - "crystallize a repeated procedure into a project skill"
prevents: A roster with an author for durable tools and no standard for them — nothing saying what earns durability, so every judgement about whether to build one is made fresh and no two sessions draw the line in the same place.
est_tokens: 1240
---

# toolcraft — the durable-tool doctrine

This node owns **the toolcraft rule** (kernel §3.8) — durable tools compound;
throwaway scripts are rework. When an operation will recur across independent
sessions, the unit of work is a **durable, tested tool** with a stable
interface — designed so at plan time, named in `tools_built` on every handback,
and cataloged in `docs/graph/tools/` by the librarian inside the close-out
spawn. Genuine one-offs and throwaway prototypes stay disposable. A task is
**not complete** until any durable tool is cataloged or explicitly recorded
absent.

Work generates capabilities, not only knowledge. A task needs an operation
performed — seed a fixture, migrate a schema, probe an endpoint, regenerate a
client — and an agent writes code to do it. If that code dies with the session,
the next task that needs the same operation writes it again, slightly
differently, with a fresh chance to get it wrong. Toolcraft is the doctrine that
keeps a capability once it is worth keeping.

**This node is the rule, not either half of the work.** Three things used to sit
in one file and are now separate, because they happen at different times and are
done by different actors:

| | Who | When |
|---|---|---|
| **the rule** — what earns durability | this node; every session reads it | always |
| **authoring** — building the tested tool | `docs/graph/agents/tool-smith.md` | mid-task, when the recurrence is noticed |
| **cataloging** — the page in `docs/graph/tools/` | the librarian, inside `docs/graph/protocols/canonize.md` | once, at close-out |

There is still **no separate cataloging spawn**: a second spawn with the same
bootstrap and lint run would be coordination waste, and canonize owns that rule.
Authoring is not a close-out step and never was — canonize catalogs the tool "it
produced", and the producer is the tool-smith.

## What counts as a durable tool (`toolcraft.durability-criteria`)

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
no core `docs/graph/skills/` discipline covers it, author it as a project skill from
`docs/graph/templates/skill.template.md`, the same
way a missing role is commissioned from `docs/graph/templates/agent.template.md`. Its
**home is the graph node** `docs/graph/skills/<name>.md`; create the projection
in each harness directory the plant actually uses
(`.claude/skills/<name>/SKILL.md` and kin) in the same pass, so the harness can
load it before the next install — `install.sh` projects what the graph holds,
so from then on the projection is maintained for you. It
**composes** disciplines by reference, never restating them. The core `docs/graph/skills/` stay the fixed shared
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

## Bounded execution lives elsewhere

The discipline for running a command that may outlive its session — explicit
bounds, detached launches, a durable log, bounded polling, liveness as an
observed signal, completion by marker — was filed here because toolcraft was the
nearest protocol. It is an execution discipline every session needs, not
tool-authoring doctrine, and its home is `method.engineering-posture`
(`toolcraft.bounded-execution`).
