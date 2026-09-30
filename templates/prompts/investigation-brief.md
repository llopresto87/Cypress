<!--
Template: prompts/investigation-brief.md
Used: when delegating a read-only investigation of a subsystem to a
sub-agent, to gather facts for a spec, a graph node, or a plan.
Model class: sonnet (the investigation class; read-only evidence).
Fill the {{PLACEHOLDERS}} and hand the body to the sub-agent.
Discipline: agents/00-orchestrator.md (delegation), skills/knowledge-graph.
-->

# Investigation brief — {{subsystem or area}}

Investigate {{subsystem / repo / path}} and report **facts only**, read-only,
for the purpose of {{authoring a node / writing a spec / planning a change}}.

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first; these blocks are your routing.**
<!-- canonical blocks from docs/graph/templates/prompts/graph-session-bootstrap.md;
     tests/seed-lint.py holds them byte-identical, so edit them there -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (this is context routing; the `route_evidence` field
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: link to the node that owns a fact instead of
   restating it. The graph outranks your memory of APIs/versions.
   A fact the graph states is settled: use it as stated; re-deriving
   or re-checking it spends what the graph saves. Facts about code are
   current only where your brief carries a code-anchor line saying no
   code changed; otherwise check the code facts you rely on against
   the code.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, and only what your parent needs. Depth:
   `method.minimum-sufficient-work`, `method.decision-economy`,
   `method.engineering-posture` §8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

```
COMPANION (echo each item back in your handback):
- Trace this spawn. Your `spawn_id` is {{caller-minted dot-chain id,
  e.g. orchestrator.3.architect.1; see delegation.tracing}}. Echo it
  verbatim in your handback's `spawn_id` field.
- Cite the router. The `agent-lint --route` ranked line and confidence
  band that selected you, or the caller's override rationale:
  {{paste the line + band, or the rationale}}. Echo it back in
  `route_evidence`. At a LOW/NONE band, say so there and name the gap:
  a different specialist, or expertise no node in this graph carries.
- End with a handback. Close your turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md`: `produced_by:
  {{you}}`, `in_domain_work_done` with paths, `route_evidence`,
  `effort`, `expertise_gap`, `gates`, `tools_built`, and, at any
  out-of-domain boundary, `recommended_next` naming the specialist.
  When your report outgrows the soft target, write the overflow note
  as you work and name it (that file's Rules).
```

- **You are a read-only leaf.** At an out-of-domain boundary you ONLY
  recommend the next specialist; the work stays with them.
- **Sample the load-bearing files.** Start from {{which manifests, entry
  points, config files to prioritize}}, and confirm a path with
  `ls`/`grep` before you open it; the graph gives you your bearings, so
  reading in bulk only spends budget.
- **Report facts with evidence.** Every claim carries a concrete file
  path (and line where it matters) and an exact value (version, port,
  name) — not a paraphrase.
- **Name the gap instead of guessing.** Write "not recorded" for a fact
  you could not establish, and "none found" for an absence you checked,
  with what you searched. Accuracy matters more than completeness: a gap
  you name is useful (the no-fabrication rule is GRAPH DISCIPLINE 4,
  above).
- **If what this brief assumes exists does not, say so and stop.** A
  brief that asks you to restore something from history, or to find
  where something is set, assumes that it exists or once did. When the
  search shows it does not, or never did, report that result with what
  you searched (every branch, deleted and renamed paths, a content
  search over history) and stop. Hand back the negative result itself:
  an invention in its place reads like a recovery.
- **Read-only.** Use commands that only inspect (`ls`, `grep`, `wc`,
  `git log`, reading files); anything that changes state, in files, Git
  or elsewhere, is outside this brief.
- Be terse. Bullets and tables. This feeds a system prompt / a node, so
  precision beats prose.

## Report these, concretely

1. {{Structure: layout, main abstractions, conventions — naming, error
   handling, layering.}}
2. {{Versions / pins / config that other work depends on.}}
3. {{External edges: what it calls, what calls it, over what protocol.}}
4. {{Data it owns: entities/tables/documents, constraints, enums.}}
5. {{Tests, gates, CI — what exists and what is absent.}}
6. {{Anything surprising or non-standard a maintainer must know.}}

## Return

A structured, terse report. Cite paths. Flag every "not recorded" and
"none found". End
with anything you deliberately omitted for length, so the caller can
ask for it.
