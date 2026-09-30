<!--
Template: skill.template.md
Authored by: orchestrator (commission), or harvested from skill-corpus/
Lives at: docs/graph/skills/<name>.md (home), projected into each harness
dir the plant uses: .claude/skills/<name>/SKILL.md and kin
Used: when a repeatable project-specific procedure recurs and no existing
skill covers it — the procedure sibling of a durable tool (toolcraft).
Fill by copying into the target path and replacing every <placeholder>.
If it is code that runs, it is a tool; if it is who does the work, it is
an agent; if it is the disciplined sequence of steps (how to do X well),
it is a skill.
-->
---
name: <kebab-case-id>
description: <one line: what procedure this skill packages, and the exact triggers that should invoke it. This is what the router matches on, so name the recurring situation concretely.>
---

# <skill name>

<One paragraph: what recurring procedure this skill exists to make
repeatable, the tempting shortcut it replaces (doing it ad-hoc, or a
named shortcut), and why that shortcut costs more than the procedure.>

This skill ONLY <the bounded procedure it runs>, because <the reason the
bound holds>.

## When to apply this skill

- <the recurring trigger situation, concretely>
- <...>

## Where it runs

<Only for a skill that dispatches project-defined agents or runs
project-defined tools; delete this section otherwise. Name the root the
skill must be started from. A harness loads agents from the directory the
session starts in, so the same skill started one directory up can pass its
early steps and then find no agent to hand the next step to. Make step 1
of the procedure confirm that each agent it dispatches is in that root's
harness roster, and that each tool it runs exists on the branch in use.>

## The procedure

<The disciplined steps, in order. Each step names its concrete move and
the gate/check that proves it done. Compose existing protocols and skills
by reference (e.g. "characterize first: the `verify` behavior-preservation
gate"): a skill orchestrates disciplines and points at their rules.
Where a step crosses a hard boundary (an irreversible or destructive act,
a security, privacy or legal line, a user-sovereign trigger), state the
boundary with its right move at that step: "Ask the owner by name before
deleting <x>; deletion is irreversible.">

1. <step: the move, plus the check that proves it>
2. <...>

## Reference files

- `docs/graph/templates/<any template this skill fills>`
- `docs/graph/protocols/<the protocol(s) this skill composes>`
- `docs/graph/agents/<the agent that primarily runs this skill>`
