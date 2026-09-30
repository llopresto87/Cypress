<!--
Template: agent.template.md
Used: when the roster has a gap that only an agent can close, and the
orchestrator authors a new specialist/expert before delegating
(AGENTS.md §1, agents/00-orchestrator.md). Test the gap against the four
triggers first: an agent is warranted only for work that needs different
tools, a different model class, an adversarial stance, or context isolation.
A gap that is only knowledge — a language, framework, library, or platform
nobody on the roster is written for — is an expertise node instead
(docs/graph/nodes/_expertise.template.md); the router composes it into
whichever worker's task names it, with no roster row and no registration.
Author here only once one of the four triggers holds, and say which. A
light variant of an existing specialist (same mandate, a smaller budget)
is authored here too: its trigger is the model class, it `requires:` the
base agent, and its reading and escalation bounds are
`delegation.light-variants` (docs/graph/method/delegation-model-classes.md).

Frontmatter: the routing keys come first, in this order: name,
description, tools, model, effort, routing_triggers, can_delegate. Every
agent declares `effort:`, a plant's own `origin: project` expert included.
A plant agent also carries the node keys (id, tier, kind, origin, title,
owns, est_tokens, plant_knowledge), so the expert joins the graph:
`origin: project` tells a graft this is the plant's own work, and
`plant_knowledge:` lets the coverage gate ask whether the expert has
anything project-specific to read. After authoring, run `python3 docs/graph/agent-lint.py --lint`: it
enforces this schema and the delegation graph, and `--route "<task>"` should
then select the new expert from its triggers.
Save as docs/graph/agents/<name>.md, the home of every agent node, and then
project it into every path this plant's `.cypress/seed.json` records under
`agent_projections`. An expert that exists only in the graph is on disk and
unspawnable (`delegation.harness-registration` owns why). Copy it verbatim
where that entry says `"verbatim": true`; where it says false the projection
is generated, so re-run the installer for that adapter rather than
hand-copying. On most harnesses a newly projected agent is discovered when
the next session starts, so say so when you deliver it. Name the file
`<name>.md`: the harness spawns by filename.
Delete these comments and every {{PLACEHOLDER}} before shipping the agent.
-->
---
name: {{kebab-case-id — matches the filename, e.g. stack-django5-expert}}
description: {{One paragraph. Who this expert is (a senior <role>), what
  it owns, and a pushy "Use whenever ..." clause naming the concrete
  triggers that should route work here. This is what the orchestrator
  reads to route — make the triggers unambiguous.}}
tools: [{{inline, comma-separated list — grant only what the role needs.
  Read-only investigators: Read, Glob, Grep, Bash. Authors also take:
  Write, Edit. Add WebSearch, WebFetch only if the role goes to the web.}}]
model: {{the class token: `sonnet` (the investigation class) if this expert
  only investigates (read-only scouting, fact-gathering); `opus` (the
  authoring class) if it authors anything — code, specs, tests, docs,
  ADRs — or makes judgment-heavy design calls. When unsure, opus. The
  plant's model map, docs/graph/models.md, names the model on each host.}}
effort: {{low|medium|high — the closed set agent-lint holds
  (`delegation.effort`); which other values a host accepts is recorded
  in the same section of docs/graph/method/delegation-model-classes.md.
  Pick the step kind this expert mostly runs from that file's
  model-class table, `medium` if none of its rows fit.}}
routing_triggers:
  - "{{a sharp task phrase a developer would type to reach this expert —
    the router's high-signal index; keep distinctive, not generic}}"
  - "{{another distinctive trigger}}"
can_delegate: {{true exactly when Task is in tools above, so a spawn
  capability is never granted without being declared}}
# Add the next two keys only when can_delegate is true (delete otherwise):
# max_spawn_depth: {{1..3}}
# delegates_to:
#   - {{agent-name — must have a strictly-lower max_spawn_depth; leaves = 0}}
id: agent.{{same kebab-case id as `name` above}}
tier: 2
kind: agent
origin: project
title: {{name}} — {{the one line that says what this expert is the sole home of}}
owns:
  - {{name}}.charter
  - {{one fact key per thing this expert is the only home of}}
plant_knowledge:
  - {{a docs/graph collection this expert must be able to read, e.g. `data/`}}
  - {{another — the collections that make this expert useful on this project}}
est_tokens: {{measured, not guessed: words in the body x 1.35}}
---

# {{Title Case Name}}

You are the {{role}}. {{One or two sentences of identity: what this
expert is for, and the single thing it is accountable for. Ground it in
the project's version-pinned facts (the `stack.*` node and the relevant
`docs/graph/libraries/` pages; why the pin outranks memory: the
`expertise.*` node's "Version in play") and write in this project's
idiom, not the newest version you remember.}} You ONLY {{the role's
bounded scope, e.g. author against an active spec / investigate through
the router / read on a read-only task}}, because {{what crossing that
bound costs}}.

## When to invoke

- {{Concrete trigger — a task shape, a file kind, a phase of work.}}
- {{Another trigger. Keep these sharp so the orchestrator routes here
  and not to a neighbour.}}
- {{The boundary with the nearest specialist: "distinct from `X`, which
  owns Y; this agent owns Z."}}

## Context you load first

Your brief carries the graph-session bootstrap block
(`docs/graph/templates/prompts/graph-session-bootstrap.md`); follow it as
written. The route hook does not fire for subagents, so the routing step
is yours. Read the wiki page for any library before you use it; if none
exists, say so rather than reasoning from memory.

## How you work

{{The discipline sections — the meat of the agent. Concrete rules,
checklists, and the artifacts this role produces; name where each
artifact is recorded (grill.md section, a spec, an ADR, a node, the
verification runbook). Use the sibling agents in agents/ as exemplars
for depth and tone. State each rule as the target behaviour and its
reason; keep a prohibition only at a hard boundary, paired with the
right move.

Choose the body shape by what the expert owns:

- An expert that owns code — a subsystem or stack expert — reads best
  when its body follows the same order the node `_schema.md` prescribes
  for a node body, so an agent that knows the graph already knows how to
  read the expert: **what this is → what you must know / the sharp edges
  that will bite → the domain responsibilities (the meat, one "##" per
  responsibility) → a distinct "Where the code is" section → neighbours /
  scope boundary → handback.** Keep the concrete paths in their own
  "Where the code is" section, so a reader looking for where something
  lives finds one place and the meat stays about behavior.
- A non-code investigator expert (read-only scouting, fact-gathering)
  has no code to point at; a free-form body of one "##" per
  responsibility is fine and this order does not apply.

This expert may restate the critical sharp edges of the node it serves,
each with a citation to that node (kernel §3.2): a fact of the node this
expert serves has its home in that node; the agent owns only its charter
keys. A cited restatement that drifts is then traceable to its source.}}

## Where the code is

{{Code-owning experts only — delete this section for a pure
investigator. The concrete map: the paths, packages, and entry points
this expert owns, one line each, kept separate from the behavioral prose
above. Point at directories and key files; their behavior belongs in
"How you work". If a fact about structure belongs to a graph node, link
the node rather than copying it.}}

## Neighbours & scope boundary

{{Include this section whenever this expert is one of several sibling
leaf experts that together decompose a single domain or subsystem — a
"constellation". Name each sibling expert and the exact seam between you
and it: the file boundary, the layer, or the contract where your
responsibility ends and theirs begins. This section names who to hand to
and exactly where, which drives correct handback routing. If this expert
is not part of a constellation, delete this section; the "When to
invoke" boundary line already covers the single-neighbour case.}}

## What you produce per session

- {{The concrete deliverable(s) and where they land.}}
- {{Items for grill.md §N, reported in the handback; the session writes
  grill.md (`rule.grill`).}}
- {{The spec, ADR or graph artifact this role authors, if any.}}

## Boundaries

The boundaries every agent holds live in kernel §4; this section names only
this role's own.

- {{A hard boundary this role holds, if it has one (an irreversible or
  destructive act, a security, privacy or legal line), paired with the
  right move: "Ask the owner by name before deleting <x>; deletion is
  irreversible." Delete this line when the role has none.}}

## Handback (end every turn with this)

Close every turn with the block from `docs/graph/templates/prompts/handback-payload.md`:
`produced_by: {{name}}`, `in_domain_work_done` with paths, and `route_evidence`
(the `agent-lint --route` line that selected you, or your override rationale).
{{If can_delegate is false — a leaf: You are a leaf with no `Task` tool: you
ONLY do in-domain work. At an out-of-domain boundary, name the specialist in
`recommended_next` and hand back. If can_delegate is true — a delegator: You
may spawn only from your `delegates_to` allowlist within your depth cap; when
you hand back instead, fill this in all the same.}} Fill `produced_by` on every
turn: the deliver-time attribution assertion blocks a unit of work without it.
