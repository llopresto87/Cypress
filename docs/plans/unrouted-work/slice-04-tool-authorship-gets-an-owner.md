# Slice 4 — tool authorship gets an owner

**Status:** implemented 2026-09-14, gate green. **Depends on:** nothing structurally; shares the kernel
budget with slice 2.

## Why

`canonize` catalogs "any durable tool **it produced**". *It* is never named
(evidence E8). `toolcraft` owns the doctrine and states it "never spawns
separately". So the graph believes tools are being authored and names nobody who
authors them. In practice the operation gets rewritten by hand each session —
which is precisely the failure `rule.toolcraft` exists to prevent, reproduced
inside the node that prevents it.

The U-40 evaluation diagnosed `toolcraft` as doctrine filed as a protocol and
proposed reclassifying it to a skill or method node. The diagnosis was right and
the conclusion too small: **a charter with no flow is an agent.**

## The collision, and why it dissolves

`canonize` states: *"there is no separate toolcraft spawn; a second spawn with
the same bootstrap and lint run would be coordination waste."*

That rationale is about **cataloging** — writing the page in `docs/graph/tools/`
— which is librarian work at close-out and stays exactly as it is. **Authoring**
is different work at a different time: mid-task, when an agent notices it has
done the same thing by hand N times. Canonize's own wording concedes the actor
exists. So the sentence is **narrowed to cataloging, never reversed.**

## Scope boundary — the load-bearing constraint

The agent authors tools for **plant operations**: deterministic, repeated actions
on the project the plant is (regenerate a client, reconcile two exports, drive a
migration). It does **not** author seed or graph machinery — linters, routers,
graph tooling, anything under this repository's own `tools/`.

Consequence, and it is intended: none of this repository's own tooling would be
its work, because the seed is not a plant. The boundary is what stops the agent
becoming a general "write me a script" route.

## Shape, and where the rule lives

| Node | Kind | Owns |
|---|---|---|
| `agents/tool-smith.md` (new) | agent | `tool-smith.charter`, `tool-smith.authoring-bar`, `tool-smith.plant-scope` |
| `protocols/toolcraft.md` | **deleted as a protocol** | — |
| `skills/toolcraft/SKILL.md` (new) | skill | `rule.toolcraft`, `toolcraft.durability-criteria` |
| `core/method/engineering-posture.md` | method | gains `toolcraft.bounded-execution` |

**`rule.toolcraft` does not move to the agent.** A kernel rule binds every
session; a rule whose only home is a specialist's charter is invisible to any
session that never spawns that specialist. Seven of the eight rules live in
protocols and one (`rule.knowledge`) in a skill — a skill home is precedent, an
agent home would be a first, and this is the wrong rule to make it with. The
doctrine stays readable by everyone; the agent is its executor. That is the same
shape `canonize`/`toolcraft` has today, with a body attached.

**`toolcraft.bounded-execution` does not come along.** ~18 lines on long-running
commands, polling, and never re-issuing a command is an execution discipline
that was filed under toolcraft because toolcraft was the nearest protocol. It
belongs with the engineering posture and is rehomed, not deleted.

## Contract

- `A_REPEATED_OPERATION_HAS_AN_AUTHOR` — `agent.tool-smith` resolves, is routed
  by its own triggers, and is named by `canonize` as the producer it catalogs
  for.
- `THE_TOOL_SMITH_DOES_NOT_AUTHOR_SEED_MACHINERY` — the charter states the plant
  boundary and refuses out-of-scope work.
- `THE_CLOSE_OUT_STILL_SPAWNS_ONCE` — `canonize` still spawns the librarian
  exactly once; authoring is not a close-out step.

## Regression, observed RED first

`tests/test-tool-authorship.py` (new):

1. `rule.toolcraft` resolves to exactly one home, and `seed-lint`'s rule map
   agrees with it — **RED** the moment the protocol is deleted and the map is not
   updated, which is the point;
2. `agent.tool-smith` resolves, carries `routing_triggers` and `prevents:`, and
   its golden rows route to it — **RED today**;
3. `canonize` names the producer and still forbids a second *cataloging* spawn —
   a characterization test over both claims, so narrowing cannot silently become
   reversing;
4. `toolcraft.bounded-execution` is owned exactly once, by the posture;
5. kernel §3.8's owner pointer resolves.

## Risk

**Moving a kernel rule home is the highest-risk edit in this plan.** `seed-lint`
enforces the eight `rule.*` keys in exactly their mapped homes, so the map, the
node, the kernel anchor and the reference pages must move together or the gate
goes red — which is the protection, not the hazard.

**Deleting a protocol changes the plant-facing protocol set.** A grafted plant
loses `protocols/toolcraft.md` and gains `skills/toolcraft.md` plus an agent.
Nothing is lost, and `graft`'s own reconcile flow is what carries it.

**The agent could become a "write me a script" route.** The plant-scope boundary
is the whole defence; it has to be in the charter and in the triggers, not only
in this record.
