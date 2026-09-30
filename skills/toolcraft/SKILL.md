---
name: toolcraft
description: Doctrine (kernel §3.8) — when an operation will recur across independent sessions, the unit of work is a durable, tested, cataloged tool, not a throwaway script. Defines what counts as a durable tool, what stays disposable, the procedure sibling (a project skill), and the fail-closed rule that a task is incomplete until a durable tool is cataloged or recorded absent. authoring a tool is agent.tool-smith; cataloging one happens inside the single canonize close-out spawn. This node is the rule both of them answer to, and every session reads it.
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
  - method.bounded-execution
artifacts:
  - templates/skill.template.md
  - templates/agent.template.md
  - templates/prompts/handback-payload.md
load_when:
  - "should this script be kept, is this a durable tool"
  - "recurring operation across sessions"
  - "catalog a tool, tools_built, skills_built"
  - "throwaway prototype versus reusable tooling"
  - "scratch scripts piling up, same script written a third time"
  - "crystallize a repeated procedure into a project skill"
prevents: A roster with an author for durable tools and no standard for them — nothing saying what earns durability, so every judgement about whether to build one is made fresh and no two sessions draw the line in the same place.
est_tokens: 1490
---

# toolcraft — the durable-tool doctrine

This node owns **the toolcraft rule** (kernel §3.8): durable tools
compound; throwaway scripts are rework. When an operation will recur
across independent sessions (or has already recurred inside one), the
unit of work is a **durable, tested tool** with a stable interface,
designed so at plan time, named in `tools_built` on every handback, and
cataloged in `docs/graph/tools/` by the librarian inside the close-out
spawn. Genuine one-offs and throwaway prototypes stay disposable. A task
completes only under the fail-closed rule below.

Work generates capabilities, not only knowledge. A task needs an
operation performed (seed a fixture, migrate a schema, probe an
endpoint, regenerate a client), and an agent writes code to do it. If
that code dies with the session, the next task that needs the same
operation writes it again, slightly differently, with a fresh chance to
get it wrong. Toolcraft is the doctrine that keeps a capability once it
is worth keeping.

This node is the rule; authoring and cataloging are separate, because
they happen at different times and are done by different actors:

| | Who | When |
|---|---|---|
| **the rule** — what earns durability | this node; every session reads it | always |
| **authoring** — building the tested tool | `docs/graph/agents/tool-smith.md` | mid-task, when the recurrence is noticed |
| **cataloging** — the page in `docs/graph/tools/` | the librarian, inside `docs/graph/protocols/canonize.md` | once, at close-out |

Cataloging happens inside the one canonize close-out spawn;
`protocol.canonize` owns that rule. Canonize catalogs the tool "it
produced", and the producer is the tool-smith.

## What counts as a durable tool (`toolcraft.durability-criteria`)

Catalog a piece of real code that:
- **recurs across independent sessions**: an agent, expert, or skill
  will plausibly run it again in a future task (the trigger is
  recurrence, not size). Recurrence also counts inside one long session,
  and the third-time rule (`agent.tool-smith`'s bar) fires on scratch
  code too (the scratch count below);
- has a **stable interface**: a named entry point, defined inputs and
  outputs, a documented invocation, not a copy-pasted snippet;
- is **authorized by a test** (§3.4): at least one test, sized by
  `test-first.proportionate-checks`, pins what it does;
- **lives in the repository**, committed where the project keeps its
  tooling, reachable by path.

## What stays disposable

- a **genuine one-off**: needed once, no future task plausibly repeats
  it;
- a **throwaway prototype** written to learn a library or shape: the
  blessed carve-out of the test-first rule (§3.4); recorded, if
  anywhere, as an exception in `grill.md §9`;
- anything embedding secrets, credentials, or production/personal data;
- project-specific tooling aimed at the seed: that is `harvest`'s
  agnosticism gate.

## The procedure sibling — durable skills

A tool is durable *code*; a **skill** is a durable *procedure*: the
disciplined sequence for a recurring kind of work (a migration recipe, a
release choreography, a data-reset dance). Same recurrence trigger,
different shape: if the recurring thing is code that runs, it is a tool;
if it is the *how* (the ordered steps and the gate each one clears,
usually composing existing protocols and tools), it is a skill. When
such a procedure recurs and no core `docs/graph/skills/` discipline
covers it, author it as a project skill from
`docs/graph/templates/skill.template.md`, the same way a missing role is
commissioned from `docs/graph/templates/agent.template.md`. Its **home
is the graph node** `docs/graph/skills/<name>.md`; create the projection
in each harness directory the plant actually uses
(`.claude/skills/<name>/SKILL.md` and kin) in the same pass, so the
harness can load it before the next install. `install.sh` projects what
the graph holds, so from then on the projection is maintained for you.
It **composes** disciplines by reference. The core `docs/graph/skills/`
stay the fixed shared methodology; a project skill is the optional,
project-specific procedure on top.

## Design-time half of the rule

The doctrine cuts earlier than task end: when `grill` identifies a
recurring operation, the plan-of-record names a durable tool (or, when
the recurring thing is a *procedure* rather than code, a project skill)
as the unit of work; the capability is *designed* durable, not
retrofitted. Workers name every tool they build in `tools_built` and
every recurring procedure in `skills_built` in their handback payload
(`docs/graph/templates/prompts/handback-payload.md`); those fields are
what the close-out brief forwards to the librarian.

## Fail-closed doctrine

A task completes only when every durable tool it produced is cataloged
and every procedure it repeated is crystallized into a project skill, or
the close-out has explicitly recorded "no durable tool / no skill,
because …" (for Tier 0/1 tasks, the session's one-line self-record in
the delivery covers this; see `docs/graph/protocols/canonize.md`). A
task that built a reusable capability (a tool, or a procedure worn in by
repetition) and left it uncaptured is a silent capability leak: the next
session cannot find what exists, so it rewrites it.

Scratch space is where copies pile up uncounted: each worker writes its
own variant, none is promoted, and the session ends with dozens of
near-duplicates. So at each delivery metrics checkpoint
(`protocol.deliver`) or at session end, the orchestrator counts the
scratch scripts by purpose; a purpose with three or more variants is a
recurrence and goes to `tool-smith`.

Cross-project mirror: `harvest` folds **project-agnostic** tools into
the seed's `tool-corpus/` and **project-agnostic** skills into
`skill-corpus/`, user-triggered only.
