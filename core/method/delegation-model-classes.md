---
id: method.delegation-model-classes
tier: 2
kind: method
origin: seed
title: delegation model classes — the class and reasoning effort each step runs on, and light variants
owns:
  - delegation.model-classes
  - delegation.light-variants
  - delegation.effort
requires:
peers:
  - method.delegation
  - method.delegation-cycle-economy
artifacts:
  - templates/agent.template.md
load_when:
  - "sonnet or opus, which model class"
  - "reasoning effort, low effort worker, light variant, light reviewer or tester"
  - "effort for this spawn, effort field in the agent definition"
prevents: Every worker run on the most expensive model at full effort, or a cheap one handed authoring, review or a security surface it cannot carry.
est_tokens: 2153
---

## Route by model class

Read-only investigation and mechanical retrieval/normalization →
**sonnet-class** (draft artifacts are finalized by an opus librarian);
authoring, implementation, judgment-heavy design, review, or adversarial
validation → **opus-class**. The one exception is a light variant
(`delegation.light-variants`, below): a light
reviewer, a light tester or a one-line-fix implementer runs small, mechanical
work on the investigation class, and never on a security surface. No other
authoring or review step leaves its class. This **model class** lives in each
agent's `model:` frontmatter. It is a distinct axis from the **task tier**
(T0–T3, kernel §0) and the graph **load-tier** (the node `tier:` field): three
independent axes that share the word loosely — only the risk axis is written
`T0–T3`; "model class" and "load-tier"/`tier:` name the other two.

A host that can select model *versions* within a class refines each phase's
class to a concrete version at spawn time. That version policy is host-specific
and lives in the host's integration overlay, never in a tool-neutral node; the
class a phase uses stays owned by that phase in its protocol node.

**Effort refines the class; it is not a fourth axis.** Effort in this node is
*reasoning effort*, a host setting. It is not the owner-declared *effort level*
of a task, which `method.minimum-sufficient-work` owns. A host that accepts a
reasoning-effort setting runs a class at low, medium or high effort. Which
hosts accept one, and whether it is set per agent definition or per spawn, is
host policy, recorded under `delegation.effort` below.
Where the host reads a default effort from the agent's definition, that default
is the baseline. A spawn that departs from it, in model or in effort, records
the departure and its reason in the brief's routing evidence, the same place an
overridden route is recorded, so the delivery can see which budget each step
ran on.

The class and effort each step kind runs on by default:

| Step kind | Class | Effort | Forced up to authoring class, high effort, when |
|---|---|---|---|
| Artifact discovery, extracting an earlier handback to a file | investigation | low to medium | the discovery itself has to decide something |
| Library research (`research-scout`) | investigation | medium | none: its draft is finalized by an authoring-class librarian |
| A mechanical gate run: a suite, the lints, writing the runbook record | investigation | low | the result is red: diagnosis goes to the authoring class (`protocol.recover`) |
| Spec contracts, architecture, rulings on a contract's reading, one-way doors, threat models, `devils-advocate` | authoring | high | already at the ceiling |
| The canonize librarian | authoring | medium | the close-out ends a grow or a graft: high |
| A harvest's faithful-import review (`protocol.harvest`) | authoring | high | already at the ceiling |
| Any step on a security surface (the list under `delegation.light-variants`) | authoring | high | already at the ceiling |

A gate-running worker judges nothing. It runs the gates, asserts what they
report, and fails closed on output it cannot read; the verdict on a red result
belongs to the authoring class.

### Light variants (`delegation.light-variants`)

Light variants are adopted for small, mechanical work, and never for a
security surface.

**A light variant is a budget, not a new mandate.** A plant may instantiate a
low-budget variant of an existing specialist for small, mechanical work (a
pinned test, a one-line fix, a follow-up diff). The variant keeps the base
agent's mandate unchanged, runs on the investigation class at low effort, and
its definition `requires:` the base agent and names it as the escalation
target. Like any commissioned expert (`delegation.routing`, in
`method.delegation`), it joins the project's roster,
never the seed's.

It reads only the exact ranges its brief names, as `file:line` spans: the spec
rows, the diff hunks, the test functions. It still runs the graph discipline's
`--plan` and reports the output, but it loads no node the brief does not name
and lists every other one as skipped, brief-scoped.

**Escalation is mechanical, never a judgment of size.** The variant stops with
`blocked-out-of-domain` and names the base agent as `recommended_next` when any
of these holds, and it never widens its own reading to cover the gap:

- deciding the work needs a line outside the ranges the brief names;
- the diff changes a line outside the hunks the brief names;
- the diff changes a spec contract, a public interface, a persisted format, or
  any line on a security surface (authentication, authorization, secrets, a
  credential holder, input from outside the trust boundary);
- the named ranges raise a question the brief does not answer: a second
  reading of a contract, or a design choice.

**Never on a security surface.** Work that touches one goes to the full agent
at the class the table gives, whatever its size. The caller applies this before
routing, and the third escalation condition is the variant's backstop when the
caller misjudged it.

**Still an independent reviewer.** A light reviewer is a reviewer at a smaller
budget. It is never the author of what it reviews, and never a worker from the
lane whose output it reviews. It does not replace the independent review a step
requires; it only runs that review more cheaply when the work is small.

**Size the brief to the class before routing to it.** The caller gives a light
variant the smallest context that decides the work: the exact ranges, the few
binding rules quoted, a short checklist, the gates and the handback. A caller
that cannot bound the reading that tightly has work that is not small, and
routes it to the base agent or splits it into briefs of one source each. A
brief that asks a variant to transcribe from several sources is not small
either, and the variant's decline is the correct outcome. The cost of the
re-route belongs to the brief.

### Effort (`delegation.effort`)

An agent definition's `effort:` key takes one value from the closed set `low`,
`medium`, `high`. Claude Code reads `effort` from subagent frontmatter with the
values `low`, `medium`, `high`, `xhigh` and `max`; the key overrides the
session's effort level for every spawn of that definition, and a subagent
without one inherits the session's
(Claude Code sub-agents page, https://code.claude.com/docs/en/sub-agents,
retrieved 2026-09-26; the levels on offer depend on the model). The seed ships
the three lower values only. Whether that host offers a per-spawn override: not
recorded. Whether opencode, Codex or GitHub Copilot read the key: not recorded.
No install transform drops the key.

Each agent definition defaults to the effort of the step kind it mostly runs,
from the table above, and to `medium` where the table has no row:

| `effort:` | Agent (the step kind it mostly runs) |
|---|---|
| high | `orchestrator` (routing and rulings on a contract's reading), `architect` (spec contracts, architecture, rulings, one-way doors), `multi-agent-architect` (architecture), `security` (any step on a security surface; threat models), `pentest` (any step on a security surface), `devils-advocate` (adversarial validation), `legal` (rulings against a rule corpus), `growth-orchestrator` (the close-out that ends a grow) |
| medium | `implementer` (routine GREEN), `tester` (RED for a new contract), `reviewer` (standard batch review), `product` (spec §3 and §9), `docs-librarian` (the canonize librarian), `research-scout` (library research), `growth-scout` (artifact discovery, low to medium) |
| medium | no table row: `ui-ux-designer`, `data-ml`, `reliability`, `tool-smith`, `seed-installer` |

A spawn's effort is derived from the first row that matches:

| # | Condition | Spawn effort |
|---|---|---|
| 1 | a security surface (any trigger in `agent.security`'s "When to invoke" list; the brief names which); spec contracts, architecture, rulings, one-way doors, threat models, `devils-advocate`; a harvest's faithful-import review; diagnosing a red gate | high |
| 2 | a light variant (never on a security surface) | low |
| 3 | the spawn carries increments: the hardest label in the batch (`delegation.effort-scale`) | low or medium-low → low; medium → medium; medium-hard or hard → high |
| 4 | no increment label: the step kind's row in the class and effort table above | that row's effort |
| 5 | otherwise | the agent definition's default |

The brief's routing evidence records one line,
`effort: <value> (row <n>: <reason>)`. When the value differs from the agent
definition's default on a host with no recorded per-spawn setting, the line adds
`host applies: definition default <value>`, so the departure is visible. The
handback echoes the line in its `effort:` field.

Departures fail closed. For rows 3 to 5, route to a definition that carries the
needed effort, or accept the recorded departure. For row 1 a departure is never
accepted: the step goes to a definition whose default is `high`, or its output
takes a review spawn at `high` before it lands (`security` for a security
surface, `architect` for a contract or ruling). A row-1 step with neither is a
block.
